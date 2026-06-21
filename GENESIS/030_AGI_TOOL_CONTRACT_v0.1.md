# GENESIS/030 — AGI Tool Contract v0.1

> **Constitutional cross-reference for AGI substrate readiness.**
>
> **Status:** v0.1 DRAFT — autonomous forge (2026-06-21, FORGE 000Ω)
>
> **Authority:** F13 SOVEREIGN — no production deployment without Arif ratification
>
> **Purpose:** Single binding cross-reference that reconciles the four substrate layers:
> Reality Engineering doctrine + FederationEnvelope schema + CapabilitySurface schema +
> MCP tool annotations spec (2025-03-26).

DITEMPA BUKAN DIBERI — Forged, not given.

---

## 0. The Single Mental Model

arifOS is an **L8 constitutional substrate** that wraps MCP tools with three concentric
governance layers:

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 4: arifOS CONSTITUTIONAL FLOORS (F1-F13)                   │
│   Source: /root/arifOS/GENESIS/000_KERNEL_CANON.md               │
│   Type: Doctrinal (the law)                                      │
│   Enforcement: arif_judge_deliberate, arif_heart_critique        │
├──────────────────────────────────────────────────────────────────┤
│ Layer 3: Reality Engineering DOCTRINE (AR-QOCF rubric)          │
│   Source: /root/forge_work/2026-06-17-reality-engineering-spec.md│
│   Type: Doctrinal (the grading)                                  │
│   Enforcement: AR-QOCF scorer, pre-SEAL gate                     │
├──────────────────────────────────────────────────────────────────┤
│ Layer 2: FederationEnvelope v2.0 (action_class, risk passport)   │
│   Source: /root/arifOS/arifosmcp/schemas/federation_envelope.py  │
│   Type: Pydantic schema (the envelope)                           │
│   Enforcement: validate_for_execution(), pre_execution_gate      │
├──────────────────────────────────────────────────────────────────┤
│ Layer 1: CapabilitySurface (ALIGNED/OVERCLAIM/DARK/UNDERCLAIM)   │
│   Source: /root/arifOS/arifosmcp/schemas/capability_surface.py   │
│   Type: Pydantic schema (the honesty map)                        │
│   Enforcement: capability_aware_router.py                        │
└──────────────────────────────────────────────────────────────────┘
```

**Above all four layers** sits the **MCP tool surface** — the standard protocol
contract. Layer 0 is the standard; Layers 1-4 are the arifOS governance that wraps it.

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 0: MCP TOOL ANNOTATIONS (2025-03-26 spec)                  │
│   readOnlyHint, destructiveHint, idempotentHint, openWorldHint   │
│   Type: Protocol hints (the standard)                            │
│   ⚠️  Spec says: annotations are UNTRUSTED unless from a         │
│   trusted server. The arifOS move: DERIVE them from              │
│   action_class, never hand-set.                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 1. The Tool Contract — Per-Tool Affordance

Every public MCP tool exposed by arifOS organs SHALL declare this contract:

```yaml
tool_contract:
  # ── Identity (Layer 0: MCP standard) ──────────────────────────
  tool_name: arif_<noun>_<verb>           # 19 canonical pattern
  organ: arifOS | WEALTH | WELL | GEOX | A-FORGE | AAA
  tool_schema_hash: sha256:...
  tool_version: v0.1.0
  description: "..."

  # ── MCP standard annotations (Layer 0) ────────────────────────
  # CRITICAL: These are DERIVED from action_class, NOT hand-set.
  # A malicious server can mark destructiveHint=true to bypass
  # confirmation. The spec says so. The arifOS move is to compute
  # these from the deterministic gates below.
  mcp_annotations:
    readOnlyHint: <computed from action_class == OBSERVE>
    destructiveHint: <computed from action_class in {MUTATE, IRREVERSIBLE}>
    idempotentHint: <computed from reversibility == HIGH>
    openWorldHint: <computed from external_effect != NONE>

  # ── FederationEnvelope action classification (Layer 2) ────────
  action_class:
    primary: OBSERVE | ANALYZE | DRAFT | SIMULATE |
             MUTATE | EXTERNAL_SIDE_EFFECT | IRREVERSIBLE
    tool_class: OBSERVE | RETRIEVE | DECIDE | MUTATE

  # ── Risk Passport (Layer 2) ──────────────────────────────────
  risk:
    tier: T0 | T1 | T2 | T3 | T4 | T5
    blast_radius: NONE | LOCAL | ACCOUNT | ORG | PUBLIC |
                  MARKET | INFRASTRUCTURE | CIVILIZATIONAL
    reversibility: HIGH | MEDIUM | LOW | IRREVERSIBLE
    secret_touch: NONE | POSSIBLE | DEFINITE
    external_effect: NONE | PRIVATE | PUBLIC | LEGAL | FINANCIAL

  # ── Sovereignty Checkpoint (Layer 2) ──────────────────────────
  # Required when tool_scope includes dignity, memory, vault, secret
  requires_sovereignty_checkpoint: false
  tool_scope: []  # subset of {read, write, external, secret,
                  # memory, dignity, vault}

  # ── CapabilitySurface honesty (Layer 1) ───────────────────────
  capability:
    available: <live probe>
    read_ok: <live probe>
    write_ok: <live probe>
    status_alignment: ALIGNED | OVERCLAIM | UNDERCLAIM | DARK | UNKNOWN
    autonomy_mode: AGI_CHAIN | SHORT_CHAIN | ASSIST | BLOCKED

  # ── Reality Engineering rubric (Layer 3) ─────────────────────
  # Pre-SEAL gate: all axes ≥ 0.65 required for SEAL
  rubric:
    quality_weight: 0.30
    originality_weight: 0.15
    craft_weight: 0.25
    functionality_weight: 0.30
    seal_threshold: 0.85
    sabar_threshold: 0.65
    hold_threshold: 0.45
    per_axis_minimum: 0.65

  # ── Constitutional floor binding (Layer 4) ───────────────────
  floors_active: [F1, F2, F4, F11, F13]  # subset of F1-F13
  evidence_required: true
  audit_pointer: vault://seal/...

  # ── Agent operating doctrine (portable, see arifos-agent-doctrine)
  doctrine:
    power_surface_classified: true
    evidence_source_required: true
    degraded_dominance_enforced: true
    actor_resolution_required: true
    reversibility_default: HIGH
    epistemic_label: OBS | DER | INT | SPEC
