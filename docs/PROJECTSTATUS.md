# Autonomous Quality Engine — project status

**Last updated:** 2026-08-03 — Strategy: **Python = API-first**; UI E2E expansion moves to a **separate TypeScript Playwright** project; freeze growing Python UI coverage (keep thin smoke). **Phase 1 Docker complete** (local + CI smoke image). **Next: Phase 3** (CI gates, traces, Allure, flake policy, portfolio packaging) for demo readiness; **Phase 2** (API clients/contracts) follows. See [ARCHITECTURE.md](ARCHITECTURE.md#roadmap--gaps-ref-projectstatusmd) and [decisions/python-api-vs-typescript-ui.md](decisions/python-api-vs-typescript-ui.md). AI audit B+D unchanged.

This file summarizes what is implemented, what is thin or missing, and how to run the suite locally. Refresh it when the codebase or test scope changes significantly. **Chronological notable changes** are recorded in [CHANGELOG.md](../CHANGELOG.md) at the repository root.

---

## How to run locally

1. **Python** — Use 3.12+ (see `pyproject.toml` / README).

2. **Create and activate a virtual environment** (from project root):
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (required once per machine):
   ```bash
   PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers .venv/bin/playwright install chromium
   ```
   Or `PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers .venv/bin/playwright install` for all browsers.

5. **Optional — environment file** — Copy `config/env.example` to `.env` and set `BASE_URL` (scheme, host, port, path—no trailing slash), plus `BROWSER`, `HEADLESS`, `TIMEOUT_MS`, `ORANGEHRM_USER`, `ORANGEHRM_PASSWORD`. The template sets **`IGNORE_HTTPS_ERRORS=false`** (full TLS validation); set **`true` only** for local self-signed HTTPS—see the warning block in `config/env.example`. Default `BASE_URL` in code targets the public demo if unset (e.g. CI).

6. **Run tests** (from project root):
   ```bash
   .venv/bin/pytest
   .venv/bin/pytest -m smoke
   .venv/bin/pytest -n auto
   .venv/bin/pytest tests/smoke/
   .venv/bin/pytest tests/regression/ -m pim
   ```

7. **Reports** — `reports/report.html`, `reports/screenshots/` (on failure), `reports/failures.txt` (for AI audit). After a **local** failed run with Ollama up, `reports/ai_suggestions.md` holds model output (same path when using `--out` manually).

8. **Docker (Phase 1 smoke — complete)** — Build and run the smoke suite in a container (no host `.venv` required; image runs as non-root `aqe`). Same image is used by the GitHub Actions **smoke** job. Pass `BASE_URL` / credentials via `-e` or smoke-only `.env.smoke` (`config/env.smoke.example`) — never bake secrets into the image, and do not pass general `.env` (AI keys). See root [README.md](../README.md#docker-local-smoke).

9. **AI failure analysis** — **Automatic Local Failure Analysis via Ollama**: When tests fail locally, Ollama automatically analyzes failures with smart truncation (2K char limit) and enhanced prompts; output is written to `reports/ai_suggestions.md`. Manual: **`./scripts/run_failure_analyzer.sh`** (uses `.venv`; avoids macOS `python3` → Homebrew alias issues) or `.venv/bin/python -m ai_audit.failure_analyzer …`. Gemini (requires `GEMINI_API_KEY`): add `--client gemini --model gemini-3.1-flash-lite` (or omit `--model` to use the default). CI uses separate on-demand analysis workflow (see [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md)). Reference docs for the SDK + API surface: [reference/gemini-genai-sdk-docs.md](reference/gemini-genai-sdk-docs.md).

---

## Scope and size

- First-party Python is on the order of **~900+ lines** across `core/`, `config/`, `pages/`, `tests/`, `utils/`, and `ai_audit/` (excluding virtualenvs).
- The project is a **small vertical slice**, not a stub: driver, POM, fixtures, CI, and AI failure analysis are wired end-to-end.

## Strategy (API-first)

- **Python (this repo):** Keep **thin UI smoke** only — do not expand page objects or UI regression depth. **Build order:** finish **Phase 3** demo CI/observability, then **Phase 2** API clients + contract suite.
- **TypeScript Playwright (separate project):** Owns broader UI E2E when that repo exists.
- **Decision:** [decisions/python-api-vs-typescript-ui.md](decisions/python-api-vs-typescript-ui.md).

## Roadmap phases (see [ARCHITECTURE.md](ARCHITECTURE.md#roadmap--gaps-ref-projectstatusmd))

**Execution order:** 1 *(done)* → **3 *(next)*** → **2 *(after demo)*** → Later.

| Phase | Status | Focus |
|-------|--------|--------|
| **1** | **Done** | **Infrastructure** — `Dockerfile` + CI **smoke** on `aqe-smoke` (Buildx/GHA cache, `docker cp` → `smoke-report`); non-root `aqe`; `.env.smoke`. Full **test** job remains host Python. |
| **3** | **Next (demo)** | **CI quality system** — unit→smoke→full DAG; traces-on-failure; JUnit; Allure + pytest-html; flake/quarantine policy; optional GHCR/cache; README CI diagram/badges. |
| **2** | **After Phase 3** | **API-first** — REST clients, runtime payloads (e.g. Faker), **contract-oriented** suite for a fast CI gate; not Python UI expansion. |

---

## What is implemented and working (as of last update)

| Area | Notes |
|------|--------|
| **Browser lifecycle** (`core/driver.py`) | Chromium / Firefox / WebKit launch, context with `base_url`, timeouts |
| **POM** (`core/base_page.py`, `core/page_factory.py`) | `click`/`fill` with mandatory `element_label`, `_run` try/except, resilient `or_` helpers (CSS, role button/menuitem, placeholder), `expect` before click/fill |
| **Config** (`config/settings.py`) | Pydantic settings, env / `.env` |
| **Pages** | Login, dashboard, PIM (employee list + add employee), leave list — all use `BasePage` interactions |
| **Tests** | 3 smoke + 5 regression (PIM + leave) |
| **Fixtures** (`tests/conftest.py`) | `page`, `page_factory`, `logged_in_page_factory`, failure screenshots, `failures.txt` |
| **AI audit** | **Automatic Local Failure Analysis via Ollama** (pytest hook), `GeminiClient` (`gemini-3.1-flash-lite`); `failure_analyzer --client ollama\|gemini` with smart truncation |
| **CI** (`../.github/workflows/test.yml`) | **smoke** builds/runs `aqe-smoke` (artifact `smoke-report`); **test** is host Python + pytest-xdist; separate AI failure analysis workflow ([ai-failure-analysis.yml](../.github/workflows/ai-failure-analysis.yml)) |

There are no `TODO` / `FIXME` markers in first-party project code under `core/`, `config/`, `pages/`, `tests/`, `ai_audit/`, or `utils/`.

---

## Gaps and incomplete areas

1. **Coverage vs. README** — Only a subset of OrangeHRM flows is covered. **By design (2026-07-27):** do not expand Python UI coverage; deeper UI E2E moves to a separate TypeScript Playwright project. Near-term growth is **Phase 3** CI/observability for demos, then **Phase 2** API/contracts.

2. **`utils/` integration** — **Resolved:** `truncate_for_log`, interaction loggers, and `BasePage` are wired; all page objects route critical actions through `self.click` / `self.fill` with descriptive `element_label` values.

3. **`ai_audit` backends** — **Resolved:** `LLMClient` is implemented by **Ollama** (default, local) and **Gemini** (`GeminiClient`, `GEMINI_API_KEY`, `--client gemini`). Default Gemini model is **`gemini-3.1-flash-lite`** (see `.cursor/rules/ai-audit-governance.mdc`).

4. **Test rigor** — Some assertions are loose (e.g. PIM search allows zero rows; add-employee uses fixed names).

5. **`pages/__init__.py`** — Re-exports only `LoginPage` and `DashboardPage`.

6. **Phase 3 gaps (demo)** — No Allure yet; no traces-on-failure artifact policy; no unit→smoke→full DAG; flake/quarantine policy not codified; portfolio CI diagram/badges thin.

---

## Maintenance

- Update this file when adding modules, tests, or changing architecture.
- After major changes, bump **Last updated** and adjust the tables/sections above.
- Log **notable** user-facing or structural changes in [CHANGELOG.md](../CHANGELOG.md); use git history for line-level archaeology.
