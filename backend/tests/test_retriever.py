from app.knowledge.models import KnowledgeItem
from app.knowledge.repository import KnowledgeRepository
from app.knowledge.retriever import KnowledgeRetriever


def make_item(item_id: str, retrieval_text: str, content: str) -> KnowledgeItem:
    return KnowledgeItem(
        id=item_id,
        category="test",
        topic=item_id,
        retrieval_text=retrieval_text,
        content=content,
        status="verified",
        source="https://example.com",
        source_type="test_fixture",
    )


class FakeRepository:
    """A minimal stand-in for KnowledgeRepository so retriever tests don't
    depend on the real corpus's exact wording — only on whether semantically
    distinct items get ranked correctly.
    """

    def __init__(self, items: list[KnowledgeItem]) -> None:
        self._items_by_id = {item.id: item for item in items}

    def get_all(self) -> list[KnowledgeItem]:
        return list(self._items_by_id.values())

    def get_by_id(self, item_id: str):
        return self._items_by_id.get(item_id)

    def get_escalation_info(self):
        return None


FIXTURE_ITEMS = [
    make_item(
        "refund_policy",
        "Our refund policy allows returns within 30 days of purchase for a full refund.",
        "Refunds are available within 30 days.",
    ),
    make_item(
        "office_hours",
        "Our office is open Monday through Friday, 9am to 5pm Pacific time.",
        "Office hours are 9-5 Pacific, weekdays.",
    ),
    make_item(
        "onboarding_steps",
        "New customers are onboarded through a kickoff call, a data audit, and a rollout plan.",
        "Onboarding: kickoff call, data audit, rollout plan.",
    ),
]


def build_test_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(repository=FakeRepository(FIXTURE_ITEMS))


# --- Semantic ranking behavior (fixtures, deterministic across corpus edits) ---


def test_retrieve_ranks_the_semantically_closest_item_first():
    retriever = build_test_retriever()

    results = retriever.retrieve("Can I get my money back if I don't like the product?", top_k=3)

    assert results[0].item.id == "refund_policy"


def test_retrieve_respects_top_k():
    retriever = build_test_retriever()

    results = retriever.retrieve("Tell me anything", top_k=1)

    assert len(results) == 1


def test_retrieve_scores_are_within_cosine_similarity_range():
    retriever = build_test_retriever()

    results = retriever.retrieve("What time does the office open?", top_k=3)

    assert all(-1.0 <= r.score <= 1.0 for r in results)
    assert results[0].item.id == "office_hours"


def test_retrieve_returns_empty_list_for_empty_corpus():
    retriever = KnowledgeRetriever(repository=FakeRepository([]))

    assert retriever.retrieve("anything", top_k=3) == []


# --- Behavior against the real bundled corpus ---


def test_retrieve_against_real_corpus_finds_pricing_gap_item():
    retriever = KnowledgeRetriever(repository=KnowledgeRepository())

    results = retriever.retrieve("How much does Cadre charge for its services?", top_k=3)

    assert any(r.item.id == "service_pricing" for r in results)


def test_retrieve_against_real_corpus_finds_ai_maturity_index():
    retriever = KnowledgeRetriever(repository=KnowledgeRepository())

    results = retriever.retrieve("What is the AI Maturity Index?", top_k=3)

    assert any(r.item.id.startswith("ai_maturity_index") for r in results)
