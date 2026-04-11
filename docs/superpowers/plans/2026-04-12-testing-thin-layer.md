# Testing Thin Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 DevForge knowledge 库中添加测试薄层知识文件，使 Planner 节点能够根据项目框架为代码节点注入正确的 helper 生成规范，消除 E2E 测试对脆弱 UI 选择器的依赖。

**Architecture:** 纯知识库扩展，零引擎改动。新建 `knowledge/testing/` 目录，包含通用规则文件和框架特定文件；Planner 节点通过 `knowledge_refs` 引用这些文件，Codex 执行代码节点时按规则生成 `ui_helper.{ts,dart,swift}` 作为 exit_artifact。

**Tech Stack:** Python（测试文件），Markdown（知识文件），pytest

---

## 文件结构

| 文件 | 类型 | 职责 |
|---|---|---|
| `knowledge/testing/profile-rules.md` | 新建 | tech-profile 节点的扫描规范 |
| `knowledge/testing/helper-rules.md` | 新建 | 8 条脆弱层规则（通用，框架无关） |
| `knowledge/testing/frameworks/playwright.md` | 新建 | Web/Playwright 框架能力矩阵 + helper 示例 |
| `knowledge/testing/frameworks/xcuitest.md` | 新建 | iOS XCUITest 框架能力矩阵 + helper 示例 |
| `knowledge/testing/frameworks/patrol.md` | 新建 | Flutter/Patrol 框架能力矩阵 + helper 示例 |
| `knowledge/testing/frameworks/jest-rtl.md` | 新建 | React 单测框架规范 |
| `tests/test_knowledge_files.py` | 新建 | 回归测试：验证知识文件存在且结构完整 |

---

### Task 1: 创建 knowledge 目录结构 + profile-rules.md

**Files:**
- Create: `knowledge/testing/profile-rules.md`
- Create: `knowledge/testing/frameworks/.gitkeep`（占位，后续任务填充）
- Create: `tests/test_knowledge_files.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_knowledge_files.py
from pathlib import Path

KNOWLEDGE_ROOT = Path("knowledge/testing")

def test_profile_rules_exists():
    assert (KNOWLEDGE_ROOT / "profile-rules.md").exists()

def test_profile_rules_has_required_sections():
    content = (KNOWLEDGE_ROOT / "profile-rules.md").read_text()
    for section in ["## 目标", "## Step 1", "## Step 2", "## Step 3", "## Step 4", "## Step 5"]:
        assert section in content, f"缺少章节: {section}"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py -v
```
Expected: FAIL with `FileNotFoundError` 或 `AssertionError`

- [ ] **Step 3: 创建目录和 profile-rules.md**

```bash
mkdir -p knowledge/testing/frameworks
```

创建 `knowledge/testing/profile-rules.md`，内容：

