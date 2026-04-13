---
node: analyze-and-generate-devforge
exit_artifacts:
  - .allforai/product-map/api-surface.json
  - .allforai/product-map/developer-personas.json
  - .allforai/product-map/developer-journey.json
  - .allforai/product-map/business-flows.json
  - .allforai/product-map/usage-patterns.json
  - .allforai/sdk-design/documentation-plan.json
---

# Task: DevForge SDK 分析与产物生成

以 concept-baseline 为参照，对 DevForge 做 SDK-style 分析并生成完整结构化产物：API surface map、developer journey、usage patterns 和文档规划。

## Project Context

DevForge 是 framework-level Python orchestration kernel，属于 SDK/library 领域。
分析使用 SDK 特化模式（sdk.md §二替代关系）：
- API surface 替代 task-inventory
- developer journey 替代 experience-map
- usage patterns 替代 use-case-tree
- documentation-plan 替代 ui-design

## Context Pull

**必需（缺失则报错返回，不要继续执行）：**
- 从 `.allforai/product-concept/concept-baseline.json` 读取 `mission`, `roles`, `errc_highlights`，
  用于 API surface 分析的一致性基线检查，避免循环分析。
- 从 `.allforai/product-concept/concept-conflicts.json` 读取 `conflicts[]`，
  用于了解哪些概念存在冲突，避免基于矛盾信息做分析。
- 从 `.allforai/bootstrap/source-summary.json` 读取 `modules[]`，
  用于确定 API surface 扫描的模块范围。
- 从 `.allforai/bootstrap/file-catalog.json` 读取 `modules[].key_files`，
  用于定位要读取的核心 API 定义文件。

**可选（缺失则输出 warning 后继续）：**
- 从 `.allforai/product-concept/product-concept.json` 读取 `core_capabilities[]`, `api_philosophy`，
  用于 API surface 组织结构的参考框架。缺失时从代码直接推断。
- 从 `.allforai/product-concept/role-value-map.json` 读取 `roles[].operation_profile`，
  用于 developer journey 的阶段设计。缺失时从测试用例推断。

## Theory Anchors

**来自 sdk.md §四：**

| 分析维度 | 理论锚点 |
|---------|---------|
| API surface | Principle of Least Astonishment, Pit of Success, Huffman Coding for APIs |
| API ergonomics | 5-Minute Rule, Cognitive Dimensions, Progressive Disclosure |
| Developer journey | Developer Experience (DX), Diátaxis Documentation Framework |
| Error design | Midori Error Model, Actionable Errors |

**来自 product-analysis.md（SDK 专业化）：**
- SDK/Library archetype → "No roles. API surface replaces tasks. Usage patterns replace use-cases."
- 输出使用自定义 schema，不强制套 web-app 模式
- 分析 business intent，不是 implementation detail

**来自 cross-phase-protocols.md §A（Push-Pull）：**
- concept-baseline 已加载 → 分析有独立基线参照，避免循环
- 每个产物都要检查与 concept-baseline 的一致性

## Guidance

### API Surface 分析

扫描以下核心公开接口并分类：

**Tier 1 — 主入口（最常用）：**
- `graph/builder.py::run_cycle(snapshot, persistence?)` — 核心运行时接口
- `main.py::main(argv?)` — CLI 入口
- `main.py::run_fixture_cycle(fixture_name)` — fixture 快速验证接口
- `main.py::run_snapshot_cycle(path, ...)` — snapshot 运行接口

**Tier 2 — 扩展接口（adapter 实现者使用）：**
- `executors/base.py` — ClaudeCodeTaskRequest, CodexTaskRequest, ExecutorDispatch 等
- `executors/adapters.py` — BaseExecutorAdapter, ClaudeCodeAdapter, CodexAdapter, PythonAdapter
- `executors/subprocess_transport.py` — SubprocessTransport
- `persistence/store.py` — Store interface

