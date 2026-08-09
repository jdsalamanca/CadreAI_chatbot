from dataclasses import dataclass

from app.knowledge.indexer import EmbeddingModel, build_index
from app.knowledge.models import EscalationInfo, KnowledgeItem
from app.knowledge.repository import KnowledgeRepository

DEFAULT_TOP_K = 3


@dataclass
class RetrievedItem:
    item: KnowledgeItem
    score: float


class KnowledgeRetriever:
    """Ties the knowledge repository to a FAISS semantic index (plan.md
    Phase 3):

        query -> embed -> FAISS search -> knowledge item IDs -> repository
        lookup -> ranked KnowledgeItems

    The index is built once, at construction, from whatever the repository
    currently holds — rebuilding it just means constructing a new
    KnowledgeRetriever.
    """

    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
        embedding_model: EmbeddingModel | None = None,
    ) -> None:
        self._repository = repository or KnowledgeRepository()
        self._embedding_model = embedding_model or EmbeddingModel()
        self._index = build_index(self._repository.get_all(), self._embedding_model)

    def retrieve(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[RetrievedItem]:
        query_vector = self._embedding_model.embed_query(query)
        hits = self._index.search(query_vector, top_k)

        results = []
        for item_id, score in hits:
            item = self._repository.get_by_id(item_id)
            if item is not None:
                results.append(RetrievedItem(item=item, score=score))
        return results

    def get_escalation_info(self) -> EscalationInfo:
        return self._repository.get_escalation_info()
