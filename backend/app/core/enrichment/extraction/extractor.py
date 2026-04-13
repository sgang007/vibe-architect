from __future__ import annotations

import json
from uuid import UUID

from app.core.enrichment.adapters.base import AbstractLLMAdapter, AdapterError
from app.models import EnrichedContext, SessionContext, SessionNLPState

from .prompt import EXTRACTION_SYSTEM_PROMPT, NLP_ANNOTATION_ADDENDUM
from .schema import EXTRACTION_SCHEMA


class ExtractionError(Exception):
    """Raised when the LLM call or schema validation fails during extraction."""


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------


def build_extraction_message(session: SessionContext) -> str:
    """Serialise the FSM conversation into a JSON payload for the LLM.

    If the session has NLP annotations (domain, entities, deduplicated
    features, etc.) they are injected as a separate ``nlp_annotations`` key
    so the LLM can use them as high-confidence priors.
    """
    qa_pairs = [
        {"question": turn.question_text, "answer": turn.answer}
        for turn in session.fsm_turns
    ]

    payload: dict = {
        "conversation": qa_pairs,
        "output_schema": EXTRACTION_SCHEMA,
        "instruction": "Extract the product context. Return only JSON.",
    }

    # Inject NLP annotations when meaningful signals are available
    nlp: SessionNLPState = session.nlp_state
    if nlp and (
        nlp.app_domain
        or nlp.entity_cache.tool_names
        or nlp.deduplicated_features
    ):
        payload["nlp_annotations"] = {
            "app_domain": nlp.app_domain,
            "app_domain_confidence": nlp.app_domain_confidence,
            "entity_cache": nlp.entity_cache.to_dict(),
            "feature_kano_hints": [h.model_dump() for h in nlp.feature_kano_hints],
            "deduplicated_features": nlp.deduplicated_features,
            "user_expertise_signal": nlp.user_expertise_signal,
            "low_confidence_turns": nlp.low_confidence_turns,
        }

    return json.dumps(payload, indent=2)


def build_system_prompt(has_nlp: bool) -> str:
    """Append the NLP addendum to the base system prompt when NLP data is present."""
    if has_nlp:
        return EXTRACTION_SYSTEM_PROMPT + "\n" + NLP_ANNOTATION_ADDENDUM
    return EXTRACTION_SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# Extractor
# ---------------------------------------------------------------------------


class ContextExtractor:
    """Drives Call 1 of the 2-LLM-call pipeline.

    Responsibilities:
      1. Build the system prompt (optionally with NLP addendum).
      2. Build the user message from the FSM conversation.
      3. Call the LLM adapter with json_mode=True.
      4. Parse and validate the response into an EnrichedContext.
      5. Return the context and a token count estimate.
    """

    def __init__(self, adapter: AbstractLLMAdapter) -> None:
        self.adapter = adapter

    async def extract(
        self, session: SessionContext
    ) -> tuple[EnrichedContext, int]:
        """Run the extraction and return (EnrichedContext, token_count).

        Raises:
            ExtractionError: on LLM failure, JSON parse failure, or schema
                             validation failure.
        """
        has_nlp = bool(
            session.nlp_state and session.nlp_state.app_domain
        )
        system_prompt = build_system_prompt(has_nlp)
        user_message = build_extraction_message(session)

        # ------------------------------------------------------------------
        # LLM call (Call 1)
        # ------------------------------------------------------------------
        try:
            raw = await self.adapter.complete(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.1,
                max_tokens=2048,
                json_mode=True,
            )
        except AdapterError as e:
            raise ExtractionError(f"LLM call failed: {e}") from e
        except Exception as e:
            raise ExtractionError(f"Unexpected error during LLM call: {e}") from e

        # ------------------------------------------------------------------
        # JSON parsing
        # ------------------------------------------------------------------
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ExtractionError(
                f"Invalid JSON from LLM (first 200 chars): {raw[:200]!r} — {e}"
            ) from e

        # ------------------------------------------------------------------
        # Pydantic validation
        # ------------------------------------------------------------------
        try:
            ctx = EnrichedContext(session_id=session.session_id, **data)
        except Exception as e:
            raise ExtractionError(f"Schema validation failed: {e}") from e

        # ------------------------------------------------------------------
        # Token accounting (rough estimate)
        # ------------------------------------------------------------------
        tokens = self.adapter.count_tokens(system_prompt + user_message + raw)
        return ctx, tokens
