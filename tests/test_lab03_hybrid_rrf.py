"""Fixed tests for Lab 3 — Hybrid Retrieval + RRF. Do not edit.

Run against your work:      pytest tests/test_lab03_hybrid_rrf.py -v
Run against the reference:  RAG_IMPL=solutions pytest tests/test_lab03_hybrid_rrf.py -v
"""
from __future__ import annotations

import pytest

from ragkit.evaluate import evaluate
from tests.conftest import impl

lab02 = impl("lab02_query_optimization")
lab03 = impl("lab03_hybrid_rrf")

# The reference solution scores 0.975 recall@5 on the gold set (see
# docs/FACILITATOR.md). This threshold leaves generous slack.
MIN_RECALL_AT_5 = 0.80

# See docs/FACILITATOR.md: one query's worth of noise in this 20-query
# gold set is exactly 0.05, and lab03's un-decomposed multi-hop handling
# costs it exactly one query relative to lab02 — a real, honest trade-off,
# not a bug.
CROSS_LAB_TOLERANCE = 0.05


def test_rrf_exact_fusion_order():
    # Two hand-built rankings: "a" is #1 in both, so it must fuse to #1.
    # "b" only appears in ranking 1 (at rank 2); "c" only in ranking 2 (at
    # rank 2) — they must tie. "z" is #3 in both, which beats a lone #2
    # appearance, so it must rank above both "b" and "c".
    rankings = [["a", "b", "z"], ["a", "c", "z"]]
    fused = lab03.reciprocal_rank_fusion(rankings, k_const=60)
    fused_ids = [chunk_id for chunk_id, _ in fused]
    fused_scores = dict(fused)

    assert fused_ids[0] == "a"
    assert fused_scores["z"] > fused_scores["b"]
    assert fused_scores["z"] > fused_scores["c"]
    assert fused_scores["b"] == pytest.approx(fused_scores["c"])
    assert fused_ids.index("z") < fused_ids.index("b")
    assert fused_ids.index("z") < fused_ids.index("c")


def test_rrf_matches_hand_computed_score():
    rankings = [["a", "x"], ["x", "a"]]
    fused = dict(lab03.reciprocal_rank_fusion(rankings, k_const=60))
    expected_a = 1 / 61 + 1 / 62
    assert fused["a"] == pytest.approx(expected_a)


def test_bm25_search_finds_the_exact_code_dense_search_misses():
    # Verified: dense-only search picks the wrong (billing) error-code
    # document for this query, because all three subsystem documents share
    # generic "error code reference" framing. BM25's exact match on the
    # literal code string must not make the same mistake.
    hits = lab03.bm25_search("E-4021 cause", k=3)
    doc_ids = {h.chunk.doc_id for h in hits}
    assert "ops-error-codes-manifest" in doc_ids


def test_retrieve_returns_hits_sorted_by_fused_score():
    hits = lab03.retrieve("What is the bereavement leave policy?", k=5)
    assert len(hits) <= 5
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_lab03_disambiguates_the_exact_error_code():
    doc_ids = [h.chunk.doc_id for h in lab03.retrieve("E-4021 cause", k=2)]
    assert "ops-error-codes-manifest" in doc_ids


def test_gold_set_recall_meets_baseline():
    card = evaluate(lab03.retrieve, pipeline="03_hybrid_rrf")
    assert card.recall_at_5 >= MIN_RECALL_AT_5


def test_gold_set_does_not_regress_lab02():
    try:
        lab02_card = evaluate(lab02.retrieve, pipeline="02_query_optimization")
    except NotImplementedError:
        pytest.skip("lab02 not implemented yet")
    lab03_card = evaluate(lab03.retrieve, pipeline="03_hybrid_rrf")
    assert lab03_card.recall_at_5 >= lab02_card.recall_at_5 - CROSS_LAB_TOLERANCE
