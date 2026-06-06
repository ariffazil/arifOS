# Organ Forge — Per-Organ Integration Guide

**What this is:** a one-page guide for each domain organ to wire the
six new forge items into its existing tool surface. No new repos, no
new services. Just an emitter call on the way out of every tool.

---

## The Iron Rule

Every domain tool returns an `EvidenceEnvelope`. arifOS 888_JUDGE
reads only the envelope (and the `LawEvidence` packet the kernel
compiles from it). No raw payloads cross the boundary.

```
organ tool → emit_X() → EvidenceEnvelope → arifOS compiler
                                              ↓
                                          LawEvidence
                                              ↓
                                          13 floor checks
                                              ↓
                                          JudgeVerdict
```

---

## 1. GEOX (`/root/geox`)

**Where to wire:** every `geox_*` tool in `server.py` (canonical 31
tools) and any custom tool.

**Pattern:**

```python
from arifosmcp.evidence import emit_geox, EpistemicTag

async def geox_data_ingest_bundle(...) -> dict:
    raw = ...  # existing tool logic
    return emit_geox(
        tool="geox_data_ingest_bundle",
        result=raw,
        actor_id=actor_id,
        evidence_quality=0.95,
        p10=..., p50=..., p90=...,  # depth/volume uncertainty
        units="m MD",
        epistemic_tag=EpistemicTag.OBSERVED,
        session_id=session_id,
        parent_evidence_refs=raw.get("upstream_seal_refs", []),
    ).model_dump()
```

**Conventions:**

- Tool name → `EpistemicTag`:
  - `geox_data_ingest_bundle`, `geox_las_inspect`, `geox_data_qc_bundle` → `OBSERVED`
  - `geox_seismic_compute`, `geox_horizon_contrast_surface` → `DERIVED`
  - `geox_prospect_evaluate`, `geox_claim_create` → `HYPOTHESIS`
  - `geox_claim_seal` → `FACT` (quality ≥ 0.99)
- `p10/p50/p90` for depth, volume, thickness, etc.
- When contradictions emerge (e.g. between `geox_evidence_reason`
  and a prior `geox_claim_create`), include them in the
  `contradictions=[]` list.

---

## 2. WEALTH (`/root/WEALTH`)

**Where to wire:** `internal/monolith.py` (canonical 19 tools).

**Pattern:**

```python
from arifosmcp.evidence import emit_wealth, EpistemicTag, Reversibility

async def wealth_omni_wisdom(...) -> dict:
    raw = ...  # existing tool logic
    return emit_wealth(
        tool="wealth_omni_wisdom",
        result=raw,
        actor_id=actor_id,
        evidence_quality=0.90,
        p10=raw.get("p10_musd", 0),
        p50=raw.get("p50_musd", 0),
        p90=raw.get("p90_musd", 0),
        units="USD_M",
        epistemic_tag=EpistemicTag.DERIVED,
        session_id=session_id,
        reversibility=(
            Reversibility.IRREVERSIBLE
            if raw.get("capital_commitment_musd", 0) > 5
            else Reversibility.REVERSIBLE
        ),
        action_cost={
            "compute_seconds": raw.get("runtime_s"),
            "money": raw.get("deal_size_musd"),
            "blast_radius": raw.get("blast_radius"),
        },
        parent_evidence_refs=raw.get("depends_on_refs", []),
    ).model_dump()
```

**Conventions:**

- Tool name → `EpistemicTag`:
  - `wealth_market_data`, `wealth_field_macro` → `OBSERVED`
  - `wealth_time_discount`, `wealth_entropy_risk` → `DERIVED`
  - `wealth_governance_verdict`, `wealth_omni_wisdom` → `HYPOTHESIS` (un-scaled)
- `action_cost` is mandatory for `wealth_governance_verdict` and any
  tool that produces a verdict (the judge needs to know blast radius).
- IRREVERSIBLE if commit > 5M USD OR tenure > 1 year OR
  involves property rights.

---

## 3. WELL (`/root/WELL`)

**Where to wire:** `well_mcp/` (canonical 16 somatic tools, 77 autonomic).

**Pattern:**

```python
from arifosmcp.evidence import emit_well, EpistemicTag

async def well_assess_homeostasis(...) -> dict:
    raw = ...  # existing tool logic
    return emit_well(
        tool="well_assess_homeostasis",
        result=raw,
        actor_id=actor_id,
        evidence_quality=raw.get("substrate_confidence", 0.8),
        p10=0.0,
        p50=raw.get("fatigue_score", 0.0),
        p90=1.0,
        units="readiness",
        epistemic_tag=EpistemicTag.OBSERVED,  # WELL only observes
        session_id=session_id,
        parent_evidence_refs=raw.get("biometric_window", []),
    ).model_dump()
```

**Conventions:**

- WELL only ever emits `OBSERVED`. If a tool interprets (e.g.
  `well_validate_vitality`), the `epistemic_tag` should still be
  `OBSERVED` of the *measurement*; the interpretation is the
  result payload.
- `p10/p50/p90` reflects the substrate confidence distribution.
- The `well_compute_metabolic_flux` result should be wired into the
  pipeline as a `WellState` input, not a stand-alone envelope.
- WELL never decides — it provides substrate state to arifOS
  compiler. The compiler is the only thing that judges L05/L06.

