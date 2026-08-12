import logging

from app.knowledge.policy import KnowledgePolicy, format_context_block
from app.schemas import ChatMessage
from app.services.llm_service import LLMService, LLMTimeoutError, LLMUnavailableError
from app.services.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatbotService:
    """Conversation orchestration: retrieve+apply knowledge policy for the
    current question, then call the LLM with the static system prompt plus
    the per-query knowledge context (plan.md Phase 5/6).
    """

    def __init__(self, llm_service: LLMService, knowledge_policy: KnowledgePolicy) -> None:
        self._llm_service = llm_service
        self._knowledge_policy = knowledge_policy

    async def get_reply(self, message: str, history: list[ChatMessage]) -> str:
        policy_result = self._knowledge_policy.evaluate(message)
        context_block = format_context_block(policy_result)
        messages = self._build_messages(message, history, context_block)

        if self._should_use_web_search(message, policy_result):
            try:
                return await self._llm_service.generate_reply_with_web_search(messages)
            except (LLMTimeoutError, LLMUnavailableError):
                logger.exception("OpenAI web search fallback failed; using standard response path")

        return await self._llm_service.generate_reply(messages)

    @staticmethod
    def _build_messages(message: str, history: list[ChatMessage], context_block: str) -> list[dict]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context_block},
        ]
        messages.extend({"role": turn.role, "content": turn.content} for turn in history)
        messages.append({"role": "user", "content": message})
        return messages

    @staticmethod
    def _should_use_web_search(message: str, policy_result) -> bool:
        if policy_result.has_relevant_knowledge and all(
            retrieved.item.status == "verified" for retrieved in policy_result.relevant_items
        ):
            return False

        if policy_result.relevant_items:
            return True

        normalized = message.strip().lower()
        casual_starts = ("hi", "hello", "hey", "thanks", "thank you", "good morning", "good afternoon", "good evening")
        if normalized in casual_starts or any(normalized.startswith(prefix + " ") for prefix in casual_starts):
            return False

        cadre_terms = (
            "cadre",
            "cadre ai",
            "ai maturity index",
            "client portal",
            "case study",
            "pricing",
            "security",
            "llm",
            "strategy",
        )
        if not any(term in normalized for term in cadre_terms):
            return False

        if "?" in normalized:
            return True

        factual_keywords = (
            "what",
            "when",
            "where",
            "who",
            "why",
            "how",
            "latest",
            "current",
            "today",
            "price",
            "pricing",
            "cost",
            "update",
            "news",
            "verify",
            "verified",
        )
        return any(keyword in normalized for keyword in factual_keywords)
