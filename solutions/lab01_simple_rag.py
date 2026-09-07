"""Lab 1 — Simple (naive) RAG — reference solution.

See labs/lab01_simple_rag.py for the exercise version of this file, with
the teaching comments and NotImplementedError stubs. This module has the
exact same public shape (build_index, retrieve, answer) so tests can run
against either one interchangeably via RAG_IMPL.
"""
from __future__ import annotations

import faiss

from ragkit.chunking import chunk_documents
from ragkit.corpus import load_corpus
from ragkit.embeddings import EmbeddingModel
from ragkit.llm import get_llm
from ragkit.types import Chunk, Hit

_embedder = EmbeddingModel()


def build_index(chunks: list[Chunk]) -> faiss.Index:
    vectors = _embedder.encode([c.text for c in chunks])
    dim = vectors.shape[1] if vectors.size else _embedder.dimension
    index = faiss.IndexFlatIP(dim)
    if vectors.size:
        index.add(vectors)
    return index


_index: faiss.Index | None = None
_indexed_chunks: list[Chunk] | None = None


def _get_index() -> tuple[faiss.Index, list[Chunk]]:
    global _index, _indexed_chunks
    if _index is None:
        _indexed_chunks = chunk_documents(load_corpus())
        _index = build_index(_indexed_chunks)
    return _index, _indexed_chunks


def retrieve(query: str, k: int = 5) -> list[Hit]:
    index, chunks = _get_index()
    if not chunks:
        return []
    query_vec = _embedder.encode([query])
    scores, indices = index.search(query_vec, min(k, len(chunks)))
    hits = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        hits.append(Hit(chunk=chunks[idx], score=float(score)))
    return hits


_ANSWER_PROMPT = """Answer the question using ONLY the context below. If the
context doesn't contain the answer, say so plainly.

Context:
{context}

Question: {question}
Answer:"""


def answer(query: str, k: int = 5) -> str:
    hits = retrieve(query, k=k)
    context = "\n\n".join(f"[{h.chunk.doc_title}] {h.chunk.text}" for h in hits)
    prompt = _ANSWER_PROMPT.format(context=context, question=query)
    return get_llm().complete(prompt)


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "What is the bereavement leave policy?"
    print(answer(query))
