from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.core.enrichment.engine import EnrichmentEngine
from .sessions import get_session_or_404

router = APIRouter(prefix="/enrichment", tags=["enrichment"])
engine = EnrichmentEngine()


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


@router.post("/answer")
async def submit_answer(req: AnswerRequest):
    session = get_session_or_404(req.session_id)

    async def event_stream():
        async for event in engine.process_answer_stream(session, req.answer):
            yield event

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            # Prevent ANY proxy/CDN/nginx from buffering the stream —
            # events must reach the browser as they are yielded
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
