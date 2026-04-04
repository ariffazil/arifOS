# arifOS Constitutional Agent System

**Version:** 2026.03.13-FORGED  
**Classification:** TRINITY SEALED — Hardened Control Plane  
**Authority:** 888_JUDGE — Muhammad Arif bin Fazil  
**Motto:** *Ditempa Bukan Diberi — Forged, Not Given*

---

## Start Here

| File | Purpose |
|------|---------|
| `agent-identity.yaml` | Per-agent identity + policy bindings (Blindspot #1) |
| `memory-ledger.yaml` | Unified canonical memory spine (Blindspot #2) |
| `event-bus.yaml` | Event-driven orchestration (Blindspot #3) |
| `capability-manifest.yaml` | Self-knowledge system (Blindspot #4) |
| `execution-controller.py` | Governed execution layer (Blindspot #1 + #5) |
| `forensic-replay.yaml` | Operational replay system (Blindspot #6) |
| `system-prompts.yaml` | Constitutional system prompts for all 4 agents |
| `skills.yaml` | Reusable skill definitions (I/O schemas) |
| `accountability-matrix.yaml` | RACI accountability + KPIs |
| `AGENTS.md` | 4 agent specs (ARCHITECT, ENGINEER, AUDITOR, VALIDATOR) |
| `control-plane-diagram.mmd` | Architecture diagram (Mermaid) |
| `example-usage.py` | Runnable demonstration |
| `README.md` | This file |

**Total: 13 files — complete constitutional control plane.**

---

## Architectural Context: MIND + BODY

This folder (`arifosmcp/AGENTS/`) is **THE BODY** — the operational control plane.

For **THE MIND** — architectural doctrine and theoretical foundation — see:
- **[EUREKA_COMPENDIUM.md](/arifOS/AGENTS/EUREKA_COMPENDIUM.md)** — TCP analogy, Trinity ΔΩΨ, 13 Floors, Genius Equation
- **Source documents:** `A000_HUB.md`, `A100_ARCHITECT.md`, `A110_CANON.md`, etc.

### Doctrine → Runtime Mapping

| Doctrine (THE MIND) | Runtime (THE BODY) |
|---------------------|-------------------|
| TCP for AI (governance over MCP) | `execution-controller.py` — Policy-gated enforcement |
| Trinity ΔΩΨ (AGI/ASI/APEX) | `agent-identity.yaml` — 4 agent roles with ΔΩΨ bindings |
| 13 Constitutional Floors F1-F13 | `execution-controller.py` — Floor threshold enforcement |
| 888_HOLD veto mechanism | `agent-identity.yaml` — Human approval requirements per agent |
| Unified Memory Spine | `memory-ledger.yaml` — Canonical observations, tasks, deployments |
| Event-Driven Architecture | `event-bus.yaml` — Git, container, health, Telegram triggers |
| Capability Self-Knowledge | `capability-manifest.yaml` — Agent self-description system |
| Immutable Forensic Replay | `forensic-replay.yaml` — Trainable reflection system |
| Non-Learning APEX (Ψ) | Hard-coded thresholds in `execution-controller.py` |
| Amanah (F1 Reversibility) | Hard separation: READ → EDIT → DEPLOY → DESTROY |

**Together:** `arifOS/AGENTS/` (doctrine) + `arifosmcp/AGENTS/` (runtime) = **Complete constitutional stack**

---

## The 6 Blindspots Addressed

This system fixes the 6 critical gaps identified in the APEX assessment:

### 1. Agent Identity + Policy-Gated Execution ✅
- **File:** `agent-identity.yaml`, `execution-controller.py`
- **Fix:** Every agent has explicit identity, capability class, and tool permissions
- **Hard separation:** READ → EDIT → DEPLOY → DESTROY strictly enforced

### 2. Unified Memory Ledger ✅
- **File:** `memory-ledger.yaml`
- **Fix:** Single canonical spine for all agent observations, tasks, tool outcomes, deployments, human approvals
- **Result:** Compounding intelligence instead of fragmented state

### 3. Event-Driven Orchestration ✅
- **File:** `event-bus.yaml`
- **Fix:** Agents react to git drift, container events, health degradation, provider failures, resource pressure, Telegram commands
- **Result:** VPS becomes living operating substrate, not just toolbox

### 4. Capability Self-Knowledge ✅
- **File:** `capability-manifest.yaml`
- **Fix:** Each agent reads its own manifest before acting — knows what tools exist, what's broken, what credentials exist, what's writable
- **Result:** No more guessing their own body

### 5. Broken Power Paths Quarantined ✅
- **File:** `agent-identity.yaml` (quarantined section), `execution-controller.py`
- **Fix:** `kimi_inside_openclaw`, `aider_inside_openclaw`, `opencode_inside_openclaw` explicitly DISABLED
- **Result:** Capability surface matches real surface — no false confidence

### 6. Immutable Operational Replay ✅
- **File:** `forensic-replay.yaml`
- **Fix:** Complete forensic lane: prompt input → tool chain → file diffs → command outputs → final decision
- **Result:** System becomes trainable by reflection

---

## The 4 Agents

| Agent | Symbol | Trinity | Role | Capability Class |
|-------|--------|---------|------|------------------|
| **A-ARCHITECT** | 🏛️ | Δ | Design Authority | READ-PLAN |
| **A-ENGINEER** | ⚙️ | Ω | Execution Authority | EDIT-WRITE |
| **A-AUDITOR** | 🔍 | Ψ | Judgment Authority | READ-REVIEW |
| **A-VALIDATOR** | ✓ | Ψ | Final Verification | DEPLOY-SEAL |

### Hard Separation Matrix

| Action | A-ARCHITECT | A-ENGINEER | A-AUDITOR | A-VALIDATOR |
|--------|-------------|------------|-----------|-------------|
| READ | ✅ | ✅ | ✅ | ✅ |
| EDIT | ❌ | ✅ (approved) | ❌ | ✅ (rollback) |
| DELETE | ❌ | ❌ | ❌ | ✅ (rollback) |
| DEPLOY | ❌ | ❌ | ❌ | ✅ (approved) |
| VOID | ❌ | ❌ | ✅ | ✅ |
| SEAL | ❌ | ❌ | ❌ | ✅ |

---

## Quick Start

### 1. Check Agent Identity

```python
from AGENTS.execution_controller import ExecutionController, AgentRole

controller = ExecutionController()
architect = controller.get_agent_identity(AgentRole.ARCHITECT)

print(f"Tools allowed: {architect.tools_allowed}")
print(f"Tools forbidden: {architect.tools_forbidden}")
```

### 2. Validate Execution

```python
receipt = controller.execute(
    agent_role=AgentRole.ENGINEER,
    intent="Fix bug in auth module",
    tools=["read_file", "edit_file"],
    files=["auth.py"],
    dry_run=True,
)

print(receipt.verdict)  # SEAL or VOID
print(receipt.human_approval)  # REQUIRED or NOT_REQUIRED
```

### 3. Check Quarantined Paths

```python
quarantined = controller.list_quarantined()
for path, info in quarantined.items():
    print(f"{path}: {info['status']} - {info['reason']}")
```

---

## Invocation

```
@a-architect [design task]
@a-engineer [implementation task]
@a-auditor [review task]
@a-validator [validation task]
```

---

## Constitutional Compliance

All agents operate under **arifOS Constitutional Law (F1-F13)**:

| Floor | Agent Application |
|-------|-------------------|
| F1 | Every action reversible or auditable |
| F2 | Agent reasoning grounded in evidence |
| F3 | Critical decisions: Tri-Witness ≥0.95 |
| F4 | Agent outputs clear (ΔS ≤ 0) |
| F6 | Error handling graceful |
| F7 | Agents know their limits |
| F8 | Genius G ≥ 0.80 for all outputs |
| F9 | No dark patterns (C_dark < 0.30) |
| F11 | Identity verified for all writes |
| F13 | Human approval for deploy/destroy |

---

## Directory Structure

```
AGENTS/
├── README.md                      # This file
├── agent-identity.yaml           # Identity + policy registry
├── memory-ledger.yaml            # Unified memory spine
├── event-bus.yaml                # Event-driven orchestration
├── capability-manifest.yaml      # Self-knowledge system
├── execution-controller.py       # Runtime enforcement
├── forensic-replay.yaml          # Operational replay
├── A-ARCHITECT.md               # Design authority spec
├── A-ENGINEER.md                # Execution authority spec
├── A-AUDITOR.md                 # Judgment authority spec
└── A-VALIDATOR.md               # Final verification spec

10 files total.
```

---

## References

- [arifOS Constitutional Floors F1-F13](/core/shared/floors.py)
- [Trinity Architecture (ΔΩΨ)](/docs/AAA_TRINITY_MAPPING.md)
- [Execution Controller](/AGENTS/execution-controller.py)

---

**SEAL:** This agent system is TRINITY SEALED under arifOS Constitutional Law v2026.03.13.

*Ditempa Bukan Diberi — Forged, Not Given*
