from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import sessions, enrichment, preview, compile, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialise NLP pipeline
    if settings.ENABLE_NLP_LAYER:
        from app.core.enrichment.nlp.pipeline import NLPPipeline
        from app.api.v1.health import set_nlp_pipeline
        pipeline = NLPPipeline()
        set_nlp_pipeline(pipeline)
    yield
    # Shutdown: cleanup


app = FastAPI(
    title="Vibe Architect API",
    description="Prompt intelligence engine for vibe-coding platforms",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router, prefix="/api/v1")
app.include_router(enrichment.router, prefix="/api/v1")
app.include_router(preview.router, prefix="/api/v1")
app.include_router(compile.router, prefix="/api/v1")
app.include_router(health.router)


@app.get("/")
async def root():
    return {"name": "Vibe Architect", "version": "3.0.0", "docs": "/docs"}
