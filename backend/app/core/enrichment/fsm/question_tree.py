from dataclasses import dataclass, field
from typing import Optional

from app.models import EnrichmentPhase


@dataclass
class Question:
    id: str
    phase: EnrichmentPhase
    text: str
    quick_replies: list[str] = field(default_factory=list)
    probe_text: str = ""


# ---------------------------------------------------------------------------
# Phase 1 — IDEA (Q1–Q3)
# ---------------------------------------------------------------------------

Q1 = Question(
    id="Q1",
    phase=EnrichmentPhase.IDEA,
    text=(
        "What is the core problem your app solves? Describe it in 1–3 sentences "
        "— focus on who is frustrated and why."
    ),
    quick_replies=["It's for consumers", "It's for businesses", "It's an internal tool"],
    probe_text=(
        "Can you be more specific? What situation triggers someone to need this app?"
    ),
)

Q2 = Question(
    id="Q2",
    phase=EnrichmentPhase.IDEA,
    text=(
        "Who are the primary users of this app? Describe them — their role, context, "
        "and how often they'd use it."
    ),
    quick_replies=["End consumers", "Business professionals", "Mixed audience"],
    probe_text=(
        "Tell me more about them — what do they do and what's their relationship "
        "with technology?"
    ),
)

Q3 = Question(
    id="Q3",
    phase=EnrichmentPhase.IDEA,
    text=(
        "What does success look like for a user after they've used your app? "
        "What changes for them?"
    ),
    quick_replies=["They save time", "They make more money", "They feel less stressed"],
    probe_text=(
        "Be specific — what would they say or do differently after using your app?"
    ),
)

# ---------------------------------------------------------------------------
# Phase 2 — TOUCHPOINTS (Q4–Q6)
# ---------------------------------------------------------------------------

Q4 = Question(
    id="Q4",
    phase=EnrichmentPhase.TOUCHPOINTS,
    text=(
        "Are there multiple types of users in your app — for example, an admin, "
        "a customer, and a vendor? List every role that logs in."
    ),
    quick_replies=[
        "Just one type of user",
        "Two roles (e.g. admin + user)",
        "Three or more roles",
    ],
    probe_text=(
        "Think about who manages the app vs. who uses it — are those the same person?"
    ),
)

Q5 = Question(
    id="Q5",
    phase=EnrichmentPhase.TOUCHPOINTS,
    text="What device do most users primarily use — mobile, desktop, or both?",
    quick_replies=["Mobile (phone/tablet)", "Desktop (browser)", "Both equally"],
    probe_text=(
        "Even a rough guess helps — would this mostly be used on the go or at a desk?"
    ),
)

Q6 = Question(
    id="Q6",
    phase=EnrichmentPhase.TOUCHPOINTS,
    text=(
        "Does your app need user accounts and login? If yes, should users sign up "
        "with email, Google, or both?"
    ),
    quick_replies=["Yes — email only", "Yes — Google/social login", "No login needed"],
    probe_text=(
        "Would users need to save their data or history between sessions?"
    ),
)

# ---------------------------------------------------------------------------
# Phase 3 — FEATURES (Q7–Q9)
# ---------------------------------------------------------------------------

Q7 = Question(
    id="Q7",
    phase=EnrichmentPhase.FEATURES,
    text=(
        "List the 3–5 core features your app must have on day one. These are the "
        "things without which the app doesn't work."
    ),
    quick_replies=["Search/browse", "Create/submit", "View/track", "Communicate", "Pay/checkout"],
    probe_text=(
        "Imagine the app is live and a user opens it for the first time — what are "
        "the first 3 things they need to be able to do?"
    ),
)

Q8 = Question(
    id="Q8",
    phase=EnrichmentPhase.FEATURES,
    text=(
        "What could go wrong in your app that you want to handle gracefully? "
        "Think about empty states, errors, and edge cases."
    ),
    quick_replies=[
        "No results found",
        "Payment fails",
        "Connection error",
        "Permission denied",
    ],
    probe_text=(
        "What would frustrate a user most if it broke? What's the worst-case "
        "scenario for your users?"
    ),
)

Q9 = Question(
    id="Q9",
    phase=EnrichmentPhase.FEATURES,
    text=(
        "Is there one feature that would genuinely delight users — something beyond "
        "the basics that would make them love the app?"
    ),
    quick_replies=[
        "Smart recommendations",
        "Real-time updates",
        "One-click actions",
        "Personalisation",
    ],
    probe_text=(
        "What's the 'wow' moment — the feature users would mention when recommending "
        "the app to a friend?"
    ),
)

