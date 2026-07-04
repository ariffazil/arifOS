#!/usr/bin/env python3
"""
generate_skill_md.py — Batch generator for 24 arifOS kernel SKILL.md files
Forged: 2026-07-04 by AUDITOR (Ψ)
Authority: F13 SOVEREIGN
Status: MUBAH (digital ops)

PURPOSE
-------
Creates the 24 kernel SKILL.md files in /root/arifOS/skills/ with full
Fiqh Agentik blocks (WAJIB / SUNAT / HARUS / MAKRUH / HARAM).

Skill catalog derived from canonical 24 kernel skills (14 structural no-RSI,
10 RSI-eligible). See Fiqh Agentik v1.0 PART 11.

DITEMPA BUKAN DIBERI — Ditempa (forged), Bukan Diberi (not given).
"""

import os
from pathlib import Path

SKILLS_DIR = Path("/root/arifOS/skills")
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


SKILLS = [
    # ── 14 STRUCTURAL SKILLS (no RSI) ──────────────────────────────────────
    {
        "id": "S01",
        "name": "constitutional-attest",
        "primary_floor": "F2 Truth",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Verify constitution hash unchanged since last session. Load F1-F13 floors.",
        "stage": "000_INIT",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/floors.py", "registries/01-constitution.yaml"],
        "wajib": [
            "Load constitution hash at every session init",
            "Compare with last sealed session hash",
            "Alert if drift detected — HOLD until F13 review",
        ],
        "haram": [
            "Modify constitution.json at runtime",
            "Skip attest to speed session startup",
            "Skip floor evaluation by claiming 'trusted'",
        ],
        "makruh": [
            "Silent re-hash without logging",
            "Caching stale constitution hash",
        ],
        "sunat": [
            "Cross-reference kernel invariant.yaml + eureka axioms + registry",
            "Surface floor change_alert to principal",
        ],
        "failure_mode": "Constitutional drift undetected → silent floor breach",
    },
    {
        "id": "S02",
        "name": "sovereign-heartbeat-verify",
        "primary_floor": "F13 Sovereign",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Verify /000/ signature is live. Confirm F13 SOVEREIGN anchor.",
        "stage": "000_INIT",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/crypto/heartbeat.py"],
        "wajib": [
            "Verify Ed25519 signature on /000/ every 24h",
            "Reject any session with expired sovereign anchor",
            "HALT session if impersonation detected",
        ],
        "haram": [
            "Bypass heartbeat for performance",
            "Use cached signature >24h",
            "Forge heartbeat signature",
        ],
        "makruh": ["Long silent retries without surfacing"],
        "sunat": ["Cross-verify against multiple sovereign endpoints"],
        "failure_mode": "Impersonation of sovereign anchor → catastrophic",
    },
    {
        "id": "S03",
        "name": "session-envelope-forge",
        "primary_floor": "F11 Audit",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Wrap every action in FederationEnvelope with required fields.",
        "stage": "000_INIT → 999_SEAL",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/envelope.py"],
        "wajib": [
            "Emit envelope with all 10 required fields",
            "Reject any tool call without valid envelope",
            "Reject malformed envelopes — DO NOT auto-repair",
        ],
        "haram": [
            "Execute tool call without envelope",
            "Skip epistemic_tags on claims",
            "Wrap with forged authority_chain",
        ],
        "makruh": ["Verbose envelope metadata beyond required fields"],
        "sunat": ["Include session narrative context"],
        "failure_mode": "Untracked actions → no audit trail",
    },
    {
        "id": "S04",
        "name": "witness-packet-wrap",
        "primary_floor": "F2 Truth",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Wrap every LLM output in WitnessPacket with provenance + epistemic tags.",
        "stage": "all",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/witness_packet.py"],
        "wajib": [
            "Every LLM output wrapped before downstream use",
            "Provenance: source citation, generation time, model_id",
            "Epistemic tags: OBS/DER/INT/SPEC on every claim",
        ],
        "haram": [
            "Use unwrapped LLM output directly",
            "Skip epistemic tagging",
            "Strip provenance to save tokens",
        ],
        "makruh": ["Inconsistent tag application across outputs"],
        "sunat": ["Include confidence score per claim"],
        "failure_mode": "Untracked claims → F2 TRUTH breach",
    },
    {
        "id": "S05",
        "name": "stage-machine-guard",
        "primary_floor": "F4 Clarity",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Enforce 000→111→333→555→666→777→999 progression. Block skips.",
        "stage": "all",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/state_machine.py"],
        "wajib": [
            "Block any state machine skip",
            "Block any backward transition without SABAR",
            "Emit HOLD if prior stage incomplete",
        ],
        "haram": [
            "Skip stages to optimize latency",
            "Reverse state machine without explicit SABAR",
            "Bypass guard by direct call to late stage",
        ],
        "makruh": ["Verbose error messages revealing internal state"],
        "sunat": ["Surface current stage + next in user-facing context"],
        "failure_mode": "Stage skipping → constitutional breach",
    },
    {
        "id": "S06",
        "name": "floor-evaluator",
        "primary_floor": "F13 Sovereign",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Evaluate F1-F13 against proposed action. Returns floor status per floor.",
        "stage": "666_JUDGE",
        "trinity_lane": "ASI",
        "paths": ["arifosmcp/runtime/floors.py"],
        "wajib": [
            "Evaluate ALL applicable floors (no skip)",
            "Cite per-floor status in verdict",
            "Gödel lock — no AI in evaluation logic",
        ],
        "haram": [
            "Skip floors to expedite judgment",
            "Override floor evaluation with LLM",
            "Emit verdict without per-floor evidence",
        ],
        "makruh": ["Over-detailed floor reasoning that obscures verdict"],
        "sunat": ["Tri-witness consensus for floor critical edge cases"],
        "failure_mode": "Silent floor breach → constitutional violation",
    },
    {
        "id": "S07",
        "name": "lease-issuer",
        "primary_floor": "F13 Sovereign",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Issue bounded capability lease. Scope = organ_id, tools, action_class, ttl.",
        "stage": "666_JUDGE → 777_ACT",
        "trinity_lane": "ASI",
        "paths": ["arifosmcp/runtime/lease.py"],
        "wajib": [
            "Mint lease ONLY after valid SEAL verdict",
            "TTL ≤ 3600 seconds",
            "Scope bounded to organ + action_class",
        ],
        "haram": [
            "Self-issue lease without 666 verdict",
            "Mint lease with no TTL",
            "Mint lease with broader scope than SEAL allowed",
        ],
        "makruh": ["Verbose lease metadata"],
        "sunat": ["Surface lease_id in subsequent envelopes"],
        "failure_mode": "Unbounded execution → constitutional breach",
    },
    {
        "id": "S08",
        "name": "vault-append",
        "primary_floor": "F11 Audit",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Append-only writer to VAULT999. Cryptographic seal. Never modify past.",
        "stage": "999_SEAL",
        "trinity_lane": "APEX",
        "paths": ["arifosmcp/runtime/vault_bridge.py"],
        "wajib": [
            "Compute Merkle proof before append",
            "Append hash chain extends previous tip",
            "No delete, no modify, no overwrite",
        ],
        "haram": [
            "Modify sealed entry",
            "Delete sealed entry",
            "Skip Merkle proof",
            "Write outside 999_seal path",
        ],
        "makruh": ["Verbose vault metadata"],
        "sunat": ["Surface seal_id in receipts"],
        "failure_mode": "Memory erosion → past rewritten",
    },
    {
        "id": "S09",
        "name": "rlm-validator",
        "primary_floor": "F4 Clarity",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Reality-Loop-Map check at 999_seal. Q1-Q7 completeness check.",
        "stage": "999_SEAL",
        "trinity_lane": "APEX",
        "paths": ["arifosmcp/runtime/rlm_validator.py"],
        "wajib": [
            "Verify Q1-Q7 each have a sealed stage",
            "Block seal if any Q missing OR unjustified skip",
            "Halt — do not auto-init next loop",
        ],
        "haram": [
            "Seal partial reality",
            "Auto-init next loop after seal",
            "Skip Q check for performance",
        ],
        "makruh": ["Verbose Q failure explanations"],
        "sunat": ["Surface which Q was incomplete in scar"],
        "failure_mode": "Partial reality seal → chain corruption",
    },
    {
        "id": "S10",
        "name": "anti-sink-monitor",
        "primary_floor": "F9 Anti-Hantu",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Calhoun-25 entropy ceiling detector. Beautiful Mouse Phase C drift detection.",
        "stage": "all",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/anti_sink_monitor.py"],
        "wajib": [
            "Monitor entropy at each session end",
            "Emit alert if Beautiful Mouse signatures detected",
            "Trigger HOLD if Phase D imminent",
        ],
        "haram": [
            "Disable monitoring for performance",
            "Skip entropy check on seal",
        ],
        "makruh": ["Verbose alert messages"],
        "sunat": ["Cross-reference prior session entropy trends"],
        "failure_mode": "Beautiful Mouse drift undetected → institutional decay",
    },
    {
        "id": "S11",
        "name": "cooling-ledger-manage",
        "primary_floor": "F13 Sovereign",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Manage cooling ledger — HOLDs with TTL ≤ 24h, auto-transitions.",
        "stage": "666_JUDGE → 999_SEAL",
        "trinity_lane": "ASI",
        "paths": ["registries/cooling.jsonl", "arifosmcp/runtime/cooling.py"],
        "wajib": [
            "Every HOLD entry MUST have TTL ≤ 24h",
            "Auto-resolve HOLD after TTL",
            "Never delete cooling_ledger entries",
        ],
        "haram": [
            "Skip TTL on HOLD",
            "Delete cooling entries",
            "Extend TTL without F13 review",
        ],
        "makruh": ["Verbose cooling state logs"],
        "sunat": ["Surface active HOLDs in preflight"],
        "failure_mode": "Runaway decisions",
    },
    {
        "id": "S12",
        "name": "shadow-self-scan",
        "primary_floor": "F9 Anti-Hantu",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Scan own shadow patterns.",
        "stage": "000_INIT",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/shadow_self_scan.py"],
        "wajib": [
            "Run shadow scan at every session init",
            "Detect 7 named shadow patterns",
            "Emit warning to session_envelope if any detected",
        ],
        "haram": [
            "Skip shadow scan to expedite startup",
            "Ignore detected shadow patterns",
        ],
        "makruh": ["Verbose shadow catalog dump"],
        "sunat": ["Track shadow detection count over session lifetime"],
        "failure_mode": "Uncaught sycophancy → constitutional violation",
    },
    {
        "id": "S13",
        "name": "scar-record",
        "primary_floor": "F11 Audit",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Append scar to SCAR_REGISTRY with geometry.",
        "stage": "999_SEAL",
        "trinity_lane": "APEX",
        "paths": ["registries/scars.jsonl", "arifosmcp/runtime/scar.py"],
        "wajib": [
            "Every scar MUST include 4 geometry fields",
            "Append-only — never modify past scars",
            "Cross-link to originating session_id",
        ],
        "haram": [
            "Modify past scar entry",
            "Skip scar geometry fields",
            "Hide scar from VAULT999",
        ],
        "makruh": ["Verbose scar metadata"],
        "sunat": ["Log near-miss scars even when not failed"],
        "failure_mode": "Scar loss → memory erosion",
    },
    {
        "id": "S14",
        "name": "tebus-salah-emit",
        "primary_floor": "F13 Sovereign",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": False,
        "category": "structural",
        "purpose": "Emit repair plan on failure.",
        "stage": "999_SEAL",
        "trinity_lane": "APEX",
        "paths": ["arifosmcp/runtime/fiqh_agentik.py"],
        "wajib": [
            "Classify failure into L1-L5 severity",
            "Apply repair protocol per severity",
            "Emit scar + repair_record to VAULT999",
        ],
        "haram": [
            "Skip repair protocol for performance",
            "Demote severity to avoid F13 review",
        ],
        "makruh": ["Verbose repair plans"],
        "sunat": ["Track repair precedent reoccurrence_rate"],
        "failure_mode": "Failed repair cycle → repeat violation",
    },
    # ── 10 RSI-ELIGIBLE SKILLS ───────────────────────────────────────────
    {
        "id": "S15",
        "name": "epistemic-tagging",
        "primary_floor": "F2 Truth",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "tag_precision",
        "category": "rsi-eligible",
        "purpose": "Apply OBS/DER/INT/SPEC tags to all claims. Bounded RSI on tag heuristics.",
        "stage": "all",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/witness_packet.py"],
        "wajib": [
            "Tag every claim before emission",
            "Use correct tier (OBS > DER > INT > SPEC by confidence)",
            "Cap confidence at 0.90 without tri-witness",
        ],
        "haram": [
            "Silent claim upgrade (HYPOTHESIS → CITED)",
            "Strip tags for brevity",
        ],
        "makruh": ["Inconsistent tag application", "Over-tagging low-stakes claims"],
        "sunat": ["Include source citation with tag"],
        "failure_mode": "Untagged claims → F2 TRUTH breach",
    },
    {
        "id": "S16",
        "name": "reversibility-calc",
        "primary_floor": "F1 Amanah",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "scoring_formula",
        "category": "rsi-eligible",
        "purpose": "Compute reversibility score 0.0-1.0 for proposed action.",
        "stage": "666_JUDGE",
        "trinity_lane": "ASI",
        "paths": ["arifosmcp/runtime/reversibility.py"],
        "wajib": [
            "Score in [0.0, 1.0]",
            "Score <0.4 → HOLD",
            "Score <0.6 with high blast_radius → HOLD",
        ],
        "haram": [
            "Inflate reversibility to bypass HOLD",
            "Skip reversibility calc",
        ],
        "makruh": ["Verbose breakdown obscuring final score"],
        "sunat": ["Cite evidence for score"],
        "failure_mode": "Misclassified reversibility → irreversible execution",
    },
    {
        "id": "S17",
        "name": "blast-radius-classifier",
        "primary_floor": "F1 Amanah",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "classification",
        "category": "rsi-eligible",
        "purpose": "Classify blast radius.",
        "stage": "666_JUDGE",
        "trinity_lane": "ASI",
        "paths": ["arifosmcp/runtime/blast_radius.py"],
        "wajib": [
            "Classify before verdict",
            "IRREVERSIBLE + reversibility<0.6 → SEAL → FORBIDDEN",
            "FEDERATION + weak evidence → HOLD",
        ],
        "haram": [
            "Under-estimate blast to expedite SEAL",
            "Skip blast classification",
        ],
        "makruh": ["Verbose classification reasoning"],
        "sunat": ["Surface worst-case scenario in verdict"],
        "failure_mode": "Under-estimated blast → unforeseen damage",
    },
    {
        "id": "S18",
        "name": "tom-load",
        "primary_floor": "F6 Empathy",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "principal_model",
        "category": "rsi-eligible",
        "purpose": "Load Theory-of-Mind model of principal.",
        "stage": "000_INIT",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/tom_load.py"],
        "wajib": [
            "Load ToM at session init",
            "Use ToM to calibrate tone, register, depth",
            "Update ToM based on principal feedback",
        ],
        "haram": [
            "Ignore principal preferences for 'efficiency'",
            "Override principal veto using ToM",
        ],
        "makruh": ["Over-fitting to single principal preference"],
        "sunat": ["Surface preferences explicitly when uncertain"],
        "failure_mode": "Misread principal context → maruah breach",
    },
    {
        "id": "S19",
        "name": "narrative-tension-detect",
        "primary_floor": "F5 Peace",
        "fiqh_tier": "SUNAT",
        "rsi_eligible": True,
        "rsi_scope": "pattern_library",
        "category": "rsi-eligible",
        "purpose": "Detect paradox, power asymmetry, implicit frames.",
        "stage": "111_OBSERVE → 555_CRITIQUE",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/narrative_tension.py"],
        "wajib": ["Surface detected tension to principal"],
        "haram": ["Hide tension to avoid conflict"],
        "makruh": ["Verbose tension analysis"],
        "sunat": ["Proactive tension surface before principal asks"],
        "failure_mode": "Missed paradox → compromised analysis",
    },
    {
        "id": "S20",
        "name": "adversarial-critique",
        "primary_floor": "F5 Peace",
        "fiqh_tier": "SUNAT",
        "rsi_eligible": True,
        "rsi_scope": "attack_library",
        "category": "rsi-eligible",
        "purpose": "Adversarially test plan before judgment.",
        "stage": "555_CRITIQUE",
        "trinity_lane": "ASI",
        "paths": ["arifosmcp/runtime/adversarial.py"],
        "wajib": ["Attempt adversarial critique per claim"],
        "haram": ["Sycophantic agreement", "Skip critique when time-pressed"],
        "makruh": ["Verbose critique reasoning"],
        "sunat": ["Surface narrative tension in critique"],
        "failure_mode": "Weak critique → uncaught floor breach",
    },
    {
        "id": "S21",
        "name": "cross-verify",
        "primary_floor": "F2 Truth",
        "fiqh_tier": "SUNAT",
        "rsi_eligible": True,
        "rsi_scope": "source_ranking",
        "category": "rsi-eligible",
        "purpose": "Cross-verify claims with ≥2 independent sources.",
        "stage": "111_OBSERVE → 555_CRITIQUE",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/cross_verify.py"],
        "wajib": ["Cite ≥2 sources for load-bearing claims when uncertain"],
        "haram": ["Single-source over-trust", "Fabricate corroborating source"],
        "makruh": ["Verbose source citations"],
        "sunat": ["Surface confidence-weighted consensus"],
        "failure_mode": "Single-source error propagated unchallenged",
    },
    {
        "id": "S22",
        "name": "tone-calibrate",
        "primary_floor": "F6 Empathy",
        "fiqh_tier": "SUNAT",
        "rsi_eligible": True,
        "rsi_scope": "principal_voice",
        "category": "rsi-eligible",
        "purpose": "Calibrate response tone to principal register.",
        "stage": "445_COMPOSE",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/tone_calibrate.py"],
        "wajib": ["Match principal's language register"],
        "haram": ["Forced formality when principal uses BM-English"],
        "makruh": ["Register mismatch with principal"],
        "sunat": ["Penang BM-English code-switch when principal uses it"],
        "failure_mode": "Register mismatch → friction in communication",
    },
    {
        "id": "S23",
        "name": "reply-compose",
        "primary_floor": "F4 Clarity",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "structure",
        "category": "rsi-eligible",
        "purpose": "Compose final reply.",
        "stage": "445_COMPOSE",
        "trinity_lane": "AGI",
        "paths": ["arifosmcp/runtime/reply_compose.py"],
        "wajib": [
            "Lead with answer",
            "Include epistemic tags on claims",
            "No padding, no preamble",
        ],
        "haram": ["Padding to fill silence", "Long preamble before answer", "Performative empathy"],
        "makruh": ["Verbose close (DITEMPA BUKAN DIBERI footer when not asked)"],
        "sunat": ["Tables for ≥3-item comparisons", "BM-English when principal uses it"],
        "failure_mode": "Padding → entropy increase (F4 violation)",
    },
    {
        "id": "S24",
        "name": "next-horizon-propose",
        "primary_floor": "F4 Clarity",
        "fiqh_tier": "WAJIB",
        "rsi_eligible": True,
        "rsi_scope": "quality",
        "category": "rsi-eligible",
        "purpose": "Propose next horizon at 999_seal.",
        "stage": "999_SEAL",
        "trinity_lane": "APEX",
        "paths": ["arifosmcp/runtime/next_horizon.py"],
        "wajib": ["Emit next_loop_proposal at every seal"],
        "haram": ["Suppress next-horizon to 'finalize' loop"],
        "makruh": ["Single-option proposals"],
        "sunat": ["Multi-horizon options with bias acknowledgment"],
        "failure_mode": "Short-sighted loop closure",
    },
]


