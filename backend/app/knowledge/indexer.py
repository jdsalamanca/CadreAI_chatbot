from dataclasses import dataclass

import faiss
import numpy as np
from fastembed import TextEmbedding

from app.knowledge.models import KnowledgeItem

# fastembed (ONNX-based) rather than sentence-transformers (torch-based): a
# fraction of the install/image size and cold-start cost for a single small
# CPU-only container, at the cost of a smaller model selection. See
# ARCHITECTURE.md for the full trade-off.
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


class EmbeddingModel:
    """Wraps the embedding backend so it can be swapped (env-configurable, per
    plan.md Phase 3) without touching indexing or retrieval logic.
    """

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        self._model = TextEmbedding(model_name=model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.array(list(self._model.embed(texts)), dtype="float32")
        faiss.normalize_L2(vectors)
        return vectors

    def embed_query(self, text: str) -> np.ndarray:
        return self.embed([text])


@dataclass
class KnowledgeIndex:
    """A FAISS index over knowledge items' `retrieval_text`, plus the position
    -> knowledge item ID mapping needed to translate a FAISS hit back into a
    real knowledge item.

    This is a derived artifact, never the source of truth: nothing here is
    persisted, and `build_index` recomputes it from the repository's items
    every time it's called (plan.md Phase 3 — "the index should be
    rebuildable from the JSON").
    """

    index: faiss.IndexFlatIP
    id_by_position: list[str]

    def search(self, query_vector: np.ndarray, top_k: int) -> list[tuple[str, float]]:
        if self.index.ntotal == 0:
            return []

        scores, positions = self.index.search(query_vector, min(top_k, self.index.ntotal))
        hits = []
        for score, position in zip(scores[0], positions[0]):
            if position == -1:
                continue
            hits.append((self.id_by_position[position], float(score)))
        return hits


def build_index(items: list[KnowledgeItem], embedding_model: EmbeddingModel) -> KnowledgeIndex:
    """Implements the Phase 3 indexing pipeline:

        knowledge item -> retrieval_text -> embedding model -> vector -> FAISS

    Embeddings are computed from `retrieval_text` only (never the full JSON
    object or `content`) and are never written back into the JSON — they
    exist only in this in-memory index.
    """
    if not items:
        return KnowledgeIndex(index=faiss.IndexFlatIP(1), id_by_position=[])

    vectors = embedding_model.embed([item.retrieval_text for item in items])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return KnowledgeIndex(index=index, id_by_position=[item.id for item in items])
