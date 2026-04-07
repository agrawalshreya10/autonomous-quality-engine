# GitHub Actions: Triggering a workflow (reference)

**Source:** [Triggering a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow) (GitHub Docs)

**Purpose:** Quick context for `on:` events, filters, chained workflows (e.g. `workflow_run`), and token behavior — aligns with this repo’s **AI Failure Analysis** workflow that runs after **Test Suite** completes.

---

## `GITHUB_TOKEN` and workflows that trigger other workflows

- Actions performed with the repo’s **`GITHUB_TOKEN`** do **not** dispatch new workflow runs for events that would normally fire — **except** `workflow_dispatch` and `repository_dispatch`. This avoids accidental **recursive** runs (e.g. push from a workflow does not re-trigger `on: push`).
- To **intentionally** trigger another workflow from a run (e.g. label added → downstream workflow), use a **GitHub App installation token** or a **personal access token** stored as a secret — not `GITHUB_TOKEN` for those cases.
- Avoid unintended or runaway workflow chains to control Actions usage/cost.

See also: [Automatic token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication).

## Defining what runs: `on:`

- **Single event:** `on: push`
- **Multiple events:** `on: [push, fork]` — any one event starts a run; simultaneous events can start **multiple** runs.
- **Activity types:** e.g. `on.label.types: [created]` — narrow when the event fires.
- **Filters:** `branches`, `branches-ignore`, `tags`, `tags-ignore`, `paths`, `paths-ignore` — glob patterns; order matters when using `!` exclusions inside `branches` / `paths` (see official doc).

Full list: [Events that trigger workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows).

## `workflow_run` (relevant to chained CI)

- Restrict which **branch** the *triggering* workflow ran on using `branches` / `branches-ignore` under `workflow_run` (same inclusion/exclusion rules as other events — not both `branches` and `branches-ignore` on the same event).
- Example pattern: run after workflow **Build** on `releases/**` but exclude `!releases/**-alpha`.

This repo’s [ai-failure-analysis.yml](../../.github/workflows/ai-failure-analysis.yml) uses `workflow_run` with `workflows: ["Test Suite"]` and `types: [completed]`.

## Cross-run artifact download (`download-artifact@v4` + `run-id`)

[`actions/download-artifact@v4`](https://github.com/actions/download-artifact) can download artifacts from **another** workflow run when you pass `run-id` (and optionally `repository`). For that case the action README requires a token that is **not** limited to the current run’s artifact scope — typically a **personal access token** (PAT) stored as a repository secret with **`actions: read`** (fine-grained PAT on the repo) or appropriate **classic** scopes (e.g. private repos often need `repo`). **`GITHUB_TOKEN` alone is not sufficient** when `run-id` refers to a different run (e.g. the failed **Test Suite** run from a follow-up **AI Failure Analysis** workflow). This repo uses secret **`ACTIONS_ARTIFACT_READ_TOKEN`** for that step.

## Path filters and diffs

- For `push` / `pull_request`, combining **branch** and **path** filters requires **both** to match.
- Path filters use two-dot vs three-dot diffs for pushes vs PRs; very large pushes (>1000 commits) or diff limits (e.g. 300 files) can affect whether the workflow runs — see official doc for edge cases.

## `workflow_dispatch`

- Optional **inputs** for manual runs; workflow file must be on the **default branch** for the trigger to apply.
- Inputs surface in `inputs` / `github.event.inputs` (boolean handling differs slightly — see doc).

## Reusable workflows

- Callers pass **inputs** and **secrets**; callee can expose **outputs**. See [Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows).

## Event data and conditionals

- Use **`github.event`** (and `toJSON(github.event)` for debugging) — shape depends on event type.
- **`if:`** on jobs/steps for finer control (e.g. only when a specific label name is set).

## Further reading (official)

- [Webhook events and payloads](https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads)
- [Contexts reference](https://docs.github.com/en/actions/learn-github-actions/contexts)
- [Expressions](https://docs.github.com/en/actions/learn-github-actions/expressions)

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
