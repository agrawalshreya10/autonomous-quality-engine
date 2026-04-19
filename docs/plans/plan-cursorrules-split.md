# Plan: Split `.cursorrules` into `.cursor/rules/*.mdc`
### Revision: Enterprise-Grade Governance Edition — 2026-04-19

---

## Goal

Replace the single root **`.cursorrules`** with **four focused, scoped Cursor rules** under **`.cursor/rules/`**, each carrying hard governance guardrails to prevent AI agents from generating incorrect code. This plan now also addresses observed **framework smearing** (AI hallucinating Selenium or async patterns inside a sync Playwright project) and **SDK drift** (AI using deprecated Gemini APIs).

The `.mdc` files become the **single source of truth** for all agent behavior in this codebase. Once validated, **`.cursorrules` will be removed** (Option B).

---

## Current state

| Source | Role |
|--------|------|
| **`.cursorrules`** | Monolithic Playwright/Pytest standards (~37 lines); only one context blob, no scoping. |
| **`.cursor/rules/genai-standards.mdc`** | Gemini SDK governance for `ai_audit/`; `alwaysApply: true`. |
| **`.cursor/rules/gemini-sdk-migration.mdc`** | Banned model IDs and patterns for `ai_audit/`; `alwaysApply: true`. |

---

## Target rule format (Cursor `.mdc`)

```yaml
---
description: One-line summary (shown in Cursor rule picker)
globs: path/pattern/**/*.py   # omit for alwaysApply-only rules
alwaysApply: true|false
---

# Rule Title
…Markdown body…
```

- **`alwaysApply: true`** — injected into every chat session. Use only for rules short enough not to pollute context.
- **`globs`** — injected only when a matching file is open/in scope.
- A rule may have **both** `globs` and `alwaysApply: true` (global baseline + extra detail for matched files).

---

## Lean 4-File Target Split

All seven original sections of `.cursorrules` are consolidated into four focused files that avoid context overlap while adding governance guardrails.

### 1. `playwright-core-sync.mdc`
**Scope:** `alwaysApply: true` (all sessions, short body)

| Concern | Content |
|---------|---------|
| Environment | Python 3.12+; always invoke via `.venv/bin/pytest` or `.venv/bin/python`. |
| Sync enforcement | **MANDATE:** Use `playwright.sync_api` ONLY. `async def`, `await`, and `asyncio` are **BANNED** in all `pages/`, `core/`, `tests/` code. |
| Execution | `BASE_URL` from config; tests must be parallel-safe. |
| AI debugging | On failure: use `ai_audit/failure_analyzer.py`; refer to `docs/PROJECTSTATUS.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`. |

**Governance note — Sync/Async conflict (CRITICAL):**
OrangeHRM tests use `playwright.sync_api` exclusively. Any AI suggestion introducing `async def`, `await playwright.async_api`, or `asyncio.run()` for page interaction is **architecturally wrong** and must be rejected. This was observed when `reports/ai_suggestions.md` (Ollama local analysis) generated async fixtures as a fix suggestion — a pattern foreign to this codebase.

---

### 2. `page-object-standards.mdc`
**Scope:** `globs: pages/**/*.py, pages/components/**/*.py, core/base_page.py, core/page_factory.py`

| Concern | Content |
|---------|---------|
| POM architecture | Pages in `pages/`; components in `pages/components/`; driver/factory in `core/`. PEP 8 + type hints everywhere. |
| Locator priority | Prefer `get_by_role`, `get_by_label`, `get_by_testid`. XPath and raw CSS IDs are last resort. |
| Resilience pattern | **MANDATE:** Every Page Object **must** use `self.get_resilient_locator(modern_selector, legacy_fallback)` (or `get_resilient_role_*`, `get_resilient_placeholder`) for critical locators. This ensures compatibility with both OrangeHRM 5.x and MAMP/ohrm.test environments. |
| `.or_()` strictness | When using `.or_()`, ensure the union does **not** pair a parent and its child node in the same DOM subtree. `expect()` runs in strict mode: if the locator resolves to >1 element the assertion fails. Prefer the most specific user-facing node (e.g. text `<p>` over its `role=alert` container). If ambiguity is unavoidable, use `.first` **on the primary side only** (see `docs/decisions/playwright-locators-and-logging.md`). |
| Placeholder resilience | For `get_by_placeholder` fallbacks: `primary.first.or_(fallback)` — **never** move `.first` to after `.or_()`; that breaks primary-first semantics. |
| Lazy locators | `Locator` objects are **descriptions**, not resolved handles. `.first` and `.or_()` are filters evaluated at action/assertion time. Do not refactor chains on the false assumption that `.first` "resolves early". |
| Interactions | Route all clicks and fills through `self.click()` / `self.fill()` from `BasePage`. Never call `locator.click()` directly in a page method. |
| `element_label` | **Mandatory** on every `self.click()`, `self.fill()`, `self.get_text()` call. |
| Past-tense logs | Emit "Performed …" only **after** the action completes in `_run`. A failed action must not appear as successful in logs. |
| Error handling | Every page method must wrap its body in try/except; log via `self._error_logger`; **re-raise** to ensure test failure propagates. |
| Assertions | Use `expect(locator)` for all UI state checks (web-first, auto-waiting). `assert` is for non-UI logic (data/API). |
| Forbidden | `page.wait_for_timeout()` is **banned**. |

