# Federation Architecture — Sovereign Intelligence Civilization Stack
<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-29
valid_from: 2026-06-29
valid_until: 2026-07-29
heptalogy: live-table-mapping
epistemic_status: LIVE_INTELLIGENCE
-->

This document serves as the canonical source of truth mapping all repositories, sites, ports, endpoints, and roles within the arifOS Federation.

## 1. Unified Domain & Repository Mapping

| Layer | Repo / Source | Site / Domain | Port / Endpoint | Core Role & Consequence Class |
| :--- | :--- | :--- | :--- | :--- |
| **Human Sovereign Root** | `ariffazil/ariffazil` | [arif-fazil.com](https://arif-fazil.com) | — | **Identity & Trust Surface:** Authorship, legitimacy, F13 absolute human veto. |
| **Constitutional Kernel** | `ariffazil/arifOS` | [arifos.arif-fazil.com](https://arifos.arif-fazil.com) | `:8088` | **AGI Substrate Layer:** 13 constitutional floors (F1–F13), canonical tools, VAULT999 ledger. |
| **State Foundation** | `ariffazil/AAA` | [aaa.arif-fazil.com](https://aaa.arif-fazil.com) | `:3001` `/cockpit` | **ASI Civilization Layer:** Adjudication logic, control plane, A2A gateways, skepticism charter. |
| **Autonomous Substrate** | `ariffazil/A-FORGE` | — | `:7071` `/7072` (MCP) | **Agentic Labor Layer:** Metabolic shell, build & deploy orchestration, execution under seal boundaries. |
| **Earth Organ** | `ariffazil/geox` | [geox.arif-fazil.com](https://geox.arif-fazil.com) | `:8081` | **Physical Consequence:** Basin analysis, seismic interpretation, petrophysics. Physics-9 grounded. |
| **Capital Organ** | `ariffazil/wealth` | [wealth.arif-fazil.com](https://wealth.arif-fazil.com) | `:18082` | **Capital Consequence:** Economic NPV/EMV valuation, risk scoring, credit relations, crisis triage. |
| **Human Substrate Organ** | `ariffazil/well` | [well.arif-fazil.com](https://well.arif-fazil.com) | `:18083` | **Vitality Consequence:** Operator cognitive pressure, sleep, fatigue, thermodynamic conditions. |
| **Protocol Gateway** | — | [mcp.arif-fazil.com](https://mcp.arif-fazil.com) | `/mcp` (POST) | **Canonical Machine Door:** Unified JSON-RPC 2.0 gateway for all agent connection interfaces. |

## 2. Structural Relationships & The Triad

```
                         ┌─────────────────────────┐
                         │   ariffazil (Human)     │
                         │   F13 SOVEREIGN VETO    │
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │      arifOS (Kernel)    │
                         │    AGI Substrate Layer  │
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │       AAA (State)       │
                         │   ASI Civilization Layer│
                         └────────────┬────────────┘
                                      │
                         ┌────────────▼────────────┐
                         │    A-FORGE (Substrate)  │
                         │    Agentic Labor Layer  │
                         └──────┬──────┬──────┬────┘
                                │      │      │
          ┌─────────────────────┘      │      └─────────────────────┐
          │                            │                            │
┌─────────▼────────┐         ┌─────────▼────────┐         ┌─────────▼────────┐
│   GEOX (Earth)   │         │ WEALTH (Capital) │         │   WELL (Vitality)│
│ Physics Witness  │         │ Economic Witness │         │ Human Witness    │
└──────────────────┘         └──────────────────┘         └──────────────────┘
```

1. **arifOS asks:** *What laws must intelligence obey?* (Kernel/Law)
2. **AAA asks:** *Who governs intelligence and who can veto it?* (State/Adjudication)
3. **A-FORGE asks:** *How does intelligence work in the field without breaking laws?* (Execution/Labor)
