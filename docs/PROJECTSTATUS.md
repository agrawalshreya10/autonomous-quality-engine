# Autonomous Quality Engine — project status

**Last updated:** 2026-04-06 — Roadmap phased (P1 Docker, P2 Faker data, **P3 CI/CD + Allure reporting**); see [ARCHITECTURE.md](ARCHITECTURE.md#roadmap--gaps-ref-projectstatusmd). **Automatic Local Failure Analysis via Ollama** and CI B+D AI workflow unchanged.

This file summarizes what is implemented, what is thin or missing, and how to run the suite locally. Refresh it when the codebase or test scope changes significantly. **Chronological notable changes** are recorded in [CHANGELOG.md](../CHANGELOG.md) at the repository root.

---

## How to run locally

1. **Python** — Use 3.11+ (see `pyproject.toml` / README).

2. **Create and activate a virtual environment** (from project root):
   ```bash
   python -m venv .venv
   source .venv/bin/activate    # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (required once per machine):
   ```bash
   playwright install chromium
   ```
   Or `playwright install` for all browsers.

5. **Optional — environment file** — Copy `config/env.example` to `.env` and set `BASE_URL` (scheme, host, port, path—no trailing slash), `IGNORE_HTTPS_ERRORS` for local self-signed HTTPS, plus `BROWSER`, `HEADLESS`, `TIMEOUT_MS`, `ORANGEHRM_USER`, `ORANGEHRM_PASSWORD`. Default `BASE_URL` in code targets the public demo if unset (e.g. CI).

6. **Run tests** (from project root):
   ```bash
   pytest
   pytest -m smoke
   pytest -n auto
   pytest tests/smoke/
   pytest tests/regression/ -m pim
   ```

7. **Reports** — `reports/report.html`, `reports/screenshots/` (on failure), `reports/failures.txt` (for AI audit). After a **local** failed run with Ollama up, `reports/ai_suggestions.md` holds model output (same path when using `--out` manually).

8. **AI failure analysis** — **Automatic Local Failure Analysis via Ollama**: When tests fail locally, Ollama automatically analyzes failures with smart truncation (2K char limit) and enhanced prompts; output is written to `reports/ai_suggestions.md`. Manual: **`./scripts/run_failure_analyzer.sh`** (uses `.venv`; avoids macOS `python3` → Homebrew alias issues) or `.venv/bin/python -m ai_audit.failure_analyzer …`. Gemini (requires `GEMINI_API_KEY`): add `--client gemini --model gemini-2.5-flash`. CI uses separate on-demand analysis workflow (see [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md)).

---

## Scope and size

- First-party Python is on the order of **~900+ lines** across `core/`, `config/`, `pages/`, `tests/`, `utils/`, and `ai_audit/` (excluding virtualenvs).
- The project is a **small vertical slice**, not a stub: driver, POM, fixtures, CI, and AI failure analysis are wired end-to-end.

## Roadmap phases (see [ARCHITECTURE.md](ARCHITECTURE.md#roadmap--gaps-ref-projectstatusmd))

| Phase | Focus |
|-------|--------|
| **1** | **Infrastructure** — Dockerization for CI/local parity; service containers as needed. |
| **2** | **Data** — Move from static JSON to **Faker** (or similar) for runtime test data. |
| **3** | **CI/CD & reporting** — Pipeline hardening plus **Allure** (`allure-pytest`) alongside **pytest-html**; dependency remains commented in `requirements.txt` until this phase. |

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
| **AI audit** | **Automatic Local Failure Analysis via Ollama** (pytest hook), `GeminiClient` (`gemini-2.5-flash`); `failure_analyzer --client ollama\|gemini` with smart truncation |
| **CI** (`.github/workflows/test.yml`) | Smoke job + full suite with pytest-xdist, artifacts; separate AI failure analysis workflow ([ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml)) |

There are no `TODO` / `FIXME` markers in first-party project code under `core/`, `config/`, `pages/`, `tests/`, `ai_audit/`, or `utils/`.

---

## Gaps and incomplete areas

1. **Coverage vs. README** — Only a subset of OrangeHRM flows is covered. Other modules (admin, recruitment, time, performance, etc.) are not implemented.

2. **`utils/` integration** — **Resolved:** `truncate_for_log`, interaction loggers, and `BasePage` are wired; all page objects route critical actions through `self.click` / `self.fill` with descriptive `element_label` values.

3. **`ai_audit` backends** — **Resolved:** `LLMClient` is implemented by **Ollama** (default, local) and **Gemini** (`GeminiClient`, `GEMINI_API_KEY`, `--client gemini`). Default Gemini model is **`gemini-2.5-flash`** (Google retired `gemini-1.5-flash` for `generateContent`).

4. **Test rigor** — Some assertions are loose (e.g. PIM search allows zero rows; add-employee uses fixed names).

5. **`pages/__init__.py`** — Re-exports only `LoginPage` and `DashboardPage`.

---

## Maintenance

- Update this file when adding modules, tests, or changing architecture.
- After major changes, bump **Last updated** and adjust the tables/sections above.
- Log **notable** user-facing or structural changes in [CHANGELOG.md](../CHANGELOG.md); use git history for line-level archaeology.
