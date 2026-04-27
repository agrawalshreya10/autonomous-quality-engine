# Autonomous Quality Engine

Enterprise-grade **Playwright** (Python) automation for **OrangeHRM**, using **Page Object Model** with **Factory Pattern**, **GitHub Actions** CI/CD, and optional **AI failure analysis** (Ollama or Gemini).

**System under test (default):** the **public demo** only — base URL `https://opensource-demo.orangehrmlive.com/` (e.g. [demo login](https://opensource-demo.orangehrmlive.com/web/index.php/auth/login)). CI and the default `BASE_URL` in [`config/env.example`](config/env.example) use this host. The suite is **not** aimed at OrangeHRM’s marketing site, customer production tenants, or any live product URL other than that shared demo (or whatever you set in `BASE_URL` for local/Docker instances).

*Product reference:* [OrangeHRM](https://www.orangehrm.com/) (for product information only; the vendor site is not a test target).

## Features

- **Playwright + Python**: Cross-browser, auto-waiting, traces and screenshots
- **POM + Factory**: `core/base_page.py`, `core/page_factory.py`, page classes in `pages/`
- **pytest**: Markers (`smoke`, `regression`, `pim`, `leave`), fixtures, parallel with **pytest-xdist**
- **Reporting**: pytest-html report in `reports/`; screenshots on failure
- **CI/CD**: GitHub Actions on push/PR; smoke job + full suite; upload reports as artifacts
- **AI audit**: **Ollama** (local) or **Gemini** (cloud); optional auto-run after local failures; see [AI failure analysis](#ai-failure-analysis)
- **Docs map**: [`docs/README.md`](docs/README.md) links architecture, decisions, historical plans, and reference notes.

## Requirements

- Python 3.12+
- Playwright browsers (see below)

## Setup

Use a **Python 3.12+** interpreter (see `pyproject.toml`). Prefer **explicit `.venv/bin/...` paths** for installs and Playwright so you never hit macOS **Homebrew `python3` / `pip` aliases** that skip the project venv.

```bash
# Clone and enter project
cd autonomous-quality-engine

# Create venv (pick the command that resolves to Python 3.12+ on your machine)
python3.12 -m venv .venv
# or: python3 -m venv .venv

# Install dependencies (no need to activate the venv first)
.venv/bin/python -m pip install -U pip
.venv/bin/pip install -r requirements.txt

# Install Playwright browsers (required once; browsers live under .playwright-browsers/)
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers .venv/bin/playwright install chromium
# Or all browsers:
# PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers .venv/bin/playwright install

# Optional: copy env template and adjust
cp config/env.example .env
```

Optional: `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`) if you prefer shorter commands in an interactive shell; the **Running tests** section still uses `.venv/bin/pytest` so behavior matches CI and project rules without relying on activation.

### Cursor MCP (optional)

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers, when you add them in your local config, can provide Playwright browser inspection, HTTP fetch, git operations, and database access to Cursor’s AI assistant. **Do not commit** a real `.cursor/mcp.json` — it often contains **machine paths** and **secrets** (e.g. database URLs). That path is intentionally untracked (see [`.gitignore`](.gitignore)); the only MCP config tracked in the repo is [`.cursor/mcp.json.example`](.cursor/mcp.json.example), which you copy locally as `.cursor/mcp.json`.

**Setup:** copy the example and edit it locally. Cursor reads `.cursor/mcp.json` in this repo; keep your secrets only on your machine.

```bash
cp .cursor/mcp.json.example .cursor/mcp.json
# Edit .cursor/mcp.json: set git repo path, MYSQL_URL, or remove servers you do not use.
```

The committed **[`.cursor/mcp.json.example`](.cursor/mcp.json.example)** shows the same *shape* as a typical config (Playwright MCP, optional fetch, git, optional MySQL). Replace placeholders; use `npx` for `command` where possible so paths match other developers. Remove any server block you do not need.

## Running tests

Always run **`.venv/bin/pytest`** (or activate the venv and still use the prefix when unsure). Do not rely on a bare `pytest` on PATH — on macOS it often picks the wrong environment.

```bash
# All tests (report in reports/report.html)
.venv/bin/pytest

# Smoke only (fast)
.venv/bin/pytest -m smoke

# Full regression marker
.venv/bin/pytest -m regression

# Module markers (see pyproject.toml)
.venv/bin/pytest tests/regression/ -m pim
.venv/bin/pytest tests/regression/ -m leave

# Parallel (multiple workers)
.venv/bin/pytest -n auto
# Or: .venv/bin/pytest -n 4

# Specific directories
.venv/bin/pytest tests/smoke/
.venv/bin/pytest tests/regression/
```

## CI/CD (GitHub Actions)

- **Trigger**: Push or PR to `main`/`master`; or run manually via **Actions** tab.
- **Workflow** [`.github/workflows/test.yml`](.github/workflows/test.yml) (**Test Suite**):
  - **smoke**: Runs `pytest -m smoke`, uploads `smoke-report` artifact.
  - **test**: Full suite with `pytest -n auto`, uploads `test-report-3.12` artifact.
- **Artifacts**: Download from the run summary to get `reports/report.html` and `reports/screenshots/`.
- **AI failure analysis (CI)**: On **Test Suite** failure, [`.github/workflows/ai-failure-analysis.yml`](.github/workflows/ai-failure-analysis.yml) downloads artifacts from that run and can run Gemini-based analysis. Requires repository secrets **`ACTIONS_ARTIFACT_READ_TOKEN`** (PAT with **Actions: Read** on the repo — `GITHUB_TOKEN` cannot download another run’s artifacts) and optional **`GEMINI_API_KEY`**. See [docs/decisions/ci-ai-failure-analysis.md](docs/decisions/ci-ai-failure-analysis.md) and [reference/github-actions-trigger-workflow.md](docs/reference/github-actions-trigger-workflow.md). Run the analyzer locally using the commands in [AI failure analysis](#ai-failure-analysis).

## AI failure analysis

Provider selection is explicit via **`AI_PROVIDER`** in `.env` (`ollama` or `gemini`; default **`ollama`** if unset). Copy [`config/env.example`](config/env.example) and set `GEMINI_API_KEY` when using Gemini.

**Use the project venv for every CLI invocation.** On macOS, `python3` is often **aliased to Homebrew** (ignores `.venv`), which causes `ModuleNotFoundError: dotenv` and other missing packages. Prefer one of these — they always use **`.venv/bin/python`**:

```bash
# Recommended: wrapper (works no matter how python3 is aliased)
./scripts/run_failure_analyzer.sh --help

# Equivalent explicit form
.venv/bin/python -m ai_audit.failure_analyzer --help
```

If `.venv` is missing or dependencies are not installed, from the **repository root** (use a **3.12+** interpreter to create the venv):

```bash
python3.12 -m venv .venv
# or: python3 -m venv .venv
.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements.txt
PLAYWRIGHT_BROWSERS_PATH=.playwright-browsers .venv/bin/playwright install chromium
```

### Local Ollama (default)

1. Install [Ollama](https://ollama.ai) and pull a model (default in this repo is **`llama3`**):
   ```bash
   ollama pull llama3
   ```
2. After test failures, `reports/failures.txt` is written; on **non-CI** runs the pytest session may also write **`reports/ai_suggestions.md`** automatically when Ollama is reachable.
3. Run the analyzer manually if needed (examples use the wrapper; add `--client ollama` if `.env` sets `AI_PROVIDER=gemini`):
   ```bash
   # From project root, with reports/ present (e.g. after a failed run)
   ./scripts/run_failure_analyzer.sh --artifacts-dir reports

   # After downloading CI artifacts (extract so failures.txt lives under that folder)
   ./scripts/run_failure_analyzer.sh --client ollama --artifacts-dir /path/to/smoke-report

   # Write suggestions to a file
   ./scripts/run_failure_analyzer.sh --artifacts-dir reports --out reports/ai_suggestions.md

   # Point at a failures file (TEST: / MESSAGE: blocks) instead of scanning artifacts
   ./scripts/run_failure_analyzer.sh --failures path/to/failures.txt --out suggestions.md
   ```

### Gemini (cloud)

Set `AI_PROVIDER=gemini` and `GEMINI_API_KEY` in `.env` (or export for the shell). CI uses the same variables in the AI Failure Analysis workflow.

```bash
# --model optional: omit to use DEFAULT_GEMINI_MODEL in ai_audit/gemini_client.py (gemini-3.1-flash-lite-preview)
AI_PROVIDER=gemini ./scripts/run_failure_analyzer.sh --client gemini --model gemini-3.1-flash-lite-preview --artifacts-dir reports
```

`gemini-1.5-*` model IDs are **not** supported here (decommissioned); use `gemini-3.1-flash-lite-preview` (default) or `gemini-3.1-flash-preview` as an explicit override. See **`.cursor/rules/ai-audit-governance.mdc`** for the canonical policy.

Optional one-shot override without changing `.env`: `--client gemini` or `--client ollama` (see `./scripts/run_failure_analyzer.sh --help`).

## Project structure

```
autonomous-quality-engine/
├── .cursor/mcp.json.example                    # Commit: sample MCP config (copy to .cursor/mcp.json)
├── .github/workflows/test.yml                 # CI: smoke + full test (Test Suite)
├── .github/workflows/ai-failure-analysis.yml  # Optional Gemini analysis after Test Suite failure
├── scripts/run_failure_analyzer.sh            # Run analyzer with .venv (avoids macOS python3 alias issues)
├── config/                      # Settings, env
├── core/                        # Driver, BasePage, PageFactory
├── pages/                       # POM: login, dashboard, pim, leave
├── tests/                       # Smoke + regression
│   ├── conftest.py              # Fixtures, screenshot on failure, failures.txt
│   ├── smoke/
│   └── regression/
├── utils/                       # Logger, helpers
├── ai_audit/                    # LLM client (Ollama), failure_analyzer
├── reports/                     # HTML report, screenshots (gitignored)
├── requirements.txt
├── pyproject.toml               # Pytest config, markers
├── CHANGELOG.md                 # Notable changes (Keep a Changelog)
└── README.md
```

## Configuration

**OrangeHRM vs. this repo:** `BASE_URL`, `ORANGEHRM_USER`, and `ORANGEHRM_PASSWORD` point at the **OrangeHRM** app you are testing (default: the public demo). They are not separate branding for the Autonomous Quality Engine project itself — see the note at the top of [`config/env.example`](config/env.example).

Env vars (or `.env`): `BASE_URL`, `BROWSER`, `HEADLESS`, `TIMEOUT_MS`, `ORANGEHRM_USER`, `ORANGEHRM_PASSWORD`, `IGNORE_HTTPS_ERRORS` (local HTTPS). For AI audit: `AI_PROVIDER`, `GEMINI_API_KEY` (Gemini), optional `OLLAMA_MODEL` / `OLLAMA_BASE_URL`. See [`config/env.example`](config/env.example).

## Contributing and pull requests

- **Standards:** Follow **`.cursor/rules/*.mdc`** (POM, locators, `expect`, logging; see `playwright-core-sync.mdc` and `page-object-standards.mdc`). Design notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); project snapshot: [docs/PROJECTSTATUS.md](docs/PROJECTSTATUS.md); notable changes: [CHANGELOG.md](CHANGELOG.md); locator/logging decisions: [docs/decisions/playwright-locators-and-logging.md](docs/decisions/playwright-locators-and-logging.md).
- **CodeRabbit:** [CodeRabbit](https://coderabbit.ai) is configured for the GitHub repository and can catch drift from those rules (e.g. missing `element_label`, raw `page` clicks on critical paths). Treat its output as advisory; **`.cursor/rules/`** and the decision docs remain authoritative for merges.
- **PR template:** Opening a PR loads [`.github/pull_request_template.md`](.github/pull_request_template.md) — complete the checklist and confirm tests were run.

## License

This repository is released under the [MIT License](LICENSE). Original portfolio project by Shreya Agrawal. OrangeHRM is a trademark of OrangeHRM Inc.