```

---

## 2. The 8-Gate Governed Intelligence Flow

Every request flows through 8 gates before any tool executes. The substrate IS the flow.

```
INBOUND REQUEST
   ↓
[G1] arif_actor_resolve         ← Context7/Notion pattern
        actor_id, actor_verified=true, resolution_hash, expires_at
        ↓  (HARD FAIL if unresolved for non-OBSERVE)
[G2] FederationEnvelope bind    ← trace_id, niat, matlamat, risk passport
        ↓  (LEGACY_WRAP only for OBSERVE/DRAFT)
[G3] CapabilitySurface check    ← ALIGNED? autonomy_mode ≠ BLOCKED?
        ↓  (FAIL → degraded-dominance: HOLD only)
[G4] MCP annotations COMPUTED   ← readOnlyHint = (action_class == OBSERVE)
                                  destructiveHint = (action_class in IRREVERSIBLE)
                                  idempotentHint = (reversibility == HIGH)
                                  openWorldHint = (external_effect != NONE)
        ↓  (NEVER hand-set; computed from Layer 2 enums)
[G5] ActionReceipts validation  ← observe_receipt_id before MUTATE
                                  arif_ack_id before ATOMIC
        ↓  (FAIL → request ack token, return cost_id)
[G6] Tool dispatch              ← dry_run=True default
        ↓  Returns EvidenceReceipt (source, actor, transformation,
                                    trust_class, injection_surface)
