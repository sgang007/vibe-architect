from __future__ import annotations

import json

from .base import AbstractLLMAdapter

MOCK_EXTRACTION_RESPONSE = {
    "jtbd": {
        "functional_job": "Manage bookings efficiently",
        "emotional_job": "Feel in control of my schedule",
        "social_job": "Impress clients with professional service",
    },
    "personas": [
        {
            "id": "end-user",
            "name": "Sarah",
            "role": "Client",
            "primary_goal": "Book appointments easily",
            "key_frustration": "Hard to find available slots",
            "entry_trigger": "Needs to schedule a service",
            "primary_device": "mobile",
            "tech_comfort": "medium",
            "usage_frequency": "weekly",
            "power_level": "champion",
            "success_signal": "Confirmation email received",
        }
    ],
    "features": [
        {
            "id": "booking",
            "name": "Appointment Booking",
            "description": "Users can book time slots",
            "moscow": "must",
            "kano": "basic",
            "related_persona_ids": ["end-user"],
            "ux_flags": ["ZEIGARNIK", "EMPTY_STATE"],
            "is_delight_feature": False,
        }
    ],
    "tech_profile": {
        "scale_tier": "startup",
        "needs_auth": True,
        "needs_payments": False,
        "payment_type": None,
        "integrations": [],
        "primary_platform": "web",
        "estimated_users_month1": 500,
    },
    "confidence": {"overall": 0.85, "low_confidence_fields": []},
}

MOCK_NARRATIVE_RESPONSE = {
    "product_identity": (
        "This is a booking application that helps clients schedule appointments with service "
        "providers. Sarah, the primary user, uses the app weekly to find and book available "
        "time slots. The app reduces friction in the scheduling process and helps providers "
        "manage their availability. Users feel confident and organised after successfully "
        "booking their appointments."
    ),
    "user_stories": (
        "FEATURE: Appointment Booking | PERSONA: Sarah\n"
        "Given: Sarah is logged in\n"
        "When: She selects a date and time\n"
        "Then: She receives a confirmation\n"
        "  And: The slot is marked unavailable"
    ),
    "edge_cases": (
        "[AUTH] User session expires during booking — redirect to login and restore booking state\n"
        "[EMPTY_STATE] No available slots — show calendar with next available date highlighted"
    ),
}


class MockLLMAdapter(AbstractLLMAdapter):
    """In-memory mock adapter for unit testing.

    Call 1 (temperature < 0.5) returns a realistic extraction JSON.
    Call 2 (temperature >= 0.5) returns a realistic narrative JSON.
    """

    def __init__(
        self,
        extraction_response: dict | None = None,
        narrative_response: dict | None = None,
    ):
        self._extraction = extraction_response or MOCK_EXTRACTION_RESPONSE
        self._narrative = narrative_response or MOCK_NARRATIVE_RESPONSE
        self._call_count = 0

    @property
    def max_context_tokens(self) -> int:
        return 131072

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
    ) -> str:
        self._call_count += 1
        if temperature < 0.5:  # Call 1 — extraction (low temperature for determinism)
            return json.dumps(self._extraction)
        else:  # Call 2 — narrative (higher temperature for creativity)
            return json.dumps(self._narrative)

    @property
    def call_count(self) -> int:
        return self._call_count
