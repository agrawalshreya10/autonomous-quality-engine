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
- **AI Audit**: Uses Gemini API (`gemini-1.5-flash`) to analyze Playwright traces and logs upon failure to provide root-cause analysis. Falls back to local Ollama when no API key is set.
- **CLI**: `python -m ai_audit.failure_analyzer --client gemini --artifacts-dir reports`
- **CI**: `GEMINI_API_KEY` stored as a GitHub Actions secret; analyzer runs on failure step.

## Roadmap & Gaps (Ref: STATUS.md)
1. **Dockerization**: Containerize the execution for GitHub Actions compatibility.
2. **Dynamic Data**: Transition from static JSON to runtime data generation using Faker.
3. **CI/CD**: Implementation of YAML-based pipelines for automated regression.
4. **Project Completion**: Refinement of README.md and documentation for portfolio presentation.
5. **CodeRabbit Integration** *(planned)*: AI-powered PR reviews on GitHub, configured to enforce `.cursorrules` standards (mandatory `element_label`, `self.click`/`self.fill` usage, `.or()` on critical locators).
6. **Gemini AI Audit in CI** *(done)*: `GeminiClient` implemented; wire `GEMINI_API_KEY` as GitHub secret and add failure-analysis step to `test.yml`.
