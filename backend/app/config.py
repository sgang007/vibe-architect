from __future__ import annotations
from typing import Any
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, EnvSettingsSource
from pydantic import ConfigDict
from typing import Optional


class _NonEmptyEnvSource(EnvSettingsSource):
    """Env var source that skips empty-string values.

    Prevents a bare ``export ANTHROPIC_API_KEY=`` in the shell from
    silently overriding the value set in the .env file.
    """

    def __call__(self) -> dict[str, Any]:
        return {k: v for k, v in super().__call__().items() if v != ""}


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        **kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Replace default env source with one that ignores empty strings.
        # This prevents a bare `export ANTHROPIC_API_KEY=` in the shell
        # from shadowing the value in the .env file.
        sources = list(BaseSettings.settings_customise_sources(
            settings_cls, **kwargs  # type: ignore[arg-type]
        ))
        for i, src in enumerate(sources):
            if isinstance(src, EnvSettingsSource) and not isinstance(src, _NonEmptyEnvSource):
                sources[i] = _NonEmptyEnvSource(settings_cls)
                break
        return tuple(sources)
    # LLM Provider
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    OLLAMA_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"

    # Session Storage
    SESSION_BACKEND: str = "redis"
    REDIS_URL: str = "redis://localhost:6379"
    SESSION_TTL_HOURS: int = 24

    # Rate Limiting
    RATE_LIMIT_SESSIONS_PER_IP_PER_HOUR: int = 3
    RATE_LIMIT_MAX_ACTIVE_SESSIONS_PER_IP: int = 1

    # Cost Controls
    MAX_CONVERSATION_TOKENS: int = 6000
    DAILY_COST_ALERT_USD: float = 10.00
    ENABLE_COST_TRACKING: bool = True

    # App
    APP_ENV: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"

    # NLP Layer (v3.0)
    ENABLE_NLP_LAYER: bool = True
    MODEL_CACHE_DIR: str = "/models"
    NLP_CLASSIFIER_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
    NLP_SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    NLP_DOMAIN_MODEL: str = "valhalla/distilbart-mnli-12-1"
    NLP_SIMILARITY_MODEL: str = "all-MiniLM-L6-v2"
    NLP_QUALITY_SUBSTANCE_THRESHOLD: float = 0.80
    NLP_DOMAIN_CONFIDENCE_THRESHOLD: float = 0.40
    NLP_DEDUP_SIMILARITY_THRESHOLD: float = 0.85
    NLP_EXPERTISE_PROBE_THRESHOLD: float = 0.70

    # Emergent Platform (v3.0)
    EMERGENT_PROMPT_MAX_TOKENS: int = 6000

    # Feature Flags
    ENABLE_PREVIEW_ENGINE: bool = True
    ENABLE_OLLAMA_FALLBACK: bool = False
    BUILD_DOWNLOAD_MODELS: bool = True

    LOG_LEVEL: str = "INFO"



settings = Settings()
