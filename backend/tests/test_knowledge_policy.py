import pytest

from app.knowledge.models import EscalationInfo, KnowledgeItem
from app.knowledge.policy import KnowledgePolicy, KnowledgeRetrievalError, format_context_block
from app.knowledge.retriever import RetrievedItem

ESCALATION_INFO = EscalationInfo(
    email="hello@gocadre.ai",
    phone="(619) 324-3223",
    contact_page="https://www.cadreai.com/contact",
    strategy_cta="Talk to an AI Strategist",
)


def make_item(item_id: str, status: str = "verified", escalation_required: bool = False, **overrides):
    defaults = {
        "id": item_id,
        "category": "test",
        "topic": item_id,
        "retrieval_text": item_id,
        "content": f"Content for {item_id}",
        "status": status,
        "source": "https://example.com",
        "source_type": "test_fixture",
        "escalation_required": escalation_required,
    }
    defaults.update(overrides)
    return KnowledgeItem(**defaults)


class FakeRetriever:
    def __init__(self, hits: list[RetrievedItem]) -> None:
        self._hits = hits
        self.last_query = None
        self.last_top_k = None

    def retrieve(self, query: str, top_k: int) -> list[RetrievedItem]:
        self.last_query = query
        self.last_top_k = top_k
        return self._hits

    def get_escalation_info(self) -> EscalationInfo:
        return ESCALATION_INFO


class ExplodingRetriever:
    def retrieve(self, query: str, top_k: int):
        raise RuntimeError("embedding backend is down")

    def get_escalation_info(self) -> EscalationInfo:
        return ESCALATION_INFO


def test_verified_item_above_threshold_is_kept():
    item = make_item("company_overview")
    retriever = FakeRetriever([RetrievedItem(item=item, score=0.9)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)

    result = policy.evaluate("what does cadre do")

    assert result.has_relevant_knowledge is True
    assert result.escalation_required is False
    assert [r.item.id for r in result.relevant_items] == ["company_overview"]


def test_items_below_threshold_are_filtered_out():
    item = make_item("weak_match")
    retriever = FakeRetriever([RetrievedItem(item=item, score=0.2)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)

    result = policy.evaluate("something unrelated")

    assert result.has_relevant_knowledge is False
    assert result.relevant_items == []


def test_gap_item_sets_escalation_required():
    gap_item = make_item(
        "service_pricing",
        status="not_publicly_available",
        escalation_required=True,
        escalation_reason="Direct the user to an AI strategist.",
    )
    retriever = FakeRetriever([RetrievedItem(item=gap_item, score=0.8)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)

    result = policy.evaluate("how much does cadre cost")

    assert result.has_relevant_knowledge is True
    assert result.escalation_required is True


def test_mixed_results_escalation_required_if_any_item_requires_it():
    verified = make_item("company_overview")
    gap = make_item("service_pricing", status="not_publicly_available", escalation_required=True)
    retriever = FakeRetriever([RetrievedItem(item=verified, score=0.8), RetrievedItem(item=gap, score=0.7)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)

    result = policy.evaluate("tell me about cadre and pricing")

    assert result.escalation_required is True
    assert len(result.relevant_items) == 2


def test_retrieval_failure_raises_knowledge_retrieval_error():
    policy = KnowledgePolicy(ExplodingRetriever(), similarity_threshold=0.5, top_k=3)

    with pytest.raises(KnowledgeRetrievalError):
        policy.evaluate("anything")


# --- format_context_block ---


def test_context_block_for_no_relevant_knowledge_does_not_assert_facts():
    retriever = FakeRetriever([])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)
    result = policy.evaluate("anything")

    block = format_context_block(result)

    assert "No verified Cadre-specific knowledge matched" in block
    assert "hello@gocadre.ai" in block


def test_context_block_flags_gap_items_as_not_publicly_available():
    gap_item = make_item(
        "service_pricing",
        status="not_publicly_available",
        escalation_required=True,
        escalation_reason="Direct the user to an AI strategist.",
    )
    retriever = FakeRetriever([RetrievedItem(item=gap_item, score=0.8)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)
    result = policy.evaluate("how much does cadre cost")

    block = format_context_block(result)

    assert "NOT PUBLICLY AVAILABLE" in block
    assert "Direct the user to an AI strategist." in block
    assert "hello@gocadre.ai" in block


def test_context_block_includes_verified_content():
    item = make_item("company_overview", content="Cadre AI is an AI strategy partner.")
    retriever = FakeRetriever([RetrievedItem(item=item, score=0.9)])
    policy = KnowledgePolicy(retriever, similarity_threshold=0.5, top_k=3)
    result = policy.evaluate("what does cadre do")

    block = format_context_block(result)

    assert "Status: VERIFIED" in block
    assert "Cadre AI is an AI strategy partner." in block
