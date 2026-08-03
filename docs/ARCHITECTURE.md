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
- **Rationale (CI + cloud LLM):** Recorded in [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md) — adopted approach **B + D** (on-demand analysis in CI; redacted, minimal publication surface). Interview-oriented talking points can live locally under **`.cursor/user-docs/ci-ai-failure-analysis.md`** (gitignored; not in the remote repo).
- **Local Development**: **Automatic Local Failure Analysis via Ollama** — pytest hook auto-triggers analysis on test failures with smart truncation (2K char limit), Ollama health check (port 11434), and enhanced Quality Architect prompts; model output is persisted to `reports/ai_suggestions.md`.
- **AI Audit**: Ollama locally (automatic + manual); optional Gemini (default model ID matches `DEFAULT_GEMINI_MODEL` in [`ai_audit/gemini_client.py`](../ai_audit/gemini_client.py), currently `gemini-3.1-flash-lite`) via `GEMINI_API_KEY` when invoking the analyzer.
- **CLI**: `python -m ai_audit.failure_analyzer --client gemini --artifacts-dir reports` (or `--client ollama`).
- **CI**: Separate **AI Failure Analysis** workflow ([ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml)) triggered by `workflow_run` when Test Suite fails; **`ACTIONS_ARTIFACT_READ_TOKEN`** (PAT, `actions:read`) for cross-run artifact download and optional **`GEMINI_API_KEY`** for cloud analysis. For triggers, token limits, and `workflow_run`, see [reference/github-actions-trigger-workflow.md](reference/github-actions-trigger-workflow.md) ([official doc](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)).

## Strategy direction (API-first)

**This Python repo is API-first going forward.** New coverage should emphasize API payloads, clients, and contract-oriented checks. **UI E2E expansion** (deeper OrangeHRM flows, richer page objects) belongs in a **separate TypeScript Playwright** project. Until that TS suite exists, keep the **thin Python UI smoke** (current `-m smoke`) for sanity and Docker/CI parity — do not grow Python UI page objects or UI regression depth. Decision record: [docs/decisions/python-api-vs-typescript-ui.md](decisions/python-api-vs-typescript-ui.md).

## Roadmap & Gaps (Ref: PROJECTSTATUS.md)

Development is grouped into **phases**; items stay numbered for reference. **Execution order for portfolio demo readiness:** Phase 1 *(done)* → **Phase 3 next** (CI quality system) → **Phase 2 after** (API clients/contracts) → Later. Phase numbers are historical labels, not the build sequence.

### Phase 1 — Infrastructure (Docker / CI–local parity) *(completed)*
1. **Dockerization** *(completed)*: Containerize the **current** pytest smoke runner for local/CI parity (image builds deps + Chromium; `BASE_URL` / credentials stay env-injected). Local `Dockerfile` / `docker run` and the GitHub Actions **smoke** job both use the `aqe-smoke` image (Buildx + GHA cache; reports via `docker cp` → **`smoke-report`** artifact). Non-root `aqe` user and smoke-only env (`.env.smoke`) are in place. The full **test** job remains host Python by design for now (not a Phase 1 gap). Optional later polish (GHCR publish, pulling a prebuilt image instead of build-per-run) is **Phase 3 cache/speed** work — not unfinished Phase 1 wiring. For attaching services (DB, cache) in Actions jobs, see [reference/github-actions-docker-service-containers.md](reference/github-actions-docker-service-containers.md) (summary of [official docs](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers)).