---

### 3. `ai-audit-governance.mdc`
**Scope:** `alwaysApply: true` + `globs: ai_audit/**/*.py`

> This rule **supersedes and replaces** any conflicting advice from `genai-standards.mdc` or `gemini-sdk-migration.mdc` on matters of model ID and SDK version. The existing `.mdc` files remain for backward-compat reference, but this file is the **enforcing standard**.

| Concern | Content |
|---------|---------|
| SDK | **ONLY** `google-genai` (`pip install google-genai`). `google-generativeai` is deprecated and **banned**. |
| Initialization | `client = genai.Client(api_key=..., http_options=types.HttpOptions(timeout=ms))` → `client.models.generate_content(...)` → `client.close()`. `genai.GenerativeModel()` is **banned**. |
| Model IDs (allowed) | `gemini-3.1-flash-preview`, `gemini-3.1-flash-lite-preview` |
| Model IDs (banned) | `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-1.0-pro`, `gemini-2.0-flash-exp` (produces CI 404). |
| Default | `DEFAULT_GEMINI_MODEL` in `ai_audit/gemini_client.py` = `gemini-3.1-flash-lite-preview` (cost/speed default for CI). |
| Sync/async | Do **not** mix sync Playwright and async Gemini calls in any analysis script. Each subsystem stays in its own execution context. |
| Prompt content | Prompts must not include secrets, tokens, passwords, or PII. |
| Dependency pin | `google-genai==1.73.1` (exact pin for deterministic CI); update only deliberately. |

---

### 4. `test-strategy.mdc`
**Scope:** `globs: tests/**/*.py, data/**`

| Concern | Content |
|---------|---------|
| Atomicity | Every test must be fully independent. Use `conftest.py` fixtures for setup/teardown; never share mutable state between tests. |
| Data | Pull static data from `data/testdata.json` or equivalent. Use `utils/helpers.py`, `utils/generate_test_data.py`, or `Faker` for runtime data. No hardcoded user credentials, names, or IDs in test steps. |
| Markers | Use `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.pim`, `@pytest.mark.leave`. |
| Parallel safety | Reference `BASE_URL` from config; assume `pytest-xdist` parallel runs; no shared file handles in tests. |
| Assertions | `expect(locator)` for UI; `assert` only for data/non-UI checks. |
| Conftest | `browser_context` fixture handles browser lifecycle. `logged_in_page_factory` for regression. `pytest_sessionfinish` hook auto-triggers local failure analysis when `reports/failures.txt` exists and Ollama is reachable. |

---

## Case Study: Framework Smearing Mitigation

### Observation (2026-04-19)

After `test_login_invalid_credentials` failed (strict-mode locator violation), the **Ollama local AI audit** generated the following fix in `reports/ai_suggestions.md`:

```python
# WRONG — from ai_suggestions.md
from playwright.sync_api import async_playwright

class LoginPage:
    async def go(self):
        self.page = await async_playwright().launch_har()

    async def error_text(self):
        return (await self.get_by_role("alert").or_(
            self.get_by_xpath("//div[@class='error-message']")
        )).text_content()
```

**Problems in that suggestion:**

| Issue | Why it is wrong |
|-------|----------------|
| `async def` + `await` | This project uses `playwright.sync_api`. Async patterns are **architecturally incompatible** with the sync Playwright session lifecycle. |
| `get_by_xpath(...)` | Playwright's Python API does not have a `get_by_xpath` method. This is a **Selenium `By.XPATH` hallucination** — the LLM confused Playwright Python with Selenium's `driver.find_element(By.XPATH, ...)`. |
| Parent + child `.or_()` | `get_by_role("alert").or_(get_by_xpath("//div[@class='error-message']"))` would still hit the strict-mode violation if both resolve to different nodes. |

### Root cause of hallucination

The local Ollama model (`llama3`) has heavy Selenium training data. Without an explicit framework separation rule in context, it defaults to Selenium/async patterns when Playwright prompts look ambiguous.

### Mitigation: Strict Framework Separation Rule

This is the **primary justification** for `playwright-core-sync.mdc` with `alwaysApply: true`. By injecting into every session:

