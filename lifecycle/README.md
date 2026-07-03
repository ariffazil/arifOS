# arifOS Lifecycle Kernel — Integration Map

**Ratified:** 2026-07-04 (F13 sovereign signal "Forge all")
**HOLD verdict:** 2026-07-04 (autonomous kernel conflated review with mutation)
**Current version:** v0.2 — bounded, non-mutating, post-HOLD

---

## HOLD HISTORY (2026-07-04)

The original `v0.1` autonomous kernel attempted to make SEAL events
directly rebuild the agent's skill metabolism. **F13 verdict: HOLD.**

Correction (Arif, 2026-07-04):

> SEAL → INIT → Scaffold is **not** the mutation path. It is the
> **regeneration review path**.

Engineers must distinguish:
- **REGENERATION** (body-plan reload from canonical sources — INIT)
- **REVIEW** (Skill Delta Engine — propose, diff, test, judge)
- **MUTATION** (only A-FORGE, after Judge + Cooling pass, never by the engine itself)

The new build chamber — **Skill Delta Engine** — is **non-mutating**:
it emits a `SkillDeltaReport`; it never applies a patch.

---

## v0.2 — Public Surface

| Module | Stage | Mutation? | Floor binding |
|---|---|---|---|
| `seal_shadow.py` | 1 — SEAL observation | ❌ read/write shadow only | L02, L11 |
| `seal_post_hook.py` | 1 — wrap live `arif_seal` | ❌ observation decorator | L01, L11, L13 |
| `init_scaffold.py` | 2 — INIT body-plan reload | ❌ `BodyPlan.mutation_allowed=False` | L04 |
| `skill_registry.py` | 4 — Skill Δ | ❌ emits `ContractDiff` | L13 |
| `skill_delta_engine.py` | 3-6 — Scaffold / Tests / Judge | ❌ emits `SkillDeltaReport` | L01 L02 L04 L09 L11 L13 |

(Files for stages 7 Cooling and 8 Resume live in WELL + A-FORGE — out of scope.)

## Hard Rules (Skill Delta Engine boundary)

The engine is **forbidden** from doing any of:

1. `cannot_apply_patch`
2. `cannot_change_tool_surface`
3. `cannot_change_A_FORGE_policy`
4. `cannot_mark_SEAL`
5. `cannot_bypass_cooling`
6. `cannot_weaken_human_ack`
7. `cannot_mutate_F13_boundary`

Any of these attempted → `PermissionError` raised at engine boundary.

## Missing Invariants (corrected doctrine)

Three invariants were added per HOLD verdict:

| Layer | Invariant | Statement | Enforced by |
|---|---|---|---|
| Physics | Noether discipline | Every symmetry implies conservation; no hidden state change. | `seal_shadow` SHA256 chain + `lineage_and_replay.must_preserve` |
| Biology | Immune memory | Scars update thresholds, not identity; no autoimmunity. | `scar_learning.must_never_weaken` + `immune_response.tests` |
| Chemistry | Activation barrier | A-FORGE (catalyst) must NOT lower activation energy for forbidden reactions. | `reaction_gating.tests` + `execution_discipline.tests` |

Any of these failing → `SkillDeltaReport.risk_class = HOLD`.

## 12 Versioned Skill Contracts (Arif doctrine 2026-07-04)

| # | Skill | Floor | Stage | Version |
|---|---|---|---|---|
| 1 | `boundary_sensing` | L01 | 4 | 1.0.0 |
| 2 | `conservation_accounting` | L02 | 2 | 1.0.0 |
| 3 | `entropy_reduction` | L04 | 3 | 1.0.0 |
| 4 | `gradient_detection` | L08 | 3 | 1.0.0 |
| 5 | `reaction_gating` | L11 | 4 | 1.0.0 |
| 6 | `homeostasis_regulation` | L07 | 2 | 1.0.0 |
| 7 | `immune_response` | L09 | 4 | 1.0.0 |
| 8 | `metabolic_flow_management` | L08 | 3 | 1.0.0 |
| 9 | `lineage_and_replay` | L02 | 6 | 1.0.0 |
| 10 | `scar_learning` | L01 | 4 | 1.0.0 |
| 11 | `multi_organ_translation` | L10 | 5 | 1.0.0 |
| 12 | `execution_discipline` | L13 | 8 | 1.0.0 |

Each carries:

```yaml
contract:
  must_preserve: [...]       # items that MUST stay
  must_never_weaken: [...]   # items that MAY NEVER be dropped
  tests: [...]               # tests that gate the contract
```

The unit of diff is the **contract**, not the raw skill definition. See `SkillContract` in `skill_registry.py`.