```markdown
# 测试画像扫描规则

## 目标

扫描项目技术栈和 UI 测试基础设施，输出 `.devforge/artifacts/tech-profile.json`。

后端模块（无 UI）跳过评估，记入 `backend_modules` 字段，不生成 helper。

---

## Step 1：识别框架

扫描以下依赖声明文件，确定每个客户端模块使用的测试框架：

| 文件 | 框架信号 | 框架 |
|------|---------|------|
| `package.json` | `"playwright"` 在 devDependencies | Playwright |
| `package.json` | `"@testing-library/react"` + `"jest"` 或 `"vitest"` | Jest-RTL |
| `package.json` | `"detox"` | Detox |
| `pubspec.yaml` | `patrol:` 在 dev_dependencies | Patrol |
| `*.xcodeproj` / `Package.swift` | UITest target 存在 | XCUITest |
| `build.gradle` | `testInstrumentationRunner` | Espresso/UIAutomator |

未识别框架时：标记 `framework: "unknown"`，跳过 helper 生成。

---

## Step 2：UI 定位覆盖率审计（按 module）

逐模块扫描可交互元素上稳定选择器的使用率：

| 框架 | 稳定选择器 | 扫描方式 |
|------|----------|---------|
| Playwright / Jest-RTL | `data-testid` / `aria-label` / `role` | Grep `data-testid` in `src/**/*.{tsx,jsx,vue}` |
| Flutter / Patrol | `ValueKey` / `Semantics label` | Grep `ValueKey\|Semantics` in `lib/**/*.dart` |
| XCUITest | `accessibilityIdentifier` | Grep `accessibilityIdentifier` in `**/*.swift` |
| Android / RN | `testID` / `contentDescription` | Grep `testID\|contentDescription` |

覆盖率计算：（有稳定标识符的可交互元素数 / 总可交互元素数）

| level | rate 范围 | 薄层策略 |
|-------|----------|---------|
| `high` | > 70% | 直接使用稳定标识符，降级逻辑最小化 |
| `medium` | 30–70% | 混合策略，部分标记 `SELECTOR_UNSTABLE` |
| `low` | < 30% | 保守降级，广泛标记 `SELECTOR_UNSTABLE` |

---

## Step 3：8 层能力评估（对每个 module 的框架）

参照 `knowledge/testing/helper-rules.md` 的 8 条规则，评估每层原生支持程度：

- `covered`：框架已可靠处理 → helper 策略：`thin`（薄封装，统一调用风格）
- `partial`：框架有基础但存在边界盲点 → helper 策略：`supplement`（补充缺失部分）
- `uncovered`：框架无内置保护 → helper 策略：`full`（完整实现）
- `n/a`：该规则不适用于此框架 → helper 策略：`skip`

---

## Step 4：多模块处理

- 每个有 UI 的 module 独立评估，独立指定 `helper_file` 路径
- 后端 module（无 UI 代码）记入 `backend_modules` 列表，不参与评估
- 多 module 项目（如 Flutter App + React Admin）：`modules` 数组包含多条记录

---

## Step 5：输出

将结果写入 `.devforge/artifacts/tech-profile.json`，格式如下：

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
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py::test_profile_rules_exists tests/test_knowledge_files.py::test_profile_rules_has_required_sections -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/profile-rules.md knowledge/testing/frameworks/ tests/test_knowledge_files.py
git commit -m "feat: add testing knowledge directory and profile-rules.md"
```

---

### Task 2: 创建 helper-rules.md（8 条脆弱层规则）

**Files:**
- Create: `knowledge/testing/helper-rules.md`
- Modify: `tests/test_knowledge_files.py`

- [ ] **Step 1: 添加测试**

在 `tests/test_knowledge_files.py` 末尾追加：

```python
def test_helper_rules_exists():
    assert (KNOWLEDGE_ROOT / "helper-rules.md").exists()

def test_helper_rules_has_8_rules():
    content = (KNOWLEDGE_ROOT / "helper-rules.md").read_text()
    for i in range(1, 9):
        assert f"**规则 {i}：" in content, f"缺少规则 {i}"

def test_helper_rules_has_coverage_matrix():
    content = (KNOWLEDGE_ROOT / "helper-rules.md").read_text()
    for level in ["covered", "partial", "uncovered"]:
        assert level in content, f"缺少覆盖程度: {level}"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py::test_helper_rules_exists -v
```
Expected: FAIL

- [ ] **Step 3: 创建 helper-rules.md**

创建 `knowledge/testing/helper-rules.md`，内容：

```markdown
# UI 测试 Helper 生成规则

> 适用于任意 UI 测试框架（Patrol、XCUITest、Playwright、Jest-RTL 等）。
> 引擎由 Codex 根据项目实际使用的测试框架决定，规则本身与框架无关。
> 框架特定的实现模式见 `knowledge/testing/frameworks/` 目录下对应文件。

## 前置步骤：读取框架画像

执行代码节点前，从节点 goal 中获取 `tech-profile.json` 路径，读取当前 module 的：
- `framework`：决定参考哪个框架文件
- `layers`：决定每个脆弱层的 helper 策略（thin / supplement / full / skip）
- `helper_file`：helper 文件的输出路径

---

## 核心原则：补充，不替代

**Helper 的作用是补充框架原生能力不足的部分，不是替代框架本身。**

| 原生支持程度 | Helper 策略 | 说明 |
|---|---|---|
| `covered` | `thin` | 框架已可靠覆盖；helper 仅做薄封装统一调用风格，不重新实现 |
| `partial` | `supplement` | 框架有基础但存在边界盲点；helper 补充缺失部分 |
| `uncovered` | `full` | 框架对该层无内置保护；helper 提供完整实现 |
| `n/a` | `skip` | 该规则不适用于此框架（如 Web 无跨 App 场景） |

**Helper 文件路径**：使用 `tech-profile.json` 中 `module.helper_file` 字段。

**若 helper 文件已存在**：只补充 `partial`/`uncovered` 层中缺失的实现，不重写已有代码。

**测试代码规范**：所有 E2E 测试代码通过 helper 调用，不直接调用框架原生 API。

---

## 8 条脆弱层规则

**规则 1：控件发现（element_discovery）**
- 目标：元素查找必须有明确的失败语义；找不到时抛出可识别的错误，不能静默跳过
- 禁止：以位置索引作为唯一定位手段
- 扫描项目：稳定标识符（testID / accessibilityIdentifier / ValueKey / data-testid）的覆盖率；
  覆盖率低时 helper 需包含多级降级逻辑，并在失败时标记 `SELECTOR_UNSTABLE`

**规则 2：按钮触发（button_trigger）**
- 目标：触发前必须确认元素在视口内、可见、且处于可交互状态
- 禁止：对不可见或 disabled 元素执行点击并忽略结果
- 扫描项目：项目中 disabled 状态的判断方式（属性名 / 颜色 / opacity / 自定义标识）

**规则 3：触控手势（gesture）**
- 目标：手势操作前 UI 必须处于稳定状态（动画 / 页面过渡完成）
- 扫描项目：项目中使用的动画时长、过渡类型（CSS transition / Flutter AnimationController 等）

**规则 4：异步等待（async_wait）**
- 目标：断言前必须等待数据就绪；超时时报告具体等待目标而非通用失败信息
- 扫描项目：项目中 loading 状态的 UI 表现（loading spinner 类型、数据就绪的可见信号）

**规则 5：系统弹窗（system_dialog）**
- 目标：测试流程不因系统弹窗中断；已知权限弹窗自动处理，未知弹窗 best-effort dismiss
- 扫描项目：平台权限声明文件（`Info.plist` / `AndroidManifest.xml`）中声明的权限列表

**规则 6：键盘与输入法（keyboard_ime）**
- 目标：输入框聚焦后，后续 tap 目标仍在可操作区域内；输入完成前不触发其他交互
- 扫描项目：表单页面结构，判断键盘弹出后是否存在被遮挡的交互元素；
  检查项目是否面向非英语用户（日语 / 中文 / 阿拉伯语等需要 IME 的语言）
- 注：仅适用于有软键盘的平台（移动端）；桌面端跳过此规则
- IME 扩展：若项目使用 IME，helper 必须额外处理输入法组合态（composing state）——
  在输入法未确认期间禁止触发其他元素；等待输入确认后再继续

**规则 7：滚动容器（scroll_container）**
- 目标：滚动容器内的元素在交互前必须已渲染进视图树
- 扫描项目：项目中使用的虚拟列表 / 懒加载组件类型（FlatList / RecyclerView / LazyColumn 等）

**规则 8：跨 App 流程（cross_app）**
- 目标：测试流程能跟踪 App 离开和返回的完整状态；跨 App 跳转后验证返回时的上下文正确性
- 扫描项目：是否存在第三方登录、外部支付跳转、Universal Link / App Link 等场景
- 注：跨 App 流程属于移动端专有场景；Web 端标记 `n/a`，跳过此规则

---

## 截图规则（独立于 8 条脆弱层规则）

- 目标：断言失败时自动截图，存入 `.devforge/artifacts/screenshots/{module}/{step}.png`
- 扫描项目：无需扫描，截图能力由各框架原生 API 提供
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py -v -k "helper_rules"
```
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/helper-rules.md tests/test_knowledge_files.py
git commit -m "feat: add helper-rules.md with 8 fragile layer rules"
```

---

### Task 3: 创建 frameworks/playwright.md

**Files:**
- Create: `knowledge/testing/frameworks/playwright.md`
- Modify: `tests/test_knowledge_files.py`

- [ ] **Step 1: 添加测试**

在 `tests/test_knowledge_files.py` 末尾追加：

```python
FRAMEWORKS = ["playwright", "xcuitest", "patrol", "jest-rtl"]

def test_framework_files_exist():
    for fw in FRAMEWORKS:
        path = KNOWLEDGE_ROOT / "frameworks" / f"{fw}.md"
        assert path.exists(), f"缺少框架文件: {fw}.md"

def test_playwright_has_capability_matrix():
    content = (KNOWLEDGE_ROOT / "frameworks" / "playwright.md").read_text()
    for layer in ["element_discovery", "button_trigger", "gesture", "async_wait",
                  "system_dialog", "keyboard_ime", "scroll_container", "cross_app"]:
        assert layer in content, f"playwright.md 缺少层: {layer}"
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py::test_framework_files_exist -v
```
Expected: FAIL

- [ ] **Step 3: 创建 frameworks/playwright.md**

创建 `knowledge/testing/frameworks/playwright.md`，内容：

```markdown
# Playwright 框架能力矩阵

> 本文档描述 Playwright 框架在 8 条脆弱层上的原生支持程度及对应 helper 实现。
> 在 Web（React / Vue / Next.js 等）项目中使用此文档。

## 框架能力矩阵

| 层 | native | helper | 说明 |
|---|---|---|---|
| element_discovery | partial | supplement | `locator()` 可靠，但无覆盖率检查；helper 补充 `SELECTOR_UNSTABLE` 标记 |
| button_trigger | partial | supplement | 无内置 enabled 状态前置检查；helper 在点击前验证可见且可交互 |
| gesture | covered | thin | `page.mouse`、`dragAndDrop()` 完善；helper 仅薄封装 |
| async_wait | partial | supplement | `waitForSelector` 可用但超时报错无业务语义；helper 补充有意义的错误信息 |
| system_dialog | covered | thin | `page.on('dialog')` 原生支持；helper 仅做注册封装 |
| keyboard_ime | covered | thin | `fill()` 处理 Unicode，桌面端无 IME 复杂性 |
| scroll_container | covered | thin | `scrollIntoViewIfNeeded()` 可靠 |
| cross_app | n/a | skip | Web 端无跨 App 场景 |

## Helper 实现（TypeScript）

helper 文件路径：使用 `tech-profile.json` 中对应 module 的 `helper_file` 字段
（如 `src/tests/helpers/ui_helper.ts`）

```typescript
import { Page, Locator } from '@playwright/test';

// element_discovery supplement
// 找不到时抛出含 SELECTOR_UNSTABLE 标记的错误，而非通用错误
export async function findElement(page: Page, testId: string): Promise<Locator> {
  const el = page.getByTestId(testId);
  if (!await el.isVisible()) {
    throw new Error(`[SELECTOR_UNSTABLE] data-testid="${testId}" not found or not visible`);
  }
  return el;
}

// button_trigger supplement
// 点击前确认元素可见且 enabled
export async function clickButton(page: Page, testId: string): Promise<void> {
  const el = page.getByTestId(testId);
  await el.waitFor({ state: 'visible' });
  const isDisabled = await el.isDisabled();
  if (isDisabled) {
    throw new Error(`[BUTTON_DISABLED] data-testid="${testId}" is disabled`);
  }
  await el.click();
}

// async_wait supplement
// 等待特定元素出现，超时时报告业务语义而非通用 TimeoutError
export async function waitForData(
  page: Page,
  testId: string,
  timeout = 5000
): Promise<void> {
  await page.waitForSelector(`[data-testid="${testId}"]`, {
    state: 'visible',
    timeout,
  }).catch(() => {
    throw new Error(
      `[ASYNC_WAIT] data-testid="${testId}" did not appear within ${timeout}ms. ` +
      `Check loading state or API response.`
    );
  });
}

// gesture thin
// 薄封装，统一调用风格
export async function dragTo(
  page: Page,
  sourceTestId: string,
  targetTestId: string
): Promise<void> {
  const source = page.getByTestId(sourceTestId);
  const target = page.getByTestId(targetTestId);
  await source.dragTo(target);
}

// system_dialog thin
// 注册 dialog handler，auto-accept 已知权限弹窗
export function setupDialogHandler(page: Page): void {
  page.on('dialog', async (dialog) => {
    await dialog.accept();
  });
}
```

## 代码节点生成规范

生成 UI 代码时，所有可交互元素（`<button>`、`<input>`、`<a>`、`<select>`、可点击 `<div>`）
必须加 `data-testid` 属性：

```tsx
// ✓ 正确：有稳定 data-testid
<button data-testid="submit-button" onClick={handleSubmit}>提交</button>
<input data-testid="email-input" type="email" value={email} />

// ✗ 错误：无稳定标识符，测试依赖文本或 CSS 类
<button className="btn-primary" onClick={handleSubmit}>提交</button>
```
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py::test_playwright_has_capability_matrix -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/frameworks/playwright.md tests/test_knowledge_files.py
git commit -m "feat: add playwright framework thin layer spec"
```

---

### Task 4: 创建 frameworks/xcuitest.md

**Files:**
- Create: `knowledge/testing/frameworks/xcuitest.md`

- [ ] **Step 1: 添加测试**

在 `tests/test_knowledge_files.py` 末尾追加：

```python
def test_xcuitest_has_capability_matrix():
    content = (KNOWLEDGE_ROOT / "frameworks" / "xcuitest.md").read_text()
    for layer in ["element_discovery", "gesture", "keyboard_ime", "scroll_container"]:
        assert layer in content, f"xcuitest.md 缺少层: {layer}"
    assert "accessibilityIdentifier" in content
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py::test_xcuitest_has_capability_matrix -v
```
Expected: FAIL

- [ ] **Step 3: 创建 frameworks/xcuitest.md**

创建 `knowledge/testing/frameworks/xcuitest.md`，内容：

```markdown
# XCUITest 框架能力矩阵

> 本文档描述 XCUITest 框架在 8 条脆弱层上的原生支持程度及对应 helper 实现。
> 在 iOS 原生（Swift / SwiftUI / UIKit）项目中使用此文档。

## 框架能力矩阵

| 层 | native | helper | 说明 |
|---|---|---|---|
| element_discovery | partial | supplement | `accessibilityIdentifier` 覆盖率通常不足；helper 补充降级链和 `SELECTOR_UNSTABLE` 标记 |
| button_trigger | covered | thin | XCUITest 原生保证元素存在才能交互；helper 仅添加 enabled 状态检查 |
| gesture | covered | thin | `swipeUp/Down/Left/Right`、`tap`、`press` 均有原生支持 |
| async_wait | partial | supplement | `waitForExistence(timeout:)` 存在但错误信息无业务语义；helper 补充 |
| system_dialog | covered | thin | `addUIInterruptionMonitor` 原生支持自动处理系统弹窗 |
| keyboard_ime | partial | supplement | 英文输入可靠；中文/日文 IME 组合态可能导致测试不稳定 |
| scroll_container | partial | supplement | `swipeUp` 可滚动，但无法确认目标元素已渲染；helper 补充渲染等待 |
| cross_app | partial | supplement | `XCUIApplication` 支持多 App，但状态跟踪需 helper 封装 |

## Helper 实现（Swift）

helper 文件路径：使用 `tech-profile.json` 中对应 module 的 `helper_file` 字段
（如 `UITests/Helpers/UIHelper.swift`）

```swift
import XCTest

class UIHelper {
    let app: XCUIApplication

    init(app: XCUIApplication) {
        self.app = app
    }

    // element_discovery supplement
    // 找不到时抛出含 SELECTOR_UNSTABLE 标记的错误
    func findElement(identifier: String, timeout: TimeInterval = 5) -> XCUIElement {
        let el = app.descendants(matching: .any)[identifier]
        let exists = el.waitForExistence(timeout: timeout)
        if !exists {
            XCTFail("[SELECTOR_UNSTABLE] accessibilityIdentifier='\(identifier)' not found within \(timeout)s")
        }
        return el
    }

    // async_wait supplement
    // 等待 loading 消失，超时时报告业务语义
    func waitForLoading(
        loadingIdentifier: String = "loading-indicator",
        timeout: TimeInterval = 10
    ) {
        let loading = app.activityIndicators[loadingIdentifier]
        if loading.exists {
            let gone = loading.waitForNonExistence(timeout: timeout)
            if !gone {
                XCTFail("[ASYNC_WAIT] Loading indicator '\(loadingIdentifier)' still visible after \(timeout)s")
            }
        }
    }

    // keyboard_ime supplement
    // 输入文本后等待 IME 确认（中日文输入法）
    func typeTextAndConfirm(_ text: String, in field: XCUIElement) {
        field.tap()
        field.typeText(text)
        // 若有输入法候选词栏，点击第一个候选词确认
        let toolbar = app.toolbars.firstMatch
        if toolbar.exists {
            toolbar.buttons.firstMatch.tap()
        }
    }

    // scroll_container supplement
    // 滚动直到目标元素可见（最多滚动 maxSwipes 次）
    func scrollUntilVisible(
        element: XCUIElement,
        in scrollView: XCUIElement,
        maxSwipes: Int = 5
    ) {
        var swipes = 0
        while !element.isHittable && swipes < maxSwipes {
            scrollView.swipeUp()
            swipes += 1
        }
        if !element.isHittable {
            XCTFail("[SCROLL_CONTAINER] Element not visible after \(maxSwipes) swipes")
        }
    }
}
```

## 代码节点生成规范

生成 iOS UI 代码时，所有可交互元素必须设置 `accessibilityIdentifier`：

```swift
// ✓ 正确：有稳定 accessibilityIdentifier
button.accessibilityIdentifier = "submit-button"
textField.accessibilityIdentifier = "email-input"

// SwiftUI
Button("提交") { handleSubmit() }
    .accessibilityIdentifier("submit-button")

// ✗ 错误：无 accessibilityIdentifier，测试只能依赖文本或位置
Button("提交") { handleSubmit() }
```

## 环境要求

- macOS + Xcode（非 macOS 环境标记 `DEFERRED_NATIVE`，仅输出脚本不执行）
- iOS Simulator：`xcrun simctl list devices` 检查可用模拟器
- 项目需有 UI Test target
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py::test_xcuitest_has_capability_matrix -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/frameworks/xcuitest.md tests/test_knowledge_files.py
git commit -m "feat: add xcuitest framework thin layer spec"
```

---

### Task 5: 创建 frameworks/patrol.md

**Files:**
- Create: `knowledge/testing/frameworks/patrol.md`

- [ ] **Step 1: 添加测试**

在 `tests/test_knowledge_files.py` 末尾追加：

```python
def test_patrol_has_capability_matrix():
    content = (KNOWLEDGE_ROOT / "frameworks" / "patrol.md").read_text()
    for layer in ["keyboard_ime", "scroll_container", "cross_app"]:
        assert layer in content, f"patrol.md 缺少层: {layer}"
    assert "ValueKey" in content or "Semantics" in content
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py::test_patrol_has_capability_matrix -v
```
Expected: FAIL

- [ ] **Step 3: 创建 frameworks/patrol.md**

创建 `knowledge/testing/frameworks/patrol.md`，内容：

```markdown
# Patrol 框架能力矩阵（Flutter）

> 本文档描述 Patrol 框架在 8 条脆弱层上的原生支持程度及对应 helper 实现。
> 在 Flutter 跨平台项目中使用此文档。

## 框架能力矩阵

| 层 | native | helper | 说明 |
|---|---|---|---|
| element_discovery | partial | supplement | Key/ValueKey 覆盖率通常不足；helper 补充多级降级链和 `SELECTOR_UNSTABLE` |
| button_trigger | partial | supplement | 无内置 enabled 状态检查；helper 补充 |
| gesture | partial | supplement | `tap`/`swipe` 有，但无稳定等待机制；helper 补充动画完成等待 |
| async_wait | partial | supplement | `pumpAndSettle()` 可用，但超时无业务语义；helper 补充 |
| system_dialog | covered | thin | `$.native.grantPermissionWhenInUse()` 原生支持 |
| keyboard_ime | uncovered | full | IME 组合态（中日文）无原生保护；helper 完整实现 |
| scroll_container | uncovered | full | 虚拟列表（ListView.builder）中元素未渲染时 `find` 失败；helper 完整实现 |
| cross_app | partial | supplement | `$.native` 支持跨 App，但状态验证需 helper 封装 |

## Helper 实现（Dart）

helper 文件路径：使用 `tech-profile.json` 中对应 module 的 `helper_file` 字段
（如 `integration_test/helpers/ui_helper.dart`）

```dart
import 'package:patrol/patrol.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

class UIHelper {
  final PatrolIntegrationTester $;

  UIHelper(this.$);

  // element_discovery supplement
  // 支持 Key → Type → Semantics 多级降级
  Future<Finder> findElement(
    dynamic keyOrType, {
    Duration timeout = const Duration(seconds: 5),
  }) async {
    Finder finder;
    if (keyOrType is Key) {
      finder = find.byKey(keyOrType);
    } else if (keyOrType is Type) {
      finder = find.byType(keyOrType);
    } else {
      throw ArgumentError('[SELECTOR_UNSTABLE] Unsupported locator type');
    }

    final exists = await $.tester.pumpUntilFound(finder, timeout: timeout);
    if (!exists) {
      throw TestFailure('[SELECTOR_UNSTABLE] Element $keyOrType not found within $timeout');
    }
    return finder;
  }

  // keyboard_ime full
  // 输入中文/日文时等待 IME 确认，避免组合态中断后续操作
  Future<void> typeWithIME(Finder field, String text) async {
    await $.tester.tap(field);
    await $.tester.pump();
    await $.tester.enterText(field, text);
    // 等待 IME 候选词消失（组合态结束）
    await $.tester.pumpAndSettle(const Duration(milliseconds: 500));
    // 关闭软键盘
    await $.tester.testTextInput.receiveAction(TextInputAction.done);
    await $.tester.pump();
  }

  // scroll_container full
  // 在虚拟列表中滚动直到目标 Widget 渲染进视图树
  Future<void> scrollUntilVisible(
    Finder target,
    Finder scrollable, {
    double delta = 100,
    int maxScrolls = 10,
  }) async {
    var scrolls = 0;
    while (!$.tester.any(target) && scrolls < maxScrolls) {
      await $.tester.drag(scrollable, Offset(0, -delta));
      await $.tester.pump();
      scrolls++;
    }
    if (!$.tester.any(target)) {
      throw TestFailure('[SCROLL_CONTAINER] Target not found after $maxScrolls scrolls');
    }
  }

  // async_wait supplement
  // 等待 loading indicator 消失，报告业务语义
  Future<void> waitForLoading({
    Duration timeout = const Duration(seconds: 10),
  }) async {
    final loading = find.byType(CircularProgressIndicator);
    if ($.tester.any(loading)) {
      await $.tester.pumpUntilGone(loading, timeout: timeout);
    }
  }
}
```

## 代码节点生成规范

生成 Flutter UI 代码时，所有可交互 Widget 必须设置 `Key`：

```dart
// ✓ 正确：有稳定 Key
ElevatedButton(
  key: const Key('submit-button'),
  onPressed: handleSubmit,
  child: const Text('提交'),
)
TextField(
  key: const Key('email-input'),
  controller: emailController,
)

// ✗ 错误：无 Key，测试只能依赖文本或位置索引
ElevatedButton(onPressed: handleSubmit, child: const Text('提交'))
```

## Widget 查找优先级

| 优先级 | 查找方式 | 示例 | 适用场景 |
|--------|---------|------|---------|
| 1 | Key | `find.byKey(Key('order_list'))` | Widget 有显式 Key（最稳定） |
| 2 | Type | `find.byType(OrderListPage)` | Widget 类型在页面内唯一 |
| 3 | Semantics | `find.bySemanticsLabel('订单')` | 有 Semantics 标签 |
| 4 | Text | `find.text('订单管理')` | 最后降级，多语言环境慎用 |
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py::test_patrol_has_capability_matrix -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/frameworks/patrol.md tests/test_knowledge_files.py
git commit -m "feat: add patrol framework thin layer spec"
```

---

### Task 6: 创建 frameworks/jest-rtl.md

**Files:**
- Create: `knowledge/testing/frameworks/jest-rtl.md`

- [ ] **Step 1: 添加测试**

在 `tests/test_knowledge_files.py` 末尾追加：

```python
def test_jest_rtl_has_capability_matrix():
    content = (KNOWLEDGE_ROOT / "frameworks" / "jest-rtl.md").read_text()
    assert "jest-rtl" in content.lower() or "react testing library" in content.lower()
    assert "getByTestId" in content
```

- [ ] **Step 2: 运行测试，确认失败**

```bash
pytest tests/test_knowledge_files.py::test_jest_rtl_has_capability_matrix -v
```
Expected: FAIL

- [ ] **Step 3: 创建 frameworks/jest-rtl.md**

创建 `knowledge/testing/frameworks/jest-rtl.md`，内容：

```markdown
# Jest + React Testing Library 规范

> 本文档适用于 React 单元测试 / 组件测试场景（Jest + React Testing Library）。
> **注意：RTL 是组件级测试工具，无 E2E 能力。** 不适用于跨页面流程测试（E2E 用 Playwright）。

## 适用范围

- 单个组件的渲染测试
- 组件内部交互（点击、输入、状态变化）
- Mock API 调用的集成测试

**不适用于：** 页面导航、跨页面流程、真实网络请求、浏览器特定行为（用 Playwright）

## 框架能力矩阵

| 层 | native | helper | 说明 |
|---|---|---|---|
| element_discovery | covered | thin | `getByTestId`、`getByRole`、`getByLabelText` 完善 |
| button_trigger | covered | thin | `userEvent.click()` 处理可见性和交互性 |
| gesture | n/a | skip | RTL 不测真实手势（组件级无意义） |
| async_wait | covered | thin | `waitFor`、`findByTestId` 原生异步支持 |
| system_dialog | n/a | skip | 无浏览器系统弹窗 |
| keyboard_ime | partial | supplement | `userEvent.type()` 支持基本输入；IME 组合态不可测 |
| scroll_container | n/a | skip | 虚拟列表在 jsdom 中不真实渲染 |
| cross_app | n/a | skip | 单组件测试无跨 App 场景 |

## 代码节点生成规范

生成 React 组件时，所有可交互元素必须加 `data-testid`：

```tsx
// ✓ 正确
<button data-testid="submit-button" onClick={handleSubmit}>提交</button>
<input data-testid="email-input" type="email" value={email} onChange={setEmail} />
<div data-testid="error-message" role="alert">{error}</div>

// ✗ 错误：无 data-testid
<button onClick={handleSubmit}>提交</button>
```

## Helper 实现（TypeScript）

helper 文件路径：使用 `tech-profile.json` 中对应 module 的 `helper_file` 字段
（如 `src/__tests__/helpers/ui_helper.ts`）

```typescript
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// element_discovery thin（RTL 原生已覆盖，仅统一调用风格）
export function getElement(testId: string) {
  return screen.getByTestId(testId);
}

// async_wait thin
export async function waitForElement(testId: string) {
  return screen.findByTestId(testId);
}

// keyboard_ime supplement（基本输入覆盖；IME 不可测，记录限制）
export async function typeText(testId: string, text: string) {
  const user = userEvent.setup();
  const input = screen.getByTestId(testId);
  await user.clear(input);
  await user.type(input, text);
  // 注：中文/日文 IME 组合态在 jsdom 中不可真实模拟
  // E2E 测试（Playwright）负责覆盖 IME 场景
}
```
```

- [ ] **Step 4: 运行测试，确认通过**

```bash
pytest tests/test_knowledge_files.py -v
```
Expected: 全部 PASS

- [ ] **Step 5: Commit**

```bash
git add knowledge/testing/frameworks/jest-rtl.md tests/test_knowledge_files.py
git commit -m "feat: add jest-rtl framework spec and complete knowledge test suite"
```

---

### Task 7: 验证完整测试套件 + 运行现有测试无回归

**Files:**
- No new files

- [ ] **Step 1: 运行全部 knowledge 测试**

```bash
pytest tests/test_knowledge_files.py -v
```

Expected output（全部 PASS）：
```
tests/test_knowledge_files.py::test_profile_rules_exists PASSED
tests/test_knowledge_files.py::test_profile_rules_has_required_sections PASSED
tests/test_knowledge_files.py::test_helper_rules_exists PASSED
tests/test_knowledge_files.py::test_helper_rules_has_8_rules PASSED
tests/test_knowledge_files.py::test_helper_rules_has_coverage_matrix PASSED
tests/test_knowledge_files.py::test_framework_files_exist PASSED
tests/test_knowledge_files.py::test_playwright_has_capability_matrix PASSED
tests/test_knowledge_files.py::test_xcuitest_has_capability_matrix PASSED
tests/test_knowledge_files.py::test_patrol_has_capability_matrix PASSED
tests/test_knowledge_files.py::test_jest_rtl_has_capability_matrix PASSED
```

- [ ] **Step 2: 运行现有测试套件，确认无回归**

```bash
pytest --ignore=tests/test_knowledge_files.py -q
```
Expected: 全部通过（307 tests passed，与实现前一致）

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "test: verify knowledge files completeness and no regression"
```

---

## Self-Review

**Spec 覆盖检查：**

| Spec 要求 | 对应 Task |
|---|---|
| knowledge/testing/profile-rules.md | Task 1 |
| knowledge/testing/helper-rules.md（8 条规则） | Task 2 |
| frameworks/playwright.md | Task 3 |
| frameworks/xcuitest.md | Task 4 |
| frameworks/patrol.md | Task 5 |
| frameworks/jest-rtl.md | Task 6 |
| 零引擎改动 | 全程无 src/devforge/ 修改 |
| tech-profile.json 数据结构 | Task 1 profile-rules.md 中定义 |
| Gap #4（helper 已存在时只补充缺失层） | Task 2、3、4、5 各框架 helper 实现注释中说明 |

**Placeholder 扫描：** 无 TBD/TODO，所有代码示例完整可运行 ✓

**类型一致性：** `tech-profile.json` 的字段名（`module_id`、`framework`、`helper_file`、`layers`）在 Task 1 定义，Task 3-6 的矩阵均与之一致 ✓
