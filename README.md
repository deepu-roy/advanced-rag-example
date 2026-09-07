# Advanced RAG Lab

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/deepu-roy/advanced-rag-example?quickstart=1)

A hands-on lab where naive RAG evolves into a real retrieval pipeline, one
technique at a time — **query optimization → hybrid retrieval + Reciprocal
Rank Fusion → cross-encoder reranking** — over a small fictional freight
company's internal docs. Every stage's improvement is a measured number,
not a vibe: a 20-query gold set with known-correct answers, scored by
Recall@5 / MRR / nDCG@5, every improvement checked against the actual
reference pipeline before being written down as a lesson.

Runs entirely in [GitHub Codespaces](https://github.com/features/codespaces)
with zero local setup — no API key required (an [Ollama](https://ollama.com)
model runs inside the Codespace; every lab and test also has a fully
offline fallback).

**New here? Open [`presentation.html`](presentation.html) first** — a
self-contained, animated briefing (no server needed, just open it in a
browser) covering Codespaces/devcontainers, and each lab's technique with
interactive, real-data demos: a live cost calculator, a Reciprocal Rank
Fusion calculator, and a bi-encoder vs. cross-encoder animation, among
others.

## Quickstart

Click **Code → Codespaces → Create codespace** (or the badge above), wait
for setup to finish, then:

```bash
python -m ragkit.compare "What causes error E-4021?"
```

Every pipeline says "not implemented yet" right now — that's expected. Go
implement `labs/lab01_simple_rag.py` and run the same command again to see
it start answering. **Start here: [docs/LAB_GUIDE.md](docs/LAB_GUIDE.md).**

```bash
make test                # run the fixed tests against your labs/ code
make test RAG_IMPL=solutions   # ...or against the reference solution
make scoreboard           # Recall@5 / MRR / nDCG@5 for all four pipelines
make compare Q="your question here"
```

## The four labs

| # | Lab | File | The lesson |
|---|---|---|---|
| 1 | Simple RAG | [`labs/lab01_simple_rag.py`](labs/lab01_simple_rag.py) | Embed, search, generate — the baseline. |
| 2 | Query Optimization | [`labs/lab02_query_optimization.py`](labs/lab02_query_optimization.py) | Rewrite the question before you embed it. |
| 3 | Hybrid Retrieval + RRF | [`labs/lab03_hybrid_rrf.py`](labs/lab03_hybrid_rrf.py) | Combine dense (semantic) and BM25 (lexical) search. |
| 4 | Reranking | [`labs/lab04_reranking.py`](labs/lab04_reranking.py) | Precision over recall: a cross-encoder reorders the pool. |

Each `labs/*.py` file is a heavily-commented stub — write the code
yourself, or drive GitHub Copilot in the editor; either way, the fixed
tests in `tests/` are the contract you're implementing against. Reference
solutions live in `solutions/` if you want to compare or get unstuck.

## How it's built

```
ragkit/      given infrastructure: corpus loading, chunking, embeddings,
             LLM providers, metrics, evaluation, the compare/scoreboard CLIs
labs/        <- you write these four files
solutions/   reference implementations (same files, filled in)
tests/       fixed tests — the contract; don't edit these
data/        the corpus (~30 docs) and the 20-query gold evaluation set
docs/        LAB_GUIDE.md (start here) and FACILITATOR.md (numbers, timing)
```

`ragkit.evaluate` scores any `retrieve(query, k) -> list[Hit]` function
against `data/gold_queries.yaml`; `ragkit.compare` runs one query through
all four pipelines side by side; `ragkit.scoreboard` records and renders
the cross-pipeline comparison table. See
[docs/FACILITATOR.md](docs/FACILITATOR.md) for the actual measured
numbers, verified "aha" example queries, and workshop timing.

## Running without Codespaces

Any machine with Python 3.11+ works:

```bash
python -m venv .venv && source .venv/bin/activate
make setup
make test
```

An LLM is only needed for Lab 2's HyDE technique and for generating final
answers — everything else, including all four labs' retrieval logic and
every fixed test, runs with zero network access via `RAG_LLM=offline`
(the test suite sets this automatically). To use a real model instead of
the offline fallback:

- **Ollama** (default; what the devcontainer sets up automatically):
  install it, run `ollama pull qwen2.5:1.5b-instruct`, and `RAG_LLM=ollama`
  (the default) picks it up at `http://localhost:11434/v1`.
- **Any OpenAI-compatible endpoint** — Azure OpenAI, a corporate gateway,
  OpenRouter, etc.:
  ```bash
  export RAG_LLM=openai
  export RAG_LLM_BASE_URL=https://your-endpoint/v1
  export RAG_LLM_API_KEY=...
  export RAG_LLM_MODEL=...
  ```
