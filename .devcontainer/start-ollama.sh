#!/usr/bin/env bash
# Starts `ollama serve` in the background unless it is already listening.
# Idempotent: run by postCreateCommand (first build) and by postStartCommand
# (every container start, since postCreate only ever runs once).
set -uo pipefail

READY_URL="http://localhost:11434/api/tags"

# Self-heal containers created before install-ollama.sh existed: onCreateCommand
# never re-runs for an existing container, so install here instead of degrading.
if ! command -v ollama >/dev/null 2>&1; then
    echo "==> ollama not on PATH — installing it now"
    bash "$(dirname "$0")/install-ollama.sh" || true
fi

if ! command -v ollama >/dev/null 2>&1; then
    echo "!! ollama not on PATH — labs fall back to RAG_LLM=offline."
    exit 0
fi

if curl -sf -m 2 "$READY_URL" >/dev/null 2>&1; then
    echo "==> Ollama already serving on :11434"
    exit 0
fi

echo "==> Starting ollama serve"
nohup ollama serve >/tmp/ollama.log 2>&1 &

for _ in $(seq 1 30); do
    if curl -sf -m 2 "$READY_URL" >/dev/null 2>&1; then
        echo "==> Ollama ready on :11434"
        exit 0
    fi
    sleep 1
done

echo "!! Ollama did not become ready within 30s — see /tmp/ollama.log"
exit 0
