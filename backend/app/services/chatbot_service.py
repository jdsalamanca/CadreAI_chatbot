from app.schemas import ChatMessage
from app.services.llm_service import LLMService

# Temporary placeholder prompt for Phase 0/testing only — no Cadre knowledge is
# wired in yet. This will be replaced with the full system prompt (role,
# knowledge boundary, escalation, injection resistance) in Phase 4.
SYSTEM_PROMPT = (
    "You are a helpful, friendly assistant for Cadre AI, a company that helps "
    "businesses adopt AI. You are currently running in a test/development mode "
    "without access to Cadre's knowledge base, so avoid stating specific facts "
    "about Cadre AI's services, clients, or pricing. Keep responses concise."
)


class ChatbotService:
    def __init__(self, llm_service: LLMService) -> None:
        self._llm_service = llm_service

    async def get_reply(self, message: str, history: list[ChatMessage]) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend({"role": turn.role, "content": turn.content} for turn in history)
        messages.append({"role": "user", "content": message})
        return await self._llm_service.generate_reply(messages)