### Phase 3 — CI/CD, observability & reporting *(next — demo priority)*
3. **CI/CD quality gates & observability** *(in progress)*: Harden the pipeline beyond “tests + HTML artifact.” Docker-based **smoke** is already done in Phase 1 — do **not** re-scope it here. Target checklist:
   - **Job DAG:** fast **unit** (no browser) → Docker **smoke** → full **test**/regression (`needs:` / clear gate semantics).
   - **Selective runs:** PR-lite (unit + smoke) vs nightly/`main`/manual full suite; path filters where useful.
   - **Failure observability:** Playwright **traces on failure** (+ screenshots) as first-class artifacts; JUnit/XML for PR/check signal; richer job summaries.
   - **Flake policy:** explicit marker / quarantine; optional controlled retry only for known flakes — no blind reruns that hide product bugs.
   - **Cache / speed (optional):** GHCR or stronger image reuse, pip/browser cache tuning — measurable CI-minute story.
   - **Artifact & secrets hygiene:** retention tiers; keep smoke on `-e` / `.env.smoke` (never general `.env` with AI keys); align with AI B+D redaction.
   - Triggers/filters reference: [reference/github-actions-trigger-workflow.md](reference/github-actions-trigger-workflow.md); Python CI patterns: [reference/github-actions-build-test-python.md](reference/github-actions-build-test-python.md).
4. **Allure reporting** *(planned)*: Integrate **Allure** alongside (not replacing) **pytest-html**. Enable `allure-pytest` in `requirements.txt` (currently commented), write `allure-results/`, generate `allure-report/` in CI, attach screenshot/trace, set environment metadata (commit, browser, `BASE_URL`); keep `.gitignore` for Allure dirs.
5. **Portfolio packaging** *(with Phase 3)*: README CI diagram + status badges; short “how failures are triaged” (trace → Allure → AI suggestion). Pull this forward from “Later” so the demo surface is interview-ready when Phase 3 lands.

### Phase 2 — API-first data & clients *(after Phase 3 demo slice)*
2. **API payloads / clients**: OrangeHRM REST (and related) clients, runtime payload generation (e.g. Faker), and at least one **contract-oriented** suite (status/schema assertions) that CI can run as a fast gate once Phase 3’s DAG exists. Static JSON fixtures give way to generated, contract-aware data. UI expansion does **not** land here — it moves to the TypeScript Playwright project.

### Later / cross-cutting
6. **CodeRabbit Integration** *(configured)*: AI-powered PR reviews on GitHub, aligned with **`.cursor/rules/*.mdc`** standards (mandatory `element_label`, `self.click`/`self.fill` usage, `.or_()` on critical locators).
7. **Gemini AI Audit in CI** *(completed)*: `GeminiClient` and `failure_analyzer` are implemented; workflows now match **B + D** (separate on-demand analysis workflow + redacted single surface) per [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md). See [ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml).
8. **TypeScript Playwright UI suite** *(separate repo)*: Broader UI E2E once that project exists; Python keeps thin smoke only until then.
9. **Further portfolio polish**: Extra narrative/README refinement beyond the Phase 3 packaging slice above.

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

## Gemini / Google GenAI SDK documentation (reference summary)

| Topic | Local summary | Official |
|--------|-------------------|----------|
| Gemini API libraries + Python GenAI docs | [gemini-genai-sdk-docs.md](reference/gemini-genai-sdk-docs.md) | [Gemini API libraries](https://ai.google.dev/gemini-api/docs/libraries), [genai generated docs](https://googleapis.github.io/google-cloud-python/generated/docs/genai/) |

## Python documentation (reference summary)

| Topic | Local summary | Official |
|--------|-------------------|----------|
| Python 3 docs index | [python-documentation.md](reference/python-documentation.md) | [Python 3 documentation](https://docs.python.org/3/) |


## OrangeHRM documentation (reference summary)

REST API Documentation (Open Source): orangehrm.github.io/orangehrm-api-doc

Why: This defines the exact JSON structure for Employees, Users, and Timesheets. Use this to ensure your Faker data matches what the backend expects.

GitHub Wiki (Architecture & Tech Stack): github.com/orangehrm/orangehrm/wiki/OrangeHRM-5X

Why: Confirms the transition to Vue 3 and Symfony 5.4, which justifies using modern Playwright locators like get_by_role instead of old-school CSS IDs.
