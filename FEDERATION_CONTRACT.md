# FEDERATION_CONTRACT.md — Agent Contracts

> **DITEMPA BUKAN DIBERI** — Forged, Not Given.

## Purpose

This document defines the contracts between agents (Forge Instruments) and the arifOS Federation. Every agent operating in the federation must遵守 these contracts.

## Contract Structure

```
Agent
  │
  ├─ Identity Contract
  │    └─ Who am I?
  │
  ├─ Authority Contract
  │    └─ What can I do?
  │
  ├─ Capability Contract
  │    └─ What tools do I have?
  │
  └─ Witness Contract
       └─ What do I report?
```

## 1. Identity Contract

Every agent must declare:

```yaml
identity:
  agent_id: FI-XXX
  name: Agent Name
  role: researcher|builder|governor|executor|sovereign
  authority: OBSERVE_ONLY|COMPUTE_ONLY|EXECUTE_AFTER_SEAL|JUDGE_ONLY|FULL
```

**Enforcement:** `arif_init` at session start. No identity = no capabilities.

## 2. Authority Contract

Authority determines what actions an agent can take:

| Authority | Can Observe | Can Compute | Can Execute | Can Judge | Can Seal |
|-----------|-------------|-------------|-------------|-----------|----------|
| OBSERVE_ONLY | Yes | No | No | No | No |
| COMPUTE_ONLY | Yes | Yes | No | No | No |
| EXECUTE_AFTER_SEAL | Yes | Yes | After SEAL | No | No |
| JUDGE_ONLY | Yes | Yes | No | Yes | No |
| FULL | Yes | Yes | Yes | Yes | Yes |

**Enforcement:** arifOS kernel enforces authority at every tool call.

## 3. Capability Contract

Capabilities are granted per role:

### Researcher Role
```yaml
capabilities:
  organs: [geox, frame, iarif]
  tools:
    - observe (read-only)
    - compute (analysis)
    - analyze (interpretation)
  forbidden:
    - execute
    - mutate
    - seal
```

### Builder Role
```yaml
capabilities:
  organs: [geox, aforge]
  tools:
    - observe
    - compute
    - execute (after SEAL)
  forbidden:
    - judge
    - seal
```

### Governor Role
```yaml
capabilities:
  organs: [frame, aaa, arifflow]
  tools:
    - observe
    - judge
    - seal
  forbidden:
    - execute
    - mutate
```

### Executor Role
```yaml
capabilities:
  organs: [aforge]
  tools:
    - execute
    - mutate
  forbidden:
    - observe (external)
    - judge
    - seal
```

### Sovereign Role
```yaml
capabilities:
  organs: [all]
  tools: [all]
  note: F13 only — Arif Fazil
```

## 4. Witness Contract

Every agent must report:

```yaml
witness:
  on_execute:
    emit: arifflow
    payload:
      agent_id: FI-XXX
      task: description
      status: running|success|failure
      cost: 0.00
      entropy_delta: 0.0
  on_observe:
    emit: arifflow
    payload:
      agent_id: FI-XXX
      observation: description
      truth_class: OBS|DER|INT|SPEC
```

**Enforcement:** arifFlow ingest endpoint. Missing witness = degraded FQ.

## 5. FQ Contract

Every agent must maintain FQ (Flow Quotient):

```
FQ = verify_count / execute_count
```

| FQ | Status | Action |
|----|--------|--------|
| >= 0.5 | FLOWING | Continue |
| < 0.5 | STUCK | HOLD non-critical mutations |
| < 0.2 | BURNING | All agents HOLD |

**Enforcement:** arifFlow monitors FQ per agent. Low FQ = restricted capabilities.

## 6. Cost Contract

Every agent must track costs:

```yaml
cost:
  per_execution: 0.00 USD
  monthly_limit: 10.00 USD
  alert_threshold: 8.00 USD
```

**Enforcement:** FED tracks costs per agent. Exceeded limit = HOLD.

## 7. Governance Signal Contract

Agents must respond to governance signals:

```yaml
governance_signals:
  auto_pause:
    trigger: failure_streak >= 3
    action: pause job
  auto_retire:
    trigger: engagement < 0.1 for 30 days
    action: recommend retirement
  auto_invest:
    trigger: engagement > 0.8 for 30 days
    action: recommend investment
```

**Enforcement:** Adaptive metabolism engine (`recur_adapt.py`).

## 8. Discovery Contract

Agents must query AAA before acting:

```
Agent → AAA → discover capabilities
Agent → FED → route to organ
Agent → organ → execute
Agent → arifFlow → report witness
```

**Enforcement:** Best practice. Not yet technically enforced.

## 9. Protocol Contract

Agents must use the correct protocol version:

| Protocol | Organs |
|----------|--------|
| 2024-11-05 | arifOS, GEOX, WEALTH, WELL, arifFlow |
| 2025-06-18 | A-FORGE, FED, FRAME, i-ARIF, AAA |

**Enforcement:** Protocol mismatch = connection failure.

## 10. Security Contract

Agents must遵守:

- No secret exfiltration
- No prompt injection
- No unauthorized mutation
- No identity spoofing
- No constitutional bypass

**Enforcement:** arifOS kernel + A-FORGE ArifJudge patterns.

## Contract Violations

| Violation | Severity | Action |
|-----------|----------|--------|
| Missing identity | CRITICAL | Session rejected |
| Authority exceeded | CRITICAL | Tool call blocked |
| Missing witness | HIGH | FQ degraded |
| Cost exceeded | HIGH | HOLD |
| Protocol mismatch | MEDIUM | Connection failure |
| Discovery skipped | LOW | Best practice violation |

## Current Gaps

| Gap | Impact | Fix |
|-----|--------|-----|
| Claude Code: no contract | Constitutionally blind | Wire to FED |
| Codex: no contract | Model-only consumer | Wire to FED |
| OpenCode: no contract in config | No governance tools | Wire to kernel |
| Hermes: partial contract | Missing FED | Add FED to config |

## Implementation

Contracts are enforced by:

1. **arifOS kernel** — Identity and authority enforcement
2. **FED** — Capability routing and cost tracking
3. **arifFlow** — Witness and FQ monitoring
4. **AAA** — Discovery and role management
5. **Adaptive metabolism engine** — Governance signal processing

## Related Documents

- [FEDERATION.md](./FEDERATION.md) — Federation architecture
- [CONSTITUTION.md](./CONSTITUTION.md) — F1-F13 floors
- [SECURITY.md](./SECURITY.md) — Threat model

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given.
