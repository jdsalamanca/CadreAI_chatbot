# CLAUDE.md

## Project Overview

Build a production-quality MVP chatbot for Cadre AI as part of the AI Engineer coding challenge.

The application should allow a user to ask questions about Cadre AI and receive accurate, grounded answers based on a curated knowledge base.

The primary goal is not to build the most complex RAG system possible. The goal is to demonstrate sound AI engineering judgment, clean architecture, reliable retrieval, hallucination prevention, good UX, and the ability to explain technical decisions.

## Technology Stack

Use the following stack unless there is a strong technical reason not to:

### Frontend
- React
- TypeScript
- Vite
- Clean, simple chat interface

### Backend
- Python
- FastAPI
- Pydantic
- Uvicorn

### Knowledge Retrieval
- JSON as the authoritative knowledge repository
- Semantic embeddings for retrieval
- FAISS for local vector similarity search
- Embedding model should be selected based on availability, quality, simplicity, and challenge constraints

### LLM
- OpenRouter API
- Use the API key supplied for the chatbot only
- Do not use the supplied OpenRouter key for coding assistance
- The application should read the API key from an environment variable
- Do not hard-code secrets or commit them to Git

### Development Assistance
AI coding assistants such as Claude Code may be used for development.
Do not use the chatbot API key for coding assistance.

---

# Core Architecture

The application should follow this conceptual architecture:

User
  ↓
React Chat UI
  ↓
FastAPI API
  ↓
Chatbot Service
  ↓
Knowledge Retriever
  ↓
FAISS semantic search
  ↓
Relevant knowledge item IDs
  ↓
Original JSON knowledge items
  ↓
Knowledge policy / escalation checks
  ↓
LLM with grounded context
  ↓
Response
  ↓
React UI

The JSON knowledge base is the source of truth.

The FAISS index is a derived artifact that can be rebuilt from the JSON.

Do not make the vector index the authoritative storage for knowledge.

---

# Knowledge Base

The project contains:

`cadre_knowledge_base.json`

The knowledge base consists of independently retrievable knowledge items.

Each item generally contains:

- `id`
- `category`
- `topic`
- `retrieval_text`
- `content`
- `status`
- `source`
- `source_type`
- `escalation_required`
- optional metadata
- `last_verified`

## Embedding Rule

Only embed:

`retrieval_text`

Do NOT embed the entire JSON object.

The purpose of `retrieval_text` is to provide a semantically rich representation optimized for retrieval.

The purpose of `content` is to provide the authoritative information that can subsequently be supplied to the LLM.

This distinction should be preserved.

Conceptually:

knowledge item
    ├── retrieval_text → embedding → FAISS
    └── content → LLM context

The embedding should not contain metadata such as internal escalation rules unless that metadata is intentionally relevant to retrieval.

---

# Retrieval Design

The initial retrieval approach should be simple and explainable.

1. Load the JSON knowledge base.
2. Generate embeddings for each `retrieval_text`.
3. Build a FAISS index.
4. Store a mapping from FAISS vector position to knowledge item ID.
5. Embed the user's query.
6. Perform semantic similarity search.
7. Retrieve the top relevant knowledge items.
8. Apply a similarity threshold.
9. Retrieve the corresponding original JSON objects.
10. Apply knowledge-status and escalation rules.
11. Pass only appropriate knowledge to the LLM.

Do not introduce a managed vector database unless there is a demonstrated need.

The corpus is small enough that a local FAISS index is appropriate for this MVP.

---

# Retrieval Granularity

Treat each JSON knowledge dictionary as a semantic knowledge item / retrieval document.

Do not automatically split every item into arbitrary token chunks.

The knowledge base has intentionally been structured into meaningful units such as:

- company overview
- core services
- AI strategy
- AI Maturity Index
- individual industry opportunities
- client portal
- LLM selection
- data security
- individual case studies
- pricing limitations

The objective is semantic relevance rather than blindly chunking text by token count.

---

# Knowledge Status and Grounding

The application must distinguish between information that Cadre publicly documents and information that is not publicly available.

Possible statuses include:

- `verified`
- `not_publicly_available`

Do not invent information that is absent from the knowledge base.

Examples:

## Pricing

Cadre's service pricing is not publicly documented in the supplied research.

The chatbot must NOT invent a price.

It should explain that standard pricing is not publicly available and recommend speaking with an AI strategist.

## AI Maturity Index

The chatbot can explain the eight pillars.

It must NOT invent:

- numerical scoring percentages
- thresholds
- questionnaire length
- exact scoring methodology
- unsupported assessment procedures

## Client Portal

The chatbot may explain that Cadre provides a centralized portal for tracking AI tools, agents, training, and results.

It must NOT invent:

- login URLs
- credentials
- password reset instructions
- authentication methods
- account permissions

Questions requiring client-specific access information should be escalated.

## Security

The chatbot may describe the security practices explicitly supported by the knowledge base.

It must NOT infer or invent:

- SOC 2 certification
- security guarantees
- compliance certifications
- contractual guarantees
- technical security controls not documented in the knowledge base

---

# Unknown Questions

If semantic retrieval does not produce sufficiently relevant knowledge, the LLM must not answer as though it knows the Cadre-specific information from its general training.

The chatbot should acknowledge the limitation and provide an appropriate escalation path.

The system should therefore use an explicit retrieval threshold.

The threshold should be configurable through environment configuration rather than hard-coded throughout the application.

Example:

`RETRIEVAL_SIMILARITY_THRESHOLD`

The exact threshold should be determined empirically during development and documented in the final project.

---

# LLM Prompting

The LLM should receive:

1. The user's question
2. Relevant retrieved Cadre knowledge
3. Explicit grounding instructions
4. Relevant escalation information when applicable

The system prompt should make clear that:

- Cadre-specific factual claims must be grounded in supplied knowledge.
- The model must not invent missing information.
- Retrieved knowledge is authoritative for the application.
- The model should distinguish between documented information and unavailable information.
- The model should answer naturally rather than exposing internal implementation details.
- The model should escalate when the knowledge base indicates escalation is required.
- The model should not mention "RAG", embeddings, FAISS, retrieval scores, or internal metadata to the end user unless explicitly asked.

---

# Escalation

Escalation is a product behavior, not simply a fallback error.

The knowledge base contains explicit escalation metadata.

When:

`escalation_required == true`

the chatbot should not attempt to manufacture an answer.

Instead it should provide a concise explanation and an appropriate next step.

Current Cadre contact information in the knowledge base:

- Email: hello@gocadre.ai
- Phone: (619) 324-3223
- Contact page: https://www.cadreai.com/contact
- Strategy CTA: Talk to an AI Strategist

Do not invent additional contact information.

---

# Frontend

Build a clean, professional chat interface.

The interface should support:

- User messages
- Assistant messages
- Loading state
- Error state
- Clear conversation affordance if useful
- Mobile-friendly layout
- Reasonable empty state / welcome message
- Markdown rendering if useful
- Links where appropriate

The UI should prioritize clarity over visual complexity.

Do not spend excessive development time on animations or decorative components.

---

# Backend API

At minimum provide a chat endpoint such as:

`POST /api/chat`

Expected behavior:

1. Validate the incoming request.
2. Retrieve relevant knowledge.
3. Apply knowledge policy.
4. Call OpenRouter when appropriate.
5. Return the assistant response.

Use Pydantic models for request and response schemas.

Keep API concerns separate from business logic.

---

# Suggested Backend Structure

A reasonable structure is:

backend/
  app/
    main.py
    api/
      routes/
        chat.py
    services/
      chatbot.py
      llm.py
      knowledge/
        repository.py
        indexer.py
        retriever.py
    models/
      chat.py
      knowledge.py
    core/
      config.py
    knowledge/
      cadre_knowledge_base.json
    indexes/
      ...

The exact structure may change if a simpler organization is justified.

Avoid unnecessary abstraction.

---

# Configuration

Use environment variables for:

- OpenRouter API key
- selected LLM model
- embedding model configuration if needed
- retrieval threshold
- top-k retrieval count
- backend/frontend configuration as necessary

Provide:

`.env.example`

Never commit `.env`.

---

# Error Handling

Handle at least:

- Missing API key
- OpenRouter failure
- Embedding failure
- Empty user message
- No relevant knowledge retrieved
- Invalid request
- Unexpected backend errors

The user should receive a useful response rather than a stack trace.

Log useful diagnostic information server-side without exposing secrets.

---

# Security

Never commit:

- API keys
- `.env`
- credentials
- tokens

Do not log API keys.

Validate user input.

Do not expose internal retrieval metadata to the frontend unless intentionally needed for debugging.

---

# Testing

Tests should focus on behavior that matters.

At minimum test:

1. Knowledge base loading.
2. Embedding/index creation or retrieval behavior.
3. Relevant query retrieves expected knowledge.
4. Irrelevant query falls below the retrieval threshold.
5. Pricing query triggers the correct limitation/escalation behavior.
6. Portal-access query does not invent login information.
7. AI Maturity Index query retrieves the relevant knowledge.
8. Unknown Cadre-specific questions are handled safely.
9. Chat API validates requests correctly.

Mock external LLM/API calls in automated tests.

Do not spend excessive time testing third-party libraries.

---

# Code Quality

Follow normal production Python and TypeScript practices.

Prefer:

- Small functions
- Clear names
- Type hints
- Pydantic models
- Separation of concerns
- Explicit error handling
- Minimal duplication
- Readable code

Avoid:

- Overengineering
- Premature abstractions
- Large monolithic files
- Hidden global state
- Hard-coded secrets
- Hard-coded knowledge inside Python when it belongs in the JSON

---

# Documentation

Maintain:

`PLAN.md`

The plan should document:

- objectives
- architecture
- implementation phases
- decisions
- trade-offs
- testing strategy
- known limitations

Update it as major implementation decisions are made.

The final README should explain:

- What the application does
- Architecture
- How semantic retrieval works
- Why JSON + FAISS was chosen
- How to run the project
- Environment variables
- How the knowledge base works
- How to rebuild the index
- Testing
- Known limitations
- AI-assisted development process

---

# AI-Assisted Development

Claude Code may be used extensively.

However:

- Understand every significant implementation.
- Do not blindly accept generated code.
- Keep architectural decisions intentional.
- Keep commits reasonably scoped.
- Review generated code for correctness and security.
- Make sure the final implementation can be explained clearly during the technical interview.

The final developer should be able to explain why each major architectural decision was made.

---

# Development Priorities

Prioritize in this order:

1. Correctness
2. Grounded answers
3. Reliable retrieval
4. Safe handling of unknown information
5. Clean architecture
6. Good user experience
7. Tests
8. Polish

Do not sacrifice grounding or correctness for visual polish.