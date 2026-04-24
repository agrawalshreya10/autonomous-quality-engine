# Plan: Scoped Cursor rules (`.cursor/rules/*.mdc`)
### Revision: Enterprise-Grade Governance Edition — 2026-04-19  
### Status: **Complete** (2026-04-23)

---

## Outcome

Project Playwright and test standards are defined in **`.cursor/rules/*.mdc`**. The previous single root project-rules file was removed so there is one governance layer. Personal learning notes can live under **`.cursor/user-docs/`** (gitignored).

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
- A rule may have **both** `globs` and **`alwaysApply: true`** (global baseline + extra detail for matched files).

---

## Current rule set (authoritative)

| File | Role |
|------|------|
| **`playwright-core-sync.mdc`** | `alwaysApply: true` — sync Playwright, environment, `expect`, no `wait_for_timeout`. |
| **`page-object-standards.mdc`** | `globs: pages/**`, `core/base_page.py`, `core/page_factory.py` — POM, `get_resilient_*`, logging, strictness. |
| **`test-strategy.mdc`** | `globs: tests/**`, `data/**` — atomic tests, data isolation, `pytest` hooks. |
| **`ai-audit-governance.mdc`** | `globs: ai_audit/**` — Gemini/Ollama policy for failure analysis; **`alwaysApply: false`** (load when editing `ai_audit/`). |
| **`gemini-sdk-migration.mdc`** | Thin `alwaysApply: true` guard for legacy SDK/model strings; defers to `ai-audit-governance.mdc` §2. |

---

## Lean 4-file split (design reference)

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
**Scope:** `globs: ai_audit/**/*.py` (canonical policy when editing `ai_audit/`; not always-injected project-wide by design)

> This rule is the **enforcing standard** for Gemini SDK, model, and initialization policy. `gemini-sdk-migration.mdc` stays a thin legacy-pattern guard that points back here rather than duplicating that section.

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
| Data | Pull static data from `data/testdata.json` or equivalent. Use `utils/helpers.py` for runtime data. No hardcoded user credentials, names, or IDs in test steps. |
| Markers | Use `@pytest.mark.smoke`, `@pytest.mark.regression`, `@pytest.mark.pim`, `@pytest.mark.leave`. |
| Parallel safety | Reference `BASE_URL` from config; assume `pytest-xdist` parallel runs; no shared file handles in tests. |
| Assertions | `expect(locator)` for UI; `assert` only for data/non-UI checks. |
| Conftest | `browser_context` fixture handles browser lifecycle. `logged_in_page_factory` for regression. `pytest_sessionfinish` hook auto-triggers local failure analysis when `reports/failures.txt` exists and Ollama is reachable. |

---

## Case study: framework smearing mitigation

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
|-------|-----------------|
| `async def` + `await` | This project uses `playwright.sync_api`. Async patterns are **architecturally incompatible** with the sync Playwright session lifecycle. |
| `get_by_xpath(...)` | Playwright's Python API does not have a `get_by_xpath` method. This is a **Selenium `By.XPATH` hallucination** — the LLM confused Playwright Python with Selenium's `driver.find_element(By.XPATH, ...)`. |
| Parent + child `.or_()` | `get_by_role("alert").or_(get_by_xpath("//div[@class='error-message']"))` would still hit the strict-mode violation if both resolve to different nodes. |

### Root cause of hallucination

The local Ollama model (`llama3`) has heavy Selenium training data. Without an explicit framework separation rule in context, it defaults to Selenium/async patterns when Playwright prompts look ambiguous.

### Mitigation: strict framework separation

This is the **primary justification** for `playwright-core-sync.mdc` with `alwaysApply: true`. By injecting into every session:

1. **Async ban** — agents cannot generate `async def` / `await` in page/test code.
2. **Locator API mandate** — `get_by_role`, `get_by_label`, `get_by_testid`, `get_by_placeholder`; no Selenium-style `find_element(By.*)` or `get_by_xpath`.
3. **Framework identity** — explicit "This project uses `playwright.sync_api` (Python)" prevents model drift toward Selenium, JS Playwright, or Cypress patterns.

`ai-audit-governance.mdc` and `gemini-sdk-migration.mdc` address Gemini API drift in `ai_audit/`.

---

## Migration (completed)

1. **Author** the `.mdc` files under **`.cursor/rules/`** (done).
2. **Verify** in Cursor that rules attach for representative files; adjust `globs` if needed (ongoing as the codebase changes).
3. **Remove** the obsolete single root project-rules file (done 2026-04-23). **Option B (clean removal)** was chosen: no "pointer" file left behind to avoid split-brain.

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| `alwaysApply: true` context bloat | Keep `playwright-core-sync.mdc` and `gemini-sdk-migration.mdc` short; put detail in globs-scoped rules. |
| Globs too narrow (rule misses) | Start broad (`pages/**/*.py`); narrow if noise appears in unrelated files. |
| `ai_audit` policy only when needed | `ai-audit-governance.mdc` is **`alwaysApply: false`** with `globs: ai_audit/**`; the thin `gemini-sdk-migration.mdc` always applies a minimal legacy-SDK block. |
| LLM still hallucinates (new patterns) | Iteratively add `BANNED:` lines to the relevant rule and document the case study. |

---

## Open decisions (resolved)

| Decision | Resolution |
|----------|------------|
| Number of files | **4** core governance files, plus `gemini-sdk-migration.mdc` as a small always-on guard. |
| Single root rules file | **Removed**; `.cursor/rules/` is the governance layer. |
| Sync/async governance | **Mandatory `alwaysApply: true` ban** in `playwright-core-sync.mdc` |
| Gemini SDK source of truth | **`ai-audit-governance.mdc`** (canonical policy; `gemini-sdk-migration.mdc` is the thin guard) |
| Locator strictness | **Documented in `page-object-standards.mdc`** with parent/child union anti-pattern |
| Resilience mandate | **`get_resilient_locator()` mandatory** in all page objects |
| Framework smearing | **Addressed** — case study section + sync ban + locator API mandate |

---

*Update this document when new hallucination patterns are observed or when rules are adjusted.*
