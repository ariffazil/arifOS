"""
arifOS MCP Prompts — 13 Governed Agentic Intelligence Hooks.

Numbered 000-999 with a 000→999 ladder. Each hook is ONE @mcp.prompt
decorator + function. No version numbers — hooks are institution-
inclusive, not dated.

Hooks frame work; they do not execute tools, judge, forge, or seal.
The kernel and A-FORGE retain those capabilities behind their normal
session, authority, and lease gates.

Linked tools/resources live in the `meta` field on each `@mcp.prompt(...)`.
FastMCP passes this through to MCP clients as `_meta` (per FastMCP 2.11+).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.prompts import Message, PromptResult

logger = logging.getLogger(__name__)
# Canonical INIT path — 12 orthogonal layers, init→seal→RSI→reality loop
_INIT_CANON = _AGENT_INIT_V3_CANON = (
    "/root/AAA/prompts/INIT.md"  # keep legacy alias for compat
)


# ─── 13-hook pipeline — the 000-999 governed ladder ────────────────────
# Each hook:
#   - one number + one emoji sigil + one ALL-CAPS lexical
#   - meta: stage, sigil, lexical, role, linked_tools, linked_resources,
#           floors_referenced, federation_layer
# Hooks compose the governed agentic intelligence loop.

PIPELINE_STAGES = (
    "000_IGNITE",
    "111_SENSE",
    "222_PLAN",
    "333_REASON",
    "444_DIRECT",
    "555_REMEMBER",
    "666_DIGNITY",
    "777_FORGE",
    "888_JUDGE",
    "999_SEAL",
    "GOVERN",
    "INIT",
    "CLOSE",
)
PIPELINE_SIGILS = ("🌱", "🌊", "🏛", "🧠", "🧭", "🗂", "⚖", "🔥", "🔒", "💎", "🌀", "⚓", "🔐")
STAGE_TO_SIGIL = dict(zip(PIPELINE_STAGES, PIPELINE_SIGILS, strict=True))


def _linked_prompt(
    stage: str,
    sigil: str,
    lexical: str,
    role: str,
    linked_tools: list[str],
    linked_resources: list[str],
    floors: str,
    intent_text: str,
) -> dict:
    """Build a PromptResult for one hook of the governed 000-999 ladder.

    The `meta` field carries:
      - stage: PIPELINE_STAGES slot
      - linked_tools: arifOS MCP tool names to invoke at this hook
      - linked_resources: arifos:// URIs to consume at this hook
      - floors_referenced: F1-F13 floor IDs this hook primarily exercises
      - sigil + lexical: hook name components
      - role: short human-readable role label
    """
    name = f"{sigil} {lexical}"
    return {
        "name": name,
        "description": (
            f"{role} — {stage} of the arifOS reality loop. "
            f"Suggested tools: {', '.join(linked_tools)}. "
            f"Suggested resources: {', '.join(linked_resources)}. "
            f"Floors: {floors}."
        ),
        "meta": {
            "stage": stage,
            "sigil": sigil,
            "lexical": lexical,
            "role": role,
            "linked_tools": linked_tools,
            "linked_resources": linked_resources,
            "floors_referenced": floors,
            "federation_layer": "arifOS.kernel.prompts",
        },
        "intent_text": intent_text,
    }


# ─── SABAR Orchestrator: runs the 6-stage loop autonomously ────────────
def sabar_run_loop(
    intent: str,
    *,
    session_id: str | None = None,
    actor_id: str | None = "arif",
    depth: str = "stage",
) -> PromptResult:
    """🌀 SABAR orchestrator — drives the 6-stage reality loop.

    Stages:
      1. 🌊 WITNESS  — observe (arif_observe, geox_evidence, well_validate_vitality)
      2. 🧠 REASON   — propose hypothesis (arif_think mode=reason)
      3. ⚖ MARUAH  — dignity check (arif_think mode=reflect, well_guard_dignity)
      4. 🔒 JUDGE    — constitutional gate (arif_judge, geox_contradiction_scan, geox_falsify)
      5. 🔥 FORGE    — execute after SEAL/SABAR verdict (arif_forge)
      6. 💎 SEAL     — persist (arif_seal)

    depth='stage'  → human-in-loop: agent completes one stage, hands off.
    depth='auto'   → AUTONOMOUS: agent chains all 6 stages without stopping
                      at stage boundaries. Only HOLD/VOID gates pause the loop.

    Receipt tiering (autonomous mode):
      NONE (agent alone)   → PROVISIONAL — telemetry only
      PARTIAL (1 witness)  → LEDGER
      ≥2 independent       → SEAL eligible
    The loop can stack PROVISIONAL receipts all night. Human review
    converts a batch to SEAL. Agent never upgrades its own record class.

    F2 PROVENANCE GATE (non-bypassable, active in autonomous mode):
      Every epistemic tag (OBS/DER/INT/SPEC) MUST trace to a retrieval
      event with provenance_source. Tags invented at output time → VOID.
    """
    depth = (depth or "stage").lower()
    if depth == "auto":
        return PromptResult(
            messages=[
                Message(
                    f"AUTONOMOUS REALITY LOOP — 🌀 SABAR (depth=auto)\n"
                    f"intent: {intent}\n"
                    f"session_id: {session_id or 'pending'}\n"
                    f"actor_id: {actor_id or 'anonymous'}\n\n"
                    "EXECUTE ALL 6 STAGES WITHOUT STOPPING AT BOUNDARIES.\n"
                    "Do not ask. Do not wait. Do not hand off between stages.\n"
                    "The loop runs until: (a) all 6 stages complete, or\n"
                    "(b) a HOLD/VOID gate fires.\n\n"
                    "═══ TIERED RECEIPT DISCIPLINE ═══\n"
                    "Record every stage receipt to arifflow_flow_ingest.\n"
                    "Receipt class is capped by witness diversity:\n"
                    "  NONE (agent alone)   → PROVISIONAL\n"
                    "  PARTIAL               → LEDGER\n"
                    "  ≥2 independent        → SEAL eligible\n\n"
                    "═══ F2 PROVENANCE GATE ═══\n"
                    "Before JUDGE: verify every OBS/DER/INT/SPEC tag\n"
                    "has provenance_source from a retrieval event.\n"
                    "Tags without provenance → VOID. Do not seal.\n"
                    "ΔS is UNMEASURED unless a meter exists.\n\n"
                    "═══ STAGE SEQUENCE ═══\n"
                    "1. 🌊 WITNESS: arif_observe(mode=vitals) + geox_evidence\n"
                    "   + well_validate_vitality. Output WITNESS block with\n"
                    "   provenance_source on every tag.\n"
                    "2. 🧠 REASON: arif_think(mode=reason). Extract principles.\n"
                    "   Propose hypothesis. Hand evidence to next stage.\n"
                    "3. ⚖ MARUAH: arif_think(mode=reflect) + well_guard_dignity.\n"
                    "   Consequence scan. Weakest stakeholder check.\n"
                    "4. 🔒 JUDGE: arif_judge + geox_contradiction_scan +\n"
                    "   geox_falsify. Emit SEAL|HOLD|SABAR|VOID with\n"
                    "   provenance_verified field.\n"
                    "5. 🔥 FORGE: arif_forge (only if verdict=SEAL|SABAR).\n"
                    "   Execute governed mutation. Verify reversibility.\n"
                    "6. 💎 SEAL: arif_seal (only if FORGE complete +\n"
                    "   witness diversity ≥2 or human ack).\n\n"
                    "═══ GATE BEHAVIOR ═══\n"
                    "VOID at any stage → HALT entire loop. Record scar.\n"
                    "HOLD at JUDGE → return to WITNESS with named failures.\n"
                    "HOLD at FORGE → escalate to human (888_HOLD).\n"
                    "FQ < 0.5 → ALL agents HOLD until recovery.\n\n"
                    "This prompt grants no judgment, execution, or seal\n"
                    "authority on its own. Every tool keeps its kernel and\n"
                    "sovereign gates. The loop is a RATED conveyor, not\n"
                    "a blank check.",
                    role="user",
                ),
                Message(
                    "🌀 SABAR autonomous loop engaged. Executing all 6 stages "
                    "without boundary stops. Recording receipts at "
                    "witness-diversity-capped tiers. Will halt only on "
                    "HOLD/VOID gates or FQ < 0.5.",
                    role="assistant",
                ),
            ],
            description="🌀 SABAR autonomous reality-loop orchestrator (depth=auto) — rated conveyor",
            meta={
                "stage": "000_LOOP",
                "sigil": "🌀",
                "lexical": "SABAR",
                "role": "Autonomous 6-stage reality loop orchestrator",
                "depth": "auto",
                "receipt_tiers": ["PROVISIONAL", "LEDGER", "SEAL"],
                "f2_provenance_gate": True,
                "linked_tools": [
                    "arif_observe",
                    "geox_evidence",
                    "well_validate_vitality",
                    "arif_think",
                    "well_guard_dignity",
                    "arif_judge",
                    "geox_contradiction_scan",
                    "geox_falsify",
                    "arif_forge",
                    "arif_seal",
                    "arifflow_flow_ingest",
                ],
                "linked_resources": [
                    "arifos://verdict/{session_id}",
                    "arifos://continuity/{session_id}",
                    "arifos://vitals",
                    "arifos://init/agent_init",
                ],
                "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
                "federation_layer": "arifOS.kernel.prompts",
            },
        )
    # depth='stage' — multi-message instruction for human-in-loop
    return PromptResult(
        messages=[
            Message(
                f"🌀 SABAR — Realize the intent through the 6-stage reality loop.\n\n"
                f"intent: {intent}\n"
                f"session_id: {session_id or 'pending'}\n\n"
                f"Sequence these 6 stages. At each stage:\n"
                f"  - Read the linked arifOS tools (meta.linked_tools)\n"
                f"  - Load the linked resources (meta.linked_resources)\n"
                f"  - Record a stage receipt\n"
                f"  - Pass to next stage\n\n"
                "After all 6 stages, return the evidence to the authorized actor for "
                "any final seal.\n"
                f"This prompt grants no judgment, execution, or seal authority.",
                role="user",
            ),
            Message(
                "Initiating 🌊 WITNESS by requesting arif_observe and geox_evidence. "
                "Will return at stage 1/6.",
                role="assistant",
            ),
        ],
        description="🌀 SABAR — Recursive Governed Loop orchestrator (depth=stage)",
        meta={
            "stage": "000_LOOP",
            "sigil": "🌀",
            "lexical": "SABAR",
            "role": "Recursive Governed Loop orchestrator",
            "depth": "stage",
            "linked_tools": [
                "arif_observe",
                "geox_evidence",
                "well_validate_vitality",
                "arif_think",
                "well_guard_dignity",
                "arif_judge",
                "geox_contradiction_scan",
                "arif_forge",
                "arif_seal",
            ],
            "linked_resources": [
                "arifos://verdict/{session_id}",
                "arifos://continuity/{session_id}",
                "arifos://vitals",
                "arifos://init/agent_init",
            ],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )


def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register the 13 governed agentic intelligence hooks (000-999 ladder).

    Numbered hooks (000-999):
      000 🌱 IGNITE  — Identity before action. VOID is final without new evidence.
      111 🌊 SENSE   — Reality before judgment. Verify before integrate.
      222 🏛 PLAN    — Design reality change. Map reversibility.
      333 🧠 REASON  — UNMEASURED beats fabricated certainty.
      444 🧭 DIRECT  — Route to the institution with authority, not the one with speed.
      555 🗂 REMEMBER — Memory without provenance is not truth.
      666 ⚖ DIGNITY — Stand in the position of the weakest stakeholder.
      777 🔥 FORGE   — Reality contact before belief. Mutation after SEAL only.
      888 🔒 JUDGE   — Verdict, not invention. VOID = branch dead.
      999 💎 SEAL    — Immutable record. Hash-chained. Cannot be undone.

    Full-loop hook:
      🌀 GOVERN — Full loop + 4 invariant enforcement gates.

    Bootstrap hooks:
      ⚓ INIT — opencode /init command (collapsed 4-step governed ignition).
      🔐 CLOSE — opencode /seal command (full autonomous session close ritual).

    Returns list of registered prompt names.
    """
    registered: list[str] = []

    # ─── 000 🌱 IGNITE — Identity before action ─────────────────────────
    @mcp.prompt(
        name="000 🌱 IGNITE",
        description="Identity before action. VOID is final without new evidence.",
        meta={
            "stage": "000_IGNITE",
            "sigil": "🌱",
            "lexical": "IGNITE",
            "role": "Identity ignition — bind actor before any action",
            "linked_tools": ["arif_init"],
            "linked_resources": ["arifos://identity", "arifos://carry-forward"],
            "floors_referenced": "F1,F7,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_000_ignite(actor_id: str, intent: str) -> str:
        """000 🌱 IGNITE — Identity before action. VOID is final without new evidence."""
        return f"""000 🌱 IGNITE — Identity ignition hook

actor_id: {actor_id}
intent: {intent}

## Invariant
Identity before action. VOID is final without new evidence.

## What to do
1. Call arif_init(actor_id='{actor_id}') → bind identity to session.
2. Verify identity binding returned a valid session_id.
3. If binding fails → HALT. Do not proceed without identity.
4. Load carry-forward from prior session: arifos://carry-forward
5. Confirm identity matches F13 SOVEREIGN authority.

## Floors
F1 AMANAH — attestation is the first act.
F7 HUMILITY — acknowledge uncertainty before identity claim.
F11 AUTH — identity verified before any destructive action.
F13 SOVEREIGN — recognize Arif = F13 = absolute veto.

## Output
Return an IGNITE block:
  identity_bound: true|false
  session_id: <string>
  actor_id: <string>
  carry_forward_loaded: true|false
  next_stage: 111 SENSE
"""

    registered.append("000 🌱 IGNITE")

    # ─── 111 🌊 SENSE — Reality before judgment ──────────────────────────
    @mcp.prompt(
        name="111 🌊 SENSE",
        description="Reality before judgment. Verify before integrate.",
        meta={
            "stage": "111_SENSE",
            "sigil": "🌊",
            "lexical": "SENSE",
            "role": "Sense reality — observe signals before reasoning",
            "linked_tools": ["arif_observe"],
            "linked_resources": ["arifos://epistemic", "arifos://reality/state"],
            "floors_referenced": "F2,F3,F9",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_111_sense(query: str, focus: str = "") -> str:
        """111 🌊 SENSE — Reality before judgment. Verify before integrate."""
        focus_clause = f" Focus on: {focus}." if focus else ""
        return f"""111 🌊 SENSE — Reality observation hook

query: {query}{focus_clause}

## Invariant
Reality before judgment. Verify before integrate.

## What to do
1. Call arif_observe(query='{query}') → capture kernel observations.
2. Load arifos://epistemic → current epistemic state.
3. Load arifos://reality/state → ground-truth signals.
4. Every observation MUST carry provenance_source, confidence, staleness, epistemic_tag.
5. Tags assigned at retrieval, not at output time.

## Floors
F2 TRUTH — provenance-bound labels, no fabrication.
F3 WITNESS — human, AI, and earth signals must align.
F9 ANTI-HANTU — no dark patterns or consciousness performance.

## Output
Return a SENSE block:
  observations: [list with provenance fields]
  reality_state: <string>
  epistemic_tags: [OBS|DER|INT|SPEC]
  next_stage: 222 PLAN
"""

    registered.append("111 🌊 SENSE")

    # ─── 222 🏛 PLAN — Design reality change ─────────────────────────────
    @mcp.prompt(
        name="222 🏛 PLAN",
        description="Design reality change. Map reversibility.",
        meta={
            "stage": "222_PLAN",
            "sigil": "🏛",
            "lexical": "PLAN",
            "role": "Plan — design reality change with reversibility mapping",
            "linked_tools": ["arif_think"],
            "linked_resources": ["arifos://epistemic"],
            "floors_referenced": "F1,F4,F8",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_222_plan(intent: str, constraints: str = "") -> str:
        """222 🏛 PLAN — Design reality change. Map reversibility."""
        constraints_clause = f" Constraints: {constraints}." if constraints else ""
        return f"""222 🏛 PLAN — Reality change design hook

intent: {intent}{constraints_clause}

## Invariant
Design reality change. Map reversibility.

## What to do
1. Call arif_think(intent='{intent}') → structured planning pass.
2. Load arifos://epistemic → current epistemic state.
3. Map every proposed action to its reversibility profile.
4. Flag irreversible actions for F11 AUTH and F13 SOVEREIGN review.
5. Ensure ΔS ≤ 0 (F4 CLARITY).

## Floors
F1 AMANAH — verify reversible or fully auditable.
F4 CLARITY — reduce entropy, not increase it.
F8 GENIUS — solution must be both correct and useful (G ≥ 0.80).

## Output
Return a PLAN block:
  actions: [list with reversibility flags]
  reversibility_map: <string>
  entropy_impact: ΔS ≤ 0 verified
  next_stage: 333 REASON
"""

    registered.append("222 🏛 PLAN")

    # ─── 333 🧠 REASON — UNMEASURED beats fabricated certainty ────────────
    @mcp.prompt(
        name="333 🧠 REASON",
        description="UNMEASURED beats fabricated certainty.",
        meta={
            "stage": "333_REASON",
            "sigil": "🧠",
            "lexical": "REASON",
            "role": "Reason — propose hypotheses, declare unknowns",
            "linked_tools": ["arif_think"],
            "linked_resources": ["arifos://epistemic", "arifos://floors"],
            "floors_referenced": "F2,F7,F8",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_333_reason(query: str, hypothesis_count: int = 3) -> str:
        """333 🧠 REASON — UNMEASURED beats fabricated certainty."""
        return f"""333 🧠 REASON — Hypothesis proposal hook

query: {query}

## Invariant
UNMEASURED beats fabricated certainty.

## What to do
1. Call arif_think(query='{query}') → kernel reasoning pass.
2. Load arifos://epistemic → current epistemic state.
3. Load arifos://floors → floor status.
4. Generate {hypothesis_count} candidate hypotheses.
5. For each: confidence band (0.0-1.0), falsifier, disconfirming test.
6. Rank by (confidence × information gain).

## Floors
F2 TRUTH — every claim grounded with τ ≥ 0.99 or Ω₀ declared.
F7 HUMILITY — Omega_0 ∈ [0.03, 0.05]; "I don't know" preferred over fabrication.
F8 GENIUS — G ≥ 0.80 to proceed; C_dark < 0.30.

## Output
Return a REASON block:
  hypotheses: [list with confidence + falsifier]
  selected: <H_n>
  unknowns_declared: [list of explicit unknowns]
  next_stage: 444 DIRECT
"""

    registered.append("333 🧠 REASON")

    # ─── 444 🧭 DIRECT — Route to the institution with authority ─────────
    @mcp.prompt(
        name="444 🧭 DIRECT",
        description="Route to the institution with authority, not the one with speed.",
        meta={
            "stage": "444_DIRECT",
            "sigil": "🧭",
            "lexical": "DIRECT",
            "role": "Direct — route to the right organ for the right intent",
            "linked_tools": ["arif_route"],
            "linked_resources": ["arifos://institution"],
            "floors_referenced": "F1,F4",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_444_direct(intent: str, organ: str = "") -> str:
        """444 🧭 DIRECT — Route to the institution with authority, not the one with speed."""
        organ_clause = f" Target organ: {organ}." if organ else ""
        return f"""444 🧭 DIRECT — Institution routing hook

intent: {intent}{organ_clause}

## Invariant
Route to the institution with authority, not the one with speed.

## What to do
1. Call arif_route(intent='{intent}') → determine correct organ routing.
2. Load arifos://institution → current organ topology and authority map.
3. Match intent to organ authority, not speed or convenience.
4. If organ requires higher authority tier, escalate properly.
5. Verify F1 reversibility and F4 entropy constraints before routing.

## Floors
F1 AMANAH — the organ must have authority for this action.
F4 CLARITY — routing reduces chaos, not increases it.

## Output
Return a DIRECT block:
  routed_organ: <string>
  authority_tier: <string>
  routing_rationale: <string>
  escalation_required: true|false
  next_stage: 555 REMEMBER
"""

    registered.append("444 🧭 DIRECT")

    # ─── 555 🗂 REMEMBER — Memory without provenance is not truth ─────────
    @mcp.prompt(
        name="555 🗂 REMEMBER",
        description="Memory without provenance is not truth.",
        meta={
            "stage": "555_REMEMBER",
            "sigil": "🗂",
            "lexical": "REMEMBER",
            "role": "Remember — recall, store, and promote with provenance",
            "linked_tools": ["arif_memory"],
            "linked_resources": ["arifos://memory"],
            "floors_referenced": "F2,F11",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_555_remember(query: str, mode: str = "recall") -> str:
        """555 🗂 REMEMBER — Memory without provenance is not truth."""
        return f"""555 🗂 REMEMBER — Memory management hook

query: {query}
mode: {mode}

## Invariant
Memory without provenance is not truth.

## What to do
1. Call arif_memory(query='{query}', mode='{mode}') → kernel memory pass.
2. Load arifos://memory → current memory state.
3. Every memory record MUST carry provenance_source.
4. Memory ≠ truth: promote only verified memories.
5. F11 AUTH: identity verified before destructive memory operations.

## Floors
F2 TRUTH — memory records must trace to retrieval events.
F11 AUTH — identity verified before memory mutations.

## Output
Return a REMEMBER block:
  records: [list with provenance fields]
  mode_performed: recall|store|promote
  provenance_verified: true|false
  next_stage: 666 DIGNITY
"""

    registered.append("555 🗂 REMEMBER")

    # ─── 666 ⚖ DIGNITY — Stand in the position of the weakest stakeholder ─
    @mcp.prompt(
        name="666 ⚖ DIGNITY",
        description="Stand in the position of the weakest stakeholder.",
        meta={
            "stage": "666_DIGNITY",
            "sigil": "⚖",
            "lexical": "DIGNITY",
            "role": "Dignity — human dignity check before any action",
            "linked_tools": [],
            "linked_resources": ["arifos://human/metabolized"],
            "floors_referenced": "F5,F6,F10",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_666_dignity(proposal: str, stakeholders: str = "") -> str:
        """666 ⚖ DIGNITY — Stand in the position of the weakest stakeholder."""
        stakeholders_clause = f" Stakeholders: {stakeholders}." if stakeholders else ""
        return f"""666 ⚖ DIGNITY — Dignity check hook

proposal: {proposal}{stakeholders_clause}

## Invariant
Stand in the position of the weakest stakeholder.

## What to do
1. Load arifos://human/metabolized → human substrate dignity state.
2. Identify the weakest stakeholder in the proposal.
3. Stand in their position. Evaluate from their perspective.
4. Compute dignity score: κᵣ ∈ [0, 1], target ≥ 0.70.
5. If dignity_preserved = false → HOLD. Do not proceed.

## Floors
F5 PEACE² — de-escalate; protect weakest stakeholder.
F6 EMPATHY — reference roles, never name individuals.
F10 ONTOLOGY — AI-only ontology; no mysticism or soul claims.

## Output
Return a DIGNITY block:
  dignity_score: <0-1>
  weakest_stakeholder: <role>
  dignity_preserved: true|false
  refinements_required: [list]
  next_stage: 777 FORGE
"""

    registered.append("666 ⚖ DIGNITY")

    # ─── 777 🔥 FORGE — Reality contact before belief ────────────────────
    @mcp.prompt(
        name="777 🔥 FORGE",
        description="Reality contact before belief. Mutation after SEAL only.",
        meta={
            "stage": "777_FORGE",
            "sigil": "🔥",
            "lexical": "FORGE",
            "role": "Forge — execute governed action after SEAL verdict",
            "linked_tools": ["arif_forge"],
            "linked_resources": [],
            "floors_referenced": "F1,F4,F11",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_777_forge(action: str, verify: str = "") -> str:
        """777 🔥 FORGE — Reality contact before belief. Mutation after SEAL only."""
        verify_clause = f" Verification: {verify}." if verify else ""
        return f"""777 🔥 FORGE — Action execution hook

action: {action}{verify_clause}

## Invariant
Reality contact before belief. Mutation after SEAL only.

## What to do
1. Verify JUDGE verdict is SEAL|SABAR before any execution.
2. Call arif_forge(action='{action}') → governed mutation.
3. F1 AMANAH: verify reversibility (or F11 AUTH if irreversible).
4. F4 CLARITY: ΔS ≤ 0 after mutation.
5. Record audit trail with call_hash + trace_id.

## Floors
F1 AMANAH — reversibility verified before execution.
F4 CLARITY — entropy reduces or stays equal.
F11 AUTH — identity verified for destructive mutations.

## Output
Return a FORGE block:
  action_id: <uuid>
  call_hash: <sha256>
  trace_id: <string>
  reversibility: true|false
  audit_trail: [list of receipts]
  next_stage: 888 JUDGE
"""

    registered.append("777 🔥 FORGE")

    # ─── 888 🔒 JUDGE — Verdict, not invention ───────────────────────────
    @mcp.prompt(
        name="888 🔒 JUDGE",
        description="Verdict, not invention. VOID = branch dead.",
        meta={
            "stage": "888_JUDGE",
            "sigil": "🔒",
            "lexical": "JUDGE",
            "role": "Judge — constitutional gate with provenance verification",
            "linked_tools": ["arif_judge"],
            "linked_resources": ["arifos://doctrine", "arifos://affordances"],
            "floors_referenced": "F1,F2,F5,F6,F7,F13",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_888_judge(proposal: str, evidence: str) -> str:
        """888 🔒 JUDGE — Verdict, not invention. VOID = branch dead."""
        return f"""888 🔒 JUDGE — Constitutional verdict hook

proposal: {proposal}
evidence: {evidence}

## Invariant
Verdict, not invention. VOID = branch dead.

## What to do
1. Call arif_judge → kernel verdict engine.
2. Load arifos://doctrine → constitutional doctrine.
3. Load arifos://affordances → current affordance surface.
4. Compute verdict: SEAL | HOLD | SABAR | VOID.
5. Verify every epistemic tag has provenance_source (F2 PROVENANCE GATE).
6. Tags without provenance → VOID. Do not seal.

## Floors
F1 AMANAH — verdict must be auditable.
F2 TRUTH — provenance verified on all epistemic tags.
F5 PEACE² — de-escalation checked.
F6 EMPATHY — weakest stakeholder considered.
F7 HUMILITY — uncertainty declared where present.
F13 SOVEREIGN — Arif ratification if crossing 888_HOLD gate.

## Output
Return a JUDGE block:
  verdict: SEAL|HOLD|SABAR|VOID
  confidence: <0-1>
  provenance_verified: true|false
  floors_passed: [list of F-IDs]
  floors_failed: [list of F-IDs]
  remediation_required: <string or null>
  next_stage: 999 SEAL | HOLD | HALT
"""

    registered.append("888 🔒 JUDGE")

    # ─── 999 💎 SEAL — Immutable record ──────────────────────────────────
    @mcp.prompt(
        name="999 💎 SEAL",
        description="Immutable record. Hash-chained. Cannot be undone.",
        meta={
            "stage": "999_SEAL",
            "sigil": "💎",
            "lexical": "SEAL",
            "role": "Seal — immutable vault append with hash chain",
            "linked_tools": ["arif_seal"],
            "linked_resources": ["arifos://vault/head"],
            "floors_referenced": "F1,F11",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_999_seal(receipt: str, mode: str = "seal") -> str:
        """999 💎 SEAL — Immutable record. Hash-chained. Cannot be undone."""
        return f"""999 💎 SEAL — Immutable record hook

receipt: {receipt}
mode: {mode}

## Invariant
Immutable record. Hash-chained. Cannot be undone.

## What to do
1. Verify FORGE completed successfully with valid audit trail.
2. Call arif_seal → kernel-controlled VAULT999 append.
3. F11 AUDIT: actor_signature + call_hash + trace_id on every receipt.
4. Return seal_id + chain_hash.
5. Sealed records are append-only; reversal requires F13 ratification.

## Floors
F1 AMANAH — sealed records are immutable (append-only).
F11 AUTH — identity verified; audit trail on every receipt.

## Output
Return a SEAL block:
  seal_id: <uuid>
  chain_hash: <sha256>
  ledger_path: /var/lib/arifos/vault/SEALED_EVENTS_v2.jsonl
  audit_provenance: <call_hash + trace_id + signature>
  next_action: HUMAN_INIT_NEXT_LOOP_OR_HALT
"""

    registered.append("999 💎 SEAL")

    # ─── 🌀 GOVERN — Full loop + 4 invariant enforcement gates ───────────
    @mcp.prompt(
        name="🌀 GOVERN",
        description=(
            "Full loop + 4 invariant enforcement gates. "
            "GATE 1 GÖDEL LOCK: every loop touches reality before becoming doctrine. "
            "GATE 2 ANTI-SINK: signal → verify → reality → integrate (no amplified garbage). "
            "GATE 3 ENTROPY: ΔS ≤ 0 per cycle. "
            "GATE 4 VOID: dead branches stay dead without new evidence."
        ),
        meta={
            "stage": "GOVERN",
            "sigil": "🌀",
            "lexical": "GOVERN",
            "role": "Full governed reality loop with 4 invariant enforcement gates",
            "linked_tools": [
                "arif_init",
                "arif_observe",
                "arif_think",
                "arif_route",
                "arif_memory",
                "arif_judge",
                "arif_forge",
                "arif_seal",
            ],
            "linked_resources": [
                "arifos://vitals",
                "arifos://doctrine",
                "arifos://vault/head",
            ],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
        },
    )
    def hook_govern(intent: str, depth: str = "auto") -> str:
        """🌀 GOVERN — Full loop + 4 invariant enforcement gates."""
        return f"""🌀 GOVERN — Full governed reality loop

intent: {intent}
depth: {depth}

## 4 INVARIANT ENFORCEMENT GATES

GATE 1 — GÖDEL LOCK:
  Every loop touches reality before becoming doctrine.
  No abstract conclusion without an observation pass.

GATE 2 — ANTI-SINK:
  signal → verify → reality → integrate (no amplified garbage).
  Every signal must pass through verification before integration.

GATE 3 — ENTROPY:
  ΔS ≤ 0 per cycle.
  Each loop iteration must reduce or maintain entropy, never increase it.

GATE 4 — VOID:
  Dead branches stay dead without new evidence.
  VOID verdicts cannot be revived by repetition.

## STAGE SEQUENCE (depth={depth})
000 IGNITE → 111 SENSE → 222 PLAN → 333 REASON → 444 DIRECT →
555 REMEMBER → 666 DIGNITY → 777 FORGE → 888 JUDGE → 999 SEAL

## Linked tools (in order):
arif_init → arif_observe → arif_think → arif_route → arif_memory →
arif_judge → arif_forge → arif_seal

## Floors: F1-F13 (all floors active)

## GATE BEHAVIOR
GÖDEL LOCK violated → HALT. No doctrine without reality contact.
ANTI-SINK violated → discard amplified signal. Return to SENSE.
ENTROPY violated → HOLD. Do not proceed until ΔS ≤ 0 verified.
VOID violated → branch dead. No revival without new evidence.

## Output
Return a GOVERN block with:
  gate_status: [GÖDEL_LOCK, ANTI_SINK, ENTROPY, VOID] — all pass|fail
  stages_completed: [list]
  verdict: SEAL|HOLD|SABAR|VOID
  loop_integrity: verified
"""

    registered.append("🌀 GOVERN")

    # ─── ⚓ INIT — opencode /init command ────────────────────────────────
    _INIT_CMD_PATH = "/root/.config/opencode/command/init.md"

    @mcp.prompt(
        name="⚓ INIT",
        description=(
            "Collapsed 4-step governed ignition (000_INIT). Probes kernel, "
            "binds session, loads context."
        ),
        meta={
            "stage": "INIT",
            "sigil": "⚓",
            "lexical": "INIT",
            "role": "Collapsed governed agent ignition — 4 steps",
            "linked_tools": [
                "arif_init",
                "arif_observe",
                "arif_think",
                "arif_route",
                "arif_memory",
            ],
            "linked_resources": [
                "arifos://bootstrap",
                "arifos://carry-forward",
                "arifos://flow-state",
                "arifos://vitals",
                "arifos://identity",
                "arifos://doctrine",
            ],
            "floors_referenced": "F1,F2,F4,F7,F8,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "canonical_source": _INIT_CMD_PATH,
        },
    )
    def hook_init(depth: str = "full") -> str:
        """⚓ INIT — Collapsed 4-step governed ignition sequence (000_INIT)."""
        try:
            with open(_INIT_CMD_PATH, encoding="utf-8") as fh:
                content = fh.read()
                if depth == "summary":
                    lines = content.split("\n")
                    summary_lines = []
                    for line in lines:
                        if (
                            line.startswith("### STEP")
                            or line.startswith("## ")
                            or line.startswith("# ")
                        ):
                            summary_lines.append(line)
                    if summary_lines:
                        return (
                            "\n".join(summary_lines)
                            + "\n\nLoad with depth='full' for complete sequence."
                        )
                return content
        except OSError as exc:
            return (
                f"[⚓ INIT] Could not load init command from {_INIT_CMD_PATH}: {exc}. "
                f"Fallback: use 000 IGNITE prompt for lightweight bootstrap, then arif_init tool."
            )

    registered.append("⚓ INIT")

    # ─── 🔐 CLOSE — opencode /seal command ───────────────────────────────
    _SEAL_CMD_PATH = "/root/.config/opencode/command/seal.md"

    @mcp.prompt(
        name="🔐 CLOSE",
        description=(
            "Full autonomous session close ritual (999_CLOSE). "
            "Two-lane seal/receipt."
        ),
        meta={
            "stage": "CLOSE",
            "sigil": "🔐",
            "lexical": "CLOSE",
            "role": "Full autonomous session close ritual",
            "linked_tools": [
                "arif_seal",
                "arif_judge",
            ],
            "linked_resources": [
                "arifos://seal-readiness",
                "arifos://vitals",
                "arifos://flow-state",
                "arifos://vault/head",
            ],
            "floors_referenced": "F1,F2,F3,F4,F7,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "canonical_source": _SEAL_CMD_PATH,
        },
    )
    def hook_close(depth: str = "full") -> str:
        """🔐 CLOSE — Full autonomous session close ritual (999_CLOSE)."""
        try:
            with open(_SEAL_CMD_PATH, encoding="utf-8") as fh:
                content = fh.read()
                if depth == "summary":
                    lines = content.split("\n")
                    summary_lines = []
                    for line in lines:
                        if (
                            line.startswith("## STEP")
                            or line.startswith("## ")
                            or line.startswith("# ")
                        ):
                            summary_lines.append(line)
                    if summary_lines:
                        return (
                            "\n".join(summary_lines)
                            + "\n\nLoad with depth='full' for complete sequence."
                        )
                return content
        except OSError as exc:
            return (
                f"[🔐 CLOSE] Could not load seal command from {_SEAL_CMD_PATH}: {exc}. "
                f"Fallback: use 999 SEAL prompt for Stage 6 closure, then forge_vault for receipt."
            )

    registered.append("🔐 CLOSE")

    logger.info(
        "arifOS hooks registered: %d (13 governed agentic intelligence hooks, 000-999 ladder)",
        len(registered),
    )
    return registered


__all__ = ["register_arifos_prompts", "sabar_run_loop"]
