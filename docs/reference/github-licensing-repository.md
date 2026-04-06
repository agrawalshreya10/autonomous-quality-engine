# Licensing a repository (reference)

**Source:** [Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository) (GitHub Docs)

**Purpose:** Why a **LICENSE** file matters for open source, where to put it, and how GitHub surfaces license metadata — not legal advice; see a lawyer for specific situations.

---

## Choosing a license

- [choosealicense.com](https://choosealicense.com) helps compare common licenses.
- **No license:** default copyright applies — others generally may not reuse, redistribute, or create derivatives without permission. For intentional open source, add an explicit license.
- [Open Source Guide — legal](https://opensource.guide/legal/#which-open-source-license-is-appropriate-for-my-project) has additional context.

**Public repos:** Per [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service), other users may **view and fork** public repositories; licensing still governs what they can do with the code beyond that.

## Where to put the license text

- Common: **`LICENSE`**, **`LICENSE.txt`**, **`LICENSE.md`**, or **`LICENSE.rst`** in the **repository root**.
- README may also state the license in prose; **including the full license file** is still recommended.

## Searching by license on GitHub

Use the `license:` search qualifier with keywords such as `MIT`, `Apache-2.0`, `GPL-3.0`, etc. Family queries like `license:gpl` can match multiple GPL variants. See [Searching for repositories](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories#search-by-license).

## Detection (Licensee)

[Licensee](https://github.com/licensee/licensee) compares the LICENSE file to known licenses; powers GitHub’s license display and related APIs. If detection fails, simplify the LICENSE file or document complexity in the README.

## Disclaimer

GitHub’s licensing docs are informational, not legal advice. For questions about a specific license or situation, consult a qualified professional.

---

*This file is a project-local summary; defer to GitHub’s documentation for authoritative, up-to-date behavior.*
