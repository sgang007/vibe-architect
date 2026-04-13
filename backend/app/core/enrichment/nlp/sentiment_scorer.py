import asyncio
import functools
from app.models import SentimentResult
from app.config import settings


class SentimentScorer:
    def __init__(self):
        self._pipe = None

    def _load(self):
        if self._pipe is not None:
            return
        from transformers import pipeline
        self._pipe = pipeline(
            "sentiment-analysis",
            model=settings.NLP_SENTIMENT_MODEL,
            device=-1,
            truncation=True,
            max_length=128,
            cache_dir=settings.MODEL_CACHE_DIR,
        )

    async def score(self, text: str) -> SentimentResult:
        self._load()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, functools.partial(self._pipe, text))
        label = result[0]["label"].lower()
        score = result[0]["score"]
        return SentimentResult(
            label=label,
            confidence=score,
            kano_hint=self._to_kano(label, score),
            feature_type="pain_driven" if label == "negative" else "delight_driven",
        )

    def _to_kano(self, label: str, score: float) -> str:
        if label == "negative" and score > 0.70:
            return "basic"
        if label == "negative":
            return "performance"
        if label == "positive" and score > 0.75:
            return "delighter"
        return "performance"

    @property
    def loaded(self) -> bool:
        return self._pipe is not None
