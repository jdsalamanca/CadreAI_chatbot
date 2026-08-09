from typing import Any

from pydantic import BaseModel

# Statuses the chatbot is allowed to surface as knowledge. "verified" items are
# presented as fact; "not_publicly_available" items are presented as explicit
# boundaries (things the bot must not guess about). Any other status (e.g. a
# future "draft" or "unverified" item) is excluded by KnowledgeRepository before
# it ever reaches the LLM or the retriever.
USABLE_STATUSES = {"verified", "not_publicly_available"}


class KnowledgeItem(BaseModel):
    id: str
    category: str
    topic: str
    retrieval_text: str
    content: Any
    status: str
    source: str
    source_type: str
    escalation_required: bool = False
    escalation_reason: str | None = None
    last_verified: str | None = None
    contact: dict[str, Any] | None = None
    partners: list[str] | None = None
    limitations: list[str] | None = None


class EscalationInfo(BaseModel):
    email: str
    phone: str
    contact_page: str
    strategy_cta: str
    recommended_for: list[str] = []


class KnowledgeBase(BaseModel):
    metadata: dict[str, Any]
    knowledge: list[KnowledgeItem]
    response_policy: dict[str, Any]
    escalation: EscalationInfo
