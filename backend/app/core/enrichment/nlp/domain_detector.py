import asyncio
import functools
from app.models import DomainResult
from app.config import settings

DOMAIN_LABELS = {
    "marketplace": ["buying and selling", "two-sided market", "vendors and buyers"],
    "booking": ["appointments", "reservations", "scheduling", "calendar booking"],
    "saas": ["software tool", "business dashboard", "team workflow"],
    "social": ["community platform", "social network", "user profiles"],
    "productivity": ["task management", "notes", "project tracking", "to-do list"],
    "ecommerce": ["online store", "products for sale", "shopping cart"],
    "finance": ["payments", "invoicing", "accounting", "financial tracking"],
    "health": ["wellness tracking", "medical records", "fitness", "health"],
}


class DomainDetector:
    def __init__(self):
        self._pipe = None
        self._all_labels = [l for labels in DOMAIN_LABELS.values() for l in labels]
        self._label_to_domain = {
            l: domain for domain, labels in DOMAIN_LABELS.items() for l in labels
        }

    def _load(self):
        if self._pipe is not None:
            return
        from transformers import pipeline
        self._pipe = pipeline(
            "zero-shot-classification",
            model=settings.NLP_DOMAIN_MODEL,
            device=-1,
            cache_dir=settings.MODEL_CACHE_DIR,
        )

    async def detect(self, text: str) -> DomainResult:
        self._load()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            functools.partial(self._pipe, text, self._all_labels, multi_label=False)
        )
        top_label = result["labels"][0]
        top_score = result["scores"][0]
        domain = self._label_to_domain.get(top_label, "default")
        return DomainResult(
            domain=domain if top_score > settings.NLP_DOMAIN_CONFIDENCE_THRESHOLD else "default",
            confidence=top_score,
        )

    @property
    def loaded(self) -> bool:
        return self._pipe is not None
