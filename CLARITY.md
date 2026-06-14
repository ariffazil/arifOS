# CLARITY — Naming, Repositories, and Canonical Surfaces

> **One source of truth for the arifOS naming situation.**
> Updated: 2026-06-14

---

## The Short Version

There is **one repository** and **one package**. Capitalization varies by surface — this document explains why and which surface to trust.

| Surface | Name | Canonical? | Notes |
|---------|------|------------|-------|
| GitHub repository | `ariffazil/arifos` | **YES** | GitHub is case-insensitive; `ariffazil/arifOS` redirects here |
| Local directory | `/root/arifOS` | **YES** | Historical capitalization; git remote points to `ariffazil/arifos` |
| PyPI package | `arifos` | **YES** | Published from the same repo |
| Python import | `arifosmcp` | **YES** | Package name inside the repo |
| Documentation | `arifOS` | Common | Capitalization used in prose and badges |

**Rule:** When in doubt, trust `ariffazil/arifos` (lowercase) on GitHub. Everything else is the same codebase with different capitalization conventions.

---

## Why the Confusion Exists

1. **GitHub case-insensitivity.** `github.com/ariffazil/arifOS` and `github.com/ariffazil/arifos` resolve to the same repository. External researchers sometimes discover both URLs and assume they are different repos.

2. **PyPI package name.** The pip-installable package is `arifos` (lowercase), versioned independently from git tags. This is normal Python packaging practice, but it adds a second name to the ecosystem.

3. **Python import path.** The code lives under `arifosmcp/` inside the repo. This is a third name (`arifos` + `mcp`).

4. **Prose capitalization.** In documentation, READMEs, and articles, `arifOS` (with capital OS) is used for readability. This is stylistic, not a separate product.

---

## Version Matrix

| Surface | Current Version | Source |
|---------|----------------|--------|
| Git repo HEAD | `main` @ `0f887477c` | `git rev-parse --short=7 HEAD` |
| PyPI package | `2026.5.26` | `pip show arifos` |
| Constitutional version | `v2026.05.05-SSCT` (F1–F13 active) + `v2026.06.13-SELH-F14DEAD` (F0 PRIME, F14 DEAD, F15-F17 draft) | `arifosmcp/CONSTITUTIONAL_EXTENSION_*.py` |
| Build tag | `v2026.05.05-SSCT` (live: `kanon-0f88747`) | `curl :8088/health` |

The PyPI version lags the git HEAD because releases are cut manually. The constitutional version is the slowest-moving — it only changes when F1–F13 floors are ratified or amended.

---

## What This Is NOT

- **NOT two competing products.** There is no fork, no rival implementation, no commercial vs. open-source split.
- **NOT a renaming in progress.** Both capitalizations will continue to coexist. This is documented, not deprecated.
- **NOT a source of truth conflict.** The GitHub repo `ariffazil/arifos` is canonical. All other names are aliases.

---

## For External Researchers

If you are reading this because you found conflicting names in documentation, reports, or package indexes:

1. Start with this file (`CLARITY.md`) in the repo root.
2. The canonical implementation is in `arifosmcp/core/shared/floors.py`.
3. The canonical tool registry is in `APEX/ASF1/tool_registry.json`.
4. The canonical database schema is in `arifosmcp/schemas/`.
5. The live health endpoint is `https://arifos.arif-fazil.com/health`.

---

## Federation Organs (Same Repo? No.)

Each organ below is a **separate git repository** with its own build lifecycle:

| Organ | Repository | Port | Language |
|-------|------------|------|----------|
| arifOS | `ariffazil/arifos` | 8088 | Python |
| A-FORGE | `ariffazil/A-FORGE` | 7071 | TypeScript |
| GEOX | `ariffazil/geox` | 8081 | Python |
| WEALTH | `ariffazil/wealth` | 18082 | Python |
| WELL | `ariffazil/well` | 18083 | Python |
| AAA | `ariffazil/AAA` | 3001 | TypeScript |
| APEX | `ariffazil/APEX` | 3002 | Node.js |

These are independent repos. They are not submodules, not a monorepo, and not governed by the same `package.json` or `pyproject.toml`. The confusion about "two arifOS repos" is unrelated to the multi-organ architecture.

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
