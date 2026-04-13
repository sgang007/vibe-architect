import asyncio
import logging

import httpx

from app.config import settings

from .base import AbstractLLMAdapter, AdapterError, AdapterRateLimitError

logger = logging.getLogger(__name__)

# Maximum seconds we are willing to wait on any single rate-limit backoff.
# Groq returns retry-after values up to 8 min (480 s) when the *daily* token
# quota is exhausted — we cap at 90 s so the user gets a fast failure instead
# of an 8-minute silent hang.
_MAX_RATE_LIMIT_WAIT = 90


class GroqAdapter(AbstractLLMAdapter):
    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.api_key = settings.GROQ_API_KEY
        self.http = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    @property
    def max_context_tokens(self) -> int:
        return 131072

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
        payload = {
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

        # Retry strategy:
        #   • Up to 3 rate-limit (429) retries, each capped at _MAX_RATE_LIMIT_WAIT s.
        #   • Up to 3 general error retries with 1/2/4 s backoff.
        # IMPORTANT: always check rate_attempt FIRST — if retry-after is very
        # large (daily quota exhausted) we fail fast rather than sleeping 8 min.
        rate_limit_delays = [15, 30, 60]
        general_delays = [1, 2, 4]

        rate_attempt = 0
        general_attempt = 0

        while True:
            try:
                resp = await self.http.post("/chat/completions", json=payload)

                if resp.status_code == 429:
                    # Fail fast once we've exhausted our retry budget
                    if rate_attempt >= len(rate_limit_delays):
                        error_body = ""
                        try:
                            error_body = resp.json().get("error", {}).get("message", "")
                        except Exception:
                            pass
                        raise AdapterRateLimitError(
                            f"Groq rate limit exceeded after {rate_attempt} retries. "
                            f"{error_body}"
                        )

                    # Honor retry-after but cap it so we don't wait indefinitely
                    retry_after_header = resp.headers.get("retry-after")
                    if retry_after_header:
                        suggested = float(retry_after_header)
                        wait = min(suggested, _MAX_RATE_LIMIT_WAIT)
                        if suggested > _MAX_RATE_LIMIT_WAIT:
                            # Daily quota likely exhausted — skip remaining retries
                            error_body = ""
                            try:
                                error_body = resp.json().get("error", {}).get("message", "")
                            except Exception:
                                pass
                            raise AdapterRateLimitError(
                                f"Groq daily token quota exhausted (retry-after {suggested:.0f}s). "
                                f"{error_body}"
                            )
                    else:
                        wait = rate_limit_delays[rate_attempt]

                    logger.warning(
                        "Groq 429 rate limit (attempt %d/%d) — waiting %.0fs",
                        rate_attempt + 1, len(rate_limit_delays), wait,
                    )
                    rate_attempt += 1
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]

            except AdapterRateLimitError:
                raise
            except Exception as e:
                if general_attempt >= len(general_delays):
                    raise AdapterError(str(e)) from e
                logger.warning("Groq request error (attempt %d): %s", general_attempt + 1, e)
                await asyncio.sleep(general_delays[general_attempt])
                general_attempt += 1

    async def aclose(self) -> None:
        await self.http.aclose()
