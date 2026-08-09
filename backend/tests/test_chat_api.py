from fastapi.testclient import TestClient

import app.api.chat as chat_module
from app.knowledge.policy import KnowledgeRetrievalError
from app.main import app
from app.services.llm_service import LLMTimeoutError, LLMUnavailableError

client = TestClient(app)


def test_chat_endpoint_returns_reply(monkeypatch):
    async def fake_get_reply(message, history):
        return "mocked reply"

    monkeypatch.setattr(chat_module._chatbot_service, "get_reply", fake_get_reply)

    response = client.post("/api/chat", json={"message": "hello", "history": []})

    assert response.status_code == 200
    assert response.json() == {"reply": "mocked reply"}


def test_chat_endpoint_rejects_empty_message():
    response = client.post("/api/chat", json={"message": "", "history": []})

    assert response.status_code == 422


def test_chat_endpoint_maps_llm_timeout_to_504(monkeypatch):
    async def fake_get_reply(message, history):
        raise LLMTimeoutError("timed out")

    monkeypatch.setattr(chat_module._chatbot_service, "get_reply", fake_get_reply)

    response = client.post("/api/chat", json={"message": "hello", "history": []})

    assert response.status_code == 504


def test_chat_endpoint_maps_llm_unavailable_to_502(monkeypatch):
    async def fake_get_reply(message, history):
        raise LLMUnavailableError("down")

    monkeypatch.setattr(chat_module._chatbot_service, "get_reply", fake_get_reply)

    response = client.post("/api/chat", json={"message": "hello", "history": []})

    assert response.status_code == 502


def test_chat_endpoint_maps_knowledge_retrieval_error_to_502(monkeypatch):
    async def fake_get_reply(message, history):
        raise KnowledgeRetrievalError("index down")

    monkeypatch.setattr(chat_module._chatbot_service, "get_reply", fake_get_reply)

    response = client.post("/api/chat", json={"message": "hello", "history": []})

    assert response.status_code == 502


def test_chat_endpoint_with_real_policy_and_mocked_llm_grounds_on_knowledge(monkeypatch):
    """End-to-end through real retrieval/policy, only the LLM call is mocked —
    guards against the retrieval wiring silently breaking.
    """
    captured = {}

    async def fake_generate_reply(self, messages):
        captured["messages"] = messages
        return "Cadre AI is an AI strategy and implementation partner."

    monkeypatch.setattr(
        chat_module._chatbot_service._llm_service.__class__, "generate_reply", fake_generate_reply
    )

    response = client.post(
        "/api/chat", json={"message": "What does Cadre AI do?", "history": []}
    )

    assert response.status_code == 200
    context_message = captured["messages"][1]["content"]
    assert "company_overview" not in context_message  # IDs are internal, not shown to the LLM as facts
    assert "Cadre AI" in context_message