1. **Async ban** — agents cannot generate `async def` / `await` in page/test code.
2. **Locator API mandate** — `get_by_role`, `get_by_label`, `get_by_testid`, `get_by_placeholder`; no Selenium-style `find_element(By.*)` or `get_by_xpath`.
3. **Framework identity** — explicit "This project uses `playwright.sync_api` (Python)" prevents model drift toward Selenium, JS Playwright, or Cypress patterns.

The `ai-audit-governance.mdc` rule similarly prevents the Gemini API generating `GenerativeModel()` patterns or banned model IDs once the codebase grows.

---

## Migration phases

### Phase 1 — Author `.mdc` files (parallel to `.cursorrules`)

1. Branch from current `main`.
2. Create the four files in `.cursor/rules/` per the definitions above.
3. Retain `.cursorrules` during this phase — no deletion yet.
4. Cross-check: for every bullet in `.cursorrules`, confirm it appears in exactly **one** `.mdc` file.

### Phase 2 — Scope verification

1. Open each key file type in Cursor: `pages/login_page.py`, `tests/smoke/test_login.py`, `ai_audit/gemini_client.py`.
2. Confirm the **expected rules attach** (check Cursor's rule context panel).
3. Adjust `globs` if a rule is missing or over-fires.
4. Run `pytest -m smoke && pytest -m regression` — no code changes expected; green is the sanity gate.

### Phase 3 — Remove `.cursorrules` (Option B — default)

**Decision: Option B (Removal)**

Once Phase 2 validation passes:

1. Delete root `.cursorrules`.
2. Commit with message: `chore: remove .cursorrules — replaced by .cursor/rules/*.mdc`.
3. Verify in a fresh Cursor session that rules still activate correctly without `.cursorrules`.

**Why Option B over A or C:**

| Option | Verdict |
|--------|---------|
| **A — Pointer file** | Leaves a "ghost" file that could confuse future agents or Cursor versions into treating it as authoritative. |
| **B — Remove** | Clean break; `.cursor/rules/` is the sole, verifiable governance layer. **Chosen.** |
| **C — Keep minimal** | Risk of split-brain: two authoritative sources for the same rules. |

### Phase 4 — CHANGELOG & docs

- [ ] Add `[Unreleased]` entry: `Chore: replace .cursorrules with four scoped .cursor/rules/*.mdc governance files`.
- [ ] Update `docs/ARCHITECTURE.md` System Design section to reference `.cursor/rules/` as the governance layer.
- [ ] Note this case study in `docs/decisions/playwright-locators-and-logging.md` under "Framework Smearing" (optional, if the decisions file grows a governance section).

---

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| `alwaysApply: true` context bloat | Keep `playwright-core-sync.mdc` and `ai-audit-governance.mdc` bodies ≤ 20 lines each. Detail lives in globs-scoped rules. |
| Globs too narrow (rule misses) | Start broad (`pages/**/*.py`); narrow if noise appears in unrelated files. |
| Duplicate / conflicting instructions between old and new | Phase 1 cross-check table (one bullet → one rule). Delete `.cursorrules` at Phase 3. |
| `genai-*.mdc` conflict with new `ai-audit-governance.mdc` | Add a `> This rule supersedes …` header in `ai-audit-governance.mdc`. Long term: merge or deprecate the older files. |
| LLM still hallucinates (new patterns) | Iteratively add `BANNED:` lines to the relevant rule and document the case study. |

---

## Deliverables checklist

- [ ] `.cursor/rules/playwright-core-sync.mdc` (new)
- [ ] `.cursor/rules/page-object-standards.mdc` (new)
- [ ] `.cursor/rules/ai-audit-governance.mdc` (new)
- [ ] `.cursor/rules/test-strategy.mdc` (new)
- [ ] Root `.cursorrules` **deleted** (Phase 3, after validation)
- [ ] `CHANGELOG.md` — Unreleased entry added
- [ ] `docs/ARCHITECTURE.md` — governance layer reference updated
- [ ] This plan marked complete in repo docs

---

## Open decisions (resolved)

| Decision | Resolution |
|----------|------------|
| Number of files | **4** (lean split; avoids context overlap) |
| Phase 3 strategy | **Option B — Remove** `.cursorrules` |
| Sync/async governance | **Mandatory `alwaysApply: true` ban** in `playwright-core-sync.mdc` |
| Gemini SDK source of truth | **`ai-audit-governance.mdc`** (new, supersedes older genai rules for enforcement) |
| Locator strictness | **Documented in `page-object-standards.mdc`** with parent/child union anti-pattern |
| Resilience mandate | **`get_resilient_locator()` mandatory** in all page objects |
| Framework smearing | **Addressed** — case study section + sync ban + locator API mandate |

---

*This document is the Source of Truth for the `.cursor/rules/` governance migration. Update when new hallucination patterns are observed or when existing rules are adjusted post-validation.*
