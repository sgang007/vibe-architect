"""JSON schema descriptor passed to the LLM in the extraction prompt.

This is NOT a Pydantic model — it is a plain Python dict that is serialised
into the user message so the LLM knows exactly what shape to return.
"""

EXTRACTION_SCHEMA: dict = {
    "jtbd": {
        "functional_job": "string",
        "emotional_job": "string",
        "social_job": "string | null",
    },
    "personas": [
        {
            "id": "string (slug, e.g. end-user)",
            "name": "string",
            "role": "string",
            "primary_goal": "string",
            "key_frustration": "string",
            "entry_trigger": "string",
            "primary_device": "mobile | desktop | both",
            "tech_comfort": "low | medium | high",
            "usage_frequency": "daily | weekly | monthly | occasional | once",
            "power_level": "champion | key_player | show_stopper | spectator",
            "success_signal": "string",
        }
    ],
    "features": [
        {
            "id": "string (slug)",
            "name": "string",
            "description": "string",
            "moscow": "must | should | could | wont",
            "kano": "basic | performance | delighter",
            "related_persona_ids": ["string"],
            "ux_flags": [
                "HICKS_LAW | MILLERS_LAW | DOHERTY | ZEIGARNIK | PEAK_END | EMPTY_STATE"
            ],
            "is_delight_feature": "boolean",
        }
    ],
    "tech_profile": {
        "scale_tier": "prototype | startup | growth",
        "needs_auth": "boolean",
        "needs_payments": "boolean",
        "payment_type": "subscription | one-off | marketplace | null",
        "integrations": ["string"],
        "primary_platform": "web | mobile | both",
        "estimated_users_month1": "number",
    },
    "confidence": {
        "overall": "0.0-1.0",
        "low_confidence_fields": ["string"],
    },
}
