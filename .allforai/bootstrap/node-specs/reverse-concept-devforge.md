---
node: reverse-concept-devforge
exit_artifacts:
  - .allforai/product-concept/product-concept.json
  - .allforai/product-concept/role-value-map.json
  - .allforai/product-concept/product-mechanisms.json
  - .allforai/product-concept/concept-baseline.json
  - .allforai/product-concept/concept-conflicts.json
---

# Task: DevForge 产品概念逆向提取

从 DevForge 代码结构、PLAN.md、README 逆向提取：使命、目标开发者画像、API 设计哲学、governance style、业务机制，以及检测代码与文档之间的概念冲突。

## Project Context

DevForge 是框架级 Python orchestration kernel。它的"用户"是构建 AI-assisted 开发流程的工程师或工具链开发者，不是终端消费者。评价维度是 SDK/framework，不是 consumer app。

## Context Pull

**必需（缺失则报错返回，不要继续执行）：**
- 从 `.allforai/bootstrap/source-summary.json` 读取 `modules[]` 字段，
  用于了解模块边界，作为 JTBD 提取和 governance style 识别的基础。
- 从 `.allforai/bootstrap/file-catalog.json` 读取 `modules[].key_files` 字段，
  用于确定要读取哪些源文件进行概念证据提取。

**可选（缺失则输出 warning 后继续）：**
- 从 `.allforai/bootstrap/infrastructure-profile.json` 读取 `subprocess_executors` 字段，
  用于理解 executor abstraction 的范围和设计意图。缺失时从 executors/ 模块代码直接读取。

## Theory Anchors

**来自 sdk.md（SDK 领域替代关系）：**
- `developer-persona-definition` 替代 `user-role-definition`：DevForge 的"用户"是开发者，分层（初级集成者 / 高级定制者 / 框架维护者）
- `api-philosophy` 是 SDK 概念的核心：DevForge 选择了什么设计哲学？Explicit over Implicit？Progressive Disclosure？
- `dogfooding` 替代 concept-validation：DevForge 对自身仓库的自托管尝试就是最强的 dogfooding 验证
- `distribution-model` 替代 `business-model`：DevForge 目前是开源 Python package（pip/uv），无商业化

**来自 reverse-concept.md（逆向提取策略）：**
- Mission 提取：`README.md` 是首要来源，PLAN.md 是架构意图来源
- JTBD 提取：每个主要 graph node（`batch_dispatch`、`concept_collection` 等）= 一个 Job domain
- Role-Value：`executors/` 中的 adapter 类型揭示外部角色边界
- Governance：`state/work_package.py` 中的 status lifecycle 揭示 governance style
- Business Model：`pyproject.toml`、LICENSE（如有）揭示分发模式

**来自 cross-phase-protocols.md §A.1：**
- concept-baseline.json 必须 < 2KB，包含 mission + roles + governance_styles + errc_highlights
- 所有下游节点自动加载 concept-baseline.json

## Guidance

### Mission 提取

从 README 第一段 + PLAN.md Goal 章节提炼：
- 帮助「谁」（target developer）
- 实现「什么目标」（orchestrate software development at kernel level）
- 通过「什么机制」（LangGraph state machine + role-driven executor dispatch）

### Developer Personas（替代 user roles）

DevForge 有三类开发者用户：
1. **集成使用者**：运行 `devforge snapshot` 或 `devforge init`，关心 CLI 易用性和 fixture 示例
2. **自定义扩展者**：实现自己的 ExecutorAdapter 或修改 project config，关心 adapter interface 稳定性
3. **框架贡献者/维护者**：修改 graph nodes、planning 逻辑或添加新 executor，关心 RuntimeState 结构和 LangGraph 依赖

从代码中寻找每类用户的证据：
- `main.py` 入口命令 → 集成使用者 JTBD
- `executors/base.py` Protocol 定义 → 扩展者 JTBD
- `graph/builder.py`、`graph/nodes.py` → 贡献者 JTBD

### API 哲学提取

扫描以下证据：
- `executors/base.py`：adapter Protocol — Explicit 还是 Convention-based？
- `graph/runtime_state.py`：RuntimeState dataclass — 显式字段 or 动态字典？
- `executors/pull_policy.py`：pull policy 设计 — 零配置 or 显式声明？
- `config/project_config.py`：配置覆盖机制 — 分层 or 全量替换？
- `main.py` `init` 命令：wizard-style onboarding 还是配置文件优先？

期望归纳出 1-2 个核心哲学，如："Python owns orchestration，executor owns bounded work"（来自 PLAN.md 设计原则）。

### Governance Style

从 `state/work_package.py` WorkPackageStatus 状态机提取：
```
proposed → ready → running → blocked/waiting_review → completed/verified/failed/deprecated
```
这是一个 **explicit multi-stage approval workflow**，不是 auto-review。

从 `planning/retry_policy.py`、`planning/retry_decision.py` 提取重试治理规则。
从 `graph/builder.py` 中的 seeding 逻辑提取 work 生成的 governance。

