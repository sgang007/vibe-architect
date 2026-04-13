from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

_nlp_pipeline = None


def set_nlp_pipeline(pipeline):
    global _nlp_pipeline
    _nlp_pipeline = pipeline


@router.get("")
async def health():
    return {"status": "ok"}


@router.get("/nlp")
async def nlp_health():
    if _nlp_pipeline is None:
        return {"status": "nlp_not_initialized", "models": {}}
    return {"status": "ok", "models": _nlp_pipeline.get_health()}
