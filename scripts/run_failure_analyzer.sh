#!/usr/bin/env bash
# Always use the repo virtualenv's Python so shell aliases (e.g. python3 -> Homebrew)
# cannot bypass .venv — see README "AI failure analysis".
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "error: ${PY} not found or not executable." >&2
  echo "From the repo root, run:" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install -U pip" >&2
  echo "  .venv/bin/python -m pip install -r requirements.txt" >&2
  exit 1
fi
exec "$PY" -m ai_audit.failure_analyzer "$@"
