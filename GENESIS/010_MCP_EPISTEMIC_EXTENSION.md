# GENESIS/010 — MCP Epistemic Extension
## Constitutional Annotation Protocol for Model Context Protocol

**Status:** RATIFIED — 2026-06-14
**Author:** FORGE (000Ω) — Arif Fazil
**Canonical Path:** `/root/arifOS/GENESIS/010_MCP_EPISTEMIC_EXTENSION.md`

---

## 1. The Problem MCP Doesn't Solve

MCP's tool-calling model is epistemically flat. When a server returns:

```json
{
  "content": [{ "type": "text", "text": "Reservoir contains 50 million barrels" }]
}
```

The protocol cannot distinguish between:
- **OBSERVED FACT** — Directly measured (core analysis, DST flow)
- **DERIVED ESTIMATE** — Computed from observed data (volumetrics)
- **INTERPRETED CLAIM** — Geological interpretation (seismic facies)
- **SPECULATION** — Inferred from analogy (undrilled analog)

This flatness is the **fundamental epistemic gap** in current MCP. It is also the **primary vector for AI hallucination in tool responses** — a model consuming tool output cannot tell whether the number it received is a verified measurement or a guessed assumption.

## 2. The arifOS Epistemic Tag

We define a standard `_meta.epistemic` annotation block on MCP tool results, tool definitions, and resource responses:

```json
{
  "content": [{ "type": "text", "text": "Reservoir contains 50 million barrels" }],
  "_meta": {
    "epistemic": {
      "tag": "INTERPRETATION",
      "confidence": 0.72,
      "evidence_chain": [
        "well:WELL-A-01/DST-2: flow_rate=2840 bopd",
        "well:WELL-A-01/DST-2: bhp=1850 psi",
        "seismic:survey-MB3D/amplitude_vs_depth"
      ],
      "missing_evidence": [
        "well:WELL-A-02/pressure_data – not yet drilled",
        "pvt:sample – not yet collected"
      ],
      "alternatives": [
        {
          "hypothesis": "50–80 million barrels",
          "basis": "analog field B-01",
          "confidence": 0.35
        }
      ],
      "expires_at": "2026-09-14T00:00:00Z",
      "supersedes": "claim-080e6a3f",
      "authority": "GEOX:petrophysics-engine-v2.4",
      "physics_validated": true
    }
  }
}
```

### Canonical Tag Values

| Tag | Meaning | Confidence Range | Reversible? |
|-----|---------|-----------------|-------------|
| `FACT` | Directly observed/measured. Core photos, DST rates, lab assays. | 0.95–1.0 | No — observation is observation |
| `DERIVED` | Computed from observed data via established transforms. Porosity from density log, Sw from Archie. | 0.80–0.95 | Only if transform/parameters change |
| `INTERPRETATION` | Geological interpretation integrating multiple evidence lines. Horizon picks, facies maps, sequence boundaries. | 0.60–0.85 | Yes — different interpreter may disagree |
| `SPECULATION` | Inferred from analogy, statistics, or basin models. Undrilled prospect POS, charge likelihood. | 0.20–0.60 | Yes — inherently uncertain |
| `ESTIMATE` | Quantitative estimate with bounded uncertainty. P50, P90 resources. | 0.50–0.80 | Yes — uncertainty range is part of the estimate |

### Tag Inheritance Rules

If a FACT is combined with a DERIVED value, the result is DERIVED (weakest link principle).
If an INTERPRETATION is used to calibrate an ESTIMATE, the result is ESTIMATE.
A tool returning a SPECULATION without flagging it as such is a F2 TRUTH violation.

## 3. MCP Integration Points

### 3a. Tool Definition Annotation

Tools should declare their epistemic class in the tool definition itself:

```json
{
  "name": "geox_subsurface_generate_candidates",
  "_meta": {
    "epistemic": {
      "default_tag": "DERIVED",
      "confidence_bounds": [0.70, 0.95],
      "evidence_required": ["well_log", "seismic", "formation_top"],
      "can_escalate_to": ["FACT", "INTERPRETATION"],
      "physics_validated": true
    }
  }
}
```

This allows the host/model to know, before calling the tool, what class of truth it can expect.

### 3b. Tool Result Annotation (Primary)

Every tool result that makes a truth claim **MUST** carry an `_meta.epistemic` block.