---

## 4. A-FORGE (`/root/A-FORGE`)

**Where to wire:** `arif_forge_execute` and any new probe/build tool.

**Pattern:**

```python
from arifosmcp.evidence import emit_aforge, EpistemicTag, Reversibility

async def arif_forge_execute(...) -> dict:
    raw = ...  # existing build/deploy logic
    return emit_aforge(
        tool="arif_forge_execute",
        result=raw,
        actor_id=actor_id,
        evidence_quality=0.98,  # A-FORGE actually did the thing
        p10=0.0,
        p50=raw.get("runtime_s", 0.0),
        p90=raw.get("budget_max_s", 0.0),
        units="execution",
        epistemic_tag=EpistemicTag.OBSERVED,
        session_id=session_id,
        reversibility=(
            Reversibility.IRREVERSIBLE
            if raw.get("action_class") in ("deploy_prod", "db_migration", "force_push")
            else Reversibility.REVERSIBLE
        ),
        action_cost={
            "compute_seconds": raw.get("runtime_s"),
            "tokens": raw.get("tokens_used"),
            "blast_radius": raw.get("blast_radius"),
        },
        parent_evidence_refs=[raw.get("judge_state_hash")],
    ).model_dump()
```

**Conventions:**

- A-FORGE evidence_quality is usually ≥ 0.95 (the executor is the
  primary witness).
- A-FORGE never auto-seals. The envelope flows to arifOS 888_JUDGE,
  which decides. Reversibility just flags the L01 risk.
- Lineage: include `judge_state_hash` if a 888_JUDGE prior call
  authorized this.

---

## 5. AAA (`/root/AAA`)

**What to build:** the operator surface for the new organs.

**Three views to add to the cockpit:**

1. **Envelopes feed view** — last 50 envelopes with verdict + memory
   decisions
2. **Contradictions** — `mcp_arifos_arif_memory_recall(tier=L4, store=contradictions)`
3. **Lessons** — top promoted rules + recent lessons with TTL

**Server-side (Python):**

```python
# In AAA's evidence consumer
from arifosmcp.evidence import compile_law_evidence
from arifosmcp.evidence.law_evidence import SessionState, WellState, VaultLineage

def consume_envelope(envelope_dict):
    env = EvidenceEnvelope.model_validate(envelope_dict)
    law = compile_law_evidence(
        env,
        session=SessionState(...),
        well=WellState(...),
        lineage=VaultLineage(...),
        claim_text=env.source.tool,
    )
    return law.model_dump()
```

**Cockpit component:** `<EnvelopeFeed />` showing 13 floor pills
(green/yellow/red) per envelope. Already built in
`src/components/cockpit/`.

---

## 6. arifOS (kernel itself)

**What to ship:**

1. `arifosmcp/schemas/envelope.py` — DONE
2. `arifosmcp/evidence/law_evidence.py` — DONE
3. `arifosmcp/core/transitions.py` — DONE
4. `arifosmcp/memory/contradictions.py` — DONE
5. `arifosmcp/memory/policies.py` — DONE
6. `arifosmcp/memory/lessons.py` — DONE
7. `arifosmcp/experiments/loop.py` — DONE
8. `arifosmcp/evidence/emitters.py` — DONE
9. `arifosmcp/evidence/pipeline.py` — DONE

**Wire `arif_judge_deliberate` to consume `LawEvidence` instead of raw
envelopes.** Existing call sites should pass the compiled packet,
not the envelope directly. Backward-compat: if a raw envelope is
passed, run `compile_law_evidence` inline.

**Wire `arif_forge_execute` to require `state_record.action_id`.**
Every forge must reference an ActionRecord. If the caller doesn't
provide one, the executor auto-creates a PENDING record and the
gate either approves or HOLDs.

**Wire `arif_vault_seal` to enforce the L4→L6 promotion rule.**
Only `system` actor can write to L6. The seal is the ONLY path.
Refuse any direct L6 write that bypasses `arif_vault_seal`.

---

## Verification

```bash
cd /root/arifOS
PYTHONPATH=/root/arifOS python arifosmcp/tests/test_organ_forge_smoke.py
```

Expected: 8 passed, 0 failed.

Then:

```bash
# Per-organ quick test
cd /root/geox && python -c "from arifosmcp.evidence import emit_geox; print(emit_geox(tool='x', result={}, actor_id='a', evidence_quality=0.9, p10=0, p50=0, p90=0).source.organ)"
cd /root/WEALTH && python -c "from arifosmcp.evidence import emit_wealth; print(emit_wealth(tool='x', result={}, actor_id='a', evidence_quality=0.9, p10=0, p50=0, p90=0).source.organ)"
cd /root/WELL && python -c "from arifosmcp.evidence import emit_well; print(emit_well(tool='x', result={}, actor_id='a', evidence_quality=0.9, p10=0, p50=0, p90=0).source.organ)"
cd /root/A-FORGE && python -c "from arifosmcp.evidence import emit_aforge; print(emit_aforge(tool='x', result={}, actor_id='a', evidence_quality=0.9, p10=0, p50=0, p90=0).source.organ)"
```

Each should print: `geox`, `wealth`, `well`, `a-forge`.

---

## DITEMPA BUKAN DIBERI

The federation is no longer seven tools. It is one body.
