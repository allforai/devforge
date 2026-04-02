"""Executor adapter exports."""

from .adapters import ClaudeCodeAdapter, ClineAdapter, CodexAdapter, OpenCodeAdapter, PythonAdapter
from .base import ClaudeCodeTaskRequest, CodexTaskRequest, ExecutorAdapter, ExecutorDispatch, SubmissionReceipt
from .payloads import format_executor_payload
from .pull_policy import PULL_POLICY_OVERRIDE_SCHEMA, PULL_POLICY_RULES, PullPolicyRule, normalize_pull_policy_overrides, resolve_pull_strategy
from .registry import EXECUTOR_REGISTRY, get_executor_adapter, register_executor_adapter

for _adapter in (
    PythonAdapter(),
    ClaudeCodeAdapter(),
    CodexAdapter(),
    ClineAdapter(),
    OpenCodeAdapter(),
):
    register_executor_adapter(_adapter)

__all__ = [
    "ClaudeCodeAdapter",
    "ClaudeCodeTaskRequest",
    "ClineAdapter",
    "CodexTaskRequest",
    "CodexAdapter",
    "EXECUTOR_REGISTRY",
    "ExecutorAdapter",
    "ExecutorDispatch",
    "format_executor_payload",
    "OpenCodeAdapter",
    "PULL_POLICY_OVERRIDE_SCHEMA",
    "PythonAdapter",
    "PULL_POLICY_RULES",
    "PullPolicyRule",
    "SubmissionReceipt",
    "get_executor_adapter",
    "normalize_pull_policy_overrides",
    "register_executor_adapter",
    "resolve_pull_strategy",
]