[G7] Degraded-dominance gate    ← if surface != ALIGNED, suppress SEAL
        ↓  judge_deliberate + vault_seal refuse positive verdict
[G8] Vault seal                 ← only if surface == ALIGNED
        ↓
RESULT (full provenance, replay-able, audited)
```

| Gate | Floor | Reversibility | Test |
|------|-------|---------------|------|
| G1 | F13 SOVEREIGN | Code rollback | anon + non-OBSERVE → HOLD |
| G2 | F11 AUTH | Code rollback | LEGACY_WRAP + ATOMIC → rejected |
| G3 | F9 ANTIHANTU | Code rollback | degraded → no positive verdict |
| G4 | F2 TRUTH | Code rollback | destructiveHint = computed |
| G5 | F1 AMANAH | Code rollback | ack required for ATOMIC |
| G6 | F7 HUMILITY | Code rollback | default = dry_run |
| G7 | F9 ANTIHANTU | Code rollback | degraded → HOLD |
| G8 | F11 AUDIT | Code rollback | seal rejected if degraded |

---

## 3. The 4-Schema Reconciliation

These four schemas MUST stay in lockstep. Any change to one requires review of the other three.

| Schema | File | Purpose |
|--------|------|---------|
| **FederationEnvelope v2.0** | `arifosmcp/schemas/federation_envelope.py` | The envelope (identity, authority, risk, scope, checkpoint) |
| **CapabilitySurface** | `arifosmcp/schemas/capability_surface.py` | The honesty map (ALIGNED/OVERCLAIM/DARK) |
| **ConstitutionIdentity** | `arifosmcp/schemas/constitution_identity.py` (Phase 6) | The law binding (one hash, one identity, one version) |
| **EvidenceReceipt** | `arifosmcp/schemas/evidence_receipt.py` (Phase 6) | The evidence chain (source, actor, trust class, injection surface) |

**Reconciliation rule:** Any new tool that adds a `risk.tier`, `action_class`, or
`blast_radius` MUST be reflected in:
- The capability router's tier table
- The pre-execution gate's action_class enum
- The conformance spine's check list
- The AGENTS.md canonical tool table

---

## 4. The 19 Canonical Tools + 34 Autonomic

arifOS exposes **53 total `@mcp.tool` decorators** but only **19 are public canonical**
(agent-callable, agent-discoverable, F1-F13 bound). The other 34 are **autonomic**
(internal, kernel-only, autonomic-system helpers).

| Category | Count | Listed in | Agent-callable? |
|----------|-------|-----------|-----------------|
| **Public canonical** | 19 | `arifosmcp/AGENTS.md` | YES |
| **Autonomic / diagnostic** | 34 | `arifosmcp/constitutional_map.py` (Phase 7) | NO |
| **Shadow / experimental** | 0 | (deprecated) | NO |

This is the honest taxonomy. Previously labeled "canonical13" — that label is deprecated.
The 19 includes all F1-F13 binding surface; the 34 are kernel internals.

---

## 5. The Reality Engineering AR-QOCF Rubric

From `/root/forge_work/2026-06-17-reality-engineering-spec.md` §2:

| Axis | What | Who scores | Weight |
|------|------|-----------|--------|
| **Q** Quality | Did the work meet intent without defects? | GEOX/WEALTH/WELL evidence organ | 0.30 |
| **O** Originality | Non-obvious connections, not pattern-match? | 555-ASI ethical critique | 0.15 |
| **C** Craft | Disciplined, well-tested, low-entropy? | A-AUDIT continuous monitor | 0.25 |
| **F** Functionality | Works as claimed under realistic conditions? | GEOX/WEALTH/WELL evidence organ | 0.30 |

**Aggregation:** weighted mean.

| Score | Verdict | Meaning |
|-------|---------|---------|
| `>= 0.85` | **SEAL** | Human Review queue, ready for merge |
| `0.65 <= s < 0.85` | **SABAR** | Need iteration, agent continues autonomously |
| `0.45 <= s < 0.65` | **HOLD** | Agent stops, escalates to A-AUDIT |
| `< 0.45` | **VOID** | Constitutional violation likely, escalate to 888-APEX |

**Critical:** ALL FOUR axes must score ≥ 0.65 for SEAL. High Functionality with low
Quality does NOT pass — prevents "works but ugly" or "elegant but lies" outcomes.

---

## 6. The Portable Agent Doctrine

From `/root/.agents/skills/arifos-agent-doctrine/SKILL.md`:

| # | Invariant | Anti-pattern |
|---|-----------|--------------|
| 1 | ROUTE BY DATA LOCATION | Narrating live system state from memory |
| 2 | GROUND BEFORE ASSERT; DEGRADED DOMINATES | SEAL with `also_warning_somewhere: vault_replay failed` |
| 3 | HINTS ≠ CONTRACTS | Trusting `readOnlyHint: true` from a malicious server |
| 4 | OUTER = min(INNER GATES) | Reporting SAFE when inner is HOLD |
| 5 | RESOLVE BEFORE ACT | Anonymous actor reaching MUTATE path |
| 6 | CHARISMA = TRUST-DOWN | Accepting "great answer!" as evidence |
| 7 | REVERSIBLE-FIRST | Defaulting to execute when draft was available |
| 8 | CONVERGENCE RAISES, FLATTERY LOWERS | One model's confident answer |
| 9 | LABEL UNCERTAINTY | Asserting without OBS/DER/INT/SPEC |
| 10 | UNDER-DOCUMENTATION ≠ NOVELTY | Inventing new vocab for old safety concepts |

These are portable — any substrate can adopt them.

---

## 7. The 12 MCP Tool Annotations — Computed, Not Declared

From the MCP spec 2025-03-26, the four standard annotations:

```yaml
readOnlyHint:        # Tool does not modify its environment
  computed_from: action_class == OBSERVE

