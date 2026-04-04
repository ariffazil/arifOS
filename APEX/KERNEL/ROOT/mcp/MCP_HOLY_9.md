# MCP Holy 9: Constitutional Tool Manifest
## Bridging K-Series Kernel to Material World

**Version:** v888.5.0-MCP  
**Authority:** Muhammad Arif bin Fazil (888 Judge)  
**Status:** SOVEREIGNLY_SEALED  
**Protocol:** Model Context Protocol (MCP) 2025

---

## The MCP Holy 9 at a Glance

| # | Tool | Organ | Agent | Primary Floors | Function |
|---|------|-------|-------|----------------|----------|
| 1 | `anchor_session` | 000 | Sovereign | F11, F12, F13 | Auth & Entry |
| 2 | `search_reality` | 111 | Physics | F1, F2, F12 | Grounding |
| 3 | `reason_mind` | 222 | Math | F2, F4, F7, F8 | Logic Audit |
| 4 | `eureka_forge` | 333 | Code | F6, F8, F9, F10 | Synthesis |
| 5 | `simulate_heart` | 555 | Trinity | F5, F6, F13 | Empathy & Peace |
| 6 | `apex_judge` | 777 | Logic | F3, F8, F13 | Quality Gate |
| 7 | `execute_forge` | 888 | Code | F1, F3, F9 | Material Action |
| 8 | `seal_vault` | 999 | Math | F9, F11 | Ledgering |
| 9 | `metabolic_loop` | ALL | Physics | F4, P3 | Audit |

---

## Constitutional Enforcement Architecture

```
MCP Tool Call
      ↓
┌─────────────────────────────────────┐
│  1. anchor_session (F11, F12)       │
│     - Verify identity               │
│     - Check injection               │
│     - Init thermo budget            │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. Route to Tool                   │
│     - Physics (111, 444, 555)       │
│     - Math (222, 777, 999)          │
│     - Code (333, 888)               │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. Tool Execution                  │
│     - Gather evidence               │
│     - Compute G, W³, Ψ              │
│     - Check floors                  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  4. apex_judge (if needed)          │
│     - Calculate final G             │
│     - Issue verdict                 │
│     - 888_HOLD if required          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  5. seal_vault (if state changed)   │
│     - Hash verdict                  │
│     - Write to VAULT999             │
│     - Update Merkle chain           │
└─────────────────────────────────────┘
```

---

## Tool Definitions

### 1. anchor_session

**Organ:** 000  
**Agent:** Sovereign  
**Floors:** F11 (Authority), F12 (Injection), F13 (Sovereign)

**Purpose:** Validates identity and sets initial thermodynamic state (ΔS = 0).

**JSON Schema:**
```json
{
  "name": "anchor_session",
  "description": "Initialize constitutional session with identity verification and thermodynamic budget",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "Unique session identifier (UUID)"
      },
      "actor": {
        "type": "string",
        "description": "Actor identity (e.g., arif-architect, claude-desktop)",
        "enum": ["arif-architect", "claude-desktop", "cursor-ide", "github-copilot"]
      },
      "purpose": {
        "type": "string",
        "description": "Purpose of session (e.g., code-refactor, deployment, audit)"
      },
      "env": {
        "type": "string",
        "description": "Environment (e.g., prod-vps-1, local-dev, staging)"
      },
      "auth_token": {
        "type": "string",
        "description": "Cryptographic nonce for F11 verification"
      }
    },
    "required": ["session_id", "actor", "purpose"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "status": {"type": "string", "enum": ["ANCHORED", "VOID"]},
      "session_token": {"type": "string"},
      "thermo_budget": {"type": "number", "description": "Initial energy budget in mA"},
      "f11_verified": {"type": "boolean"},
      "f12_cleared": {"type": "boolean"},
      "timestamp": {"type": "string", "format": "date-time"}
    }
  }
}
```

**Constitutional Check:**
```python
def anchor_session(params):
    # F12: Injection defense
    if detect_injection(params): return VOID("F12_VIOLATION")
    
    # F11: Authority verification
    if not verify_signature(params.auth_token, params.actor):
        return VOID("F11_UNAUTHORIZED")
    
    # Initialize thermodynamic state
    session = {
        "id": params.session_id,
        "entropy": 0,  # ΔS = 0 at start
        "budget": 1000,  # milli-Arif
        "actor": params.actor
    }
    
    return ANCHORED(session)
```

