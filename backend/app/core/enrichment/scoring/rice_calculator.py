"""RICE score calculator for features.

RICE = (Reach × Impact × Confidence) / Effort

Mappings
--------
Reach       → number of related personas (minimum 1)
Impact      → MoSCoW priority: must=3, should=2, could=1, wont=0
Confidence  → Kano category: basic=0.9, performance=0.7, delighter=0.5
Effort      → base 1, +1 if ZEIGARNIK flag (multi-step), +1 if ≥3 UX flags
"""

from app.models import Feature, Persona, RICEScore

_IMPACT_MAP: dict[str, float] = {
    "must": 3.0,
    "should": 2.0,
    "could": 1.0,
    "wont": 0.0,
}

_CONFIDENCE_MAP: dict[str, float] = {
    "basic": 0.9,
    "performance": 0.7,
    "delighter": 0.5,
}


def calculate_rice(feature: Feature, personas: list[Persona]) -> RICEScore:
    """Calculate the RICE score for a single feature.

    Args:
        feature:  The Feature to score.
        personas: The full list of personas in the session (used for context
                  only; reach is derived from feature.related_persona_ids).

    Returns:
        A populated RICEScore instance.
    """
    # Reach: at least 1 so we never divide by zero later
    reach = float(max(len(feature.related_persona_ids), 1))

    # Impact from MoSCoW; default to "could" level when unmapped
    impact = _IMPACT_MAP.get(feature.moscow, 1.0)

    # Confidence from Kano; default to "performance" level when unmapped
    confidence = _CONFIDENCE_MAP.get(feature.kano, 0.7)

    # Effort: start at base 1
    effort = 1.0
    if "ZEIGARNIK" in feature.ux_flags:
        effort += 1.0  # multi-step workflows cost more
    if len(feature.ux_flags) >= 3:
        effort += 1.0  # high UX complexity adds overhead

    score = (reach * impact * confidence) / max(effort, 1.0)

    return RICEScore(
        feature_id=feature.id,
        reach=reach,
        impact=impact,
        confidence=confidence,
        effort=effort,
        score=round(score, 2),
    )


def calculate_all(
    features: list[Feature], personas: list[Persona]
) -> list[RICEScore]:
    """Calculate RICE scores for every feature, sorted highest → lowest."""
    scores = [calculate_rice(f, personas) for f in features]
    return sorted(scores, key=lambda s: s.score, reverse=True)
