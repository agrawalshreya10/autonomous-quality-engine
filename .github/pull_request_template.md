## Summary

<!-- What changed and why (1–3 sentences). -->

## Review expectations

- **CodeRabbit** (if enabled on the repo): Expect AI review comments on style and consistency. Treat **`.cursor/rules/*.mdc`** (especially `playwright-core-sync.mdc` and `page-object-standards.mdc`) as the contract for this project: mandatory `element_label` on `BasePage` interactions, resilient `.or_()` on critical locators, `expect()` for UI state, no `page.wait_for_timeout()`.
- **Human review**: Cross-check POM changes against [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) and, for locator/logging behavior, [docs/decisions/playwright-locators-and-logging.md](../docs/decisions/playwright-locators-and-logging.md).

## Checklist

- [ ] I ran tests locally (`pytest` or at least `pytest -m smoke`).
- [ ] Page objects use `self.click` / `self.fill` (or other `BasePage` helpers) with descriptive `element_label` where applicable.
- [ ] No new `wait_for_timeout` calls; UI waits use Playwright auto-wait + `expect` as per `.cursor/rules/playwright-core-sync.mdc`.
