"""Lab 2 — Query Optimization — reference solution.

See labs/lab02_query_optimization.py for the exercise version of this
file, with the teaching comments and NotImplementedError stubs.
"""
from __future__ import annotations

import re

from ragkit.glossary import find_acronyms, load_glossary
from ragkit.llm import get_llm
from ragkit.types import Hit
from solutions import lab01_simple_rag as lab01

_glossary = load_glossary()

_HYDE_PROMPT = """Write a single short paragraph that would plausibly answer
this question, as if it were an excerpt from an internal company document.
Do not say you don't know; make a best-effort guess at the specific policy,
process, or number involved.

Question: {question}
Paragraph:"""

_SPLIT_PATTERN = re.compile(r"\s*(?:,?\s+and\s+|\s+or\s+)\s*", re.IGNORECASE)


def expand_query(query: str) -> list[str]:
    variants = [query]

    # 1. Acronym expansion: if the query uses an acronym our glossary knows,
    # add a variant that spells it out too, so embedding similarity has a
    # chance even when the document never uses the acronym itself.
    acronyms = find_acronyms(query, _glossary)
    if acronyms:
        expanded = query
        for acro in acronyms:
            expanded = expanded.replace(acro, f"{acro} ({_glossary[acro]})")
        variants.append(expanded)

    # 2. Sub-question split: a compound question often needs two different
    # documents. Splitting on "and"/"or" lets each half be searched on its
    # own instead of forcing one embedding to represent both at once.
    parts = [p.strip().rstrip("?").strip() for p in _SPLIT_PATTERN.split(query) if p.strip()]
    if len(parts) > 1:
        variants.extend(p + "?" for p in parts)

    # 3. HyDE (Hypothetical Document Embeddings): ask the LLM to write a
    # plausible-sounding answer, then search using *that* text's embedding.
    # A hypothetical answer often lands closer, vocabulary-wise, to the real
    # document than the bare question does.
    hyde_paragraph = get_llm().complete(_HYDE_PROMPT.format(question=query))
    if hyde_paragraph:
        variants.append(hyde_paragraph)

    # De-duplicate while preserving order (a rewrite that happens to match
    # something already in the list adds nothing).
    seen: set[str] = set()
    unique = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def retrieve(query: str, k: int = 5) -> list[Hit]:
    best: dict[str, Hit] = {}
    for variant in expand_query(query):
        for hit in lab01.retrieve(variant, k=k):
            existing = best.get(hit.chunk.id)
            if existing is None or hit.score > existing.score:
                best[hit.chunk.id] = hit
    ranked = sorted(best.values(), key=lambda h: h.score, reverse=True)
    return ranked[:k]


if __name__ == "__main__":
    import sys

    query = " ".join(sys.argv[1:]) or "How long to file an OTIF exception?"
    print("Variants:")
    for v in expand_query(query):
        print(f"  - {v}")
    print()
    for hit in retrieve(query, k=3):
        print(f"  [{hit.score:.3f}] {hit.chunk.doc_title}")
