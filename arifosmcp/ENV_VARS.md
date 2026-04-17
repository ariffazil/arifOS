# arifOS MCP — Environment Variables

**Epoch:** 2026-04-17
**Status:** SEALED — Day 3

---

## Axis Feature Flags

Control which tool axes are mounted in the live server. All default to enabled.
Set to `false` to gate an axis during staged rollout or incident response.

| Variable | Default | Axis | Risk |
|---|---|---|---|
| `ARIFOS_ENABLE_P_AXIS` | `true` | Perception (read-only sense) | low |
| `ARIFOS_ENABLE_T_AXIS` | `true` | Transformation (compute) | low |
| `ARIFOS_ENABLE_V_AXIS` | `true` | Valuation (economic compute) | low |
| `ARIFOS_ENABLE_G_AXIS` | `true` | Governance (judge/verdict) | high |
| `ARIFOS_ENABLE_E_AXIS` | `true` | Execution (forge/vault) | high |
| `ARIFOS_ENABLE_M_AXIS` | `true` | Meta (metacognition) | low |

Usage in `server.py`:

```python
import os
_axis_enabled = lambda axis: os.getenv(f"ARIFOS_ENABLE_{axis}_AXIS", "true").lower() != "false"
```

---

## Execution Gates

| Variable | Default | Effect |
|---|---|---|
| `ARIFOS_ENABLE_APPROVAL_PROVIDER` | `false` | Mount FastMCP F13 approval UI for 888_HOLD gates |
| `ENABLE_DANGEROUS_TOOLS` | `false` | Unlock destructive-risk tools (inherited from A-FORGE) |
| `ARIFOS_PUBLIC_BOOTSTRAP` | `true` | Strict public mode — legacy aliases and debug tools opt-in only |

---

## Constitutional Thresholds

| Variable | Default | Meaning |
|---|---|---|
| `ARIFOS_OMEGA_MIN` | `0.95` | Minimum Ω_ortho for gateway to pass |
| `ARIFOS_PEACE2_FLOOR` | `0.70` | Minimum Peace² for economic operations |
| `ARIFOS_W3_MIN` | `0.95` | Minimum W³ witness score for SEAL |
| `ARIFOS_KAPPA_H_LOW` | `0.03` | kappa-H band floor (epistemic calibration) |
| `ARIFOS_KAPPA_H_HIGH` | `0.15` | kappa-H band ceiling |

---

## Infrastructure

| Variable | Required | Purpose |
|---|---|---|
| `DATABASE_URL` | Yes (VPS) | PostgreSQL for VAULT999 Merkle ledger |
| `REDIS_URL` | No | Cache / pub-sub for session continuity |
| `QDRANT_URL` | No | Vector memory (arifos_memory tool) |
| `ANTHROPIC_API_KEY` | Yes | LLM backend for mind/heart tools |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
