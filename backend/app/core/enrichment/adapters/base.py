from abc import ABC, abstractmethod


class AdapterError(Exception):
    pass


class AdapterRateLimitError(AdapterError):
    pass


class AbstractLLMAdapter(ABC):
    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> str:
        """Make a single completion call. Returns raw string."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate token count for budget checking."""

    @property
    @abstractmethod
    def max_context_tokens(self) -> int:
        """Hard context window limit for this adapter."""