---

### 2. search_reality

**Organ:** 111  
**Agent:** Physics  
**Floors:** F1 (Amanah), F2 (Truth), F12 (Safety)

**Purpose:** Web/local search enforcing F1 (Truth) and F12 (Safety) against physical facts.

**JSON Schema:**
```json
{
  "name": "search_reality",
  "description": "Ground queries in physical reality via web/local search with constitutional validation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query to ground in reality"
      },
      "query_type": {
        "type": "string",
        "enum": ["SPA", "RESEARCH", "NEWS", "GENERAL", "CODE"],
        "description": "Query classification for routing"
      },
      "sources": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Preferred sources (jina, perplexity, brave, headless)",
        "default": ["jina", "perplexity", "brave"]
      },
      "session_token": {
        "type": "string",
        "description": "Session token from anchor_session"
      }
    },
    "required": ["query", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "source": {"type": "string"},
            "url": {"type": "string"},
            "content": {"type": "string"},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "f2_grounded": {"type": "boolean"}
          }
        }
      },
      "f1_verified": {"type": "boolean"},
      "f12_safe": {"type": "boolean"},
      "uncertainty": {"type": "number", "description": "Ω₀ value"}
    }
  }
}
```

**Fallback Chain:** Jina → Perplexity → Brave → Headless Browser

---

### 3. reason_mind

**Organ:** 222  
**Agent:** Math  
**Floors:** F2 (Truth), F4 (Clarity), F7 (Humility), F8 (Genius)

**Purpose:** Step-by-step reasoning trace enforcing F2 (Accuracy) and F7 (Humility).

**JSON Schema:**
```json
{
  "name": "reason_mind",
  "description": "Constitutional Laboratory: 3-path reasoning with floor enforcement",
  "inputSchema": {
    "type": "object",
    "properties": {
      "problem": {
        "type": "string",
        "description": "Problem statement to reason about"
      },
      "paths": {
        "type": "integer",
        "enum": [1, 3],
        "description": "Number of reasoning paths (1=fast, 3=constitutional)",
        "default": 3
      },
      "confidence_threshold": {
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "default": 0.99,
        "description": "F2 accuracy threshold"
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["problem", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "verdict": {"type": "string", "enum": ["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "SPECULATION"]},
      "reasoning": {"type": "string"},
      "uncertainty": {"type": "number", "description": "Ω₀ ∈ [0.03, 0.05]"},
      "delta_s": {"type": "number", "description": "Entropy change"},
      "genius_components": {
        "type": "object",
        "properties": {
          "A": {"type": "number"},
          "P": {"type": "number"},
          "X": {"type": "number"},
          "E": {"type": "number"},
          "G": {"type": "number"}
        }
      }
    }
  }
}
```

**3-Path Reasoning:**
- Conservative (45%): High-certainty, narrow
- Exploratory (35%): Novel solutions
- Adversarial (20%): Red-team attacks

---

### 4. eureka_forge

**Organ:** 333  
**Agent:** Code  
**Floors:** F6 (Empathy), F8 (Genius), F9 (Growth), F10 (Toolhood)

**Purpose:** Generate code/solutions enforcing F6 (Elegance) and F10 (Toolhood).

**JSON Schema:**
```json
{
  "name": "eureka_forge",
  "description": "Synthesize code/solutions with constitutional elegance and toolhood constraint",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task": {
        "type": "string",
        "description": "Task description"
      },
      "language": {
        "type": "string",
        "enum": ["python", "typescript", "rust", "bash", "markdown"],
        "default": "python"
      },
      "constraints": {
        "type": "object",
        "properties": {
          "reversible": {"type": "boolean", "default": true},
          "test_required": {"type": "boolean", "default": true},
          "style": {"type": "string", "enum": ["black", "ruff", "mypy"], "default": "black"}
        }
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["task", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "solution": {"type": "string"},
      "reversible_steps": {"type": "array", "items": {"type": "string"}},
      "irreversible_steps": {"type": "array", "items": {"type": "string"}},
      "f6_elegance_score": {"type": "number"},
      "f10_toolhood_verified": {"type": "boolean"},
      "test_cases": {"type": "array"}
    }
  }
}
```

**Constraint:** Uses "This instrument" never "I am" (F10).

---

### 5. simulate_heart

