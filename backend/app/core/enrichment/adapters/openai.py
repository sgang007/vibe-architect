import asyncio

import httpx

from app.config import settings

from .base import AbstractLLMAdapter, AdapterError, AdapterRateLimitError


class OpenAIAdapter(AbstractLLMAdapter):
    """Adapter for the OpenAI Chat Completions API."""

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self):
        self.model = settings.OPENAI_MODEL
        self.api_key = settings.OPENAI_API_KEY
        self.http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    @property
    def max_context_tokens(self) -> int:
        # gpt-4o-mini has a 128k context window
        return 128000

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
        payload: dict = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        delays = [1, 2, 4]
        last_error: Exception = AdapterError("Unknown error")
        for attempt, delay in enumerate(delays):
            try:
                resp = await self.http.post("/chat/completions", json=payload)
                if resp.status_code == 429:
                    if attempt < len(delays) - 1:
                        await asyncio.sleep(delay)
                        continue
                    raise AdapterRateLimitError("OpenAI rate limit exceeded after retries")
                if resp.status_code == 401:
                    raise AdapterError("OpenAI authentication failed — check OPENAI_API_KEY")
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except AdapterRateLimitError:
                raise
            except AdapterError:
                raise
            except Exception as e:
                last_error = e
                if attempt == len(delays) - 1:
                    raise AdapterError(f"OpenAI request failed: {e}") from e
                await asyncio.sleep(delay)

        raise last_error

    async def aclose(self) -> None:
        await self.http.aclose()
