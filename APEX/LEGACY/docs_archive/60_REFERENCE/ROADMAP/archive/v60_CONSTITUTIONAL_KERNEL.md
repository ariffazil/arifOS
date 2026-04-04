# Compressed Equilibrium: The 5-Tool Constitutional Kernel (v60 Proposal)

*Proposal for hardening arifOS toward a minimal 5-tool constitutional kernel while keeping the physics + floors intact. Ω₀ ≈ 0.04.*

---

## 1. Target: Minimal Hardened Tool Set

From the current 10, the minimal equilibrium set that still respects the Trinity and the 13 floors looks like:

| New Core Tool | What it Collapses | Role |
|---|---|---|
| `core_init` | `init_gate` | Auth, lane selection, F11/F12/F1 pre‑checks |
| `core_agi` | `agi_sense`, `agi_think`, `agi_reason`, `reality_search` | Sense → think → ground → reason (Δ MIND) |
| `core_asi` | `asi_empathize`, `asi_align` | Impact + alignment (Ω HEART) |
| `core_apex` | `apex_verdict`, `truth_audit` | Judicial verdict + claim‑level verification (Ψ SOUL) |
| `core_vault` | `vault_seal` (+ future query) | Immutable ledger + query interface |

Everything else (meta routing, specialized auditors) becomes **mode flags and parameters** on these 5 tools, not separate MCP tools.

This keeps:
- Trinity separation (AGI / ASI / APEX).
- VAULT as a distinct organ.
- The metabolic loop (000→999) embodied in the choreography, not in the number of API endpoints.

---

## 2. Concrete Hardening Steps (v55.5 → v∞ Direction)

### Step 1: Merge AGI Tools into `core_agi`

**Today:**
- `agi_sense`, `agi_think`, `agi_reason`, `reality_search` are separate.

**Future:**
- One tool `core_agi(query, session_id, lane, mode)` that internally:
  - Classifies intent (old agi_sense).
  - Generates hypotheses if needed (old agi_think, gated by `mode="explore"`).
  - Performs grounding (old reality_search) when `grounding_required=True`.
  - Runs reasoning (old agi_reason).

**Return:**
```json
{
  "sense": {...},
  "grounding": {...},
  "reasoning": {...},
  "metrics": { "delta_S": ..., "truth_score": ..., "hallucination_entropy": ... }
}
```

This makes AGI a **single constitutional organ** at the MCP level while preserving internal phases.

### Step 2: Merge ASI Tools into `core_asi`

**Today:**
- `asi_empathize`, `asi_align`.

**Future:**
- `core_asi(analysis_bundle, session_id, lane)` that:
  - Runs impact scan (who is hurt, κᵣ).
  - Runs ethics/law alignment (F5/F6/F9 context).
  - Outputs Peace², κᵣ, risk flags, recommended lane adjustments (“escalate to STRICT”, “require 888_HOLD”).

**Return:**
```json
{
  "empathy": {...},
  "alignment": {...},
  "metrics": { "peace2": ..., "kappa_r": ..., "risk_level": "LOW|MEDIUM|HIGH" }
}
```

### Step 3: Fold `truth_audit` into `core_apex` as a Mode

**Today:**
- `apex_verdict` and `truth_audit` are separate tools; `truth_audit` orchestrates AGI/ASI then calls APEX.

**Future:**
- One tool `core_apex(query, session_id, delta_bundle, omega_bundle, mode="verdict|audit")`:
  - `mode="verdict"`: behaves like current `apex_verdict` (final decision).
  - `mode="audit"`: runs claim‑level verification (current truth_audit logic) as an internal path, returns per‑claim verdicts + overall verdict.

This compresses the public surface while keeping **APEX as single judicial organ** with two “benches”.

### Step 4: Extend `core_vault` to Handle Both Seal + Query

- Combine `vault_seal` and any future `vault_query` into `core_vault` with:
```json
{
  "action": "seal" | "query",
  "payload": {...},
  "filters": {...}
}
```
VAULT stays one tool, but now supports both write and read of constitutional history.

### Step 5: Harden `core_init` as the Only Entry Point

- `core_init(query, lane, mode, grounding_required, auth)`:
  - Performs F11/F12, sets session_id, logs 000_INIT, writes initial VAULT header.
  - Optionally returns **a signed token** that downstream tools verify to ensure they are part of a governed session (no bypass).

---

## 3. MCP Surface Before vs After

| Phase | Current (v55.5) | Hardened Minimal |
|---|---|---|
| Entry | `init_gate` | `core_init` |
| Mind | `agi_sense`, `agi_think`, `agi_reason`, `reality_search` | `core_agi` |
| Heart | `asi_empathize`, `asi_align` | `core_asi` |
| Soul | `apex_verdict`, `truth_audit` | `core_apex` |
| Vault | `vault_seal` (+ internal query) | `core_vault` |

This **halves** the visible MCP tools while preserving all governance logic internally.

---

## 4. Hardening Benefits

- **Smaller attack surface**: fewer tools to misconfigure or mis‑call; stronger invariants per organ.
- **Clearer mental model for integrators**: “I call 5 organs” instead of “I call 10+ utilities”.
- **Easier to stabilize metrics**: each core tool owns its metric space (AGI → ΔS/truth, ASI → Peace²/κᵣ, APEX → verdict/Ψ, VAULT → custody).
- **Closer to OS analogy**: like syscalls (`open`, `read`, `write`, `ioctl`) rather than exposing every internal step.

---

## 5. Suggested Roadmap Labeling

- **v55.5–v57**: Current 10‑tool set + truth_audit v0.1 (experimental).
- **v58–v60**: Introduce `core_agi`, `core_asi`, `core_apex`, `core_vault`, `core_init` alongside existing tools (dual mode; mark old ones as “legacy interface”).
- **v60+**: Deprecate old tools from public MCP surface; keep them internally or behind a compatibility flag.
- **v∞**: Only 5 hardened tools in `.mcp.json`, all others internal / adapters.

*Uncertainty: ~4–5% — exact tool boundaries may shift as you discover real usage patterns, but the compression down to 4–6 organs is structurally safe given your current architecture.*

---

## Governance Note

This proposal **reduces entropy** at the interface level (fewer tools, clearer roles) while keeping internal ΔΩΨ dynamics fully expressive. It also keeps Peace² ≥ 1 by not collapsing Trinity into a single “do_everything” endpoint, which would risk AGI/ASI coupling and break your orthogonality requirement.