# ---------------------------------------------------------------------------
# Phase 4 — TECHNICAL (Q10–Q14)
# ---------------------------------------------------------------------------

Q10 = Question(
    id="Q10",
    phase=EnrichmentPhase.TECHNICAL,
    text=(
        "Does your app need to accept payments? If yes — subscriptions, one-off "
        "purchases, or a marketplace model?"
    ),
    quick_replies=["No payments", "One-off purchases", "Subscriptions", "Marketplace"],
    probe_text=(
        "Even if payments come later — do you want the system designed to support "
        "them from day one?"
    ),
)

Q11 = Question(
    id="Q11",
    phase=EnrichmentPhase.TECHNICAL,
    text=(
        "Does your app need to integrate with any external services? Examples: "
        "Google Calendar, Stripe, Twilio, Zapier, WhatsApp."
    ),
    quick_replies=[
        "No integrations needed",
        "Email/notifications",
        "Calendar",
        "Payments only",
    ],
    probe_text=(
        "Think about your workflow — are there tools your users already use that "
        "this app should connect to?"
    ),
)

Q12 = Question(
    id="Q12",
    phase=EnrichmentPhase.TECHNICAL,
    text=(
        "How many users do you expect in the first month — roughly? This helps "
        "size the tech stack correctly."
    ),
    quick_replies=[
        "Under 100 (prototype)",
        "100–1,000 (early startup)",
        "1,000–10,000 (growth)",
        "10,000+ (scale)",
    ],
    probe_text=(
        "Even a rough order of magnitude helps — is this for a small team, "
        "a niche community, or a broad audience?"
    ),
)

Q13 = Question(
    id="Q13",
    phase=EnrichmentPhase.TECHNICAL,
    text=(
        "Which vibe-coding platform will you use to build this? This determines "
        "how the prompt is structured."
    ),
    quick_replies=["Replit", "Bolt", "Lovable", "v0", "Cursor", "Emergent"],
    probe_text=(
        "Not sure? Just pick the one you've heard of — you can change it later."
    ),
)

Q14 = Question(
    id="Q14",
    phase=EnrichmentPhase.TECHNICAL,
    text=(
        "Anything else important about your app that you haven't mentioned? "
        "Technical constraints, business requirements, or things the AI should know."
    ),
    quick_replies=[
        "That covers it",
        "Must be GDPR compliant",
        "Needs to be offline-capable",
        "Multi-language support",
    ],
    probe_text=(
        "Think about constraints — budget, timeline, existing systems, regulatory "
        "requirements, or non-negotiables."
    ),
)

# ---------------------------------------------------------------------------
# Phase → question mapping
# ---------------------------------------------------------------------------

PHASE_QUESTIONS: dict[str, list[Question]] = {
    "IDEA": [Q1, Q2, Q3],
    "TOUCHPOINTS": [Q4, Q5, Q6],
    "FEATURES": [Q7, Q8, Q9],
    "TECHNICAL": [Q10, Q11, Q12, Q13, Q14],
}

PHASE_ORDER: list[str] = [
    "IDLE",
    "IDEA",
    "TOUCHPOINTS",
    "FEATURES",
    "TECHNICAL",
    "EXTRACTING",
    "ENRICHED",
    "PREVIEWING",
    "READY",
]


def get_questions_for_phase(phase: str) -> list[Question]:
    """Return the ordered list of Question objects for the given phase name."""
    return PHASE_QUESTIONS.get(phase, [])


def phase_complete(answered_count: int, phase: str) -> bool:
    """Return True when all questions in a phase have been answered."""
    return answered_count >= len(PHASE_QUESTIONS.get(phase, []))


def next_phase(current: str) -> str:
    """Return the name of the phase that follows *current* in PHASE_ORDER."""
    idx = PHASE_ORDER.index(current)
    return PHASE_ORDER[idx + 1] if idx + 1 < len(PHASE_ORDER) else current


def progress_pct(phase: str, question_index: int) -> int:
    """Return an integer percentage (0–95) based on completed Q&A pairs.

    The maximum returned is 95 — the final 5 % is awarded when extraction
    completes and the session moves to ENRICHED.
    """
    total_questions = 14
    answered = 0
    for p in ["IDEA", "TOUCHPOINTS", "FEATURES", "TECHNICAL"]:
        if PHASE_ORDER.index(p) < PHASE_ORDER.index(phase):
            answered += len(PHASE_QUESTIONS[p])
        elif p == phase:
            answered += question_index
            break
    return min(int(answered / total_questions * 100), 95)
