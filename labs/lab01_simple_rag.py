"""Lab 1 — Simple (naive) RAG.

The baseline everyone starts from: embed the corpus once, embed the query,
find the nearest chunks by cosine similarity, stuff them into a prompt,
done. This lab has exactly one retrieval trick: none. It exists so the
later labs have something to visibly improve on.

Before writing any code, try this:

    python -m ragkit.compare "What's the process if a delivery isn't OTIF?"

(It'll say "not implemented yet" for every lab until you fill them in —
that's expected. Come back to it once lab01 works, and again after each
later lab, to watch the answer change.)

WHAT YOU'RE IMPLEMENTING
-------------------------
1. build_index(chunks)   — embed every chunk, wrap the vectors in a FAISS
                            index you can search by cosine similarity.
2. retrieve(query, k)    — embed the query the same way, search the index,
                            turn the FAISS results back into Hit objects.
3. answer(query, k)      — retrieve top-k chunks, stuff them into a prompt,
                            ask the LLM to answer using only that context.

Everything you need is already built for you in `ragkit`:
  - ragkit.corpus.load_corpus()            -> list[Document]
  - ragkit.chunking.chunk_documents(docs)  -> list[Chunk]
  - ragkit.embeddings.EmbeddingModel()     -> .encode(texts) -> np.ndarray,
        shape (n, dim), already L2-normalized
  - ragkit.llm.get_llm()                   -> .complete(prompt) -> str
  - ragkit.types.Hit(chunk, score)

Run `pytest tests/test_lab01_simple_rag.py -v` to check your work, or
`python -m labs.lab01_simple_rag "your question"` to try it interactively.
"""
from __future__ import annotations

import faiss

from ragkit.chunking import chunk_documents
from ragkit.corpus import load_corpus
from ragkit.embeddings import EmbeddingModel
from ragkit.llm import get_llm  # noqa: F401 - used once you implement answer()
from ragkit.types import Chunk, Hit

_embedder = EmbeddingModel()


def build_index(chunks: list[Chunk]) -> faiss.Index:
    """Embed every chunk's text and return a FAISS index over the vectors.

    HINT: because EmbeddingModel().encode() returns L2-normalized vectors,
    inner product (faiss.IndexFlatIP) is equivalent to cosine similarity —
    you don't need to normalize anything yourself.

    HINT: FAISS only knows about row positions (0, 1, 2, ...), not your
    chunk ids. Whoever calls build_index() needs to keep the same `chunks`
    list around to map a result row back to a Chunk — that's exactly what
    `_get_index()` below does; you don't need to store the mapping yourself.
    """
    raise NotImplementedError("build_index: embed chunks and build a faiss.IndexFlatIP over them")


# Module-level cache: build the index once per process, not once per query.
# (Given — you don't need to change this.)
_index: faiss.Index | None = None
_indexed_chunks: list[Chunk] | None = None


def _get_index() -> tuple[faiss.Index, list[Chunk]]:
    global _index, _indexed_chunks
    if _index is None:
        _indexed_chunks = chunk_documents(load_corpus())
        _index = build_index(_indexed_chunks)
    return _index, _indexed_chunks


def retrieve(query: str, k: int = 5) -> list[Hit]:
    """Embed `query`, search the index, and return the top-k chunks as
    Hits, best (highest score) first.

    HINT: call `_get_index()` to get `(index, chunks)`.

    HINT: FAISS's `index.search(query_vec, k)` takes a 2D array (even for a
    single query — shape (1, dim)) and returns `(scores, indices)`, each
    shaped (1, k). A returned index of -1 means "no result" (only possible
    if the index has fewer than k vectors) — skip those.
    """
    raise NotImplementedError("retrieve: embed the query and search the FAISS index")


_ANSWER_PROMPT = """Answer the question using ONLY the context below. If the
context doesn't contain the answer, say so plainly.

Context:
{context}

Question: {question}
Answer:"""


def answer(query: str, k: int = 5) -> str:
    """Retrieve top-k chunks and ask the LLM to answer using only that
    context. This is the "G" in RAG — everything before this point was
    retrieval; this is generation.

    HINT: build a `context` string from the retrieved chunks (their text,
    maybe with their doc title as a label), fill `_ANSWER_PROMPT`, and pass
    it to `get_llm().complete(prompt)`.
    """
    raise NotImplementedError("answer: retrieve context, fill _ANSWER_PROMPT, call get_llm()")


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "What is the bereavement leave policy?"
    print("Retrieved:")
    for hit in retrieve(query, k=5):
        print(f"  [{hit.score:.3f}] {hit.chunk.doc_title}")
    print("\nAnswer:")
    print(answer(query, k=5))
