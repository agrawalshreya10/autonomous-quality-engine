# OrangeHRM Playwright Framework Architecture

## Project Overview
An Enterprise-Grade automation framework for OrangeHRM, designed for a Senior SDET portfolio. 
- **Target Environment**: Local MAMP server (`http://localhost:8888/orangehrm`) and Public Demo.
- **Tech Stack**: Python, Playwright, Pytest, Gemini AI (for Audit).

## System Design
- **BasePage Core**: Centralized logic for logging, resilient locators, and web-first assertions.
- **Hybrid Locator Strategy**: 
    - Page-specific locators stay inside their respective Classes.
    - Shared/Global locators (Navbars, Logout) are stored in `core/constants.py`.
- **Component Pattern**: Large pages are decomposed into reusable components in `pages/components/`.

## AI Integration
- **AI Audit**: Uses Gemini API to analyze Playwright traces and logs upon failure to provide root-cause analysis.

## Roadmap & Gaps (Ref: STATUS.md)
1. **Dockerization**: Containerize the execution for GitHub Actions compatibility.
2. **Dynamic Data**: Transition from static JSON to runtime data generation using Faker.
3. **CI/CD**: Implementation of YAML-based pipelines for automated regression.
3. Implementation Step