from app.models import EnrichedContext, AppPreview, ComplexityScore


def score(ctx: EnrichedContext, preview: AppPreview) -> ComplexityScore:
    screen_count = len(preview.site_map)
    feature_count = len(ctx.features)
    persona_count = len(ctx.personas)
    has_payments = ctx.tech_profile.needs_payments
    has_auth = ctx.tech_profile.needs_auth

    complexity_points = screen_count + feature_count + persona_count
    if has_payments:
        complexity_points += 4
    if has_auth:
        complexity_points += 3

    if complexity_points <= 12:
        tier = "simple"
        effort_weeks = "1\u20132 weeks"
    elif complexity_points <= 24:
        tier = "moderate"
        effort_weeks = "3\u20135 weeks"
    else:
        tier = "complex"
        effort_weeks = "6\u201310 weeks"

    suggestions = []
    if feature_count > 6:
        wont_features = [f.name for f in ctx.features if f.moscow in ("could", "wont")][:3]
        if wont_features:
            suggestions.append(f"Defer these features to v2: {', '.join(wont_features)}")

    if has_payments and ctx.tech_profile.scale_tier == "prototype":
        suggestions.append("Consider removing payments for initial prototype \u2014 add in v2")

    if persona_count > 3:
        suggestions.append("Focus on 1\u20132 primary personas for v1 to reduce scope")

    return ComplexityScore(
        tier=tier,
        screen_count=screen_count,
        feature_count=feature_count,
        effort_weeks=effort_weeks,
        scope_reduction_suggestions=suggestions,
    )
