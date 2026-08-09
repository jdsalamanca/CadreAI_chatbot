import logging
from dataclasses import dataclass
from typing import Any

from app.knowledge.models import EscalationInfo
from app.knowledge.retriever import KnowledgeRetriever, RetrievedItem

logger = logging.getLogger(__name__)


class KnowledgeRetrievalError(Exception):
    """Raised when embedding/FAISS search itself fails (not when it simply
    finds nothing relevant — that's PolicyResult.has_relevant_knowledge=False).
    """


@dataclass
class PolicyResult:
    relevant_items: list[RetrievedItem]
    has_relevant_knowledge: bool
    escalation_required: bool
    escalation_info: EscalationInfo


class KnowledgePolicy:
    """The policy layer between retrieval and LLM generation (plan.md Phase 5):

        retrieve -> filter by relevance (similarity threshold) -> inspect
        status -> inspect escalation_required -> construct response context

    This is where "the model must not guess" gets enforced structurally: items
    that don't clear the similarity threshold are never handed to the LLM as
    knowledge, and items that are explicitly `not_publicly_available` are
    always paired with their escalation guidance.
    """

    def __init__(self, retriever: KnowledgeRetriever, similarity_threshold: float, top_k: int) -> None:
        self._retriever = retriever
        self._similarity_threshold = similarity_threshold
        self._top_k = top_k

    def evaluate(self, query: str) -> PolicyResult:
        try:
            results = self._retriever.retrieve(query, top_k=self._top_k)
        except Exception as exc:
            logger.exception("Knowledge retrieval failed for query")
            raise KnowledgeRetrievalError("Unable to retrieve Cadre knowledge right now.") from exc

        relevant = [r for r in results if r.score >= self._similarity_threshold]
        escalation_required = any(r.item.escalation_required for r in relevant)

        return PolicyResult(
            relevant_items=relevant,
            has_relevant_knowledge=bool(relevant),
            escalation_required=escalation_required,
            escalation_info=self._retriever.get_escalation_info(),
        )


def render_content(content: Any, indent: int = 0) -> str:
    prefix = "  " * indent
    if isinstance(content, str):
        return f"{prefix}{content}"
    if isinstance(content, list):
        return "\n".join(f"{prefix}- {render_content(entry, 0)}" for entry in content)
    if isinstance(content, dict):
        return "\n".join(
            f"{prefix}{key}: "
            f"{render_content(value, indent + 1) if isinstance(value, (dict, list)) else value}"
            for key, value in content.items()
        )
    return f"{prefix}{content}"


def _contact_block(escalation_info: EscalationInfo) -> str:
    return (
        "Cadre contact/escalation options (use only when appropriate; never invent alternatives):\n"
        f"- Email: {escalation_info.email}\n"
        f"- Phone: {escalation_info.phone}\n"
        f"- Contact page: {escalation_info.contact_page}\n"
        f'- CTA: "{escalation_info.strategy_cta}"'
    )


def format_context_block(policy_result: PolicyResult) -> str:
    """Renders a PolicyResult into the text handed to the LLM as a system
    message alongside the static system prompt. Keeps `content` (authoritative
    facts) separate from status/escalation metadata, per CLAUDE.md.
    """
    contact_block = _contact_block(policy_result.escalation_info)

    if not policy_result.has_relevant_knowledge:
        return (
            "No verified Cadre-specific knowledge matched this question above the retrieval "
            "confidence threshold. Do not answer using general knowledge as though it were a "
            "documented Cadre fact. If the question appears to be about Cadre AI, acknowledge the "
            "limitation and offer to connect the user with a Cadre AI strategist using the contact "
            "info below. If the question is unrelated to Cadre AI, respond naturally and briefly "
            "redirect toward what you can help with instead of forcing contact info into an "
            "unrelated conversation.\n\n" + contact_block
        )

    sections = []
    for rank, retrieved in enumerate(policy_result.relevant_items, start=1):
        item = retrieved.item
        if item.status == "not_publicly_available":
            status_line = "Status: NOT PUBLICLY AVAILABLE — do not guess or invent details"
            escalation_line = (
                f"Escalation guidance: {item.escalation_reason}\n" if item.escalation_reason else ""
            )
        else:
            status_line = "Status: VERIFIED"
            escalation_line = ""

        sections.append(
            f"{rank}. Topic: {item.topic} | Category: {item.category}\n"
            f"{status_line}\n"
            f"{escalation_line}"
            f"Source: {item.source}\n"
            f"Information: {render_content(item.content)}"
        )

    return (
        "Relevant Cadre knowledge retrieved for this question:\n\n"
        + "\n\n".join(sections)
        + "\n\n"
        + contact_block
    )
