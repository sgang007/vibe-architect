from __future__ import annotations
import json
from app.models import EnrichedContext, AppPreview, NarrativeOutput, SessionContext
from app.core.enrichment.adapters.base import AbstractLLMAdapter

NARRATIVE_SYSTEM_PROMPT = """You are a senior product manager and UX writer. You write clear, specific, professional product documentation that helps AI coding tools build great apps.

You will receive a structured product context object (JSON). You must return a JSON object with exactly three fields: product_identity, user_stories, and edge_cases.

Writing rules for product_identity:
  - Write 4-6 sentences of plain prose. No bullet points.
  - Lead with the core loop: who does what, how often, and what changes.
  - Name every persona and their relationship to the app.
  - End with the emotional promise: how users feel after a successful interaction.

Writing rules for user_stories:
  - Write one Given/When/Then story per feature per relevant persona.
  - Format: FEATURE: [name] | PERSONA: [name]\\nGiven: ...\\nWhen: ...\\nThen: ...\\n  And: ...
  - Each story must be independently testable.
  - Do not write stories for personas where is_relevant = false.

Writing rules for edge_cases:
  - Write one edge case per ux_flag raised across all features.
  - Also write: auth edge cases (if needs_auth), payment edge cases (if needs_payments), empty state edge case for every EMPTY_STATE flag.
  - Format each as: [CATEGORY] Description of what happens and what the app must do.

Return ONLY valid JSON. No markdown. No explanation."""


def build_narrative_message(ctx: EnrichedContext, preview: AppPreview, platform: str) -> str:
    return json.dumps({
        "enriched_context": {
            "jtbd": ctx.jtbd.model_dump(),
            "personas": [p.model_dump() for p in ctx.personas],
            "features": [f.model_dump() for f in ctx.features],
            "tech_profile": ctx.tech_profile.model_dump(),
        },
        "app_preview": {
            "screen_count": len(preview.site_map),
            "screen_names": [s.name for s in preview.site_map],
        },
        "target_platform": platform,
        "output_schema": {
            "product_identity": "string (4-6 sentences of prose)",
            "user_stories": "string (multi-line, one story per feature/persona pair)",
            "edge_cases": "string (multi-line, one edge case per line)"
        }
    }, indent=2)


class NarrativeSynthesizer:
    def __init__(self, adapter: AbstractLLMAdapter):
        self.adapter = adapter

    async def synthesize(
        self,
        session: SessionContext,
        platform: str,
        redis_client=None,
    ) -> NarrativeOutput:
        # 1. In-memory session cache — exact platform match
        if platform in session.narrative_outputs:
            return session.narrative_outputs[platform]

        # 2. Narrative content is platform-agnostic (same personas, features,
        #    user stories, edge cases). Re-use any already-generated narrative
        #    from another platform rather than making a redundant Groq call.
        #    Only the NarrativeOutput.platform label differs, so we copy it.
        if session.narrative_outputs:
            existing = next(iter(session.narrative_outputs.values()))
            reused = NarrativeOutput(
                session_id=existing.session_id,
                platform=platform,
                product_identity=existing.product_identity,
                user_stories=existing.user_stories,
                edge_cases=existing.edge_cases,
                call2_input_tokens=existing.call2_input_tokens,
                call2_output_tokens=existing.call2_output_tokens,
            )
            session.narrative_outputs[platform] = reused
            return reused

        # 3. Redis cache (shared across server restarts / instances)
        cache_key = f"narrative:{session.session_id}:{platform}"
        if redis_client:
            cached = await redis_client.get(cache_key)
            if cached:
                return NarrativeOutput.model_validate_json(cached)

        ctx = session.enriched_context
        preview = session.app_preview

        user_message = build_narrative_message(ctx, preview, platform)

        raw = await self.adapter.complete(
            system_prompt=NARRATIVE_SYSTEM_PROMPT,
            user_message=user_message,
            temperature=0.7,
            max_tokens=3000,
            json_mode=True,
        )

        data = json.loads(raw)
        tokens = self.adapter.count_tokens(NARRATIVE_SYSTEM_PROMPT + user_message + raw)

        output = NarrativeOutput(
            session_id=session.session_id,
            platform=platform,
            product_identity=data["product_identity"],
            user_stories=data["user_stories"],
            edge_cases=data["edge_cases"],
            call2_input_tokens=self.adapter.count_tokens(NARRATIVE_SYSTEM_PROMPT + user_message),
            call2_output_tokens=self.adapter.count_tokens(raw),
        )

        # Cache result
        if redis_client:
            await redis_client.setex(cache_key, 86400, output.model_dump_json())

        # Update session cost tracking
        session.narrative_outputs[platform] = output
        session.call2_tokens[platform] = tokens
        session.total_cost_usd += tokens * 0.59 / 1_000_000

        return output
