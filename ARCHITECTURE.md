# Knowledge Architecture Decision

## Status: superseded by an explicit semantic-retrieval requirement

The analysis below (full-context injection, no embeddings) was the original Phase 2 decision, made when
`plan.md`/`CLAUDE.md` left the knowledge architecture open and only required "the simplest architecture
that reliably supports the corpus." `plan.md` and `CLAUDE.md` were since rewritten to explicitly require
semantic retrieval via embeddings + a local FAISS index (see `plan.md` Phase 3 "Embeddings and FAISS" and
Phase 4 "Retrieval Evaluation"). That is a deliberate scope decision by the project owner — demonstrating
semantic retrieval is now an explicit goal of the exercise, not something the corpus size alone would have
required. The original analysis is kept below rather than deleted, because it's still the honest answer to
"would this corpus need RAG on its own merits?" (no) — the interview-ready framing is: *"the corpus itself
is small enough that a much simpler design would have worked, but I built FAISS-backed retrieval because it
was an explicit requirement, and here's how I made that reliable and measured it."*

See **"Revised Decision — Semantic Retrieval with FAISS"** below for what was actually implemented in
Phase 3/4.

---

## Original Phase 2 Analysis (corpus-driven, since superseded)

This was the original Phase 2 deliverable from `plan.md`: analyze the researched Cadre AI corpus
(`research/`, `cadre_knowledge_base.json`) and decide how it should be represented and retrieved, before
writing any retrieval code.

## Corpus Analysis

Measured directly from `cadre_knowledge_base.json`:

| Metric | Value |
|---|---|
| Knowledge items | 27 |
| Categories | 11 (company, services, getting_started, commercial, assessment, contact, industries, client_portal, technology, security, case_studies) |
| Status breakdown | 24 `verified`, 3 `not_publicly_available` (escalation-flagged gaps) |
| Total corpus size | ~24.9 KB / ~6,200 tokens for the entire file |
| `retrieval_text` only (all 27 items) | ~1,500 tokens |
| Average item length | 274 characters |
| Longest item | 799 characters (an eight-pillar breakdown) |
| Expected update frequency | Low — tied to Cadre publishing new case studies/pages, not a live data feed |
| Document type | Entirely structured, short, discrete facts — no long-form documents (no whitepapers, transcripts, or multi-page PDFs) |

Two things stand out:

