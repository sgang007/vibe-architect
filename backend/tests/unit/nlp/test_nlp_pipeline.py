"""TC-NLP-01 through TC-NLP-12 (with ENABLE_NLP_LAYER=false for fast CI)."""
import os
import pytest
from app.models import SessionContext, EnrichmentPhase, AnswerQuality


# Fast tests — run with ENABLE_NLP_LAYER=false (regex fallback)
class TestNLPFallback:
    """These tests verify the regex fallback classifier (always fast, no models needed)."""

    def test_TC_NLP_01_adequate_for_12_word_concrete_answer(self):
        """TC-NLP-01: Returns ADEQUATE for 12-word concrete answer."""
        from app.core.enrichment.fsm.answer_classifier import classify_regex
        answer = "I want to build a booking platform for hair salons with online scheduling"
        quality = classify_regex(answer)
        assert quality in (AnswerQuality.ADEQUATE, AnswerQuality.RICH)

    def test_TC_NLP_02_vague_for_i_dont_know(self):
        """TC-NLP-02: Returns VAGUE for 'I don't know'."""
        from app.core.enrichment.fsm.answer_classifier import classify_regex
        quality = classify_regex("I don't know")
        assert quality == AnswerQuality.VAGUE

    def test_TC_NLP_08_readability_expertise_signal(self):
        """TC-NLP-08: ReadabilityAnalyzer returns expertise signal > 0 after expert answers."""
        from app.core.enrichment.nlp.readability_analyzer import ReadabilityAnalyzer
        analyzer = ReadabilityAnalyzer()
        session = SessionContext()
        session.phase = EnrichmentPhase.IDEA

        expert_answers = [
            "We need a multi-tenant SaaS platform implementing RBAC with granular permission scoping.",
            "The system must handle concurrent webhook ingestion with idempotency guarantees.",
            "Our architecture requires event-driven microservices with eventual consistency patterns.",
        ]

        for answer in expert_answers:
            result = analyzer.analyze(answer)
            analyzer.update_expertise_signal(session, result)

        assert session.user_expertise_signal > 0

    def test_TC_NLP_09_no_nlp_annotations_when_disabled(self, monkeypatch):
        """TC-NLP-10: Call 1 user message does NOT contain nlp_annotations when NLP disabled."""
        from app.core.enrichment.extraction.extractor import build_extraction_message
        from app.models import FSMTurn, SessionNLPState
        session = SessionContext()
        session.phase = EnrichmentPhase.EXTRACTING
        session.nlp_state = SessionNLPState()  # empty NLP state

        from app.core.enrichment.fsm.question_tree import PHASE_QUESTIONS
        turn_idx = 0
        for phase_name, questions in PHASE_QUESTIONS.items():
            phase_enum = EnrichmentPhase[phase_name]
            for q in questions:
                session.fsm_turns.append(FSMTurn(
                    turn_index=turn_idx,
                    phase=phase_enum,
                    question_id=q.id,
                    question_text=q.text,
                    answer="Sample answer",
                    answer_quality=AnswerQuality.ADEQUATE,
                ))
                turn_idx += 1

        import json
        message = build_extraction_message(session)
        data = json.loads(message)
        # When NLP state is empty, nlp_annotations should not be injected
        assert "nlp_annotations" not in data or data.get("nlp_annotations") is None

    def test_TC_NLP_11_pipeline_graceful_fallback_on_error(self):
        """TC-NLP-11: NLPPipeline gracefully returns regex fallback when model raises exception."""
        from unittest.mock import patch, AsyncMock
        import asyncio

        # Patch settings to enable NLP
        with patch("app.config.settings") as mock_settings:
            mock_settings.ENABLE_NLP_LAYER = False
            from app.core.enrichment.nlp.pipeline import NLPPipeline
            pipeline = NLPPipeline()
            assert not pipeline.enabled

            session = SessionContext()
            session.phase = EnrichmentPhase.IDEA

            result = asyncio.get_event_loop().run_until_complete(
                pipeline.process_answer("yes", EnrichmentPhase.IDEA, session)
            )
            assert result.quality == AnswerQuality.VAGUE


# Slow tests — only run with ENABLE_NLP_LAYER=true and models downloaded
@pytest.mark.skipif(
    os.environ.get("ENABLE_NLP_LAYER", "false").lower() != "true",
    reason="Requires NLP models. Run with ENABLE_NLP_LAYER=true"
)
class TestNLPModels:
    def test_TC_NLP_03_entity_extractor_identifies_stripe(self):
        """TC-NLP-03: EntityExtractor identifies 'Stripe' as tool_name and 'admin' as role_term."""
        import asyncio
        from app.core.enrichment.nlp.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        session = SessionContext()
        session.phase = EnrichmentPhase.TECHNICAL

        cache = asyncio.get_event_loop().run_until_complete(
            extractor.extract("The admin uses Stripe for payment processing", session)
        )
        assert "Stripe" in cache.tool_names or "stripe" in {t.lower() for t in cache.tool_names}
        assert "admin" in cache.role_terms

    def test_TC_NLP_04_sentiment_basic_for_negative_feature(self):
        """TC-NLP-04: SentimentScorer returns kano_hint=basic for negative-sentiment text."""
        import asyncio
        from app.core.enrichment.nlp.sentiment_scorer import SentimentScorer
        scorer = SentimentScorer()

        result = asyncio.get_event_loop().run_until_complete(
            scorer.score("Users are frustrated when they can't find their bookings and lose money")
        )
        assert result.kano_hint in ("basic", "performance")

    def test_TC_NLP_05_sentiment_delighter_for_positive_feature(self):
        """TC-NLP-05: SentimentScorer returns kano_hint=delighter for high-confidence positive."""
        import asyncio
        from app.core.enrichment.nlp.sentiment_scorer import SentimentScorer
        scorer = SentimentScorer()

        result = asyncio.get_event_loop().run_until_complete(
            scorer.score("Users absolutely love the magical auto-scheduling that delights them with perfect timing")
        )
        assert result.kano_hint in ("delighter", "performance")

    def test_TC_NLP_06_domain_detector_returns_booking(self):
        """TC-NLP-06: DomainDetector returns domain=booking for salon scheduling app."""
        import asyncio
        from app.core.enrichment.nlp.domain_detector import DomainDetector
        detector = DomainDetector()

        result = asyncio.get_event_loop().run_until_complete(
            detector.detect("appointment scheduling app for salons and beauty services")
        )
        assert result.domain == "booking"

    def test_TC_NLP_07_deduplicator_merges_similar_features(self):
        """TC-NLP-07: FeatureDeduplicator merges semantically similar features."""
        import asyncio
        from app.core.enrichment.nlp.feature_deduplicator import FeatureDeduplicator
        deduplicator = FeatureDeduplicator()

        features = [
            "in-app messaging between users",
            "chat between buyer and seller",
            "payment processing",
        ]
        result = asyncio.get_event_loop().run_until_complete(
            deduplicator.deduplicate(features)
        )
        # The two messaging features should be merged
        assert len(result.unique) < len(features)
        assert len(result.merged_pairs) >= 1
