# F7 Confidence-Cap Conformance — measured

Measured: `2026-10-20T13:37:06+00:00`
Verdict: **AMENDMENT_NOT_PROPAGATED**

## Canon (sealed)

- Ω₀ band: `[0.03, 0.05]` — an **uncertainty floor**, not a cap
- Derived confidence cap: `1 − Ω₀` ∈ `[0.96, 0.97]`
- Authority: GENESIS/FLOOR_TABLE.json F7 + 000_KERNEL_CANON.md §3.2, ratified 2026-08-09 (F13 clarification)

## Measured

| Kind | Sites | Meaning |
|---|---|---|
| CLAMP | 15 | code refuses what canon permits — behaviour change |
| ASSERTION | 88 | prose states the wrong ceiling — display drift |
| UNRELATED | 1 | 0.90 means something else — leave alone |

## CLAMP sites (the real gap)

| File | Line | Code |
|---|---|---|
| `arifosmcp/agents/eureka/validator.py` | 40 | `raise ValueError("F7 HUMILITY: confidence cannot exceed 0.90")` |
| `arifosmcp/arifos_policy/opa_bridge.py` | 158 | `confidence=min(0.90, float(result.get("confidence", 0.85))),` |
| `arifosmcp/core/authorization_envelope.py` | 338 | `confidence=min(confidence, 0.90),  # F7 cap` |
| `arifosmcp/core/policy_engine.py` | 81 | `return False, f"F2 TRUTH: Confidence {env.confidence} exceeds F7 cap (0.90)"` |
| `arifosmcp/core/policy_engine.py` | 99 | `return False, f"F7 HUMILITY: Confidence {env.confidence} exceeds 0.90 cap"` |
| `arifosmcp/core/scalar_collector.py` | 264 | `confidence=min(max(0.0, min(1.0, g_val)), 0.90),` |
| `arifosmcp/core/scalar_collector.py` | 276 | `confidence=min(max(0.0, min(1.0, g_val)), 0.90),` |
| `arifosmcp/core/scalar_collector.py` | 427 | `confidences.append(min(max(cf, 0.0), 0.90))` |
| `arifosmcp/runtime/DNA.py` | 28 | `CONFIDENCE_CAP: Final[float] = 0.90` |
| `arifosmcp/runtime/feedback_loop.py` | 250 | `confidence = min(confidence, 0.90)` |
| `arifosmcp/runtime/mind_reason.py` | 327 | `"confidence_cap": round(min(0.90, 1.0 - (rho * 0.3)), 2),` |
| `arifosmcp/runtime/mind_state.py` | 214 | `confidence=min(confidence, 0.90),  # F7 cap` |
| `arifosmcp/runtime/mind_state.py` | 281 | `self.epistemic_band = min(band, 0.90)  # F7 cap` |
| `arifosmcp/runtime/sabar_gate.py` | 79 | `OMEGA_0_HARD_CAP = 0.90` |
| `arifosmcp/schemas/stage_packets/__init__.py` | 125 | `default=0.0, ge=0.0, le=0.90, description="Capped at 0.90 (F7 HUMILITY)"` |

## Reading

The amendment that raised the ceiling from 0.90 to 0.97 reached the
canon and the doctrine prose. It did not reach the enforcement code,
which still clamps at 0.90 in the paths above. No compiler in any
language catches this: Rust and TypeScript would both compile thirty
copies of a stale constant without complaint. The remedy is one
constant with one owner plus a test that fails on drift — which is
what `arifosmcp/constitutional_canon.py` now provides.

_CLAMP sites change behaviour: the kernel refuses what canon permits. Migrating them is an F13 decision, not a refactor._
