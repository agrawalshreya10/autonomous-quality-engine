# Gemini / Google GenAI SDK documentation (reference)

**Purpose:** Keep a project-local index of **authoritative** Gemini + Google GenAI SDK documentation used by `ai_audit/` (Gemini client + failure analyzer) and CI AI Failure Analysis workflow notes.

**Primary sources (official):**

- **Gemini API libraries (recommended SDKs, legacy status, install)**: [Gemini API libraries](https://ai.google.dev/gemini-api/docs/libraries)
- **Python GenAI client reference (generated docs)**: [google-cloud-python genai generated docs](https://googleapis.github.io/google-cloud-python/generated/docs/genai/)

## When to use which link

- Use **Gemini API libraries** when you need:
  - Confirmation that **`google-genai`** is the recommended Python SDK (vs legacy `google-generativeai`)
  - Quickstart install guidance and SDK ecosystem overview
  - Migration guidance signals (legacy library deprecation status)

- Use **generated `genai` docs** when you need:
  - Exact **function signatures** and parameter names (e.g., request config, timeouts)
  - The canonical Python client API surface (`Client`, `models.generate_content`, config/types)

## Project alignment

- The repo’s Gemini integration is implemented under `ai_audit/` and should follow the **Google GenAI SDK** guidance above.
- Default model for failure analysis in this repo: **`gemini-3.1-flash-lite-preview`** (allowed alternatives are defined in **`.cursor/rules/ai-audit-governance.mdc`**).
- For CI behavior and redaction strategy, see [../decisions/ci-ai-failure-analysis.md](../decisions/ci-ai-failure-analysis.md).

