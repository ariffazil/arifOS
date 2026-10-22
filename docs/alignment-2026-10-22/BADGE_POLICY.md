# Federation Badge Policy (BADGE_POLICY)

**Authority:** ARIF (Human Sovereign)  
**Generated UTC:** 2026-10-22T14:24:01Z  
**Principle:** Badges are Telemetry, Not Medals  

---

## 1. Permitted Badges (Objective Telemetry)

The following badge types are permitted across federation repositories:
1. **Distribution & Packaging:**
   - PyPI package version (`img.shields.io/pypi/v/...`)
   - Supported Python/Rust editions
2. **Repository Health & Build:**
   - GitHub Actions CI status (`img.shields.io/github/actions/workflow/status/...`)
   - Permitted only if linking to a real passing workflow.
3. **Legal & Licensing:**
   - SPDX license badge (`img.shields.io/badge/license-AGPL--3.0-blue`)
4. **Third-Party Catalog Verification:**
   - Glama connector status / score badge
   - Curated directory listing badge (e.g. `Awesome AI Agent Governance` linking directly to `agentrust-io/awesome-ai-governance`)
5. **Measured Machine State:**
   - Real-time endpoint badges (e.g. `img.shields.io/endpoint?url=.../.well-known/badges/...`) that dynamically reflect live `/health`.

---

## 2. Strictly Forbidden Badges (Marketing & False Authority)

The following badges are **PROHIBITED**:
- ❌ Badges claiming unverified superiority ("100% Safe", "Best Governance").
- ❌ Badges claiming official endorsements from platforms where arifOS is only self-listed.
- ❌ Badges claiming commercial adoption or enterprise certification without an external audit report.
- ❌ Static green badges that mask failing runtime floors.
