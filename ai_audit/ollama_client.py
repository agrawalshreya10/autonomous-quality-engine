"""Ollama-based LLM client for local failure analysis (requests -> /api/generate)."""

import json
import os

import requests

from ai_audit.client import LLMClient


class OllamaClient(LLMClient):
    """Call local Ollama HTTP API with the llama3 family (or OLLAMA_MODEL)."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_sec: int = 60,
    ) -> None:
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or "llama3"
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
        try:
            resp = requests.post(
                url,
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
                timeout=self.timeout_sec,
            )
            resp.raise_for_status()
            data = resp.json()
            return (data.get("response") or "").strip()
        except requests.exceptions.RequestException as e:
            return (
                f"Ollama request failed: {e}. Is Ollama running? "
                f"Try: ollama serve && ollama pull {self.model}"
            )
        except Exception as e:
            return f"Error: {e}"
