# OrangeHRM Playwright Test Suite

Enterprise-grade test automation for [OrangeHRM](https://www.orangehrm.com/) using **Playwright** (Python), **Page Object Model** with **Factory Pattern**, **GitHub Actions** CI/CD, and optional **AI failure analysis** via local Ollama.

Target: [OrangeHRM Open Source Demo](https://opensource-demo.orangehrmlive.com/).

## Features

- **Playwright + Python**: Cross-browser, auto-waiting, traces and screenshots
- **POM + Factory**: `core/base_page.py`, `core/page_factory.py`, page classes in `pages/`
- **pytest**: Markers (`smoke`, `regression`, `pim`, `leave`), fixtures, parallel with **pytest-xdist**
- **Reporting**: pytest-html report in `reports/`; screenshots on failure
- **CI/CD**: GitHub Actions on push/PR; smoke job + full suite; upload reports as artifacts
- **AI audit**: Local Ollama analyzes failed test logs and suggests fixes (run after downloading artifacts)

## Requirements

- Python 3.11+
- Playwright browsers (see below)

## Setup

```bash
# Clone and enter project
cd orangehrm-playwright

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

```bash
# All tests (report in reports/report.html)
pytest

# Smoke only (fast)
pytest -m smoke

# Parallel (multiple workers)
pytest -n auto
# Or: pytest -n 4

# Specific module
pytest tests/smoke/
pytest tests/regression/ -m pim
```

## CI/CD (GitHub Actions)

- **Trigger**: Push or PR to `main`/`master`; or run manually via **Actions** tab.
- **Jobs**:
  - **smoke**: Runs `pytest -m smoke`, uploads `smoke-report` artifact.
  - **test**: Full suite with `pytest -n auto`, uploads `test-report-3.11` artifact.
- **Artifacts**: Download from the run summary to get `reports/report.html` and `reports/screenshots/`.

## AI failure analysis (local)

Uses **Ollama** (local LLM). No API keys.

1. Install [Ollama](https://ollama.ai) and pull a model:
   ```bash
   ollama run llama3.2
   ```
2. After test failures, a `reports/failures.txt` is written (or create one with `TEST:` and `MESSAGE:` lines).
3. Run the analyzer:
   ```bash
   # From project root, with reports/ present (e.g. after local run)
   python -m ai_audit.failure_analyzer --artifacts-dir reports

   # Or after downloading CI artifacts (extract to e.g. ./artifacts)
   python -m ai_audit.failure_analyzer --artifacts-dir ./artifacts

   # Optional: write suggestions to file
   python -m ai_audit.failure_analyzer --artifacts-dir reports --out suggestions.md
   ```

## Project structure

```
orangehrm-playwright/
├── .github/workflows/test.yml   # CI: smoke + full test
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
└── README.md
```

## Configuration

Env vars (or `.env`): `BASE_URL`, `BROWSER`, `HEADLESS`, `TIMEOUT_MS`, `ORANGEHRM_USER`, `ORANGEHRM_PASSWORD`. See `config/env.example`.

## License

Use as needed for learning and portfolio. OrangeHRM is a trademark of OrangeHRM Inc.