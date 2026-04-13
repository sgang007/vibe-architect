from __future__ import annotations
import json
import asyncio
from uuid import UUID
from typing import AsyncIterator
from app.models import SessionContext, EnrichmentPhase, FSMResponse
from app.core.enrichment.adapters import get_adapter, get_fallback_adapter
from app.core.enrichment.adapters.base import AdapterRateLimitError
from app.core.enrichment.fsm.state_machine import FSMEngine
from app.core.enrichment.extraction.extractor import ContextExtractor, ExtractionError
from app.core.enrichment.scoring.rice_calculator import calculate_all
from app.core.enrichment.scoring.persona_matrix import build_matrix
from app.core.enrichment.nlp.pipeline import NLPPipeline


class EnrichmentEngine:
    def __init__(self):
        self.nlp = NLPPipeline()
        self.fsm = FSMEngine(nlp_pipeline=self.nlp)

    async def process_answer_stream(
        self,
        session: SessionContext,
        answer: str,
    ) -> AsyncIterator[str]:
        """Yields SSE-formatted events."""

        fsm_response: FSMResponse = await self.fsm.on_user_answer(session, answer)

        if fsm_response.trigger_extraction:
            yield self._sse("extracting", {})
            try:
                adapter = get_adapter()
                extractor = ContextExtractor(adapter)

                # Run extraction in a background task so we can send heartbeats
                # while the LLM API call is in progress.  Without heartbeats the
                # Vite proxy (and any other HTTP proxy) will kill the silent stream.
                result_holder: list = []
                error_holder: list = []

                async def _do_extract(ext: ContextExtractor):
                    try:
                        result_holder.append(await ext.extract(session))
                    except Exception as exc:
                        error_holder.append(exc)

                task = asyncio.create_task(_do_extract(extractor))

                # Send an SSE comment every 3 s — proxies and browsers treat
                # SSE comments as "stream is alive" pings.
                while not task.done():
                    await asyncio.sleep(3)
                    if not task.done():
                        yield ": keepalive\n\n"

                # If the primary adapter was rate-limited, try the fallback
                if error_holder and isinstance(error_holder[0], (AdapterRateLimitError, ExtractionError)):
                    orig_err = error_holder[0]
                    # Check if it's a rate-limit wrapped inside ExtractionError
                    is_rate_limit = isinstance(orig_err, AdapterRateLimitError) or (
                        isinstance(orig_err, ExtractionError) and
                        "rate limit" in str(orig_err).lower()
                    )
                    if is_rate_limit:
                        fallback = get_fallback_adapter()
                        if fallback:
                            yield ": switching to fallback AI\n\n"
                            error_holder.clear()
                            fallback_extractor = ContextExtractor(fallback)
                            fb_task = asyncio.create_task(_do_extract(fallback_extractor))
                            while not fb_task.done():
                                await asyncio.sleep(3)
                                if not fb_task.done():
                                    yield ": keepalive\n\n"

                # Re-raise any remaining extraction error
                if error_holder:
                    raise error_holder[0]

                enriched_ctx, tokens = result_holder[0]

                # Deterministic scoring
                rice_scores = calculate_all(enriched_ctx.features, enriched_ctx.personas)
                matrix = build_matrix(enriched_ctx.features, enriched_ctx.personas)

                session.enriched_context = enriched_ctx
                session.call1_tokens = tokens
                session.total_cost_usd += tokens * 0.59 / 1_000_000
                session.phase = EnrichmentPhase.ENRICHED

                complexity_score = len(enriched_ctx.features) + len(enriched_ctx.personas)
                yield self._sse("extracted", {
                    "complexity_score": complexity_score,
                    "phase": session.phase.value,
                    "progress_pct": 100,
                })
            except ExtractionError as e:
                yield self._sse("error", {"code": "extraction_failed", "message": str(e)})
            except Exception as e:
                yield self._sse("error", {"code": "extraction_failed", "message": str(e)})
        elif fsm_response.probe:
            yield self._sse("probe", {"text": fsm_response.question})
        elif fsm_response.question:
            data = {
                "text": fsm_response.question,
                "quick_replies": fsm_response.quick_replies,
                "phase": fsm_response.phase.value if fsm_response.phase else None,
                "progress_pct": fsm_response.progress_pct,
            }
            if fsm_response.phase != session.phase:
                yield self._sse("phase_advance", {
                    "new_phase": fsm_response.phase.value if fsm_response.phase else None,
                    "progress_pct": fsm_response.progress_pct,
                    "label": fsm_response.phase.value if fsm_response.phase else "",
                })
            yield self._sse("question", data)

    @staticmethod
    def _sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"
