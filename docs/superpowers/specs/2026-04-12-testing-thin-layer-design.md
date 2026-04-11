# Design: Testing Thin Layer（测试薄层机制）

**Date:** 2026-04-12
**Scope:** `knowledge/testing/`（新建知识库）+ Planner 节点规范扩展（无引擎改动）
**Goal:** 当 DevForge 指挥 Codex 生成 UI 代码时，自动产出框架感知的测试薄层（稳定选择器、helper wrapper、脆弱层补偿），消除后续 E2E 节点对脆弱 UI 选择器的依赖。

---

## 背景

当前 DevForge workflow 中，代码生成节点（Codex 执行）产出的 UI 代码不携带测试基础设施：
- 无稳定选择器（data-testid / ValueKey / accessibilityIdentifier）
- 无 helper wrapper 抽象脆弱的框架 API（scroll、gesture、async wait 等）
- E2E 测试节点直接调用框架原生 API，随布局/文案/动画变化频繁断裂

参考来源：myskills `deadhunt/phase3/helper-rules.md` + `testforge/phase0-profile.md`

---

## 方案选择

**选择方案 A（knowledge_ref 注入）+ 方案 C（Planner 感知）的组合**

- 零引擎改动，纯知识库 + Planner goal 规范
- tech-profile 节点作为 workflow 首节点，输出框架画像
- Planner 读 tech-profile.json，为每个 UI 代码节点挂对应框架的 knowledge_refs
- 代码节点 exit_artifacts 包含 ui_helper 文件，引擎的"文件即真相"机制自动强制其存在

---

## 核心概念：框架能力矩阵

每个测试框架对 8 条脆弱层的原生支持程度不同，薄层策略随之而变：

| 原生支持程度 | 薄层策略 | 说明 |
|---|---|---|
| `covered` | `thin` | 框架已可靠覆盖，helper 仅做薄封装统一调用风格 |
| `partial` | `supplement` | 框架有基础支持但存在边界盲点，补充缺失部分 |
| `uncovered` | `full` | 框架无内置保护，helper 提供完整实现 |
| `n/a` | `skip` | 该规则不适用于此框架（如 Web 端跳过 cross_app） |

**8 条脆弱层：**
1. element_discovery — 控件发现，禁止位置索引
2. button_trigger — 触发前确认可见且可交互
3. gesture — 手势前确认 UI 稳定（动画完成）
4. async_wait — 断言前等待数据就绪
5. system_dialog — 系统弹窗自动处理
6. keyboard_ime — 软键盘/输入法状态管理
7. scroll_container — 滚动容器内元素渲染确认
8. cross_app — 跨 App 流程状态跟踪

---

## 执行流程

### 1. `wf init <goal>` 触发 Planner

Planner 节点的 goal 包含以下判断逻辑（写入 nodes/planner.json）：

```
分析目标，制定执行节点计划。

若目标涉及 UI/前端代码：
  1. 在计划首节点加入 tech-profile 节点（depends_on: []）
  2. 所有 UI 代码节点的 depends_on 包含 "tech-profile"
  3. 所有 UI 代码节点的 knowledge_refs 包含：
     - knowledge/testing/helper-rules.md
     - knowledge/testing/frameworks/<对应框架>.md（Planner 执行后根据 tech-profile.json 填写）
  4. 所有 UI 代码节点的 exit_artifacts 包含对应模块的 helper_file 路径

若目标为纯后端（重构、数据分析、API 开发无前端）：
  跳过 tech-profile 节点，不加测试薄层相关 knowledge_refs
```

### 2. tech-profile 节点执行

```json
{
  "id": "tech-profile",
  "capability": "tech-profiling",
  "goal": "扫描项目技术栈和 UI 测试基础设施，输出 tech-profile.json。\n\n参照 knowledge/testing/profile-rules.md 执行。\n\n输出到 .devforge/artifacts/tech-profile.json",
  "exit_artifacts": [".devforge/artifacts/tech-profile.json"],
  "knowledge_refs": ["knowledge/testing/profile-rules.md"],
  "executor": "codex",
  "mode": null,
  "depends_on": []
}
```

### 3. `tech-profile.json` 数据结构

