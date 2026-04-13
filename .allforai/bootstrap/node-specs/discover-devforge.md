---
node: discover-devforge
exit_artifacts:
  - .allforai/bootstrap/source-summary.json
  - .allforai/bootstrap/file-catalog.json
  - .allforai/bootstrap/infrastructure-profile.json
---

# Task: DevForge 仓库深度扫描

对 DevForge 代码库做 SDK-focused 完整 discovery。建立模块清单、公开 API surface、测试覆盖情况和基础设施档案，供 reverse-concept 节点使用。

## Project Context

- **语言/版本**: Python 3.12
- **框架**: LangGraph ≥0.2, httpx
- **包管理**: uv + setuptools
- **架构**: 分层 orchestration kernel（state → planning → graph → executor）
- **测试**: pytest，256 个测试，全通过
- **入口**: `devforge` CLI（`src/devforge/main.py`）
- **核心模块**: state/, graph/, executors/, planning/, scheduler/, knowledge/, llm/, persistence/, tools/, context/, roles/, seams/, config/, topology.py

## Theory Anchors

- **SDK Discovery Focus**: 重点在公开 API surface（类、函数、Protocol）、测试套件（覆盖哪些场景）、文档（README、PLAN.md、docs/）
- **Breadth first**: 先扫模块目录结构，再读关键文件
- **Infrastructure before business**: 先理解 persistence/llm/tools 基础层，再看 planning/graph 业务层
- **Config is code**: `llm.yaml`、`.env.example`、`pyproject.toml` 包含业务决策

## Guidance

### 扫描优先级

1. **公开接口层**（最重要）
   - `src/devforge/executors/base.py` — ExecutorAdapter Protocol 定义
   - `src/devforge/graph/builder.py` — run_cycle() 主入口
   - `src/devforge/graph/runtime_state.py` — RuntimeState 模型
   - `src/devforge/main.py` — CLI 命令接口
   - `src/devforge/state/` — 所有状态模型（WorkPackage、Project、Initiative、Seam 等）

2. **基础设施层**
   - `src/devforge/persistence/` — 四层存储架构
   - `src/devforge/llm/` — LLM provider 抽象
   - `src/devforge/tools/` — 外部工具集成

3. **业务逻辑层**
   - `src/devforge/planning/` — 规划决策链
   - `src/devforge/executors/adapters.py` — 执行器分派
   - `src/devforge/graph/nodes.py` — graph nodes

4. **测试套件**（理解覆盖场景）
   - `tests/test_e2e_*.py` — 端到端测试（揭示核心业务流）
   - `tests/test_graph_runner.py` — 主运行时测试（最重要）
   - `tests/test_state_and_roles.py` — 状态模型测试

5. **文档**
   - `README.md` — 用户视角的产品描述
   - `PLAN.md` — 架构设计文档（最详细）
   - `docs/cli.md`、`docs/project-config.md`
   - `llm.yaml` — LLM 配置示例

### source-summary.json 要覆盖

- 每个模块的职责、边界、核心类/函数
- 公开 API surface（Protocol/ABC 定义、入口函数）
- 模块间依赖关系
- 架构模式识别（adapter、strategy、factory、LangGraph state machine）
- 测试密度（每模块有多少测试？）

### file-catalog.json 要覆盖

- 每个模块的关键文件列表（不需要全部文件，选最重要的）
- 每个文件的 business intent（一句话）
- 区分：public interface / internal implementation / test / fixture / config

### infrastructure-profile.json 要覆盖

- 数据存储：SQLite（workspace.sqlite3）、JSON snapshot、JSONL event log、filesystem artifacts
- LLM providers：OpenRouter、Google AI，httpx transport
- 外部工具：Brave Search、FAL image、Stitch UI
- 进程执行：subprocess transport（ClaudeCode CLI、Codex CLI、Python local runner）
- 没有传统 web server、没有消息队列、没有 Redis/cache layer

### 注意事项

- DevForge 是框架级 SDK，不是终端用户 App。"用户"是调用 `run_cycle()` 或 `devforge` CLI 的开发者
- 测试文件是理解行为契约的最佳入口，比源码注释更可靠
- `src/devforge/fixtures/` 包含 game_project.json 和 ecommerce_project.json，是理解 WorkspaceState 完整结构的最佳样本
- PLAN.md 包含完整的设计意图，应作为 discovery 的锚点文档

## Exit Artifacts

### `.allforai/bootstrap/source-summary.json`

```json
{
  "project_name": "devforge",
  "tech_stacks": [...],
  "modules": [
    {
      "id": "<M001-M015>",
      "path": "<relative path>",
      "role": "backend | shared",
      "public_interfaces": ["<class/function names>"],
      "internal_count": "<number of internal files>",
      "test_count": "<number of test files covering this module>",
      "description": "<business intent>"
    }
  ],
  "architecture_pattern": "<string>",
  "detected_patterns": ["<pattern names>"],
  "dependency_graph": {
    "<module>": ["<depends on modules>"]
  }
}
```

### `.allforai/bootstrap/file-catalog.json`

```json
{
  "modules": [
    {
      "id": "<M001>",
      "key_files": [
        {
          "path": "<relative path>",
          "intent": "<business intent one sentence>",
          "type": "public_interface | implementation | test | fixture | config"
        }
      ]
    }
  ]
}
```

### `.allforai/bootstrap/infrastructure-profile.json`

```json
{
  "databases": [
    { "type": "sqlite", "path": ".devforge/workspace.sqlite3", "usage": "snapshot + event + memory store" }
  ],
  "caches": [],
  "auth": null,
  "storage": [
    { "type": "filesystem", "path": ".devforge/artifacts/", "usage": "executor output artifacts" }
  ],
  "background_jobs": [],
  "external_apis": [
    { "name": "OpenRouter", "usage": "LLM routing" },
    { "name": "Google AI", "usage": "Gemini LLM" },
    { "name": "Brave Search", "usage": "web search tool" },
    { "name": "FAL", "usage": "image generation" }
  ],
  "subprocess_executors": [
    { "name": "claude_code", "binary": "claude", "protocol": "CLI --print --output-format json" },
    { "name": "codex", "binary": "codex", "protocol": "CLI exec --full-auto" },
    { "name": "python_local", "binary": "python", "protocol": "-m devforge.executors.local_runner" }
  ]
}
```

## Downstream Contract

→ `reverse-concept-devforge` 读取：
- `source-summary.json` → `modules[]`（模块边界和公开接口，作为 JTBD 提取的基础）
- `source-summary.json` → `architecture_pattern`（辅助识别 governance style）
- `file-catalog.json` → `modules[].key_files`（知道要读哪些文件提取概念证据）
- `infrastructure-profile.json` → `subprocess_executors`, `external_apis`（辅助识别 executor abstraction 的设计意图）
