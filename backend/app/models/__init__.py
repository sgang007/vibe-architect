from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EnrichmentPhase(str, Enum):
    IDLE = "IDLE"
    IDEA = "IDEA"
    TOUCHPOINTS = "TOUCHPOINTS"
    FEATURES = "FEATURES"
    TECHNICAL = "TECHNICAL"
    EXTRACTING = "EXTRACTING"
    ENRICHED = "ENRICHED"
    PREVIEWING = "PREVIEWING"
    READY = "READY"


class AnswerQuality(str, Enum):
    EMPTY = "empty"
    VAGUE = "vague"
    MINIMAL = "minimal"
    ADEQUATE = "adequate"
    RICH = "rich"


class FSMTurn(BaseModel):
    turn_index: int
    phase: EnrichmentPhase
    question_id: str
    question_text: str
    answer: str
    answer_quality: AnswerQuality = AnswerQuality.ADEQUATE
    quick_replies_shown: list[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EntityCache(BaseModel):
    persona_candidates: set[str] = set()
    tool_names: set[str] = set()
    role_terms: set[str] = set()
    payment_signals: set[str] = set()
    scale_signals: set[str] = set()
    geographies: set[str] = set()

    def merge(self, new: dict[str, set]) -> None:
        for key, values in new.items():
            if hasattr(self, key):
                getattr(self, key).update(values)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> dict:
        return {k: list(v) for k, v in self.model_dump().items()}


class SentimentResult(BaseModel):
    label: Literal["positive", "neutral", "negative"]
    confidence: float
    kano_hint: Literal["basic", "performance", "delighter"]
    feature_type: Literal["pain_driven", "delight_driven"]


class DomainResult(BaseModel):
    domain: str
    confidence: float


class ReadabilityResult(BaseModel):
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    word_count: int = 0


class FeatureKanoHint(BaseModel):
    feature_text: str
    kano_hint: str
    sentiment_confidence: float


class SessionNLPState(BaseModel):
    app_domain: Optional[str] = None
    app_domain_confidence: float = 0.0
    entity_cache: EntityCache = Field(default_factory=EntityCache)
    feature_kano_hints: list[FeatureKanoHint] = []
    deduplicated_features: list[str] = []
    user_expertise_signal: float = 0.0
    low_confidence_turns: list[int] = []


class NLPAnnotation(BaseModel):
    quality: AnswerQuality
    entities: Optional[EntityCache] = None
    sentiment: Optional[SentimentResult] = None
    domain: Optional[DomainResult] = None
    readability_score: Optional[float] = None


# JTBD model
class JTBD(BaseModel):
    functional_job: str
    emotional_job: str
    social_job: Optional[str] = None


# Persona model (from Call 1 extraction)
class Persona(BaseModel):
    id: str
    name: str
    role: str
    primary_goal: str
    key_frustration: str
    entry_trigger: str
    primary_device: Literal["mobile", "desktop", "both"]
    tech_comfort: Literal["low", "medium", "high"]
    usage_frequency: Literal["daily", "weekly", "monthly", "occasional", "once"]
    power_level: Literal["champion", "key_player", "show_stopper", "spectator"]
    success_signal: str


# Feature model (from Call 1 extraction)
class Feature(BaseModel):
    id: str
    name: str
    description: str
    moscow: Literal["must", "should", "could", "wont"]
    kano: Literal["basic", "performance", "delighter"]
    related_persona_ids: list[str] = []
    ux_flags: list[str] = []
    is_delight_feature: bool = False


class TechProfile(BaseModel):
    scale_tier: Literal["prototype", "startup", "growth"]
    needs_auth: bool
    needs_payments: bool
    payment_type: Optional[Literal["subscription", "one-off", "marketplace"]] = None
    integrations: list[str] = []
    primary_platform: Literal["web", "mobile", "both"]
    estimated_users_month1: int = 100


class ExtractionConfidence(BaseModel):
    overall: float
    low_confidence_fields: list[str] = []


class EnrichedContext(BaseModel):
    session_id: UUID
    jtbd: JTBD
    personas: list[Persona]
    features: list[Feature]
    tech_profile: TechProfile
    confidence: ExtractionConfidence
    nlp_state: SessionNLPState = Field(default_factory=SessionNLPState)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RICEScore(BaseModel):
    feature_id: str
    reach: float
    impact: float
    confidence: float
    effort: float
    score: float


class FeaturePersonaScore(BaseModel):
    feature_id: str
    persona_id: str
    is_relevant: bool
    usage_frequency: Optional[str] = None
    power_level: Optional[str] = None


# Screen + Wireframe models
class WireframeZone(BaseModel):
    type: str  # NAV, HERO, LIST, FORM, CTA, FOOTER
    description: str
    x: int = 0
    y: int = 0
    width: int = 375
    height: int = 80


class CTASpec(BaseModel):
    label: str
    action: str
    loading_label: str = "Loading..."
    success_state: str = "Done"
    error_message: str = "Something went wrong"


class ScreenSpec(BaseModel):
    id: str
    name: str
    accessible_by: list[str]
    purpose: str
    zones: list[WireframeZone] = []
    primary_cta: Optional[CTASpec] = None
    ux_flags: list[str] = []
    empty_state_message: Optional[str] = None
    empty_state_cta: Optional[str] = None
    responsive: dict[str, str] = {}
    svg: Optional[str] = None


class FlowNode(BaseModel):
    id: str
    type: str  # TRIGGER, SCREEN, ACTION, SYSTEM, DECISION, OUTCOME
    label: str
    next_ids: list[str] = []


class UserFlow(BaseModel):
    persona_id: str
    persona_name: str
    nodes: list[FlowNode] = []
    svg: Optional[str] = None


class ComplexityScore(BaseModel):
    tier: Literal["simple", "moderate", "complex"]
    screen_count: int
    feature_count: int
    effort_weeks: str
    scope_reduction_suggestions: list[str] = []


class AppPreview(BaseModel):
    session_id: UUID
    site_map: list[ScreenSpec] = []
    user_flows: list[UserFlow] = []
    complexity: Optional[ComplexityScore] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class NarrativeOutput(BaseModel):
    session_id: UUID
    platform: str
    product_identity: str
    user_stories: str
    edge_cases: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    call2_input_tokens: int = 0
    call2_output_tokens: int = 0


class SessionContext(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    phase: EnrichmentPhase = EnrichmentPhase.IDLE
    fsm_turns: list[FSMTurn] = []
    enriched_context: Optional[EnrichedContext] = None
    app_preview: Optional[AppPreview] = None
    narrative_outputs: dict[str, NarrativeOutput] = {}
    call1_tokens: int = 0
    call2_tokens: dict[str, int] = {}
    total_cost_usd: float = 0.0
    nlp_state: SessionNLPState = Field(default_factory=SessionNLPState)
    user_expertise_signal: float = 0.0
    probe_count_this_phase: int = 0


class FSMResponse(BaseModel):
    question: Optional[str] = None
    quick_replies: list[str] = []
    advance: bool = True
    trigger_extraction: bool = False
    phase: Optional[EnrichmentPhase] = None
    progress_pct: int = 0
    probe: bool = False
