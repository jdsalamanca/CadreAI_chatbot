from app.knowledge.policy import KnowledgePolicy, format_context_block
from app.schemas import ChatMessage
from app.services.llm_service import LLMService
from app.services.prompts import SYSTEM_PROMPT


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

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": context_block},
        ]
        messages.extend({"role": turn.role, "content": turn.content} for turn in history)
        messages.append({"role": "user", "content": message})

        return await self._llm_service.generate_reply(messages)
