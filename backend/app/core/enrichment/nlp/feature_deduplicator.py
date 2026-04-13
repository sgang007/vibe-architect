import asyncio
from dataclasses import dataclass
from app.config import settings


@dataclass
class DeduplicationResult:
    unique: list[str]
    merged_pairs: list[tuple[str, str]]


class FeatureDeduplicator:
    def __init__(self):
        self._model = None

    def _load(self):
        if self._model is not None:
            return
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(
            settings.NLP_SIMILARITY_MODEL,
            cache_folder=settings.MODEL_CACHE_DIR,
        )

    async def deduplicate(self, raw_features: list[str]) -> DeduplicationResult:
        if len(raw_features) <= 1:
            return DeduplicationResult(unique=raw_features, merged_pairs=[])

        self._load()
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self._model.encode, raw_features)

        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(embeddings)
        threshold = settings.NLP_DEDUP_SIMILARITY_THRESHOLD

        merged_pairs = []
        to_remove = set()
        for i in range(len(raw_features)):
            if i in to_remove:
                continue
            for j in range(i + 1, len(raw_features)):
                if j in to_remove:
                    continue
                if sim_matrix[i][j] > threshold:
                    keep = i if len(raw_features[i]) >= len(raw_features[j]) else j
                    drop = j if keep == i else i
                    merged_pairs.append((raw_features[keep], raw_features[drop]))
                    to_remove.add(drop)

        unique = [f for i, f in enumerate(raw_features) if i not in to_remove]
        return DeduplicationResult(unique=unique, merged_pairs=merged_pairs)

    @property
    def loaded(self) -> bool:
        return self._model is not None
