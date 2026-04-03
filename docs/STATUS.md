# OrangeHRM Playwright — project status

**Last updated:** 2026-04-01 — Swapped `OpenAIClient` for `GeminiClient` (`gemini-1.5-flash`); `failure_analyzer --client gemini`; ARCHITECTURE.md roadmap updated with CodeRabbit (planned) and Gemini CI audit (done).

This file summarizes what is implemented, what is thin or missing, and how to run the suite locally. Refresh it when the codebase or test scope changes significantly.

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

7. **Reports** — `reports/report.html`, `reports/screenshots/` (on failure), `reports/failures.txt` (for AI audit).

8. **AI failure analysis** — Local Ollama: `python -m ai_audit.failure_analyzer --artifacts-dir reports`. Gemini (requires `GEMINI_API_KEY` in `.env` or environment): `python -m ai_audit.failure_analyzer --client gemini --model gemini-1.5-flash --artifacts-dir reports`.

---

## Scope and size

- First-party Python is on the order of **~900+ lines** across `core/`, `config/`, `pages/`, `tests/`, `utils/`, and `ai_audit/` (excluding virtualenvs).
- The project is a **small vertical slice**, not a stub: driver, POM, fixtures, CI, and AI failure analysis are wired end-to-end.

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
| **AI audit** | `OllamaClient` (local), `GeminiClient` (`gemini-1.5-flash`); `failure_analyzer --client ollama\|gemini` |
| **CI** (`.github/workflows/test.yml`) | Smoke job + full suite with pytest-xdist, artifacts |

There are no `TODO` / `FIXME` markers in first-party project code under `core/`, `config/`, `pages/`, `tests/`, `ai_audit/`, or `utils/`.

---

## Gaps and incomplete areas

1. **Coverage vs. README** — Only a subset of OrangeHRM flows is covered. Other modules (admin, recruitment, time, performance, etc.) are not implemented.

2. **`utils/` integration** — **Resolved:** `truncate_for_log`, interaction loggers, and `BasePage` are wired; all page objects route critical actions through `self.click` / `self.fill` with descriptive `element_label` values.

3. **`ai_audit` backends** — **Resolved:** `LLMClient` is implemented by **Ollama** (default, local) and **Gemini** (`GeminiClient`, `GEMINI_API_KEY`, `--client gemini`). Free tier of Gemini 1.5 Flash covers portfolio-scale usage.

4. **Test rigor** — Some assertions are loose (e.g. PIM search allows zero rows; add-employee uses fixed names).

5. **`pages/__init__.py`** — Re-exports only `LoginPage` and `DashboardPage`.

---

## Maintenance

- Update this file when adding modules, tests, or changing architecture.
- After major changes, bump **Last updated** and adjust the tables/sections above.
