#!/usr/bin/env python3
"""Manual retrieval-evaluation harness (plan.md Phase 4).

Run from the backend/ directory:

    ../.venv/bin/python scripts/evaluate_retrieval.py [top_k]

Prints a per-question hit/miss table plus the score distribution for both
correctly-retrieved and off-topic queries, to help tune EMBEDDING_MODEL,
RETRIEVAL_TOP_K, and RETRIEVAL_SIMILARITY_THRESHOLD (see app/config.py).
"""

import sys

from app.knowledge.evaluation import OFF_TOPIC_QUERIES, evaluate
from app.knowledge.retriever import KnowledgeRetriever


def main() -> None:
    top_k = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    retriever = KnowledgeRetriever()

    result = evaluate(retriever, top_k=top_k)

    for case in result.cases:
        marker = "HIT " if case.hit else "MISS"
        print(f"[{marker}] top_score={case.top_score:.3f}  '{case.question}'")
        print(f"       expected={list(case.expected_ids)} got={case.retrieved_ids}")

    hits = sum(1 for case in result.cases if case.hit)
    print()
    print(f"Hit rate @ top_{top_k}: {result.hit_rate:.1%} ({hits}/{len(result.cases)})")

    hit_scores = [case.top_score for case in result.cases if case.hit]
    miss_scores = [case.top_score for case in result.cases if not case.hit]
    if hit_scores:
        print(f"Top-score range on hits:   min={min(hit_scores):.3f}  max={max(hit_scores):.3f}")
    if miss_scores:
        print(f"Top-score range on misses: min={min(miss_scores):.3f}  max={max(miss_scores):.3f}")

    print()
    print("Off-topic queries (no relevant knowledge expected):")
    for query in OFF_TOPIC_QUERIES:
        retrieved = retriever.retrieve(query, top_k=top_k)
        top_score = retrieved[0].score if retrieved else 0.0
        top_id = retrieved[0].item.id if retrieved else None
        print(f"  top_score={top_score:.3f}  top_id={top_id}  '{query}'")


if __name__ == "__main__":
    main()
