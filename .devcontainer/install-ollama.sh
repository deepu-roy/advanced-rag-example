#!/usr/bin/env bash
# Installs the Ollama binary from the official GitHub release tarball.
#
# We deliberately do NOT use https://ollama.com/install.sh (nor the
# ghcr.io/prulloac/devcontainer-features/ollama feature, which is just a thin
# wrapper around it): ollama.com is blocked by egress policy in this
# environment, so that installer always fails. github.com (binaries) and
# registry.ollama.ai (model pulls) are both reachable, so we use those.
set -euo pipefail

OLLAMA_VERSION="${OLLAMA_VERSION:-v0.33.3}"
PREFIX="${PREFIX:-/usr/local}"

if command -v ollama >/dev/null 2>&1; then
    echo "==> ollama already installed: $(ollama --version 2>/dev/null | head -1 || true)"
    exit 0
fi

case "$(uname -m)" in
    x86_64) ARCH=amd64 ;;
    aarch64 | arm64) ARCH=arm64 ;;
    *)
        echo "!! Unsupported architecture: $(uname -m)" >&2
        exit 1
        ;;
esac

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

echo "==> Installing prerequisites (ca-certificates, curl, zstd)"
$SUDO apt-get update -y
$SUDO apt-get install -y --no-install-recommends ca-certificates curl zstd

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

BASE="https://github.com/ollama/ollama/releases/download/${OLLAMA_VERSION}"

echo "==> Downloading ollama ${OLLAMA_VERSION} (linux/${ARCH})"
# Releases moved from .tgz to .tar.zst; try the current name, then the legacy one.
if curl -fsSL -o "$TMP/ollama.tar.zst" "${BASE}/ollama-linux-${ARCH}.tar.zst"; then
    $SUDO tar -C "$PREFIX" --zstd -xf "$TMP/ollama.tar.zst"
elif curl -fsSL -o "$TMP/ollama.tgz" "${BASE}/ollama-linux-${ARCH}.tgz"; then
    $SUDO tar -C "$PREFIX" -xzf "$TMP/ollama.tgz"
else
    echo "!! Could not download ollama ${OLLAMA_VERSION} for linux/${ARCH}." >&2
    echo "   The labs still work fully offline (RAG_LLM=offline)." >&2
    exit 1
fi

$SUDO chmod +x "${PREFIX}/bin/ollama"
echo "==> Installed: $("${PREFIX}/bin/ollama" --version 2>/dev/null | head -1 || true)"
