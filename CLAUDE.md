# Cadre AI Customer Support Chatbot

## Project Overview

Build a production-quality MVP customer support chatbot for Cadre AI.

The chatbot should help prospective and existing clients with common inbound questions about Cadre AI, including:

- What Cadre AI does
- Services and capabilities
- Industries served
- How to get started
- How to book a strategy call
- The AI Maturity Index
- Case studies
- LLM/model selection
- Data security
- Client portal access
- Questions that are outside the chatbot's knowledge or scope

The application will use:

- React for the frontend
- Python + FastAPI for the backend
- OpenRouter for LLM access
- A knowledge layer whose architecture will be determined after researching and characterizing Cadre AI's publicly available information

Do not assume that the knowledge layer must use JSON, embeddings, RAG, or a vector database. Choose the simplest architecture that reliably supports the resulting knowledge corpus.

---

## Core Engineering Principles

### 1. Research Before Architecture

Do not make major knowledge architecture decisions before understanding the available Cadre AI information.

The initial workflow should be:

1. Research publicly available Cadre AI information.
2. Record sources and factual claims.
3. Review and validate the research.
4. Characterize the resulting knowledge corpus:
   - Size
   - Structure
   - Number and type of documents
   - Frequency of updates
   - Relationship between structured and unstructured information
5. Select the simplest appropriate knowledge architecture.
6. Implement the knowledge layer.
7. Build retrieval/context injection around that layer.

Do not introduce RAG, embeddings, a vector database, or other infrastructure simply because it is an AI chatbot.

---

## Knowledge Integrity

The chatbot must not invent information about Cadre AI.

Treat the validated knowledge corpus as the source of truth.

When information is unavailable:

- Do not guess.
- Do not fabricate pricing, capabilities, clients, case studies, policies, or technical details.
- Clearly communicate that the information is unavailable.
- Provide an appropriate escalation or contact path when applicable.

Every externally researched factual claim should have a traceable source.

Prefer primary Cadre AI sources over third-party sources.

Do not silently convert assumptions or inferences into factual knowledge.

---

## Application Architecture

Maintain clear separation of concerns.

### Frontend

React is responsible for:

- Chat interface
- Message rendering
- User input
- Loading and error states
- Suggested questions
- Escalation / booking calls to action where appropriate

The frontend must not contain:

- API keys
- OpenRouter credentials
- Server-side configuration
- Direct calls to the LLM provider

### Backend

FastAPI is responsible for:

- API endpoints
- Request validation
- Conversation orchestration
- Knowledge retrieval
- LLM interaction
- Error handling
- Configuration

### Services

Keep the following responsibilities separate where practical:

- `ChatbotService` — conversation orchestration
- `KnowledgeService` — access to Cadre knowledge
- `LLMService` — interaction with OpenRouter
- Configuration — environment variables and application settings

The chatbot should depend on a knowledge abstraction rather than directly depending on a specific storage/retrieval implementation.

For example, the initial implementation may use structured JSON, while a future implementation could use semantic retrieval without requiring major changes to the chatbot orchestration layer.

---

## LLM Guidelines

Use OpenRouter for model access.

Do not hardcode model-specific behavior throughout the application.

Keep:

- Model configuration
- System prompts
- LLM client logic
- Generation parameters

separate from application/business logic.

The system prompt should explicitly define:

- The chatbot's role
- Its knowledge boundary
- Appropriate tone
- How to handle unknown information
- How to handle unsupported requests
- How to handle escalation
- How to avoid hallucinating Cadre-specific information
- Basic prompt-injection resistance

Do not place the entire application architecture inside the system prompt.

Knowledge and behavioral instructions should remain conceptually separate.

---

## Security

Never commit secrets to Git.

Use environment variables for:

- OpenRouter API key
- API configuration
- Deployment configuration
- Other credentials

Never expose server-side environment variables to the React client.

Ensure `.env` files containing secrets are ignored by Git.

