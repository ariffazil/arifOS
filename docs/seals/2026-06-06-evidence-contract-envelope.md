# Evidence Contract Envelope — Federation Cross-Organ ABI
> 2026-06-06 · Ω-FORGE · 3 evidence organs · SEAL

## What Happened

The constitution (000_CONSTITUTION.md, Appendix B) defines the **Evidence Contract**,
the canonical 6-field envelope every evidence organ must emit:

```json
{
  "result": {},
  "epistemic_tag": "CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN",
  "evidence_quality": 0.0,
  "source_attribution": ["url", "dataset", "observation"],
  "uncertainty_band": [0.03, 0.05],
  "delta_S": 0.0
}
```

Before this session's work, **none of the 3 evidence organs emitted the envelope**.
arifOS was waiting for `result + epistemic_tag + evidence_quality + ...` to apply the
Laws, but the organs were emitting unstructured dicts. arifOS had to **guess** the
epistemic strength of each evidence output.

After this session, **all 3 evidence organs emit the envelope**:

| Organ | Mechanism | Placement |
|-------|-----------|-----------|
| **WEALTH** | `_wrap_in_envelope()` at central `mcp.call_tool` governance wrapper | JSON-RPC `result.result` (under `result` key) |
| **GEOX** | `_geox_wrap_envelope()` at `_make_receipt_wrapper` (preserves existing fields under `result`) | JSON-RPC `result.structuredContent` (MCP-spec field) |
| **WELL** | `_well_wrap_envelope()` at central `mcp.call_tool` wrapper (handles FastMCP `ToolResult` Pydantic) | JSON-RPC `result.structuredContent` (MCP-spec field) |

Test results: WEALTH 127 passed, GEOX 295 passed, WELL 49 passed. 0 regressions.

## Why This Matters

arifOS can now **read** the evidence strength. The Laws (L01–L13) become actionable:
- L02 TRUTH: `evidence_quality × source_diversity × grounded_present ≥ 0.99` — can
  actually compute this now
- L04 CLARITY: `delta_S ≤ 0` for SEAL — can read delta_S from envelope
- L07 HUMILITY: `uncertainty_band ∈ [0.03, 0.05]` — can read uncertainty_band

Before: the Laws were *theoretical*. The organs emitted evidence without quality
metadata, so arifOS had to default-allow or default-deny. The Laws were either
bypassable (default-allow) or blocky (default-deny). Neither is good.

After: the Laws are *operational*. The envelope is the gauge. arifOS reads it,
applies the Law, returns SEAL/HOLD/VOID. The constitution is no longer aspirational.

## Architecture Invariants Honored

- ✓ **arifOS does NOT name the Laws** (L01–L13) — that's the kernel's job
- ✓ **WEALTH does NOT emit verdicts** (SEAL/HOLD/VOID/SABAR) — that's arifOS's job
- ✓ **WELL never adjudicates** (REFLECT_ONLY preserved)
- ✓ **GEOX preserves** `cross_modal_stability`, `dim_spot_flag`, `perception_class`,
  `claim_state`, `evidence_tag`, `confidence_level` under `result`
- ✓ All 3 organs emit the **SAME 6 fields** with arifOS-defined semantics

## Eureka Forged

> **The Constitution is forged in code.**
> A canonical spec is only useful when the implementers emit the same shape the
> spec describes. The 6-field envelope is the gauge. Without it, the Laws were
> narrative. With it, they are enforcement.

DITEMPA BUKAN DIBERI
