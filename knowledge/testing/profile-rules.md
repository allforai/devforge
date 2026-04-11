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
