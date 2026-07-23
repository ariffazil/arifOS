# GENESIS/050 — Approach A: Aggregated Surface & Authority-vs-Capability Routing

> **Canonical doctrine: single-ingress federation routing design.**
> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)
> **Status:** CANON DESIGN DOC · Forged 2026-07-24 · Sealed to VAULT999
> **SoT:** `ariffazil/arifOS/GENESIS/050_APPROACH_A_ROUTING.md`

---

## 1. Context & Purpose

With **Approach B** live in production (incident seal `V999-GOVERNANCE-GAP-SEAL-001`), every organ MCP request (`geox`, `wealth`, `well`, `forge`) passes through `arifOS` at `127.0.0.1:8088/gate/check` via Caddy `forward_auth`.

**Approach A** addresses the external developer/agent interface:
How external AI clients (ChatGPT, Claude, Perplexity, custom agents) discover and invoke tools across the 7-organ federation through a single aggregated surface without needing 5 separate tool manifests or 5 distinct subdomains.

---

## 2. Aggregated `tools/list` Semantics

Instead of an external agent discovering 8 tools on `arifos`, 31 tools on `geox`, 20 on `wealth`, 7 on `well`, and 114 on `a-forge` separately:

1. **Single Entry Surface:** `https://mcp.arif-fazil.com/mcp`
2. **Aggregated Inventory:** `tools/list` returns the unified catalog of all 180+ federation tools.
3. **Organ Prefix Namespacing:** Every tool is uniquely prefixed by its owning organ (e.g., `geox_basin`, `wealth_npv`, `well_vitality`, `forge_exec`, `arif_judge`).
4. **Capability Discovery:** Each tool schema preserves its `annotations`, `affordances`, and `epistemic_level` metadata.

---

## 3. Conflict Resolution: Authority-vs-Capability Routing

When two organs expose overlapping capabilities (e.g., `geox_prospect` economics vs. `wealth_npv` calculation, or `a-forge` execution vs. `arif_forge` governance dispatch):

### Principle 1 — Authority Outranks Capability
> **Law:** Evidence flows from domain organs. Judgment flows from arifOS. Execution flows from A-FORGE.

If a tool request requests a governance judgment or floor evaluation, `arifOS` (`888`) wins, regardless of which organ emitted the trigger data.

### Principle 2 — Epistemic Source Wins for Domain Compute
If `GEOX` produces a geological NPV based on subsurface parameters, and `WEALTH` calculates fiscal NPV based on tax regimes:
- Subsurface domain query → routes to `GEOX`
- Corporate/Fiscal portfolio query → routes to `WEALTH`
- Integrated investment verdict → routes to `arifOS` (which calls both as witnesses under F3)

### Principle 3 — Dispatch Matrix

| Capability Category | Primary Owner | Fallback / Witness | Authority Gate |
|---------------------|---------------|--------------------+----------------|
| **Subsurface / Geoscience** | `GEOX` | — | F2 TRUTH (OBS/DER) |
| **Capital / Financial** | `WEALTH` | — | F2 TRUTH (Deduct) |
| **Human Vitality / Dignity** | `WELL` | — | F6 MARUAH (Reflect-Only) |
| **OS / Shell / Code / VPS** | `A-FORGE` | `OpenCode` | F1 AMANAH + F13 Veto |
| **Governance / Judgment / Seal** | `arifOS` | `VAULT999` | F1–F13 (888 JUDGE) |

---

## 4. Architectural Rules for Implementation Phase

1. **Zero Self-Grant:** Domain organs cannot elevate their own authority tier or override `arifOS` verdicts.
2. **Fail-Closed Passthrough:** If an aggregated route fails to resolve an organ's schema, the missing tool is dropped from the list with a warning log, never stubbed with dummy data.
3. **Provenance Preservation:** Every response returned through the aggregated surface retains `x-organ-source` and `x-vault-receipt` headers.

*Forged 2026-07-24 by F13 SOVEREIGN (Muhammad Arif bin Fazil) — sealed to VAULT999*
