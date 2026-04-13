import asyncio

from app.config import settings

from .base import AbstractLLMAdapter, AdapterError, AdapterRateLimitError


class AnthropicAdapter(AbstractLLMAdapter):
    """Adapter for the Anthropic Messages API using the official Python SDK."""

    def __init__(self):
        try:
            import anthropic as anthropic_sdk
            self._sdk = anthropic_sdk
        except ImportError as e:
            raise ImportError("anthropic package not installed. Run: pip install anthropic") from e
        self.model = settings.ANTHROPIC_MODEL
        self.api_key = settings.ANTHROPIC_API_KEY
        self._client = self._sdk.AsyncAnthropic(api_key=self.api_key)

    @property
    def max_context_tokens(self) -> int:
        # claude-haiku-4-5 supports 200k tokens
        return 200000

    def count_tokens(self, text: str) -> int:
        # Rough approximation: ~4 chars per token on average
        return len(text.split()) * 4 // 3

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> str:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_message},
            ],
        }

        # Anthropic supports forcing JSON output via a prefilled assistant turn
        if json_mode:
            kwargs["messages"].append({"role": "assistant", "content": "{"})

        delays = [1, 2, 4]
        last_error: Exception = AdapterError("Unknown error")
        for attempt, delay in enumerate(delays):
            try:
                response = await self._client.messages.create(**kwargs)
                text = response.content[0].text
                # If we prefilled with "{", restore the opening brace
                if json_mode:
                    text = "{" + text
                return text
            except self._sdk.RateLimitError as e:
                if attempt < len(delays) - 1:
                    await asyncio.sleep(delay)
                    continue
                raise AdapterRateLimitError(
                    f"Anthropic rate limit exceeded after retries: {e}"
                ) from e
            except self._sdk.AuthenticationError as e:
                raise AdapterError(
                    f"Anthropic authentication failed — check ANTHROPIC_API_KEY: {e}"
                ) from e
            except self._sdk.APIError as e:
                last_error = e
                if attempt == len(delays) - 1:
                    raise AdapterError(f"Anthropic API error: {e}") from e
                await asyncio.sleep(delay)
            except Exception as e:
                last_error = e
                if attempt == len(delays) - 1:
                    raise AdapterError(f"Anthropic request failed: {e}") from e
                await asyncio.sleep(delay)

        raise last_error

    async def aclose(self) -> None:
        await self._client.close()
