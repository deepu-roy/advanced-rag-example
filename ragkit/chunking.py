"""Split Documents into overlapping Chunks small enough to embed.

This is plain infrastructure (not a lab exercise): a fixed-size sliding
window over whitespace-tokenized text. Real systems often chunk by
structure (headings, sentences); a simple window is enough for the
retrieval lessons this lab is about, and keeps chunk boundaries predictable
for tests.
"""
from __future__ import annotations

from ragkit.types import Chunk, Document

DEFAULT_CHUNK_SIZE = 120  # words per chunk
DEFAULT_OVERLAP = 30  # words shared between consecutive chunks of the same doc


def chunk_documents(
    docs: list[Document],
    size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Chunk every document with a sliding window.

    Deterministic and lossless: every word of every document appears in at
    least one chunk, and consecutive chunks of the same document share
    exactly `overlap` words.
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks: list[Chunk] = []
    step = size - overlap
    for doc in docs:
        words = doc.text.split()
        if not words:
            continue
        start = 0
        index = 0
        while True:
            piece = words[start : start + size]
            chunks.append(
                Chunk(
                    id=f"{doc.id}::{index}",
                    doc_id=doc.id,
                    doc_title=doc.title,
                    text=" ".join(piece),
                    tags=doc.tags,
                )
            )
            index += 1
            if start + size >= len(words):
                break
            start += step
    return chunks
