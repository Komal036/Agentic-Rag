# Agentic Self-Correcting RAG

A retrieval-augmented generation system that knows when it's wrong.

Standard RAG retrieves once and generates once — if the retrieval is bad, it still
confidently answers using irrelevant context. This system adds a self-correction
loop: it grades its own retrieval, rewrites queries when retrieval is weak, falls
back to web search when the local knowledge base is insufficient, checks its own
generated answer for hallucination, and explicitly abstains ("I don't have enough
information") instead of guessing.

Inspired by two papers:
- **Self-RAG** (Asai et al., 2023) — self-reflective grading at each pipeline stage
- **Corrective RAG / CRAG** (Yan et al., 2024) — corrective action based on retrieval quality (refine / web search / combine)

This project reimplements the *ideas* from both papers using prompted LLM calls as
graders (not fine-tuned reflection tokens), orchestrated as a LangGraph state machine.

---

## Architecture

```
                                Query
                                  │
                                  ▼
                          ┌───────────────┐
                          │    Router     │  skip retrieval for greetings/chit-chat
                          └───────┬───────┘
                     ┌────────────┴────────────┐
                 direct                     retrieve
                    │                           │
                    ▼                           ▼
              Direct Answer              ┌──────────────┐
                    │                    │   Retrieve   │◄────────────┐
                    ▼                    │ (dense+BM25  │             │
                   END                   │  +rerank)    │             │
                                          └──────┬───────┘             │
                                                  ▼                    │
                                          ┌──────────────────┐         │
                                          │ Retrieval Grader  │         │
                                          │ sufficient /      │         │
                                          │ insufficient /    │         │
                                          │ off_topic /       │         │
                                          │ rewrite           │         │
                                          └────────┬──────────┘         │
                          ┌───────────────┬────────┴────────┐          │
                     sufficient      insufficient/       off_topic /   │
                          │           rewrite            retries       │
                          │              │              exhausted      │
                          │              └──────────────────┘          │
                          │              rewrite query, retry ─────────┘
                          │
                          │                    ┌──────────────────┐
                          │                    │  Web Search       │
                          │◄───────────────────┤  Fallback (Tavily)│
                          ▼                    └──────────────────┘
                  ┌───────────────┐
                  │   Generate     │  answer + citations
                  └───────┬────────┘
                          ▼
                  ┌───────────────────┐
                  │ Hallucination      │  is the answer grounded
                  │ Grader             │  in the retrieved context?
                  └─────────┬──────────┘
                  ┌─────────┴──────────┐
             grounded              not grounded
                  │                     │
                  ▼                     ▼
          ┌───────────────┐      regenerate (budget-limited)
          │ Answer Grader  │      or → Abstain
          │ does it answer │
          │ the question?  │
          └───────┬────────┘
          ┌────────┴────────┐
         yes                no (loop back to Retrieve, budget-limited)
          │
          ▼
        Final Answer
```

**The loop is bounded** by:
- `max_iterations` — hard cap on retrieval attempts
- `timeout_seconds` — wall-clock cap regardless of iteration count
- `min_new_chunks_per_iteration` — stuck-loop detection: if a rewritten query
  returns no new information, stop instead of looping forever
- `max_local_retries_before_web_fallback` — how many local retries before
  escalating to web search

---

## Why this is harder than plain RAG (and what it actually solves)

Plain RAG has three blind spots this system addresses:

1. **No way to detect bad retrieval** — plain RAG generates from whatever it retrieved,
   good or bad. → Fixed by the **retrieval grader**.
2. **No fallback when the knowledge base lacks the answer** — plain RAG will still
   generate *something*, often leaning on the model's own unverified background
   knowledge. → Fixed by the **web search fallback**.
3. **No concept of "I don't know"** — plain RAG always answers confidently.
   → Fixed by the **abstention mechanism**.

The hallucination grader is *not* a claim that hallucination is "solved" — it's one
more imperfect LLM-based check layered on top of the above three structural fixes.

---

## Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Orchestration | LangGraph | Native support for conditional loops/cycles |
| LLM | Anthropic Claude (Sonnet for generation, Haiku for grading) | Cheap model for classification-style grading, stronger model for generation |
| Embeddings | sentence-transformers (`bge-small-en-v1.5`) | Free, local, no per-call cost |
| Vector DB | ChromaDB | Simple local persistence, good for a project scope |
| Sparse retrieval | `rank_bm25` | Keyword/exact-match retrieval, complements dense embeddings |
| Reranker | Cross-encoder (`bge-reranker-base`) | Reorders fused results by true query relevance |
| Web fallback | Tavily API | Search API purpose-built for LLM agents |
| Backend | FastAPI | Serves the graph as an API |
| Evaluation | RAGAS | Standard RAG metrics: faithfulness, context precision/recall |

---

## Project Structure (grows phase by phase — not all present yet)

```
agentic-rag/
├── data/                    # source documents (PDFs, etc.)
├── ingestion/
│   ├── loaders.py            # Phase 1: read files off disk -> raw text
│   └── chunking.py           # Phase 1: split raw text into overlapping chunks
├── retrieval/                 # Phase 2-3: vector store, BM25, fusion, reranker
├── graders/                   # Phase 4-7: router, retrieval/hallucination/answer graders, rewriter, generator
├── tools/                     # Phase 6: web search fallback
├── graph/                     # Phase 8: LangGraph state machine
├── eval/                      # Phase 9: benchmark + naive-vs-agentic comparison
├── api/                       # Phase 10: FastAPI app
├── config.py                  # tunable constants (added when first needed)
├── .env                        # API keys (never committed)
├── requirements.txt
└── README.md
```

---

## Build Roadmap

| Phase | What it builds | Key concept |
|---|---|---|
| 0 | Repo, env, dependencies, dataset | Project setup |
| 1 | Document loading + chunking | Why chunk size/overlap matters |
| 2 | Plain vector retrieval + generation | Baseline RAG — the "before" |
| 3 | Hybrid retrieval (dense + BM25 + rerank) | Why embeddings alone aren't enough |
| 4 | Retrieval grader | LLM-as-judge, structured output |
| 5 | Query rewriting + iteration loop | Loop budgets, stuck-loop detection |
| 6 | Web search fallback | CRAG's corrective action |
| 7 | Hallucination + answer graders, abstention | Groundedness, honest failure |
| 8 | Port to LangGraph | State machines, conditional edges |
| 9 | Evaluation harness | Naive vs agentic, quantified proof |
| 10 | UI + polish | Reasoning-trace demo panel |

---

## Setup

```bash
conda create -n agentic-rag python=3.11 -y
conda activate agentic-rag
pip install -r requirements.txt
cp .env.example .env       # add ANTHROPIC_API_KEY, TAVILY_API_KEY
```

---

