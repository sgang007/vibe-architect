import asyncio
import functools
from typing import Optional
from app.models import AnswerQuality, ReadabilityResult
from app.config import settings

VAGUE_PHRASES = {
    "yes", "no", "maybe", "idk", "not sure", "ok", "fine",
    "don't know", "no idea", "whatever", "something", "anything",
    "i don't know", "not really", "sort of", "kind of"
}


class AnswerQualityClassifier:
    """Classifies user answer quality using DistilBERT + readability signals."""

    def __init__(self):
        self._pipe = None

    def _load(self):
        if self._pipe is not None:
            return
        from transformers import pipeline
        self._pipe = pipeline(
            "text-classification",
            model=settings.NLP_CLASSIFIER_MODEL,
            device=-1,
            truncation=True,
            max_length=128,
            cache_dir=settings.MODEL_CACHE_DIR,
        )

    async def classify(self, answer: str, readability: ReadabilityResult) -> AnswerQuality:
        self._load()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, functools.partial(self._pipe, answer)
        )
        label = result[0]["label"]
        score = result[0]["score"]
        wc = readability.word_count or len(answer.split())
        fre = readability.flesch_reading_ease
        return self._map_to_quality(label, score, wc, fre, answer)

    def _map_to_quality(self, label, score, wc, fre, answer) -> AnswerQuality:
        if wc == 0:
            return AnswerQuality.EMPTY

        stripped = answer.strip().lower()
        if stripped in VAGUE_PHRASES:
            return AnswerQuality.VAGUE

        if wc < 5 and label == "NEGATIVE":
            return AnswerQuality.VAGUE

        if fre > 65 and wc >= 8:
            return AnswerQuality.ADEQUATE

        substance_score = score if label == "POSITIVE" else (1.0 - score)
        if substance_score > 0.90 and wc >= 15:
            return AnswerQuality.RICH
        if substance_score > 0.80 and wc >= 6:
            return AnswerQuality.ADEQUATE

        if wc < 4:
            return AnswerQuality.VAGUE
        if wc < 8:
            return AnswerQuality.MINIMAL
        return AnswerQuality.ADEQUATE

    @property
    def loaded(self) -> bool:
        return self._pipe is not None
