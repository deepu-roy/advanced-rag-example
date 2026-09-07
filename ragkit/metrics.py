"""Retrieval quality metrics used to score every lab against the gold set.

All three take the same shape of input: `retrieved` is a ranked list of ids
(best first), `relevant` is the *set* of ids considered correct for that
query. This is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

import math


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Fraction of relevant ids that appear anywhere in the top k."""
    if not relevant:
        return 0.0
    top_k = set(retrieved[:k])
    return len(top_k & relevant) / len(relevant)


def mrr(retrieved: list[str], relevant: set[str]) -> float:
    """Reciprocal rank of the first relevant id (0.0 if none found)."""
    for rank, item_id in enumerate(retrieved, start=1):
        if item_id in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Normalized discounted cumulative gain at k, with binary relevance.

    Each relevant id is only counted once even if it appears more than
    once in `retrieved` (e.g. two chunks from the same relevant document)
    — otherwise a duplicate could inflate the score past 1.0.
    """
    if not relevant:
        return 0.0
    dcg = 0.0
    seen: set[str] = set()
    for i, item_id in enumerate(retrieved[:k], start=1):
        if item_id in relevant and item_id not in seen:
            seen.add(item_id)
            dcg += 1.0 / math.log2(i + 1)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, ideal_hits + 1))
    return dcg / idcg if idcg > 0 else 0.0
