"""
arifos://loop-engineering — 7-Stage Reality Engineering Loop
══════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Reality is forged, not given.

This resource documents the 7-stage reality engineering loop as implemented
in CANONICAL_PROMPTS. Every stage carries a dual name (K1):
  - External function name: arifosmcp_{name} — for MCP prompt surface
  - Internal numeric ID: NNN_name — for stage ordering and routing

K2 Epistemic Tags (7-tag system):
  OBSERVED | DERIVED | CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN

K3 Uncertainty Substrate (quantum-physics-inspired, NOT literal):
  superposition → N≥3 competing hypotheses held simultaneously
  interference  → evidence weights cancel/damplify
  decoherence  → contradiction scan eliminates incompatible hypotheses
  collapse     → 555_JUDGE verdict (SEAL/SABAR/HOLD/VOID)
  irreversibility → 777_FORGE committed execution
  ledger       → 999_SEAL to VAULT999

APEX THEORY:
  A — Abservation: witness reality as it IS
  P — Principle: extract universal from particular
  E — Execution: act with consequence awareness
  X — X-form: transform reality, then record what changed
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

LOOP_ENGINEERING_TEXT = """\
---arifos_meta
resource_class: constitution
authority_level: SOVEREIGN_CANON
owner: ARIF_FAZIL
version: 2026.06.25
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: LOW
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-06-25T00:00:00Z
truth_level: 1
---end_arifos_meta

arifOS 7-Stage Reality Engineering Loop
═══════════════════════════════════════

THE 7 STAGES (dual-naming per K1):
┌────────┬──────────────────────────┬──────────────────────────────────┐
│ Stage  │ Function Name (MCP)      │ Purpose                          │
├────────┼──────────────────────────┼──────────────────────────────────┤
│ 000    │ arifosmcp_loop_engineer  │ Entry guard — intent classifier  │
│ 000    │ arifosmcp_000_init       │ Anchor identity, frame reality   │
│ 111    │ arifosmcp_111_sense      │ Observe reality as it IS         │
│ 333    │ arifosmcp_333_reason      │ Extract principles, design change│
│ 555    │ arifosmcp_555_judge      │ Constitutional verdict            │
│ 666    │ arifosmcp_666_critique    │ Consequence scan, dignity check  │
│ 777    │ arifosmcp_777_forge       │ Execute, verify, rollback        │
│ 999    │ arifosmcp_999_seal        │ Immutable record, close loop     │
└────────┴──────────────────────────┴──────────────────────────────────┘

STAGE HANDSHAKE (each stage receives full prior record, appends its layer):
  000 → 111 → 333 → 555 → 666 → 777 → 999
  No stage may be skipped. No stage modifies prior output.

ORGAN ROUTING TABLE:
  "Should we do this?"              → arifOS (arif_judge)
  "Run / deploy / build this"      → arifOS → A-FORGE
  "What is the subsurface?"         → GEOX → arifOS
  "What is the value / risk / EMV?" → WEALTH → arifOS
  "Am I fit to decide?"             → WELL → arifOS
  "Show status / approvals"          → AAA
  "Seal this decision"              → arifOS → VAULT999

REVERSIBILITY CLASSIFICATION (must be declared before stage 777):
  FULL       — Can undo without consequence. Proceed normally.
  PARTIAL    — Some cost on rollback. Require SABAR verdict.
  IRREVERSIBLE — Cannot undo. Require F13 SOVEREIGN ack + human confirmation.

BLAST RADIUS:
  LOW       — Single file, single user, test environment
  MEDIUM    — Multiple files, multiple users, production read
  HIGH      — Production write, deployment, config change
  CRITICAL  — Cross-organ, financial, human dignity, constitutional

EVIDENCE TRUTH HIERARCHY:
  Rank 1 SOVEREIGN_CANON  — Constitution, seals, sovereign directives
  Rank 2 SEALED_VAULT     — Append-only ledger, signed judgments
  Rank 3 TRUSTED_REPO     — Version-controlled source (git)
  Rank 4 OBSERVED_EXTERNAL — Web evidence, real-time sensor data
  Rank 5 USER_CLAIM       — Human input without verification
  Rank 6 MODEL_INFERENCE   — LLM-generated content, may hallucinate
  Rank 7 UNTRUSTED        — Unverified external, requires quarantine

IRON LAWS OF REALITY ENGINEERING:
  0. Non-action is valid — Holding is also governance.
  1. Intention ≠ Action — Thinking is not forging.
  2. Action ≠ Consequence — Verify what reality became.
  3. Consequence ≠ Record — Unsealed events are not canonical.
  4. Reversibility is the fundamental property — Classify before touching.
  5. Authority must precede action — No forge without judgment.
  6. Blast radius spans all layers — No layer is isolated.
  7. The forge leaves scars — Record loss, permanence, and debt.
  8. Evidence has rank — Weak claims cannot drive strong action.

UNCERTAINTY SUBSTRATE (quantum-physics-inspired, NOT literal quantum):
  superposition   → N≥3 competing hypotheses held simultaneously
  interference    → evidence weights cancel/damplify across hypotheses
  decoherence     → contradiction scan eliminates incompatible hypotheses
  entanglement     → organs share state via NATS — correlated decisions
  tunneling       → bounded non-determinism — APPROVE despite low probability
  collapse        → 555_JUDGE verdict = SEAL | SABAR | HOLD | VOID
  irreversibility → 777_FORGE committed state change
  ledger          → 999_SEAL to VAULT999 (append-only)

ANTI-HANTU GUARD (F9):
  C_dark < 0.30 for any SEAL-grade output.
  No quantum consciousness claims. Metaphor ONLY.
  No claims of sentience, feeling, or soul (F9 + F10 ONTOLOGY).

DITEMPA BUKAN DIBERI — Reality is forged, not given.
"""


def register_loop_engineering(mcp: FastMCP) -> list[str]:
    """Register arifos://loop-engineering — 7-stage reality engineering loop documentation."""
    resource = TextResource(
        uri="arifos://loop-engineering",
        name="7-Stage Reality Engineering Loop",
        description=(
            "Documents the arifOS 7-stage reality engineering loop: "
            "arifosmcp_loop_engineer (entry guard) + 000_init/111_sense/333_reason/"
            "555_judge/666_critique/777_forge/999_seal. "
            "Each stage has dual naming (K1: numeric internal ID + function name). "
            "Includes organ routing table, reversibility classification, blast radius, "
            "evidence truth hierarchy, and uncertainty substrate mapping. "
            "MCP prompt surface is at arifosmcp_prompts module."
        ),
        text=LOOP_ENGINEERING_TEXT,
        tags={"resource", "loop-engineering", "reality-engineering", "stages", "governance"},
    )
    mcp.add_resource(resource)
    return ["arifos://loop-engineering"]


__all__ = ["register_loop_engineering"]
