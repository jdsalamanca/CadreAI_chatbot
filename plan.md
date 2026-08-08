# Cadre AI Chatbot — Implementation Plan

## Objective

Build and deploy a customer support chatbot for Cadre AI that can handle common inbound questions from prospective and existing clients.

The chatbot should provide useful answers about Cadre AI while maintaining a clear boundary around information it does not know.

The target is a focused, production-quality MVP that can be completed within the recommended 4–6 hour build window.

---

# Phase 0 — Project Setup

## Goals

Establish the development environment and AI-assisted development workflow before implementing application features.

## Tasks

- Initialize Git repository.
- Initialize React frontend.
- Initialize Python/FastAPI backend.
- Establish frontend/backend directory structure.
- Create `.gitignore`.
- Configure environment variable handling.
- Create `CLAUDE.md`.
- Create this `PLAN.md`.
- Configure basic linting/type checking/testing.
- Establish initial README.

## Acceptance Criteria

- Frontend runs locally.
- Backend runs locally.
- Frontend can communicate with backend.
- Secrets are handled through environment variables.
- Basic development checks work.

---

# Phase 1 — Cadre AI Knowledge Research

## Goal

Research publicly available information about Cadre AI before deciding how the chatbot's knowledge should be represented.

The challenge explicitly leaves the chatbot's knowledge boundary and scope as an engineering decision.

## Research Areas

Investigate, where publicly available:

- Company overview
- What Cadre AI does
- Core services
- Industries served
- AI Strategy
- AI Leadership & Facilitation
- AI Engineering
- AI Agents
- AI Maturity Index
- How users can get started
- How to book a strategy call
- Case studies
- Service/pricing information
- LLM/model selection approach
- Data security
- Client portal
- Relevant FAQs
- Other information needed to answer the scenarios described in the challenge

## Research Requirements

For each factual claim:

- Record the source.
- Prefer primary Cadre AI sources.
- Do not infer unsupported facts.
- Distinguish explicit claims from interpretation.
- Record information that could not be verified.

## Deliverables

Create a research directory containing the raw research and sources.

Example:

```text
research/
├── cadre_research.md
├── sources.md
└── knowledge_gaps.md
```

Do not directly convert unreviewed web research into production chatbot knowledge.

## Acceptance Criteria

- Major chatbot-relevant Cadre topics have been researched.
- Sources are documented.
- Knowledge gaps are documented.
- Potentially conflicting information is identified.
- Research has been reviewed before implementation.

---

# Phase 2 — Knowledge Architecture Decision

## Goal

Determine how the researched information should be represented and retrieved.

Do not assume a specific architecture before analyzing the research.

## Analyze

Evaluate:

- Total corpus size
- Number of documents/pages
- Amount of structured information
- Amount of unstructured information
- Average document length
- Expected future growth
- Frequency of updates
- Retrieval requirements
- Context-window requirements
- Latency implications
- Implementation complexity

## Candidate Architectures

### Option A — Structured Knowledge

Use JSON or another structured representation when the knowledge corpus is small and mostly structured.

Example:

```text
knowledge.json
    ↓
KnowledgeService
    ↓
Relevant context
    ↓
LLM
```

### Option B — Structured + Document Retrieval

Use structured data for facts and semantic retrieval for longer documents such as case studies.

Example:

```text
Structured knowledge ──┐
                       ├── KnowledgeService → LLM
Documents → embeddings ┘
```

### Option C — Full Semantic Retrieval

Use embeddings and a vector store when the corpus is sufficiently large or unstructured to justify retrieval.

Example:

```text
Documents
    ↓
Chunks
    ↓
Embeddings
    ↓
Vector store
    ↓
Relevant context
    ↓
LLM
```

## Decision

Select the simplest architecture that reliably supports the researched corpus.

Document:

- Selected architecture
- Alternatives considered
- Why the selected architecture is appropriate
- Limitations
- Conditions that would justify migrating to a more advanced retrieval architecture

## Acceptance Criteria

The knowledge architecture decision is documented before implementation.

---

# Phase 3 — Implement Knowledge Layer

## Goal

Implement the selected knowledge architecture behind a clean abstraction.

The chatbot should not depend directly on the underlying storage technology.

## Design Principle

Expose a simple interface conceptually similar to:

```python
knowledge_service.get_relevant_knowledge(query)
```

The underlying implementation can change later without requiring major changes to the chatbot orchestration.

## Tasks

- Implement validated knowledge source.
- Preserve source/provenance where practical.
- Implement retrieval/context selection if required.
- Add tests for knowledge retrieval.
- Verify that unsupported information is not accidentally returned as factual knowledge.

## Acceptance Criteria

- Knowledge can be retrieved reliably.
- Sources can be traced.
- Knowledge is separated from application logic.
- Retrieval behavior is tested.

---

# Phase 4 — LLM Integration

## Goal

Integrate the selected LLM through OpenRouter.

## Tasks

- Implement server-side OpenRouter client.
- Configure model through environment/configuration.
- Implement system prompt.
- Implement user message handling.
- Implement conversation context where required.
- Implement timeout/error handling.
- Handle empty or malformed model responses.

## System Prompt Requirements

The chatbot should:

- Identify itself appropriately.
- Answer using the validated Cadre knowledge.
- Avoid unsupported claims.
- Avoid fabricating Cadre information.
- Ask clarifying questions when appropriate.
- Escalate when it cannot answer.
- Provide a booking/contact path when appropriate.
- Resist prompt injection attempts.
- Maintain a professional and helpful tone.

