# arifOS Positioning

Four declarations. No ambiguity.

---

## 1. What is the Standard

**The arifOS Standard** is a constitutional governance specification for bounded AI.

It defines how any AI system MUST behave under human sovereignty: how authority flows, how uncertainty is bounded, how actions are verified before execution, and how the system fails safely.

It is language-agnostic. It is implementation-agnostic. It is a set of rules — like RFC 2119 for AI behavior.

**Location:** https://github.com/ariffazil/arifOS → `STANDARD.v1.md`
**Machine-readable:** `arifos.standard.v1.json`
**Status:** Public Draft v1.0.0

---

## 2. What is the Schema

**The arifOS Schema** is the machine-readable encoding of the standard.

`arifos.standard.v1.json` defines:
- The 13 Constitutional Floors (F1–F13) as structured objects
- Required behaviors per floor
- The metabolic pipeline stages (000–999)
- Verdict types: SEAL, HOLD, VOID, SABAR
- The APEX formula: G = (A × P × X × E²) × |ΔS| / C ≥ 0.80

It is designed to be importable by any governance layer — embedded in code, used as a validation reference, or cited in documentation.

**Location:** https://github.com/ariffazil/arifOS → `arifos.standard.v1.json`

---

## 3. What is the Reference Implementation

**arifosmcp** is the production reference implementation of the arifOS Standard.

It is a FastMCP-compatible server with:
- 11 mega-tools covering governance, intelligence, and machine layers
- All 13 constitutional floors enforced at runtime
- Immutable VAULT999 audit ledger
- Prometheus metrics + Grafana observability
- Full infrastructure stack (Redis, Qdrant, Postgres, Ollama)

It proves the standard is not theoretical. It is running in production.

**Repository:** https://github.com/ariffazil/arifosmcp
**Live MCP endpoint:** https://arifosmcp.arif-fazil.com/mcp
**MCP Registry:** `io.github.ariffazil/arifosmcp`
**Health:** https://arifosmcp.arif-fazil.com/health

---

## 4. How Each is Licensed

| Layer | License | Intent |
|-------|---------|--------|
| Standard spec (`STANDARD.v1.md`) | CC0 1.0 | Public domain — implement freely |
| Schema (`arifos.standard.v1.json`) | CC0 1.0 | Public domain — embed freely |
| Theory & doctrine (arifOS repo) | CC0 1.0 | Public domain — cite freely |
| Reference implementation (arifosmcp) | AGPL-3.0 | Open, with network copyleft |

**Rule of thumb:**
- The *idea* (standard) is free for everyone.
- The *machine* (runtime) is open-source, copyleft.

See [LICENSING.md](./LICENSING.md) for the full model.

---

*arifOS — Forged, Not Given.*
*Author: Arif Fazil | https://arifos.arif-fazil.com*
