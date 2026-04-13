from app.models import EnrichedContext, AppPreview, SessionContext, EnrichmentPhase
from .ia_builder import derive_screens
from .flow_mapper import build_flows
from .wireframe_gen import generate_all
from .complexity_scorer import score


class PreviewEngine:
    async def generate(self, session: SessionContext) -> AppPreview:
        ctx = session.enriched_context
        if not ctx:
            raise ValueError("EnrichedContext not available \u2014 run extraction first")

        screens = derive_screens(ctx)
        screens = generate_all(screens)
        flows = build_flows(ctx)
        preview = AppPreview(session_id=session.session_id, site_map=screens, user_flows=flows)
        preview.complexity = score(ctx, preview)

        session.app_preview = preview
        session.phase = EnrichmentPhase.READY
        return preview