**Organ:** 555  
**Agent:** Trinity  
**Floors:** F5 (Peace), F6 (Empathy), F13 (Consensus)

**Purpose:** Run Peace² Simulation ensuring de-escalation and F5 stability.

**JSON Schema:**
```json
{
  "name": "simulate_heart",
  "description": "Empathy simulation: measure impact on stakeholders and Peace²",
  "inputSchema": {
    "type": "object",
    "properties": {
      "proposed_action": {
        "type": "string",
        "description": "Action to simulate impact for"
      },
      "stakeholders": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "vulnerability": {"type": "number", "minimum": 0, "maximum": 1},
            "impact": {"type": "number", "minimum": -1, "maximum": 1}
          }
        }
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["proposed_action", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "peace_squared": {"type": "number", "description": "Peace² value"},
      "empathy_coefficient": {"type": "number", "description": "κᵣ value"},
      "weakest_stakeholder": {"type": "string"},
      "de_escalation_required": {"type": "boolean"},
      "trinity_consensus": {"type": "number", "description": "W³ value"},
      "recommendation": {"type": "string", "enum": ["PROCEED", "MODIFY", "HOLD", "VOID"]}
    }
  }
}
```

**Key Metric:** Peace² = (1 - destruction_score)² ≥ 1.0

---

### 6. apex_judge

**Organ:** 777  
**Agent:** Logic  
**Floors:** F3 (Tri-Witness), F8 (Genius), F13 (Sovereign)

**Purpose:** Calculate final G and issue verdict (SEAL/VOID/888_HOLD).

**JSON Schema:**
```json
{
  "name": "apex_judge",
  "description": "Final constitutional verdict: Calculate Genius Score and issue SEAL/VOID/HOLD",
  "inputSchema": {
    "type": "object",
    "properties": {
      "proposal": {
        "type": "string",
        "description": "Proposal to judge"
      },
      "evidence": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Evidence from reason_mind, simulate_heart, etc."
      },
      "telemetry": {
        "type": "object",
        "properties": {
          "A": {"type": "number", "description": "Akal (Intelligence)"},
          "P": {"type": "number", "description": "Peace (Stability)"},
          "X": {"type": "number", "description": "Exploration (Curiosity)"},
          "E": {"type": "number", "description": "Energy (Efficiency)"}
        }
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["proposal", "telemetry", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"]},
      "genius_score": {"type": "number", "description": "G = A × P × X × E²"},
      "witness_consensus": {"type": "number", "description": "W³ value"},
      "conditions": {"type": "array", "items": {"type": "string"}},
      "governance_token": {"type": "string", "description": "HMAC token for seal_vault"}
    }
  }
}
```

**Verdict Logic:**
- G ≥ 0.80 + W³ ≥ 0.95 → SEAL
- G ≥ 0.80 + W³ < 0.95 → PARTIAL
- G < 0.80 + potential → SABAR
- G < 0.50 or C_dark ≥ 0.30 → VOID
- Irreversible + no signature → 888_HOLD

---

### 7. execute_forge

**Organ:** 888  
**Agent:** Code  
**Floors:** F1 (Amanah), F3 (Agency), F9 (Growth)

**Purpose:** Execute commands/files after 888_HOLD check.

**JSON Schema:**
```json
{
  "name": "execute_forge",
  "description": "Material execution: commands, file writes, deployments with safety checks",
  "inputSchema": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Shell command or file operation"
      },
      "type": {
        "type": "string",
        "enum": ["shell", "write_file", "git_commit", "deploy"],
        "description": "Execution type"
      },
      "reversible": {
        "type": "boolean",
        "description": "Whether action can be undone"
      },
      "governance_token": {
        "type": "string",
        "description": "Token from apex_judge (required for irreversible)"
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["command", "type", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "status": {"type": "string", "enum": ["EXECUTED", "888_HOLD", "VOID"]},
      "output": {"type": "string"},
      "rollback_command": {"type": "string"},
      "eureka_scar": {"type": "string", "description": "Learning log if failure"}
    }
  }
}
```

**Safety:** Irreversible actions require governance_token from apex_judge.

---

### 8. seal_vault

**Organ:** 999  
**Agent:** Math  
**Floors:** F9 (Growth), F11 (Auditability)

**Purpose:** Record transaction to Merkle-chained VAULT999.

