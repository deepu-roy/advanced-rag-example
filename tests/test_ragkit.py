"""Tests for the given ragkit infrastructure. Not a lab exercise — these
should pass without you changing anything, and exist so you can trust the
foundation the labs are built on."""
from __future__ import annotations

from ragkit.chunking import chunk_documents
from ragkit.corpus import load_corpus
from ragkit.glossary import find_acronyms, load_glossary
from ragkit.metrics import mrr, ndcg_at_k, recall_at_k
from ragkit.types import Document


def test_load_corpus_has_unique_ids_and_content():
    docs = load_corpus()
    assert len(docs) >= 20
    ids = [d.id for d in docs]
    assert len(ids) == len(set(ids))
    assert all(d.text.strip() for d in docs)


def test_chunking_is_lossless():
    docs = [Document(id="d1", title="D1", text=" ".join(f"word{i}" for i in range(50)))]
    chunks = chunk_documents(docs, size=20, overlap=5)
    covered: set[str] = set()
    for c in chunks:
        covered.update(c.text.split())
    assert covered == {f"word{i}" for i in range(50)}


def test_chunking_respects_overlap():
    docs = [Document(id="d1", title="D1", text=" ".join(f"word{i}" for i in range(50)))]
    chunks = chunk_documents(docs, size=20, overlap=5)
    for a, b in zip(chunks, chunks[1:]):
        if a.doc_id == b.doc_id:
            assert a.text.split()[-5:] == b.text.split()[:5]


def test_glossary_finds_known_acronym():
    glossary = load_glossary()
    assert "OTIF" in glossary
    assert find_acronyms("What is OTIF?", glossary) == ["OTIF"]


def test_glossary_ignores_non_acronym_words():
    glossary = load_glossary()
    assert find_acronyms("What is the plan for tomorrow?", glossary) == []


def test_recall_at_k_basic():
    assert recall_at_k(["a", "b", "c"], {"b"}, k=2) == 1.0
    assert recall_at_k(["a", "b", "c"], {"z"}, k=2) == 0.0
    assert recall_at_k(["a", "b"], {"a", "z"}, k=2) == 0.5


def test_mrr_basic():
    assert mrr(["a", "b", "c"], {"b"}) == 0.5
    assert mrr(["a", "b", "c"], {"z"}) == 0.0
    assert mrr(["a", "b", "c"], {"a"}) == 1.0


def test_ndcg_perfect_order_is_one():
    assert ndcg_at_k(["a", "b"], {"a", "b"}, k=2) == 1.0


def test_ndcg_never_exceeds_one():
    # A relevant id repeated in the ranking must not inflate the score
    # past 1.0 — relevance is per-document, not per-occurrence.
    assert ndcg_at_k(["a", "a", "a"], {"a"}, k=3) <= 1.0
