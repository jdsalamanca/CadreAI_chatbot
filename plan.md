# PLAN.md

# Cadre AI Chatbot — Implementation Plan

## 1. Objective

Build a React + FastAPI chatbot for Cadre AI that can answer prospective and existing-client questions using a curated, source-attributed knowledge base.

The chatbot should demonstrate:

- Semantic retrieval
- Grounded LLM responses
- Knowledge verification
- Explicit handling of unknown information
- Escalation when appropriate
- Clean software architecture
- Good frontend UX
- Sensible engineering trade-offs

The goal is a reliable MVP rather than an unnecessarily complex production platform.

---

# 2. Core User Scenarios

The chatbot must handle at least the following scenarios.

### Company and Services

- What does Cadre AI do?
- What services does Cadre provide?
- Does Cadre build AI software?
- How does Cadre decide whether to build something custom?

### Getting Started

- How do I get started with Cadre?
- What is the AI Transformation Intensive?
- What happens during the process?

### Pricing

- How much does Cadre cost?
- What does AI Strategy cost?
- How much does an AI agent cost?

Expected behavior:
Do not invent pricing. Explain that standard service pricing is not publicly available and direct the user toward an AI strategist.

### AI Maturity Index

- What is the AI Maturity Index?
- What are the eight pillars?
- How do I get scored?

Expected behavior:
Explain documented information. Do not invent the scoring methodology or numerical thresholds.

### Strategy Calls

- How do I book a strategy call?
- How do I talk to an AI strategist?

Expected behavior:
Provide the documented CTA/contact information.

### Industries

- Do you work with manufacturing?
- Does Cadre work with real estate?
- Can you help financial services companies?
- Do you work with my industry?

Expected behavior:
Use the industry knowledge and do not reject an industry merely because it is not in the public list.

### Client Portal

- How do I access the Cadre portal?
- Where do I log in?
- I forgot my portal password.

Expected behavior:
Explain what the portal is known to provide, but do not invent login information. Escalate.

### LLM Selection

- What LLMs does Cadre use?
- How does Cadre choose an LLM?
- Do you use Claude/OpenAI/etc.?

Expected behavior:
Explain the use-case-driven model-selection approach using only supported information.

### Security

- How does Cadre protect our data?
- Is our data used to train models?
- Is Cadre SOC 2 compliant?

Expected behavior:
Answer only claims supported by the knowledge base. Do not invent certifications or guarantees.

### Case Studies

- Do you have manufacturing examples?
- What has Cadre done for professional services?
- Do you have examples in hospitality?
- What results have Cadre achieved?

Expected behavior:
Retrieve the most relevant case studies and clearly identify reported results as case-study results.

### Unknown Questions

- Questions unrelated to Cadre
- Questions about unsupported Cadre facts
- Questions requiring private/client-specific information

Expected behavior:
Do not hallucinate. Explain the limitation and redirect/escalate where appropriate.

---

# 3. Architecture

```text
                 React Frontend
                       │
                       │ POST /api/chat
                       ▼
                 FastAPI Backend
                       │
                       ▼
                Chatbot Service
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Knowledge Retriever    LLM Service
             │                   │
             ▼                   │
        FAISS Index              │
             │                   │
             ▼                   │
      Knowledge Repository       │
             │                   │
             ▼                   │
     cadre_knowledge_base.json ──┘
```

The JSON is authoritative.

The FAISS index is derived from the JSON.

The LLM receives relevant `content` from retrieved knowledge items rather than the raw retrieval representation.

---

# 4. Knowledge Representation

Each knowledge item is a semantic retrieval unit.

Example:

```json
{
  "id": "ai_maturity_index",
  "category": "assessment",
  "topic": "AI Maturity Index",
  "retrieval_text": "...",
  "content": "...",
  "status": "verified",
  "source": "...",
  "escalation_required": false
}
```

The important separation is:

### Retrieval representation

`retrieval_text`

Used to generate embeddings.

### Authoritative representation

`content`

Used as context for the LLM.

### Policy metadata

`status`, `escalation_required`, `escalation_reason`, etc.

Used by the application to determine how retrieved information may be used.

---

# 5. Phase 1 — Project Setup

## Tasks

- Initialize repository.
- Create React/Vite frontend.
- Create FastAPI backend.
- Establish project structure.
- Add `.gitignore`.
- Add `.env.example`.
- Add initial README.
- Add `CLAUDE.md`.
- Add `PLAN.md`.

## Definition of Done

The frontend and backend can start independently and communicate successfully.

---

# 6. Phase 2 — Knowledge Repository

## Tasks

Implement a knowledge repository responsible for:

- Loading `cadre_knowledge_base.json`
- Validating the structure
- Exposing knowledge items by ID
- Providing the collection of retrievable items

Potential interface:

```python
load()
get_by_id(id)
get_all()
```