```json
{
  "modules": [
    {
      "module_id": "frontend",
      "path": "src/",
      "framework": "Playwright",
      "helper_file": "src/tests/helpers/ui_helper.ts",
      "ui_locator_coverage": {
        "rate": 0.71,
        "level": "high",
        "stable_patterns": ["data-testid='*'"],
        "unstable_risk": "low"
      },
      "layers": {
        "element_discovery":  { "native": "partial",   "helper": "supplement" },
        "button_trigger":     { "native": "partial",   "helper": "supplement" },
        "gesture":            { "native": "covered",   "helper": "thin" },
        "async_wait":         { "native": "partial",   "helper": "supplement" },
        "system_dialog":      { "native": "covered",   "helper": "thin" },
        "keyboard_ime":       { "native": "covered",   "helper": "thin" },
        "scroll_container":   { "native": "covered",   "helper": "thin" },
        "cross_app":          { "native": "n/a",       "helper": "skip" }
      }
    }
  ],
  "backend_modules": ["api/"],
  "platforms": ["web"]
}
```

**多模块项目**（如 Flutter App + React Admin）：`modules` 数组包含多条记录，每条有独立的 `framework` 和 `layers` 评估。

### 4. Planner 执行后（depends_on: ["tech-profile"]）

Planner 读 tech-profile.json，为每个 UI 代码节点生成自包含 goal：

```
示例节点 goal（自包含）：
"实现用户注册功能（src/auth/Register.tsx）。

测试薄层要求（参照 knowledge/testing/helper-rules.md + knowledge/testing/frameworks/playwright.md）：
- 所有可交互元素（按钮、输入框、链接）必须加 data-testid
- 参照 tech-profile.json 中 frontend 模块的 layers 评估：
  - element_discovery（partial → supplement）：生成 findElement() helper
  - async_wait（partial → supplement）：生成 waitForData() helper
  - gesture/system_dialog/keyboard_ime/scroll_container（covered → thin）：薄封装统一调用风格
- 若 src/tests/helpers/ui_helper.ts 已存在，只补充缺失的 supplement/full 层，不重写已有实现
- helper 文件输出到 src/tests/helpers/ui_helper.ts

exit_artifacts: [src/auth/Register.tsx, src/tests/helpers/ui_helper.ts]"
```

---

## 知识库结构

```
knowledge/testing/
├── profile-rules.md          # tech-profile 节点的扫描规范
├── helper-rules.md           # 8 条脆弱层规则（通用，框架无关）
└── frameworks/
    ├── xcuitest.md           # iOS 原生：scroll/gesture 原生覆盖好，IME 需 full
    ├── patrol.md             # Flutter：scroll/keyboard 需 full，gesture partial
    ├── playwright.md         # Web：大部分 covered，cross_app skip
    └── jest-rtl.md           # React 单测：无 E2E 场景，仅 element_discovery 薄层
```

### `profile-rules.md` 内容规范

```markdown
## 目标
扫描项目，输出 .devforge/artifacts/tech-profile.json

## Step 1：识别框架
扫描依赖声明文件：
- package.json → playwright / jest / vitest / cypress / detox
- pubspec.yaml → patrol / flutter_test
- *.xcodeproj / Package.swift → XCUITest
- build.gradle → Espresso / UIAutomator

## Step 2：UI 定位覆盖率审计（按 module）
- Web：data-testid / aria-label / role 在可交互元素上的覆盖率
- Flutter：ValueKey / Semantics label 的覆盖率
- iOS：accessibilityIdentifier 的覆盖率
- Android/RN：testID / contentDescription 的覆盖率
覆盖率 > 70% → high；30–70% → medium；< 30% → low

## Step 3：8 层能力评估（对每个 module 的框架）
按 helper-rules.md 的 8 条规则，评估每层 native 支持程度（covered/partial/uncovered/n/a）

## Step 4：多模块处理
- 每个有 UI 的 module 独立评估、独立指定 helper_file 路径
- 后端 module（无 UI）记入 backend_modules，不评估

## Step 5：输出
写入 .devforge/artifacts/tech-profile.json
```

### `helper-rules.md` 内容规范

移植自 myskills `deadhunt/phase3/helper-rules.md`，包含：
- 核心原则：补充，不替代
- 8 条脆弱层规则（见上方定义）
- Helper 文件生成原则（测试代码全部通过 helper 调用，不直接调用框架原生 API）
- 截图规则（断言失败时自动截图）

