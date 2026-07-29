"""Unit tests for structured fix suggestions (no LLM / no browser)."""

from __future__ import annotations

import json

import pytest

from ai_audit.fix_suggestion import (
    FixSuggestion,
    find_banned_patterns,
    fix_suggestion_json_schema,
    heuristic_fallback,
    parse_fix_suggestion,
    render_suggestion_markdown,
    validate_or_fallback,
)

pytestmark = pytest.mark.unit

_VALID_PAYLOAD = {
    "category": "Locator",
    "root_cause": "Login error alert locator timed out.",
    "fix_markdown": (
        "Use `self.error_message = self._page.locator('.oxd-alert-content-text')` "
        "and `expect(self.error_message).to_be_visible()`."
    ),
    "confidence": 0.85,
}


def _valid_json(**overrides: object) -> str:
    payload = {**_VALID_PAYLOAD, **overrides}
    return json.dumps(payload)


class TestParseAndRender:
    def test_valid_structured_json(self) -> None:
        suggestion = parse_fix_suggestion(_valid_json())
        assert suggestion.category == "Locator"
        assert suggestion.confidence == 0.85
        md = render_suggestion_markdown(suggestion)
        assert "**Category:** Locator" in md
        assert "**Root Cause:**" in md
        assert "**Fix:**" in md
        assert "**Confidence:** 0.85" in md

    def test_markdown_fenced_json(self) -> None:
        fenced = f"```json\n{_valid_json()}\n```"
        suggestion = parse_fix_suggestion(fenced)
        assert suggestion.category == "Locator"

    def test_invalid_json_raises(self) -> None:
        with pytest.raises(Exception):
            parse_fix_suggestion("{not json")

    def test_invalid_category_raises(self) -> None:
        with pytest.raises(Exception):
            parse_fix_suggestion(_valid_json(category="Network"))

    def test_empty_fix_markdown_raises(self) -> None:
        with pytest.raises(Exception):
            parse_fix_suggestion(_valid_json(fix_markdown="   "))


class TestValidateOrFallback:
    def test_valid_renders_markdown(self) -> None:
        out = validate_or_fallback(
            _valid_json(),
            "locator not found",
            test_name="test_login",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" not in out
        assert "**Category:** Locator" in out
        assert "**Confidence:** 0.85" in out

    def test_invalid_json_fallback(self) -> None:
        out = validate_or_fallback(
            "{not json",
            "Timeout waiting for locator",
            provider="ollama",
        )
        assert out.startswith("*HEURISTIC_FALLBACK*")
        assert "**Category:**" in out
        assert "**Confidence:** 0.00" in out

    def test_invalid_category_fallback(self) -> None:
        out = validate_or_fallback(
            _valid_json(category="Flaky"),
            "selector resolved to 2 elements",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" in out

    def test_empty_response_fallback(self) -> None:
        out = validate_or_fallback("", "connection refused", provider="gemini")
        assert "*HEURISTIC_FALLBACK*" in out
        assert "**Category:** Environment" in out

    def test_empty_fix_markdown_fallback(self) -> None:
        out = validate_or_fallback(
            _valid_json(fix_markdown=""),
            "assert expected mismatch",
            provider="ollama",
        )
        assert "*HEURISTIC_FALLBACK*" in out


class TestBannedPatterns:
    def test_clean_sync_fix_ok(self) -> None:
        assert find_banned_patterns(_VALID_PAYLOAD["fix_markdown"]) == []

    def test_selenium_import_rejected(self) -> None:
        out = validate_or_fallback(
            _valid_json(
                fix_markdown=(
                    "from selenium.webdriver.common.by import By\n"
                    "driver.find_element(By.ID, 'user')"
                )
            ),
            "locator not found",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" in out
        assert "banned pattern:" in out

    def test_await_rejected(self) -> None:
        out = validate_or_fallback(
            _valid_json(fix_markdown="await page.goto(url)"),
            "timeout",
            provider="ollama",
        )
        assert "*HEURISTIC_FALLBACK*" in out
        assert "banned pattern: await" in out

    def test_await_call_syntax_rejected(self) -> None:
        """await(...) has no whitespace after the keyword; still banned."""
        assert find_banned_patterns("await(page.goto(url))") == ["await"]
        out = validate_or_fallback(
            _valid_json(fix_markdown="result = await(self._page.goto(url))"),
            "timeout",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" in out
        assert "banned pattern: await" in out

    def test_get_by_xpath_rejected(self) -> None:
        out = validate_or_fallback(
            _valid_json(fix_markdown="page.get_by_xpath('//div')"),
            "not found",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" in out
        assert "banned pattern: get_by_xpath" in out

    def test_async_in_root_cause_does_not_reject_clean_fix(self) -> None:
        """Policy scans fix_markdown only — traceback quotes in root_cause are allowed."""
        out = validate_or_fallback(
            _valid_json(root_cause="Failure mentioned async timeout in logs"),
            "timeout",
            provider="gemini",
        )
        assert "*HEURISTIC_FALLBACK*" not in out
        assert "**Category:** Locator" in out

    def test_heuristic_fallback_mentions_standards(self) -> None:
        out = heuristic_fallback("locator not visible", reason="banned pattern: await")
        assert "page-object-standards.mdc" in out
        assert "playwright-locators-and-logging.md" in out


class TestSchemaShape:
    def test_json_schema_has_required_fields(self) -> None:
        schema = fix_suggestion_json_schema()
        props = schema.get("properties") or {}
        for key in ("category", "root_cause", "fix_markdown", "confidence"):
            assert key in props
        # Pydantic may expose FixSuggestion as a usable response_schema type.
        assert FixSuggestion.model_fields.keys() >= {
            "category",
            "root_cause",
            "fix_markdown",
            "confidence",
        }
