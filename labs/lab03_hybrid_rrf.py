"""Lab 3 — Hybrid Retrieval + Reciprocal Rank Fusion (RRF).

Dense embeddings are great at *meaning* and can be surprisingly bad at
*exact tokens* when several documents are otherwise very similar: three
near-identical "error code reference" documents, differing only in which
codes they list, can genuinely confuse a dense retriever into picking the
wrong one. BM25 (classic sparse/lexical search) is the opposite: great at
exact tokens, blind to paraphrase. This lab runs both and fuses their
rankings with RRF, so each covers the other's blind spot.

Verified in this corpus: dense-only search gets this wrong (it picks the
billing error-code doc instead of the manifest one); BM25's exact match on
the literal code string breaks the tie correctly.

    python -m ragkit.compare "E-4021 cause"

RRF formula, for a chunk id `d` across a set of rankings:

    score(d) = sum, over every ranking that contains d, of 1 / (k_const + rank(d))

`rank(d)` is 1-based position in that ranking; `k_const` (usually 60)
softens the impact of very high ranks so one list can't dominate purely by
being the only one that ranks something #1.

WHAT YOU'RE IMPLEMENTING
-------------------------
1. build_bm25(chunks)                    — a rank_bm25.BM25Okapi index
2. bm25_search(query, k)                 — lexical search over that index
3. reciprocal_rank_fusion(rankings, k_const=60) -> list[(chunk_id, score)],
                                            sorted by fused score descending
4. retrieve(query, k)                    — dense (lab01) + sparse (bm25),
                                            fused by RRF

Everything you need:
  - rank_bm25.BM25Okapi(tokenized_corpus) — build with a list of token
    lists, one per chunk (see `_tokenize` below, given for you: it keeps
    hyphenated identifiers like "e-4021" intact and strips punctuation, so
    "E-4021?" in a query still matches "E-4021" in a document)
  - bm25.get_scores(tokenized_query) -> array of one float per chunk, in
    the same order as the corpus you built the index with
  - labs.lab01_simple_rag.retrieve — the dense side, reused as-is
"""
from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from labs import lab01_simple_rag as lab01  # noqa: F401 - used once you implement retrieve()
from ragkit.chunking import chunk_documents
from ragkit.corpus import load_corpus
from ragkit.llm import answer_from_hits
from ragkit.types import Chunk, Hit

# Words and hyphenated identifiers (e.g. "e-4021", "on-time-in-full"), with
# surrounding punctuation stripped. (Given.)
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_PATTERN.findall(text.lower())


def build_bm25(chunks: list[Chunk]) -> BM25Okapi:
    """Tokenize every chunk's text with `_tokenize` and build a BM25Okapi
    index over the resulting token lists."""
    raise NotImplementedError("build_bm25: tokenize each chunk and build a BM25Okapi index")


# Module-level cache, same pattern as lab01's _get_index(). (Given.)
_bm25: BM25Okapi | None = None
_bm25_chunks: list[Chunk] | None = None


def _get_bm25() -> tuple[BM25Okapi, list[Chunk]]:
    global _bm25, _bm25_chunks
    if _bm25 is None:
        _bm25_chunks = chunk_documents(load_corpus())
        _bm25 = build_bm25(_bm25_chunks)
    return _bm25, _bm25_chunks


def bm25_search(query: str, k: int = 5) -> list[Hit]:
    """Score `query` against the BM25 index and return the top-k chunks as
    Hits, best first.

    HINT: `bm25.get_scores(_tokenize(query))` returns one float per chunk,
    in the same order as `_get_bm25()`'s chunk list. Sort chunk indices by
    that score, descending, and take the top-k.
    """
    raise NotImplementedError("bm25_search: tokenize the query, score with bm25.get_scores, sort")


def reciprocal_rank_fusion(
    rankings: list[list[str]], k_const: int = 60
) -> list[tuple[str, float]]:
    """Fuse multiple ranked lists of chunk ids into one, sorted by fused
    score descending. `rankings[i]` is a list of chunk ids, best first.

    HINT: accumulate scores in a dict: for each ranking, for each
    (1-based) rank and chunk_id, add `1 / (k_const + rank)` to that id's
    running total. A chunk id that never appears in a ranking simply
    contributes nothing from that ranking.
    """
    raise NotImplementedError("reciprocal_rank_fusion: sum 1/(k_const + rank) across rankings")


def retrieve(query: str, k: int = 5) -> list[Hit]:
    """Run dense (lab01) and sparse (bm25) search, fuse their rankings with
    RRF, and return the top-k as Hits. Hit.score is the fused RRF score.

    HINT: fetch more than k from each side (e.g. `max(k * 4, 20)`) before
    fusing — RRF needs a wide-enough pool to have something to fuse.

    HINT: you'll need a way to map a fused chunk_id back to a Chunk to
    build the final Hits — keep a dict from chunk_id to Hit as you collect
    the dense and sparse results.
    """
    raise NotImplementedError("retrieve: fuse lab01.retrieve and bm25_search with RRF")


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "What's the process if a delivery isn't OTIF?"
    print("Retrieved:")
    hits = retrieve(query, k=5)
    for hit in hits:
        print(f"  [{hit.score:.4f}] {hit.chunk.doc_title}")
    print("\nAnswer:")
    print(answer_from_hits(query, hits))
