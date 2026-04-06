# GitHub Actions: Managing custom actions (reference)

**Source:** [Managing custom actions](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/manage-custom-actions) (GitHub Docs)

**Purpose:** Where to put action code, how to version consumer `uses:` references, portability (GHES / GHEC), and README expectations — useful if this repo later publishes a **composite** or **Docker/JavaScript** action.

---

## Where to put an action

- **Publishable / community-facing:** Prefer a **dedicated repository** so you can version, track issues, and release independently of app code.
- **Private / internal:** Can live anywhere in a repo; GitHub recommends **`.github/actions/<name>`** when mixing app, workflow, and action code in one repository.

## Compatibility (not only github.com)

- Do **not** hard-code `https://api.github.com`.
- Use **`GITHUB_API_URL`** (REST) and **`GITHUB_GRAPHQL_URL`** (GraphQL), or **`@actions/github`** from the [Actions toolkit](https://github.com/actions/toolkit/tree/main/packages/github), so the action works on GitHub Enterprise and alternate hosts.

## Release management for `uses:`

- Consumers should **pin a major version** (e.g. `@v1`), not the default branch (may be unstable).
- **Tags** (semantic versioning, moving major tag `v1`): e.g. `uses: org/action@v1` or `@v1.0.1`.
- **Branches:** e.g. `uses: org/action@v1-beta`.
- **Full commit SHA:** immutable; no automatic updates if the action changes.

If the org uses **immutable releases**, follow [Using immutable releases and tags](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/using-immutable-releases-and-tags-to-manage-your-actions-releases).

## README for an action

Document: what it does; required/optional **inputs** and **outputs**; **secrets** and **environment variables**; a minimal **workflow example**.

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
