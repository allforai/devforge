# Design: Workflow Engine Core (Sub-project 1)

**Date:** 2026-04-11
**Scope:** `src/devforge/workflow/` (new module) + REPL integration
**Goal:** 独立 workflow 引擎，读取 `.devforge/workflow.json`，按节点顺序执行，追踪 artifact，写 transition log。替代 meta-skill 的 `/run` 命令，与现有 run_cycle 并存（方案 B）。

---

## 背景

DevForge 当前有两套执行机制：
- **run_cycle**：面向开发周期，基于 snapshot + work_package，适合持续迭代
- **meta-skill `/run`**：面向一次性分析工作流，基于 workflow.json + node-specs，适合 discover/reverse-concept/product-analysis 等任务

目标是把第二套能力内化到 DevForge，长期替代 meta-skill。本子项目只做引擎核心，不涉及动态节点分化（子项目 2）和内置工作流模板（子项目 3）。

---

## 方案选择

**选择方案 B：独立引擎，零破坏**

- 新建 `src/devforge/workflow/` 模块，不修改现有 run_cycle
- 现有 259 个测试不受影响
- REPL 新增 `wf` 命令组，与现有命令并存
- 为子项目 2（动态分化）和子项目 3（内置模板）预留接口

---

## 数据模型

### `.devforge/workflow.json`

```json
{
  "schema_version": "1.0",
  "id": "wf-<slug>-<timestamp>",
  "goal": "工作流目标描述",
  "created_at": "<ISO timestamp>",
  "nodes": [
    {
      "id": "<node-id>",
      "capability": "<capability-name>",
      "goal": "<节点目标描述>",
      "status": "pending | running | completed | failed",
      "depends_on": ["<node-id>"],
      "exit_artifacts": ["<relative-path>"],
      "knowledge_refs": ["<relative-path-to-md>"],
      "executor": "claude_code | codex",  // 默认 claude_code
      "parent_node_id": null,
      "depth": 0,
      "error": null
    }
  ],
  "transition_log": [
    {
      "node": "<node-id>",
      "status": "completed | failed",
      "started_at": "<ISO timestamp>",
      "completed_at": "<ISO timestamp>",
      "artifacts_created": ["<paths>"],
      "error": null
    }
  ]
}
```

**节点状态流转：** `pending → running → completed | failed`

**文件即真相：** 引擎启动时先检查 exit_artifacts 是否存在，存在则标记 completed，优先于 transition_log 记录。

---

## 新模块结构

```
src/devforge/workflow/
├── __init__.py          # 导出 WorkflowEngine
├── models.py            # WorkflowNode, WorkflowState TypedDict
├── engine.py            # 核心执行循环
└── artifacts.py         # exit_artifacts 存在性检查
```

### `models.py`

```python
from typing import TypedDict, Literal

NodeStatus = Literal["pending", "running", "completed", "failed"]

class WorkflowNode(TypedDict):
    id: str
    capability: str
    goal: str
    status: NodeStatus
    depends_on: list[str]
    exit_artifacts: list[str]
    knowledge_refs: list[str]
    executor: str
    parent_node_id: str | None
    depth: int
    error: str | None

class TransitionEntry(TypedDict):
    node: str
    status: Literal["completed", "failed"]
    started_at: str
    completed_at: str
    artifacts_created: list[str]
    error: str | None

class WorkflowState(TypedDict):
    schema_version: str
    id: str
    goal: str
    created_at: str
    nodes: list[WorkflowNode]
    transition_log: list[TransitionEntry]
```

### `artifacts.py`

```python
from pathlib import Path

def check_artifacts(root: Path, paths: list[str]) -> bool:
    """全部 exit_artifacts 存在则返回 True。"""
    return all((root / p).exists() for p in paths)
```

### `engine.py` 核心逻辑

```python
MAX_CONCURRENT = 3

def select_next_nodes(state: WorkflowState) -> list[WorkflowNode]:
    """选出可立即执行的节点（依赖全部 completed，且未超并发上限）。"""
    completed = {n["id"] for n in state["nodes"] if n["status"] == "completed"}
    running = [n for n in state["nodes"] if n["status"] == "running"]
    if len(running) >= MAX_CONCURRENT:
        return []
    return [
        n for n in state["nodes"]
        if n["status"] == "pending"
        and set(n["depends_on"]) <= completed
    ][:MAX_CONCURRENT - len(running)]

def run_one_cycle(root: Path) -> dict:
    """执行一轮：选节点 → 调用执行器 → 写 transition_log → 返回摘要。"""
    ...
```

---

## 引擎执行流程

```
wf run 触发一次 run_one_cycle：

1. 读 .devforge/workflow.json
2. 检查所有节点的 exit_artifacts：存在 → status = completed（文件即真相）
3. select_next_nodes() 选出可执行节点（pending + 依赖满足 + 不超并发）
4. 对每个选中节点：
   a. 读 knowledge_refs 文件内容
   b. 构建执行器 prompt（goal + knowledge_refs + 已完成节点的 artifacts 路径）
   c. 调用 ClaudeCodeAdapter 或 CodexAdapter
   d. 追加 transition_log（started_at / completed_at / artifacts_created / error）
   e. 更新节点 status
5. 写回 workflow.json
6. 返回执行摘要
```

**终止条件：**
- 所有节点 `completed` → 成功，打印完成报告
- 某节点 `failed` 连续 3 次 → 警告用户，停止并等待人工干预
- 无可执行节点但有 `pending` 节点 → 存在未满足依赖，报错说明哪些节点阻塞

---

## REPL 集成

### 新增命令

| 命令 | 说明 |
|---|---|
| `wf` | 显示工作流 DAG 状态 |
| `wf run` | 执行下一批可运行节点 |
| `wf init <名称>` | 从内置模板创建 workflow.json |
| `wf log` | 显示 transition_log |
| `wf reset <node-id>` | 重置节点为 pending（重跑） |

### `wf` 输出示例

```
Workflow: 逆向分析 DevForge 项目
──────────────────────────────────
✅ discover          (completed)
⏳ reverse-concept   (pending, 等待: discover)
⏳ product-analysis  (pending, 等待: reverse-concept)

进度: 1/3 节点完成
输入 'wf run' 继续执行
```

### 目标设置集成

启动时询问"当前目标"后：
- `.devforge/workflow.json` 已存在 → 自动显示 `wf` 状态
- 不存在 → 提示 `wf init <模板>` 创建，或 `c` 继续现有 run_cycle

---

## 文件变更

| 文件 | 变更类型 |
|---|---|
| `src/devforge/workflow/__init__.py` | 新建 |
| `src/devforge/workflow/models.py` | 新建 |
| `src/devforge/workflow/engine.py` | 新建 |
| `src/devforge/workflow/artifacts.py` | 新建 |
| `src/devforge/repl.py` | 修改：新增 wf 命令解析和渲染 |
| `tests/test_workflow_engine.py` | 新建 |

---

## 测试策略

- **unit**：`artifacts.py` 的文件检查，`select_next_nodes()` 的依赖解析，`TransitionEntry` 写入
- **integration**：完整 workflow 从 pending → completed，失败重试逻辑，文件即真相覆盖 transition_log
- **不测**：执行器实际调用（mock adapter），REPL 渲染输出

---

## 不在本子项目范围内

- 动态节点分化（子项目 2）
- 内置工作流模板 + 知识库迁移（子项目 3）
- 并发执行（顺序执行即可，并发在子项目 2 引入）
