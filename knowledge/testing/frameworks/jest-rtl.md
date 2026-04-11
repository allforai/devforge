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

// ✗ 错误
<button onClick={handleSubmit}>提交</button>
```

## Helper 实现（TypeScript）

helper 文件路径：使用 `tech-profile.json` 中对应 module 的 `helper_file` 字段
（如 `src/__tests__/helpers/ui_helper.ts`）

```typescript
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// element_discovery thin
export function getElement(testId: string) {
  return screen.getByTestId(testId);
}

// async_wait thin
export async function waitForElement(testId: string) {
  return screen.findByTestId(testId);
}

// keyboard_ime supplement
export async function typeText(testId: string, text: string) {
  const user = userEvent.setup();
  const input = screen.getByTestId(testId);
  await user.clear(input);
  await user.type(input, text);
  // 注：中文/日文 IME 组合态在 jsdom 中不可真实模拟
  // E2E 测试（Playwright）负责覆盖 IME 场景
}
```

## React Testing Library

React Testing Library (RTL) encourages testing user behavior rather than implementation details.
Use `getByTestId` for stable element queries in all component tests.
