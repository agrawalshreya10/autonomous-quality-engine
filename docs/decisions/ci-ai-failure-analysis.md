# Decision: CI failure analysis with a cloud LLM (Gemini)

**Status:** Accepted  
**Scope:** When and how the `ai_audit.failure_analyzer` path may call Gemini (or other backends) from GitHub Actions, versus local-only use.

---

## Context

The project can summarize failed Playwright/pytest runs using `ai_audit.failure_analyzer`, which reads artifacts such as `reports/failures.txt`, `reports/report.html`, and screenshot paths. That text is sent to an LLM backend (e.g. Ollama locally, Gemini via HTTP API) to produce short triage suggestions.

Constraints that matter for CI:

- The repository may be **public**; anything uploaded as an artifact or written to the job summary is broadly visible to people with access to the workflow run.
- **Secrets** (`GEMINI_API_KEY`, credentials) must not appear in committed files; CI injects keys via GitHub Actions secrets.
- **Failure payloads** can contain stack traces, URLs, and occasional sensitive strings if tests or config leak them; treating outbound LLM calls and published outputs as sensitive is appropriate.
- **Third-party APIs** imply cost per call, quota limits, and data egress to the vendor whenever a request is made.

The options below are labeled **A–D** for reference in other documents and discussions.

---

## Options

### A — Automatic cloud LLM on every CI failure

Run the analyzer in the same job as tests, conditioned on `failure()`, whenever `GEMINI_API_KEY` is present. Publish results to the job summary and/or artifacts.

**Characteristics:** Maximum automation; every red build that reaches this step can trigger API usage and egress of failure context.

### B — Gated / on-demand cloud LLM in CI

Do **not** tie inference to every failed test job by default. Invoke analysis only through an explicit trigger, for example:

- A separate workflow with `workflow_dispatch` (manual run from the Actions UI), or
- Another controlled entry point (scheduled job, `workflow_run` after tests with strict inputs, etc.).

Local development remains unchanged: developers can still run `python -m ai_audit.failure_analyzer` with Ollama or Gemini from their machine.

**Characteristics:** API calls happen when someone deliberately starts analysis, not on every failing pipeline.

### C — No cloud LLM in CI; local-only

CI produces reports, screenshots, and `failures.txt` only. Any LLM usage is **only** on developer machines (e.g. Ollama) or outside GitHub Actions.

**Characteristics:** No cloud API key required in GitHub; no vendor egress from CI; triage is manual or local.

### D — Hygiene and publication surface (orthogonal to A/B/C)

**D is not a substitute for choosing A, B, or C.** It defines **how** outputs are handled **when** analysis runs:

- Prefer a **single** primary channel for human-readable AI output (e.g. job summary **or** one redacted artifact—not both duplicating the same content without reason).
- Apply **redaction** before publishing (e.g. patterns for API-key-shaped strings, `Bearer` tokens, common `*_SECRET` / `*_PASSWORD` assignments).
- Use **`::add-mask::`** (or equivalent) for known secret values in CI logs.
- Avoid storing **unredacted** full model output as a long-lived **internal** artifact in GitHub unless there is a clear need; the ephemeral runner already held the raw file during the step.

**Characteristics:** Reduces redundant copies, narrows retention risk, and keeps logs and artifacts easier to reason about for security review.

---

## Evaluation criteria

| Criterion | Notes |
|-----------|--------|
| API cost and call frequency | Automatic per-failure runs scale with flake rate and branch volume. |
| Operational complexity | More workflows and triggers require documentation and occasional debugging. |
| Data egress and retention | Each call sends failure text to the vendor; artifacts/summaries retain derived text on GitHub. |
| Secret exposure risk | Logs, summaries, and artifacts can leak credentials if tests or redaction miss a pattern. |
| Maintainability | Shell `sed`/redaction and workflow steps must be kept consistent when changing report formats. |
| Common enterprise posture | Many organizations limit automatic transmission of build/log data to external SaaS without explicit intent or policy alignment. |

---

## Decision

Adopt **B + D**:

1. **B** governs **when** the cloud LLM runs in CI: **on-demand** (or otherwise explicitly gated), not automatically on every failed test job.
2. **D** governs **how** results are published when analysis **does** run: masked secrets, redacted text, a **single** clear publication surface, and no standing practice of uploading unredacted full responses as routine artifacts.

**B and D address different layers:** scheduling/triggering versus output handling. They are combined by design.

---

## Consequences

- The default **test** workflow should **not** depend on running Gemini on every `failure()` if the repository follows this decision; a **separate** workflow (or manual procedure) documents how to run analysis after a failure.
- `GEMINI_API_KEY` remains optional in GitHub: CI test jobs can stay green without it; the on-demand workflow documents that the secret is required **only** when that workflow is used.
- Local workflows stay valid: `failure_analyzer` with `--client ollama` or `--client gemini` and `.env` / environment variables.
- Documentation in `docs/STATUS.md`, `docs/ARCHITECTURE.md`, and `config/env.example` should stay aligned with this decision as workflows are updated.

---

## Related code and configuration

| Path | Role |
|------|------|
| `.github/workflows/test.yml` | Main CI: tests and report artifacts; should align with B+D once refactored. |
| `ai_audit/failure_analyzer.py` | CLI entrypoint; `--client`, `--artifacts-dir`, `--out`. |
| `ai_audit/gemini_client.py` | Gemini HTTP client; reads `GEMINI_API_KEY`. |
| `ai_audit/ollama_client.py` | Local Ollama client. |
| `config/env.example` | Documents optional `GEMINI_API_KEY` for local or CI secret setup. |

---

## Revision history

- Document created to record selection of **B + D** and the option space **A–D** for CI cloud failure analysis.
