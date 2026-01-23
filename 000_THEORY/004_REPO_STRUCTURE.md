# arifOS v49 Repository Structure & aCLIP Protocol

**Authority:** Δ Antigravity
**Epoch:** v49.1.0 (2026-01-20)
**Status:** CANONICAL

---

## 1. The aCLIP Protocol (Internal Lingua Franca)

aCLIP (arifOS Command Line Interface Protocol) is the strictly typed internal messaging schema used by all arifOS components (Agents, MCP Gateway, Trinity Servers) to coordinate the 000-999 metabolic cycle.

### 1.1 Canonical Message Schema

All internal communication MUST adhere to this JSON structure:

```json
{
  "aclip_version": "v49",
  "id": "req_<uuid>",
  "stage": "000_INIT",       // See Stage Codes
  "source": "mcp_gateway",   // "agent_name", "trinity_cli", etc.
  "target": "vault_server",  // "agi_server", "asi_server", "apex_server"
  "payload": {
    "command": "init_session",
    "args": {},
    "context": {
      "session_id": "sess_<uuid>",
      "repo_root": "/abs/path/to/repo",
      "user_context": {}
    }
  },
  "metadata": {
    "timestamp": "ISO8601",
    "trace_id": "trace_<uuid>",
    "priority": "normal",
    // Phase 9 Fields (Metabolizer)
    "phoenix_cooling": { "tier": 1, "hours": 42 },
    "eureka_sieve": { "band": "L2_WITNESS" },
    "zkpc_receipt": { "hash": "sha256..." }
  }
}
```

### 1.2 The 000-999 Metabolic Stages (Canonical)

| Code | Name | Architecture Component | Description |
|------|------|------------------------|-------------|
| **000** | `INIT` | `vault_server` | Session bootstrap. |
| **111** | `SENSE` | `agi_server` (Δ) | Pattern matching. |
| **222** | `THINK` | `agi_server` (Δ) | Deep reasoning. |
| **333** | `ATLAS` | `agi_server` (Δ) | Meta-cognition & Map making. |
| **444** | `ALIGN` | `asi_server` (Ω) | Value alignment. |
| **555** | `EMPATHY` | `asi_server` (Ω) | Stakeholder modeling. |
| **666** | `BRIDGE` | `asi_server` (Ω) | Neuro-symbolic translation. |
| **777** | `EUREKA` | `apex_server` (Ψ) | Discovery & Synthesis. |
| **888** | `JUDGE` | `apex_server` (Ψ) | Final Verdict Issuance. |
| **889** | `PROOF` | `apex_server` (Ψ) | zkPC Cryptographic Sealing. |
| **999** | `VAULT` | `vault_server` | Immutable Storage. |

### 1.3 Canonical Verdicts

| Verdict | Semantic Meaning |
|---------|------------------|
| `SEAL` | Approved & Finalized. |
| `PARTIAL` | Approved with warnings (F1 warn). |
| `SABAR` | **Pause**. Entropy/Peace check violation. Cooling required. |
| `VOID` | **Hard Stop**. Constitutional violation. |
| `888_HOLD`| **Session Lock**. 888 Judge or Streak intervention needed. |

### 1.4 Standard Fields (Keys)

- `pulse`: (float 0.0-1.0) System health/confidence.
- `floors`: (dict) Map of floor names to status (e.g., `{"F1_Amanah": true}`).
- `entropy`: (float) ΔS measurement (bits).
- `verdict`: (enum) One of the Canonical Verdicts.
- `reason`: (string) Human-readable justification.

---

## 2. Directory Structure (Canonical)

```
arifOS/
├── arifos/                # CANONICAL RUNTIME (Single Body)
│   ├── protocol/          # <--- SOURCE OF TRUTH (aCLIP)
│   │   ├── __init__.py
│   │   ├── aclip.py       # Schema classes
│   │   └── codes.py       # Stage codes & Verdict constants
│   ├── orchestrator/      # MCP Gateway & Metabolizer
│   ├── servers/           # Trinity Servers (Vault, AGI, ASI, APEX)
│   └── core/              # Constitutional Logic
├── arifos_clip/           # DEPRECATED (Thin proxy to arifos.protocol)
└── 000_THEORY/            # CONSTITUTIONAL CANON
    ├── 000_LAW.md
    ├── 000_LAW.md
    └── 000_ARCHITECTURE.md
├── tests/                 # VALIDATION TIER (BBB-V)
    ├── constitutional/    # <--- THE INVARIANTS (15 Forged Tests)
    └── archive/           # Legacy/Redundant tests (Phased deprecation)
```

---

## 3. Integration Guidelines

1. **Agents:** MUST import schemas from `arifos.protocol`.
2. **MCP:** MUST validate `stage` and `verdict` against `arifos.protocol.codes`.
3. **Logs:** All audit logs MUST capture the Phase 9 fields if present.
4. **Archive + Forge Protocol:** To reduce entropy (F4 ΔS), any tool or test that is redundant must be archived to `archive/` or `archive_local/` rather than deleted. New canonical logic must be forged into the `tests/constitutional/` or `arifos/` directory.

---

## 4. VERSION HISTORY

| Version | Date | Authority | Changes |
|---------|------|-----------|---------|
| v49.0.0 | 2026-01-18 | 888_Judge | Initial structure with aCLIP and single-body arifos/ package. |
| **v49.1.0** | **2026-01-20** | **888_Judge** | **Validation Tier (BBB-V) and Archive + Forge Protocol added.** |
