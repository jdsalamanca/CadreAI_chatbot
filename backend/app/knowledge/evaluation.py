from dataclasses import dataclass

from app.knowledge.retriever import KnowledgeRetriever

# Each case is a realistic user question plus the knowledge item ID(s) that
# should count as a "hit" if any of them appear in the top-k results.
# plan.md Phase 4: "Create a small evaluation set covering: Question -> Expected
# knowledge item(s)". Covers every category in cadre_knowledge_base.json.
EVAL_CASES: list[tuple[str, tuple[str, ...]]] = [
    ("What does Cadre AI do?", ("company_overview", "core_services")),
    ("What services does Cadre offer?", ("core_services",)),
    (
        "Does Cadre build custom software or just recommend existing tools?",
        ("workflow_automation_and_custom_solutions",),
    ),
    ("How do I get started working with Cadre?", ("getting_started", "ai_transformation_intensive")),
    (
        "What happens during the AI Transformation Intensive?",
        ("ai_transformation_process", "ai_transformation_intensive"),
    ),
    ("How much does Cadre charge for its services?", ("service_pricing",)),
    ("What is the AI Maturity Index?", ("ai_maturity_index_overview",)),
    ("What are the eight pillars Cadre evaluates?", ("ai_maturity_index_pillars",)),
    ("How exactly is my AI Maturity score calculated?", ("ai_maturity_index_scoring_gap",)),
    ("How do I book a strategy call?", ("strategy_call",)),
    ("What industries does Cadre work with?", ("industries",)),
    ("Does Cadre work with construction companies?", ("industry_construction",)),
    ("Can Cadre help a real estate business?", ("industry_real_estate",)),
    ("Do you work with financial services companies?", ("industry_financial_services",)),
    ("Do you only work with the industries listed on your site?", ("industry_outside_list",)),
    ("How do I log into the Cadre client portal?", ("client_portal_access_gap", "client_portal")),
    ("What can I do in the Cadre client portal?", ("client_portal",)),
    ("What LLMs does Cadre use?", ("llm_selection",)),
    ("How does Cadre decide which AI model to use for a project?", ("llm_selection",)),
    ("How does Cadre protect our company data?", ("data_security",)),
    ("Is Cadre SOC 2 compliant?", ("data_security",)),
    ("Do you have a manufacturing case study?", ("case_study_manufacturing",)),
    (
        "What results have you achieved for professional services clients?",
        ("case_study_professional_services",),
    ),
    ("Tell me about a hospitality client success story.", ("case_study_hospitality",)),
    ("Do you have any mortgage or lending case studies?", ("case_study_mortgage",)),
    ("What technology partners does Cadre work with?", ("cadre_partners",)),
    ("Why is clean data important before implementing AI?", ("ai_healthy_data",)),
]

# Deliberately unrelated to Cadre — used to observe what similarity scores
# look like for queries with no relevant knowledge, to help pick
# RETRIEVAL_SIMILARITY_THRESHOLD. Not scored against EVAL_CASES.
OFF_TOPIC_QUERIES = [
    "What's the weather like today?",
    "Can you write me a haiku about the ocean?",
    "What's the capital of France?",
]


@dataclass
class CaseResult:
    question: str
    expected_ids: tuple[str, ...]
    retrieved_ids: list[str]
    top_score: float
    hit: bool


@dataclass
class EvaluationResult:
    cases: list[CaseResult]

    @property
    def hit_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for case in self.cases if case.hit) / len(self.cases)


def evaluate(retriever: KnowledgeRetriever, top_k: int) -> EvaluationResult:
    results = []
    for question, expected_ids in EVAL_CASES:
        retrieved = retriever.retrieve(question, top_k=top_k)
        retrieved_ids = [r.item.id for r in retrieved]
        hit = any(item_id in retrieved_ids for item_id in expected_ids)
        top_score = retrieved[0].score if retrieved else 0.0
        results.append(CaseResult(question, expected_ids, retrieved_ids, top_score, hit))
    return EvaluationResult(results)
