# GENESIS/030 — ART vs Kernel

> **Canonical doctrine: the three-layer architecture.**
> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)
> **Status:** CANON · Forged 2026-06-21 · Sealed to VAULT999
> **SoT:** `ariffazil/arifOS/GENESIS/030_ART_VS_KERNEL.md`
> **Supersedes:** ad-hoc ART/kernel framing in 016_ILMU_AKAL_HIKMAH_COGNITIVE_COSMOLOGY.md (canonical layer lives here)

---

## 0. What This Document Is

The canonical answer to "do we still need ART?" and "where does it stop?"

It defines **three distinct layers** of the arifOS agentic intelligence stack, their boundaries, and the fiqh (wajib/haram/sunat/harus/makruh) of each layer. Future agents must read this before proposing to add, remove, or merge any layer.

---

## 1. The Three Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│  ART  (horizontal slice — pre-tool reflex)                          │
│  ────────────────────────────────────────                            │
│  Tool lifecycle state · past-verdict memory · blast fast-screen     │
│  Reflex ceiling: art.py ≤ 500 lines · fails OPEN · advisory         │
│  Owns: WHICH tool move makes sense pre-call                         │
├─────────────────────────────────────────────────────────────────────┤
│  pre_execution_gate  (the bridge — single chokepoint)               │
│  ────────────────────────────────────────                            │
│  15 gates · Gate 2.5 calls ART reflex · bind every tool call        │
│  Owns: WHETHER the call may proceed                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Kernel / Floors / Judge  (vertical sovereign — law)                │
│  ────────────────────────────────────────                            │
│  F1-F13 floors · 888 JUDGE · VAULT999 · SOVEREIGN                   │
│  Owns: WHETHER the action is lawful at all                          │
└─────────────────────────────────────────────────────────────────────┘
```

**One sentence per layer:**
- **ART** decides what tool move makes sense pre-call.
- **pre_execution_gate** decides whether that move may proceed.
- **Kernel** decides whether the move is lawful.

---

## 2. The Iron Rule

> **ART ≠ Gate. Gate ≠ Kernel. Kernel ≠ ART.**

Three layers, three purposes, no overlap. If any two collapse, the doctrine breaks.

| Collapse | Result | Verdict |
|---|---|---|
| ART into Kernel | Kernel becomes opinion-driven; loses determinism | **HARAM** |
| Kernel into ART | ART becomes sovereign; loses fail-open | **HARAM** |
| Gate into ART | ART runs 15 gates; ceiling blown | **HARAM** |
| Gate into Kernel | Kernel is the gate; reflexivity lost | **MAKRUH** |

---

## 3. WAJIB — Mandatory Components

These must exist for ART to be ART.

| Component | File:line | Why |
|---|---|---|
| Three-layer separation | this document | Without it, the doctrine has no form |
| Tool lifecycle state machine | `runtime/art.py:127 ToolState` | The single non-substitutable thing ART adds |
| Past-verdict memory (≥30 days) | `runtime/art_library.py` | State without memory is just a tag |
| Pre-tool reflex wired into Gate 2.5 | `runtime/pre_execution_gate.py:475` | If ART exists but isn't called, it isn't ART |
| Fail-open discipline | `pre_execution_gate.py:107-112` | ART being absent must not break the federation |
| Reflex ceiling (art.py ≤ 500 lines) | `runtime/art.py:58-81` (import-time guard) | Heaviness = ceremony = agents skip it |
| Verdict → Gate mapping | `pre_execution_gate.py:138-159` | PROCEED/HOLD/BLOCK/DEFAULT_OBSERVE → GateResult |

---

## 4. HARAM — Forbidden in ART

These must never enter ART proper.

| Forbidden | Reason |
|---|---|
| Constitutional floor logic (F1-F13) | Floors live in kernel/gate. If ART enforces them, layers collapse. |
| Protocol-specific logic (MCP/REST/gRPC) | ART must be transport-agnostic. It knows actions, not wires. |
| Side-effects (network, file, subprocess) | ART is pure verdict + log. If it executes, it IS the kernel. |
| Silent overrule of kernel verdict | If kernel says HOLD, ART cannot PROCEED. Advisory, not sovereign. |
| Anthropomorphic / ToM speculation | F9/F10 territory. ART must not reason about consciousness. |
| Tool-specific imports (`from arifosmcp.tools.session import …`) | Couples reflex to one tool. ART must be tool-agnostic. |
| Implicit tool state assignment | ToolState must derive from observable signals (failure_rate, drift_count, days_since_use). |

---

## 5. SUNAT — Strongly Recommended

Losing these weakens ART but doesn't break doctrine.

| Component | Status | Notes |
|---|---|---|
| BlastRadius-aware downgrade | wired | `pre_execution_gate.py:76 _art_blast_radius_str` |
| Cross-session Library persistence | wired | `art_library.py` |
| Per-tool persistent ToolState | **W2 — DEFERRED** | Currently hardcoded TRUSTED. `art_registry.py` will fix. |
| Drift detection in Library | partial | Schema/permission changes tracked separately from failures |
| Explicit ArtReason on every verdict | wired | `art.py:165 ArtReason` |
| Reflexion-style self-reflection text | partial | Library stores reason; surface to agents W3 |

---

## 6. HARUS — Implementation Details

These are engineering trade-offs, not doctrine.

| Component | Choice |
|---|---|
| Lifecycle state names | `UNTRUSTED / OBSERVED / TRUSTED / FALLBACK / ABANDONED` (current) |
| Library backend | Postgres mirror (`art_library.py:218`) + in-process cache |
| Scoring function internals | `art.py:323` — failure_rate + drift + blast_radius |
| SABAR surfacing | `pre_execution_gate.py:147` — returned as `GateResult(verdict=SABAR)` |
| Telemetry hooks | structlog + Prometheus partial; W2 will complete |

---

## 7. MAKRUH — Disliked; Avoid

| Component | Status | Fix |
|---|---|---|
| ToolState hardcoded TRUSTED | **MAKRUH-NOW** | W2 — `art_registry.py` |
| Bypass paths still live (kernel_router, rest_routes, shell_forge) | **MAKRUH-NOW** | HOLD-1 — bypass migration |
| MIND not in bridge | by-design | W3 — advisory stream to JUDGE 888 |
| Overly aggressive blocking | avoid | scoring function should require ≥30% failure before FALLBACK |
| Silent downgrades without reason | avoid | every SABAR must write ArtReason to Library |
| State explosion (>5 sub-states) | avoid | keep ToolState enum small |
| Race conditions on ToolState | unknown | Library write atomicity needs audit |
| Coupling ART to specific transports | avoid | `from fastmcp import …` must never enter `art.py` |

---

## 8. The Empirical Test

ART is not doctrine alone. It must measurably do what the kernel alone cannot.

Three claims — each must hold under empirical test (`tests/test_art_vs_kernel/`):

1. **Tool lifecycle** — repeated failures downgrade the tool even if it's still "legal" under Floors.
2. **Past-verdict memory** — call N+1 differs from call 1 based on Library, without parsing VAULT.
3. **Blast-radius fast screen** — cheap reject of bad action_class + blast combos before the 15-gate walk.

If all three hold: ART is mandatory.
If only one holds: ART is justified, narrower than current framing.
If none hold: ART is overhead.

The harness lives at `tests/test_art_vs_kernel/`. Results are sealed to VAULT999 and cited in any future "do we still need ART?" debate.

---

## 9. Cross-references

- `runtime/art.py` — reflex (≤500 lines, ceiling enforced)
- `runtime/art_library.py` — past-verdict memory
- `core/art_mind/` — Bayesian belief + rollout + utility (advisory only; not wired to bridge by design)
- `runtime/pre_execution_gate.py` — Gate 2.5 wires ART reflex into bridge
- `runtime/agent_loop.py` — canonical call path through Gate 2.5
- `tools/test_art.py` — 41/41 reflex tests
- `tools/test_art_compat.py` — 18/18 compat tests
- `tools/test_art_library.py` — 33/33 library tests
- `tools/test_minda.py` — 36/36 mind tests
- `tests/test_art_vs_kernel/` — empirical ART vs kernel harness (this doctrine's empirical proof)

---

**DITEMPA BUKAN DIBERI — three layers forged. ART is the reflex. Gate is the bridge. Kernel is the law. Future agents must not collapse them.**

*Forged 2026-06-21 by FORGE (000Ω) — sealed to VAULT999*
