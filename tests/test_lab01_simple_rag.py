"""Fixed tests for Lab 1 — Simple RAG. Do not edit.

Run against your work:      pytest tests/test_lab01_simple_rag.py -v
Run against the reference:  RAG_IMPL=solutions pytest tests/test_lab01_simple_rag.py -v
"""
from __future__ import annotations

from ragkit.evaluate import evaluate
from tests.conftest import impl

lab01 = impl("lab01_simple_rag")

# The reference solution scores 1.00 recall@5 on the gold set (see
# docs/FACILITATOR.md for full measured numbers). This threshold leaves
# generous slack for a correct-but-differently-structured implementation.
MIN_RECALL_AT_5 = 0.75


def test_build_index_returns_one_vector_per_chunk(chunks):
    index = lab01.build_index(chunks)
    assert index.ntotal == len(chunks)


def test_retrieve_returns_k_hits_best_first():
    hits = lab01.retrieve("What is the bereavement leave policy?", k=5)
    assert len(hits) == 5
    scores = [h.score for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_finds_an_obviously_relevant_chunk():
    # Near-verbatim vocabulary overlap with data/corpus/hr-code-of-conduct.md
    hits = lab01.retrieve("What is our policy on gifts from vendors?", k=3)
    doc_ids = {h.chunk.doc_id for h in hits}
    assert "hr-code-of-conduct" in doc_ids


def test_answer_uses_retrieved_context(monkeypatch):
    seen: dict = {}

    class FakeLLM:
        def complete(self, prompt, system=None):
            seen["prompt"] = prompt
            return "fake answer"

    monkeypatch.setattr(lab01, "get_llm", lambda: FakeLLM())
    result = lab01.answer("What is the bereavement leave policy?", k=2)
    assert result == "fake answer"
    assert "Context:" in seen["prompt"]
    assert "bereavement" in seen["prompt"].lower() or "leave" in seen["prompt"].lower()


def test_gold_set_recall_meets_baseline():
    card = evaluate(lab01.retrieve, pipeline="01_simple_rag")
    assert card.recall_at_5 >= MIN_RECALL_AT_5, (
        f"recall@5={card.recall_at_5:.2f} is below the {MIN_RECALL_AT_5} baseline "
        "expected from a correct simple-RAG pipeline"
    )
