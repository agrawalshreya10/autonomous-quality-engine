"""
Failure analyzer: read test failures from artifacts and ask LLM for fix suggestions.

Provider selection is explicit: set AI_PROVIDER in .env (ollama or gemini; default ollama).
Run locally after downloading CI artifacts:
  python -m ai_audit.failure_analyzer --artifacts-dir ./artifacts
Or with a failures file:
  python -m ai_audit.failure_analyzer --failures failures.txt
"""

import argparse
import os
import re
import socket
import sys
from pathlib import Path

from dotenv import load_dotenv

from ai_audit.client import LLMClient
from ai_audit.gemini_client import GeminiClient
from ai_audit.ollama_client import OllamaClient


def _find_screenshot(artifacts_dir: Path, test_name: str) -> str | None:
    """Look for a screenshot matching test name in reports/screenshots or screenshots."""
    for sub in ("reports/screenshots", "screenshots"):
        screenshots = artifacts_dir / sub
        if screenshots.exists():
            for f in screenshots.glob("*.png"):
                stem = f.stem
                if test_name in stem or stem in test_name or stem in test_name.replace("::", "_"):
                    return str(f)
    return None


def _trim_failure_message(message: str, max_chars: int = 2000) -> str:
    """
    Smart truncation: extract AssertionError and last 3 lines of traceback.
    Cap at max_chars to ensure fast local inference and low token costs.
    """
    if len(message) <= max_chars:
        return message
    
    lines = message.splitlines()
    
    # Find AssertionError or similar key failure lines
    assertion_lines = []
    traceback_lines = []
    
    for i, line in enumerate(lines):
        # Capture assertion errors, playwright errors, or other key failure indicators
        if any(keyword in line.lower() for keyword in ['assertionerror', 'error:', 'failed:', 'timeout']):
            # Include this line and a few context lines
            start = max(0, i - 1)
            end = min(len(lines), i + 2)
            assertion_lines.extend(lines[start:end])
            break
    
    # Get last 3 lines of traceback (usually the most relevant)
    if len(lines) >= 3:
        traceback_lines = lines[-3:]
    
    # Combine and deduplicate
    key_lines = []
    seen = set()
    for line in assertion_lines + traceback_lines:
        if line.strip() and line not in seen:
            key_lines.append(line)
            seen.add(line)
    
    # Join and truncate if still too long
    result = "\n".join(key_lines)
    if len(result) > max_chars:
        result = result[:max_chars - 3] + "..."
    
    return result if result.strip() else message[:max_chars]


