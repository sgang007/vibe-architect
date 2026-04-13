from __future__ import annotations
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.models import EnrichedContext, AppPreview, NarrativeOutput

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates", "base")


def _get_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape([]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_tech_stack(ctx: EnrichedContext, platform: str) -> str:
    env = _get_env()
    t = env.get_template("tech_stack.j2")
    fe = "React Native + Expo" if ctx.tech_profile.primary_platform == "mobile" else "React 18 + Vite + TypeScript + Tailwind CSS"
    if ctx.tech_profile.scale_tier == "prototype":
        be = "Supabase"
    elif ctx.tech_profile.needs_payments:
        be = "Node.js + Express + Supabase + Stripe"
    else:
        be = "Node.js + Express + Supabase"
    return t.render(tech_profile=ctx.tech_profile, platform=platform, tech_stack_fe=fe, tech_stack_be=be)


def render_screen_spec(ctx: EnrichedContext, preview: AppPreview) -> str:
    env = _get_env()
    t = env.get_template("screen_spec.j2")
    return t.render(site_map=preview.site_map, personas=ctx.personas)


def render_build_sequence(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("build_sequence.j2")
    must_have = [f for f in ctx.features if f.moscow == "must"]
    fe = "React Native + Expo" if ctx.tech_profile.primary_platform == "mobile" else "React 18 + Vite"
    be = "Supabase" if ctx.tech_profile.scale_tier == "prototype" else "Node.js + Supabase"
    base_step = 6 if ctx.tech_profile.needs_auth else 4
    payments_step = base_step + len(must_have) + 1
    final_steps_start = payments_step + (1 if ctx.tech_profile.needs_payments else 0)
    return t.render(
        tech_profile=ctx.tech_profile,
        must_have_features=must_have,
        tech_stack_fe=fe,
        tech_stack_be=be,
        loop_start=base_step + 1,
        loop_next=base_step + 2,
        base_step=base_step + 2,
        payments_step=payments_step,
        final_steps_start=final_steps_start + 1,
    )


def render_data_model(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("data_model.j2")
    return t.render(personas=ctx.personas, features=ctx.features, tech_profile=ctx.tech_profile)


def render_api_contract(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("api_contract.j2")
    return t.render(features=ctx.features, tech_profile=ctx.tech_profile)


def render_design_system() -> str:
    env = _get_env()
    t = env.get_template("design_system.j2")
    return t.render()


def render_nfr(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("nfr.j2")
    return t.render(tech_profile=ctx.tech_profile)


def render_design_intent(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("design_intent.j2")
    return t.render(
        tech_profile=ctx.tech_profile,
        app_domain=ctx.nlp_state.app_domain or "default",
        domain_color_mood="calm and trustworthy",
    )


def render_enhancement_layer(ctx: EnrichedContext) -> str:
    env = _get_env()
    t = env.get_template("enhancement_layer.j2")
    return t.render(tech_profile=ctx.tech_profile)


def render_user_personas(ctx: EnrichedContext) -> str:
    lines = ["## User Personas\n"]
    for p in ctx.personas:
        lines.append(f"### {p.name} — {p.role}")
        lines.append(f"- Goal: {p.primary_goal}")
        lines.append(f"- Frustration: {p.key_frustration}")
        lines.append(f"- Device: {p.primary_device} | Tech comfort: {p.tech_comfort}")
        lines.append(f"- Uses the app: {p.usage_frequency}")
        lines.append(f"- Power level: {p.power_level}")
        lines.append(f"- Success signal: {p.success_signal}")
        lines.append("")
    return "\n".join(lines)


def render_screen_inventory(preview: AppPreview) -> str:
    lines = ["## Screen Inventory\n"]
    for i, screen in enumerate(preview.site_map, 1):
        lines.append(f"{i}. **{screen.name}** — {screen.purpose}")
    return "\n".join(lines)


def build_all_sections(
    ctx: EnrichedContext,
    preview: AppPreview,
    narrative: NarrativeOutput,
    platform: str,
) -> dict[str, str]:
    return {
        "product_identity": f"## Product Identity\n\n{narrative.product_identity}",
        "user_personas": render_user_personas(ctx),
        "screen_inventory": render_screen_inventory(preview),
        "screen_specs": render_screen_spec(ctx, preview),
        "data_models": render_data_model(ctx),
        "tech_stack": render_tech_stack(ctx, platform),
        "user_stories": f"## User Stories (Acceptance Criteria)\n\n{narrative.user_stories}",
        "edge_cases": f"## Edge Cases\n\n{narrative.edge_cases}",
        "nfr": render_nfr(ctx),
        "api_contracts": render_api_contract(ctx),
        "build_sequence": render_build_sequence(ctx),
        "design_system": render_design_system(),
        "design_intent": render_design_intent(ctx),
        "enhancement_layer": render_enhancement_layer(ctx),
    }
