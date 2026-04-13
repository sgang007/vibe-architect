"""TC-EMR-01 through TC-EMR-05"""
import pytest
from app.core.compiler.adapters.emergent import EmergentAdapter
from app.core.compiler.adapters.base import PromptSection


def test_TC_EMR_01_emergent_has_design_intent_and_enhancement_layer():
    """TC-EMR-01: EmergentAdapter section_order contains DESIGN_INTENT and ENHANCEMENT_LAYER."""
    adapter = EmergentAdapter()
    assert PromptSection.DESIGN_INTENT in adapter.section_order
    assert PromptSection.ENHANCEMENT_LAYER in adapter.section_order


def test_TC_EMR_02_emergent_excludes_api_contracts_and_build_sequence():
    """TC-EMR-02: EmergentAdapter section_order does NOT contain API_CONTRACTS or BUILD_SEQUENCE."""
    adapter = EmergentAdapter()
    assert PromptSection.API_CONTRACTS not in adapter.section_order
    assert PromptSection.BUILD_SEQUENCE not in adapter.section_order


def test_TC_EMR_03_design_intent_renders_booking_mood():
    """TC-EMR-03: design_intent.j2 renders 'booking' mood for domain=booking."""
    from app.core.compiler.template_engine import render_design_intent
    from app.models import (
        EnrichedContext, JTBD, TechProfile, ExtractionConfidence, SessionNLPState
    )
    from uuid import uuid4

    ctx = EnrichedContext(
        session_id=uuid4(),
        jtbd=JTBD(functional_job="Book appointments", emotional_job="Feel organised"),
        personas=[],
        features=[],
        tech_profile=TechProfile(
            scale_tier="startup",
            needs_auth=True,
            needs_payments=False,
            primary_platform="web",
            estimated_users_month1=500,
        ),
        confidence=ExtractionConfidence(overall=0.9),
        nlp_state=SessionNLPState(app_domain="booking"),
    )

    result = render_design_intent(ctx)
    assert "booking" in result.lower() or "calm" in result.lower() or "calendly" in result.lower()


def test_TC_EMR_04_enhancement_layer_includes_mobile_note_when_mobile():
    """TC-EMR-04: enhancement_layer.j2 includes bottom nav/touch target for mobile platform."""
    from app.core.compiler.template_engine import render_enhancement_layer
    from app.models import EnrichedContext, JTBD, TechProfile, ExtractionConfidence, SessionNLPState
    from uuid import uuid4

    ctx = EnrichedContext(
        session_id=uuid4(),
        jtbd=JTBD(functional_job="x", emotional_job="y"),
        personas=[],
        features=[],
        tech_profile=TechProfile(
            scale_tier="startup",
            needs_auth=True,
            needs_payments=False,
            primary_platform="mobile",
            estimated_users_month1=100,
        ),
        confidence=ExtractionConfidence(overall=0.9),
        nlp_state=SessionNLPState(),
    )

    result = render_enhancement_layer(ctx)
    assert "mobile" in result.lower() or "44" in result


def test_TC_EMR_05_emergent_prompt_token_count_under_limit():
    """TC-EMR-05: Compiled Emergent prompt token count stays under 6000 tokens."""
    adapter = EmergentAdapter()
    sections = {s.value: f"## {s.value}\n\nSample content for {s.value} section. " * 5
                for s in adapter.section_order}
    prompt = adapter.assemble(sections)
    # Rough token estimate: words * 1.3
    token_estimate = len(prompt.split()) * 4 // 3
    assert token_estimate < adapter.max_prompt_tokens
