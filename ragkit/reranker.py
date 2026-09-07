"""Cross-encoder reranking: given a query and a list of candidate texts,
score each (query, text) pair *jointly* instead of embedding them
separately (which is what dense retrieval does).

This is plain infrastructure — given, not a lab exercise. The interesting
part Lab 4 implements is *when* and *how* to use it: over-fetch a candidate
pool cheaply, then spend this more expensive model only on reordering that
pool.
"""
from __future__ import annotations

DEFAULT_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Lazily loads a CrossEncoder model on first use."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = CrossEncoder(self.model_name)
        return self._model

    def score(self, query: str, texts: list[str]) -> list[float]:
        """Return one relevance score per text, same order in as out.

        Higher is more relevant. Scores are raw model logits, not
        probabilities — they're only meaningful relative to each other for
        the same query, never compared across queries or against dense/BM25
        scores.
        """
        if not texts:
            return []
        pairs = [(query, text) for text in texts]
        scores = self.model.predict(pairs)
        return [float(s) for s in scores]
