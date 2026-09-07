#!/usr/bin/env bash
# The expensive, cacheable half of setup: package install, the Ollama model
# pull, and the embedding/reranker download + cache warm.
#
# This lives in updateContentCommand rather than postCreateCommand on purpose.
# A Codespaces prebuild runs setup only up to onCreateCommand and
# updateContentCommand, then snapshots the container; postCreateCommand is NOT
# run during a prebuild. Keeping this work here is what lets a prebuilt
# codespace start with the ~1GB model and the HF weights already on disk.
#
# updateContentCommand (not onCreateCommand) because this depends on repo
# source, so it must re-run on every prebuild update. It also runs during
# ordinary non-prebuilt container creation, so local devcontainers behave the
# same.
#
# Nothing here is required reading to do the labs; it's setup plumbing.
set -uo pipefail

export KMP_DUPLICATE_LIB_OK=TRUE

echo "==> Installing advanced-rag-example in editable mode"
pip install --quiet --upgrade pip
pip install --quiet -e ".[dev]"

echo "==> Starting Ollama and pulling the default model (best-effort)"
bash "$(dirname "$0")/start-ollama.sh"
if command -v ollama >/dev/null 2>&1; then
    ollama pull qwen2.5:1.5b-instruct || {
        echo "!! Could not pull qwen2.5:1.5b-instruct (offline network, or Ollama"
        echo "   still starting up). This is fine — labs fall back to RAG_LLM=offline"
        echo "   automatically. Try 'ollama pull qwen2.5:1.5b-instruct' again later."
    }
else
    echo "!! ollama not found on PATH — skipping model pull. The labs still work"
    echo "   fully offline (RAG_LLM=offline is the automatic fallback)."
fi

echo "==> Pre-downloading embedding/reranker models and warming caches"
echo "    (runs the reference solutions once, offline, so this never depends"
echo "     on Ollama being ready yet)"
RAG_IMPL=solutions RAG_LLM=offline python -m ragkit.scoreboard --run || {
    echo "!! Cache warm-up failed non-fatally — the first 'make test' or 'make lab1'"
    echo "   will just take a bit longer while models download."
}
