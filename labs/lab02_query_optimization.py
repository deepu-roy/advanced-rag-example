"""Lab 2 — Query Optimization.

Lab 1 embeds the query exactly as written and hopes the corpus uses the
same words. It doesn't always: participants ask about "OTIF" when the
runbook spells out "on-time-in-full", or ask one compound question that
really needs two different documents. This lab fixes the *query*, not the
retriever — lab01's index is reused as-is.

Try before/after on this one — it's a verified, measured win in this
corpus (naive search ranks the right document 3rd; expansion moves it to
1st):

    python -m ragkit.compare "What's the process if a delivery isn't OTIF?"

Three techniques, combined:
  1. Acronym expansion   — look up any acronym in ragkit's glossary and add
                            an expanded variant of the query.
  2. Sub-question split  — a compound question ("X, and who approves Y?")
                            is split into its parts and each is searched
                            separately.
  3. HyDE (Hypothetical Document Embeddings) — ask the LLM to *write* a
     plausible answer, then search using that answer's embedding instead
     of the question's. A hypothetical answer often lands closer,
     vocabulary-wise, to the real document than the bare question does.

WHAT YOU'RE IMPLEMENTING
-------------------------
1. expand_query(query)  -> list[str]   — the original query plus 1+
                                          rewrites (always keep the
                                          original: a bad rewrite should
                                          never make things worse)
2. retrieve(query, k)                  — search with every variant, merge
                                          results by chunk id, keeping each
                                          chunk's *best* score across
                                          variants

Everything you need:
  - ragkit.glossary.load_glossary() -> {"OTIF": "on-time-in-full", ...}
  - ragkit.glossary.find_acronyms(text, glossary) -> list[str], the
    glossary keys that appear in `text` as whole uppercase tokens
  - ragkit.llm.get_llm().complete(prompt) -> str   (for HyDE)
  - labs.lab01_simple_rag.retrieve — lab 1's dense search, reused as-is;
    you're changing the *query* here, not the index

Run `pytest tests/test_lab02_query_optimization.py -v` to check your work.
"""
from __future__ import annotations

import re

from labs import lab01_simple_rag as lab01  # noqa: F401 - used once you implement retrieve()
from ragkit.glossary import find_acronyms, load_glossary  # noqa: F401 - used in expand_query()
from ragkit.llm import get_llm  # noqa: F401 - used in expand_query() for HyDE
from ragkit.types import Hit

_glossary = load_glossary()

_HYDE_PROMPT = """Write a single short paragraph that would plausibly answer
this question, as if it were an excerpt from an internal company document.
Do not say you don't know; make a best-effort guess at the specific policy,
process, or number involved.

Question: {question}
Paragraph:"""

# Splits a compound question on "and"/"or" connectives. (Given — a small
# regex utility, not the interesting part of this exercise.)
_SPLIT_PATTERN = re.compile(r"\s*(?:,?\s+and\s+|\s+or\s+)\s*", re.IGNORECASE)


def expand_query(query: str) -> list[str]:
    """Return [query, *rewrites]. Always include the original query
    unchanged, so a rewrite that goes wrong never *loses* the naive result.

    HINT for acronym expansion: `find_acronyms(query, _glossary)` gives you
    the acronyms present; build a variant that replaces each one with
    "ACRONYM (expansion)" so both forms are present for the embedder.

    HINT for sub-question splitting: `_SPLIT_PATTERN.split(query)` breaks a
    compound question into parts — only useful if it actually produced
    more than one non-empty piece.

    HINT for HyDE: call `get_llm().complete(_HYDE_PROMPT.format(question=query))`
    and add the result as another variant (if it's non-empty).

    HINT: de-duplicate the final list while preserving order — a rewrite
    that happens to match something already in the list adds nothing.
    """
    raise NotImplementedError(
        "expand_query: combine acronym expansion, sub-question splitting, and HyDE"
    )


def retrieve(query: str, k: int = 5) -> list[Hit]:
    """Search with every variant from expand_query(), then merge: if the
    same chunk is found by more than one variant, keep its best score.

    HINT: build a dict keyed by `hit.chunk.id`, updating it only when a new
    hit's score beats what's already there, then sort by score descending
    and return the top-k.
    """
    raise NotImplementedError("retrieve: search each expand_query() variant, merge by best score")


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "What's the process if a delivery isn't OTIF?"
    print("Variants:")
    for v in expand_query(query):
        print(f"  - {v}")
    print()
    for hit in retrieve(query, k=3):
        print(f"  [{hit.score:.3f}] {hit.chunk.doc_title}")