def _check_ollama_health() -> bool:
    """Check if Ollama is running on default port 11434."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        return result == 0
    except Exception:
        return False


def _parse_failures_file(path: Path) -> list[tuple[str, str]]:
    """Parse a simple failures file: each block is 'TEST: name' then 'MESSAGE: ...'."""
    text = path.read_text()
    pairs: list[tuple[str, str]] = []
    current_name: str | None = None
    current_msg: list[str] = []
    for line in text.splitlines():
        if line.startswith("TEST:"):
            if current_name and current_msg:
                pairs.append((current_name, "\n".join(current_msg)))
            current_name = line.replace("TEST:", "").strip()
            current_msg = []
        elif line.startswith("MESSAGE:") or (current_name and not line.startswith("TEST:")):
            if line.startswith("MESSAGE:"):
                line = line.replace("MESSAGE:", "").strip()
            current_msg.append(line)
    if current_name and current_msg:
        pairs.append((current_name, "\n".join(current_msg)))
    return pairs


def _read_failures_from_artifacts(artifacts_dir: Path) -> list[tuple[str, str, str | None]]:
    """Try to find failures in artifact dir: look for failures.txt or report."""
    results: list[tuple[str, str, str | None]] = []
    for failures_file in (artifacts_dir / "failures.txt", artifacts_dir / "reports" / "failures.txt"):
        if failures_file.exists():
            for name, msg in _parse_failures_file(failures_file):
                # Apply smart truncation to reduce noise
                trimmed_msg = _trim_failure_message(msg)
                screenshot = _find_screenshot(artifacts_dir, name)
                results.append((name, trimmed_msg, screenshot))
            return results
    for report_path in (artifacts_dir / "reports" / "report.html", artifacts_dir / "report.html"):
        if report_path.exists():
            html = report_path.read_text()
            for m in re.finditer(r'data-test-id="([^"]+)".*?class="[^"]*failed[^"]*"', html, re.DOTALL):
                results.append((m.group(1), "See report.html for details", _find_screenshot(artifacts_dir, m.group(1))))
            if not results:
                for m in re.finditer(r'<td[^>]*>([^<]*test_[^<]+)</td>', html):
                    results.append((m.group(1).strip(), "See report.html for details", _find_screenshot(artifacts_dir, m.group(1).strip())))
            return results[:10]
    return results


def _effective_provider(cli_client: str) -> str:
    """
    Resolve provider: explicit --client ollama|gemini overrides; --client auto uses AI_PROVIDER
    from the environment (default ollama if missing or empty).
    """
    if cli_client in ("ollama", "gemini"):
        return cli_client
    raw = os.environ.get("AI_PROVIDER", "")
    normalized = raw.strip().lower()
    if not normalized:
        return "ollama"
    if normalized in ("ollama", "gemini"):
        return normalized
    raise ValueError(
        f"AI_PROVIDER must be 'ollama' or 'gemini' (got {raw!r}). "
        "Unset or empty defaults to ollama."
    )


def _resolve_model(provider: str, model: str | None) -> str:
    if model:
        return model
    return "gemini-3-flash" if provider == "gemini" else "llama3"


def get_client(provider: str, model: str | None) -> LLMClient | None:
    """Return OllamaClient or GeminiClient from explicit provider only."""
    resolved_model = _resolve_model(provider, model)
    if provider == "gemini":
        if not os.environ.get("GEMINI_API_KEY"):
            raise RuntimeError(
                "Gemini requested but API Key is missing. Check your .env or CI Secrets."
            )
        return GeminiClient(model=resolved_model)
    if provider == "ollama":
        if not _check_ollama_health():
            print("[AI-AUDIT] Local Ollama not detected. Skipping auto-analysis. To enable, run 'ollama serve'.")
            return None
        return OllamaClient(model=resolved_model)
    raise ValueError(f"Unknown provider: {provider!r}")


def main() -> int:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Analyze test failures with Ollama (local) or Gemini (cloud)")
    parser.add_argument("--artifacts-dir", type=Path, default=Path("."), help="Directory containing reports/ and optionally failures.txt")
    parser.add_argument("--failures", type=Path, help="Path to failures file (TEST: / MESSAGE: format)")
    parser.add_argument(
        "--client",
        choices=("auto", "ollama", "gemini"),
        default="auto",
        help="LLM backend: auto reads AI_PROVIDER from .env (default ollama); ollama|gemini overrides for this run",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override (Ollama default: llama3, Gemini default: gemini-3-flash)",
    )
    parser.add_argument("--out", type=Path, help="Write suggestions to file")
    args = parser.parse_args()

    try:
        effective_provider = _effective_provider(args.client)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.failures and args.failures.exists():
        failures = [(n, _trim_failure_message(m), None) for n, m in _parse_failures_file(args.failures)]
    else:
        failures = _read_failures_from_artifacts(args.artifacts_dir)

    if not failures:
        print("No failures found. Create failures.txt with TEST: and MESSAGE: lines, or run tests and pass --artifacts-dir to the directory with reports/report.html.", file=sys.stderr)
        return 1

    try:
        client = get_client(effective_provider, args.model)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1
    if client is None:
        return 1  # Ollama health check failed

    audit_line = f"[SYSTEM] AI Audit initiated using provider: {effective_provider}\n"
    print(audit_line, end="")

    output_lines: list[str] = [audit_line]
    for test_name, message, screenshot_path in failures:
        out = client.suggest_fix(
            test_name=test_name,
            failure_message=message,
            screenshot_path=screenshot_path,
        )
        output_lines.append(f"## {test_name}\n\n{out}\n\n---\n")
        print(f"## {test_name}\n\n{out}\n\n---")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text("\n".join(output_lines))
        print(f"\nWrote suggestions to {args.out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
