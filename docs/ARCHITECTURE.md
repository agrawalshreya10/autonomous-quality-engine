# OrangeHRM Playwright Framework Architecture

## Project Overview
An Enterprise-Grade automation framework for OrangeHRM, designed for a Senior SDET portfolio. 

## Target Environment
- **Local Development**: Hosted on a MAMP server mapped to `http://ohrm.test`.
- **Database**: Local MySQL instance managed via MAMP.
- **AI Audit**: Local Ollama for private log analysis + Gemini API (cloud) for advanced failure auditing.

## Tools
- **Tech Stack**: Python, Playwright, Pytest, Gemini AI (for Audit).

## System Design
- **BasePage Core**: Centralized logic for logging, resilient locators, and web-first assertions.
- **Hybrid Locator Strategy**: 
    - Page-specific locators stay inside their respective Classes.
    - Shared/Global locators (Navbars, Logout) are stored in `core/constants.py`.
- **Component Pattern**: Large pages are decomposed into reusable components in `pages/components/`.

## AI Integration
- **Rationale (CI + cloud LLM):** Recorded in [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md) — adopted approach **B + D** (on-demand analysis in CI; redacted, minimal publication surface). Interview-oriented talking points live locally under `.cursor/interview-prep/ci-ai-failure-analysis.md` (gitignored; not in the remote repo).
- **AI Audit**: Ollama locally by default; optional Gemini (`gemini-1.5-flash`) via `GEMINI_API_KEY` when invoking the analyzer.
- **CLI**: `python -m ai_audit.failure_analyzer --client gemini --artifacts-dir reports` (or `--client ollama`).
- **CI**: `GEMINI_API_KEY` as a GitHub Actions secret when using an on-demand analysis workflow; align `.github/workflows/` with the decision doc (see roadmap).

## Roadmap & Gaps (Ref: STATUS.md)
1. **Dockerization**: Containerize the execution for GitHub Actions compatibility.
2. **Dynamic Data**: Transition from static JSON to runtime data generation using Faker.
3. **CI/CD**: Implementation of YAML-based pipelines for automated regression.
4. **Project Completion**: Refinement of README.md and documentation for portfolio presentation.
5. **CodeRabbit Integration** *(planned)*: AI-powered PR reviews on GitHub, configured to enforce `.cursorrules` standards (mandatory `element_label`, `self.click`/`self.fill` usage, `.or()` on critical locators).
6. **Gemini AI Audit in CI** *(in progress)*: `GeminiClient` and `failure_analyzer` are implemented; refactor `test.yml` to match **B + D** (on-demand workflow + redacted single surface) per [docs/decisions/ci-ai-failure-analysis.md](decisions/ci-ai-failure-analysis.md).
