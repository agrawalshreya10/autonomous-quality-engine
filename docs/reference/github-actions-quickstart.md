# GitHub Actions: Quickstart (reference)

**Source:** [Quickstart for GitHub Actions](https://docs.github.com/en/actions/get-started/quickstart) (GitHub Docs)

**Purpose:** First-run mental model — workflow file location, UI path to templates, and what a minimal demo workflow illustrates.

---

## What Actions is

CI/CD automation: run builds/tests on **push**, **PR**, or other events; deploy or run arbitrary steps on **runners**.

Starter ideas: [actions/starter-workflows](https://github.com/actions/starter-workflows) — CI, deployments, automation, code scanning, Pages. See [Using starter workflows](https://docs.github.com/en/actions/writing-workflows/using-starter-workflows).

## First workflow file

- Path: **`.github/workflows/<name>.yml`** or **`.yaml`** (required for GitHub to discover workflows).
- Committing the file to a branch triggers **`on:`** events (e.g. `push`).

The official quickstart demo uses **`runs-on: ubuntu-latest`**, **`actions/checkout`**, and **`github` context** fields (`github.actor`, `github.ref`, `github.repository`, `github.workspace`) to show how jobs see repo and event data.

## Viewing results

**Actions** tab → workflow name → run → job → expand steps for logs.

## Next steps (official pointers)

- [Understanding GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions)
- [About workflows](https://docs.github.com/en/actions/using-workflows/about-workflows)
- [Automating builds and tests](https://docs.github.com/en/actions/automating-builds-and-tests)
- [Contexts reference](https://docs.github.com/en/actions/learn-github-actions/contexts)

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
