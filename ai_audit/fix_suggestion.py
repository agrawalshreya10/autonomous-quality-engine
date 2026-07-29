"""Structured fix-suggestion schema, markdown rendering, and HEURISTIC_FALLBACK."""

from __future__ import annotations

import logging
import re
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger("ai_audit.fix_suggestion")

Category = Literal["Locator", "Timing", "Data", "Environment"]

# Short, stable preamble — fold project rules once (ai-audit-governance.mdc §2 Instruction folding).
SYSTEM_PREAMBLE = (
    "You are a Quality Architect for this Playwright Python suite. "
    "Output Playwright sync_api only; no Selenium; no async. "
    "Prefer BasePage get_resilient_* helpers; do not use parent–child .or_() unions. "
    "Respond with JSON only matching the schema fields: "
    "category (Locator|Timing|Data|Environment), root_cause, fix_markdown, confidence (0-1)."
)

_FIX_GUIDANCE = (
    "Fill fix_markdown with a concise Playwright sync Page Object fix "
    "(prefer get_resilient_*; cite standards docs if unsure). "
    "Do not invent Selenium or async code."
)

_LOCATOR_KEYWORDS = (
    "locator",
    "selector",
    "get_by_",
    "strict mode",
    "resolved to",
    "not visible",
    "not found",
)
_TIMING_KEYWORDS = ("timeout", "timed out", "waiting for", "wait_for")
_DATA_KEYWORDS = ("assert", "expected", "credential", "password", "username", "mismatch")
_ENV_KEYWORDS = (
    "connection",
    "network",
    "refused",
    "certificate",
    "base_url",
    "env",
    "dns",
)

_FALLBACK_FIX = (
    "Do not apply fabricated Selenium or async Playwright snippets. "
    "Review this failure against project standards before changing code:\n\n"
    "- `docs/decisions/playwright-locators-and-logging.md`\n"
    "- `.cursor/rules/page-object-standards.mdc`\n\n"
    "Use Playwright **sync_api** only (no Selenium, no async). "
    "Prefer `BasePage` helpers (`get_resilient_locator`, `get_resilient_role_button`, "
    "`get_resilient_role_menuitem`, `get_resilient_placeholder`). "
    "Avoid parent–child `.or_()` unions that violate strict mode."
)

# Banned patterns in suggested Fix code (ai-audit-governance.mdc §3). Labels are for logs/fallback reasons.
_BANNED_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bfrom\s+selenium\b", re.IGNORECASE), "selenium import"),
    (re.compile(r"\bimport\s+selenium\b", re.IGNORECASE), "selenium import"),
    (re.compile(r"\bWebDriverWait\b"), "WebDriverWait"),
    (re.compile(r"\bexpected_conditions\b"), "expected_conditions"),
    (re.compile(r"\bdriver\.find_element\b"), "driver.find_element"),
    (re.compile(r"\bBy\.(?:ID|XPATH|CSS_SELECTOR|NAME|CLASS_NAME|TAG_NAME|LINK_TEXT)\b"), "Selenium By."),
    (re.compile(r"\bget_by_xpath\b"), "get_by_xpath"),
    (re.compile(r"\bquerySelector\b"), "querySelector"),
    (re.compile(r"\bplaywright\.async_api\b"), "playwright.async_api"),
    (re.compile(r"\basync\s+def\b"), "async def"),
    (re.compile(r"\bawait\s+\w"), "await"),
)

_ROOT_CAUSE_MAX_CHARS = 800


