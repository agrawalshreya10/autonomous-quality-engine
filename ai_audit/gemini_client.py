"""Gemini (Google AI) client for failure analysis via generateContent REST API."""

import json
import os
import urllib.error
import urllib.request

from ai_audit.client import LLMClient


class GeminiClient(LLMClient):
    """Call Gemini generateContent API when GEMINI_API_KEY is set."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-1.5-flash",
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
                "or use OllamaClient (--client ollama) for local analysis."
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
            "You are a Senior SDET. A Playwright (Python) UI test failed.",
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
            "Respond with two short sections: "
            "**Probable cause** and **Suggested fix** (code or steps). Use markdown."
        )
        return "\n\n".join(parts)

    def _generate(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                data = json.loads(resp.read().decode())
                candidates = data.get("candidates") or []
                if not candidates:
                    return f"Unexpected Gemini response: {data!r}"
                content = candidates[0].get("content") or {}
                text_parts = content.get("parts") or []
                return (text_parts[0].get("text", "") if text_parts else "").strip()
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors="replace") if e.fp else ""
            return f"Gemini HTTP {e.code}: {err_body or e.reason}"
        except urllib.error.URLError as e:
            return f"Gemini request failed: {e.reason}"
        except Exception as e:
            return f"Gemini error: {e}"
