"""Unit tests for failure_analyzer CLI helpers (#9, #10, #16)."""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

from ai_audit import failure_analyzer as fa
from ai_audit.gemini_client import (
    ALLOWED_GEMINI_MODELS,
    DEFAULT_GEMINI_MODEL,
    GeminiClient,
    validate_gemini_model,
)

pytestmark = pytest.mark.unit


class TestOllamaHealthUrl:
    def test_default_host_port(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        assert fa._ollama_host_port() == ("127.0.0.1", 11434)

    def test_custom_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://ollama.internal:11435")
        assert fa._ollama_host_port() == ("ollama.internal", 11435)

    def test_host_without_scheme(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OLLAMA_BASE_URL", "10.0.0.5:1234")
        assert fa._ollama_host_port() == ("10.0.0.5", 1234)

    def test_health_uses_parsed_host(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom-host:9999")
        seen: list[tuple[str, int]] = []

        def fake_create_connection(address, timeout=None):  # noqa: ANN001
            seen.append(address)
            raise OSError("refused")

        monkeypatch.setattr(socket, "create_connection", fake_create_connection)
        assert fa._check_ollama_health() is False
        assert seen == [("custom-host", 9999)]

    def test_health_ok(self, monkeypatch: pytest.MonkeyPatch) -> None:
        class _Conn:
            def __enter__(self) -> _Conn:
                return self

            def __exit__(self, *args: object) -> None:
                return None

        monkeypatch.setattr(socket, "create_connection", lambda *a, **k: _Conn())
        assert fa._check_ollama_health() is True


class TestGeminiAllowlist:
    def test_default_and_override_allowed(self) -> None:
        assert validate_gemini_model(DEFAULT_GEMINI_MODEL) == DEFAULT_GEMINI_MODEL
        assert validate_gemini_model("gemini-3.1-flash-preview") == (
            "gemini-3.1-flash-preview"
        )
        assert ALLOWED_GEMINI_MODELS == {
            "gemini-3.1-flash-lite-preview",
            "gemini-3.1-flash-preview",
        }

    def test_decommissioned_rejected(self) -> None:
        with pytest.raises(ValueError, match="Unsupported Gemini model"):
            validate_gemini_model("gemini-1.5-flash")
        with pytest.raises(ValueError, match="Unsupported Gemini model"):
            fa._resolve_model("gemini", "gemini-1.5-pro")
        with pytest.raises(ValueError, match="Unsupported Gemini model"):
            GeminiClient(api_key="test-key", model="gemini-1.0-pro")

    def test_resolve_defaults(self) -> None:
        assert fa._resolve_model("gemini", None) == DEFAULT_GEMINI_MODEL
        assert fa._resolve_model("ollama", None) == fa.DEFAULT_OLLAMA_MODEL


class TestMissingFailuresPath:
    def test_explicit_missing_failures_exits(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        missing = tmp_path / "does-not-exist.txt"
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "failure_analyzer",
                "--failures",
                str(missing),
                "--client",
                "ollama",
            ],
        )
        assert fa.main() == 1
        err = capsys.readouterr().err
        assert "Failures file not found" in err
        assert str(missing) in err
