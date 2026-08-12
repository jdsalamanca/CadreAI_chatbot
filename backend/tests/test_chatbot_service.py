import asyncio

from app.knowledge.models import EscalationInfo, KnowledgeItem
from app.knowledge.policy import PolicyResult
from app.knowledge.retriever import RetrievedItem
from app.schemas import ChatMessage
from app.services.chatbot_service import ChatbotService
from app.services.prompts import SYSTEM_PROMPT

ESCALATION_INFO = EscalationInfo(
    email="hello@gocadre.ai",
    phone="(619) 324-3223",
    contact_page="https://www.cadreai.com/contact",
    strategy_cta="Talk to an AI Strategist",
)


class FakePolicy:
    def __init__(self, result: PolicyResult) -> None:
        self._result = result
        self.last_query = None

    def evaluate(self, query: str) -> PolicyResult:
        self.last_query = query
        return self._result


class FakeLLM:
    def __init__(self, reply: str = "hi there") -> None:
        self.reply = reply
        self.last_messages = None
        self.web_search_messages = None

    async def generate_reply(self, messages: list[dict]) -> str:
        self.last_messages = messages
        return self.reply

    async def generate_reply_with_web_search(self, messages: list[dict]) -> str:
        self.web_search_messages = messages
        return self.reply


def make_relevant_policy_result() -> PolicyResult:
    item = KnowledgeItem(
        id="company_overview",
        category="company",
        topic="What Cadre AI does",
        retrieval_text="...",
        content="Cadre AI is an AI strategy partner.",
        status="verified",
        source="https://www.cadreai.com/",
        source_type="official_website",
    )
    return PolicyResult(
        relevant_items=[RetrievedItem(item=item, score=0.9)],
        has_relevant_knowledge=True,
        escalation_required=False,
        escalation_info=ESCALATION_INFO,
    )


def make_no_knowledge_policy_result() -> PolicyResult:
    return PolicyResult(
        relevant_items=[],
        has_relevant_knowledge=False,
        escalation_required=False,
        escalation_info=ESCALATION_INFO,
    )


def test_get_reply_sends_system_prompt_context_history_and_message_in_order():
    policy = FakePolicy(make_relevant_policy_result())
    llm = FakeLLM(reply="hello!")
    service = ChatbotService(llm, policy)

    history = [
        ChatMessage(role="user", content="hi"),
        ChatMessage(role="assistant", content="hello"),
    ]

    reply = asyncio.run(service.get_reply("What does Cadre do?", history))

    assert reply == "hello!"
    assert policy.last_query == "What does Cadre do?"

    messages = llm.last_messages
    assert messages[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert "Cadre AI is an AI strategy partner." in messages[1]["content"]
    assert messages[2] == {"role": "user", "content": "hi"}
    assert messages[3] == {"role": "assistant", "content": "hello"}
    assert messages[4] == {"role": "user", "content": "What does Cadre do?"}


def test_get_reply_uses_fallback_context_when_no_relevant_knowledge():
    policy = FakePolicy(make_no_knowledge_policy_result())
    llm = FakeLLM()
    service = ChatbotService(llm, policy)

    asyncio.run(service.get_reply("What's the weather like?", []))

    context_message = llm.last_messages[1]["content"]
    assert "No verified Cadre-specific knowledge" in context_message


def test_get_reply_uses_web_search_when_knowledge_is_unverified():
    item = KnowledgeItem(
        id="secret_pricing",
        category="pricing",
        topic="Pricing details",
        retrieval_text="...",
        content="Pricing is handled privately.",
        status="not_publicly_available",
        source="https://www.cadreai.com/",
        source_type="official_website",
        escalation_required=True,
        escalation_reason="Pricing is not public.",
    )
    policy = FakePolicy(
        PolicyResult(
            relevant_items=[RetrievedItem(item=item, score=0.93)],
            has_relevant_knowledge=True,
            escalation_required=True,
            escalation_info=ESCALATION_INFO,
        )
    )
    llm = FakeLLM(reply="use search")
    service = ChatbotService(llm, policy)

    asyncio.run(service.get_reply("What does Cadre charge?", []))

    assert llm.web_search_messages is not None
    assert llm.last_messages is None
    assert "Pricing details" in llm.web_search_messages[1]["content"]


def test_get_reply_does_not_use_web_search_when_verified_rag_answer_exists():
    policy = FakePolicy(make_relevant_policy_result())
    llm = FakeLLM(reply="grounded answer")
    service = ChatbotService(llm, policy)

    asyncio.run(service.get_reply("What does Cadre do?", []))

    assert llm.web_search_messages is None
    assert llm.last_messages is not None
