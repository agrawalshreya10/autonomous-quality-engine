"""Gemini (Google AI) client for failure analysis via google-generativeai SDK."""

import os

from ai_audit.client import LLMClient


class GeminiClient(LLMClient):
    """Call Gemini when GEMINI_API_KEY is set (google-generativeai)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
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
        return self._generate(prompt)

    def _build_prompt(
        self,
        test_name: str,
        failure_message: str,
        log_snippet: str = "",
        screenshot_path: str | None = None,
    ) -> str:
        parts = [
            "You are a Quality Architect. Analyze the following failure. "
            "Categorize it and provide the exact Playwright Python code fix using the Page Object Model and .or() resilient locators.",
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
            "**Fix** (exact Python code using self.get_by_role().or_() patterns). Use markdown."
        )
        return "\n\n".join(parts)

    def _generate(self, prompt: str) -> str:
        try:
            import google.generativeai as genai
        except ImportError:
            return (
                "google-generativeai is not installed. Run: pip install google-generativeai"
            )

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                ),
                request_options={"timeout": self.timeout_sec},
            )
            text = (getattr(response, "text", None) or "").strip()
            if text:
                return text
            return f"Unexpected Gemini response (no text): {response!r}"
        except Exception as e:
            return f"Gemini error: {e}"
