import logging
from fastapi import APIRouter, HTTPException
from app.core.compiler.engine import CompilerEngine
from app.core.enrichment.adapters.base import AdapterRateLimitError
from app.core.enrichment.adapters import get_fallback_adapter
from .sessions import get_session_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/compile", tags=["compile"])
compiler = CompilerEngine()

VALID_PLATFORMS = ["replit", "bolt", "lovable", "v0", "cursor", "emergent"]


@router.post("/{session_id}/{platform}")
async def compile_prompt(session_id: str, platform: str):
    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Invalid platform. Choose from: {VALID_PLATFORMS}")

    session = get_session_or_404(session_id)
    if not session.enriched_context:
        raise HTTPException(status_code=400, detail="Session must be enriched first")
    if not session.app_preview:
        raise HTTPException(status_code=400, detail="Preview must be generated first")

    try:
        prompt = await compiler.compile(session, platform)
        return {
            "session_id": session_id,
            "platform": platform,
            "prompt": prompt,
            "token_estimate": len(prompt.split()) * 4 // 3,
        }
    except AdapterRateLimitError:
        # Primary adapter (Groq) rate-limited — try fallback (Anthropic/OpenAI)
        fallback = get_fallback_adapter()
        if fallback:
            logger.warning("Groq rate limited on compile — retrying with fallback adapter")
            try:
                prompt = await compiler.compile(session, platform, adapter_override=fallback)
                return {
                    "session_id": session_id,
                    "platform": platform,
                    "prompt": prompt,
                    "token_estimate": len(prompt.split()) * 4 // 3,
                }
            except Exception as fb_err:
                raise HTTPException(status_code=500, detail=f"Fallback also failed: {fb_err}")
        raise HTTPException(
            status_code=429,
            detail="AI rate limit reached. Please wait a moment and try again.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
