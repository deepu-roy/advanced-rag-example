"""Lab 3 — Hybrid Retrieval + Reciprocal Rank Fusion (RRF) — reference
solution.

See labs/lab03_hybrid_rrf.py for the exercise version of this file, with
the teaching comments and NotImplementedError stubs.
"""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from ragkit.chunking import chunk_documents
from ragkit.corpus import load_corpus
from ragkit.types import Chunk, Hit
from solutions import lab01_simple_rag as lab01

# Words and hyphenated identifiers (e.g. "e-4021", "on-time-in-full"), with
# surrounding punctuation stripped. Plain `.lower().split()` would leave a
# trailing "?" or ":" glued to the last word of a sentence, which silently
# breaks exact-token matches on identifiers like "E-4021?" vs "E-4021" —
# exactly the kind of match BM25 exists to get right.
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())


def build_bm25(chunks: list[Chunk]) -> BM25Okapi:
    return BM25Okapi([_tokenize(c.text) for c in chunks])


_bm25: BM25Okapi | None = None
_bm25_chunks: list[Chunk] | None = None


def _get_bm25() -> tuple[BM25Okapi, list[Chunk]]:
    global _bm25, _bm25_chunks
    if _bm25 is None:
        _bm25_chunks = chunk_documents(load_corpus())
        _bm25 = build_bm25(_bm25_chunks)
    return _bm25, _bm25_chunks


def bm25_search(query: str, k: int = 5) -> list[Hit]:
    bm25, chunks = _get_bm25()
    if not chunks:
        return []
    scores = bm25.get_scores(_tokenize(query))
    ranked_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
    return [Hit(chunk=chunks[i], score=float(scores[i])) for i in ranked_idx]


def reciprocal_rank_fusion(
    rankings: list[list[str]], k_const: int = 60
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item_id in enumerate(ranking, start=1):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k_const + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def retrieve(query: str, k: int = 5) -> list[Hit]:
    fetch = max(k * 4, 20)
    dense_hits = lab01.retrieve(query, k=fetch)
    sparse_hits = bm25_search(query, k=fetch)

    by_id: dict[str, Hit] = {h.chunk.id: h for h in dense_hits}
    by_id.update({h.chunk.id: h for h in sparse_hits})

    fused = reciprocal_rank_fusion(
        [[h.chunk.id for h in dense_hits], [h.chunk.id for h in sparse_hits]]
    )
    return [Hit(chunk=by_id[chunk_id].chunk, score=score) for chunk_id, score in fused[:k]]


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "What causes error E-4021?"
    for hit in retrieve(query, k=5):
        print(f"  [{hit.score:.4f}] {hit.chunk.doc_title}")
