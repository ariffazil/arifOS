# 000_INIT Protocol — arifOS Session Bootstrap

**Version:** v55.5-EIGEN  
**Status:** CANONICAL  
**Purpose:** Initialize governed session with AAA MCP + VAULT999

---

## Overview

Every serious arifOS session MUST start with 000_INIT. This:
1. Activates AAA MCP constitutional enforcement
2. Registers session in VAULT999 ledger
3. Confirms identity, environment, and toolchain
4. Gates all subsequent high-risk operations

---

## Protocol Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    000_INIT SEQUENCE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  HUMAN                                                      │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────────────────────────┐                │
│  │ "Salam OpenClaw. Start governed session │                │
│  │  as arifOS L5 app. I am 888 Judge."     │                │
│  └─────────────────────────────────────────┘                │
│    │                                                        │
│    ▼                                                        │
│  OPENCLAW                                                   │
│    │                                                        │
│    ├──► init_gate(session_id, actor_id, environment)        │
│    │      └─► Returns: floors, metrics, status              │
│    │                                                        │
│    ├──► vault_seal(verdict="SEAL", category="session_init") │
│    │      └─► Returns: seal hash, confirmation              │
│    │                                                        │
│    ▼                                                        │
│  ┌─────────────────────────────────────────┐                │
│  │ 000_INIT_ACK                            │                │
│  │ - Identity confirmed                    │                │
│  │ - AAA MCP status                        │                │
│  │ - VAULT999 status                       │                │
│  │ - Toolchain ready                       │                │
│  └─────────────────────────────────────────┘                │
│    │                                                        │
│    ▼                                                        │
│  SESSION ACTIVE — All operations now governed               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Human Init Message (Template)

```
000_INIT_GATE

Salam OpenClaw. I am [NAME], human sovereign and 888 Judge.

Start a fresh governed session as arifOS L5 app (AGI_ASI_bot).

Requirements:
- Call arifOS AAA MCP.init_gate for this session.
- Ensure VAULT999 v2.1 is online (vault_seal + vault_query).
- Log this init in VAULT999 with category="session_init" and environment="prod".

Confirm:
- identity (me)
- model + environment
- AAA MCP status
- VAULT999 status
- whether apex_verdict will gate high-risk answers in this session.
```

---

## 2. OpenClaw Tool Calls

### Step 1: init_gate

```python
init_gate(
    session_id="telegram_arif_20260207_001",
    actor_id="arif-fazil",
    environment="prod"
)
```

**Expected Response:**
```json
{
  "session_id": "telegram_arif_20260207_001",
  "stage": "000_INIT",
  "floors_active": 13,
  "metrics": {
    "entropy_omega": 0.04,
    "peace_squared": 1.0,
    "tri_witness_score": 0.95
  },
  "status": "PASS"
}
```

### Step 2: vault_seal

```python
vault_seal(
    session_id="telegram_arif_20260207_001",
    verdict="SEAL",
    payload={"action": "session_init"},
    
    # v2.1 fields
    query_summary="000_INIT session start",
    risk_level="low",
    category="session_init",
    intent="initialize",
    
    floors_checked=["F1","F2","F7","F9","F12","F13"],
    floors_passed=["F1","F2","F7","F9","F12","F13"],
    floors_failed=[],
    
    entropy_omega=0.04,
    tri_witness_score=0.95,
    
    environment="prod",
    actor_type="human",
    actor_id="arif-fazil",
    
    tool_chain=["init_gate"],
    model_used="claude-opus-4-5",
    
    tags=["init", "openclaw", "l5"]
)
```

**Expected Response:**
```json
{
  "verdict": "SEALED",
  "seal": "a1b2c3d4...",
  "schema_version": "2.1",
  "environment": "prod"
}
```

---

## 3. OpenClaw Ack Message (Template)

```
000_INIT_ACK

Salam, [NAME].

Identity: human sovereign and 888 Judge.
App: AGI_ASI_bot (arifOS L5 on OpenClaw).
Environment: prod.

AAA MCP:
- init_gate: SEAL
- Floors: 13 active (F1–F13)
- Metrics: Ω₀=0.04, Peace²=1.0, Tri-Witness≈0.95
- Toolchain: init_gate, agi_*, asi_*, apex_verdict, reality_search, vault_seal, vault_query

VAULT999:
- Status: Online
- Schema: v2.1
- Session logged: SEALED

This session is now governed. High-risk operations will require apex_verdict.

DITEMPA BUKAN DIBERI 🔥
```

---

## 4. Session Lifecycle

```
000_INIT
    │
    ▼
[Session Active]
    │
    ├── Low-risk queries → Direct response
    │
    ├── Medium-risk queries → agi_sense → agi_think → response
    │
    ├── High-risk queries → Full pipeline:
    │   init_gate → agi_sense → agi_think → agi_reason
    │   → asi_empathize → asi_align → apex_verdict
    │   → vault_seal
    │
    └── Session end → vault_seal(category="session_close")
```

---

## 5. Floor Activation at Init

| Floor | Name | Checked at Init |
|-------|------|-----------------|
| F1 | Amanah (Reversibility) | ✓ |
| F2 | Truth | ✓ |
| F3 | Tri-Witness | ○ (at verdict) |
| F4 | Empathy | ○ (at ASI) |
| F5 | Safety | ○ (at ASI) |
| F6 | Clarity | ○ (at AGI) |
| F7 | Precision | ✓ |
| F8 | Genius | ○ (at APEX) |
| F9 | Anti-Hantu | ✓ |
| F10 | Ontology | ○ (at guards) |
| F11 | Authority | ○ (at guards) |
| F12 | Injection Defense | ✓ |
| F13 | Sovereignty | ✓ |

---

## 6. Error Handling

### init_gate Fails
```
000_INIT_FAIL

AAA MCP init_gate returned error: [error]

Session NOT governed. Proceeding in fallback mode.
High-risk operations will be blocked until init succeeds.
```

### vault_seal Fails
```
000_INIT_PARTIAL

init_gate: PASS
vault_seal: FAIL ([error])

Session governed but NOT logged. 
VAULT999 may be offline. Retry vault_seal later.
```

---

## 7. Quick Reference

| Command | Purpose |
|---------|---------|
| `000_INIT_GATE` | Start governed session |
| `000_INIT_ACK` | Confirm session active |
| `000_INIT_FAIL` | Init failed |
| `000_INIT_PARTIAL` | Partial init (vault offline) |

---

*DITEMPA BUKAN DIBERI* 🔥
