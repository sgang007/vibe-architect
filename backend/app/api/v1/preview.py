from fastapi import APIRouter, HTTPException
from app.core.preview.engine import PreviewEngine
from .sessions import get_session_or_404

router = APIRouter(prefix="/preview", tags=["preview"])
preview_engine = PreviewEngine()


@router.post("/{session_id}")
async def generate_preview(session_id: str):
    session = get_session_or_404(session_id)
    if not session.enriched_context:
        raise HTTPException(status_code=400, detail="Session must be enriched first")
    preview = await preview_engine.generate(session)
    return {
        "session_id": session_id,
        "screen_count": len(preview.site_map),
        "screens": [{"id": s.id, "name": s.name, "purpose": s.purpose, "svg": s.svg} for s in preview.site_map],
        "user_flows": [{"persona_id": f.persona_id, "persona_name": f.persona_name, "node_count": len(f.nodes)} for f in preview.user_flows],
        "complexity": preview.complexity.model_dump() if preview.complexity else None,
    }
