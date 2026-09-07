"""Shared data types used across ragkit, labs, and solutions.

These are intentionally plain, frozen dataclasses with no behavior — just
shape. Keeping them here (instead of every module inventing its own) means
every lab agrees on what a "chunk" or a "hit" looks like.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Document:
    """One source document loaded from data/corpus/*.md."""

    id: str
    title: str
    text: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Chunk:
    """A slice of a Document, small enough to embed and retrieve individually.

    `id` is conventionally f"{doc_id}::{chunk_index}" so it's traceable back
    to its source document just by looking at it.
    """

    id: str
    doc_id: str
    doc_title: str
    text: str
    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Hit:
    """One retrieved chunk plus the score that ranked it.

    `score` means different things in different labs (cosine similarity,
    BM25 score, RRF score, cross-encoder logit) — it's only ever compared
    to other scores from the *same* pipeline, never across pipelines.
    """

    chunk: Chunk
    score: float
