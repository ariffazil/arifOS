# AGENTS BRIDGE — Mind-Body Sync

**Version:** 2026.03.13-FORGED  
**Purpose:** Canonical bridge between arifOS Mind (Theory) and Body (Runtime)

---

## The Duality

```
┌─────────────────────────────────────────────────────────────────┐
│                        arifOS SYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  🧠 THE MIND                    💪 THE BODY                      │
│  C:\arifOS\AGENTS\             C:\arifosmcp\AGENTS\              │
│                                                                   │
│  ├── EUREKA_COMPENDIUM.md      ├── README.md                     │
│  ├── A000_HUB.md               ├── agent-identity.yaml           │
│  ├── A100_ARCHITECT.md         ├── memory-ledger.yaml            │
│  ├── A110_CANON.md             ├── event-bus.yaml                │
│  ├── A120_TOPOGRAPHY.md        ├── capability-manifest.yaml      │
│  ├── A200_ENGINEER.md          ├── execution_controller.py       │
│  ├── A300_STATE.md             ├── forensic-replay.yaml          │
│  ├── A400_SUPERPOWERS.md       ├── AGENTS.md                     │
│  ├── A801_GEMINI.md            ├── control-plane-diagram.mmd     │
│  └── A803_KIMI.md              └── example-usage.py              │
│                                                                   │
│  [Theory/Reference]            [Runtime/Execution]                │
│  - Constitutional law          - Agent control plane              │
│  - Trinity architecture        - Identity + policy                │
│  - 13 Floors (F1-F13)          - Execution receipts               │
│  - Metabolic loop (000-999)    - Quarantined paths                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ AKI Bridge
                              │ (Arif Kernel Interface)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    L3 CIVILIZATION (Execution)                   │
│         Shell, Files, Docker, APIs, External Systems             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Mapping: Mind → Body

| Mind Concept (arifOS) | Body Implementation (arifosmcp) |
|----------------------|--------------------------------|
| **Trinity (ΔΩΨ)** | **4 Agent Roles** |
| AGI Mind (Δ) | A-ARCHITECT (design) |
| ASI Heart (Ω) | A-ENGINEER (execute) |
| APEX Soul (Ψ) | A-AUDITOR + A-VALIDATOR (judge) |
| **13 Floors** | **Policy Enforcement** |
| F1 Amanah | `reversible` flag in receipts |
| F2 Truth | `evidence_required` check |
| F3 Tri-Witness | `witness_count >= 3` for deploy |
| F4 Clarity | `delta_s <= 0` validation |
| F6 Empathy | Error handling in controller |
| F7 Humility | `uncertainty_bound` field |
| F8 Genius | `G_score >= 0.80` check |
| F9 Anti-Hantu | `no_consciousness_claim` audit |
| F11 Authority | `identity_verified` gate |
| F13 Sovereign | `human_approval_required` |
| **Metabolic Loop** | **Execution Flow** |
| 000 INIT | `ExecutionController.__init__` |
| 111-333 MIND | Agent identity + capability check |
| 555-666 HEART | Policy validation |
| 777 FORGE | Receipt generation |
| 888 JUDGE | Verdict: SEAL/VOID/HOLD |
| 999 SEAL | VAULT999 commit |
| **Body-Mind Duality** | **Directory Structure** |
| C:\arifOS\ (Mind) | Theory, canon, reference |
| C:\arifosmcp\ (Body) | Runtime, execution, state |
| **AKI Airlock** | **Hard Boundaries** |
| No L3 without contract | `tools_forbidden` list |
| Zero transport deps in core | `execution_controller.py` in AGENTS/ |

---

## The 4 Agents: Full Specification

| Agent | Mind Role | Body Role | Trinity | Permissions |
|-------|-----------|-----------|---------|-------------|
| **A-ARCHITECT** | Δ Designer | Design Authority | AGI (Δ) | READ, PLAN |
| **A-ENGINEER** | Ω Executor | Execution Authority | ASI (Ω) | READ, EDIT (approved) |
| **A-AUDITOR** | Ψ Judge | Judgment Authority | APEX (Ψ) | READ, REVIEW, VOID |
| **A-VALIDATOR** | Ψ Sealer | Final Verification | APEX (Ψ) | READ, EDIT (rollback), DEPLOY, SEAL |

### Hard Separation Matrix

| Action | A-ARCHITECT | A-ENGINEER | A-AUDITOR | A-VALIDATOR |
|--------|:-----------:|:----------:|:---------:|:-----------:|
| **read_file** | ✅ | ✅ | ✅ | ✅ |
| **write_file** | ❌ | ✅ (Δ approved) | ❌ | ✅ (rollback) |
| **file_delete** | ❌ | ❌ | ❌ | ✅ (rollback only) |
| **docker_deploy** | ❌ | ❌ | ❌ | ✅ (888_HOLD) |
| **issue_VOID** | ❌ | ❌ | ✅ | ✅ |
| **issue_SEAL** | ❌ | ❌ | ❌ | ✅ |

---

## 6 Blindspots → 6 Fixes

| Blindspot | Mind File | Body File | Fix |
|-----------|-----------|-----------|-----|
| Agent Identity | A110_CANON.md | agent-identity.yaml | UUID-based identity |
| Unified Memory | A300_STATE.md | memory-ledger.yaml | Canonical spine |
| Event Orchestration | A400_SUPERPOWERS.md | event-bus.yaml | Event-driven agents |
| Self-Knowledge | A803_KIMI.md | capability-manifest.yaml | Agents read own manifest |
| Broken Paths | A120_TOPOGRAPHY.md | execution_controller.py | Quarantine DISABLED paths |
| Forensic Replay | A100_ARCHITECT.md | forensic-replay.yaml | Immutable replay chain |

---

## Quarantined Paths (Blindspot #5)

The following paths are **explicitly DISABLED** in the Body:

```yaml
kimi_inside_openclaw:
  status: QUARANTINED
  reason: Psychological surface > real surface
  risk: False confidence

