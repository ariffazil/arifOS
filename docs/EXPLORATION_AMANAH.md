# EXPLORATION×AMANAH — APEX Dimension: Safe Exploration Under Custody

**Version:** v2026.06.20
**SEAL:** DITEMPA BUKAN DIBERI
**Authority:** F13 SOVEREIGN — Muhammad Arif bin Fazil
**Status:** LIFTED FROM KERNEL CODE (canonical, machine-checkable)

---

## 1. Definition

**EXPLORATION×AMANAH** is the constitutional guarantee that every
movement into unknown state-space is governed by moral custody,
reversibility assessment, and human veto. It is the fusion of two
principles:

- **EXPLORATION** — movement into unknown state-space. The agent must
  be able to search, hypothesize, simulate, and discover.
- **AMANAH** (Arabic/Malay: أمانة — trust, stewardship) — moral
  custody over that exploration. Every exploration carries risk, and
  every risk must be stewarded.

EXPLORATION×AMANAH answers: **"How far can the agent venture into the
unknown, under whose custody, with what reversibility, and with what
veto?"**

The rule: **Explore freely, but never without custody.** The agent can
think wild thoughts, but every action that touches the world must have
a custody chain, a reversibility assessment, and a blast radius estimate.

---

## 2. Mapping to APEX / Kernel

```
Dimension              Maps to kernel surface
─────────────────────────────────────────────
AKAL                   transition candidates + policy evaluator
PRESENT                KSR + arif_sense_observe (111)
ENERGY                 Landauer floor + cost accounting
ENTROPY                ΔS = Δ(info) + drift detection
EXPLORATION×AMANAH     risk class + custody chain + F13    ← THIS DOC
AUTHORITY              signature + role + legitimacy
```

### 2.1 EXPLORATION×AMANAH binds to:

| Surface | Role |
|---------|------|
| `ReversibilityEngine` | Classifies every tool call: TRIVIAL → REVERSIBLE → PARTIAL → IRREVERSIBLE → CRITICAL. |
| `ReversibilityClass` (enum) | 5-tier reversibility: `trivial`, `reversible`, `partial`, `irreversible`, `critical`. |
| `ActionClass` (7-tier) | `OBSERVE` → `SUGGEST` → `SIMULATE` → `DRAFT` → `QUEUE` → `EXECUTE_REVERSIBLE` → `EXECUTE_HIGH_IMPACT` → `IRREVERSIBLE`. |
| `actionClassifier.ts` | Maps tool names to action classes. Default: OBSERVE (conservative). |
| `f1Amanah.ts` | F1 floor: actor+session required, reversibility_score, blast_radius, rollback_plan. |
| `ForgeManifest.custody_chain` | Records who held action from conception to execution. `[{role, actor_id, timestamp}]`. |
| `TransitionReceipt.custody_chain` | `[initiator, validator, approver, executor]` — sealed to VAULT999. |
| `MCPGate` (mcp_gate_v0.py) | 5-phase gate: session → blocked → irreversible → simulate-first → risk-based. |
| `BlastRadius` field | `low | medium | high | critical` — estimated blast radius per tool. |
| `888_HOLD` | Mandatory hold for IRREVERSIBLE and EXECUTE_HIGH_IMPACT actions. |
| `kernel_state.py:456-545` | Custody chain on kernel transitions: `[initiator, validator, approver, executor]`. |

---

## 3. The Reversibility Engine

**Code:** `arifosmcp/core/reversibility_engine.py` (542 lines)

### 3.1 Reversibility classes

**Code:** `reversibility_engine.py:25-32`

```python
class ReversibilityClass(StrEnum):
    TRIVIAL = "trivial"        # No state change (read, search, query)
    REVERSIBLE = "reversible"  # Easily undone (write temp, create draft)
    PARTIAL = "partial"        # Undoable with effort (edit, update, patch)
    IRREVERSIBLE = "irreversible"  # Cannot be undone (delete, drop, publish)
    CRITICAL = "critical"      # Cannot be undone — catastrophic (sudo, volume delete)
```

### 3.2 Pattern-based classification

**Code:** `reversibility_engine.py:36-71`

The engine scans tool names and parameters for irreversible patterns:

```python
_IRREVERSIBLE_PATTERNS = [
    r"\bdelete\b", r"\bdrop\b", r"\bremove\b", r"\bdestroy\b",
    r"\btruncate\b", r"\berase\b", r"\brm\s", r"\brm\s+-rf\b",
    r"\bdrop\s+table\b", r"\bdelete\s+from\b",
    r"\bgit\s+push\s+.*--force\b", r"\bgit\s+reset\s+--hard\b",
    r"\bdocker\s+volume\s+rm\b", r"\bdocker\s+container\s+rm\b",
]
```

### 3.3 Reversibility → Action class mapping

**Code:** `reversibility_engine.py:522-541`

```python
rev_to_action = {
    "trivial": "OBSERVE",
    "reversible": "MUTATE",
    "partial": "MUTATE",
    "irreversible": "ATOMIC",
    "critical": "ATOMIC",
}
```

