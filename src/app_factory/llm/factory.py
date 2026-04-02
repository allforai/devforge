"""LLM client factory helpers."""

from __future__ import annotations

from app_factory.llm.base import LLMClient

from .config import LLMProviderConfig
from .google import GoogleGenAIClient
from .http import HTTPTransport
from .mock import MockLLMClient
from .openrouter import OpenRouterClient


def build_llm_client(
    provider: str,
    *,
    model: str,
    api_key: str | None = None,
    transport: HTTPTransport | None = None,
) -> LLMClient:
    """Build one provider-specific LLM client."""

    if provider == "mock":
        return MockLLMClient(model_name=model)
    if provider == "google":
        kwargs = {"model_name": model, "api_key": api_key}
        if transport is not None:
            kwargs["transport"] = transport
        return GoogleGenAIClient(**kwargs)
    if provider == "openrouter":
        kwargs = {"model_name": model, "api_key": api_key}
        if transport is not None:
            kwargs["transport"] = transport
        return OpenRouterClient(**kwargs)
    raise ValueError(f"Unsupported llm provider: {provider}")


def build_llm_client_from_config(
    config: LLMProviderConfig,
    *,
    transport: HTTPTransport | None = None,
) -> LLMClient:
    """Build one provider-specific client from config."""

    return build_llm_client(
        config.provider,
        model=config.model,
        api_key=config.api_key,
        transport=transport,
    )
