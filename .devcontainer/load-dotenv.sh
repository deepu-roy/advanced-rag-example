#!/usr/bin/env bash
# Exports KEY=VALUE pairs from the repo-root .env into the current shell.
#
# Meant to be *sourced*, not executed: by ~/.bashrc (so every integrated
# terminal sees HF_TOKEN) and by the setup scripts (so model downloads run
# authenticated). The repo-root .env is gitignored and stays on your machine.
#
# Values are parsed, never eval'd or sourced, so a stray backtick or $(...) in
# .env cannot execute anything. Already-set variables win, which keeps
# Codespaces secrets authoritative over a leftover local .env.

__load_dotenv_file() {
    local file="$1" line key val
    [ -r "$file" ] || return 0
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line#"${line%%[![:space:]]*}"}"
        case "$line" in
            '' | '#'*) continue ;;
            *=*) ;;
            *) continue ;;
        esac
        line="${line#export }"
        key="${line%%=*}"
        val="${line#*=}"
        key="${key//[[:space:]]/}"
        [ -n "$key" ] || continue
        # Strip one layer of matching surrounding quotes.
        case "$val" in
            \"*\" | \'*\') val="${val:1:${#val}-2}" ;;
        esac
        [ -n "${!key:-}" ] && continue
        export "$key=$val"
    done < "$file"
}

__load_dotenv_file "${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env}"
unset -f __load_dotenv_file