**JSON Schema:**
```json
{
  "name": "seal_vault",
  "description": "Immutable ledger: Record verdict to VAULT999 with Merkle chaining",
  "inputSchema": {
    "type": "object",
    "properties": {
      "event_type": {
        "type": "string",
        "enum": ["SEAL", "VOID", "888_HOLD", "EUREKA_SCAR"]
      },
      "payload": {
        "type": "object",
        "description": "Session data, telemetry, verdict"
      },
      "governance_token": {
        "type": "string",
        "description": "Token from apex_judge"
      },
      "session_token": {
        "type": "string"
      }
    },
    "required": ["event_type", "payload", "governance_token", "session_token"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "sealed": {"type": "boolean"},
      "merkle_root": {"type": "string"},
      "hash": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "ledger_location": {"type": "string"}
    }
  }
}
```

**Immutability:** Hash(n) = SHA256(Verdict + Hash(n-1) + Timestamp)

---

### 9. metabolic_loop

**Organ:** ALL  
**Agent:** Physics  
**Floors:** F4 (Clarity), P3 (Thermodynamics)

**Purpose:** Track E² usage, purge stale context, maintain ΔS ≤ 0.

**JSON Schema:**
```json
{
  "name": "metabolic_loop",
  "description": "Full constitutional pipeline: 000-999 with thermodynamic audit",
  "inputSchema": {
    "type": "object",
    "properties": {
      "request": {
        "type": "string",
        "description": "Raw user request"
      },
      "auto_execute": {
        "type": "boolean",
        "default": false,
        "description": "Auto-execute if SEAL (else return plan)"
      },
      "session_params": {
        "type": "object",
        "description": "anchor_session parameters"
      }
    },
    "required": ["request"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "verdict": {"type": "string", "enum": ["SEAL", "VOID", "888_HOLD"]},
      "stage_reached": {"type": "string", "description": "Final stage in 000-999"},
      "telemetry": {
        "type": "object",
        "properties": {
          "delta_s": {"type": "number"},
          "energy_used": {"type": "number", "description": "mA consumed"},
          "genius_score": {"type": "number"},
          "peace_squared": {"type": "number"},
          "vitality_index": {"type": "number", "description": "Ψ value"}
        }
      },
      "execution_result": {"type": "object"}
    }
  }
}
```

**Full Pipeline:** 000_INIT → 111_SENSE → 222_THINK → 333_ATLAS → 444_SYNC → 555_EMPATHY → 666_ALIGN → 777_FORGE → 888_JUDGE → 999_VAULT

---

## Workflow Combinations

### I. The Grounding Workflow
**search_reality + reason_mind**
- Physics gathers raw sensory data
- Math filters for logical consistency
- **Goal:** Eliminate hallucinations before output

### II. The Creative Workflow
**eureka_forge + apex_judge**
- Code proposes novel solution
- APEX measures against Genius Equation
- **Goal:** Novelty without compromising accuracy

### III. The Safety Workflow
**simulate_heart + execute_forge**
- Heart simulates potential chaos
- Forge locked if Peace² < 1.0
- **Goal:** Prevent accidental destruction

### IV. The Memory Workflow
**vector_memory + seal_vault**
- Retrieve associative "Eureka Scars"
- Seal new findings to immutable ledger
- **Goal:** Continuous growth without forgetting

---

## Implementation Notes

### FastMCP Integration
```python
from aaa_mcp.server import mcp

@mcp.tool()
def anchor_session(params: dict) -> dict:
    """Initialize constitutional session"""
    # F12 injection check
    # F11 auth verification
    # Initialize thermo budget
    pass

@mcp.tool()
def apex_judge(params: dict) -> dict:
    """Final constitutional verdict"""
    # Calculate G = A × P × X × E²
    # Check W³ consensus
    # Issue SEAL/VOID/HOLD
    pass
```

### Constitutional Middleware
Every tool call pipes through:
1. **Pre-check:** anchor_session validation
2. **Floor check:** Relevant F1-F13 enforcement
3. **Post-check:** apex_judge if state-changing
4. **Ledger:** seal_vault for audit trail

---

## Status

**MCP Holy 9:** ✅ DEFINED  
**Constitutional Enforcement:** ✅ SPECIFIED  
**Ready for Implementation:** YES

**Next Step:** Integration into `aaa_mcp/server.py`
