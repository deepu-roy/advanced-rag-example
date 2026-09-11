"""Loads repo-root `.env` on import so local runs can supply secrets (HF_TOKEN,
RAG_LLM_API_KEY, ...) without exporting them into the host shell.

Every entry point — labs, solutions, ragkit CLIs, pytest — imports `ragkit`, so
this runs before anything reads os.environ. Real environment variables always
win, which keeps Codespaces secrets authoritative over a stray local `.env`.
"""
from __future__ import annotations

import os
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def _load_dotenv(path: Path = _ENV_FILE) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


_load_dotenv()
