from __future__ import annotations

import logging

from app.config import settings

from .base import AbstractLLMAdapter, AdapterError, AdapterRateLimitError
from .groq import GroqAdapter
from .ollama import OllamaAdapter
from .mock import MockLLMAdapter

logger = logging.getLogger(__name__)


def get_adapter(provider: str | None = None) -> AbstractLLMAdapter:
    """Instantiate and return the appropriate LLM adapter.

    Args:
        provider: Override the provider from settings. One of:
                  "groq", "ollama", "openai", "anthropic", "mock".

    Returns:
        An instance of the matching AbstractLLMAdapter subclass.

    Raises:
        ValueError: If the provider name is not recognised.
    """
    p = provider or settings.LLM_PROVIDER
    if p == "groq":
        return GroqAdapter()
    elif p == "ollama":
        return OllamaAdapter()
    elif p == "openai":
        from .openai import OpenAIAdapter
        return OpenAIAdapter()
    elif p == "anthropic":
        from .anthropic import AnthropicAdapter
        return AnthropicAdapter()
    elif p == "mock":
        return MockLLMAdapter()
    raise ValueError(f"Unknown LLM provider: {p!r}")


def get_fallback_adapter() -> AbstractLLMAdapter | None:
    """Return a fallback adapter when the primary one is rate-limited.

    Priority: Anthropic → OpenAI → None (caller must handle).
    """
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "sk-ant-...":
        logger.info("Falling back to Anthropic adapter")
        from .anthropic import AnthropicAdapter
        return AnthropicAdapter()
    if getattr(settings, "OPENAI_API_KEY", None) and settings.OPENAI_API_KEY != "sk-...":
        logger.info("Falling back to OpenAI adapter")
        from .openai import OpenAIAdapter
        return OpenAIAdapter()
    return None


__all__ = [
    "AbstractLLMAdapter",
    "AdapterError",
    "AdapterRateLimitError",
    "GroqAdapter",
    "OllamaAdapter",
    "MockLLMAdapter",
    "get_adapter",
    "get_fallback_adapter",
]
