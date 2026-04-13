import asyncio
from collections import defaultdict
from app.models import EntityCache, SessionContext

ROLE_TERMS = {
    "admin", "owner", "manager", "vendor", "driver", "agent", "operator",
    "customer", "client", "user", "member", "staff", "employee", "guest",
    "buyer", "seller", "host", "tenant", "provider", "consumer"
}


class EntityExtractor:
    def __init__(self):
        self._nlp = None

    def _load(self):
        if self._nlp is not None:
            return
        import spacy
        self._nlp = spacy.load("en_core_web_sm")
        ruler = self._nlp.add_pipe("entity_ruler", before="ner")
        ruler.add_patterns([
            {"label": "ROLE", "pattern": term} for term in ROLE_TERMS
        ])

    async def extract(self, answer: str, session: SessionContext) -> EntityCache:
        self._load()
        loop = asyncio.get_event_loop()
        doc = await loop.run_in_executor(None, self._nlp, answer)
        new_entities: dict[str, set] = defaultdict(set)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                new_entities["persona_candidates"].add(ent.text)
            elif ent.label_ in ("ORG", "PRODUCT"):
                new_entities["tool_names"].add(ent.text)
            elif ent.label_ in ("GPE", "LOC"):
                new_entities["geographies"].add(ent.text)
            elif ent.label_ == "MONEY":
                new_entities["payment_signals"].add(ent.text)
            elif ent.label_ == "CARDINAL":
                new_entities["scale_signals"].add(ent.text)
            elif ent.label_ == "ROLE":
                new_entities["role_terms"].add(ent.text.lower())

        session.nlp_state.entity_cache.merge(dict(new_entities))
        return session.nlp_state.entity_cache

    @property
    def loaded(self) -> bool:
        return self._nlp is not None