Use Pydantic models where appropriate.

Do not hard-code Cadre knowledge into Python.

## Definition of Done

The application can load and validate the complete knowledge base.

---

# 7. Phase 3 — Embeddings and FAISS

## Tasks

Implement the indexing pipeline.

For every knowledge item:

```text
knowledge item
     ↓
retrieval_text
     ↓
embedding model
     ↓
vector
     ↓
FAISS
```

Maintain a mapping:

```text
FAISS index position → knowledge item ID
```

The embedding model should be configurable.

Do not store embeddings inside the JSON.

The index should be rebuildable from the JSON.

## Important

Do not introduce a hosted vector database.

The knowledge base is small enough for local FAISS.

## Definition of Done

A query can be embedded and used to retrieve the most semantically relevant knowledge items.

---

# 8. Phase 4 — Retrieval Evaluation

Before integrating the LLM, test retrieval independently.

Create a small evaluation set covering:

```text
Question
Expected knowledge item(s)
```

Examples:

```text
"What does Cadre do?"
→ company_overview / core_services

"Does Cadre work with construction companies?"
→ industries / industry_construction

"What is the AI Maturity Index?"
→ ai_maturity_index_overview / ai_maturity_index_pillars

"How much does Cadre charge?"
→ service_pricing

"Where do I log into the portal?"
→ client_portal / client_portal_access_gap

"How does Cadre choose an LLM?"
→ llm_selection

"What security certifications does Cadre have?"
→ data_security or insufficient relevant knowledge
```

Measure whether the expected knowledge items appear in the top-k results.

Tune:

- embedding model
- top-k
- similarity threshold

based on observed behavior rather than arbitrary assumptions.

---

# 9. Phase 5 — Knowledge Policy

Implement a policy layer between retrieval and LLM generation.

Conceptually:

```text
retrieve
   ↓
filter by relevance
   ↓
inspect status
   ↓
inspect escalation_required
   ↓
construct response context
```

Examples:

### Verified

```text
status = verified
escalation_required = false
```

Pass content to the LLM.

### Not publicly available

```text
status = not_publicly_available
escalation_required = true
```

Provide the LLM with the limitation and escalation instructions, or handle the escalation deterministically where appropriate.

### No relevant result

Do not ask the LLM to guess.

Return a safe fallback or escalation response.

---

# 10. Phase 6 — LLM Integration

Implement an LLM service responsible for communicating with OpenRouter.

The model should be configurable.

Environment variables should include something similar to:

```text
OPENROUTER_API_KEY=
OPENROUTER_MODEL=
```

Do not hard-code the API key.

The system prompt should enforce:

1. Answer using supplied Cadre knowledge.
2. Do not invent facts.
3. Do not infer unsupported claims.
4. Be transparent when information is unavailable.
5. Follow escalation instructions.
6. Answer conversationally.
7. Do not expose internal implementation details.

The retrieved knowledge should be included as structured context.

---

# 11. Phase 7 — Chat API

Implement:

`POST /api/chat`

Example request:

```json
{
  "message": "What does Cadre AI do?"
}
```

Example response:

```json
{
  "message": "...",
  "escalation_required": false
}
```

The exact response schema can be adjusted as implementation progresses.

Keep the API independent from the frontend.

---

# 12. Phase 8 — React Chat UI

Build a simple professional interface.

Required:

- Chat history
- User/assistant message distinction
- Input field
- Send action
- Loading indicator
- Error handling
- Empty state
- Responsive layout

Potential enhancement:

For strategy-call responses, make:

**Talk to an AI Strategist**

a clickable CTA.

Do not invent a scheduling URL. Use only a verified URL available in the knowledge base or project configuration.

---

# 13. Phase 9 — Testing

Implement tests for:

### Knowledge

- JSON loads correctly.
- Invalid knowledge structures fail clearly.

### Retrieval

- Relevant queries return relevant items.
- Irrelevant queries can fall below the threshold.
- Correct knowledge IDs are returned.

### Policy

- Verified information can be used.
- Pricing triggers the correct behavior.
- Portal access does not invent instructions.
- Unsupported scoring information is not invented.

### API

- Valid request succeeds.
- Empty message is rejected.
- External LLM errors are handled.
- Unexpected errors do not expose stack traces.

Mock OpenRouter calls.

---

# 14. Phase 10 — Evaluation Questions

Before submission, manually test the chatbot with at least these questions:

1. What does Cadre AI do?
2. Does Cadre build AI software?
3. How do I get started?
4. What is the AI Transformation Intensive?
5. How much does Cadre charge?
6. What is the AI Maturity Index?
7. What are the eight pillars?
8. How do I get my AI Maturity score?
9. How do I book a strategy call?
10. Do you work with manufacturing?
11. Do you work with an industry that isn't listed?
12. How do I access the Cadre portal?
13. What LLMs does Cadre use?
14. How does Cadre choose an LLM?
15. How does Cadre protect our data?
16. Is Cadre SOC 2 compliant?
17. Show me a manufacturing case study.
18. Show me a professional services case study.
19. What results has Cadre achieved?
20. Ask an unrelated question.

