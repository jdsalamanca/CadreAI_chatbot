import json

import pytest
from pydantic import ValidationError

from app.knowledge.repository import KnowledgeRepository

BASE_KB = {
    "metadata": {"name": "Test KB", "version": "0.0.1"},
    "response_policy": {},
    "escalation": {
        "email": "hello@gocadre.ai",
        "phone": "(619) 324-3223",
        "contact_page": "https://www.cadreai.com/contact",
        "strategy_cta": "Talk to an AI Strategist",
        "recommended_for": ["Pricing questions"],
    },
}


def make_kb_file(tmp_path, knowledge_items):
    data = {**BASE_KB, "knowledge": knowledge_items}
    path = tmp_path / "kb.json"
    path.write_text(json.dumps(data))
    return path


def verified_item(**overrides):
    item = {
        "id": "sample_verified",
        "category": "company",
        "topic": "Sample verified fact",
        "retrieval_text": "A sample verified fact.",
        "content": "This is a verified fact about Cadre AI.",
        "status": "verified",
        "source": "https://www.cadreai.com/",
        "source_type": "official_website",
        "escalation_required": False,
    }
    item.update(overrides)
    return item


def gap_item(**overrides):
    item = {
        "id": "sample_gap",
        "category": "commercial",
        "topic": "Sample undocumented topic",
        "retrieval_text": "Not publicly documented.",
        "content": "Public information does not cover this.",
        "status": "not_publicly_available",
        "source": "https://www.cadreai.com/",
        "source_type": "official_website_review",
        "escalation_required": True,
        "escalation_reason": "Direct the user to hello@gocadre.ai.",
    }
    item.update(overrides)
    return item


# --- Behavior against the real bundled corpus ---


def test_loads_real_bundled_corpus():
    repository = KnowledgeRepository()
    items = repository.get_all()
    assert len(items) > 20


def test_get_by_id_returns_expected_item():
    repository = KnowledgeRepository()
    item = repository.get_by_id("company_overview")
    assert item is not None
    assert item.source.startswith("https://www.cadreai.com")


def test_get_by_id_returns_none_for_unknown_id():
    repository = KnowledgeRepository()
    assert repository.get_by_id("does_not_exist") is None


def test_real_corpus_escalation_info_is_accessible():
    repository = KnowledgeRepository()
    escalation = repository.get_escalation_info()
    assert escalation.email == "hello@gocadre.ai"
    assert escalation.contact_page.startswith("https://")


# --- Behavior against constructed fixtures ---


def test_verified_and_gap_items_are_both_retained(tmp_path):
    path = make_kb_file(tmp_path, [verified_item(), gap_item()])
    repository = KnowledgeRepository(data_path=path)

    assert repository.get_by_id("sample_verified").status == "verified"
    assert repository.get_by_id("sample_gap").status == "not_publicly_available"


def test_unsupported_status_item_is_excluded(tmp_path):
    path = make_kb_file(
        tmp_path,
        [
            verified_item(id="keep_me"),
            verified_item(id="drop_me", status="draft"),
        ],
    )
    repository = KnowledgeRepository(data_path=path)

    assert repository.get_by_id("keep_me") is not None
    assert repository.get_by_id("drop_me") is None
    assert [item.id for item in repository.get_all()] == ["keep_me"]


def test_missing_required_field_raises_validation_error(tmp_path):
    broken_item = verified_item()
    del broken_item["source"]
    path = make_kb_file(tmp_path, [broken_item])

    with pytest.raises(ValidationError):
        KnowledgeRepository(data_path=path)
