# Changelog

All **notable** changes to this project are recorded here. Routine refactors and typo fixes may be omitted.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers are used when the project cuts explicit releases; otherwise **dated** entries are fine for a portfolio repo.

**Scope:** You can **backfill** older work from `git log` into new `[YYYY-MM-DD]` sections anytime. **Going forward**, add a bullet under `[Unreleased]` (or a new date section when you tag) as part of meaningful PRs—this file does not auto-update.

## [Unreleased]

### Changed

- **Cursor** — Removed root **`.cursorrules`**; project standards are defined in **`.cursor/rules/*.mdc`**. Removed the obsolete **`.cursor/ai-contract/`** folder (local learning notes can live under **`.cursor/user-docs/`**, gitignored).
- **Documentation** — Added `docs/README.md` as the docs index, removed completed one-off plan files (`docs/plans/plan-dependency-determinism.md`, `docs/plans/plan-cursorrules-split.md`) after the migrations they described, and kept the `google-genai` maintenance note in the docs index and **`.cursor/rules/ai-audit-governance.mdc`** instead of duplicate plans. Standards are enforced in **`.cursor/rules/*.mdc`**.

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
