"""Small acronym -> expansion glossary for the fictional freight company
this lab's corpus belongs to.

Lab 2 uses this to demonstrate a cheap, common query-rewriting technique:
before ever calling an LLM, expand any acronym the *query* uses but the
*documents* spell out in full (or vice versa), so dense retrieval doesn't
have to bridge the vocabulary gap on its own.

This is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GLOSSARY_PATH = REPO_ROOT / "data" / "glossary.yaml"

_ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,6}(?:-\d+)?\b")


def load_glossary(path: Path | str = DEFAULT_GLOSSARY_PATH) -> dict[str, str]:
    """Load the acronym -> expansion mapping, keyed by uppercase acronym."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {str(k).upper(): str(v) for k, v in data.items()}


def find_acronyms(text: str, glossary: dict[str, str]) -> list[str]:
    """Return glossary keys that appear in `text` as whole uppercase tokens,
    in the order they first appear."""
    seen: list[str] = []
    for token in _ACRONYM_PATTERN.findall(text):
        if token in glossary and token not in seen:
            seen.append(token)
    return seen
