"""Ollama-based LLM client for local failure analysis (requests -> /api/generate)."""

import json
import logging
import os

import requests

from ai_audit.client import LLMClient

logger = logging.getLogger("ai_audit.ollama")

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
        url = f"{self.base_url}/api/generate"
        body = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        logger.info(
            "Ollama /api/generate start (provider=ollama, model=%r, test_name=%r, base_url=%r, timeout_sec=%s)",
            self.model,
            test_name,
            self.base_url,
            self.timeout_sec,
        )
        try:
            resp = requests.post(
                url,
                data=json.dumps(body),
                headers={"Content-Type": "application/json"},
                timeout=self.timeout_sec,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            logger.error(
                "Ollama HTTP request failed (test_name=%r, model=%r, status=%s, base_url=%r): %s",
                test_name,
                self.model,
                status,
                self.base_url,
                e,
                exc_info=True,
            )
            if status == 404:
                return (
                    f"Ollama returned 404 (model or route not found). "
                    f"Check OLLAMA_MODEL={self.model!r} and that the server is reachable at {self.base_url!r}."
                )
            return (
                f"Ollama request failed: {e}. Is Ollama running? "
                f"Try: ollama serve && ollama pull {self.model}"
            )

        try:
            data = resp.json()
        except ValueError as e:
            logger.error(
                "Ollama response JSON parse failed (test_name=%r, model=%r): %s",
                test_name,
                self.model,
                e,
                exc_info=True,
            )
            return f"Ollama error: invalid JSON in response: {e}"

        if not isinstance(data, dict):
            logger.warning(
                "Ollama response JSON was not an object (test_name=%r, model=%r, type=%r)",
                test_name,
                self.model,
                type(data).__name__,
            )
            return f"Unexpected Ollama response (not a JSON object): {data!r}"

        text = (data.get("response") or "").strip()
        if text:
            return text
        logger.warning(
            "Ollama response had no text in \"response\" (test_name=%r, model=%r, data=%r)",
            test_name,
            self.model,
            data,
        )
        return f"Unexpected Ollama response (no text): {data!r}"