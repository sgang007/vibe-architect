"""UX-law flag utilities.

The LLM extraction step already annotates each feature with the applicable
UX-law flags (HICKS_LAW, MILLERS_LAW, etc.).  This module provides thin
helpers for reading and querying those flags downstream — in the preview
engine, compiler, and scoring pipeline.
"""

from app.models import Feature

# Canonical set of UX-law flags the system recognises
UX_LAWS: frozenset[str] = frozenset(
    {
        "HICKS_LAW",
        "MILLERS_LAW",
        "DOHERTY",
        "ZEIGARNIK",
        "PEAK_END",
        "EMPTY_STATE",
    }
)


def get_ux_flags(feature: Feature) -> list[str]:
    """Return the UX-law flags that are set on *feature* and are recognised.

    Filters out any unrecognised strings that might have leaked from LLM
    hallucinations so consumers always receive a clean list.
    """
    return [f for f in feature.ux_flags if f in UX_LAWS]


def has_flag(feature: Feature, flag: str) -> bool:
    """Return True when *feature* has the given UX-law *flag* set."""
    return flag in feature.ux_flags


def flag_summary(feature: Feature) -> dict[str, bool]:
    """Return a dict mapping every known UX law to its presence on *feature*."""
    return {law: law in feature.ux_flags for law in sorted(UX_LAWS)}
