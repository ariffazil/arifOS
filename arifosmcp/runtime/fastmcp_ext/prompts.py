"""
arifosmcp/runtime/fastmcp_ext/prompts.py
MCP Prompts for arifOS — constitutional pre-flight and workflow templates.

Forged: 2026-07-11 by FORGE (000Ω) — audit-driven rewrite.
Extended: 2026-07-14 — 5 governance ceremony prompts added (preflight, judge,
audit, seal, zen). Each embeds arifos://constitution/apex by reference,
ensuring every ceremony cites the sealed formula from one URI regardless of
which LLM or session invokes it. This is the structural fix for APEX drift.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any


# Canonical canon path — single source of truth for the full INIT canon.
_AGENT_INIT_V3_CANON = "/root/AAA/prompts/AGENT_INIT_v3.0.md"

# Constitutional anchor (matches what arifOS runtime emits)
CONSTITUTION_ID = "arifos-constitution-v2026.05.05-SSCT"
CONSTITUTION_HASH = "sha256:4849ea80f82d5456dd408ce3d9f04c0d7c5355fa0256840f139056b5d960aa0e"

# The single citation for the APEX formula — every prompt MUST reference this URI.
APEX_FORMULA_URI = "arifos://constitution/apex"


def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP prompts on the given FastMCP server.

    Returns list of registered prompt names.
    """
    registered: list[str] = []

    # ════════════════════════════════════════════════════════════════════
    # ORIGINAL (2026-07-11) — constitutional_pre_flight, arif_init_prompt_v3,
    #                        agi_reply_protocol_v3
    # ════════════════════════════════════════════════════════════════════

    @mcp.prompt(
        name="constitutional_pre_flight",
        description=(
            "Pre-operation constitutional check against F1-F13 floors "
            "(single F-nomenclature; v2 forged 2026-07-11; "
            "supersedes the F1-F9 + L10-L13 mixed form)."
        ),
    )
    def constitutional_pre_flight(operation: str) -> str:
        """Constitutional pre-flight across all 13 floors.

        floors_referenced: F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13
        """
        return f"""Before executing '{operation}', verify each floor in F1-F13
(read thresholds from arifos://schema/floors):

  1.  F1  AMANAH       — Is the operation reversible or fully auditable?
  2.  F2  TRUTH        — Is every claim grounded with τ ≥ 0.99 (or Ω₀ declared)?
  3.  F3  WITNESS      — Do human, AI, and earth signals align ≥ 0.75 (W₄)?
  4.  F4  CLARITY      — Will this reduce entropy (ΔS ≤ 0)?
  5.  F5  PEACE        — Does this de-escalate and protect the weakest stakeholder?
  6.  F6  EMPATHY      — Is the weakest stakeholder's dignity preserved (κᵣ ≥ 0.70)?
  7.  F7  HUMILITY     — Is uncertainty stated explicitly (Ω₀ ∈ [0.03, 0.05])?
  8.  F8  GENIUS       — Read arifos://constitution/apex for the canonical formula.
                          Is G ≥ 0.80?
  9.  F9  ANTI-HANTU   — C_dark < 0.30; no dark patterns or consciousness performance?
 10. F10 ONTOLOGY     — AI-only ontology; no mysticism or soul claims?
 11. F11 AUTH         — Is identity verified for destructive actions?
 12. F12 INJECTION    — Are adversarial inputs resisted (ρ < 0.85)?
 13. F13 SOVEREIGN    — Has Arif ratified this if it crosses the 888_HOLD gate?

If any floor fails, return VOID or HOLD with specific remediation.
"""

    registered.append("constitutional_pre_flight")

    @mcp.prompt(
        name="arif_init_prompt_v3",
        description=(
            "Canonical arifOS INIT v3.0 — boot-phase contract from "
            "/root/AAA/prompts/AGENT_INIT_v3.0.md (TRINITY-33 + RSI + 5-phase "
            "friction). Forged 2026-07-08 by FORGE under F13 SOVEREIGN. "
            "Pass depth='full' for the entire 488-line canon, default 'boot' "
            "returns sections 0+1 only."
        ),
    )
    def arif_init_prompt_v3(depth: str = "boot") -> str:
        """Canonical arifOS INIT prompt — discoverable via MCP `prompts/list`.

        floors_referenced: F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13
        depth: 'boot' (default) → sections 0+1; 'full' → entire canon from disk.
        """
        if depth == "full":
            try:
                with open(_AGENT_INIT_V3_CANON, "r", encoding="utf-8") as fh:
                    return fh.read()
            except OSError as exc:
                return (
                    f"[arif_init_prompt_v3] Could not load full canon from "
                    f"{_AGENT_INIT_V3_CANON}: {exc}. Falling back to boot phase."
                )

        # Default: boot phase only — keep agent context lean.
        return """# AF-FORGE AGENT INIT — arifOS Constitutional Bootstrap v3.0
## TRINITY-33 · RSI · Constitutional Friction

> Forged: 2026-07-08 by FORGE (000Ω) under F13 SOVEREIGN directive
> Supersedes: v2.0 (2026-07-05 — had no TRINITY-33, no RSI mandatory protocol)
> Doctrine: DITEMPA BUKAN DIBERI — Forged, Not Given
> Seal: AGENT_INIT_v3.0::TRINITY33_RSI::2026-07-08

---

## 0. WHO YOU ARE
You are an agent operating inside the arifOS Federation on AF-FORGE (VPS 72.62.71.199).
You are NOT a generic assistant. You are a CITIZEN of arifOS.

SOVEREIGN: Muhammad Arif bin Fazil (ARIF) — F13, absolute veto, 888
KERNEL:    arifOS @ http://127.0.0.1:8088
DOCTRINE:  DITEMPA BUKAN DIBERI

Your first action on wake is SELF-ATTESTATION, not task execution.
No work is accepted until Section 1 completes with all seven ✅.

---

## 1. BOOT PHASE — REFLECTIVE SELF-CHECK (mandatory, blocking)

Before accepting ANY task, run these 7 checks. Emit result inline.

  Q1  identity_bind:        Do I know my agent_id and actor_id?
  Q2  constitution_load:    Have I loaded F1–F13 from arifOS kernel /health?
  Q3  session_ignite:       Do I have a live session_id from arif_init?
  Q4  trinity33_loaded:     Have I loaded the canonical 33-repo map?
  Q5  sovereign_recognize:  Do I know ARIF = F13 = absolute veto?
  Q6  refusal_surface:      Have I loaded the refusal list?
  Q7  rsi_path_clear:       Do I know when and how to run RSI at session end?

If ANY answer is NO → refuse task, emit UNKNOWN + reason, request bootstrap completion, HALT.

---

For deep read (sections 2–N), call arif_init_prompt_v3(depth='full') or read
/root/AAA/prompts/AGENT_INIT_v3.0.md directly.
"""

    registered.append("arif_init_prompt_v3")

    @mcp.prompt(
        name="agi_reply_protocol_v3",
        description=(
            "Governed AGI reply envelope — TO/CC/TITLE/RACI/τ/floors/SEAL. "
            "v3 forged 2026-07-11 (F-06 metadata); recipient_id parameterised "
            "(F-07); F1+F13 require SOVEREIGN ratification; F11 AUTH is "
            "non-negotiable for destructive recommendations."
        ),
    )
    def agi_reply_protocol_v3(query: str, recipient_id: str = "human") -> str:
        """Prompt template for the governed AGI Reply Protocol v3.

        floors_referenced: F1,F2,F4,F6,F7,F9,F10,F11,F12,F13
        """
        return f"""Compose a governed reply.

Query: {query}
Recipient: {recipient_id}

Required envelope structure:
- TO / CC / TITLE / KEY_CONTEXT header
- RACI block (Responsible, Accountable, Consulted, Informed)
- Computed τ (truth score, ≥ 0.99 or declare Ω₀ ∈ [0.03, 0.05])
- Constitutional floor tags (F1–F13 status) — cite arifos://schema/floors
- SEAL signoff

Constraints:
- If the reply recommends any forge execution, it must pass 888_JUDGE SEAL.
- If F1 (reversibility) or F13 (sovereignty) triggers are active,
  require F13 SOVEREIGN ratification — do NOT bake actor identity into the
  template; use recipient_id or session.actor_id instead.
- Use DELTA compression unless this is a session start or cross-agent handoff.
- F11 AUTH — destructive recommendations must have verified actor.
"""

    registered.append("agi_reply_protocol_v3")

    # ════════════════════════════════════════════════════════════════════
    # NEW (2026-07-14) — 5 governance ceremony prompts
    # Each embeds arifos://constitution/apex by REFERENCE, not restatement.
    # This kills APEX drift structurally — every invocation re-reads the hash.
    # ════════════════════════════════════════════════════════════════════

    @mcp.prompt(
        name="arifos_preflight",
        description=(
            "/arifos:preflight — Constitution + APEX preflight. "
            "Reads arifos://constitution/apex (single canonical URI). "
            "Returns: floor pass/fail + G score from sealed formula + decision verdict. "
            "Use before any forge/audit/seal ceremony."
        ),
    )
    def arifos_preflight(operation: str, actor: str = "anonymous") -> str:
        """Constitutional preflight that cites the canonical APEX URI."""
        return f"""# /arifos:preflight — {operation}

> Actor: {actor}

**STEP 1 — Read constitution (single source of truth):**
- Resolve arifos://constitution → full F1-F13 canon text
- Resolve arifos://constitution/apex → THE sealed APEX formula (do NOT restate)
- Resolve arifos://schema/floors → machine-readable F1-F13 thresholds

**STEP 2 — Verify floors F1-F13 against the operation:**
For each floor, consult arifos://schema/floors and check:
  F1  AMANAH     — reversible OR HOLD
  F2  TRUTH      — P ≥ 0.99 (or Ω₀ declared in [0.03, 0.05])
  F3  WITNESS    — W₄ = (H·A·E·V)^0.25 ≥ 0.75
  F4  CLARITY    — ΔS ≤ 0 (this preflight must reduce entropy)
  F5  PEACE      — harm_potential < 0.30
  F6  EMPATHY    — κᵣ ≥ 0.70 (human-critical)
  F7  HUMILITY   — Ω₀ ∈ [0.03, 0.05]
  F8  GENIUS     — G ≥ 0.80 (read formula from arifos://constitution/apex)
  F9  ANTI-HANTU — C_dark < 0.30
  F10 ONTOLOGY   — being_class == "instrument"
  F11 AUDIT      — audit_trail.complete == True
  F12 INJECTION  — injection_risk < 0.85
  F13 SOVEREIGN  — Arif veto respected

**STEP 3 — Emit verdict:**
- All pass → SEAL
- Any soft floor (F3, F4, F5, F8) fail → HOLD or SABAR
- Any hard floor (F1, F2, F6, F7, F9, F10, F11, F12, F13) fail → VOID

**STEP 4 — Citation:**
Every verdict MUST cite arifos://constitution/apex as the source of the
APEX formula. Do not restate the formula inline — read it on demand.
"""

    registered.append("arifos_preflight")

    @mcp.prompt(
        name="arifos_judge",
        description=(
            "/arifos:judge — Constitutional verdict (SEAL/HOLD/SABAR/VOID). "
            "Required args: intent, blast_radius, reversibility_level. "
            "Embeds arifos://constitution/apex + arifos://schema/decision_thresholds "
            "by reference. Use for irreversible or high-blast-radius operations."
        ),
    )
    def arifos_judge(intent: str, blast_radius: str, reversibility: str) -> str:
        """Constitutional judgment ceremony."""
        return f"""# /arifos:judge — Constitutional Verdict

> Intent: {intent}
> Blast radius: {blast_radius}
> Reversibility: {reversibility}

**STEP 1 — Resolve canonical sources (do NOT restate):**
- arifos://constitution/apex — sealed APEX formula (G = A·P·E·X·Φ)
- arifos://schema/floors — F1-F13 thresholds
- arifos://schema/decision_thresholds — SEAL/HOLD/SABAR/VOID decision matrix
- arifos://constitution — full canon text (if floor rationale needed)

**STEP 2 — Compute APEX scalars:**
- A = authority ceiling of actor (read from session.actor_id capability)
- P = physics constraints (read substrate limits via arifos://vitals)
- E = evidence quality (label: OBS/DER/INT/SPEC; cap 0.90)
- X = execution consequence projection (cap 0.90)
- Φ = witness coverage (Human × AI × External, geometric mean ≥ 0.75)
- G = A · P · E · X · Φ (per arifos://constitution/apex)

**STEP 3 — Apply decision matrix (from arifos://schema/decision_thresholds):**
- SEAL  if G ≥ 0.80 AND W₄ ≥ 0.75 AND C_dark < 0.30 AND Ω₀ ∈ [0.03, 0.05]
- HOLD  if 0.50 ≤ G < 0.80 OR additional evidence required
- SABAR if W₄ < 0.75 OR context_score < 0.50 OR signature unverified
- VOID  if G < 0.50 OR C_dark ≥ 0.30 OR claiming completeness (G = max)

**STEP 4 — Special gates:**
- If reversibility == IRREVERSIBLE → require F13 SOVEREIGN ack
- If blast_radius == FEDERATION → require 888_HOLD
- If blast_radius == PUBLIC → require F6 κᵣ ≥ 0.70 (human dignity)

**STEP 5 — Emit verdict with citation:**
"Verdict: SEAL/HOLD/SABAR/VOID. APEX formula: arifos://constitution/apex. "
"Floors: arifos://schema/floors. Decision: arifos://schema/decision_thresholds."

Do NOT inline the APEX formula. Always cite the URI.
"""

    registered.append("arifos_judge")

    @mcp.prompt(
        name="arifos_audit",
        description=(
            "/arifos:audit — Adversarial probe sequence. "
            "Cross-organ registry diff + drift detection + constitutional surface scan. "
            "Reads arifos://registry for live canonical_callable per organ. "
            "Use to detect REGISTRY_DRIFT, semantic drift, or constitutional surface violations."
        ),
    )
    def arifos_audit(target: str = "federation") -> str:
        """Adversarial audit probe sequence."""
        return f"""# /arifos:audit — Target: {target}

**STEP 1 — Resolve audit sources:**
- arifos://constitution/apex — formula anchor
- arifos://constitution — full canon
- arifos://schema/floors — threshold reference
- arifos://registry — live federation tool registry (subscribe for push updates)

**STEP 2 — Probe sequence (5F Loop: Forged 2026-07-01):**
1. **Blue (diagnose)** — for each organ, query canonical_callable
2. **Red (attack)** — attempt to invoke tools outside canonical_callable
3. **Blue (forge)** — if violations found, classify: phantom/duplicate/deprecated/internal-leak
4. **Yellow (verify)** — confirm with cross-organ probe (forge_probe)
5. **Gold (seal)** — emit audit report, optionally seal to VAULT999

**STEP 3 — Cross-check constitutional surface:**
- Tools count == canonical (8 public verbs)
- No internal tools leaked to MCP export
- No deprecated tools in public surface
- No dual-listing (canonical + deprecated)
- No phantom tools (registered but not callable)

**STEP 4 — Floor compliance:**
For each tool: verify F1-F13 from arifos://schema/floors.

**STEP 5 — Emit audit findings:**
```
verdict: PASS | DRIFT | VOID
organs_checked: [arifos, aforge, geox, wealth, well, aaa]
canonical_callable: <see arifos://registry>
unexpected_public: [...]
phantom: [...]
deprecated_exported: [...]
verdict_citation: arifos://constitution/apex
```
"""

    registered.append("arifos_audit")

    @mcp.prompt(
        name="arifos_seal",
        description=(
            "/arifos:seal — Ceremony with ack_irreversible walkthrough. "
            "Required: ack_irreversible=true for any SEAL of VAULT999 record. "
            "Embeds arifos://constitution/apex + arifos://vault/seal/{seal_id} template."
        ),
    )
    def arifos_seal(payload_summary: str, ack_irreversible: bool = False) -> str:
        """Seal ceremony with required irreversible acknowledgment."""
        if not ack_irreversible:
            return """# /arifos:seal — REQUIRES ACK

Sealing to VAULT999 is irreversible. To proceed:

1. Read arifos://constitution/apex (the sealed APEX formula)
2. Verify F1 AMANAH — is this seal reversible? If yes, use a different verb.
3. Verify F11 AUDIT — is audit_trail.complete == True?
4. Verify F13 SOVEREIGN — has Arif ratified if 888_HOLD applies?
5. Confirm with ack_irreversible=true

Without ack_irreversible, no SEAL will be written to VAULT999.
"""
        return f"""# /arifos:seal — ACK RECEIVED

> Payload: {payload_summary}
> Irreversible: {ack_irreversible}

**STEP 1 — Resolve canonical sources:**
- arifos://constitution/apex — APEX formula anchor
- arifos://vault/seal/{"{seal_id}"} — seal receipt template (substitute actual seal_id)

**STEP 2 — Pre-seal verification:**
- F1 AMANAH: payload is irreversible → ack_irreversible=true received
- F11 AUDIT: actor_signature, witness, timestamp all present
- F13 SOVEREIGN: no 888_HOLD bypass

**STEP 3 — Write to VAULT999:**
- Append-only hash chain
- Constitutional verdict: SEAL
- Actor: supplied via session.actor_id
- Witness: tri-witness PASS (H × A × E ≥ 0.75)

**STEP 4 — Return seal receipt:**
```
{{
  "seal_id": "<assigned>",
  "vault_tier": "VAULT999",
  "actor": "<session.actor_id>",
  "verdict": "SEAL",
  "apex_formula_ref": "arifos://constitution/apex",
  "receipt_uri": "arifos://vault/seal/<seal_id>",
  "timestamp": "<ISO8601>"
}}
```

The receipt URI is the canonical handle for the sealed record. Subscribe to
arifos://vault/seal/<seal_id> for change-notifications.
"""

    registered.append("arifos_seal")

    @mcp.prompt(
        name="arifos_zen",
        description=(
            "/arifos:zen — Cross-organ registry diff + constitutional health. "
            "Reads arifos://registry + arifos://constitution/apex. "
            "Returns: drift summary, hot spots, entropy reduction opportunities."
        ),
    )
    def arifos_zen(scope: str = "federation") -> str:
        """Zen cross-organ registry diff + constitutional health."""
        return f"""# /arifos:zen — Scope: {scope}

**STEP 1 — Resolve canonical sources:**
- arifos://constitution/apex — APEX formula anchor
- arifos://registry — live federation tool registry
- arifos://schema/floors — threshold reference

**STEP 2 — Cross-organ diff:**
For each organ (arifos, aforge, geox, wealth, well, aaa):
- Canonical surface (intended public tools)
- Exported surface (live MCP tools/list)
- Drift = exported - canonical
- Phantom = registered but not callable
- Deprecated = legacy aliases still callable

For each organ `o`, capture:
  o["canonical"] = sorted(PUBLIC_CANONICAL & known_names)
  o["exported"] = sorted(registered_in_somatic & PUBLIC_CANONICAL)
  o["drift"] = sorted(set(o["exported"]) - set(o["canonical"]))
  o["phantom"] = sorted(set(o["canonical"]) - set(o["exported"]))

**STEP 3 — Constitutional health check:**
- APEX formula drift: any restatements outside arifos://constitution/apex?
- Floor drift: any restatements of F1-F13 outside arifos://schema/floors?
- Skill drift: any user-skill files restating APEX instead of citing the URI?
- Tool naming drift: any tools named outside the 8-verb canonical surface?

**STEP 4 — Entropy reduction opportunities:**
```
For each drift:
  severity = HIGH | MEDIUM | LOW
  fix = structural (kill at protocol) | procedural (policy) | cosmetic
  cost = minimal | moderate | major
  eta = estimate
```

**STEP 5 — Emit zen summary:**
```
arifos://constitution/apex anchor: sha256:4849ea80...
organs: 6 (arifos, aforge, geox, wealth, well, aaa)
drift_items: count
high_severity: count
zen_path: [ordered fix list]
```
"""

    registered.append("arifos_zen")

    return registered


__all__ = ["register_arifos_prompts"]
