# Autonomous Quality Engine

Enterprise-grade **Playwright** (Python) automation for **OrangeHRM**, using **Page Object Model** with **Factory Pattern**, **GitHub Actions** CI/CD, and optional **AI failure analysis** (Ollama or Gemini).

**System under test (default):** the **public demo** only — base URL `https://opensource-demo.orangehrmlive.com/` (e.g. [demo login](https://opensource-demo.orangehrmlive.com/web/index.php/auth/login)). CI and the default `BASE_URL` in [`config/env.example`](config/env.example) use this host. The suite is **not** aimed at OrangeHRM’s marketing site, customer production tenants, or any live product URL other than that shared demo (or whatever you set in `BASE_URL` for local/Docker instances).

*Product reference:* [OrangeHRM](https://www.orangehrm.com/) (vendor / product information only, not an automation target.)

## Features

- **Playwright + Python**: Cross-browser, auto-waiting, traces and screenshots
- **POM + Factory**: `core/base_page.py`, `core/page_factory.py`, page classes in `pages/`
- **pytest**: Markers (`smoke`, `regression`, `pim`, `leave`), fixtures, parallel with **pytest-xdist**
- **Reporting**: pytest-html report in `reports/`; screenshots on failure
- **CI/CD**: GitHub Actions on push/PR; smoke job + full suite; upload reports as artifacts
- **AI audit**: **Ollama** (local) or **Gemini** (cloud); optional auto-run after local failures; see [AI failure analysis](#ai-failure-analysis)

## Requirements

- Python 3.11+
- Playwright browsers (see below)

## Setup

```bash
# Clone and enter project
cd autonomous-quality-engine

# Create venv and install dependencies
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install Playwright browsers (required once)
playwright install chromium
# Or: playwright install  # all browsers

# Optional: copy env template and adjust
cp config/env.example .env
```

## Running tests

Use the project virtualenv so Playwright, **python-dotenv**, and other dependencies resolve (`source .venv/bin/activate`, or invoke `.venv/bin/pytest` / `.venv/bin/python` directly).

```bash
# All tests (report in reports/report.html)
pytest

# Smoke only (fast)
pytest -m smoke

# Full regression marker
pytest -m regression

# Module markers (see pyproject.toml)
pytest tests/regression/ -m pim
pytest tests/regression/ -m leave

# Parallel (multiple workers)
pytest -n auto
# Or: pytest -n 4

# Specific directories
pytest tests/smoke/
pytest tests/regression/
```

## CI/CD (GitHub Actions)

- **Trigger**: Push or PR to `main`/`master`; or run manually via **Actions** tab.
- **Workflow** [`.github/workflows/test.yml`](.github/workflows/test.yml) (**Test Suite**):
  - **smoke**: Runs `pytest -m smoke`, uploads `smoke-report` artifact.
  - **test**: Full suite with `pytest -n auto`, uploads `test-report-3.11` artifact.
- **Artifacts**: Download from the run summary to get `reports/report.html` and `reports/screenshots/`.
- **AI failure analysis (CI)**: On **Test Suite** failure, [`.github/workflows/ai-failure-analysis.yml`](.github/workflows/ai-failure-analysis.yml) downloads artifacts from that run and can run Gemini-based analysis. Requires repository secrets **`ACTIONS_ARTIFACT_READ_TOKEN`** (PAT with **Actions: Read** on the repo — `GITHUB_TOKEN` cannot download another run’s artifacts) and optional **`GEMINI_API_KEY`**. See [docs/decisions/ci-ai-failure-analysis.md](docs/decisions/ci-ai-failure-analysis.md) and [reference/github-actions-trigger-workflow.md](docs/reference/github-actions-trigger-workflow.md). Run the analyzer locally using the commands in [AI failure analysis](#ai-failure-analysis).

## AI failure analysis

Provider selection is explicit via **`AI_PROVIDER`** in `.env` (`ollama` or `gemini`; default **`ollama`** if unset). Copy [`config/env.example`](config/env.example) and set `GEMINI_API_KEY` when using Gemini. Use the same venv as tests (`.venv/bin/python`) so **`python-dotenv`** and other deps load.

### Local Ollama (default)

1. Install [Ollama](https://ollama.ai) and pull a model (default in this repo is **`llama3`**):
   ```bash
   ollama pull llama3
   ```
2. After test failures, `reports/failures.txt` is written; on **non-CI** runs the pytest session may also write **`reports/ai_suggestions.md`** automatically when Ollama is reachable.
3. Run the analyzer manually if needed:
   ```bash
   # From project root, with reports/ present (e.g. after a failed run)
   python -m ai_audit.failure_analyzer --artifacts-dir reports

   # After downloading CI artifacts (extract to e.g. ./artifacts)
   python -m ai_audit.failure_analyzer --artifacts-dir ./artifacts

   # Write suggestions to a file
   python -m ai_audit.failure_analyzer --artifacts-dir reports --out reports/ai_suggestions.md

   # Point at a failures file (TEST: / MESSAGE: blocks) instead of scanning artifacts
   python -m ai_audit.failure_analyzer --failures path/to/failures.txt --out suggestions.md
   ```

### Gemini (cloud)

Set `AI_PROVIDER=gemini` and `GEMINI_API_KEY` in `.env` (or export for the shell). CI uses the same variables in the AI Failure Analysis workflow.

```bash
AI_PROVIDER=gemini python -m ai_audit.failure_analyzer --model gemini-1.5-flash --artifacts-dir reports
```

Optional one-shot override without changing `.env`: `--client gemini` or `--client ollama` (see `python -m ai_audit.failure_analyzer --help`).

## Project structure

```
autonomous-quality-engine/
├── .github/workflows/test.yml                 # CI: smoke + full test (Test Suite)
├── .github/workflows/ai-failure-analysis.yml  # Optional Gemini analysis after Test Suite failure
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

Env vars (or `.env`): `BASE_URL`, `BROWSER`, `HEADLESS`, `TIMEOUT_MS`, `ORANGEHRM_USER`, `ORANGEHRM_PASSWORD`, `IGNORE_HTTPS_ERRORS` (local HTTPS). For AI audit: `AI_PROVIDER`, `GEMINI_API_KEY` (Gemini), optional `OLLAMA_MODEL` / `OLLAMA_BASE_URL`. See [`config/env.example`](config/env.example).

## Contributing and pull requests

- **Standards:** Follow **`.cursorrules`** (POM, locators, `expect`, logging). Design notes: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); project snapshot: [docs/PROJECTSTATUS.md](docs/PROJECTSTATUS.md); notable changes: [CHANGELOG.md](CHANGELOG.md); locator/logging decisions: [docs/decisions/playwright-locators-and-logging.md](docs/decisions/playwright-locators-and-logging.md).
- **CodeRabbit:** When [CodeRabbit](https://coderabbit.ai) is connected to the repository, use it to catch drift from those rules (e.g. missing `element_label`, raw `page` clicks on critical paths). Treat its output as advisory; **`.cursorrules`** and the decision docs remain authoritative for merges.
- **PR template:** Opening a PR loads [`.github/pull_request_template.md`](.github/pull_request_template.md) — complete the checklist and confirm tests were run.

## License

Use as needed for learning and portfolio. OrangeHRM is a trademark of OrangeHRM Inc.