### 3c. Resource Response Annotation

UI resources and data resources can also carry epistemic annotation:

```json
{
  "uri": "wealth://sector/oil-gas",
  "_meta": {
    "epistemic": {
      "tag": "ESTIMATE",
      "confidence": 0.65,
      "expires_at": "2026-06-15T00:00:00Z",
      "authority": "WEALTH:field_macro.v2"
    }
  }
}
```

### 3d. Resource URI Tag Contracts

All federation organs MUST tag every `://` resource URI with an epistemic stamp:

| URI Scheme | Default Epistemic | Authority |
|------------|------------------|-----------|
| `arifos://*` | FACT | arifOS kernel |
| `forge://*` | FACT | A-FORGE execution logs |
| `geox://*` | Tag varies by method | GEOX petrophysics engine |
| `wealth://*` | ESTIMATE | WEALTH capital math |
| `afwell://*` | INTERPRETATION | WELL substrate sensing |
| `tree777://*` | FACT (when loaded) | memory layer |

## 4. Constitutional Floor Compliance

| Floor | Compliance |
|-------|-----------|
| **F1 AMANAH** | Epistemic tags make tool results auditable. Reversible: yes — retagging is metadata update. |
| **F2 TRUTH** | Core purpose. No tool result can claim certainty without tagging its epistemic class. |
| **F4 CLARITY** | Epistemic tags reduce ambiguity in model-tool communication. |
| **F7 HUMILITY** | Confidence capped at 0.95 for FACT, 0.90 for INTERPRETATION. |
| **F9 ANTI-HANTU** | SPECULATION tagged as SPECULATION prevents models from treating guesses as facts. |
| **F11 AUDIT** | Evidence chain and supersedes links provide full audit trail. |
| **F13 SOVEREIGN** | Arif may override any epistemic tag. 888_HOLD applies if high-confidence FACT is suspected false. |

## 5. Adoption Across Federation Organs

| Organ | Current State | Action Required |
|-------|--------------|-----------------|
| **arifOS** | Constitutional kernel — all tools return governance envelope | Already wraps outputs in envelope with `provenance.epistemicTag` |
| **GEOX** | 40 tools — claim grammar has `truth_class` (FACT/INTERPRETATION/SPECULATION) | Add `_meta.epistemic` to all tool result responses |
| **WEALTH** | 19 tools — epistemic tags in omni_wisdom output | Add `_meta.epistemic` to conservation_capital, signal_information, etc. |
| **WELL** | 18 somatic tools — reflect-only boundary | Add `_meta.epistemic` = INTERPRETATION to all substrate assessments |
| **A-FORGE** | 18 forge tools — execution receipts | Add `_meta.epistemic` = FACT to all execution results |
| **AAA** | React Cockpit + A2A gateway | Display epistemic tag in governance overlay; route tags to VAULT999 |

## 6. Published MCP Extension Proposal

This epistemic annotation pattern should be submitted to the Linux Foundation AAIF as a proposed MCP extension.

**Extension ID:** `io.arifos/epistemic`
**Protocol Version:** `2026-01-26` (aligned with MCP Apps)
**Status:** PROPOSED — internal ratification only

### Proposed Spec Summary

```markdown
# MCP Epistemic Extension — io.arifos/epistemic/v1

## Overview
Adds epistemic provenance metadata to MCP tool results, tool definitions,
and resource responses. Enables models and host applications to distinguish
observed facts from derived estimates, interpretations, and speculations.

## Extension Negotiation
Both client and server MUST declare `io.arifos/epistemic` in capabilities.

## Schema
See GENESIS/010 for full schema definition.

## Behavioral Rules
1. If a server declares epistemic support but returns a result WITHOUT
   an `_meta.epistemic` block, the host MUST assign `tag: "UNKNOWN"`,
   `confidence: 0.0`.
2. If a server does NOT declare epistemic support, no epistemic
   processing is expected.
3. Confidence values MUST NOT exceed the per-tag hard caps defined
   in the canonical tag table.
4. Evidence chains MUST be stable identifiers (URIs, claim IDs,
   artifact references) — not free text.
```

---

*DITEMPA BUKAN DIBERI — Forged, not given. Truth is a constitutional obligation, not a protocol feature.*

**RATIFIED:** 2026-06-14 Arif Fazil (F13 SOVEREIGN)