aider_inside_openclaw:
  status: QUARANTINED
  reason: Psychological surface > real surface
  risk: False confidence

opencode_inside_openclaw:
  status: QUARANTINED
  reason: Psychological surface > real surface
  risk: False confidence
```

**Mind Rule:** These appear in capability manifests but are flagged as non-functional.  
**Body Rule:** Execution controller will VOID any attempt to use these.

---

## Execution Receipt (VAULT999 Bridge)

Every action generates a receipt that bridges Mind and Body:

```yaml
receipt:
  id: uuid                    # Body: unique execution ID
  agent: A-ENGINEER           # Body: runtime agent
  mind_role: Ω                # Mind: Trinity role
  intent: "Fix auth bug"      # Body: natural language
  tools_used: [read, edit]    # Body: tool chain
  files: [auth.py]            # Body: affected paths
  
  # Constitutional validation
  verdict: SEAL|VOID|HOLD     # Mind: APEX judgment
  floors_checked: [F1,F2,F4]  # Mind: which floors passed
  human_approval: REQUIRED    # Mind: F13 check
  
  # Cryptographic binding
  merkle_hash: sha256(...)    # Body: integrity proof
  vault_seal: true|false      # Body: committed to VAULT999
  timestamp: ISO8601          # Body: when executed
```

---

## Usage Patterns

### Pattern 1: Invoke Agent

```python
# Body-level invocation
from AGENTS.execution_controller import ExecutionController, AgentRole

controller = ExecutionController()
receipt = controller.execute(
    agent_role=AgentRole.ENGINEER,
    intent="Refactor auth module",
    tools=["read_file", "edit_file"],
    files=["auth.py"],
    dry_run=True,  # F1: Reversibility
)

print(receipt.verdict)  # Mind: SEAL or VOID
```

### Pattern 2: Bridge Workflow

```
Mind (arifOS)                      Body (arifosmcp)
─────────────────────────────────────────────────────────
1. Read EUREKA_COMPENDIUM    →   2. Load capability-manifest
3. Verify Trinity alignment  →   4. Check agent-identity
5. Confirm 13 Floors         →   6. Validate execution
7. Issue SEAL verdict        →   8. Generate receipt
9. Update canon              →   10. Commit to VAULT999
```

---

## Constitutional Compliance Matrix

| Floor | Mind Check | Body Enforcement |
|-------|------------|------------------|
| F1 | Theory: reversibility | Code: `dry_run` flag, backups |
| F2 | Theory: evidence | Code: `evidence_required` |
| F3 | Theory: consensus | Code: `witness_count >= 3` |
| F4 | Theory: ΔS ≤ 0 | Code: `complexity_score` |
| F6 | Theory: empathy | Code: graceful error handling |
| F7 | Theory: humility | Code: `uncertainty_bound` |
| F8 | Theory: G ≥ 0.80 | Code: `G_score` validation |
| F9 | Theory: anti-hantu | Code: `no_consciousness_claim` |
| F11 | Theory: authority | Code: `identity_verified` |
| F13 | Theory: sovereign | Code: `human_approval_required` |

---

## First Action Rule (Unified)

When entering the arifOS system:

```
1. Read C:\arifOS\AGENTS\EUREKA_COMPENDIUM.md      (Mind)
2. Read C:\arifosmcp\AGENTS\README.md              (Body)
3. Run C:\arifosmcp\AGENTS\example-usage.py        (Test)
4. Load C:\arifosmcp\AGENTS\capability-manifest.yaml (Self-knowledge)
5. Verify C:\arifosmcp\AGENTS\agent-identity.yaml   (Identity)
6. Only then: Modify code in C:\arifosmcp\          (Execute)
```

---

## File Locations Summary

| Purpose | Mind Path | Body Path |
|---------|-----------|-----------|
| **Entry Point** | `EUREKA_COMPENDIUM.md` | `README.md` |
| **Architecture** | `A100_ARCHITECT.md` | `control-plane-diagram.mmd` |
| **Agent Specs** | `A000_HUB.md` | `AGENTS.md` |
| **Runtime** | Theory only | `execution_controller.py` |
| **Identity** | Theory (F11) | `agent-identity.yaml` |
| **Memory** | Theory (VAULT999) | `memory-ledger.yaml` |
| **Events** | Theory (A400) | `event-bus.yaml` |
| **Forensics** | Theory (000-999) | `forensic-replay.yaml` |

---

## Test the Bridge

```bash
cd C:\arifosmcp\AGENTS
python example-usage.py
```

Expected output:
- ✅ Agent identity verified
- ✅ Policy enforcement working
- ✅ Quarantined paths disabled
- ✅ Execution receipts generated
- ✅ Hard separation matrix enforced

---

**DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]**

*Mind-Body Bridge: Canonical sync between Theory (C:\arifOS) and Runtime (C:\arifosmcp)*
