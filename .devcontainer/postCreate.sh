#!/usr/bin/env bash
# Runs when a Codespace (or local devcontainer) is created, after
# updateContent.sh has done the heavy installing. Deliberately kept cheap:
# postCreateCommand is skipped during a Codespaces prebuild, so anything slow
# put here would be paid by every participant instead of once by the prebuild.
#
# Nothing here is required reading to do the labs; it's setup plumbing.
set -uo pipefail

export KMP_DUPLICATE_LIB_OK=TRUE

if ! python -c "import ragkit" >/dev/null 2>&1; then
    echo "!! ragkit is not importable — re-running the content setup"
    bash "$(dirname "$0")/updateContent.sh"
fi

echo "==> Setup complete. Try:"
echo "      make test          # run the fixed tests against your labs/ code"
echo "      make compare Q=\"What causes error E-4021?\""
echo "      make scoreboard    # see all four pipelines' measured scores"
