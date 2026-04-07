# GitHub Actions: Building and testing Python (reference)

**Source:** [Building and testing Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) (GitHub Docs)

**Purpose:** Align CI with GitHub’s recommended patterns for **`actions/setup-python`**, matrices, caching, pytest, and artifacts — matches how this repo’s [test.yml](../../.github/workflows/test.yml) installs Python and dependencies.

---

## Hosted runners and Python

- GitHub-hosted runners include Python/PyPy in the **tools cache**; see [Supported software](https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#supported-software).
- Prefer **`actions/setup-python`** so the interpreter is explicit and consistent across Ubuntu/macOS/Windows.

## `setup-python` basics

- **`python-version`:** exact (e.g. `3.12`), range (e.g. `3.x`), or matrix value.
- **`cache: pip`** (optional): speeds installs; discovers `requirements.txt` / lockfiles per [setup-python caching](https://github.com/actions/setup-python#caching-packages-dependencies).
- Missing versions fail with a clear error listing available versions.
- **Matrix `exclude`:** skip unwanted OS × Python combinations.

## Multiple Python versions

Use a **strategy matrix** (`python-version` list) and `${{ matrix.python-version }}` in the setup step — same pattern as the official doc’s PyPy + CPython examples.

## Installing dependencies

- Typical flow: upgrade **pip**, then `pip install -r requirements.txt` (this project uses [requirements.txt](../../requirements.txt)).
- Optional: [`actions/cache`](https://github.com/actions/cache) for custom pip paths if needed ([Python caching examples](https://github.com/actions/cache/blob/main/examples.md#python---pip)).

## Testing

- Run the same commands as locally (e.g. **pytest**). Official examples also show **pytest-cov**, **JUnit XML**, **Ruff**, **tox**.
- Upload reports/screenshots with **`actions/upload-artifact`**; use **`if: always()`** when you want artifacts even when tests fail.

## Publishing to PyPI (optional)

- Release-triggered workflows can build wheels/sdists and publish (e.g. **Trusted Publishing** / OIDC). See the full guide and [Configuring OpenID Connect in PyPI](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-pypi).

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
