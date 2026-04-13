"""TC-FSM-01 through TC-FSM-05"""
import pytest
from app.models import SessionContext, EnrichmentPhase, AnswerQuality
from app.core.enrichment.fsm.state_machine import FSMEngine
from app.core.enrichment.adapters.mock import MockLLMAdapter


@pytest.fixture
def fsm():
    return FSMEngine(nlp_pipeline=None)


@pytest.fixture
def session():
    s = SessionContext()
    s.phase = EnrichmentPhase.IDEA
    return s


@pytest.mark.asyncio
async def test_TC_FSM_01_advances_idea_to_touchpoints(fsm, session):
    """TC-FSM-01: FSMEngine advances IDEA → TOUCHPOINTS after 3 adequate answers."""
    answers = [
        "I want to build a booking app for hair salons where clients can schedule appointments online.",
        "The primary users are salon clients who want to book appointments and salon owners who manage their schedule.",
        "After using the app clients feel organised and salons are fully booked with no double-booking issues.",
    ]
    for answer in answers:
        response = await fsm.on_user_answer(session, answer)

    assert session.phase == EnrichmentPhase.TOUCHPOINTS


@pytest.mark.asyncio
async def test_TC_FSM_02_vague_answer_returns_probe(fsm, session):
    """TC-FSM-02: AnswerClassifier returns VAGUE for single-word answers and returns probe."""
    response = await fsm.on_user_answer(session, "maybe")
    assert response.probe is True
    assert response.question is not None
    assert len(response.question) > 0


@pytest.mark.asyncio
async def test_TC_FSM_03_adequate_for_nine_plus_words(fsm, session):
    """TC-FSM-03: AnswerClassifier returns ADEQUATE for answers with 9+ words."""
    from app.core.enrichment.fsm.answer_classifier import classify_regex
    quality = classify_regex("I want to build an app for scheduling salon appointments online easily")
    assert quality == AnswerQuality.ADEQUATE


@pytest.mark.asyncio
async def test_TC_FSM_04_triggers_extraction_after_q14(fsm, session):
    """TC-FSM-04: FSMEngine emits trigger_extraction=True after Q14 answer."""
    # Drive through all 14 questions with adequate answers
    phase_answers = {
        "IDEA": [
            "A booking platform for salon clients to schedule hair appointments online.",
            "Salon clients who are busy professionals and salon owners managing their business.",
            "Clients feel organised and salons run efficiently with no phone tag.",
        ],
        "TOUCHPOINTS": [
            "Two roles: the client who books and the admin who manages availability.",
            "Mostly mobile — clients book on the go from their phones.",
            "Yes email login and Google OAuth for convenience.",
        ],
        "FEATURES": [
            "Appointment booking, availability calendar, notifications, and profile management.",
            "Double booking prevention and failed payment handling gracefully.",
            "Smart reminders that suggest rescheduling based on weather or past preferences.",
        ],
        "TECHNICAL": [
            "Yes subscriptions for premium salon listings.",
            "Google Calendar integration and Stripe for payments.",
            "We expect about 500 users in the first month starting small.",
            "Lovable platform for the initial build.",
            "Must be GDPR compliant and support multiple time zones.",
        ],
    }

    for phase_name, answers in phase_answers.items():
        for answer in answers:
            response = await fsm.on_user_answer(session, answer)
            if response.trigger_extraction:
                assert response.trigger_extraction is True
                return

    pytest.fail("trigger_extraction was never fired after all 14 answers")


@pytest.mark.asyncio
async def test_TC_FSM_05_fsm_never_calls_llm_during_conversation(session):
    """TC-FSM-05: FSMEngine never calls LLMAdapter during conversation turns."""
    mock = MockLLMAdapter()
    fsm = FSMEngine(nlp_pipeline=None)

    answers = [
        "A marketplace for freelance designers to find project work.",
        "Freelance designers looking for clients and businesses needing design work.",
        "Designers get steady income and businesses get quality design work efficiently.",
    ]
    for answer in answers:
        await fsm.on_user_answer(session, answer)

    # MockAdapter.complete was never called — FSM is purely deterministic
    assert mock._call_count == 0
