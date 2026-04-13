import re

from app.models import AnswerQuality

# One-word / stock phrases that signal the user hasn't really engaged
VAGUE_PHRASES: frozenset[str] = frozenset(
    {
        "yes",
        "no",
        "maybe",
        "idk",
        "not sure",
        "ok",
        "fine",
        "don't know",
        "no idea",
        "whatever",
        "something",
        "anything",
        "i don't know",
        "not really",
        "sort of",
        "kind of",
    }
)


def classify_regex(answer: str) -> AnswerQuality:
    """Fallback regex / word-count classifier used when NLP layer is disabled.

    Quality tiers:
      EMPTY   — no content at all
      VAGUE   — single stock phrase or fewer than 4 words
      MINIMAL — 4–8 words (some content but thin)
      ADEQUATE — 9+ words (enough to extract meaningful context)

    The NLP layer can upgrade MINIMAL → ADEQUATE or VAGUE → MINIMAL when it
    detects substantive entities even in short answers.
    """
    stripped = answer.strip()
    normalised = stripped.lower()
    # Collapse whitespace for word counting
    words = re.split(r"\s+", normalised) if normalised else []
    wc = len(words)

    if wc == 0:
        return AnswerQuality.EMPTY

    if normalised in VAGUE_PHRASES:
        return AnswerQuality.VAGUE

    if wc < 4:
        return AnswerQuality.VAGUE

    if wc < 9:
        return AnswerQuality.MINIMAL

    return AnswerQuality.ADEQUATE
