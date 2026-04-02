"""Project-aware LLM routing helpers."""

from __future__ import annotations

import os
from typing import Any

from .base import LLMClient
from .factory import build_llm_client
from .mock import MockLLMClient


def build_task_llm_client(
    *,
    task: str,
    preferences: dict[str, Any] | None = None,
) -> LLMClient:
    """Build a task-specific LLM client from project preferences.

    Offline-safe by default: unless live routing is explicitly enabled and an API key
    is available, this returns a mock client carrying the routed provider/model identity.
    """

    preferences = preferences or {}
    provider = _provider_for_task(task, preferences)
    model = _model_for_task(task, preferences) or "mock-structured-v1"
    allow_live = bool(preferences.get("allow_live", False))
    api_key = _api_key_for_provider(provider, preferences)

    if allow_live and provider != "mock" and api_key:
        return build_llm_client(provider, model=model, api_key=api_key)
    return MockLLMClient(provider_name=provider, model_name=model)


def _model_for_task(task: str, preferences: dict[str, Any]) -> str | None:
    key_by_task = {
        "concept_collection": "concept_model",
        "planning_and_shaping": "planning_model",
        "retry_decision": "retry_model",
    }
    specific_key = key_by_task.get(task)
    if specific_key and preferences.get(specific_key):
        return str(preferences[specific_key])
    if preferences.get("model"):
        return str(preferences["model"])
    return None


def _provider_for_task(task: str, preferences: dict[str, Any]) -> str:
    key_by_task = {
        "concept_collection": "concept_provider",
        "planning_and_shaping": "planning_provider",
        "retry_decision": "retry_provider",
    }
    specific_key = key_by_task.get(task)
    if specific_key and preferences.get(specific_key):
        return str(preferences[specific_key])
    return str(preferences.get("provider", "mock"))


def _api_key_for_provider(provider: str, preferences: dict[str, Any]) -> str | None:
    if preferences.get("api_key"):
        return str(preferences["api_key"])
    env_var = {
        "openrouter": "OPENROUTER_API_KEY",
        "google": "GOOGLE_API_KEY",
    }.get(provider)
    if env_var is None:
        return None
    return os.getenv(env_var)