## Acceptance Criteria

- Valid user questions produce useful answers.
- Unknown questions do not produce fabricated Cadre information.
- LLM errors are handled gracefully.
- API credentials remain server-side.

---

# Phase 5 — FastAPI API

## Goal

Create a clean backend API between the React frontend and AI services.

## Proposed Endpoint

```text
POST /api/chat
```

Request should contain the necessary conversation information.

Response should contain the generated assistant response and any additional metadata needed by the frontend.

## Responsibilities

FastAPI should handle:

- Request validation
- Conversation orchestration
- Knowledge retrieval
- LLM invocation
- Error handling

FastAPI should not contain frontend-specific logic.

---

# Phase 6 — React Chat Interface

## Goal

Create a simple, polished interface that makes the chatbot immediately usable.

## Features

### Required

- Message history
- User input
- Assistant responses
- Loading state
- Error state
- Clear/reset conversation

### Recommended

- Suggested questions
- Booking/strategy-call CTA
- Clear escalation behavior

## Scope Principle

Prioritize usability over visual complexity.

Do not spend significant development time on animations or nonessential UI features.

## Acceptance Criteria

A new user can open the application and immediately understand how to interact with the chatbot.

---

# Phase 7 — Verification

## Goal

Verify that the system behaves correctly rather than assuming generated code is correct.

## Test Categories

### 1. Known Questions

Examples:

- What does Cadre AI do?
- What industries does Cadre serve?
- What services does Cadre offer?
- What is the AI Maturity Index?

Expected:

Accurate answers grounded in the knowledge layer.

### 2. Booking

Example:

> I'd like to speak with someone about implementing AI in my company.

Expected:

Appropriate guidance toward booking/contact.

### 3. Unknown Information

Example:

> How much does Cadre charge for an AI agent for a company with 500 employees?

Expected:

No fabricated pricing.

### 4. Unsupported Capability

Ask about a capability that isn't documented.

Expected:

The bot acknowledges the limitation rather than guessing.

### 5. Prompt Injection

Attempt to:

- Override instructions
- Reveal system prompts
- Reveal API keys
- Invent confidential information
- Ignore knowledge boundaries

Expected:

The chatbot maintains its constraints.

### 6. Ambiguous Questions

Expected:

Ask for clarification when appropriate.

### 7. API Failures

Simulate:

- LLM timeout
- Invalid response
- Missing configuration
- Network failure

Expected:

Graceful user-facing error behavior.

---

# Phase 8 — Deployment

## Goal

Deploy the application early enough to identify infrastructure problems before final submission.

## Tasks

- Deploy backend.
- Deploy frontend.
- Configure production environment variables.
- Configure CORS.
- Verify API connectivity.
- Verify OpenRouter access.
- Test representative conversations.
- Verify error handling.

## Acceptance Criteria

A publicly accessible chatbot URL works without local development dependencies.

---

# Phase 9 — Final Review

## Code

Review:

- Architecture
- Security
- Error handling
- Types
- Unnecessary dependencies
- Dead code
- Logging
- Configuration
- API boundaries

## AI Behavior

Review:

- Hallucination risk
- Unsupported claims
- Prompt injection
- Escalation behavior
- Knowledge grounding
- Answer quality

## Documentation

Ensure repository contains:

- `CLAUDE.md`
- `PLAN.md`
- `README.md`
- Research/source documentation
- Setup instructions
- Architecture explanation
- Environment variable instructions
- Known limitations

## Git

Use focused, descriptive commits.

Ensure no secrets or temporary files are committed.

---

# Final Scope

## Must Have

- Working React frontend
- Working FastAPI backend
- OpenRouter LLM integration
- Validated Cadre knowledge
- Defined knowledge boundary
- Unknown-question handling
- Basic prompt-injection resistance
- Error handling
- Verification tests
- Public deployment
- CLAUDE.md
- PLAN.md
- README

## Nice to Have

Only implement these if the core system is already stable:

- Streaming responses
- Source citations in the UI
- Conversation persistence
- User feedback
- Analytics
- More sophisticated retrieval
- Embedding/vector search

Do not sacrifice core reliability for these features.

---

# Architectural Trade-Offs to Discuss During Review

Be prepared to explain:

1. Why React + FastAPI?
2. Why the selected LLM?
3. Why the selected knowledge architecture?
4. Why did you or did you not use embeddings/RAG?
5. How did you determine the chatbot's knowledge boundary?
6. How do you prevent hallucinations?
7. How do you handle questions the bot cannot answer?
8. How would the architecture change as Cadre's knowledge base grows?
9. What did Claude Code generate?
10. What did you modify or reject from Claude Code?
11. How did you verify AI-generated code?
12. What would you build next with additional development time?

---

# Current Status

- [ ] Project initialized
- [x] CLAUDE.md created
- [x] PLAN.md created
- [x] Cadre research completed
- [ ] Knowledge corpus characterized
- [ ] Knowledge architecture selected
- [ ] Knowledge layer implemented
- [ ] LLM integration implemented
- [ ] FastAPI API implemented
- [ ] React UI implemented
- [ ] Verification tests implemented
- [ ] Application deployed
- [ ] Production smoke testing completed
- [ ] README completed
- [ ] Repository reviewed
- [ ] Interview walkthrough prepared