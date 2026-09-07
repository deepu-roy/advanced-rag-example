"""CLI: run one query through all four pipelines and print their top hits
side by side, so the effect of each stage is visible on a single query
instead of only in aggregate metrics.

Usage:
    python -m ragkit.compare "What causes error E-4021?"

Set RAG_IMPL=solutions to compare the reference pipelines instead of your
own labs/ implementation. This is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

import importlib
import os
import sys

PIPELINE_MODULES = [
    ("01 simple", "lab01_simple_rag"),
    ("02 query-opt", "lab02_query_optimization"),
    ("03 hybrid+RRF", "lab03_hybrid_rrf"),
    ("04 reranking", "lab04_reranking"),
]


def _load_pipeline(module_name: str):
    package = os.environ.get("RAG_IMPL", "labs")
    return importlib.import_module(f"{package}.{module_name}")


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print('Usage: python -m ragkit.compare "your question"')
        raise SystemExit(1)
    query = " ".join(argv)
    print(f'Query: "{query}"\n')
    for label, module_name in PIPELINE_MODULES:
        print(f"--- {label} ---")
        try:
            module = _load_pipeline(module_name)
            hits = module.retrieve(query, k=3)
            if not hits:
                print("  (no results)")
            for hit in hits:
                snippet = hit.chunk.text[:110].replace("\n", " ")
                print(f"  [{hit.score:7.3f}] {hit.chunk.doc_title} :: {snippet}...")
        except NotImplementedError:
            print("  (not implemented yet)")
        except Exception as exc:  # noqa: BLE001
            print(f"  (error: {exc})")
        print()


if __name__ == "__main__":
    main()