class FixSuggestion(BaseModel):
    """Validated assistant reply for a single failure analysis (Ollama or Gemini)."""

    category: Category
    root_cause: str = Field(min_length=1)
    fix_markdown: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("fix_markdown", "root_cause")
    @classmethod
    def _strip_nonempty(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must be non-empty after strip")
        return stripped


def fix_suggestion_json_schema() -> dict:
    """JSON Schema for constrained decoding (Ollama ``format``, Gemini ``response_schema``)."""
    return FixSuggestion.model_json_schema()


# Backward-compatible alias used by older call sites / docs.
ollama_format_schema = fix_suggestion_json_schema


def build_analysis_prompt(
    *,
    test_name: str,
    failure_message: str,
    log_snippet: str = "",
    screenshot_path: str | None = None,
) -> str:
    """Shared Quality Architect prompt for both Ollama and Gemini."""
    parts = [
        SYSTEM_PREAMBLE,
        f"Test: {test_name}",
        f"Failure/error: {failure_message}",
    ]
    if log_snippet:
        parts.append(f"Log snippet:\n{log_snippet}")
    if screenshot_path:
        parts.append(
            f"A screenshot was saved at: {screenshot_path} "
            "(you cannot see the pixels; suggest based on typical UI issues)."
        )
    parts.append(_FIX_GUIDANCE)
    return "\n\n".join(parts)


def render_suggestion_markdown(suggestion: FixSuggestion) -> str:
    """Render a validated suggestion as markdown for ``reports/ai_suggestions.md``."""
    return (
        f"**Category:** {suggestion.category}\n\n"
        f"**Root Cause:** {suggestion.root_cause}\n\n"
        f"**Fix:**\n{suggestion.fix_markdown}\n\n"
        f"**Confidence:** {suggestion.confidence:.2f}"
    )


def infer_category(failure_message: str) -> Category:
    """Deterministic category from keyword match on the failure string."""
    lower = failure_message.lower()
    if any(k in lower for k in _LOCATOR_KEYWORDS):
        return "Locator"
    if any(k in lower for k in _TIMING_KEYWORDS):
        return "Timing"
    if any(k in lower for k in _DATA_KEYWORDS):
        return "Data"
    if any(k in lower for k in _ENV_KEYWORDS):
        return "Environment"
    return "Locator"


def truncate_root_cause(failure_message: str, max_chars: int = _ROOT_CAUSE_MAX_CHARS) -> str:
    """Use a truncated failure/traceback summary as root cause."""
    text = failure_message.strip() or "(empty failure message)"
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def heuristic_fallback(
    failure_message: str,
    *,
    reason: str,
) -> str:
    """
    Emit deterministic HEURISTIC_FALLBACK markdown when schema validation fails,
    ``fix_markdown`` is empty, or banned patterns are found.
    """
    category = infer_category(failure_message)
    root_cause = truncate_root_cause(failure_message)
    suggestion = FixSuggestion(
        category=category,
        root_cause=root_cause,
        fix_markdown=_FALLBACK_FIX,
        confidence=0.0,
    )
    header = (
        f"*HEURISTIC_FALLBACK* ({reason})\n\n"
        if reason
        else "*HEURISTIC_FALLBACK*\n\n"
    )
    return header + render_suggestion_markdown(suggestion)


def find_banned_patterns(text: str) -> list[str]:
    """
    Return labels for banned framework patterns in suggested fix text.

    Scans ``fix_markdown`` only (not root_cause) so traceback quotes do not false-positive.
    """
    hits: list[str] = []
    for pattern, label in _BANNED_PATTERNS:
        if pattern.search(text) and label not in hits:
            hits.append(label)
    return hits


def _strip_json_fences(text: str) -> str:
    """Remove optional markdown code fences around JSON."""
    stripped = text.strip()
    fence = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", stripped, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return stripped


def parse_fix_suggestion(raw_text: str) -> FixSuggestion:
    """
    Parse and validate model output as :class:`FixSuggestion`.

    :raises ValidationError: if JSON is invalid or fields fail validation
    :raises ValueError: if ``fix_markdown`` is empty after validation
    """
    payload = _strip_json_fences(raw_text)
    suggestion = FixSuggestion.model_validate_json(payload)
    if not suggestion.fix_markdown.strip():
        raise ValueError("empty fix_markdown")
    return suggestion


def validate_or_fallback(
    raw_text: str,
    failure_message: str,
    *,
    test_name: str = "",
    provider: str = "",
) -> str:
    """
    Validate structured model JSON and policy-scan ``fix_markdown``.

    On schema or banned-pattern failure, log WARNING and return HEURISTIC_FALLBACK.
    """
    try:
        suggestion = parse_fix_suggestion(raw_text)
    except (ValidationError, ValueError, TypeError) as exc:
        logger.warning(
            "Structured output validation failed "
            "(provider=%s, test_name=%r, reason=%s); emitting HEURISTIC_FALLBACK",
            provider or "unknown",
            test_name,
            exc,
        )
        return heuristic_fallback(failure_message, reason=f"validation failed: {exc}")

    violations = find_banned_patterns(suggestion.fix_markdown)
    if violations:
        logger.warning(
            "Banned patterns in fix_markdown "
            "(provider=%s, test_name=%r, violations=%s); emitting HEURISTIC_FALLBACK",
            provider or "unknown",
            test_name,
            violations,
        )
        return heuristic_fallback(
            failure_message,
            reason=f"banned pattern: {violations[0]}",
        )

    return render_suggestion_markdown(suggestion)
