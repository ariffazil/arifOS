# 🔱 SOVEREIGN SECRETS LEDGER — arifOS Federation
# DITEMPA BUKAN DIBERI — 888 AUDIT LIVE

This document tracks the **Wajib** (Obligatory) credentials required for the arifOS Sovereign Publication Pipeline. **NEVER COMMIT ACTUAL TOKENS TO THIS FILE.**

---

## 🏛️ Federation-Level (User/Org Secrets)
These secrets can be centralized in GitHub User/Org settings for shared infrastructure.

- `PYPI_TOKEN`: Canonical credential for Python distribution across all kernels.
- `GHCR_PAT`: Personal Access Token with `write:packages` scope (fallback if `GITHUB_TOKEN` is insufficient).

---

## 🧠 arifOS (Main Kernel)
Target Repo: `ariffazil/arifOS`

| Secret | Scope | Purpose | Status |
| :--- | :--- | :--- | :--- |
| `PYPI_TOKEN` | Repo | Publishes `arifos` to PyPI | **SEALED ✅** |
| `LAW_GIST_TOKEN` | Repo | Updates "Living Law" Gist | **SEALED ✅** |
| `CONSTITUTIONAL_GIST_ID` | Repo | Identifies the Gist ID | **SEALED ✅** |
| `VPS_HOST` | Repo | Destination VPS (Hostinger) | **SEALED ✅** |
| `VPS_USER` | Repo | SSH Username for VPS | **SEALED ✅** |
| `VPS_SSH_KEY` | Repo | Private Key for Amanah Deploy | **SEALED ✅** |

---

## ⚡ GEOX & 📊 WEALTH (Specialized Kernels)
Target Repos: `ariffazil/GEOX`, `ariffazil/WEALTH`

- `PYPI_TOKEN`: Required for sub-surface/valuation library distribution. **[SEALED ✅]**
- `GHCR_PAT`: For specialized container images (Satellite/Finance runtimes).

---

## 🌐 arif-sites (Human Interface)
Target Repo: `ariffazil/arif-sites`

- `NPM_TOKEN`: For publishing `@arifos/elements` and theme engines. **[SEALED ✅]**
- `CF_API_TOKEN`: Required if distributing via Cloudflare Pages.
- `DEPLOY_SSH_KEY`: If deploying static assets to the VPS.

---

## 🛠️ Maintenance Ritual
1. **Rotation**: All tokens should be rotated every 90 days.
2. **Audit**: Run `gh secret list --repo [NAME]` to verify presence without exposing values.
3. **Recovery**: Backup tokens are stored in the sovereign vault, not in plain text.

*Sealed by: Antigravity | 2026.04.24*