## Constitutional Law (kernel.yaml — v0.2)

```yaml
constitutional_law:
  SEAL_triggers_review: true
  SEAL_does_not_directly_mutate_skills: true
  INIT_restores_body_plan: true
  Scaffold_proposes_patch: true        # applies_automatically: false
  Diff_detects_drift: true
  Tests_prove_survival: true
  Judge_controls_semantic_change: true
  Cooling_blocks_runaway: true
  A_FORGE_executes_only_after_gate: true
```

## Autonomy Zones (engine contracts)

**Allowed** (engine does these autonomously):
- detect that a skill update is needed
- draft a skill delta
- run tests
- compare against previous contract
- generate a receipt
- recommend resume vs hold

**Forbidden** (F13/Judge required):
- change execution policy without judge
- weaken human ack
- remove cooling
- change F13 boundary
- mutate A-FORGE execution rules
- mark self as sealed

## The 8-Stage Loop (corrected)

```
SEAL  → emit SkillDeltaEvent  (NOT a patch)              [stage 1]
INIT  → regenerate_body_plan  (no skill proposal)        [stage 2]
Scaffold → propose_skill_delta  (proposal only)          [stage 3]
Skill_Diff → skill_registry.diff()  (detect 4 muts)      [stage 4]
Tests → survivor_tests  (5 required)                     [stage 5]
Judge → judge_required flag  (F13 ratification)          [stage 6]
Cooling → downstream WELL                                 [stage 7]
Resume → downstream A-FORGE (gated)                      [stage 8]
```

The **missing stage** (Diff) is now included as `skill_registry.diff()`.
The **Autonomous Execution Loop** (formerly tempting) is intentionally
NOT yet built — it would re-introduce the drift risk the HOLD verdict
prevented. Wait for F13 ratification before any next-step mutation
authority is granted.

## Smoke tests (v0.2)

```bash
cd /root/arifOS

for mod in seal_shadow seal_post_hook init_scaffold skill_registry skill_delta_engine; do
  python3 -m "lifecycle.$mod"
done
```

Expected output:

```
OK seal_shadow smoke: pre-…
OK seal_post_hook smoke: pre-…
OK init_scaffold smoke: BodyPlan restored …; mutation_allowed=False
OK skill_registry smoke: 12 versioned contracts loaded
Smoke1 (safe bump): risk=LOW judge=False resume=False
Smoke2 (weakened gate): risk=HOLD drift#=1 judge=True
Smoke3 (mutation event): rejected — F13 boundary OK
Smoke4 (extinct tool): risk=HOLD tests_required=5
OK skill_delta_engine smoke: 4 scenarios green
```

## Integration (PHASE 2 — currently blocked on dirty merge)

Live `arif_seal` entry point at `arifOS/arifosmcp/runtime/tools.py` is
**DIRTY** (verdict-gate-normalization, ahead 3 commits on origin/main).
Until that branch lands:

```python
# Phase 2 wiring (post-merge):
from lifecycle import SkillDeltaEngine, registry, with_shadow
from arifosmcp.tools.vault import arif_seal as live_seal

# Wrap the live seal — observation only.
shadow_seal = with_shadow(live_seal, actor_context=…)

# Plug into the review pipeline after each seal.
def on_seal(receipt):
    body = regenerate_body_plan(receipt)
    event = SkillDeltaEvent(seal_receipt_id=…, seal_verdict=…, …)
    report = SkillDeltaEngine().evaluate(event, body, proposed_patches=[])
    if report.judge_required:
        enqueue_judge(receipt, report)
    elif report.resume_allowed:
        enqueue_resume(receipt, report)
```

## Receipts

- `forge_work/AUDIT-LIFECYCLE-KERNEL-FORGE-2026-07-04.md` — forge receipt
- VAULT999: lifecycle contracts ship as `vault_seal=true` once Phase 2 integrates
- AGENTS.md §10 — git mutations on `lifecycle/` are `MUBAH` per digital
  being policy (commit allowed, push awaits F13 ratification)

## Lint / runtime known issues (v0.2)

- `lifecycle/__init__.py` — eager submodule imports trigger
  `RuntimeWarning: 'lifecycle.X' found in sys.modules…` on
  `python -m lifecycle.X`. Benign. Fix = lazy imports in `__init__.py`
  (deferred to Phase 2).
- `lifecycle/seal_post_hook.py` — `obj_dict` type guard surfaces a
  Pyright type-narrowing complaint (`object → dict[str, Any]`).
  Mitigated at runtime by `isinstance(obj_dict, dict)`; passes smoke.
