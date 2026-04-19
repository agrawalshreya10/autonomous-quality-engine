## Goal

Make the AI audit dependency on `google-genai` deterministic (no loose version range) so Gemini SDK behavior is stable and reproducible across machines/CI. We’ll worry about longer-term maintenance later.

## Constraints / assumptions

- Pin to an **exact** version that is known to exist on PyPI and compatible with our current `GeminiClient` usage.
- Apply the pin consistently in both `requirements.txt` (pip installs) and `pyproject.toml` (packaging metadata / dependency resolution).

## Execution steps

- Identify the latest available stable `google-genai` release (via `pip index versions google-genai`).
- Update:
  - `requirements.txt`: `google-genai==<version>`
  - `pyproject.toml`: `google-genai==<version>`
- Run a quick validation:
  - `python -c "from google import genai; from google.genai import types; print('ok')"`
  - `pytest -m smoke` (and optionally `pytest -m regression` if time permits).