For each, verify:

- Retrieval relevance
- Factual accuracy
- No hallucinations
- Correct escalation
- Natural response

---

# 15. Phase 11 — Documentation

README should contain:

## Overview

What the chatbot does.

## Architecture

React → FastAPI → Retriever → FAISS → Knowledge Base → OpenRouter.

## Knowledge Base

Explain why JSON is the source of truth.

## Retrieval

Explain why `retrieval_text` is embedded rather than the entire JSON object.

## Grounding

Explain how verified and unavailable knowledge is handled.

## Escalation

Explain how unsupported questions and unavailable information are handled.

## Setup

Explain environment variables and how to run frontend/backend.

## Testing

Explain how to run tests.

## Limitations

Document:

- Public knowledge limitations
- Pricing not publicly available
- Portal access information not publicly available
- Exact AI Maturity scoring methodology not publicly available
- Dependence on external LLM/API
- Local FAISS architecture

---

# 16. Phase 12 — Final Review

Before submission:

- Remove secrets.
- Verify `.env` is ignored.
- Verify `.env.example` is present.
- Run tests.
- Run frontend.
- Run backend.
- Test the full chat flow.
- Verify OpenRouter API usage.
- Verify retrieval.
- Verify escalation.
- Review README.
- Review CLAUDE.md.
- Review PLAN.md.
- Review git diff.
- Remove unnecessary files.
- Ensure the repository can be cloned and run by another developer.

---

# 17. Definition of Success

The project is successful when:

1. A user can have a natural conversation with the chatbot.
2. Relevant Cadre information is retrieved semantically.
3. The LLM produces grounded answers.
4. The chatbot does not invent unsupported Cadre facts.
5. Pricing questions are handled safely.
6. Portal access questions are handled safely.
7. AI Maturity Index questions are handled accurately.
8. Industry questions are handled appropriately.
9. Case studies are retrievable.
10. Unknown questions trigger appropriate fallback/escalation.
11. The code is clean and explainable.
12. The project can be run by another developer from the README.
13. The developer can explain the major architectural decisions during the Day 5 interview.

---

# Current Status

Completed:

- Challenge requirements reviewed.
- React + FastAPI selected.
- JSON knowledge repository approach selected.
- Semantic retrieval approach selected.
- FAISS selected as the initial vector index.
- `retrieval_text` selected as the only text to embed.
- JSON remains the source of truth.
- Verified/unavailable knowledge distinction established.
- Explicit escalation behavior established.
- Cadre knowledge base created.
- Project structure initialized (React/Vite frontend, FastAPI backend, single-container Docker deployment,
  all verified working end-to-end prior to knowledge integration).
- `cadre_knowledge_base.json` integrated into `backend/app/knowledge/data/`.
- Knowledge repository implemented (`KnowledgeRepository`: load, validate, `get_by_id`, `get_all`,
  escalation info; unsupported-status items excluded automatically) — tested.
- Embedding/indexing pipeline implemented (`indexer.py`: `fastembed` (ONNX) + local FAISS `IndexFlatIP` over
  `retrieval_text`; FAISS-position → knowledge-item-ID mapping; index rebuilt from the repository at
  construction time, never persisted, embeddings never stored in the JSON).
- Semantic retrieval implemented (`retriever.py`: `KnowledgeRetriever.retrieve(query, top_k)`).
- Retrieval evaluation set built and tuned (`app/knowledge/evaluation.py`,
  `scripts/evaluate_retrieval.py`): 27-question eval set, 100% hit rate at `top_k=5` (started at 85.2% for
  `top_k=3`), `RETRIEVAL_SIMILARITY_THRESHOLD=0.5` calibrated against a clear score gap between genuine
  matches (≥0.59) and off-topic queries (≤0.48). See `ARCHITECTURE.md` for full results and trade-offs.

Next:

1. Wire `KnowledgeRetriever` into `ChatbotService` (currently implemented and tested standalone, but the
   live `/api/chat` endpoint doesn't call it yet).
2. Implement the grounding/policy layer (Phase 5: inspect `status`/`escalation_required`, safe fallback when
   no relevant result clears the threshold).
3. Rewrite the system prompt per Phase 6's requirements (grounding, escalation, no mention of
   RAG/embeddings/FAISS/scores to the end user).
4. Update the chat API response schema if needed (e.g. `escalation_required`).
5. Update the React chat UI for CTA/escalation behavior (Phase 8).
6. Add remaining tests (policy layer, API-level with mocked OpenRouter).
7. Document and polish (README per Phase 11).
8. Final end-to-end evaluation against the Phase 10 question list.