from __future__ import annotations
from app.models import SessionContext, NarrativeOutput
from app.core.enrichment.adapters import get_adapter
from app.core.enrichment.adapters.base import AbstractLLMAdapter
from app.core.compiler.narrative_synth import NarrativeSynthesizer
from app.core.compiler.template_engine import build_all_sections
from app.core.compiler.adapters import get_platform_adapter


class CompilerEngine:
    async def compile(
        self,
        session: SessionContext,
        platform: str,
        redis_client=None,
        adapter_override: AbstractLLMAdapter | None = None,
    ) -> str:
        if not session.enriched_context or not session.app_preview:
            raise ValueError("Session must be enriched and previewed before compilation")

        # Call 2 — narrative synthesis (cached per session)
        # adapter_override is used when the primary adapter (Groq) is rate-limited
        adapter = adapter_override or get_adapter()
        synth = NarrativeSynthesizer(adapter)
        narrative = await synth.synthesize(session, platform, redis_client)

        # Build all 12+ sections
        sections = build_all_sections(
            session.enriched_context,
            session.app_preview,
            narrative,
            platform,
        )

        # Assemble with platform adapter
        platform_adapter = get_platform_adapter(platform)
        return platform_adapter.assemble(sections)
