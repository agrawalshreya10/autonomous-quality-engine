# Documentation Index

Use this page as the quick map for project docs. The root `README.md` explains how to run the framework; this folder explains architecture, decisions, plans, and reference material.

## Start Here

| Need | Read |
|------|------|
| Current project scope, run commands, roadmap | [`PROJECTSTATUS.md`](PROJECTSTATUS.md) |
| Framework architecture and system design | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Notable decisions that should not drift | [`decisions/`](decisions/) |
| Historical implementation plans | [`plans/`](plans/) |
| External-doc summaries used by the project | [`reference/`](reference/) |

## Core Decisions

- [`decisions/playwright-locators-and-logging.md`](decisions/playwright-locators-and-logging.md) explains the reasoning behind locator strictness, `.or_()` usage, lazy locators, and past-tense interaction logs.
- [`decisions/ci-ai-failure-analysis.md`](decisions/ci-ai-failure-analysis.md) records the CI AI failure-analysis strategy: on-demand analysis plus a minimal redacted publication surface.

## Governance Sources

- Playwright execution, page object, test strategy, and AI audit rules live in [`../.cursor/rules/`](../.cursor/rules/).
- Gemini SDK and model policy is canonical in [`../.cursor/rules/ai-audit-governance.mdc`](../.cursor/rules/ai-audit-governance.mdc). Keep the `google-genai` pin in `requirements.txt` and `pyproject.toml` aligned with that policy when intentionally upgrading.

## Maintenance Notes

- Treat files under `docs/plans/` as historical once their work is complete. Keep current behavior in `PROJECTSTATUS.md`, `ARCHITECTURE.md`, and decision docs instead of maintaining duplicate plan text.
- Local Cursor scratch plans under `.cursor/plans/` are not repo documentation; move durable decisions into `docs/` before deleting local clutter.