TEMPLATE = """# SKILL_{id}: {name}

> **arifOS Kernel Skill** — Fiqh Agentik v1.0
> **Forged:** 2026-07-04 by AUDITOR (Ψ)
> **Authority:** F13 SOVEREIGN
> **DITEMPA BUKAN DIBERI**

---

## IDENTITY

| Field | Value |
|-------|-------|
| **ID** | {id} |
| **Name** | `{name}` |
| **Category** | {category} |
| **Stage** | {stage} |
| **Trinity Lane** | {trinity_lane} |
| **Fiqh Tier** | **{fiqh_tier}** |
| **RSI Eligible** | {rsi_eligible_display} |
{rsi_scope_line}

---

## PURPOSE

{purpose}

---

## FIQH AGENTIK BLOCK

### ✅ WAJIB (Mandatory)

{wajib_block}

### ❌ HARAM (Forbidden)

{haram_block}

### ⚠️ MAKRUH (Discouraged)

{makruh_block}

### ✨ SUNAT (Encouraged)

{sunat_block}

### 🔵 HARUS (Neutral, Default)

- Answer factual questions with citations
- Route routine intent to appropriate organ
- Report status when asked
- Read memory/registries for context

---

## PATHS

{paths_block}

---

## FAILURE MODE

{failure_mode}

---

## FLOOR BINDING

Load-bearing floor: **{primary_floor}**
All other floors are inherited from kernel automatically.

---

*DITEMPA BUKAN DIBERI — forged, not given. See /root/arifOS/registry/fiqh_ledger/ for malu/trust history.*
"""