1. **The entire corpus fits comfortably in a single LLM call's context.** Even the full JSON file is
   ~6,200 tokens — a small fraction of `gpt-4o-mini`'s context window, and negligible in latency/cost terms
   (fractions of a cent per request at OpenRouter's per-token pricing).
2. **There is nothing to chunk.** Every item is already a short, independently meaningful unit (274 chars
   average, 799 max). Chunking strategies exist to solve the problem of documents that are too long to fit
   in context or too long for a single embedding to represent well — that problem doesn't exist here.

## Candidate Architectures Considered

### Option A — Structured Knowledge (JSON), full-context injection — **Selected**

Load `cadre_knowledge_base.json` once at startup; on every request, hand the model the full set of
`verified` items (plus the escalation-flagged gaps, so the model always knows its own boundaries) as
structured context alongside the system prompt.

### Option A′ — Structured Knowledge (JSON), keyword-filtered retrieval — Considered, rejected

Same storage, but `get_relevant_knowledge(query)` scores items by keyword/substring overlap against
`topic`/`retrieval_text`/`category` and returns only a top-N subset.

Rejected because, at this corpus size, filtering adds a real failure mode (a user asks something that
doesn't lexically match an item's stored keywords — e.g. "law firms" vs. the stored "Professional
Services" — and a relevant item silently gets excluded) in exchange for a benefit that doesn't materialize
at 6,200 tokens (token/cost/latency savings are negligible). It also means the model would only see the
`not_publicly_available` guardrail items when the query happens to match them, weakening the
"always know your own boundaries" property that full injection gives for free.

### Option B — Structured + Document Retrieval (embeddings for long documents)

Reserved for a corpus with genuinely long unstructured documents (e.g. full case-study PDFs, transcripts,
a knowledge-base wiki) alongside structured facts, where the long documents don't fit in context and need
chunking + semantic search. Rejected: the current corpus has no such documents — every case study is
already a short structured summary.

### Option C — Full Semantic Retrieval (embeddings + vector store)

Reserved for a large or heavily unstructured corpus where relevant context can't be reliably determined
without semantic search. Rejected: 27 short structured items don't justify a vector store, an embedding
pipeline, or the operational overhead (re-embedding on updates, index management, similarity-search
latency) that comes with it. This would be infrastructure added because "it's an AI chatbot," which
`CLAUDE.md` explicitly warns against.

## Decision

**Option A, with full-context injection instead of query-time filtering.**

`KnowledgeService` will expose an interface shaped like `get_relevant_knowledge(query: str)` (matching the
shape `plan.md` proposes, so `ChatbotService` never depends on how knowledge is stored or selected), but at
the current corpus size its implementation is intentionally trivial: it returns the entire validated
corpus, formatted as source-attributed context, regardless of `query`. The `query` parameter exists for
interface stability — so that introducing real filtering later (Option A′) is a change inside
`KnowledgeService` only, with zero changes to `ChatbotService` or the API layer.

### Why this is appropriate

- Matches `plan.md`'s decision rule: prefer the simpler solution the engineer can fully explain and verify.
  "Always inject the whole (small) corpus" has zero retrieval logic to get wrong.
- The three `not_publicly_available` gap items (pricing, AI Maturity Index scoring, portal access) are
  always present in context, so the model always has its escalation boundaries in view rather than only
  when a query happens to match them — directly supporting `CLAUDE.md`'s knowledge-integrity requirement.
- No new infrastructure (no vector DB, no embedding calls, no chunking) — one JSON file, loaded once,
  read-only at request time.
- Corpus is small enough that this doesn't trade off answer quality for simplicity; there's no realistic
  scenario at 27 items where filtering would produce a better-informed answer than showing everything.

### Limitations

- Every request pays ~6,200 input tokens even for questions the corpus can't answer at all (e.g. small
  talk). This is a cost/latency tradeoff made deliberately in favor of simplicity and boundary-safety; it's
  cheap enough today to not matter (see cost estimate above).
- No semantic matching means a future corpus with paraphrased/ambiguous item wording could still confuse
  the model at the margins — this is a model-prompting concern rather than a retrieval concern, and is
  mitigated by the system prompt (Phase 4), not by KnowledgeService.
- Doesn't scale indefinitely — see migration triggers below.

### Conditions that would justify migrating

Move to **Option A′** (keyword filtering, still no embeddings) if:
- The corpus grows to roughly 100+ items and full injection starts meaningfully affecting latency/cost, but
  items remain short and structured.

Move to **Option B** (structured + embeddings for specific documents) if:
- Cadre publishes long-form content that doesn't compress into a short structured item — e.g. full
  case-study write-ups, a detailed methodology doc, or transcripts — where chunking and semantic retrieval
  add real value for those specific documents, while FAQs/facts stay structured.

Move to **Option C** (full semantic retrieval) if:
- The corpus grows large and heterogeneous enough (hundreds of documents, mixed structured/unstructured)
  that neither full injection nor simple keyword filtering can reliably surface the right content, and/or
  update frequency becomes high enough to need incremental indexing rather than a single static file.

None of these conditions hold today.

## Acceptance

Per `plan.md`'s original Phase 2 acceptance criteria, this decision was documented prior to implementing
the knowledge layer.

---

## Revised Decision — Semantic Retrieval with FAISS (plan.md Phase 3/4)

### Architecture

```
knowledge item ──(retrieval_text)──▶ embedding model ──▶ vector ──▶ FAISS (IndexFlatIP)
                                                                        │
query ─────────────────────────────▶ embedding model ──▶ vector ──▶ search(top_k)
                                                                        │
                                                          FAISS position → knowledge item ID
                                                                        │
                                                          KnowledgeRepository.get_by_id(id)
                                                                        │
                                                          ranked KnowledgeItem + content (authoritative)
```

- **`KnowledgeRepository`** (`backend/app/knowledge/repository.py`) — loads and validates
  `cadre_knowledge_base.json`, excludes any item whose `status` isn't `verified`/`not_publicly_available`,
  exposes `get_by_id`/`get_all`/`get_escalation_info`. The JSON remains the sole source of truth; nothing
  here is derived.
- **`indexer.py`** — `EmbeddingModel` (wraps the embedding backend) + `build_index(items, embedding_model)`,
  which embeds each item's `retrieval_text` (never `content` or the full JSON object) and builds an
  in-memory FAISS `IndexFlatIP` over L2-normalized vectors (inner product on normalized vectors = cosine
  similarity), plus a FAISS-position → knowledge-item-ID list. Nothing is persisted to disk — the index is
  cheap enough (27 items, small ONNX model) to rebuild from the repository every time a `KnowledgeRetriever`
  is constructed.
- **`retriever.py`** — `KnowledgeRetriever.retrieve(query, top_k)` embeds the query, searches the index, and
  maps hits back to real `KnowledgeItem`s via the repository, returning them ranked with their similarity
  score.

### Embedding model choice: `fastembed` (ONNX) over `sentence-transformers` (torch)

Both are legitimate "local, no hosted vector DB" choices. `fastembed` was chosen because this is a single
CPU-only Docker container: `sentence-transformers` pulls in PyTorch (hundreds of MB, meaningfully slower
cold start), whereas `fastembed` runs on `onnxruntime` with quantized models — a fraction of the install
size and startup cost, with quality that's more than sufficient for a 27-item corpus. Default model:
`BAAI/bge-small-en-v1.5` (384-dim). Configurable via `EMBEDDING_MODEL` — see `backend/app/config.py` — so
swapping models doesn't touch `indexer.py`/`retriever.py`.

### Phase 4 — Retrieval Evaluation results

Eval set: 27 question → expected-knowledge-item-ID(s) pairs in `backend/app/knowledge/evaluation.py`,
covering every category in the corpus. Harness: `backend/scripts/evaluate_retrieval.py` (also exercised as
a regression test in `backend/tests/test_retrieval_evaluation.py`).

| top_k | Hit rate | Notes |
|---|---|---|
| 3 (initial) | 85.2% (23/27) | 4 misses: AI Maturity scoring gap, LLM-selection paraphrase, 2× data-security paraphrases |
| 3 (after `retrieval_text` tuning) | 96.3% (26/27) | Rewrote `retrieval_text` for `llm_selection` and `data_security` to include more paraphrase coverage (e.g. explicitly mentioning "SOC 2", "data protection", "deciding/choosing which AI model") — `content` (the authoritative text sent to the LLM) was **not** changed, only the text used for embedding |
| **5 (final)** | **100% (27/27)** | The three AI Maturity Index items (`overview`/`pillars`/`scoring_gap`) are close semantic neighbors and compete for the same top-3 slots depending on phrasing; top_k=5 resolves this without further prompt-specific tuning |

Off-topic queries ("What's the weather like today?", etc.) scored 0.426–0.476 top similarity, versus
0.592–0.889 for every genuine hit — a clear gap. **`RETRIEVAL_SIMILARITY_THRESHOLD = 0.5`** sits in that gap
and is asserted by test (`test_off_topic_queries_score_below_the_similarity_threshold` /
`test_relevant_queries_score_above_the_similarity_threshold`).

Final configuration (`backend/app/config.py`, all overridable via env vars):

- `EMBEDDING_MODEL = BAAI/bge-small-en-v1.5`
- `RETRIEVAL_TOP_K = 5`
- `RETRIEVAL_SIMILARITY_THRESHOLD = 0.5`

### Limitations of the revised approach

- Retrieval quality depends on `retrieval_text` wording, not just on the embedding model — two items needed
  their `retrieval_text` rewritten (not their factual `content`) to be found reliably. This is expected and
  documented rather than papered over; it's the standard maintenance cost of an embedding-based retriever.
- The FAISS index is rebuilt in-memory at process startup (no persistence). At 27 items with a small ONNX
  model this is sub-second; it would need revisiting (persisted index, incremental updates) at a much larger
  corpus size — see the original analysis's migration triggers above, which still apply to *when this
  becomes necessary for performance*, independent of why it was originally built.
- `RETRIEVAL_SIMILARITY_THRESHOLD` is calibrated against the current 27-item corpus and embedding model; it
  would need re-tuning (via `evaluate_retrieval.py`) if either changes materially.
- The threshold and top_k are not yet wired into a policy/escalation layer that changes chatbot behavior —
  that's `plan.md` Phase 5 ("Knowledge Policy"), not yet implemented.
