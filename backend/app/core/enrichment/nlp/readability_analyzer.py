import textstat
from app.models import ReadabilityResult, SessionContext


class ReadabilityAnalyzer:
    """Pure rule-based. Always enabled regardless of ENABLE_NLP_LAYER flag."""

    def analyze(self, text: str) -> ReadabilityResult:
        if not text or len(text.split()) < 3:
            return ReadabilityResult()
        return ReadabilityResult(
            flesch_reading_ease=textstat.flesch_reading_ease(text),
            flesch_kincaid_grade=textstat.flesch_kincaid_grade(text),
            gunning_fog=textstat.gunning_fog(text),
            word_count=len(text.split()),
        )

    def update_expertise_signal(self, session: SessionContext, result: ReadabilityResult) -> float:
        prev = session.user_expertise_signal or 0.0
        grade = result.flesch_kincaid_grade or 0.0
        alpha = 0.3
        new_signal = alpha * (min(grade, 16) / 16) + (1 - alpha) * prev
        session.user_expertise_signal = round(new_signal, 3)
        return session.user_expertise_signal
