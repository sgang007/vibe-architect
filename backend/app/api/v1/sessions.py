from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from uuid import UUID
from app.models import SessionContext, EnrichmentPhase
from app.core.enrichment.fsm.state_machine import FSMEngine

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory store (replace with Redis in production)
_sessions: dict[str, SessionContext] = {}


class CreateSessionResponse(BaseModel):
    session_id: str
    first_question: str
    quick_replies: list[str]
    phase: str


@router.post("", response_model=CreateSessionResponse)
async def create_session(request: Request):
    session = SessionContext()
    session.phase = EnrichmentPhase.IDEA
    _sessions[str(session.session_id)] = session

    fsm = FSMEngine()
    first = fsm.get_first_question()

    return CreateSessionResponse(
        session_id=str(session.session_id),
        first_question=first.question,
        quick_replies=first.quick_replies,
        phase="IDEA",
    )


@router.get("/{session_id}")
async def get_session(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = {
        "session_id": str(session.session_id),
        "phase": session.phase.value,
        "turn_count": len(session.fsm_turns),
        "fsm_turns": [t.model_dump(mode="json") for t in session.fsm_turns],
        "total_cost_usd": session.total_cost_usd,
        "call1_tokens": session.call1_tokens,
        "call2_tokens": session.call2_tokens,
        "has_enriched_context": session.enriched_context is not None,
        "has_preview": session.app_preview is not None,
    }
    if session.enriched_context is not None:
        ec = session.enriched_context
        result["enriched_context"] = {
            "jtbd": ec.jtbd.model_dump(),
            "personas": [p.model_dump() for p in ec.personas],
            "features": [f.model_dump() for f in ec.features],
            "tech_profile": ec.tech_profile.model_dump(),
            "confidence": ec.confidence.model_dump(),
        }
    return result


def get_session_or_404(session_id: str) -> SessionContext:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
