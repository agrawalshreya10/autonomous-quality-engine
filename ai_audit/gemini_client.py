"""Gemini (Google AI) client for failure analysis via google-genai SDK.

Uses :class:`google.genai.Client` and ``client.models.generate_content`` (not
``GenerativeModel``). Default model follows ``.cursor/rules/ai-audit-governance.mdc``.
"""

import logging
import os

from ai_audit.client import LLMClient

logger = logging.getLogger("ai_audit.gemini")

# Allowed family: gemini-3.1-flash-preview | gemini-3.1-flash-lite-preview
# (canonical rule: .cursor/rules/ai-audit-governance.mdc)
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite-preview"


class GeminiClient(LLMClient):
    """Call Gemini when GEMINI_API_KEY is set (google-genai)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_GEMINI_MODEL,
        timeout_sec: int = 120,
    ) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model
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
        prompt = self._build_prompt(
            test_name=test_name,
            failure_message=failure_message,
            log_snippet=log_snippet,
            screenshot_path=screenshot_path,
        )
        return self._generate(prompt, test_name=test_name)

    def _build_prompt(
        self,
        test_name: str,
        failure_message: str,
        log_snippet: str = "",
        screenshot_path: str | None = None,
    ) -> str:
        parts = [
            "You are a Quality Architect. Analyze the following failure. "
            "Categorize it and provide the exact Playwright Python code fix using the Page Object Model. "
            "Prefer self-healing locators via BasePage helpers: get_resilient_locator, get_resilient_role_button, "
            "get_resilient_role_menuitem, and get_resilient_placeholder. "
            "If you must union locators, use the Playwright Python method .or_() (not .or()—that is JavaScript).",
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
        parts.append(
            "Respond with three short sections: "
            "**Category** (Locator, Timing, Data, Environment), "
            "**Root Cause**, and "
            "**Fix** (exact Python for playwright.sync_api: prefer get_resilient_* on BasePage; avoid parent–child "
            ".or_() unions that violate strict mode). Use markdown."
        )
        return "\n\n".join(parts)

    def _generate(self, prompt: str, test_name: str = "") -> str:
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
                "google-genai is not installed. Run: pip install google-genai"
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
                        temperature=0.2,
                    ),
                )
            finally:
                client.close()

            text = (getattr(response, "text", None) or "").strip()
            if text:
                return text
            logger.warning(
                "Gemini response had no text (test_name=%r, model=%r, response=%r)",
                test_name,
                self.model,
                response,
            )
            return f"Unexpected Gemini response (no text): {response!r}"
        except Exception as e:
            logger.error(
                "Gemini generate_content failed (test_name=%r, model=%r): %s",
                test_name,
                self.model,
                e,
                exc_info=True,
            )
            return f"Gemini error: {e}"
