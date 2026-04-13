import asyncio

import httpx

from app.config import settings

from .base import AbstractLLMAdapter, AdapterError, AdapterRateLimitError


class OllamaAdapter(AbstractLLMAdapter):
    """Adapter for a locally-hosted Ollama instance.

    Ollama exposes an OpenAI-compatible /api/chat endpoint.
    We post to OLLAMA_URL/api/chat with the model specified in settings.
    """

    def __init__(self):
        self.model = settings.OLLAMA_MODEL
        self.base_url = settings.OLLAMA_URL.rstrip("/")
        self.http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=120.0,  # local models can be slow
        )

    @property
    def max_context_tokens(self) -> int:
        # Llama 3.1 8B default context
        return 8192

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
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if json_mode:
            payload["format"] = "json"

        delays = [1, 2, 4]
        last_error: Exception = AdapterError("Unknown error")
        for attempt, delay in enumerate(delays):
            try:
                resp = await self.http.post("/api/chat", json=payload)
                if resp.status_code == 429:
                    if attempt < len(delays) - 1:
                        await asyncio.sleep(delay)
                        continue
                    raise AdapterRateLimitError("Ollama rate limit exceeded after retries")
                resp.raise_for_status()
                data = resp.json()
                # Ollama /api/chat response: {"message": {"role": "assistant", "content": "..."}}
                return data["message"]["content"]
            except AdapterRateLimitError:
                raise
            except Exception as e:
                last_error = e
                if attempt == len(delays) - 1:
                    raise AdapterError(f"Ollama request failed: {e}") from e
                await asyncio.sleep(delay)

        raise last_error

    async def aclose(self) -> None:
        await self.http.aclose()
