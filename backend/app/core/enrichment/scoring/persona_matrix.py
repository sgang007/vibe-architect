"""Persona × Feature relevance matrix builder.

Produces a flat list of FeaturePersonaScore objects that capture whether a
given feature is relevant to each persona, and — when it is — copies the
persona's usage_frequency and power_level for use in downstream ranking and
narrative generation.
"""

from app.models import Feature, FeaturePersonaScore, Persona


def build_matrix(
    features: list[Feature], personas: list[Persona]
) -> list[FeaturePersonaScore]:
    """Build the full cross-product relevance matrix.

    For each (feature, persona) pair:
      - is_relevant is True when the persona's id appears in
        feature.related_persona_ids.
      - usage_frequency and power_level are populated only for relevant pairs
        so consumers can filter and rank easily.

    Returns:
        A flat list of FeaturePersonaScore objects (len = len(features) ×
        len(personas)).
    """
    matrix: list[FeaturePersonaScore] = []
    for feature in features:
        for persona in personas:
            relevant = persona.id in feature.related_persona_ids
            matrix.append(
                FeaturePersonaScore(
                    feature_id=feature.id,
                    persona_id=persona.id,
                    is_relevant=relevant,
                    usage_frequency=persona.usage_frequency if relevant else None,
                    power_level=persona.power_level if relevant else None,
                )
            )
    return matrix


def relevant_personas_for_feature(
    feature: Feature, personas: list[Persona]
) -> list[Persona]:
    """Convenience helper: return only the personas relevant to *feature*."""
    ids = set(feature.related_persona_ids)
    return [p for p in personas if p.id in ids]


def relevant_features_for_persona(
    persona: Persona, features: list[Feature]
) -> list[Feature]:
    """Convenience helper: return only the features relevant to *persona*."""
    return [f for f in features if persona.id in f.related_persona_ids]
