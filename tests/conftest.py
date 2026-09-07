"""Shared pytest configuration for the lab test suite.

Two things happen here for every test:

1. RAG_LLM is forced to "offline" for the whole session, so grading is
   deterministic and never depends on a live model server (Ollama or
   otherwise). A test that specifically wants a live provider should be
   marked `@pytest.mark.llm` (deselected by default — see pyproject.toml)
   and set RAG_LLM itself via monkeypatch.

2. Tests import lab modules through `impl(name)` instead of a bare
   `import labs.lab01_simple_rag`, so the whole suite can be pointed at the
   reference solutions with `RAG_IMPL=solutions pytest` to prove every test
   here is satisfiable by a correct implementation.
"""
from __future__ import annotations

import importlib
import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _offline_llm_for_tests():
    os.environ["RAG_LLM"] = "offline"


def impl(module_name: str):
    """Import `<RAG_IMPL>.<module_name>` (RAG_IMPL defaults to "labs")."""
    package = os.environ.get("RAG_IMPL", "labs")
    return importlib.import_module(f"{package}.{module_name}")


@pytest.fixture(scope="session")
def corpus():
    from ragkit.corpus import load_corpus

    return load_corpus()


@pytest.fixture(scope="session")
def chunks(corpus):
    from ragkit.chunking import chunk_documents

    return chunk_documents(corpus)
