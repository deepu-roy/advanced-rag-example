"""LLM access for the lab pipelines.

One interface (`LLMProvider.complete(prompt) -> str`), three
implementations, selected by the RAG_LLM environment variable:

    RAG_LLM=ollama    (default)  a local Ollama server, OpenAI-compatible API
    RAG_LLM=openai                any OpenAI-compatible endpoint you point it
                                   at (Azure OpenAI, a corporate gateway,
                                   OpenRouter, ...) via RAG_LLM_BASE_URL /
                                   RAG_LLM_API_KEY / RAG_LLM_MODEL
    RAG_LLM=offline                no network calls at all; deterministic
                                   rule-based rewriting/answering

`get_llm()` is what labs call. If a real provider is configured but
unreachable (Ollama not started yet, a bad key, network blocked), it falls
back to the offline provider with a printed warning rather than crashing a
lab — the exercise should never live or die by a model server being up.

The test suite pins RAG_LLM=offline (see tests/conftest.py) so grading never
depends on a live model. This is given infrastructure, not a lab exercise.
"""
from __future__ import annotations

import os
import re
from abc import ABC, abstractmethod

from ragkit.types import Hit

DEFAULT_OLLAMA_MODEL = "qwen2.5:1.5b-instruct"

# get_llm() is called once per query in some labs; cache providers per
# backend so we only pay the "is it reachable" probe once per process.
_provider_cache: dict[str, LLMProvider] = {}


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, *, system: str | None = None) -> str: ...


class OpenAICompatProvider(LLMProvider):
    """Wraps any OpenAI-compatible /chat/completions endpoint: Ollama, Azure
    OpenAI, a corporate gateway, OpenRouter, ... They all speak the same
    wire protocol, so one client class covers all of them."""

    def __init__(self, base_url: str, api_key: str, model: str):
        from openai import OpenAI

        self._client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return (response.choices[0].message.content or "").strip()


class OfflineRewriter(LLMProvider):
    """Deterministic, network-free stand-in for an LLM.

    Good enough to exercise query-optimization *mechanics* (expansion,
    decomposition, hypothetical-answer templating) without needing a model
    server, and used to keep the test suite fast and fully reproducible.
    """

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        # "Answer" mode: surface the first sentence of whatever context block
        # the caller stuffed into the prompt, so lab01's answer() has
        # something non-trivial to show without a real model.
        context_match = re.search(r"Context:\n(.*?)\n\nQuestion:", prompt, re.DOTALL)
        if context_match:
            sentences = re.split(r"(?<=[.!?])\s+", context_match.group(1).strip())
            return sentences[0] if sentences and sentences[0] else "(offline: no context found)"

        # "HyDE" mode: template a generic hypothetical-answer paragraph that
        # at least echoes the question's own vocabulary back, which is often
        # enough for embedding similarity even without real content.
        question_match = re.search(r"Question:\s*(.*?)\s*\nParagraph:", prompt, re.DOTALL)
        if question_match:
            topic = question_match.group(1).strip().rstrip("?")
            return f"According to internal policy, {topic.lower()} is handled as documented below."

        return "(offline mode: no answer generated)"


def get_llm() -> LLMProvider:
    backend = os.environ.get("RAG_LLM", "ollama").lower()
    if backend in _provider_cache:
        return _provider_cache[backend]

    if backend == "offline":
        provider: LLMProvider = OfflineRewriter()
        _provider_cache[backend] = provider
        return provider

    if backend == "openai":
        base_url = os.environ.get("RAG_LLM_BASE_URL")
        api_key = os.environ.get("RAG_LLM_API_KEY")
        model = os.environ.get("RAG_LLM_MODEL")
        if not (base_url and api_key and model):
            print(
                "[ragkit.llm] RAG_LLM=openai but RAG_LLM_BASE_URL/RAG_LLM_API_KEY/"
                "RAG_LLM_MODEL are not all set — falling back to offline mode."
            )
            provider = OfflineRewriter()
            _provider_cache[backend] = provider
            return provider
        candidate = OpenAICompatProvider(base_url=base_url, api_key=api_key, model=model)
    else:  # "ollama"
        candidate = OpenAICompatProvider(
            base_url=os.environ.get("RAG_LLM_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama",
            model=os.environ.get("RAG_LLM_MODEL", DEFAULT_OLLAMA_MODEL),
        )

    try:
        candidate.complete("ping", system="Reply with the single word: pong")
        provider = candidate
    except Exception as exc:  # noqa: BLE001 - any failure means "use offline"
        print(f"[ragkit.llm] {backend} provider unreachable ({exc}); falling back to offline mode.")
        provider = OfflineRewriter()

    _provider_cache[backend] = provider
    return provider


_ANSWER_PROMPT = """Answer the question using ONLY the context below. If the
context doesn't contain the answer, say so plainly.

Context:
{context}

Question: {question}
Answer:"""


def answer_from_hits(query: str, hits: list[Hit]) -> str:
    """Generate an answer from already-retrieved hits.

    Labs 2-4 only change *retrieval*, so they share this generation step
    instead of each reimplementing lab 1's answer().
    """
    if not hits:
        return "(no context retrieved)"
    context = "\n\n".join(f"[{hit.chunk.doc_title}]\n{hit.chunk.text}" for hit in hits)
    return get_llm().complete(_ANSWER_PROMPT.format(context=context, question=query))
