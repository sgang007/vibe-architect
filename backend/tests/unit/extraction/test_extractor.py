"""TC-EXT-01 through TC-EXT-05"""
import pytest
import json
from uuid import uuid4
from app.models import SessionContext, EnrichmentPhase, FSMTurn, AnswerQuality
from app.core.enrichment.extraction.extractor import ContextExtractor, build_extraction_message
from app.core.enrichment.adapters.mock import MockLLMAdapter, MOCK_EXTRACTION_RESPONSE


def make_session_with_turns():
    session = SessionContext()
    session.phase = EnrichmentPhase.EXTRACTING
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
                answer=f"Sample answer for {q.id}",
                answer_quality=AnswerQuality.ADEQUATE,
            ))
            turn_idx += 1
    return session


@pytest.mark.asyncio
async def test_TC_EXT_01_call1_payload_contains_all_14_turns():
    """TC-EXT-01: Call 1 payload contains all 14 Q&A turns and the extraction schema."""
    session = make_session_with_turns()
    assert len(session.fsm_turns) == 14

    message = build_extraction_message(session)
    data = json.loads(message)

    assert "conversation" in data
    assert len(data["conversation"]) == 14
    assert "output_schema" in data
    assert "jtbd" in data["output_schema"]
    assert "personas" in data["output_schema"]
    assert "features" in data["output_schema"]


@pytest.mark.asyncio
async def test_TC_EXT_02_parses_valid_json_into_enriched_context():
    """TC-EXT-02: Extractor correctly parses valid JSON response into EnrichedContext."""
    session = make_session_with_turns()
    adapter = MockLLMAdapter()
    extractor = ContextExtractor(adapter)

    ctx, tokens = await extractor.extract(session)

    assert ctx.session_id == session.session_id
    assert ctx.jtbd.functional_job is not None
    assert len(ctx.personas) >= 1
    assert len(ctx.features) >= 1
    assert ctx.tech_profile.scale_tier in ("prototype", "startup", "growth")


@pytest.mark.asyncio
async def test_TC_EXT_03_raises_extraction_error_on_malformed_json():
    """TC-EXT-03: Extractor raises ExtractionError on malformed JSON."""
    from app.core.enrichment.extraction.extractor import ExtractionError

    class BadAdapter(MockLLMAdapter):
        async def complete(self, *args, **kwargs):
            return "this is not json {"

    session = make_session_with_turns()
    extractor = ContextExtractor(BadAdapter())

    with pytest.raises(ExtractionError):
        await extractor.extract(session)


@pytest.mark.asyncio
async def test_TC_EXT_04_rice_score_nonzero_for_must_features():
    """TC-EXT-04: RICE calculator produces non-zero score for every must-have feature."""
    from app.core.enrichment.adapters.mock import MOCK_EXTRACTION_RESPONSE
    from app.models import Feature, Persona
    from app.core.enrichment.scoring.rice_calculator import calculate_all

    features = [Feature(**f) for f in MOCK_EXTRACTION_RESPONSE["features"]]
    personas = [Persona(**p) for p in MOCK_EXTRACTION_RESPONSE["personas"]]

    scores = calculate_all(features, personas)
    must_scores = [s for s, f in zip(scores, features) if f.moscow == "must"]

    assert len(must_scores) > 0
    for score in must_scores:
        assert score.score > 0


@pytest.mark.asyncio
async def test_TC_EXT_05_persona_matrix_has_n_times_m_entries():
    """TC-EXT-05: Persona matrix has exactly N×M entries for N features × M personas."""
    from app.models import Feature, Persona
    from app.core.enrichment.scoring.persona_matrix import build_matrix

    features = [Feature(**f) for f in MOCK_EXTRACTION_RESPONSE["features"]]
    personas = [Persona(**p) for p in MOCK_EXTRACTION_RESPONSE["personas"]]

    matrix = build_matrix(features, personas)
    assert len(matrix) == len(features) * len(personas)
