# Autonomous Quality Engine — framework architecture

## Project Overview
An Enterprise-Grade automation framework for OrangeHRM, designed for a Senior SDET portfolio. 

## Target Environment
- **Local Development**: Hosted on a MAMP server mapped to `http://ohrm.test`.
- **Database**: Local MySQL instance managed via MAMP.
- **AI Audit**: Local Ollama for private log analysis + Gemini API (cloud) for advanced failure auditing.

## Tools
- **Tech Stack**: Python, Playwright, Pytest, **pytest-html** (primary HTML reports), Gemini AI (for Audit). **Allure** (`allure-pytest`) is planned for **Phase 3** — see Roadmap.

## Playwright Component Testing (reference — 2026)

Official Playwright **component tests** are **experimental**, run on the **Node.js** toolchain, and target **UI framework bundles** (e.g. `@playwright/experimental-ct-react`, `@playwright/experimental-ct-vue`). They are **not** the same as this repo’s **Python E2E** suite. Use this section when deciding whether to add CT alongside E2E.

**Current best practices (aligned with [Playwright component testing docs](https://playwright.dev/docs/test-components)):**

- **Isolation via `mount`:** Tests use the `mount` fixture to render a component in a real browser; `mount` returns a **locator scoped to the component** — assert and interact through that locator like any Playwright test.
- **User-centric assertions:** Prefer **accessibility-oriented** selectors (`getByRole`, `getByLabel`, alt text) and visible outcomes. **Do not** reach into component instances or internal methods from tests; that couples tests to implementation and contradicts Playwright’s guidance.
- **Stories / test wrappers:** For props that cannot cross the Node/browser boundary (complex objects, synchronous Node callbacks), use **wrapper components or story modules** that adapt props to plain serializable values — the documented “story file” pattern.
- **Hooks:** Use `beforeMount` / `afterMount` (and `hooksConfig` where needed) in `playwright/index.*` for **theme, router, global providers** (e.g. Pinia testing setup) so each test gets a controlled environment.
- **Lifecycle:** Use **`unmount`** and **`update`** when testing teardown, prop updates, and parent-driven re-renders.
- **Network:** Use the experimental **`router`** fixture (and optionally **MSW** handlers) to mock APIs during CT — same stability principles as E2E network mocking.
- **Bundling & config:** CT uses **Vite** under the hood; align **`ctViteConfig`** (aliases, plugins) with your app’s build when they diverge — Playwright does not automatically reuse your full Vite config.
- **Observability:** Reuse standard Playwright Test settings: **parallel runs**, **tracing** / reporting as configured — CT shares the same post-failure debugging story as E2E.
- **Naming clarity:** This repository’s `pages/components/` directory is the **Page Object Model** place for **reusable page pieces** in **Python**, **not** Playwright CT source. If OrangeHRM (or a separate front-end) gains JS CT, colocate CT specs with the component bundle (e.g. `*.spec.tsx`) per Playwright’s layout, or add a dedicated package — do not conflate POM “components” with `@playwright/experimental-ct-*` unless explicitly adopted.

## System Design
- **BasePage Core**: Centralized logic for logging, resilient locators, and web-first assertions. **Locator + interaction-log behavior (including `.first` / `.or_()` semantics and when to log “Performed”) is decided in** [docs/decisions/playwright-locators-and-logging.md](decisions/playwright-locators-and-logging.md) — use that doc as the default checklist before changing DOM-related code.
- **DOM verification**: Prefer **Playwright MCP** (`.cursor/mcp.json`, `@playwright/mcp`) in Cursor for live structure checks; pair with traces and tests for failures.
- **Hybrid Locator Strategy**: 
    - Page-specific locators stay inside their respective Classes.
    - Shared/Global locators (Navbars, Logout) are stored in `core/constants.py`.
- **Component Pattern**: Large pages are decomposed into reusable components in `pages/components/`.

## AI Integration
- **Rationale (CI + cloud LLM):** Recorded in [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md) — adopted approach **B + D** (on-demand analysis in CI; redacted, minimal publication surface). Interview-oriented talking points live locally under `.cursor/interview-prep/ci-ai-failure-analysis.md` (gitignored; not in the remote repo).
- **Local Development**: **Automatic Local Failure Analysis via Ollama** — pytest hook auto-triggers analysis on test failures with smart truncation (2K char limit), Ollama health check (port 11434), and enhanced Quality Architect prompts; model output is persisted to `reports/ai_suggestions.md`.
- **AI Audit**: Ollama locally (automatic + manual); optional Gemini (`gemini-3-flash` default) via `GEMINI_API_KEY` when invoking the analyzer.
- **CLI**: `python -m ai_audit.failure_analyzer --client gemini --artifacts-dir reports` (or `--client ollama`).
- **CI**: Separate **AI Failure Analysis** workflow ([ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml)) triggered by `workflow_run` when Test Suite fails; **`ACTIONS_ARTIFACT_READ_TOKEN`** (PAT, `actions:read`) for cross-run artifact download and optional **`GEMINI_API_KEY`** for cloud analysis. For triggers, token limits, and `workflow_run`, see [reference/github-actions-trigger-workflow.md](reference/github-actions-trigger-workflow.md) ([official doc](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)).

## Roadmap & Gaps (Ref: PROJECTSTATUS.md)

Development is grouped into **phases**; items below stay numbered for easy reference.

### Phase 1 — Infrastructure
1. **Dockerization**: Containerize the execution for GitHub Actions compatibility. For attaching services (DB, cache) in GitHub Actions jobs, see [reference/github-actions-docker-service-containers.md](reference/github-actions-docker-service-containers.md) (summary of [official docs](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)).

### Phase 2 — Data
2. **Dynamic Data**: Transition from static JSON to runtime data generation using Faker.

### Phase 3 — CI/CD & reporting
3. **CI/CD**: Harden YAML-based pipelines for automated regression. Event triggers and filters: [reference/github-actions-trigger-workflow.md](reference/github-actions-trigger-workflow.md) (summary of [Triggering a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)). CI patterns for Python: [reference/github-actions-build-test-python.md](reference/github-actions-build-test-python.md).
4. **Allure reporting**: Integrate **Allure** alongside (not necessarily replacing) **pytest-html**. Enable `allure-pytest` in `requirements.txt` (currently commented), configure pytest to write `allure-results/`, add CI steps to run the **Allure CLI** (or an Actions wrapper) to produce `allure-report/` and optionally upload as an artifact; keep `.gitignore` entries for `allure-results/` and `allure-report/`. Rationale: structured steps, attachments, and richer dashboards for portfolio and team review — see discussion in project docs vs. single-file HTML reports.

### Later / cross-cutting
5. **Project Completion**: Refinement of README.md and documentation for portfolio presentation.
6. **CodeRabbit Integration** *(planned)*: AI-powered PR reviews on GitHub, configured to enforce `.cursorrules` standards (mandatory `element_label`, `self.click`/`self.fill` usage, `.or()` on critical locators).
7. **Gemini AI Audit in CI** *(completed)*: `GeminiClient` and `failure_analyzer` are implemented; workflows now match **B + D** (separate on-demand analysis workflow + redacted single surface) per [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md). See [ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml).

## GitHub documentation (reference summaries)

Project-local notes in `docs/reference/` (canonical URLs on GitHub Docs):

| Topic | Local summary | Official |
|--------|-------------------|----------|
| Actions quickstart | [github-actions-quickstart.md](reference/github-actions-quickstart.md) | [Quickstart for GitHub Actions](https://docs.github.com/en/actions/get-started/quickstart) |
| Python build & test | [github-actions-build-test-python.md](reference/github-actions-build-test-python.md) | [Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) |
| Custom actions | [github-actions-manage-custom-actions.md](reference/github-actions-manage-custom-actions.md) | [Managing custom actions](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/manage-custom-actions) |
| Workflow triggers | [github-actions-trigger-workflow.md](reference/github-actions-trigger-workflow.md) | [Triggering a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) |
| Docker service containers | [github-actions-docker-service-containers.md](reference/github-actions-docker-service-containers.md) | [Communicating with Docker service containers](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers) |
| Repository licensing | [github-licensing-repository.md](reference/github-licensing-repository.md) | [Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) |

## Python documentation (reference summary)

| Topic | Local summary | Official |
|--------|-------------------|----------|
| Python 3 docs index | [python-documentation.md](reference/python-documentation.md) | [Python 3 documentation](https://docs.python.org/3/) |


## OrangeHRM documentation (reference summary)

REST API Documentation (Open Source): orangehrm.github.io/orangehrm-api-doc

Why: This defines the exact JSON structure for Employees, Users, and Timesheets. Use this to ensure your Faker data matches what the backend expects.

GitHub Wiki (Architecture & Tech Stack): github.com/orangehrm/orangehrm/wiki/OrangeHRM-5X

Why: Confirms the transition to Vue 3 and Symfony 5.4, which justifies using modern Playwright locators like get_by_role instead of old-school CSS IDs.
