"""Sentence embeddings, with a disk cache so repeated runs (and tests) don't
re-embed the same text through a slow model every time.

Labs call `EmbeddingModel().encode(texts)` and get back a (n, dim) float32
numpy array, L2-normalized so inner product == cosine similarity — which is
what lets FAISS's IndexFlatIP double as cosine search. This is given
infrastructure, not a lab exercise.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "data" / ".cache" / "embeddings"
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def _cache_key(model_name: str, texts: list[str]) -> str:
    payload = json.dumps({"model": model_name, "texts": texts}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


class EmbeddingModel:
    """Lazily loads a SentenceTransformer model and caches encodings on disk."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, cache_dir: Path | str = CACHE_DIR):
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self._model = None  # loaded on first use, not at construction time

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str], use_cache: bool = True) -> np.ndarray:
        """Return an (n, dim) float32 array of L2-normalized embeddings, one
        row per input text, in the same order."""
        if not texts:
            return np.zeros((0, self.dimension), dtype="float32")
        if not use_cache:
            return self._encode_raw(texts)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        key = _cache_key(self.model_name, texts)
        cache_path = self.cache_dir / f"{key}.npy"
        if cache_path.exists():
            return np.load(cache_path)
        vectors = self._encode_raw(texts)
        np.save(cache_path, vectors)
        return vectors

    def _encode_raw(self, texts: list[str]) -> np.ndarray:
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype("float32")
