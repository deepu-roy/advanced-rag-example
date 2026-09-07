"""Lab 4 — Reranking with a Cross-Encoder — reference solution.

See labs/lab04_reranking.py for the exercise version of this file, with
the teaching comments and NotImplementedError stubs.
"""
from __future__ import annotations

from ragkit.reranker import CrossEncoderReranker
from ragkit.types import Hit
from solutions import lab03_hybrid_rrf as lab03

_reranker = CrossEncoderReranker()

CANDIDATE_POOL_SIZE = 30


def rerank(query: str, candidates: list[Hit], top_n: int) -> list[Hit]:
    if not candidates:
        return []
    scores = _reranker.score(query, [c.chunk.text for c in candidates])
    reranked = [Hit(chunk=c.chunk, score=score) for c, score in zip(candidates, scores)]
    reranked.sort(key=lambda h: h.score, reverse=True)
    return reranked[:top_n]


def retrieve(query: str, k: int = 5) -> list[Hit]:
    pool = lab03.retrieve(query, k=CANDIDATE_POOL_SIZE)
    return rerank(query, pool, top_n=k)


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "How much bereavement leave do I get?"
    for hit in retrieve(query, k=5):
        print(f"  [{hit.score:7.3f}] {hit.chunk.doc_title}")
