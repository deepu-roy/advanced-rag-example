# Facilitator Notes

## Format and timing (suggested, ~2 hours)

| Segment | Time | Notes |
|---|---|---|
| Intro + Codespaces launch | 10 min | Click the badge in the README, wait for the prebuild (should be near-instant if prebuilds are enabled — see below). |
| Lab 1 — Simple RAG | 20 min | Straightforward; most people finish with time to spare. |
| Lab 2 — Query Optimization | 25 min | The three techniques (acronym expansion, splitting, HyDE) can be done in any order; acronym expansion alone is enough to pass the tests. |
| Lab 3 — Hybrid + RRF | 25 min | RRF's math is the trickiest part conceptually; point people at `test_rrf_matches_hand_computed_score` if they're stuck on the formula. |
| Lab 4 — Reranking | 20 min | Shortest lab by code volume; the point is more conceptual (precision vs. recall) than mechanical. |
| Wrap-up: `make scoreboard`, `make compare` | 15 min | Have everyone run these on their own Codespace so the "aha" is personal, not just a slide. |

## Enabling the Codespaces prebuild

Once this repo is pushed to GitHub: **Settings → Codespaces → Set up
prebuild**, targeting the default branch. Without this, the first launch
pulls the devcontainer image and runs `postCreate.sh` live (~3-5 minutes,
mostly model downloads); with it, participants land in a warm environment
in well under a minute. Do this at least an hour before the session so the
prebuild has time to complete.

## Measured reference scores — read the category table first

Produced by `make verify` (`RAG_IMPL=solutions RAG_LLM=offline`), against
the 20-query gold set in `data/gold_queries.yaml`.

**Do not lead with the overall table in the session.** It averages every
stage's genuinely-fixed queries together with ~7 "control" queries every
pipeline already gets right, which visually flattens a real, targeted fix
into what looks like a shrug:

| Pipeline | Recall@5 | MRR | nDCG@5 |
|---|---|---|---|
| 01 simple RAG | 1.000 | 0.892 | 0.916 |
| 02 query optimization | 1.000 | 0.938 | 0.953 |
| 03 hybrid + RRF | 0.975 | 0.925 | 0.925 |
| 04 reranking | 0.975 | 0.975 | 0.962 |

**Lead with this instead** — `make scoreboard`'s second table, MRR grouped
by which stage a query actually targets (`>` marks a category's own
stage):

| query category | 01 simple | 02 query-opt | 03 hybrid+RRF | 04 rerank |
|---|---|---|---|---|
| lab1 (control) | 1.000 | 1.000 | 1.000 | 1.000 |
| lab2 targets | **0.833** → **1.000** | | 0.875 | 0.875 |
| lab3 targets | 0.667 | 0.750 → **1.000** | | 1.000 |
| lab4 targets | 0.917 | 0.917 | 0.833 → **1.000** | |

Read down each row, not across the whole table: every category's MRR
jumps to (or holds) its ceiling of 1.0 at *exactly* the stage built to fix
it, and doesn't reliably move at any other stage. That's the actual
claim this lab is making — not "the aggregate improves," but "each
technique fixes the specific failure it targets." Say this explicitly:
**the overall table is what a real system's users would experience
(mostly fine, incrementally better); the category table is what proves
each lab's code is actually doing its job.** Both are honest; they answer
different questions.

nDCG dips very slightly at Lab 3 in the overall table, for the reason
below.

### Why the lab2-category and Lab 3's overall numbers dip instead of only going up

One query — *"For a non-employee who needs remote network access, what
software do they install, and whose sign-off do they need first?"* —
needs **two** documents (a VPN policy and an access-approval policy) to
get full credit. Lab 2's HyDE + sub-question splitting handles this by
decomposing the question before searching. Lab 3's `retrieve()` is built
directly on Lab 1's raw dense search plus BM25 — it does **not** inherit
Lab 2's decomposition — so this one compound question loses ground the
moment you move to Lab 3: its Recall@5 drops from 1.0 to 0.5, which is
exactly 0.05 off the 20-query overall aggregate (one query = 1/20 = 0.05
of the total) and is the entire reason the lab2-category row in the table
above reads 0.875 instead of holding at 1.000 for Labs 3 and 4.

This is real, not a corpus bug, and worth saying out loud in the session:
**these techniques are not automatically cumulative.** Each lab isolates
one improvement in the pipeline it's built on top of (Lab 3 builds on Lab
1's dense search, not Lab 2's query rewriting), so a production system
that wants every benefit at once has to deliberately combine them — e.g.
decompose the query *and* hybridize *and* rerank — rather than assuming
each new technique automatically inherits everything before it. The test
suite's cross-lab checks (`test_gold_set_does_not_regress_*`) allow a 0.05
tolerance for exactly this reason, spelled out in each test file.

## Genuinely-verified "aha" moments to point out live

Every one of these was checked against the actual reference pipeline, not
assumed — see `data/gold_queries.yaml` for the full set and comments.

- **Lab 2 fixes**: `"What's the process if a delivery isn't OTIF?"` —
  naive search ranks the right doc 3rd; query expansion puts it 1st.
  `make compare Q="What's the process if a delivery isn't OTIF?"`
- **Lab 3 fixes**: `"E-4021 cause"` — dense search confidently picks the
  *wrong* one of three near-identical error-code references; BM25's exact
  match breaks the tie correctly, and the fused hybrid result agrees.
  `make compare Q="E-4021 cause"`
- **Lab 4 fixes**: `"How much paid time off do new parents get after an
  adoption?"` — hybrid retrieval already finds the right policy but ranks
  it 2nd; reranking moves it to 1st with a large, confident score gap
  (compare the top-2 scores in the Lab 4 section of `make compare` output
  — the gap is much larger than in Lab 3's fused scores, which is the
  point: the cross-encoder is far more decisive than fusion alone).
  `make compare Q="How much paid time off do new parents get after an adoption?"`

## If Ollama isn't working for someone

Every lab and every test works with `RAG_LLM=offline` (the test suite
forces this automatically). If a participant's Ollama pull failed during
setup (flaky network, corporate proxy), they can:
1. Retry: `ollama pull qwen2.5:1.5b-instruct`
2. Or just keep working — `RAG_LLM` falls back to offline automatically
   whenever the configured provider is unreachable, with a printed
   warning, not a crash. Lab 2's HyDE technique still runs; it just uses
   the deterministic offline template instead of a real generated
   paragraph. The retrieval lessons are unaffected either way.
3. Or point at any OpenAI-compatible endpoint your org has (Azure OpenAI,
   a gateway, etc.):
   `RAG_LLM=openai RAG_LLM_BASE_URL=... RAG_LLM_API_KEY=... RAG_LLM_MODEL=...`

## Scope note

The original plan sketched a ~45-document corpus; this ships with 31.
Every gold-set query and every "aha" moment above was empirically verified
against the actual embedding and reranking models (not assumed from
corpus design alone — an early draft's "traps" mostly didn't trip up
`all-MiniLM-L6-v2`, which is stronger than a quick read of the docs would
suggest). 31 well-targeted documents with verified failure modes teach the
four techniques more reliably than 45 documents with unverified ones.
Extending the corpus following the same pattern (see `data/corpus/*.md`
frontmatter and `data/gold_queries.yaml`'s comments) is straightforward if
you want more workshop material later — verify any new gold query against
the reference pipelines the same way before trusting it.
