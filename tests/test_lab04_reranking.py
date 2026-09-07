"""Fixed tests for Lab 4 — Reranking. Do not edit.

Run against your work:      pytest tests/test_lab04_reranking.py -v
Run against the reference:  RAG_IMPL=solutions pytest tests/test_lab04_reranking.py -v
"""
from __future__ import annotations

import pytest

from ragkit.evaluate import evaluate
from ragkit.types import Chunk, Hit
from tests.conftest import impl

lab03 = impl("lab03_hybrid_rrf")
lab04 = impl("lab04_reranking")

# The reference solution scores 0.975 recall@5 and 0.975 MRR on the gold
# set (see docs/FACILITATOR.md). These thresholds leave generous slack.
MIN_RECALL_AT_5 = 0.80
MIN_MRR = 0.85

CROSS_LAB_TOLERANCE = 0.05


def _fake_chunk(chunk_id: str, text: str) -> Chunk:
    return Chunk(id=chunk_id, doc_id=chunk_id, doc_title=chunk_id, text=text, tags=())


def test_rerank_returns_exactly_top_n():
    candidates = [
        Hit(chunk=_fake_chunk(f"c{i}", f"filler text number {i}"), score=0.0) for i in range(10)
    ]
    result = lab04.rerank("a query", candidates, top_n=4)
    assert len(result) == 4


def test_rerank_is_sorted_descending():
    candidates = [
        Hit(chunk=_fake_chunk(f"c{i}", f"filler text number {i}"), score=0.0) for i in range(8)
    ]
    result = lab04.rerank("a query", candidates, top_n=8)
    scores = [h.score for h in result]
    assert scores == sorted(scores, reverse=True)


def test_rerank_returns_a_subset_of_its_input():
    candidates = [
        Hit(chunk=_fake_chunk(f"c{i}", f"filler text number {i}"), score=0.0) for i in range(6)
    ]
    result = lab04.rerank("a query", candidates, top_n=6)
    assert {h.chunk.id for h in result} == {c.chunk.id for c in candidates}


def test_rerank_handles_empty_candidates():
    assert lab04.rerank("a query", [], top_n=5) == []


def test_rerank_promotes_the_obviously_relevant_candidate():
    query = "What is the bereavement leave policy?"
    candidates = [
        Hit(
            chunk=_fake_chunk("relevant", "Employees receive five days of paid bereavement leave."),
            score=0.0,
        ),
        Hit(
            chunk=_fake_chunk("decoy1", "The office coffee machine is serviced every Tuesday."),
            score=0.0,
        ),
        Hit(
            chunk=_fake_chunk("decoy2", "Parking permits renew annually in the spring."),
            score=0.0,
        ),
    ]
    result = lab04.rerank(query, candidates, top_n=3)
    assert result[0].chunk.id == "relevant"


def test_gold_set_recall_meets_baseline():
    card = evaluate(lab04.retrieve, pipeline="04_reranking")
    assert card.recall_at_5 >= MIN_RECALL_AT_5


def test_gold_set_mrr_meets_baseline():
    # The point of reranking: recall barely moves, MRR/nDCG jump because
    # the right chunk was already in the pool and just gets moved to the
    # top. Check MRR here, not recall — recall is checked above.
    card = evaluate(lab04.retrieve, pipeline="04_reranking")
    assert card.mrr >= MIN_MRR


def test_gold_set_mrr_does_not_regress_lab03():
    try:
        lab03_card = evaluate(lab03.retrieve, pipeline="03_hybrid_rrf")
    except NotImplementedError:
        pytest.skip("lab03 not implemented yet")
    lab04_card = evaluate(lab04.retrieve, pipeline="04_reranking")
    assert lab04_card.mrr >= lab03_card.mrr - CROSS_LAB_TOLERANCE
