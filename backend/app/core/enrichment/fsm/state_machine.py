from __future__ import annotations

from app.models import (
    AnswerQuality,
    EnrichmentPhase,
    FSMResponse,
    FSMTurn,
    SessionContext,
)

from .answer_classifier import classify_regex
from .question_tree import (
    PHASE_ORDER,
    get_questions_for_phase,
    next_phase,
    phase_complete,
    progress_pct,
)

# Phases in which the FSM actively collects answers
_ACTIVE_PHASES = {"IDEA", "TOUCHPOINTS", "FEATURES", "TECHNICAL"}


class FSMEngine:
    """Finite-state-machine that drives the 14-question intake interview.

    The engine is stateless between calls: all mutable state lives in the
    *session* object that is passed in and mutated in place.

    If an optional *nlp_pipeline* is injected it is used to classify answer
    quality and annotate entities; otherwise the lightweight regex classifier
    is used as a fallback.
    """

    def __init__(self, nlp_pipeline=None):
        self.nlp = nlp_pipeline

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def on_user_answer(self, session: SessionContext, answer: str) -> FSMResponse:
        """Process a user answer and return the next FSM response.

        Side-effects:
          - Advances *session.phase* when a phase is complete.
          - Appends an FSMTurn to *session.fsm_turns* for each accepted answer.
          - Increments *session.probe_count_this_phase* on vague answers.
        """
        phase = session.phase.value

        # Initialise from IDLE on first answer
        if phase == "IDLE":
            session.phase = EnrichmentPhase.IDEA
            phase = "IDEA"

        if phase not in _ACTIVE_PHASES:
            return FSMResponse(question="Session is already complete.")

        # ------------------------------------------------------------------
        # 1. Classify answer quality
        # ------------------------------------------------------------------
        questions_for_phase = get_questions_for_phase(phase)
        answered_count_pre = self._answered_in_phase(session, phase)
        current_q_for_classification = (
            questions_for_phase[answered_count_pre]
            if answered_count_pre < len(questions_for_phase)
            else None
        )

        if self.nlp and self.nlp.enabled:
            annotation = await self.nlp.process_answer(answer, session.phase, session)
            quality = annotation.quality
        else:
            quality = classify_regex(answer)

        # Quick-reply answers are always valid — treat them as at least MINIMAL
        # even if they are single words (e.g. "Replit", "Bolt", "mobile").
        if (
            quality in (AnswerQuality.VAGUE, AnswerQuality.EMPTY)
            and current_q_for_classification is not None
        ):
            normalised = answer.strip().lower()
            quick_reply_normalised = [qr.lower() for qr in current_q_for_classification.quick_replies]
            if normalised in quick_reply_normalised:
                quality = AnswerQuality.MINIMAL

        # ------------------------------------------------------------------
        # 2. Handle vague / empty answers
        # ------------------------------------------------------------------
        if quality in (AnswerQuality.VAGUE, AnswerQuality.EMPTY):
            # Expert users (high expertise signal) get grace after the first probe
            if (
                session.user_expertise_signal > 0.7
                and session.probe_count_this_phase >= 1
            ):
                # Treat as minimal so we don't loop forever
                quality = AnswerQuality.MINIMAL
            else:
                session.probe_count_this_phase += 1
                questions = get_questions_for_phase(phase)
                answered_count = self._answered_in_phase(session, phase)
                if answered_count < len(questions):
                    q = questions[answered_count]
                    return FSMResponse(
                        question=q.probe_text,
                        quick_replies=[],
                        advance=False,
                        probe=True,
                        phase=session.phase,
                        progress_pct=progress_pct(phase, answered_count),
                    )

        # ------------------------------------------------------------------
        # 3. Record the accepted answer
        # ------------------------------------------------------------------
        questions = get_questions_for_phase(phase)
        answered_count = self._answered_in_phase(session, phase)

        # Guard: phase already exhausted (shouldn't happen in normal flow)
        if answered_count >= len(questions):
            return await self._advance_phase(session, phase)

        current_q = questions[answered_count]
        turn = FSMTurn(
            turn_index=len(session.fsm_turns),
            phase=session.phase,
            question_id=current_q.id,
            question_text=current_q.text,
            answer=answer,
            answer_quality=quality,
            quick_replies_shown=list(current_q.quick_replies),
        )
        session.fsm_turns.append(turn)
        session.probe_count_this_phase = 0

        # ------------------------------------------------------------------
        # 4. Advance or continue
        # ------------------------------------------------------------------
        new_answered = answered_count + 1
        if phase_complete(new_answered, phase):
            return await self._advance_phase(session, phase)

        # Still more questions in this phase
        next_q = questions[new_answered]
        return FSMResponse(
            question=next_q.text,
            quick_replies=list(next_q.quick_replies),
            phase=session.phase,
            progress_pct=progress_pct(phase, new_answered),
        )

    def get_first_question(self) -> FSMResponse:
        """Return the opening question without mutating any session."""
        from .question_tree import Q1

        return FSMResponse(
            question=Q1.text,
            quick_replies=list(Q1.quick_replies),
            phase=EnrichmentPhase.IDEA,
            progress_pct=0,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _answered_in_phase(self, session: SessionContext, phase: str) -> int:
        """Count the turns that belong to the given phase."""
        return sum(1 for t in session.fsm_turns if t.phase.value == phase)

    async def _advance_phase(
        self, session: SessionContext, current_phase: str
    ) -> FSMResponse:
        """Move to the next phase and return the appropriate response."""
        np = next_phase(current_phase)

        if np == "EXTRACTING":
            session.phase = EnrichmentPhase.EXTRACTING
            return FSMResponse(
                trigger_extraction=True,
                phase=EnrichmentPhase.EXTRACTING,
                progress_pct=100,
            )

        session.phase = EnrichmentPhase[np]
        session.probe_count_this_phase = 0

        if np in _ACTIVE_PHASES:
            next_questions = get_questions_for_phase(np)
            if next_questions:
                first_q = next_questions[0]
                return FSMResponse(
                    question=first_q.text,
                    quick_replies=list(first_q.quick_replies),
                    phase=session.phase,
                    progress_pct=progress_pct(np, 0),
                )

        return FSMResponse(phase=session.phase, progress_pct=100)
