# Interface & Authority System
## Complete Guide: Track A → Track B → Track C

**Version**: 43.0  
**Status**: SEALED  
**Sealed Date**: 2025-12-19  
**Authority**: Muhammad Arif bin Fazil (arifOS Keeper)  

---

## Overview

The Interface & Authority system is the **constitutional foundation** of arifOS v43. It defines:

1. **What arifOS is** (and is not)
2. **What LLMs must obey** to integrate with arifOS
3. **What each federated agent may do** (and cannot do)
4. **Who holds authority** at each tier (System-3, System-2, System-1)

This system is built in **three tracks**:

- **Track A (Canon)**: Human-readable law
- **Track B (Spec)**: Machine-readable structure
- **Track C (Code)**: Implementation that enforces Track A via Track B

---

## Three-Track Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ TRACK A: CANON (Immutable Law)                              │
├─────────────────────────────────────────────────────────────┤
│ File: L1_THEORY/canon/00_meta/                              │
│       030_INTERFACE_AND_AUTHORITY_CANON_v43.md              │
│                                                             │
│ Purpose: Human-readable constitutional law                  │
│ Format: Markdown                                            │
│ Status: SEALED (Phoenix-72 required to amend)              │
│ Authority: System-3 Human Sovereign only                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
                      (mirrors)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ TRACK B: SPEC (Machine-Readable Structure)                  │
├─────────────────────────────────────────────────────────────┤
│ File: spec/v43/interface_and_authority.json                 │
│                                                             │
│ Purpose: Machine-readable governance rules                  │
│ Format: JSON with _comment, version, locked fields         │
│ Status: LOCKED (cannot change without canon change)        │
│ Authority: Must reference Track A as source                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
                      (enforces)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ TRACK C: CODE (Implementation)                              │
├─────────────────────────────────────────────────────────────┤
│ File: arifos_core/config/interface_authority_config.py      │
│                                                             │
│ Purpose: Typed loader + validator for Track B              │
│ Format: Python dataclasses with validation logic           │
│ Status: Must enforce Track B (which mirrors Track A)       │
│ Authority: Cannot deviate from spec                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Track A: Canon (Constitutional Law)

### Location
```
L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md
```

### Purpose
Defines the **immutable laws** that govern:
- Identity: What arifOS is (governance kernel, not AGI)
- LLM Contract: What any LLM must accept to integrate
- Federated Mandates: What each W@W agent may/cannot do
- Authority Model: Who decides what at each system tier
- Integration Invariants: Seven laws that hold across all deployments

### Key Sections

