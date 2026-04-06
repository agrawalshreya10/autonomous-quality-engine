"""Ollama-based LLM client for local failure analysis."""

import json
import urllib.error
import urllib.request

from ai_audit.client import LLMClient


class OllamaClient(LLMClient):
    """Call local Ollama API (e.g. ollama run llama3.2) to suggest fixes."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2",
        timeout_sec: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_sec = timeout_sec

    def suggest_fix(
        self,
        test_name: str,
        failure_message: str,
        log_snippet: str = "",
        screenshot_path: str | None = None,
    ) -> str:
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
        url = f"{self.base_url}/api/generate"
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
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
                return data.get("response", "").strip()
        except urllib.error.URLError as e:
            return f"Ollama request failed: {e}. Is Ollama running? Try: ollama run {self.model}"
        except Exception as e:
            return f"Error: {e}"
