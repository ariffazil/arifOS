"""
arifos://loop-engineering — 13-Hook Governed Prompt Ladder
══════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Reality is forged, not given.

This resource documents the live 13-hook prompt ladder.
The 2026-06-25 7-stage table is superseded as of 2026-11-10.
Wire ids are ASCII slugs. Stage keys stay numeric.
Run order puts s888_judge before s777_forge.
s666_dignity is advisory while F6 is unmeasured.

K2 Epistemic Tags (7-tag system):
  OBSERVED | DERIVED | CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN

K3 Uncertainty Substrate (quantum-physics-inspired, NOT literal):
  superposition → N≥3 competing hypotheses held simultaneously
  interference  → evidence weights cancel/damplify
  decoherence  → contradiction scan eliminates incompatible hypotheses
  collapse        → s888_judge verdict token (SEAL/SABAR/HOLD/VOID). Not a vault write.
  irreversibility → s777_forge runs after that verdict token
  ledger          → s999_seal vault append, human ack required

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
version: 2026.11.10
mutation_allowed: false
requires_actor_verified: false
requires_session: false
lease_required: false
blast_radius: LOW
evidence_level: CANONICAL
staleness_policy: fail_closed
last_attested: 2026-11-10T04:17:00Z
truth_level: 1
---end_arifos_meta

arifOS 13-Hook Governed Prompt Ladder
═══════════════════════════════════════

LIVE 13-HOOK LADDER (wire id, run order):
  s_govern       sequence only; this prompt does not enforce gates
  s_init         session ignition, five tools
  s000_ignite    identity only
  s111_sense     observe
  s222_plan      plan
  s333_reason    hypotheses
  s444_direct    route
  s555_remember  memory
  s666_dignity   advisory while F6 is unmeasured
  s888_judge     verdict token
  s777_forge     execute after the verdict token
  s999_seal      vault append, human ack required
  s_close        close; vault append waits for a human ack

Registration order still lists s777_forge before s888_judge.
Run order is judge, then forge.
arif_report coordinates and is not a stage.

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
  collapse        → s888_judge verdict token (SEAL/SABAR/HOLD/VOID). Not a vault write.
  irreversibility → s777_forge runs after that verdict token
  ledger          → s999_seal vault append, human ack required

ANTI-HANTU GUARD (F9):
  C_dark < 0.30 for any SEAL-grade output.
  No quantum consciousness claims. Metaphor ONLY.
  No claims of sentience, feeling, or soul (F9 + F10 ONTOLOGY).

DITEMPA BUKAN DIBERI — Reality is forged, not given.
"""


def register_loop_engineering(mcp: FastMCP) -> list[str]:
    """Register arifos://loop-engineering — 13-hook governed prompt ladder."""
    resource = TextResource(
        uri="arifos://loop-engineering",
        name="13-Hook Governed Prompt Ladder",
        description=(
            "13-hook governed prompt ladder. The 2026-06-25 7-stage table is superseded "
            "as of 2026-11-10. Run order puts s888_judge before s777_forge. "
            "s666_dignity is advisory while F6 is unmeasured. "
            "Includes organ routing, reversibility, blast radius, evidence ranks, "
            "and the uncertainty substrate. Verdict token and vault write are different."
        ),
        text=LOOP_ENGINEERING_TEXT,
        tags={"resource", "loop-engineering", "reality-engineering", "stages", "governance"},
    )
    mcp.add_resource(resource)
    return ["arifos://loop-engineering"]


__all__ = ["register_loop_engineering"]