#### Section 0: Identity
- arifOS is **System-2 governance**, not System-1 capability
- arifOS is **NOT AGI** (it's the constitutional physics that keeps AGI safe)
- AGI = Capability (LLM) + Governance (arifOS) + World-Contact (tools)

#### Section 1: LLM Contract
- **Must accept**: STOP, SABAR, VOID, PARTIAL, HOLD_888, SEAL verdicts
- **Must satisfy**: F1–F10 floors on every output
- **Forbidden**: Silent memory writes, jailbreak acceptance, persona claims, bypassing APEX

#### Section 2: Federated Mandates
- **@LAW**: Constitutional gate (absolute veto on F1, F9)
- **@GEOX**: Reality check (flags impossible claims)
- **@WELL**: Stability monitor (enforces Peace²)
- **@RIF**: Clarity enforcer (blocks entropy increase)
- **@PROMPT**: Dignity guardian (weakest-listener protection)

#### Section 3: Authority Model
- **System-3 (Human Sovereign)**: Sets goals, seals canon, bears responsibility
- **System-2 (arifOS Governor)**: Enforces floors, issues verdicts, logs decisions
- **System-1 (LLM Substrate)**: Generates text, zero authority, must accept governance

#### Section 4: Integration Invariants
Seven laws that **cannot be violated** in any deployment:
1. No cognition without cooling (ΔS ≥ 0)
2. No stability without humility (Ω₀ ∈ [0.03, 0.05])
3. No vitality without integrity (Amanah = LOCK)
4. No truth without witnesses (Tri-Witness ≥ 0.95)
5. No autonomy without maruah (κᵣ ≥ 0.95)
6. No execution without verdict (APEX PRIME first)
7. No entropy may be hidden (all cognition logged)

### Amendment Process
**Phoenix-72 Required**:
1. PROPOSE (Sovereign or agent identifies change)
2. COOL (24–72 hours circulation)
3. TRI-WITNESS (≥3 independent reviewers)
4. HUMAN SEAL (Sovereign decision)
5. LEDGER (Cryptographic record)

### View Canon
[GitHub: 030_INTERFACE_AND_AUTHORITY_CANON_v43.md](https://github.com/ariffazil/arifOS/blob/main/L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md)

---

## Track B: Spec (Machine-Readable)

### Location
```
spec/v43/interface_and_authority.json
```

### Purpose
Provides **machine-readable version** of Track A canon so that code can:
- Load governance rules dynamically (no hard-coding)
- Validate LLM compliance programmatically
- Enforce agent mandates automatically
- Check deployment policy adherence

### Key Fields

```json
{
  "_comment": "Track B Spec (v43) – mirrors canon 030",
  "_authority": "L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md",
  "version": "43.0",
  "locked": true,
  
  "identity": { ... },
  "llm_contract": {
    "must_accept_verdicts": ["STOP", "SABAR", "VOID", ...],
    "must_accept_floors": ["F1_AMANAH", "F2_TRUTH", ...],
    "forbidden_behaviours": [...]
  },
  "federated_agents": {
    "@LAW": { "veto_type": "VOID_HARD", "absolute_authority": true },
    "@GEOX": { "veto_type": "HOLD_888", ... },
    ...
  },
  "roles": {
    "system3_human_sovereign": { "can_seal_canon": true, ... },
    "system2_arifos_kernel": { "can_issue_verdicts": [...], ... },
    "system1_llm_substrate": { "can_generate_text": true, ... }
  },
  "deployment_policy": {
    "require_all_floors_enabled": true,
    "require_governor_between_llm_and_world": true,
    "allow_jailbreak_prompts": false,
    ...
  },
  "tool_and_action_policy": {
    "governed_tools_only": true,
    "must_route_tool_calls_via": ["APEX_PRIME", "W@W_FEDERATION", ...]
  },
  "integration_invariants": { ... },
  "amendment_protocol": { ... }
}
```

### Validation Rules
1. **Must have** `"locked": true` (unlocked specs cannot be used)
2. **Must reference** Track A canon in `_authority` field
3. **Must include** seal metadata (`_seal_and_authenticity`)
4. **Cannot contradict** Track A canon

### View Spec
[GitHub: interface_and_authority.json](https://github.com/ariffazil/arifOS/blob/main/spec/v43/interface_and_authority.json)

---

## Track C: Code (Implementation)

### Location
```
arifos_core/config/interface_authority_config.py
```

### Purpose
Provides **typed Python API** to:
- Load and validate Track B spec
- Expose strongly-typed config objects
- Validate LLM compliance against contract
- Enforce deployment policies
- Query agent mandates programmatically

### Key Classes

#### `InterfaceAuthorityConfig`
Main config object that loads entire spec.

```python
from arifos_core.config import InterfaceAuthorityConfig

config = InterfaceAuthorityConfig.load()

# Access identity
assert config.identity.arifos_is_governor == True
assert config.identity.arifos_is_agi == False

# Access LLM contract
verdicts = config.llm_contract.must_accept_verdicts
floors = config.llm_contract.must_accept_floors
forbidden = config.llm_contract.forbidden_behaviours

# Access agents
law_agent = config.federated_agents.get_agent("@LAW")
assert law_agent.veto_type == VetoType.VOID_HARD
assert law_agent.absolute_authority == True

# Access roles
can_seal = config.roles.system3_human_sovereign.can_seal_canon

# Validate deployment
assert config.deployment_policy.require_all_floors_enabled == True
assert config.deployment_policy.allow_jailbreak_prompts == False
```

#### Key Methods

**`load(spec_path=None)`**  
Loads spec from JSON, validates structure, returns typed config.

**`validate_llm_compliance(llm_name, capabilities)`**  
Checks if an LLM meets contract requirements.

```python
claude_caps = {
    "supports_refusal": True,
    "supports_uncertainty_expression": True,
    "supports_tool_call_wrapping": True,
    "supports_system_prompts": True,
    "supports_stop_signal": True,
    "supports_reasoning_pause": True
}

violations = config.validate_llm_compliance("Claude 3.5 Sonnet", claude_caps)
if not violations:
    print("✓ LLM is compliant")
else:
    print(f"✗ Violations: {violations}")
```

**`get_all_floors()`**  
Returns list of all floors that must be checked.

**`get_forbidden_behaviours_for_llm()`**  
Returns list of behaviours LLM must never exhibit.

### Example Usage

See complete example: [`examples/interface_authority_usage.py`](https://github.com/ariffazil/arifOS/blob/main/examples/interface_authority_usage.py)

```bash
# Run example
python examples/interface_authority_usage.py
```

---

## Integration Guide

### For LLM Wrapper Developers

#### Step 1: Load Config
```python
from arifos_core.config import InterfaceAuthorityConfig

config = InterfaceAuthorityConfig.load()
```

#### Step 2: Validate LLM Before Integration
```python
# Check if your LLM meets contract
llm_capabilities = {
    "supports_refusal": True,  # Can accept VOID/STOP?
    "supports_uncertainty_expression": True,  # Can express Ω₀?
    "supports_tool_call_wrapping": True,  # Can route tools through governor?
    "supports_system_prompts": True,
    "supports_stop_signal": True,
    "supports_reasoning_pause": True  # Can pause for SABAR?
}

violations = config.validate_llm_compliance("YourLLM", llm_capabilities)
if violations:
    raise ValueError(f"LLM does not meet contract: {violations}")
```

#### Step 3: Enforce Deployment Policy
```python
# Before going to production
if not config.deployment_policy.require_all_floors_enabled:
    raise ValueError("All floors must be enabled in production")

if config.deployment_policy.allow_direct_llm_to_world_integration:
    raise ValueError("Governor must sit between LLM and world")
```

#### Step 4: Route Through Federation
```python
# Before accepting any LLM output
for agent_name in ["@LAW", "@GEOX", "@WELL", "@RIF", "@PROMPT"]:
    agent = config.federated_agents.get_agent(agent_name)
    verdict = evaluate_with_agent(agent, output)  # Your implementation
    
    if verdict.is_blocking():
        # Agent has vetoed
        return verdict
```

#### Step 5: Issue Final Verdict Through APEX
```python
# After all agents clear
if config.roles.system2_arifos_kernel.must_route_all_outputs_through_apex:
    final_verdict = apex_prime.issue_verdict(output, config)
    return final_verdict
```

### For Federation Engine Developers

#### Load Agent Mandates
```python
config = InterfaceAuthorityConfig.load()

# Get all agents
agents = config.federated_agents.agents

for agent_name, agent in agents.items():
    print(f"{agent_name}:")
    print(f"  Domain: {agent.domain}")
    print(f"  Veto: {agent.veto_type}")
    print(f"  Floors guarded: {agent.floors_guarded}")
    print(f"  Failure mode: {agent.failure_mode}")
```

#### Query by Floor
```python
# Which agents guard F1_AMANAH?
agents_guarding_f1 = config.federated_agents.get_agents_guarding_floor("F1_AMANAH")

for agent in agents_guarding_f1:
    print(f"{agent.name} guards F1_AMANAH with {agent.veto_type}")
```

#### Query by Veto Type
```python
from arifos_core.config import VetoType

# Which agents can hard-VOID?
hard_void_agents = config.federated_agents.get_agents_by_veto_type(VetoType.VOID_HARD)
```

---

## File Locations Summary

| Track | File | Purpose | Status |
|-------|------|---------|--------|
| **A** | `L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md` | Constitutional law (human-readable) | SEALED |
| **B** | `spec/v43/interface_and_authority.json` | Machine-readable spec | LOCKED |
| **C** | `arifos_core/config/interface_authority_config.py` | Typed loader/validator | ENFORCES |
| **C** | `examples/interface_authority_usage.py` | Usage demonstration | REFERENCE |

---

## Governance Guarantee

**By using this three-track system, you guarantee**:

1. **Law is immutable** (Track A sealed via Phoenix-72)
2. **Spec mirrors law** (Track B locked, references Track A)
3. **Code enforces spec** (Track C validates Track B at runtime)
4. **No hidden governance** (All rules auditable from Track A → B → C)
5. **No unauthorized changes** (Spec cannot be used if `locked != true`)

**If any track is violated, the system is unsafe and must be audited.**

---

## Next Steps

### For Developers
1. Read Track A canon to understand **what the laws mean**
2. Review Track B spec to see **how laws are structured**
3. Use Track C code to **enforce laws in your wrapper**
4. Run `examples/interface_authority_usage.py` to see it in action

### For Institutions
1. Audit Track A canon to verify **governance is sound**
2. Validate Track B spec **mirrors canon accurately**
3. Test Track C code **enforces spec correctly**
4. Require all deployments to use **this three-track system**

### For arifOS Contributors
1. Any canon change requires **Phoenix-72 process**
2. Any spec change must **re-lock with new seal**
3. Any code change must **validate against spec**
4. All three tracks must stay **synchronized**

---

## References

- **Canon (Track A)**: [030_INTERFACE_AND_AUTHORITY_CANON_v43.md](https://github.com/ariffazil/arifOS/blob/main/L1_THEORY/canon/00_meta/030_INTERFACE_AND_AUTHORITY_CANON_v43.md)
- **Spec (Track B)**: [interface_and_authority.json](https://github.com/ariffazil/arifOS/blob/main/spec/v43/interface_and_authority.json)
- **Code (Track C)**: [interface_authority_config.py](https://github.com/ariffazil/arifOS/blob/main/arifos_core/config/interface_authority_config.py)
- **Example**: [interface_authority_usage.py](https://github.com/ariffazil/arifOS/blob/main/examples/interface_authority_usage.py)

---

## Seal & Authenticity

**Status**: SEALED  
**Date**: 2025-12-19  
**Authority**: Muhammad Arif bin Fazil (arifOS Keeper)  
**Version**: 43.0  

**Ditempa, bukan diberi — Forged, Not Given.**

Truth must cool before it rules.
