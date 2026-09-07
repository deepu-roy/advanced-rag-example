"""Lab 4 — Reranking with a Cross-Encoder.

Dense + BM25 + RRF (lab 3) is usually good at getting the right chunk
*somewhere* in the top 20-30 candidates — but not necessarily at #1. A
cross-encoder reranker looks at the (query, candidate) pair *together*
(instead of embedding each separately, like lab01's dense retriever does)
and scores relevance directly. It's too slow to run over the whole corpus,
which is why it goes *after* retrieval, not instead of it: over-fetch a
wide candidate pool cheaply, then spend the expensive model only on
reordering that pool.

Verified in this corpus: hybrid retrieval already puts the right document
in the top-5 pool but not 1st; reranking moves it to 1st — Recall@5 barely
moves (the document was already "found"), but MRR/nDCG jump because the
document is now actually on top.

    python -m ragkit.compare "How much paid time off do new parents get after an adoption?"

WHAT YOU'RE IMPLEMENTING
-------------------------
1. rerank(query, candidates, top_n) -> list[Hit]   — score every candidate
   with the cross-encoder, keep the best top_n, sorted by that new score
2. retrieve(query, k)                              — over-fetch a wide
   pool via lab03's hybrid retrieve, then rerank down to k

Everything you need:
  - ragkit.reranker.CrossEncoderReranker().score(query, texts) -> list[float],
    one score per text, same order in as out — higher is more relevant
  - labs.lab03_hybrid_rrf.retrieve — the candidate pool, reused as-is
"""
from __future__ import annotations

from labs import lab03_hybrid_rrf as lab03  # noqa: F401 - used once you implement retrieve()
from ragkit.reranker import CrossEncoderReranker
from ragkit.types import Hit

_reranker = CrossEncoderReranker()

CANDIDATE_POOL_SIZE = 30


def rerank(query: str, candidates: list[Hit], top_n: int) -> list[Hit]:
    """Score every candidate against `query` with the cross-encoder and
    return the best top_n, sorted by that new score (descending).

    HINT: `_reranker.score(query, [c.chunk.text for c in candidates])`
    returns one float per candidate, in the same order — zip it back up
    with `candidates` to build new Hits carrying the cross-encoder score.
    """
    raise NotImplementedError("rerank: score candidates with the cross-encoder, keep top_n")


def retrieve(query: str, k: int = 5) -> list[Hit]:
    """Over-fetch CANDIDATE_POOL_SIZE candidates from lab03's hybrid
    retrieval, then rerank down to the final top-k."""
    raise NotImplementedError("retrieve: over-fetch via lab03.retrieve, then rerank(...)")


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "How much paid time off do new parents get after an adoption?"
    for hit in retrieve(query, k=5):
        print(f"  [{hit.score:7.3f}] {hit.chunk.doc_title}")