**Tier 3 — 配置/状态接口（advanced users）：**
- `state/workspace.py` — WorkspaceState
- `state/work_package.py` — WorkPackage
- `state/project.py` — ProjectState
- `config/project_config.py` — ProjectConfig, llm_preferences, knowledge_preferences
- `llm/config.py`, `llm/factory.py` — LLM 配置接口

对每个 Tier，评估：
- **Least Astonishment**：参数命名、返回类型、异常类型是否符合 Python 惯例？
- **Pit of Success**：默认行为是否安全？是否需要额外配置才能出错？
- **Progressive Disclosure**：基础用法是否简洁，高级用法是否可达？

### Developer Journey 分析（替代 experience-map）

基于 sdk.md 的 developer journey：
```
发现 → 评估 → 集成 → 使用 → 扩展 → 贡献
```

对每个阶段，从代码 + 文档证据确认：
- **发现**：README 是否清晰描述了价值主张？PLAN.md 是否可读？
- **评估**：有 fixture 示例、有 `devforge fixture game_project` 快速验证 — 5分钟规则能否通过？
- **集成**：`devforge init` 流程；`devforge init --workspace` 多项目模式；snapshot 格式学习曲线
- **使用**：snapshot cycle 稳定性；project_config 覆盖机制；persistence root 配置
- **扩展**：ExecutorAdapter Protocol 实现；pull_policy_overrides；knowledge_preferences 定制
- **贡献**：graph/nodes.py 可扩展性；planning/ 逻辑的可替换性；测试套件覆盖情况

记录每个阶段的 friction points（摩擦点）和 smooth points（顺畅点）。

### Business Flows 分析

从 `tests/test_e2e_*.py` 和 `tests/fixtures/` 提取核心 business flows：

1. **New project onboarding flow**: `devforge init` → `devforge snapshot` → cycle execution
2. **Existing repo onboarding flow**: topology detection → wp-repo-onboarding → analysis_design → implementation
3. **Failed executor recovery flow**: executor exhaustion → final_fail → local acceptance fallback → report
4. **Multi-cycle continuation flow**: previous result → context carry-over → next cycle dispatch
5. **Project config override flow**: base snapshot + project_config → merged preferences → executor dispatch

每个 flow 记录：trigger、stages、termination condition、key artifacts。

### Usage Patterns 分析（替代 use-case-tree）

从 `tests/` 目录提取真实使用模式：

**基础模式：**
- `run_fixture_cycle("game_project")` — 快速验证单循环
- `run_snapshot_cycle(path)` — 从文件运行
- `run_snapshot_cycle(path, persistence_root=".devforge")` — 带持久化

**配置模式：**
- `--project-config` 覆盖单项目 llm/knowledge 偏好
- `--persistence-root` 启用 SQLite + artifact store
- `llm.yaml` 全局 LLM provider 配置

**扩展模式：**
- 实现 ExecutorAdapter Protocol（`dispatch()`, `poll()`, `normalize_result()`）
- 注册自定义 executor 到 registry
- 添加 knowledge content（domains/ 或 phases/ markdown 文件）

**诊断模式：**
- `devforge doctor` — executor 就绪检查
- `devforge repl` — 交互式 REPL session

每个模式给出：scenario、how-to、expected outcome、common gotchas。

### Documentation Plan 分析

基于 Diátaxis Framework（sdk.md §四 documentation-design）：

**当前文档状态评估：**
- Tutorials：`README.md` Quick Start → 覆盖了 fixture 运行，但缺少 "build your first custom executor" tutorial
- How-to Guides：`docs/cli.md`, `docs/project-config.md` → 存在但不完整
- API Reference：无专门 API 参考文档
- Explanation：`PLAN.md` 是架构解释文档，但面向贡献者而非集成者

**识别 documentation gaps：**
- 无 Getting Started（5分钟跑通 Hello World）
- 无 executor adapter 实现指南
- 无 snapshot JSON schema 参考
- 无 LangGraph integration 解释（为什么用 LangGraph？状态机如何工作？）
- 无 troubleshooting / FAQ

### Quality Checks（自我检查）

