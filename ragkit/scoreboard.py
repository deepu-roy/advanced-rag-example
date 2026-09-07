"""Persist and render the cross-lab comparison table.

`record(scorecard)` appends one row to data/.cache/scoreboard.json;
`render()` prints the table `make scoreboard` shows. Kept separate from
evaluate.py so evaluate() has no side effects, and only this module writes
to disk. This is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

import json
from pathlib import Path

from ragkit.evaluate import ScoreCard, evaluate

REPO_ROOT = Path(__file__).resolve().parent.parent
SCOREBOARD_PATH = REPO_ROOT / "data" / ".cache" / "scoreboard.json"

PIPELINES = [
    ("01_simple_rag", "lab01_simple_rag"),
    ("02_query_optimization", "lab02_query_optimization"),
    ("03_hybrid_rrf", "lab03_hybrid_rrf"),
    ("04_reranking", "lab04_reranking"),
]

# Short column labels for the category-breakdown table below — the full
# pipeline names above are too wide to fit four per row legibly.
SHORT_LABEL = {
    "01_simple_rag": "01",
    "02_query_optimization": "02",
    "03_hybrid_rrf": "03",
    "04_reranking": "04",
}

# Which query category each stage is "responsible for" — used to bold/mark
# that cell in the category breakdown table, since that's the cell the
# whole lab is trying to move.
STAGE_FOR_CATEGORY = {
    "lab1": "01_simple_rag",
    "lab2": "02_query_optimization",
    "lab3": "03_hybrid_rrf",
    "lab4": "04_reranking",
}
CATEGORY_LABELS = {
    "lab1": "lab1 (control)",
    "lab2": "lab2 (query-opt targets)",
    "lab3": "lab3 (hybrid/RRF targets)",
    "lab4": "lab4 (reranking targets)",
}


def record(scorecard: ScoreCard) -> None:
    SCOREBOARD_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = _load()
    rows[scorecard.pipeline] = {
        "recall_at_5": scorecard.recall_at_5,
        "mrr": scorecard.mrr,
        "ndcg_at_5": scorecard.ndcg_at_5,
        "by_teaches": scorecard.by_teaches(),
    }
    SCOREBOARD_PATH.write_text(json.dumps(rows, indent=2, sort_keys=True))


def _load() -> dict:
    if SCOREBOARD_PATH.exists():
        return json.loads(SCOREBOARD_PATH.read_text())
    return {}


def render() -> str:
    rows = _load()
    lines = [
        "OVERALL (all gold queries averaged together)",
        f"{'pipeline':<24}{'recall@5':>10}{'mrr':>10}{'ndcg@5':>10}",
        "-" * 54,
    ]
    for name, _module in PIPELINES:
        if name not in rows:
            lines.append(f"{name:<24}{'--':>10}{'--':>10}{'--':>10}   (not run yet)")
            continue
        r = rows[name]
        lines.append(
            f"{name:<24}{r['recall_at_5']:>10.2f}{r['mrr']:>10.2f}{r['ndcg_at_5']:>10.2f}"
        )

    lines.append("")
    lines.append(
        "MRR BY QUERY CATEGORY — the real story. The overall table above averages"
    )
    lines.append(
        "each stage's fix in with several \"control\" queries every pipeline already"
    )
    lines.append(
        "gets right, which dilutes a real, targeted improvement into a small overall"
    )
    lines.append(
        "move. Read down each row instead: it should jump (or hold its ceiling) right"
    )
    lines.append("(column headers are stage numbers; a '>' marks a category's own stage)")
    lines.append("")
    header = f"{'category':<26}" + "".join(f"{SHORT_LABEL[name]:>10}" for name, _ in PIPELINES)
    lines.append(header)
    lines.append("-" * len(header))
    for category, label in CATEGORY_LABELS.items():
        cells = []
        for name, _module in PIPELINES:
            if name not in rows or category not in rows[name].get("by_teaches", {}):
                cells.append(f"{'--':>10}")
                continue
            value = rows[name]["by_teaches"][category]["mrr"]
            marker = ">" if STAGE_FOR_CATEGORY[category] == name else " "
            cells.append(f"{marker}{value:>9.3f}")
        lines.append(f"{label:<26}" + "".join(cells))

    return "\n".join(lines)


def run_all(package: str = "labs") -> None:
    """Import each pipeline from `package` (labs or solutions), evaluate it
    against the gold set, and record the result. Skips (with a note)
    pipelines that raise NotImplementedError so a partial workshop still
    produces a partial scoreboard."""
    import importlib

    for name, module_name in PIPELINES:
        try:
            module = importlib.import_module(f"{package}.{module_name}")
            card = evaluate(module.retrieve, pipeline=name)
            record(card)
            print(f"scored {name}: recall@5={card.recall_at_5:.2f} mrr={card.mrr:.2f}")
        except NotImplementedError:
            print(f"skipped {name}: not implemented yet")
        except Exception as exc:  # noqa: BLE001
            print(f"skipped {name}: error during evaluation ({exc})")


if __name__ == "__main__":
    import os
    import sys

    if "--run" in sys.argv:
        run_all(package=os.environ.get("RAG_IMPL", "labs"))
    print()
    print(render())
