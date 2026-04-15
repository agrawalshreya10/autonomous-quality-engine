"""Gemini (Google AI) client for failure analysis via google-genai SDK."""

import os

from ai_audit.client import LLMClient


class GeminiClient(LLMClient):
    """Call Gemini when GEMINI_API_KEY is set (google-genai)."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-3-flash",
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
            from google import genai
            from google.genai import types
        except ImportError:
            return (
                "google-genai is not installed. Run: pip install google-genai"
            )

        try:
            client = genai.Client(api_key=self.api_key)
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
            return f"Unexpected Gemini response (no text): {response!r}"
        except Exception as e:
            return f"Gemini error: {e}"