在生成每个产物后检查：
- api-surface.json：每个接口 item 有 tier、稳定性评估、example usage
- developer-personas.json：至少 3 个 persona，每个有 frequency + primary_interface
- developer-journey.json：6 个阶段都有 friction_points 和 smooth_points
- business-flows.json：至少 5 个 flows，每个有 trigger、stages、termination
- usage-patterns.json：至少 8 个 patterns，分 basic/config/extension/diagnostic 类别
- documentation-plan.json：覆盖 Diátaxis 4 象限，每个文档有 priority 和 current_status

## Exit Artifacts

### `.allforai/product-map/api-surface.json`

```json
{
  "tiers": [
    {
      "tier": 1,
      "name": "main entrypoints",
      "interfaces": [
        {
          "module": "<module path>",
          "name": "<function/class name>",
          "signature": "<simplified signature>",
          "intent": "<what it does>",
          "ergonomics_score": "good | ok | needs_improvement",
          "ergonomics_notes": "<specific observations>",
          "example": "<minimal usage example>"
        }
      ]
    }
  ],
  "overall_philosophy": "<extracted API philosophy>",
  "consistency_issues": ["<naming inconsistencies, API shape problems>"]
}
```

### `.allforai/product-map/developer-personas.json`

```json
{
  "personas": [
    {
      "id": "<string>",
      "name": "<persona name>",
      "level": "beginner | intermediate | advanced",
      "primary_jtbd": "<job to be done>",
      "frequency": "daily | weekly | occasional",
      "primary_interface": "CLI | Python API | config files",
      "success_looks_like": "<what success means for this persona>",
      "current_pain_points": ["<pain list>"],
      "evidence": ["<file:line references>"]
    }
  ]
}
```

### `.allforai/product-map/developer-journey.json`

```json
{
  "stages": [
    {
      "stage": "discover | evaluate | integrate | use | extend | contribute",
      "goal": "<what developer wants at this stage>",
      "devforge_touchpoints": ["<what devforge offers at this stage>"],
      "friction_points": ["<what's hard or unclear>"],
      "smooth_points": ["<what works well>"],
      "evidence": ["<file:line or doc references>"]
    }
  ]
}
```

### `.allforai/product-map/business-flows.json`

```json
{
  "flows": [
    {
      "id": "<string>",
      "name": "<flow name>",
      "trigger": "<what starts this flow>",
      "stages": ["<ordered steps>"],
      "termination": "<how the flow ends>",
      "key_artifacts": ["<state files or outputs produced>"],
      "evidence": ["<test or source file references>"]
    }
  ]
}
```

### `.allforai/product-map/usage-patterns.json`

```json
{
  "patterns": [
    {
      "id": "<string>",
      "category": "basic | config | extension | diagnostic",
      "name": "<pattern name>",
      "scenario": "<when you use this>",
      "how_to": "<code or CLI example>",
      "expected_outcome": "<what happens>",
      "common_gotchas": ["<things that go wrong>"]
    }
  ]
}
```

### `.allforai/sdk-design/documentation-plan.json`

```json
{
  "framework": "diataxis",
  "current_coverage": {
    "tutorials": "<assessment>",
    "how_to_guides": "<assessment>",
    "reference": "<assessment>",
    "explanation": "<assessment>"
  },
  "documents": [
    {
      "title": "<document title>",
      "type": "tutorial | how-to | reference | explanation",
      "audience": "<target developer persona id>",
      "priority": "high | medium | low",
      "current_status": "exists | partial | missing",
      "existing_file": "<path if exists>",
      "gap_description": "<what's missing if not complete>"
    }
  ],
  "critical_gaps": ["<highest priority missing docs>"]
}
```

## Integration Points

このノードは単独ノードです。並行実装は不要です。

## Downstream Contract

このノードは最終ノードです。生成された産物は以下の目的で使用されます：
- 人間によるレビュー（concept-conflicts 解決後）
- 将来の `/run` セッションでのフォワード設計フェーズへの入力
- DevForge 自身のドキュメント改善計画の根拠