- `OBSERVE` → may proceed without plan
- `MUTATE` → requires plan
- `ATOMIC` → requires Arif approval (888_HOLD)

---

## 4. The 7-Tier Action Classifier

**Code:** `A-FORGE/src/domain/governance/actionClassifier.ts` (152 lines)

```typescript
type ActionClass =
  | "OBSERVE"              // Read-only, no side effects
  | "SUGGEST"              // Recommend, draft, propose — no commit
  | "SIMULATE"             // Dry run, forward model, preview
  | "DRAFT"                // Write unsent/composed content
  | "QUEUE"                // Schedule, defer, enqueue
  | "EXECUTE_REVERSIBLE"   // Git commit, create file, restart service
  | "EXECUTE_HIGH_IMPACT"  // Deploy, billing, data mutation
  | "IRREVERSIBLE";        // rm -rf, DROP TABLE, vault seal
```

### 4.1 Class priority (lower = more severe)

```typescript
const CLASS_PRIORITY = {
    "OBSERVE": 7, "SUGGEST": 6, "SIMULATE": 5, "DRAFT": 4,
    "QUEUE": 3, "EXECUTE_REVERSIBLE": 2, "EXECUTE_HIGH_IMPACT": 1,
    "IRREVERSIBLE": 0,
};
```

### 4.2 Governance requirements

```typescript
function requiresGovernance(actionClass): boolean {
    return actionClass !== "OBSERVE" && actionClass !== "SUGGEST";
}
function requires888Hold(actionClass): boolean {
    return actionClass === "IRREVERSIBLE" || actionClass === "EXECUTE_HIGH_IMPACT";
}
```

---

## 5. F1 AMANAH — The Floor

**Code:** `A-FORGE/src/domain/governance/f1Amanah.ts` (102 lines)

### 5.1 Five rules

| Rule | Check | Severity |
|------|-------|----------|
| R1 | Every action must declare `actor` + `session_id` | VOID if missing |
| R2 | `reversibility_score` must be in [0, 1] | VOID if out of range |
| R3 | High blast_radius + low reversibility (< 0.3) → HOLD | Requires stewardship |
| R4 | Destructive action without `rollback_plan` → HOLD | F1 + F5 pair |
| R5 | Constitutional floor change → always HOLD | Requires F13 ratification |

### 5.2 Destructive action types

```typescript
const DESTRUCTIVE_TYPES = [
    "DELETE", "VAULT_SEAL", "PRODUCTION_DEPLOY",
    "FINANCIAL_TRANSACTION", "SECRET_ROTATION",
    "CONSTITUTIONAL_FLOOR_CHANGE", "INFRASTRUCTURE_RESTART",
];
```

---

## 6. The Custody Chain

**Code:** `arifosmcp/schemas/forge.py:147-153`, `arifosmcp/schemas/transition_receipt.py:205-213`

### 6.1 ForgeManifest custody chain

```python
# APEX EXPLORATION × AMANAH: custody chain (hardened 2026-06-20)
# Records who held this action from conception to execution.
# Each entry: {"role": "initiator|validator|approver|executor", "actor_id": str, "timestamp": str}
custody_chain: list[dict[str, str]] = Field(
    default_factory=list,
    description="Custody chain: who held this action from conception to execution",
)
```

### 6.2 TransitionReceipt custody chain

```python
custody_chain: list[str] = Field(
    default_factory=list,
    description=(
        "Chain of custody: [initiator, validator, approver, executor]. "
        "Every action records who held it from conception to execution. "
        "This is how EXPLORATION × AMANAH is enforced — accountability "
        "through the full custody chain, sealed to VAULT999."
    ),
)
```

### 6.3 Kernel state custody chain

**Code:** `arifosmcp/runtime/kernel_state.py:456-545`

```python
# custody_chain: [initiator, validator, approver, executor]
custody_chain: list[str] | None = None,
```

---

## 7. The MCP Gate — 5-Phase Enforcement

**Code:** `arifosmcp/gate/mcp_gate_v0.py` (387 lines)

The gate runs 5 phases in order. Each phase can BLOCK, HOLD, or pass through.

```
Phase 1: SESSION GATE
  └── No active session + action_class not OBSERVE/SUGGEST → BLOCK
  └── "F1 AMANAH: no anonymous mutation."

Phase 2: BLOCKED TOOLS
  └── Tool in BLOCKED registry → BLOCK
  └── "F8 LAW / F9 ANTI-HANTU: constitutionally prohibited."

Phase 3: IRREVERSIBLE TOOLS
  └── Tool in IRREVERSIBLE_TOOLS → HOLD_888
  └── "F1 AMANAH + F13 SOVEREIGN: requires explicit human approval."

Phase 4: SIMULATE-FIRST GATE
  └── Tool in SIMULATE_REQUIRED + not SIMULATE/OBSERVE → SIMULATE_FIRST
  └── "F1 AMANAH: simulate before actuate."

Phase 5: RISK-BASED GATING
  └── physical_impact + EXECUTE_* → REQUIRE_APPROVAL
  └── financial_impact + EXECUTE_* → REQUIRE_APPROVAL
  └── high/critical blast_radius + not SIMULATE/OBSERVE → REQUIRE_APPROVAL
```

