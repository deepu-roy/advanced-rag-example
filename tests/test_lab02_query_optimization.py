"""Fixed tests for Lab 2 — Query Optimization. Do not edit.

Run against your work:      pytest tests/test_lab02_query_optimization.py -v
Run against the reference:  RAG_IMPL=solutions pytest tests/test_lab02_query_optimization.py -v
"""
from __future__ import annotations

import pytest

from ragkit.evaluate import evaluate
from tests.conftest import impl

lab01 = impl("lab01_simple_rag")
lab02 = impl("lab02_query_optimization")

# The reference solution scores 1.00 recall@5 on the gold set (see
# docs/FACILITATOR.md). This threshold leaves generous slack.
MIN_RECALL_AT_5 = 0.80

# A single query's worth of noise in a 20-query gold set is exactly 0.05 —
# see docs/FACILITATOR.md for why lab03's hybrid retrieval isn't perfectly
# monotonic on every single query even though the aggregate trend is.
CROSS_LAB_TOLERANCE = 0.05


def test_expand_query_always_includes_the_original():
    variants = lab02.expand_query("What is our vacation policy?")
    assert "What is our vacation policy?" in variants


def test_expand_query_produces_multiple_distinct_variants():
    variants = lab02.expand_query("What's the process if a delivery isn't OTIF?")
    assert len(set(variants)) >= 2


def test_expand_query_expands_a_known_acronym():
    variants = lab02.expand_query("What's the process if a delivery isn't OTIF?")
    assert any("on-time-in-full" in v.lower() for v in variants)


def test_retrieve_merges_by_best_score_not_duplicates():
    hits = lab02.retrieve("What is the bereavement leave policy?", k=5)
    ids = [h.chunk.id for h in hits]
    assert len(ids) == len(set(ids)), "retrieve() returned the same chunk twice"


def test_lab02_fixes_the_acronym_gap():
    # Verified: naive dense search (lab01) ranks the right document 3rd for
    # this query; expanding "OTIF" to "on-time-in-full" should pull it
    # into (at worst) 2nd. (The reference solution gets it to 1st, but
    # top-2 leaves room for a reasonable alternative implementation.)
    query = "What's the process if a delivery isn't OTIF?"
    doc_ids = [h.chunk.doc_id for h in lab02.retrieve(query, k=2)]
    assert "ops-otif-exceptions" in doc_ids


def test_gold_set_recall_meets_baseline():
    card = evaluate(lab02.retrieve, pipeline="02_query_optimization")
    assert card.recall_at_5 >= MIN_RECALL_AT_5


def test_gold_set_does_not_regress_lab01():
    try:
        lab01_card = evaluate(lab01.retrieve, pipeline="01_simple_rag")
    except NotImplementedError:
        pytest.skip("lab01 not implemented yet")
    lab02_card = evaluate(lab02.retrieve, pipeline="02_query_optimization")
    assert lab02_card.recall_at_5 >= lab01_card.recall_at_5 - CROSS_LAB_TOLERANCE
