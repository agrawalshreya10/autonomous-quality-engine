# Changelog

All **notable** changes to this project are recorded here. Routine refactors and typo fixes may be omitted.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers are used when the project cuts explicit releases; otherwise **dated** entries are fine for a portfolio repo.

**Scope:** You can **backfill** older work from `git log` into new `[YYYY-MM-DD]` sections anytime. **Going forward**, add a bullet under `[Unreleased]` (or a new date section when you tag) as part of meaningful PRs—this file does not auto-update.

## [Unreleased]

### Added

- **CI Docker smoke** — GitHub Actions **smoke** job builds `aqe-smoke` (Buildx + GHA cache), runs the container with demo env (no committed `.env`), copies reports via `docker cp`, and uploads **`smoke-report`**. Full **test** job remains host Python.

### Fixed

- **Leave CI flake (demo 403)** — `LeaveListPage` waits for **Module Forbidden** or **Search** (outcome `.or_()`), then raises `PermissionError`; leave regression tests **skip** instead of racing an immediate `is_visible` probe / timing out on Search. Search button uses resilient role+CSS locator (aligned with PIM).
- **CI Docker smoke env** — Smoke container receives `GITHUB_ACTIONS=true` so `pytest_sessionfinish` does not treat containerized CI as a local run and invoke the failure analyzer.
- **Gemini GA model (#32)** — `DEFAULT_GEMINI_MODEL` / allowlist swapped from the decommissioned `gemini-3.1-flash-lite-preview` (shut down 2026-05-25) to GA **`gemini-3.1-flash-lite`**; override option is now GA **`gemini-3.5-flash`** ([#32](https://github.com/agrawalshreya10/autonomous-quality-engine/issues/32)). CI workflow, docs, and governance rule synced.
- **CHANGELOG** — Removed git conflict markers accidentally committed in the previous merge.
- **AI audit (#9)** — Ollama TCP health check honors `OLLAMA_BASE_URL` (host/port) instead of hardcoding `localhost:11434`.
- **AI audit (#10)** — Gemini model allowlist (`ALLOWED_GEMINI_MODELS`) fail-fast rejects decommissioned IDs (e.g. `gemini-1.5-*`) at resolve / client construction.
- **AI audit (#16)** — Explicit `--failures` path that does not exist exits with an error instead of silently falling back to `--artifacts-dir`.
- **Docker non-root runtime** — Smoke image runs as unprivileged user `aqe` (ownership of `/app`, read/exec on `/ms-playwright`) so pytest and Chromium are not root ([#23](https://github.com/agrawalshreya10/autonomous-quality-engine/issues/23)).
- **Docker smoke env** — README uses smoke-only `.env.smoke` / `config/env.smoke.example` instead of general `.env`, so AI keys are not injected into the container ([#24](https://github.com/agrawalshreya10/autonomous-quality-engine/issues/24)).

## [2026-07-29]

### Added

- **Docker (Phase 1)** — Root `Dockerfile` and `.dockerignore` for local-first `pytest -m smoke` (Python 3.12 + Playwright Chromium). `BASE_URL` / credentials remain env-injected. CI image wiring landed later under [Unreleased].
- **ADR** — [`docs/decisions/python-api-vs-typescript-ui.md`](docs/decisions/python-api-vs-typescript-ui.md): Python repo is **API-first**; UI E2E expansion moves to a separate TypeScript Playwright project; freeze growing Python UI coverage (keep thin smoke).
- **Shared AI fix contract** — `ai_audit/fix_suggestion.py` now drives **both** Ollama and Gemini: shared `SYSTEM_PREAMBLE` / `build_analysis_prompt`, `FixSuggestion` schema, `validate_or_fallback`, and **banned-pattern** scan on `fix_markdown` (Selenium / async / `get_by_xpath`, etc.) → `HEURISTIC_FALLBACK`.
- **Unit tests** — `tests/unit/test_fix_suggestion.py` covers valid JSON, invalid category, empty body, fenced JSON, and banned-pattern rejection (no live LLM).

### Changed

- **Roadmap / strategy** — `docs/ARCHITECTURE.md` and `docs/PROJECTSTATUS.md` updated: Phase 1 Docker for current smoke; Phase 2 toward API payloads/clients; UI expansion noted as TS Playwright (separate). Docs index links the new ADR.
- **Gemini structured output** — `GeminiClient` requests JSON via `response_mime_type="application/json"` + `response_schema=FixSuggestion` (`temperature=0`), then the same `validate_or_fallback` path as Ollama.
- **Cursor** — Removed root **`.cursorrules`**; project standards are defined in **`.cursor/rules/*.mdc`**. Removed the obsolete **`.cursor/ai-contract/`** folder (local learning notes can live under **`.cursor/user-docs/`**, gitignored).
- **Documentation** — Added `docs/README.md` as the docs index, removed completed one-off plan files (`docs/plans/plan-dependency-determinism.md`, `docs/plans/plan-cursorrules-split.md`) after the migrations they described, and kept the `google-genai` maintenance note in the docs index and **`.cursor/rules/ai-audit-governance.mdc`** instead of duplicate plans. Standards are enforced in **`.cursor/rules/*.mdc`**. Updated **`ai-audit-governance.mdc`** for dual-provider structured output + policy scan.

## [2026-04-19]

### Added

- **`scripts/run_failure_analyzer.sh`** — Runs `ai_audit.failure_analyzer` with **`.venv/bin/python`** so shells where `python3` is **aliased to Homebrew** (common on macOS) still use project dependencies (`python-dotenv`, etc.). Documented in README.
- **Gemini / Google GenAI SDK doc references** — `docs/reference/gemini-genai-sdk-docs.md` (links to official Gemini libraries page and the Python `genai` generated reference docs); cross-linked from `docs/ARCHITECTURE.md` and `docs/PROJECTSTATUS.md`.
- **`.playwright-browsers/` gitignore** — Added to ignore large local Playwright browser installs.

### Fixed

- **Playwright strict-mode locator violations** — `pages/login_page.py` `error_message` now uses single `.oxd-alert-content-text` instead of union (`.or_()` matched both parent `role=alert` and child text, causing multi-match strict error). Similar fix in `pages/pim/employee_list_page.py` `is_loaded()`.
- **AI Failure Analysis workflow** — Artifact order is **`smoke-report` before `test-report-*`**, and the analyzer **retries** other artifacts if the first exits non-zero (e.g. matrix passed with empty `failures.txt` while smoke failed). The job **no longer fails with exit code 1** when the wrong artifact was tried first; it publishes a summary or successful analysis.
- **Gemini AI audit** — Default and CI model updated to **`gemini-3.1-flash-lite-preview`** (replacing ad-hoc `gemini-3-flash` / older IDs; **`gemini-1.5-*`** is discontinued). Implementation uses **`google-genai`** only — **`genai.Client`** + **`client.models.generate_content`**, with **`HttpOptions(timeout=...)`** so **`timeout_sec`** is honored.

### Changed

- **Repository name** (documentation and packaging): **Autonomous Quality Engine** — `pyproject.toml` project name `autonomous-quality-engine`; README, `docs/ARCHITECTURE.md`, `docs/PROJECTSTATUS.md`, and `config/env.example` titles/paths updated accordingly. Rename the GitHub repository in **Settings** to match when ready.
- **Dependencies** — `requirements.txt` / `pyproject.toml` pinned **`google-genai==1.73.1`** for deterministic installs; documented that **`google-genai`** is the supported Gemini client (not legacy `google-generativeai`).
- **Cursor rules** — `.cursor/rules/ai-audit-governance.mdc` is the canonical Gemini / AI-audit policy; `.cursor/rules/gemini-sdk-migration.mdc` remains a thin legacy-pattern guard to reduce drift.
- **Documentation** — `docs/decisions/playwright-locators-and-logging.md` updated with guidance on avoiding **parent + child** `.or_()` unions that trigger strict-mode violations.

### Documentation

- **`config/env.example`** — Added clarifying comment: "This is the test automation project (AQE); `BASE_URL` and `ORANGEHRM_*` variables point at the OrangeHRM system under test, not separate AQE branding."
- **`README.md`** — Added **Configuration** section clarifying OrangeHRM vs. AQE branding.
- **`docs/ARCHITECTURE.md`** — Updated AI Audit line to reference `DEFAULT_GEMINI_MODEL` in `ai_audit/gemini_client.py` for single source of truth on model ID.

## [2026-04-07]

### Added

- **MIT license** — Root [`LICENSE`](LICENSE) (MIT, copyright 2026 Shreya Agrawal); [`pyproject.toml`](pyproject.toml) `license = { file = "LICENSE" }`; README License section points to the file.

### Fixed

- **AI Failure Analysis** workflow: use **`ACTIONS_ARTIFACT_READ_TOKEN`** (PAT with `actions:read`) for `actions/download-artifact@v4` with `run-id` instead of `GITHUB_TOKEN`, which is scoped only to the current workflow run; document in README, decision doc, and [github-actions-trigger-workflow.md](docs/reference/github-actions-trigger-workflow.md).

## [2026-04-06]

### Added

- **`docs/PROJECTSTATUS.md`** — Renamed from `docs/STATUS.md`; living snapshot of scope, how to run, gaps, and roadmap table.
- **`CHANGELOG.md`** (repo root) — This file.
- **GitHub Actions — AI Failure Analysis** ([`.github/workflows/ai-failure-analysis.yml`](.github/workflows/ai-failure-analysis.yml)): runs on `workflow_run` after **Test Suite** completes with `failure`; downloads test artifacts; optional Gemini analysis with redacted job summary ([decision B+D](docs/decisions/ci-ai-failure-analysis.md)).
- **`docs/reference/`** — Summaries linking to official docs (GitHub Actions: triggers, Docker service containers, Python CI, custom actions, quickstart, licensing; Python docs index; OrangeHRM API/wiki pointers in `ARCHITECTURE.md`).
- **Roadmap phases** in `docs/ARCHITECTURE.md` — Phase 1 Docker, Phase 2 Faker, Phase 3 CI/CD + **Allure** (planned; `allure-pytest` still commented in `requirements.txt`).

### Changed

- **Test workflow** ([`.github/workflows/test.yml`](.github/workflows/test.yml)): removed inline Gemini steps and AI suggestion artifacts from the test job; failure summary points to the separate AI workflow and local analyzer commands.
- **`ai_audit/failure_analyzer`**: failure message truncation; Ollama TCP health check on port 11434; failures file path handling.
- **`ai_audit/gemini_client`**: migrate to `google-genai` (python-genai) SDK (replaces deprecated `google-generativeai`).
- **`ai_audit/ollama_client`**: `requests` to `/api/generate`; `OLLAMA_BASE_URL` / `OLLAMA_MODEL` env support.
- **`tests/conftest.py`**: `pytest_sessionfinish` runs automatic local failure analysis (non-CI) via `failure_analyzer` when the session fails and `reports/failures.txt` exists.
- **Dependencies** (`requirements.txt`, `pyproject.toml`): `requests`, `google-genai`.

### Documentation

- **`docs/ARCHITECTURE.md`**: AI integration, phased roadmap, reference doc tables, OrangeHRM documentation summary.
