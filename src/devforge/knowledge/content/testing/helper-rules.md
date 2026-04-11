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