### 框架文件内容规范（以 `playwright.md` 为例）

```markdown
## Playwright 框架能力矩阵

| 层 | 原生支持 | 薄层策略 | 说明 |
|---|---|---|---|
| element_discovery | partial | supplement | locator() 可靠，但无覆盖率检查；helper 补充 SELECTOR_UNSTABLE 标记 |
| button_trigger | partial | supplement | 无内置 enabled 状态前置检查；helper 补充 |
| gesture | covered | thin | page.mouse / drag_and_drop 完善 |
| async_wait | partial | supplement | waitForSelector 可用，但超时报错不含业务语义；helper 补充有意义的错误信息 |
| system_dialog | covered | thin | page.on('dialog') 原生支持 |
| keyboard_ime | covered | thin | fill() 处理 Unicode；IME 组合态桌面端已覆盖 |
| scroll_container | covered | thin | scroll_into_view_if_needed() 可靠 |
| cross_app | n/a | skip | Web 无跨 App 场景 |

## Helper 示例（supplement 层）

\`\`\`typescript
// element_discovery supplement
async function findElement(page: Page, testId: string) {
  const el = page.getByTestId(testId);
  if (!await el.isVisible()) {
    throw new Error(`[SELECTOR_UNSTABLE] Element data-testid="${testId}" not found`);
  }
  return el;
}

// async_wait supplement
async function waitForData(page: Page, testId: string, timeout = 5000) {
  await page.waitForSelector(`[data-testid="${testId}"]`, {
    state: 'visible', timeout,
    message: `等待数据加载：data-testid="${testId}" 未在 ${timeout}ms 内出现`
  });
}
\`\`\`
```

---

## 思维测试验证（Gap 分析）

| Gap | 描述 | 修法 |
|---|---|---|
| #1 | Planner 依赖 tech-profile.json，但 tech-profile 是 Planner 输出的节点 | tech-profile 由 Planner 创建为首节点（depends_on: []），Planner 本身 depends_on: ["tech-profile"] 不成立——tech-profile 在 Planner 的**输出计划**中，不是 Planner 的**前置依赖**。Planner goal 写明若涉及 UI 则在计划首节点加入 tech-profile |
| #2 | 纯后端 workflow 不应加 tech-profile | Planner 根据 goal 文本判断是否涉及 UI，仅在 UI workflow 中加入 tech-profile 节点 |
| #3 | 多模块项目需要为不同模块挂不同 framework 文档 | Planner 读 tech-profile.json 的 modules 数组，为每个代码节点按 module_id 匹配对应 frameworks/ 文档 |
| #4 | ui_helper.ts 已存在时不应重写 | 节点 goal 中明确写：若 helper 文件已存在，只补充 partial/uncovered 层，不重写已有实现 |

---

## 文件变更

| 文件 | 变更类型 |
|---|---|
| `knowledge/testing/profile-rules.md` | 新建 |
| `knowledge/testing/helper-rules.md` | 新建（移植自 myskills） |
| `knowledge/testing/frameworks/xcuitest.md` | 新建 |
| `knowledge/testing/frameworks/patrol.md` | 新建 |
| `knowledge/testing/frameworks/playwright.md` | 新建 |
| `knowledge/testing/frameworks/jest-rtl.md` | 新建 |

**引擎侧零改动。** 全部为知识库内容文件，Planner goal 规范写入 `nodes/planner.json`（已有机制）。

---

## 测试策略

- **不测知识文件本身**（内容正确性由 LLM 执行时验证）
- **integration test（mock Codex）**：
  - tech-profile 节点执行后，验证 `.devforge/artifacts/tech-profile.json` 存在且含正确 framework 字段
  - Planner 节点读取 tech-profile.json 后，生成的节点计划中 UI 节点包含 `knowledge/testing/helper-rules.md` 和对应框架文档
  - 代码节点的 exit_artifacts 包含 helper_file 路径，引擎强制其存在

---

## 不在本子项目范围内

- 实际运行 E2E 测试并收集结果（属于 testforge workflow，不是薄层生成）
- helper 文件的质量评分或覆盖率统计（属于后续迭代）
- 框架文件以外的测试框架（遇到新框架时 LLM 参照已有框架文件自行适配）