### 冲突检测（MANDATORY）

检查以下维度：

| 冲突类型 | 检查方式 |
|---------|---------|
| doc_vs_code | PLAN.md 说"Phase 1 includes seam schema" → 检查 `seams/verifier.py` 实现程度是否与 Phase 1 描述匹配 |
| doc_vs_code | README 说"98 passed" → 实际当前是 256 passed |
| module_vs_module | `executors/stubs.py` 存在 stub adapter → 检查是否与 `executors/adapters.py` 实现有冲突 |
| schema_vs_logic | `state/` 中某些字段是否在任何代码中被读写（orphaned fields？） |
| config_vs_impl | `llm.yaml` 中定义的 provider 是否都在 `llm/` 中有对应实现 |

将所有发现写入 `concept-conflicts.json`，高严重度冲突呈现给用户确认。

### Evidence-Based Extraction 规则

每个 claim 必须附 code evidence：
```json
{
  "claim": "DevForge 使用显式的 work package lifecycle 替代隐式的 chat history 状态",
  "evidence": [
    "src/devforge/state/work_package.py:10-20 — WorkPackageStatus literal 定义了 9 种明确状态",
    "src/devforge/graph/builder.py — seeding functions 根据状态机转换决定下一步工作"
  ]
}
```

### Quality Bar

- 每个 JTBD 至少 2 个代码证据
- developer personas 必须有不同的 operation profile（使用频率/关注点不同）
- governance style 必须对应 status 字段和 admin-like 控制路径
- business model 记录为"开源 Python package，无商业化，分发通过 PyPI/uv"（即使没有 payment 代码，也要明确记录）
- concept-baseline.json < 2KB

## Exit Artifacts

### `.allforai/product-concept/product-concept.json`

SDK-adapted product-concept schema：
```json
{
  "schema_version": "1.0",
  "product_name": "devforge",
  "mission": "<Help [target developer] achieve [outcome] by [mechanism]>",
  "target_developers": [
    {
      "persona": "<name>",
      "level": "beginner | intermediate | advanced",
      "primary_jtbd": "<job to be done>",
      "success_criteria": "<how they know it worked>"
    }
  ],
  "core_capabilities": [
    {
      "id": "<string>",
      "name": "<string>",
      "jtbd": "<job this capability serves>",
      "evidence": ["<file:line references>"]
    }
  ],
  "api_philosophy": {
    "primary": "<philosophy name>",
    "evidence": ["<file:line>"],
    "rationale": "<why this was chosen>"
  },
  "errc_highlights": {
    "must_have": ["<core capabilities>"],
    "differentiators": ["<what makes devforge unique vs raw LangGraph>"],
    "eliminate": ["<explicitly out of scope>"],
    "reduce": ["<intentionally simplified>"]
  },
  "mvp_capabilities": ["<id refs>"],
  "post_launch_capabilities": ["<id refs>"]
}
```

### `.allforai/product-concept/role-value-map.json`

```json
{
  "roles": [
    {
      "id": "<string>",
      "name": "<developer persona name>",
      "jobs": ["<JTBD list>"],
      "pains": ["<pain points with current alternatives>"],
      "gains": ["<gains from using devforge>"],
      "operation_profile": {
        "frequency": "daily | weekly | occasional",
        "primary_interface": "CLI | Python API | config files"
      }
    }
  ]
}
```

### `.allforai/product-concept/product-mechanisms.json`

```json
{
  "governance_styles": [
    {
      "domain": "<e.g. work package lifecycle>",
      "style": "<auto_review | manual_approval | multi_stage>",
      "evidence": ["<file:line>"]
    }
  ],
  "system_boundaries": {
    "in_scope": ["<what devforge owns>"],
    "external": ["<what executors own>", "<what LLM providers own>"]
  },
  "content_lifecycle": {
    "stages": ["<work package status progression>"],
    "transitions": ["<who/what triggers each transition>"]
  }
}
```

### `.allforai/product-concept/concept-baseline.json`

Compact (<2KB) baseline per `cross-phase-protocols.md §A.1` schema. Must include:
- `mission`
- `target_market` (developer personas summary)
- `roles[]` (developer types with high_frequency_tasks)
- `governance_styles[]`
- `errc_highlights` (must_have + differentiators)

### `.allforai/product-concept/concept-conflicts.json`

Per `reverse-concept.md` conflict schema. Include `summary.total` even if zero.

## Downstream Contract

→ `analyze-and-generate-devforge` 读取：
- `concept-baseline.json` → `mission`, `roles`, `errc_highlights`（一致性检查基线）
- `concept-conflicts.json` → `conflicts[]`（避免基于矛盾信息做分析）
- `product-concept.json` → `core_capabilities[]`, `api_philosophy`（API surface 分析的框架）
- `role-value-map.json` → `roles[].jobs`, `roles[].operation_profile`（developer journey 设计依据）
