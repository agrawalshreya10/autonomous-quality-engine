# OrangeHRM Playwright Framework Architecture

## Project Overview
An Enterprise-Grade automation framework for OrangeHRM, designed for a Senior SDET portfolio. 

## Target Environment
- **Local Development**: Hosted on a MAMP server mapped to `http://ohrm.test`.
- **Database**: Local MySQL instance managed via MAMP.
- **AI Audit**: Local Ollama for private log analysis + Gemini API (cloud) for advanced failure auditing.

## Tools
- **Tech Stack**: Python, Playwright, Pytest, Gemini AI (for Audit).

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
- **AI Audit**: Ollama locally (automatic + manual); optional Gemini (`gemini-1.5-flash`) via `GEMINI_API_KEY` when invoking the analyzer.
- **CLI**: `python -m ai_audit.failure_analyzer --client gemini --artifacts-dir reports` (or `--client ollama`).
- **CI**: Separate **AI Failure Analysis** workflow ([ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml)) triggered by `workflow_run` when Test Suite fails, with `GEMINI_API_KEY` secret for on-demand cloud analysis.

## Roadmap & Gaps (Ref: STATUS.md)
1. **Dockerization**: Containerize the execution for GitHub Actions compatibility.
2. **Dynamic Data**: Transition from static JSON to runtime data generation using Faker.
3. **CI/CD**: Implementation of YAML-based pipelines for automated regression.
4. **Project Completion**: Refinement of README.md and documentation for portfolio presentation.
5. **CodeRabbit Integration** *(planned)*: AI-powered PR reviews on GitHub, configured to enforce `.cursorrules` standards (mandatory `element_label`, `self.click`/`self.fill` usage, `.or()` on critical locators).
6. **Gemini AI Audit in CI** *(completed)*: `GeminiClient` and `failure_analyzer` are implemented; workflows now match **B + D** (separate on-demand analysis workflow + redacted single surface) per [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md). See [ai-failure-analysis.yml](.github/workflows/ai-failure-analysis.yml).