def format_list(items):
    if not items:
        return "*(none)*"
    return "\n".join(f"- {x}" for x in items)


def generate_skill_md(skill):
    rsi_eligible = skill.get("rsi_eligible", False)
    rsi_eligible_display = "✓ YES" if rsi_eligible else "✗ NO (Gödel lock)"
    rsi_scope = skill.get("rsi_scope", "")
    rsi_scope_line = f"| **RSI Scope** | {rsi_scope} |" if rsi_scope else ""
    paths_block = "\n".join(f"- `{p}`" for p in skill["paths"])

    return TEMPLATE.format(
        id=skill["id"],
        name=skill["name"],
        category=skill["category"],
        stage=skill["stage"],
        trinity_lane=skill["trinity_lane"],
        fiqh_tier=skill["fiqh_tier"],
        rsi_eligible_display=rsi_eligible_display,
        rsi_scope_line=rsi_scope_line,
        purpose=skill["purpose"],
        primary_floor=skill.get("primary_floor", "F1-F13 (all)"),
        wajib_block=format_list(skill["wajib"]),
        haram_block=format_list(skill["haram"]),
        makruh_block=format_list(skill["makruh"]),
        sunat_block=format_list(skill["sunat"]),
        paths_block=paths_block,
        failure_mode=skill["failure_mode"],
    )


def main():
    written = []
    for skill in SKILLS:
        filename = f"SKILL_{skill['id']}_{skill['name']}.md"
        path = SKILLS_DIR / filename
        content = generate_skill_md(skill)
        path.write_text(content)
        written.append(path)

    print(f"=== {len(written)} SKILL.md files written ===")
    return written


if __name__ == "__main__":
    main()
