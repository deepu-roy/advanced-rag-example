# Lab Guide

Four labs, each one file in `labs/`, each building on the last. Every lab
has the same shape: a short "what's broken" story, the technique that
fixes it, and a stub file with `NotImplementedError`s and hints for you to
fill in. Fixed tests in `tests/` (which you don't edit) tell you when
you've got it right.

You can write the code yourself, or drive GitHub Copilot in the editor —
either way, the tests are the contract. `RAG_IMPL=solutions pytest` runs
the same tests against a working reference if you want to compare, or get
unstuck.

Before starting, run `make setup` once, then try:

```bash
python -m ragkit.compare "What causes error E-4021?"
```

Every lab says "not implemented yet" right now. Come back to this command
after each lab — watching the same query's answer change *is* the lab.

The corpus is a small fictional freight company's internal docs
(`data/corpus/`, ~30 files) with a handful of deliberately gnarly details:
an acronym the docs never spell out, three near-identical error-code
references that differ in one token, six near-duplicate leave policies.
These aren't edge cases — they're the everyday reasons naive RAG gives
wrong or badly-ranked answers.

## Lab 1 — Simple RAG (`labs/lab01_simple_rag.py`)

**The setup.** Embed every chunk of the corpus once, embed the query the
same way, return the nearest chunks by cosine similarity, stuff them into
a prompt. No tricks. This is what most people mean by "RAG" on day one,
and it works remarkably well for direct questions.

**What you'll build.** `build_index()` (embed + wrap in a FAISS index),
`retrieve()` (embed the query, search, map back to chunks), `answer()`
(retrieve + prompt + call the LLM).

**Check your work:** `pytest tests/test_lab01_simple_rag.py -v`

## Lab 2 — Query Optimization (`labs/lab02_query_optimization.py`)

**The failure.** Ask *"What's the process if a delivery isn't OTIF?"* and
Lab 1 ranks the right document 3rd — behind a warehouse-safety doc and the
company glossary, both of which happen to share more surface vocabulary
with the question than the actual answer does. The runbook that answers
this never uses the acronym "OTIF" at all — it says "on-time-in-full"
throughout.

**The fix.** Don't just embed the question as asked — rewrite it first:
- **Acronym expansion**: look up the acronym in a glossary, add a variant
  that spells it out.
- **Sub-question splitting**: a compound question ("X, and who approves
  Y?") is really two questions; search each separately.
- **HyDE**: ask the LLM to *write* a plausible answer, then search using
  that answer's embedding — a fabricated answer often lands closer to the
  real document's vocabulary than the bare question does.

Search with every variant, merge results, keep each chunk's best score.

**Check your work:** `pytest tests/test_lab02_query_optimization.py -v`

## Lab 3 — Hybrid Retrieval + RRF (`labs/lab03_hybrid_rrf.py`)

**The failure.** The corpus has three near-identical "error code
reference" documents — one per subsystem — that share almost all their
framing language ("This reference lists the error codes raised by the ___
subsystem..."). Ask about a specific code, `E-4021`, and dense search
picks the *wrong* subsystem document: all three are so semantically
similar that the one distinguishing detail — the exact code string — gets
outweighed by the shared boilerplate.

**The fix.** BM25 (classic lexical/keyword search) doesn't care about
semantic similarity — it cares about exact token matches, weighted by how
rare that token is across the corpus. `E-4021` is rare and appears
verbatim in exactly one document, so BM25 nails it. Reciprocal Rank Fusion
(RRF) combines BM25's ranking with the dense ranking from Lab 1, so you
get dense search's strength on paraphrase *and* BM25's strength on exact
identifiers, without having to pick one.

**Check your work:** `pytest tests/test_lab03_hybrid_rrf.py -v`

## Lab 4 — Reranking (`labs/lab04_reranking.py`)

**The failure.** Ask *"How much paid time off do new parents get after an
adoption?"* Hybrid retrieval (Lab 3) already finds the right document —
it's in the top-5 — but ranks it 2nd, behind a different leave policy that
shares more surface wording with the question. The document was *found*;
it just wasn't ranked first.

**The fix.** A cross-encoder reranker looks at the query and a candidate
chunk *together* in one pass (instead of embedding each separately, which
is what every previous lab does), which makes it much better at judging
"is this actually the best answer" even when several candidates look
similar from a distance. It's too slow to run over the whole corpus, so it
runs *after* retrieval: over-fetch a wide candidate pool cheaply (Lab 3),
then spend the expensive model only on reordering that pool.

This is the stage where **Recall@5 barely moves** — the right chunk was
already in the pool — but **MRR and nDCG jump**, because precision, not
recall, is what reranking actually buys you. Watch the scoreboard for
this: if you only look at Recall@5, Lab 4 will look like it did nothing.

**Check your work:** `pytest tests/test_lab04_reranking.py -v`

## After all four

```bash
make scoreboard   # measured Recall@5 / MRR / nDCG@5 for every pipeline
make compare Q="How much paid time off do new parents get after an adoption?"
```

See `docs/FACILITATOR.md` for the full measured numbers and an honest note
on where the improvement curve isn't perfectly smooth — and why that's a
real lesson too, not a corpus bug.
