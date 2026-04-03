"""Abstract LLM client for failure analysis. Implementations: Ollama, Gemini."""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract client for requesting fix suggestions from an LLM."""

    @abstractmethod
    def suggest_fix(
        self,
        test_name: str,
        failure_message: str,
        log_snippet: str = "",
        screenshot_path: str | None = None,
    ) -> str:
        """
        Ask the LLM for a probable cause and suggested fix.

        :param test_name: Failed test name (e.g. test_login_success)
        :param failure_message: Assertion or error message
        :param log_snippet: Optional last N lines of test log
        :param screenshot_path: Optional path to screenshot (described in prompt if not sent to API)
        :return: Suggested cause and fix as markdown or plain text
        """
        pass
