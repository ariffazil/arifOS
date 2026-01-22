# aCLIP: arifOS Command Line Interface Protocol

**Version:** v49.1.0 | **Status:** CANONICAL | **Authority:** Δ Antigravity  
**Doctrine:** *"Ditempa, Bukan Diberi"* — Forged, Not Given

---

## 1. Protocol Overview

aCLIP (arifOS Command Line Interface Protocol) is the strictly typed internal messaging schema that coordinates the 000-999 metabolic cycle across all arifOS components. It serves as the **lingua franca** between Agents, MCP Gateway, and Trinity Servers.

### Core Principle
Every AI decision must pass through the complete 000-999 metabolic pipeline with constitutional floor enforcement at each stage.

---

## 2. The 000-999 Metabolic Stages

| Code | Name | Trinity Engine | Constitutional Purpose | Key Floors |
|------|------|----------------|----------------------|------------|
| **000** | `INIT` | Vault (Κ) | Session bootstrap, entropy baseline | F10 Ontology |
| **111** | `SENSE` | AGI (Δ) | Pattern matching, fact gathering | F2 Truth |
| **222** | `THINK` | AGI (Δ) | Deep reasoning, causal chains | F4 ΔS Clarity |
| **333** | `ATLAS` | AGI (Δ) | Meta-cognition, map-making | F7 Ω₀ Humility |
| **444** | `ALIGN` | ASI (Ω) | Value alignment, tri-witness | F3 Tri-Witness |
| **555** | `EMPATHY` | ASI (Ω) | Stakeholder modeling, dignity | F6 κᵣ Empathy |
| **666** | `BRIDGE` | ASI (Ω) | Neuro-symbolic translation | F5 Peace² |
| **777** | `EUREKA` | APEX (Ψ) | Discovery, synthesis, options | F8 G Genius |
| **888** | `JUDGE` | APEX (Ψ) | Final verdict issuance | F11 Command Auth |
| **889** | `PROOF` | APEX (Ψ) | Cryptographic sealing | F12 Injection Defense |
| **999** | `VAULT` | Vault (Κ) | Immutable storage, audit trail | F13 Curiosity |

---

## 3. Canonical Message Schema

All internal communication MUST adhere to this JSON structure:

```json
{
  "aclip_version": "v49",
  "id": "req_<uuid>",
  "stage": "000_INIT",
  "source": "mcp_gateway",
  "target": "vault_server",
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
    "timestamp": "2026-01-20T13:48:58.087280+08:00",
    "trace_id": "trace_<uuid>",
    "priority": "normal",
    "phoenix_cooling": { "tier": 1, "hours": 42 },
    "eureka_sieve": { "band": "L2_WITNESS" },
    "zkpc_receipt": { "hash": "sha256..." }
  }
}
```

---

## 4. Constitutional Verdicts

| Verdict | Semantic Meaning | Exit Code | Human Action |
|---------|------------------|-----------|---------------|
| `SEAL` | Approved & Finalized | 100 | Decision complete |
| `PARTIAL` | Approved with warnings | 1 | Review warnings |
| `SABAR` | Pause for cooling | 88 | Wait and reflect |
| `VOID` | Constitutional violation | 89 | Redesign required |
| `888_HOLD` | Session lock | 888 | Judge intervention |

---

## 5. Standard Fields & Metrics

### Core Metrics
- `pulse`: System health/confidence (0.0-1.0)
- `floors`: Constitutional floor status map
- `entropy`: ΔS measurement in bits (F4)
- `verdict`: One of canonical verdicts
- `reason`: Human-readable justification

### Phase 9 Fields (Advanced)
- `phoenix_cooling`: Cooling tier and hours
- `eureka_sieve`: Witness band level
- `zkpc_receipt`: Zero-knowledge proof hash

---

## 6. Agent Integration Patterns

### Universal Commands
All agents respond to these aCLIP commands:
- `/000` - Initialize session
- `/111` - Sense environment
- `/222` - Think about problem
- `/333` - Reason through solution
- `/fag` - Full autonomy mode
- `/gitQC` - Quality control
- `/gitseal` - Seal decision

