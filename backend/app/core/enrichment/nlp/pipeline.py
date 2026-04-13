from __future__ import annotations
import asyncio
from app.models import (
    EnrichmentPhase, SessionContext, NLPAnnotation, AnswerQuality,
    FeatureKanoHint
)
from app.config import settings
from .readability_analyzer import ReadabilityAnalyzer
from .answer_classifier import AnswerQualityClassifier
from .entity_extractor import EntityExtractor
from .sentiment_scorer import SentimentScorer
from .domain_detector import DomainDetector
from .feature_deduplicator import FeatureDeduplicator
from app.core.enrichment.fsm.answer_classifier import classify_regex


class NLPPipeline:
    """Orchestrates all NLP modules. Gracefully degrades if any module fails."""

    def __init__(self):
        self.enabled = settings.ENABLE_NLP_LAYER
        self.readability = ReadabilityAnalyzer()  # always enabled
        if self.enabled:
            self.classifier = AnswerQualityClassifier()
            self.ner = EntityExtractor()
            self.sentiment = SentimentScorer()
            self.domain = DomainDetector()
            self.deduplicator = FeatureDeduplicator()
        else:
            self.classifier = None
            self.ner = None
            self.sentiment = None
            self.domain = None
            self.deduplicator = None

    async def process_answer(
        self,
        answer: str,
        phase: EnrichmentPhase,
        session: SessionContext,
    ) -> NLPAnnotation:
        readability = self.readability.analyze(answer)
        self.readability.update_expertise_signal(session, readability)

        if not self.enabled:
            quality = classify_regex(answer)
            return NLPAnnotation(quality=quality, readability_score=readability.flesch_reading_ease)

        # M1 — blocks FSM decision
        try:
            quality = await self.classifier.classify(answer, readability)
        except Exception:
            quality = classify_regex(answer)

        # Track low-confidence turns
        if quality in (AnswerQuality.VAGUE, AnswerQuality.MINIMAL):
            session.nlp_state.low_confidence_turns.append(len(session.fsm_turns))

        # M2, M3, M4 — async, do not block
        tasks = []
        task_keys = []

        tasks.append(self._safe(self.ner.extract(answer, session)))
        task_keys.append("ner")

        if phase in (EnrichmentPhase.FEATURES,):
            tasks.append(self._safe(self.sentiment.score(answer)))
            task_keys.append("sentiment")

        if phase == EnrichmentPhase.IDEA and not session.nlp_state.app_domain:
            tasks.append(self._safe(self.domain.detect(answer)))
            task_keys.append("domain")

        results = await asyncio.gather(*tasks, return_exceptions=True)
        result_map = dict(zip(task_keys, results))

        entities = result_map.get("ner")
        if isinstance(entities, Exception):
            entities = None

        sentiment_result = result_map.get("sentiment")
        if isinstance(sentiment_result, Exception):
            sentiment_result = None
        elif sentiment_result:
            # Store kano hint for later injection into Call 1
            session.nlp_state.feature_kano_hints.append(
                FeatureKanoHint(
                    feature_text=answer[:200],
                    kano_hint=sentiment_result.kano_hint,
                    sentiment_confidence=sentiment_result.confidence,
                )
            )

        domain_result = result_map.get("domain")
        if isinstance(domain_result, Exception):
            domain_result = None
        elif domain_result and domain_result.domain != "default":
            session.nlp_state.app_domain = domain_result.domain
            session.nlp_state.app_domain_confidence = domain_result.confidence

        return NLPAnnotation(
            quality=quality,
            entities=entities if not isinstance(entities, Exception) else None,
            sentiment=sentiment_result,
            domain=domain_result,
            readability_score=readability.flesch_reading_ease,
        )

    async def deduplicate_features(self, raw_features: list[str], session: SessionContext) -> list[str]:
        if not self.enabled or not self.deduplicator:
            return raw_features
        try:
            result = await self.deduplicator.deduplicate(raw_features)
            session.nlp_state.deduplicated_features = result.unique
            return result.unique
        except Exception:
            return raw_features

    @staticmethod
    async def _safe(coro):
        try:
            return await coro
        except Exception as e:
            return e

    def get_health(self) -> dict:
        return {
            "enabled": self.enabled,
            "distilbert": self.classifier.loaded if self.classifier else False,
            "spacy": self.ner.loaded if self.ner else False,
            "roberta": self.sentiment.loaded if self.sentiment else False,
            "distilbart": self.domain.loaded if self.domain else False,
            "minilm": self.deduplicator.loaded if self.deduplicator else False,
            "textstat": True,
        }
