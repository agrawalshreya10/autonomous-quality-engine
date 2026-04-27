"""Ollama-based LLM client for local failure analysis (requests -> /api/generate)."""

import json
import os

import requests

from ai_audit.client import LLMClient

# Default when OLLAMA_MODEL is unset and no constructor `model` is passed (keep in sync with failure_analyzer CLI).
DEFAULT_OLLAMA_MODEL = "llama3"


class OllamaClient(LLMClient):
    """Call local Ollama HTTP API; model from constructor, ``OLLAMA_MODEL`` env, or ``DEFAULT_OLLAMA_MODEL``."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_sec: int = 60,
    ) -> None:
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL
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