destructiveHint:     # Tool may perform destructive updates
  computed_from: action_class in (MUTATE, IRREVERSIBLE)
                  AND reversibility == IRREVERSIBLE

idempotentHint:      # Repeated calls with same args have no additional effect
  computed_from: reversibility == HIGH
                  AND action_class in (MUTATE, ATOMIC)

openWorldHint:       # Tool interacts with an open world (external systems)
  computed_from: external_effect in (PUBLIC, LEGAL, FINANCIAL)
```

**Why computed:** the spec says annotations are UNTRUSTED. A malicious server
could mark `destructiveHint: false` to bypass confirmation. The arifOS move:
**derive them from the deterministic enums in FederationEnvelope v2.0.** This
closes the spec loophole by construction.

---

## 8. The Compatibility Map — Existing Schemas

This section enumerates the existing schemas that already implement the contract.
Each row confirms what is ALREADY BUILT and points to its file.

| Contract field | Existing schema | Status |
|---------------|-----------------|--------|
| `action_class` | `FederationEnvelope.ActionClass` (7 enums) | ✅ EXISTS |
| `tool_class` | `FederationEnvelope.ToolClass` (4 enums) | ✅ EXISTS |
| `blast_radius` | `FederationEnvelope.BlastRadius` (8 enums) | ✅ EXISTS |
| `reversibility` | `FederationEnvelope.ReversibilityLevel` (4 enums) | ✅ EXISTS |
| `secret_touch` | `FederationEnvelope.SecretTouch` (3 enums) | ✅ EXISTS |
| `external_effect` | `FederationEnvelope.ExternalEffect` (5 enums) | ✅ EXISTS |
| `tool_scope` | `FederationEnvelope.ToolScope` (7 enums) | ✅ EXISTS |
| `authority` | `FederationEnvelope.AuthorityEnvelope` (6 sources) | ✅ EXISTS |
| `actor_verification` | `FederationEnvelope.actor_verification` (3 levels) | ✅ EXISTS |
| `sovereignty_checkpoint` | `arifosmcp/schemas/sovereignty_checkpoint.py` | ✅ EXISTS |
| `claim_state` | `arifosmcp/schemas/embodied_tool.py` | ✅ EXISTS |
| `receipts` | `FederationEnvelope.ActionReceipts` | ✅ EXISTS |
| `status_alignment` | `CapabilitySurface.StatusAlignment` (5 enums) | ✅ EXISTS |
| `capability_tier` | `CapabilitySurface.CapabilityTier` (5 enums) | ✅ EXISTS |
| `autonomy_mode` | `CapabilitySurface.AutonomyMode` (4 enums) | ✅ EXISTS |
| `constitution_identity` | (Phase 6 — new tuple schema) | ❌ MISSING |
| `evidence_receipt` | dict-bag in tools.py (Phase 6 — promote to Pydantic) | ⚠️ PARTIAL |
| `mcp_annotations` (computed) | not yet computed (Phase 2) | ❌ MISSING |

**Net:** 15/18 fields are already implemented as Pydantic enums. The substrate is
BUILT. The remaining work is wiring + computed annotations + identity tuple.

---

## 9. The Forge Plan — Phased Wiring

| Phase | What | Auto/888 |
|-------|------|----------|
| 0 | This doctrine link | AUTO ✅ |
| 1a | Fix `schema_echo_stable` | AUTO |
| 1b | Fix `vault_replay` | AUTO |
| 2 | MCP annotations COMPUTED from action_class | AUTO |
| 3 | `arif_actor_resolve` tool | AUTO |
| 4 | Judge degraded-dominance wiring | AUTO |
| 5 | Vault degraded-dominance wiring | AUTO |
| 6 | ConstitutionIdentity + EvidenceReceipt Pydantic | AUTO |
| 7 | Honest tool registry (19+34=53 declared) | AUTO |
| 8 | AR-QOCF rubric live in kernel | AUTO |
| 9 | Memory atoms as constitutional state | AUTO |
| 10 | arif_actor_resolve enforcement tightening | AUTO |
| 11 | 888_HOLD items: constitution migration ledger, cross-organ Reality Engineering | **888** |

---

## 10. The Receipt

**Forged:** 2026-06-21 by FORGE (000Ω)
**Files read:** `/root/forge_work/agi-substrate-blueprint-2026-06-21.md`,
`/root/forge_work/2026-06-17-reality-engineering-spec.md`,
`/root/forge_work/2026-06-21-conformance-fix-receipt.md`,
`/root/.agents/skills/arifos-agent-doctrine/SKILL.md`,
`/root/AGENTS.md`, `/root/arifOS/AGENTS.md`, `/root/arifOS/arifosmcp/AGENTS.md`
**Files referenced:** `federation_envelope.py` (624 lines), `capability_surface.py`
(144 lines), `tools.py` (15.3K+ lines, partial)
**Files written:** `/root/arifOS/GENESIS/030_AGI_TOOL_CONTRACT_v0.1.md` (this file)
**Mutations to source code:** 0 (doctrine only — Phase 1a + 1b edits are STAGED, not deployed)
**Action class:** T1 (autonomous design forge)
**Next action:** Continue Phase 2 (annotations derived) + Phase 3 (arif_actor_resolve)
locally. Batch all edits. Single 888_HOLD request for production deploy.

---

## DITEMPA BUKAN DIBERI

**Forged by:** FORGE (000Ω) on 2026-06-21
**Sources:** Opus 4.8 substrate analysis, ChatGPT Filesystem/Fetch/Memory patterns,
Reality Engineering spec 2026-06-17, FederationEnvelope v2.0, CapabilitySurface,
arifos-agent-doctrine skill, Saltzer & Schroeder 1975 (provenance table)
**Status:** v0.1 DRAFT — cross-reference for AGI substrate readiness

The substrate is forged, not given. The doctrine is portable. The wiring continues.
