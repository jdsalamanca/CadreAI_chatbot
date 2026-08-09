"""Phase 4 (plan.md) — retrieval evaluation as an automated regression test.

Parameter tuning itself was done interactively via
backend/scripts/evaluate_retrieval.py (see ARCHITECTURE.md for the results:
top_k=3 started at 85.2%, retrieval_text tuning for two weak items plus
raising top_k to 5 reached 100% on the eval set, with a clear score gap
between genuine matches (>=0.59) and off-topic queries (<=0.48)). This test
locks that behavior in so a future corpus/model change that regresses
retrieval quality fails loudly.
"""

from app.config import settings
from app.knowledge.evaluation import OFF_TOPIC_QUERIES, evaluate
from app.knowledge.repository import KnowledgeRepository
from app.knowledge.retriever import KnowledgeRetriever

MIN_ACCEPTABLE_HIT_RATE = 0.9


def build_real_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(repository=KnowledgeRepository())


def test_hit_rate_at_configured_top_k_meets_bar():
    retriever = build_real_retriever()

    result = evaluate(retriever, top_k=settings.retrieval_top_k)

    misses = [case.question for case in result.cases if not case.hit]
    assert result.hit_rate >= MIN_ACCEPTABLE_HIT_RATE, f"Missed: {misses}"


def test_off_topic_queries_score_below_the_similarity_threshold():
    retriever = build_real_retriever()

    for query in OFF_TOPIC_QUERIES:
        results = retriever.retrieve(query, top_k=1)
        top_score = results[0].score if results else 0.0
        assert top_score < settings.retrieval_similarity_threshold, (
            f"Off-topic query scored above threshold: '{query}' -> {top_score:.3f}"
        )


def test_relevant_queries_score_above_the_similarity_threshold():
    retriever = build_real_retriever()

    result = evaluate(retriever, top_k=1)

    below_threshold = [
        (case.question, case.top_score)
        for case in result.cases
        if case.top_score < settings.retrieval_similarity_threshold
    ]
    assert not below_threshold, f"Relevant queries scored below threshold: {below_threshold}"
