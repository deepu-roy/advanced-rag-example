"""Run a retrieval function over the gold query set and score it.

`evaluate(retrieve_fn)` is the one thing every lab's tests and the
scoreboard call: pass in any function `(query: str, k: int) -> list[Hit]`
and get back a ScoreCard with per-query and averaged Recall@5 / MRR /
nDCG@5. This is given infrastructure, not a lab exercise.

Relevance is judged at the *document* level: a gold query lists the source
document id(s) that answer it, and a retrieved chunk counts as a hit if its
`chunk.doc_id` is in that set. This keeps gold-query authoring simple (you
label "this document answers this question", not individual chunk
boundaries) and is insensitive to exactly how a document got chunked.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ragkit.metrics import mrr, ndcg_at_k, recall_at_k
from ragkit.types import Hit

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GOLD_PATH = REPO_ROOT / "data" / "gold_queries.yaml"

RetrieveFn = Callable[..., list[Hit]]


@dataclass(frozen=True)
class GoldQuery:
    query: str
    relevant: tuple[str, ...]  # document ids that answer this query
    teaches: str  # which lab stage this query is designed to be fixed by


@dataclass
class QueryScore:
    query: str
    teaches: str
    recall_at_5: float
    mrr: float
    ndcg_at_5: float


@dataclass
class ScoreCard:
    pipeline: str
    per_query: list[QueryScore] = field(default_factory=list)

    @property
    def recall_at_5(self) -> float:
        return _mean(s.recall_at_5 for s in self.per_query)

    @property
    def mrr(self) -> float:
        return _mean(s.mrr for s in self.per_query)

    @property
    def ndcg_at_5(self) -> float:
        return _mean(s.ndcg_at_5 for s in self.per_query)

    def by_teaches(self) -> dict[str, dict[str, float]]:
        """Recall@5 and MRR grouped by the failure mode each query targets —
        e.g. {"lab2": {"recall_at_5": 1.0, "mrr": 1.0}, ...}.

        This is usually the more informative view than the whole-gold-set
        aggregate above. The aggregate averages a stage's genuinely-fixed
        queries together with every other query in the set — including
        several "control" queries every pipeline already gets right and
        can't improve on further — which dilutes a real, targeted fix down
        to a small overall move. Grouping by which stage a query actually
        targets shows the real signal: a category's score should jump (or
        stay at its ceiling) right at the stage built to fix it, even when
        the whole-set aggregate barely twitches.
        """
        groups: dict[str, list[QueryScore]] = {}
        for s in self.per_query:
            groups.setdefault(s.teaches, []).append(s)
        return {
            teaches: {
                "recall_at_5": _mean(s.recall_at_5 for s in scores),
                "mrr": _mean(s.mrr for s in scores),
            }
            for teaches, scores in groups.items()
        }


def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def load_gold_queries(path: Path | str = DEFAULT_GOLD_PATH) -> list[GoldQuery]:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [
        GoldQuery(query=item["query"], relevant=tuple(item["relevant"]), teaches=item["teaches"])
        for item in raw
    ]


def evaluate(
    retrieve_fn: RetrieveFn,
    *,
    pipeline: str = "pipeline",
    k: int = 5,
    gold_queries: list[GoldQuery] | None = None,
) -> ScoreCard:
    gold_queries = gold_queries if gold_queries is not None else load_gold_queries()
    card = ScoreCard(pipeline=pipeline)
    for gq in gold_queries:
        hits = retrieve_fn(gq.query, k=k)
        # Dedup by first (best) occurrence: relevance is per-document, so if
        # two chunks of the same document both land in the top-k, that
        # document's rank is its *first* appearance, not a second "hit".
        # Without this, nDCG can exceed 1.0 by double-counting a document.
        retrieved_doc_ids: list[str] = []
        seen_docs: set[str] = set()
        for h in hits:
            if h.chunk.doc_id not in seen_docs:
                seen_docs.add(h.chunk.doc_id)
                retrieved_doc_ids.append(h.chunk.doc_id)
        relevant = set(gq.relevant)
        card.per_query.append(
            QueryScore(
                query=gq.query,
                teaches=gq.teaches,
                recall_at_5=recall_at_k(retrieved_doc_ids, relevant, k),
                mrr=mrr(retrieved_doc_ids, relevant),
                ndcg_at_5=ndcg_at_k(retrieved_doc_ids, relevant, k),
            )
        )
    return card
