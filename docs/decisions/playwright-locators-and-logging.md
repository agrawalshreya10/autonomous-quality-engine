# Decision: Playwright locators, `.or_()`, interaction logs, and DOM debugging

**Status:** Accepted  
**Date:** 2026-04-03 (debugging session)  
**Scope:** `core/base_page.py` patterns, resilient locators (especially `get_resilient_placeholder`), and how we verify DOM-related assumptions next time.

---

## Why this document exists

A debugging session surfaced two areas where **incorrect mental models** waste time:

1. **Interaction logging** — Past-tense “Performed …” lines must not be emitted before the action succeeds.
2. **`.first` + `.or_()` on locators** — Playwright `Locator` objects are **lazy**; confusing “lazy filter” with “eager resolution” leads to wrong refactors.

This file is the **default checklist** before changing locator chains or logging in `BasePage` and page objects. Enforcement lives in **`.cursor/rules/page-object-standards.mdc`** and **`.cursor/rules/playwright-core-sync.mdc`**.

---

## 1. Interaction logs (`log_interaction` / “Performed …”)

### Correct behavior

- Emit interaction logs **after** `self._run(...)` completes successfully for `navigate`, `click`, and `fill`.
- If `_run` raises, **do not** log “Performed …” — the past-tense message would falsely imply success.
- Errors remain on the structured `_error_logger` path inside `_run` (exception + traceback, re-raise).

### Anti-pattern

- Calling `log_interaction` **before** the wrapped action runs. Failed steps then appear as if they completed.

---

## 2. Resilient placeholder: `get_by_placeholder(...).first.or_(...)`

### Mental model (must be central to DOM decisions)

- Playwright **does not** query the DOM when you build a `Locator`. Chains like `.first` and `.or_()` describe **filters and alternatives**, evaluated when an action or assertion runs.
- **`.first` before `.or_()` is not “premature resolution.”** It constrains the **primary** side of the union to the first match for that placeholder.

### Intended semantics (primary wins over fallback)

Use:

```text
page.get_by_placeholder(primary).first.or_(page.get_by_placeholder(fallback))
```

- The left side is “first element matching the primary placeholder text.”
- The right side is “elements matching the fallback placeholder.”
- The union is evaluated when the test **acts** on the locator; if the primary side matches nothing actionable, the fallback can still participate per Playwright’s rules for the combined locator.

### Regression to avoid

**Do not** “fix” this by moving `.first` to **after** `.or_()`:

```text
page.get_by_placeholder(primary).or_(page.get_by_placeholder(fallback)).first  # risky
```

When **both** placeholders could match different elements in the same DOM, `.first` on the **whole** union picks by **document order**, not “primary first.” That **breaks** the explicit **primary → fallback** priority used elsewhere for self-healing.

### When in doubt

- Prefer verifying behavior against a real page (local OrangeHRM / demo) rather than guessing locator algebra.
- Use **Playwright MCP** (see below) to inspect structure and reduce trial-and-error.

### `.or_()` must not pair **parent** and **child** of the same widget

If the left locator matches a **container** (e.g. `role=alert`, `.oxd-table-body`) and the right matches a **node inside it** (e.g. `.oxd-alert-content-text`, `get_by_text("No Records Found")`), the union can resolve to **two** elements at once. `expect(locator)` and other strict operations then fail. Prefer a **single** locator (e.g. the inner text node only) or wait for **one** stable container that is always present when the view loads.

---

## 3. Playwright MCP (Cursor)

**Config:** `.cursor/mcp.json` registers `@playwright/mcp` (see `mcpServers.playwright`).

**Role in decision-making:** For future DOM checks, prefer driving or inspecting the browser through this MCP when available instead of assuming selector behavior from memory. It keeps **observed DOM** at the center of changes to locators and resilient helpers.

**Note:** MCP availability depends on the editor session and whether the MCP server starts successfully; local `pytest` + traces remain the source of truth for failing tests.

---

## 4. Quick checklist (before merging locator or logging changes)

| Check | Question |
|-------|----------|
| Logging | Is “Performed …” only logged after the action succeeds? |
| `.or_()` | Does the chain preserve **primary-first** intent (especially for placeholders)? |
| `.or_()` | Does the union avoid **parent + child** of the same UI block (strict multi-match)? |
| Laziness | Am I treating `Locator` as a description, not a resolved element handle? |
| Proof | Did I validate against a running app or trace, not only code reading? |

---

## References

- `core/base_page.py` — `_run`, `navigate`, `click`, `fill`, `get_resilient_placeholder`
- **`.cursor/rules/playwright-core-sync.mdc`**, **`.cursor/rules/page-object-standards.mdc`** — enforcing rules for `expect`, no `wait_for_timeout`, resilient critical locators, and strict `.or_()` usage
- [ARCHITECTURE.md](../ARCHITECTURE.md) — high-level design pointer