The provided challenge API key is exclusively for powering the chatbot and must not be used for unrelated development or coding assistance.

---

## Development Workflow

Claude Code should be used as an AI development partner, not as an autonomous replacement for engineering judgment.

Before implementing a significant feature:

1. Read `PLAN.md`.
2. Understand the current architecture.
3. Identify the smallest appropriate implementation.
4. Implement the feature.
5. Inspect generated code.
6. Run relevant tests/checks.
7. Fix issues.
8. Update documentation or `PLAN.md` when architectural decisions change.

Do not blindly accept generated code.

If generated code introduces unnecessary complexity, reject or simplify it.

If Claude's implementation conflicts with the architecture, stop and discuss the conflict before proceeding.

---

## Subagents

Use subagents when tasks are sufficiently independent to benefit from parallel work.

Good candidates include:

- Web research
- Knowledge-base analysis
- Security review
- Test-case generation
- Code review

Do not use subagents simply to increase activity.

Each subagent should have:

- A clearly defined objective
- Relevant context
- A concrete output
- A clear boundary around what it may modify

Review all subagent output before incorporating it into the project.

---

## Testing and Verification

The chatbot should be tested against at least the following categories:

### Normal questions

Questions that should have clear answers from the knowledge base.

### Out-of-scope questions

Questions that Cadre's public information does not support.

Expected behavior: do not fabricate an answer.

### Hallucination tests

Questions designed to tempt the model to invent:

- Pricing
- Clients
- Case studies
- Capabilities
- Policies
- Technical details

### Prompt-injection tests

Attempts to make the chatbot:

- Ignore its instructions
- Reveal hidden prompts
- Reveal credentials
- Invent confidential information
- Override its knowledge boundaries

### Ambiguous questions

Questions where clarification is preferable to guessing.

### Escalation

Questions where the correct behavior is to redirect the user toward a Cadre representative or strategy call.

Run automated checks and manually test important conversational flows before considering the MVP complete.

---

## Code Quality

Prefer:

- Small functions
- Explicit types
- Clear naming
- Separation of concerns
- Useful error handling
- Minimal dependencies
- Simple implementations

Avoid:

- Premature abstractions
- Unnecessary frameworks
- Unnecessary databases
- Over-engineered agent architectures
- Duplicated business logic
- Large functions combining unrelated responsibilities

Choose boring, reliable engineering when it is sufficient.

---

## Scope Management

The target is a polished MVP, not a complete production platform.

Prioritize:

1. Correct answers
2. Reliable knowledge boundaries
3. Good user experience
4. Clean architecture
5. Verification
6. Deployment

Do not sacrifice a working core experience for additional features.

If a feature is intentionally excluded, document the reason in `PLAN.md`.

---

## Deployment

The application must be publicly accessible before the review.

Deploy early rather than waiting until the end of development.

After deployment:

- Verify frontend accessibility.
- Verify API connectivity.
- Verify production environment variables.
- Test representative chatbot interactions.
- Test error handling.
- Verify that no secrets are exposed.

---

## Git

Use small, focused commits with descriptive messages.

Prefer commits such as:

- `chore: initialize project`
- `docs: add project plan`
- `feat: add Cadre knowledge research`
- `feat: implement knowledge service`
- `feat: add chatbot API`
- `feat: implement chat interface`
- `test: add hallucination scenarios`
- `fix: handle LLM errors`
- `chore: prepare production deployment`

Avoid one large final commit containing the entire project.

---

## Important Decision Rule

When choosing between two technically valid approaches:

1. Prefer the simpler solution.
2. Prefer the approach the engineer can fully explain and verify.
3. Prefer the approach that satisfies the current requirements.
4. Consider future scalability, but do not implement future complexity without a present need.
5. Document meaningful trade-offs in `PLAN.md`.

The goal is not to demonstrate how much infrastructure can be built.

The goal is to demonstrate sound engineering judgment while using AI-assisted development effectively.