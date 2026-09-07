"""Load the lab's source corpus from data/corpus/*.md.

Each file is a Markdown document with a small YAML frontmatter block:

    ---
    id: hr-leave-bereavement
    title: Bereavement Leave Policy
    tags: [hr, leave, policy]
    ---
    # Bereavement Leave

    ...body...

`load_corpus()` is the only thing labs/solutions need from this module. This
is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from ragkit.types import Document

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS_DIR = REPO_ROOT / "data" / "corpus"

_FRONTMATTER_DELIM = "---"


def _parse_document(path: Path) -> Document:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith(_FRONTMATTER_DELIM):
        raise ValueError(f"{path} is missing a YAML frontmatter block")
    _, frontmatter, body = raw.split(_FRONTMATTER_DELIM, 2)
    meta = yaml.safe_load(frontmatter) or {}
    doc_id = meta.get("id") or path.stem
    title = meta.get("title") or doc_id
    tags = tuple(meta.get("tags", []))
    return Document(id=doc_id, title=title, text=body.strip(), tags=tags)


def load_corpus(corpus_dir: Path | str = DEFAULT_CORPUS_DIR) -> list[Document]:
    """Load every *.md file in corpus_dir into a Document, sorted by id."""
    corpus_dir = Path(corpus_dir)
    paths = sorted(corpus_dir.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No corpus documents found under {corpus_dir}")
    docs = [_parse_document(p) for p in paths]
    ids = [d.id for d in docs]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Duplicate document ids in corpus: {sorted(dupes)}")
    return sorted(docs, key=lambda d: d.id)
