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
    func findElement(identifier: String, timeout: TimeInterval = 5) -> XCUIElement {
        let el = app.descendants(matching: .any)[identifier]
        let exists = el.waitForExistence(timeout: timeout)
        if !exists {
            XCTFail("[SELECTOR_UNSTABLE] accessibilityIdentifier='\(identifier)' not found within \(timeout)s")
        }
        return el
    }

    // async_wait supplement
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
    func typeTextAndConfirm(_ text: String, in field: XCUIElement) {
        field.tap()
        field.typeText(text)
        let toolbar = app.toolbars.firstMatch
        if toolbar.exists {
            toolbar.buttons.firstMatch.tap()
        }
    }

    // scroll_container supplement
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
// ✓ 正确
button.accessibilityIdentifier = "submit-button"
textField.accessibilityIdentifier = "email-input"

// SwiftUI
Button("提交") { handleSubmit() }
    .accessibilityIdentifier("submit-button")

// ✗ 错误
Button("提交") { handleSubmit() }
```

## 环境要求

- macOS + Xcode（非 macOS 环境标记 `DEFERRED_NATIVE`，仅输出脚本不执行）
- iOS Simulator：`xcrun simctl list devices` 检查可用模拟器
- 项目需有 UI Test target
