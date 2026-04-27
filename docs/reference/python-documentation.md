# Python 3 documentation (reference)

**Source:** [Python 3 documentation](https://docs.python.org/3/) (python.org — version-specific builds, e.g. 3.12.x, 3.14.x)

**Purpose:** Map the official doc **landing page** to common tasks. This repo targets **Python 3.12+** (see `playwright-core-sync.mdc` in `.cursor/rules/`); pick the matching minor doc version from the site’s version switcher when behavior differs between releases.

---

## Main sections (from the docs home page)

| Section | Typical use |
|--------|----------------|
| **What's new in Python 3.x** | Upgrade notes and breaking changes when bumping the interpreter. |
| **Tutorial** | Language tour for readers new to Python or refreshing syntax. |
| **Library reference** | Standard library and builtins — day-to-day APIs (`pathlib`, `typing`, `asyncio`, etc.). |
| **Language reference** | Formal syntax and semantics (grammar, execution model). |
| **Python setup and usage** | Installing and invoking the interpreter, environment options. |
| **HOWTOs** | Deeper topics (e.g. descriptors, sorting, Unicode). |
| **Installing Python modules** | `pip`, virtual environments, third-party packages (PyPI). |
| **Distributing Python modules** | Packaging and publishing libraries. |
| **Extending and embedding** / **Python’s C API** | C/C++ integration. |
| **FAQs** | Common questions. |
| **Deprecations** | Features scheduled for removal or already removed. |

## Indices and search

- **Global module index** — all modules in the stdlib docs.
- **General index** — functions, classes, terms.
- **Glossary** — terminology.
- **Search** — full-text search within the selected doc version.

## Other resources (linked from the docs site)

- [PEP Index](https://peps.python.org/) — language and process proposals.
- [Beginner’s Guide](https://wiki.python.org/moin/BeginnersGuide), book lists, talks.
- [Python Developer’s Guide](https://devguide.python.org/) — contributing to CPython and documentation.

## Project alignment

- Prefer the **Library reference** and **Language reference** when verifying stdlib behavior, typing, and syntax for automation code in `pages/`, `tests/`, `core/`, and `ai_audit/`.

---

*This file is a project-local index; defer to [docs.python.org](https://docs.python.org/3/) for authoritative, version-specific behavior.*
