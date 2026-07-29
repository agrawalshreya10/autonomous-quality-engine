"""Gemini (Google AI) client for failure analysis via google-genai SDK.

Uses :class:`google.genai.Client` and ``client.models.generate_content`` (not
``GenerativeModel``). Default model follows ``.cursor/rules/ai-audit-governance.mdc``.
"""

from __future__ import annotations

import logging
import os

from ai_audit.client import LLMClient
from ai_audit.fix_suggestion import (
    FixSuggestion,
    build_analysis_prompt,
    validate_or_fallback,
)

logger = logging.getLogger("ai_audit.gemini")

# Allowed family: gemini-3.1-flash-lite (GA default) | gemini-3.5-flash (GA override)
# gemini-3.1-flash-lite-preview was shut down 2026-05-25 (see Gemini API deprecations).
# (canonical rule: .cursor/rules/ai-audit-governance.mdc)
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
ALLOWED_GEMINI_MODELS = frozenset(
    {
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
    }
)


def validate_gemini_model(model: str) -> str:
    """Fail fast on decommissioned / unsupported Gemini model IDs."""
    if model not in ALLOWED_GEMINI_MODELS:
        allowed = ", ".join(sorted(ALLOWED_GEMINI_MODELS))
        raise ValueError(
            f"Unsupported Gemini model: {model!r}. Allowed: {allowed}"
        )
    return model


class GeminiClient(LLMClient):
    """Call Gemini when GEMINI_API_KEY is set (google-genai)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout_sec: int = 120,
    ) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = validate_gemini_model(model)
        self.timeout_sec = timeout_sec

    def suggest_fix(
        self,
        test_name: str,
        failure_message: str,
        log_snippet: str = "",
        screenshot_path: str | None = None,
    ) -> str:
        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY missing; skipping Gemini (provider=gemini, test_name=%r, model=%r)",
                test_name,
                self.model,
            )
            return (
                "GEMINI_API_KEY is not set. Export it or add it to .env, "
                "or use Ollama (--client ollama / AI_PROVIDER=ollama) for local analysis."
            )
        prompt = build_analysis_prompt(
            test_name=test_name,
            failure_message=failure_message,
            log_snippet=log_snippet,
            screenshot_path=screenshot_path,
        )
        ok, text = self._generate(prompt, test_name=test_name)
        if not ok:
            return text
        return validate_or_fallback(
            text,
            failure_message,
            test_name=test_name,
            provider="gemini",
        )

    def _generate(self, prompt: str, test_name: str = "") -> tuple[bool, str]:
        """
        Call Gemini with JSON structured output matching :class:`FixSuggestion`.

        :return: ``(True, response_text)`` on SDK success (body may be empty);
            ``(False, error_message)`` on import/API failures (caller must not
            treat as model JSON).
        """
        try:
            from google import genai
            from google.genai import types
        except ImportError as e:
            logger.error(
                "google-genai import failed: %s",
                e,
                exc_info=True,
            )
            return (
                False,
                "google-genai is not installed. Run: pip install google-genai",
            )

        logger.info(
            "Gemini generate_content start (provider=gemini, model=%r, test_name=%r, timeout_sec=%s)",
            self.model,
            test_name,
            self.timeout_sec,
        )

        # HttpOptions.timeout is in milliseconds (see google.genai.types.HttpOptions).
        timeout_ms = max(1, int(self.timeout_sec * 1000))
        try:
            client = genai.Client(
                api_key=self.api_key,
                http_options=types.HttpOptions(timeout=timeout_ms),
            )
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        response_mime_type="application/json",
                        response_schema=FixSuggestion,
                    ),
                )
            finally:
                client.close()

            text = (getattr(response, "text", None) or "").strip()
            if not text:
                logger.warning(
                    "Gemini response had no text (test_name=%r, model=%r, response=%r)",
                    test_name,
                    self.model,
                    response,
                )
            # Empty body still goes through validate_or_fallback → HEURISTIC_FALLBACK.
            return True, text
        except Exception as e:
            logger.error(
                "Gemini generate_content failed (test_name=%r, model=%r): %s",
                test_name,
                self.model,
                e,
                exc_info=True,
            )
            return False, f"Gemini error: {e}"
