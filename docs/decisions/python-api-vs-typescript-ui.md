# Decision: Python API-first vs TypeScript UI expansion

**Status:** Accepted  
**Date:** 2026-07-27  
**Scope:** Where new OrangeHRM coverage grows — this Python repo vs a separate TypeScript Playwright project.

---

## Context

This repository is a Python Playwright suite with a thin UI smoke/regression slice (login, PIM, leave), POM, CI, and AI failure analysis. Growing deep UI coverage in Python and standing up strong API coverage in the same repo would split focus and duplicate browser investment.

Playwright’s primary UI tooling and ecosystem momentum for large E2E suites sit on the **TypeScript/Node** side. Python remains a strong fit for **API clients, payload contracts, and data-driven checks**.

---

## Decision

1. **This Python repo pivots to API-first** testing (clients, payloads, contract-oriented suites). Roadmap **Phase 2** covers that work; **execution order** runs **Phase 3** (demo CI/observability) before Phase 2 so the portfolio gate story is ready first.
2. **UI E2E expansion** (broader OrangeHRM flows, richer page objects) moves to a **separate TypeScript Playwright** project — not grown further here.
3. **Keep a thin Python UI smoke** (current `-m smoke` / existing page objects) until the TS project exists and can own browser coverage. Do **not** expand Python UI page objects or UI regression depth in the meantime.
4. **Phase 1 Docker** stays and is **complete** (local image + CI smoke job). Portfolio **execution order** prioritizes **Phase 3** (CI gates/observability/Allure) for demo readiness, then **Phase 2** API clients/contracts — valid regardless of the UI handoff to TypeScript.

---

## Consequences

| Stays in Python (this repo) | Moves / deferred |
|-----------------------------|------------------|
| Thin UI smoke for sanity + Docker/CI parity | New UI flows, deep POM growth |
| AI failure analysis, core fixtures, config | Broader browser E2E (→ TS Playwright) |
| Upcoming API clients / payload tests | — |

**How to frame this split:** Python owns infrastructure, thin UI smoke, the CI quality system (next), and API/contracts; TypeScript Playwright owns deeper UI E2E.