---

## 8. Blast Radius

**Code:** `arifosmcp/core/tool_self_model.py:145`, `arifosmcp/gate/mcp_gate_v0.py:46`

```yaml
blast_radius: low | medium | high | critical
```

| Level | Meaning | Gate behavior |
|-------|---------|---------------|
| `low` | Local state only | Pass through |
| `medium` | Session-scoped effects | Log + proceed |
| `high` | Service-scoped effects | REQUIRE_APPROVAL |
| `critical` | Federation-scoped effects | HOLD_888 |

---

## 9. Invariants (Fail-Closed)

| # | Invariant | Failure mode |
|---|-----------|--------------|
| I1 | Every action must declare `actor` + `session_id`. | Missing → VOID. No anonymous mutation. |
| I2 | IRREVERSIBLE tools → mandatory 888_HOLD. | No bypass. Human approval required. |
| I3 | `reversibility_score` must be in [0, 1]. | Out of range → VOID. |
| I4 | High blast_radius + low reversibility → HOLD. | Requires explicit stewardship. |
| I5 | Destructive action without `rollback_plan` → HOLD. | F1 + F5 pair. |
| I6 | Constitutional floor change → always HOLD. | Requires F13 ratification. |
| I7 | `custody_chain` must be non-empty for MUTATE/ATOMIC actions. | Empty chain → no accountability → HOLD. |
| I8 | SIMULATE_REQUIRED tools must be simulated before execution. | Direct execution → SIMULATE_FIRST gate fires. |
| I9 | Default action class is OBSERVE (conservative). | Unknown tool → read-only, never mutation. |
| I10 | `requires888Hold` returns true for IRREVERSIBLE and EXECUTE_HIGH_IMPACT. | These action classes cannot proceed without human verdict. |

---

## 10. Test Gates (Fail-Closed)

A deploy is BLOCKED if any of the following occurs:

- IRREVERSIBLE tool proceeds without 888_HOLD.
- Action without `actor` + `session_id` is not rejected with VOID.
- `reversibility_score` outside [0, 1] is accepted.
- High blast_radius + low reversibility does not trigger HOLD.
- Destructive action proceeds without `rollback_plan`.
- `custody_chain` is empty for MUTATE/ATOMIC actions.
- SIMULATE_REQUIRED tool executes without simulation first.
- Unknown tool is classified as something other than OBSERVE.
- `requires888Hold` returns false for IRREVERSIBLE actions.

---

## 11. Cross-references

- **APEX THEORY:** `/root/arifOS/static/arifos/theory/000/APEX_THEORY.md` — four pillars, crown equation.
- **PRESENT:** `/root/arifOS/docs/PRESENT.md` — attested live state (sibling doc).
- **ENERGY_ENTROPY:** `/root/arifOS/docs/ENERGY_ENTROPY.md` — thermodynamic cost (sibling doc).
- **AUTHORITY:** `/root/arifOS/docs/AUTHORITY.md` — legitimacy of state mutation (sibling doc).
- **AKAL:** `/root/arifOS/docs/AKAL.md` — lawful transition selection (sibling doc).
- **APEX DOSSIER:** `/root/forge_work/APEX_DOSSIER_2026-06-20.md` — dimension mapping.
- **Reversibility engine:** `/root/arifosmcp/core/reversibility_engine.py` (542 lines).
- **Action classifier:** `/root/A-FORGE/src/domain/governance/actionClassifier.ts` (152 lines).
- **F1 Amanah:** `/root/A-FORGE/src/domain/governance/f1Amanah.ts` (102 lines).
- **MCP Gate:** `/root/arifosmcp/gate/mcp_gate_v0.py` (387 lines).
- **ForgeManifest custody:** `/root/arifosmcp/schemas/forge.py:147-153`.
- **TransitionReceipt custody:** `/root/arifosmcp/schemas/transition_receipt.py:205-213`.
- **Kernel state custody:** `/root/arifosmcp/runtime/kernel_state.py:456-545`.
- **CanonicalEnvelope:** `/root/arifosmcp/transport/canonical_envelope.py:55-114`.
- **Sibling docs:** `PRESENT.md`, `ENERGY_ENTROPY.md`, `AUTHORITY.md`, `AKAL.md` (all done).

---

## 12. Versioning

- **v2026.06.20** — Initial canonical doc. Lifted from existing kernel
  code (`reversibility_engine.py` 542 lines, `actionClassifier.ts` 152
  lines, `f1Amanah.ts` 102 lines, `mcp_gate_v0.py` 387 lines,
  `schemas/forge.py:147-153`, `schemas/transition_receipt.py:205-213`,
  `runtime/kernel_state.py:456-545`, `transport/canonical_envelope.py:55-114`).
  Doctrine → code alignment. No new fields invented; existing exploration
  governance primitives documented as law.

**Tag convention:** `vYYYY.MM.DD` per federation IRON RULE.

---

**DITEMPA BUKAN DIBERI** — Exploration is forged through custody, not assumed through freedom.
