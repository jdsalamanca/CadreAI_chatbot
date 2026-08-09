import json
import logging
from pathlib import Path
from typing import Any

from app.knowledge.models import USABLE_STATUSES, EscalationInfo, KnowledgeBase, KnowledgeItem

logger = logging.getLogger(__name__)

DEFAULT_DATA_PATH = Path(__file__).resolve().parent / "data" / "cadre_knowledge_base.json"


class KnowledgeRepository:
    """Loads and validates cadre_knowledge_base.json.

    This is the sole source of truth for Cadre knowledge (plan.md Phase 2).
    It performs no retrieval — see KnowledgeRetriever for the FAISS-backed
    semantic search built on top of this repository (Phase 3).
    """

    def __init__(self, data_path: Path | None = None) -> None:
        path = data_path or DEFAULT_DATA_PATH
        raw: dict[str, Any] = json.loads(path.read_text())
        knowledge_base = KnowledgeBase.model_validate(raw)

        usable, skipped = [], []
        for item in knowledge_base.knowledge:
            (usable if self._is_usable(item) else skipped).append(item)
        if skipped:
            logger.warning(
                "Excluding %d knowledge item(s) with unsupported status from the "
                "corpus (ids: %s)",
                len(skipped),
                ", ".join(item.id for item in skipped),
            )

        self._items_by_id: dict[str, KnowledgeItem] = {item.id: item for item in usable}
        self._escalation: EscalationInfo = knowledge_base.escalation

    @staticmethod
    def _is_usable(item: KnowledgeItem) -> bool:
        return item.status in USABLE_STATUSES

    def get_all(self) -> list[KnowledgeItem]:
        return list(self._items_by_id.values())

    def get_by_id(self, item_id: str) -> KnowledgeItem | None:
        return self._items_by_id.get(item_id)

    def get_escalation_info(self) -> EscalationInfo:
        return self._escalation