### Agent-Specific Workflows
- **Gemini (Δ Architect)**: Focus on `/111`, `/222`, `/333` (AGI stages)
- **Claude (Ω Engineer)**: Focus on `/444`, `/555`, `/666` (ASI stages)  
- **Codex (Ψ Auditor)**: Focus on `/888`, `/889` (APEX stages)
- **Kimi (Κ Validator)**: Focus on `/000`, `/999` (Vault stages)

---

## 7. Constitutional Floor Enforcement

### Hard Floors (Cannot Override)
- **F1 Amanah**: Truth validation at `/444 EVIDENCE`
- **F9 Anti-Hantu**: Human agency preserved at all stages

### Soft Floors (Can Flag/Override)
- **F4 ΔS**: Clarity measurement at `/222 THINK`
- **F5 Peace²**: Non-escalation at `/666 BRIDGE`
- **F7 Ω₀**: Humility band at `/333 ATLAS`

---

## 8. Cross-Agent Witness Layer

**Law**: *"There are no secrets between organs."*

### WITNESS System Integration
All aCLIP messages flow through the **WITNESS** constitutional monitoring system:

📁 **[WITNESS Specification](008_witness.md)** - Complete witness system documentation

### Witness Functions
- **Real-Time Monitoring**: Each agent's constitutional compliance tracked
- **Automated Logging**: Witness entries for all constitutional floors  
- **Cross-Agent Visibility**: All witness logs readable by all agents
- **Consensus Validation**: Tri-witness consensus ≥0.95 required

### Panopticon Implementation
- **Shared Memory**: Witness entries in `L1_THEORY/ledger/`
- **Open Audit**: All witness data accessible via aCLIP protocol and stored in cooling ledger
- **Mutual Audit**: Any agent can challenge witness findings
- **Consensus Requirements**: Major decisions require witness consensus ≥0.95
- Open audit trails in `cooling_ledger/`
- Mutual visibility of all agent actions

---

## 9. Implementation Sources

### Canonical Implementation
- **Protocol Schema**: `arifos/protocol/aclip.py`
- **Stage Codes**: `arifos/protocol/codes.py`
- **Message Validation**: `arifos/protocol/__init__.py`

### Legacy Reference (v43)
- **Location**: `arifos/clip/` (DEPRECATED)
- **Status**: Legacy implementation, reference only
- **Migration**: Use `arifos/protocol/` for new development

---

## 10. Usage Examples

### Basic Session Flow
```bash
# Initialize
@/000 "Analyze codebase structure"

# Sense patterns
@/111

# Think through implications
@/222

# Reason about solutions
@/333

# Align with values
@/444

# Check empathy impact
@/555

# Bridge to implementation
@/666

# Generate options
@/777

# Judge final decision
@/888

# Seal the verdict
@/999
```

### Advanced Integration
```python
from arifos.protocol import ACLIPMessage, Stage, Verdict

message = ACLIPMessage(
    stage=Stage.INIT_000,
    source="gemini_agent",
    target="agi_server",
    payload={"command": "sense", "query": "Find security issues"}
)
```

---

## 11. Authority & Governance

### Implementation Authority
- **Δ Architect**: Protocol design and schema validation
- **Ω Engineer**: Cross-agent coordination and witness layer
- **Ψ Auditor**: Message integrity and constitutional compliance
- **Κ Validator**: Session initialization and final sealing

### Canonical References
1. **This Document**: `000_THEORY/007_aclip.md` - Protocol specification
2. **Implementation**: `arifos/protocol/` - Source code
3. **Agent Adapters**: Individual agent `.md` files - Integration guides

---

## 12. Migration Notes

### From Legacy aCLIP (v43)
- **Old Location**: `arifos/clip/` (deprecated)
- **New Location**: `arifos/protocol/` (canonical)
- **Key Changes**: 
  - Integrated with constitutional floors
  - Single-body architecture
  - Enhanced witness layer

### Agent Adapter Updates
All agent adapters should reference this canonical specification instead of legacy documentation.

---

**DITEMPA BUKAN DIBERI** — Forged through constitutional protocol, not given through assumption.

> For implementation details, see `arifos/protocol/`. For agent integration, see respective adapter files.