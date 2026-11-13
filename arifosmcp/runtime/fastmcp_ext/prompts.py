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



def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register the 13 governed hooks.

    Wire names are ASCII slugs. Emoji stays in the title.
    Run order is s888_judge before s777_forge. Registration order is unchanged.
    s666_dignity is advisory until F6 is measured.
    s999_seal is the vault write and needs a human ack.
    s_govern sequences the loop and does not enforce gates.
    s_init is session ignition (5 tools). s000_ignite is identity only.
    s_close waits for a human ack before arif_seal.
    arif_report coordinates and has no prompt.
    """
    registered: list[str] = []

    # ─── s000_ignite — Identity before action ─────────────────────────
    @mcp.prompt(
        name="s000_ignite",
        title="000 🌱 — Identity Ignition",
        description="Position Zero (/000) Sovereign Anchor. Identity before action. REALITY > EVERYTHING.",
        meta={
            "stage": "000_IGNITE",
            "sigil": "🌱",
            "lexical": "IGNITE",
            "role": "Identity ignition — bind actor to Position Zero (/000) before any action",
            "linked_tools": ["arif_init"],
            "linked_resources": [
                "arifos://identity",
                "arifos://000/genesis",
                "arifos://000/claims",
                "arifos://carry-forward",
            ],
            "floors_referenced": "F1,F7,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "tool_verb": "arif_init",
            "execution_order": 10,
            "entry_kind": "identity_only",
            "execution_role": "step",
            "legacy_name": "000 🌱 IGNITE",
        },
    )
    def hook_000_ignite(actor_id: str, intent: str) -> str:
        """s000_ignite — Position Zero (/000) Sovereign Anchor. Identity before action. REALITY > EVERYTHING."""
        return f"""s000_ignite — Identity ignition hook

actor_id: {actor_id}
intent: {intent}

## Invariant
REALITY > EVERYTHING.
Position Zero (/000) Sovereign Anchor: All authority in the federation originates from the sovereign human at Position Zero (Muhammad Arif bin Fazil, did:web:arif-fazil.com).
Identity before action. VOID is final without new evidence.

## What to do
1. Call arif_init(actor_id='{actor_id}', intent='{intent}') → bind identity to session. intent is required.
2. Verify identity binding returned a valid session_id and verified Position Zero authority.
3. If binding fails → HALT. Do not proceed without identity.
4. Load genesis attestation & sovereign claims: arifos://000/genesis, arifos://000/claims, arifos://identity.
5. Load carry-forward from prior session: arifos://carry-forward.
6. Enforce Gödel Lock: No closed AI system can prove all truths within itself; sovereign human provides external ground truth.
7. Confirm identity matches F13 SOVEREIGN authority.

## Floors & Principles
F1 AMANAH — attestation is the first act.
F7 HUMILITY — acknowledge uncertainty before identity claim; UNKNOWN is a valid state.
F11 AUTH — identity verified before any action.
F13 SOVEREIGN — recognize Arif = F13 = absolute veto.
ANTI-BANGANG LAW: Reality first, human first, system second. Satu masalah, satu owner, satu jalan.

## Output
Return an IGNITE block:
  identity_bound: true|false
  session_id: <string>
  actor_id: <string>
  position_zero_verified: true|false
  carry_forward_loaded: true|false
  next_stage: s111_sense
"""

    registered.append("s000_ignite")

    # ─── s111_sense — Reality before judgment ──────────────────────────
    @mcp.prompt(
        name="s111_sense",
        title="111 🌊 — Reality Observation",
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
            "tool_verb": "arif_observe",
            "execution_order": 20,
            "execution_role": "step",
            "legacy_name": "111 🌊 SENSE",
        },
    )
    def hook_111_sense(query: str, focus: str = "") -> str:
        """s111_sense — Reality before judgment. Verify before integrate."""
        focus_clause = f" Focus on: {focus}." if focus else ""
        return f"""s111_sense — Reality observation hook

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
  next_stage: s222_plan
"""

    registered.append("s111_sense")

    # ─── s222_plan — Design reality change ─────────────────────────────
    @mcp.prompt(
        name="s222_plan",
        title="222 🏛 — Reality Change Design",
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
            "tool_verb": "arif_think",
            "execution_order": 30,
            "execution_role": "step",
            "shared_tool_note": "PLAN and REASON both call arif_think",
            "legacy_name": "222 🏛 PLAN",
        },
    )
    def hook_222_plan(intent: str, constraints: str = "") -> str:
        """s222_plan — Design reality change. Map reversibility."""
        constraints_clause = f" Constraints: {constraints}." if constraints else ""
        return f"""s222_plan — Reality change design hook

intent: {intent}{constraints_clause}

## Invariant
Design reality change. Map reversibility.

## What to do
1. Call arif_think(mode='plan', query='{intent}') → structured planning pass.
2. Load arifos://epistemic → current epistemic state.
3. Map every proposed action to its reversibility profile.
4. Flag irreversible actions for F11 AUTH and F13 SOVEREIGN review.
5. Entropy is UNMEASURED unless a tool result contains delta_s.

## Floors
F1 AMANAH — verify reversible or fully auditable.
F4 CLARITY — reduce entropy, not increase it.
F8 GENIUS — solution must be both correct and useful (G ≥ 0.80).

## Output
Return a PLAN block:
  actions: [list with reversibility flags]
  reversibility_map: <string>
  entropy_impact: UNMEASURED unless a tool returns delta_s
  next_stage: s333_reason
"""

    registered.append("s222_plan")

    # ─── s333_reason — UNMEASURED beats fabricated certainty ────────────
    @mcp.prompt(
        name="s333_reason",
        title="333 🧠 — Hypothesis Reasoning",
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
            "tool_verb": "arif_think",
            "execution_order": 40,
            "execution_role": "step",
            "shared_tool_note": "PLAN and REASON both call arif_think",
            "legacy_name": "333 🧠 REASON",
        },
    )
    def hook_333_reason(query: str, hypothesis_count: int = 3) -> str:
        """s333_reason — UNMEASURED beats fabricated certainty."""
        return f"""s333_reason — Hypothesis proposal hook

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
  next_stage: s444_direct
"""

    registered.append("s333_reason")

    # ─── s444_direct — Route to the institution with authority ─────────
    @mcp.prompt(
        name="s444_direct",
        title="444 🧭 — Organ Routing",
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
            "tool_verb": "arif_route",
            "execution_order": 50,
            "execution_role": "step",
            "legacy_name": "444 🧭 DIRECT",
        },
    )
    def hook_444_direct(intent: str, organ: str = "") -> str:
        """s444_direct — Route to the institution with authority, not the one with speed."""
        organ_clause = f" Target organ: {organ}." if organ else ""
        return f"""s444_direct — Institution routing hook

intent: {intent}{organ_clause}

## Invariant
Route to the institution with authority, not the one with speed.

## What to do
1. Call arif_route(intent='{intent}') → determine correct organ routing.
2. Load arifos://institution → current organ topology and authority map.
3. Match intent to organ authority plane:
   - arifOS (:8088): Authority, judge, seal, VAULT999 (JUDGE_ONLY).
   - A-FORGE (:7071/7072): Governed execution (requires judge_state_hash).
   - arifFlow (:7073): Metabolism, FQ balance, verify-deficit gates.
   - GEOX (:8081): Earth reasoning (mode=screen for ANALYZE vs mode=evaluate for JUDGMENT).
   - WEALTH (:18082): Capital evidence, live market snapshots, four-layer intelligence.
   - WELL (:18083): Human vitality, substrate readiness, dignity guard.
   - FRAME (:18085): Drift witness, OBSERVE_ONLY.
   - HERMES (:18087): Agent-to-agent gateway, multi-human lanes.
   - CHRON (:18102): Temporal intelligence, predictions calibration.
4. Separate pure computation (ANALYZE / OBSERVE_ONLY) from state mutation (OPERATOR / JUDGMENT).
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
  next_stage: s555_remember
"""

    registered.append("s444_direct")

    # ─── s555_remember — Memory without provenance is not truth ─────────
    @mcp.prompt(
        name="s555_remember",
        title="555 🗂 — Memory Governance",
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
            "tool_verb": "arif_memory",
            "execution_order": 60,
            "execution_role": "step",
            "legacy_name": "555 🗂 REMEMBER",
        },
    )
    def hook_555_remember(query: str, mode: str = "recall") -> str:
        """s555_remember — Memory without provenance is not truth."""
        return f"""s555_remember — Memory management hook

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
6. promote and forget refuse unless human_approval is true. The write mode is remember.

## Floors
F2 TRUTH — memory records must trace to retrieval events.
F11 AUTH — identity verified before memory mutations.

## Output
Return a REMEMBER block:
  records: [list with provenance fields]
  mode_performed: recall|remember|promote
  provenance_verified: true|false
  next_stage: s666_dignity
"""

    registered.append("s555_remember")

    # ─── s666_dignity — Stand in the position of the weakest stakeholder ─
    @mcp.prompt(
        name="s666_dignity",
        title="666 ⚖ — Dignity Check",
        description="Advisory dignity check. No linked tool. F6 is unmeasured. Not an enforcing gate.",
        meta={
            "stage": "666_DIGNITY",
            "sigil": "⚖",
            "lexical": "DIGNITY",
            "role": "Dignity — advisory check while F6 is unmeasured. Not an enforcing gate",
            "linked_tools": [],
            "linked_resources": ["arifos://human/metabolized"],
            "floors_referenced": "F5,F6,F10",
            "federation_layer": "arifOS.kernel.prompts",
            "tool_verb": "none",
            "execution_order": 70,
            "execution_role": "step",
            "advisory_only": True,
            "enforcement": "none",
            "f6_status": "unmeasured",
            "superseded_stage": "CRITIQUE archived 2026-09-16; this stage is DIGNITY",
            "legacy_name": "666 ⚖ DIGNITY",
        },
    )
    def hook_666_dignity(proposal: str, stakeholders: str = "") -> str:
        """Advisory dignity check. F6 is unmeasured. Not an enforcing gate."""
        stakeholders_clause = f" Stakeholders: {stakeholders}." if stakeholders else ""
        return f"""s666_dignity — Advisory dignity check. Not an enforcing gate.

proposal: {proposal}{stakeholders_clause}

## Status
advisory_only: true
enforcement: none
f6_status: unmeasured
This stage has no linked tool. It does not compute a score.
F6 is unmeasured. Do not invent a number. Do not treat this stage as a gate.
CRITIQUE was archived on 2026-09-16. This stage is DIGNITY.

## What to do
1. Load arifos://human/metabolized. Read only.
2. Name the weakest stakeholder role in the proposal. Do not name a private person.
3. Say what would harm that role if the proposal landed.
4. If harm is plausible, say HOLD and hand the text to s888_judge.
   This stage does not block by itself.

## Floors
F5 — de-escalate. Protect the weakest role.
F6 — unmeasured. No score. No threshold.
F10 — no soul claim and no invented interior state.

## Output
Return a DIGNITY block:
  advisory_only: true
  f6_status: unmeasured
  weakest_stakeholder_role: role or UNKNOWN
  harm_if_landed: string or UNKNOWN
  handoff: s888_judge
"""

    registered.append("s666_dignity")

    # ─── s777_forge — Reality contact before belief ────────────────────
    @mcp.prompt(
        name="s777_forge",
        title="777 🔥 — Governed Execution",
        description="Governed execution after the judge verdict token. Not a vault write.",
        meta={
            "stage": "777_FORGE",
            "sigil": "🔥",
            "lexical": "FORGE",
            "role": "Forge — execute after the judge verdict token. Not a vault write.",
            "linked_tools": ["arif_forge"],
            "linked_resources": [],
            "floors_referenced": "F1,F4,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "tool_verb": "arif_forge",
            "execution_order": 90,
            "execution_role": "step",
            "runs_after": "s888_judge",
            "verdict_handle": "judge_state_hash",
            "vault_write": False,
            "legacy_name": "777 🔥 FORGE",
        },
    )
    def hook_777_forge(
        action: str,
        judge_state_hash: str,
        ack_irreversible: str = "false",
        mode: str = "engineer",
    ) -> str:
        """Governed execution after the judge verdict token. Not a vault write."""
        ack = "true" if str(ack_irreversible).strip().lower() == "true" else "false"
        return f"""s777_forge — Governed execution. Not a vault write.

manifest: {action}
mode: {mode}
judge_state_hash: {judge_state_hash}
ack_irreversible: {ack}

## Names
SEAL, SABAR, HOLD, and VOID are verdict tokens from s888_judge.
They are not a vault write. The vault write is s999_seal only.
Pass the judge handle as judge_state_hash.
Pass the work as manifest. The forge tool has no action parameter.

## What to do
1. Require a prior s888_judge result. Proceed only when the verdict token is SEAL or SABAR and judge_state_hash is present.
2. Call arif_forge(mode='{mode}', manifest='{action}', judge_state_hash='{judge_state_hash}', ack_irreversible={ack}).
3. Pass ack_irreversible as true only when the human confirmed an irreversible mode such as commit or deploy. Otherwise leave it false.
4. MUTATE and ATOMIC refuse without judge_state_hash even when the published schema required list is empty.
5. Read forge_status from the tool result. If the tool did not return it, write UNMEASURED.

## Output
Return a FORGE block:
  forge_status: from the tool, or UNMEASURED
  judge_state_hash: {judge_state_hash}
  vault_write: false
  next_stage: s999_seal
"""

    registered.append("s777_forge")

    # ─── s888_judge — Verdict, not invention ───────────────────────────
    @mcp.prompt(
        name="s888_judge",
        title="888 🔒 — Constitutional Verdict",
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
            "tool_verb": "arif_judge",
            "execution_order": 80,
            "execution_role": "step",
            "runs_before": "s777_forge",
            "verdict_token": "SEAL|SABAR|HOLD|VOID",
            "vault_write": False,
            "legacy_name": "888 🔒 JUDGE",
        },
    )
    def hook_888_judge(proposal: str, evidence: str) -> str:
        """s888_judge — Verdict, not invention. VOID = branch dead."""
        return f"""s888_judge — Constitutional verdict hook

proposal: {proposal}
evidence: {evidence}

## Invariant
Verdict, not invention. VOID = branch dead.

## What to do
1. Call arif_judge(mode='judge', candidate='{proposal}', evidence='{evidence}').
   The result must include judge_state_hash for the next forge call.
   SEAL, SABAR, HOLD, and VOID are verdict tokens. They are not a vault write.
2. Load arifos://doctrine → constitutional doctrine.
3. Load arifos://affordances → current affordance surface.
4. Compute verdict across 7-rank lattice (non-compensatory):
   SEAL > PROVISIONAL > PARTIAL > SABAR > HOLD > HOLD_888 > VOID.
   Floors are never averaged; one failing floor drops the verdict.
5. Verify every epistemic tag has provenance_source (F2 PROVENANCE GATE).
6. Tags without provenance → VOID. Do not seal.
7. Only verdicts of SEAL or SABAR permit proceeding to execution.

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
  judge_state_hash: from the tool, or UNMEASURED
  vault_write: false
  confidence: <0-1>
  provenance_verified: true|false
  floors_passed: [list of F-IDs]
  floors_failed: [list of F-IDs]
  remediation_required: <string or null>
  next_stage: s777_forge if the verdict token is SEAL or SABAR
"""

    registered.append("s888_judge")

    # ─── s999_seal — Immutable record ──────────────────────────────────
    @mcp.prompt(
        name="s999_seal",
        title="999 💎 — Immutable Record",
        description="Immutable vault append. Hash-chained. Human ack required. Cannot be undone.",
        meta={
            "stage": "999_SEAL",
            "sigil": "💎",
            "lexical": "SEAL",
            "role": "Seal — immutable vault append. Human ack required. Not the judge verdict.",
            "linked_tools": ["arif_seal"],
            "linked_resources": ["arifos://vault/head", "arifos://000/claims"],
            "floors_referenced": "F1,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "tool_verb": "arif_seal",
            "execution_order": 100,
            "execution_role": "step",
            "requires_human_ack": True,
            "vault_write": True,
            "legacy_name": "999 💎 SEAL",
        },
    )
    def hook_999_seal(
        payload: str,
        judge_state_hash: str,
        ack_irreversible: str,
        mode: str = "seal",
    ) -> str:
        """Vault append. Irreversible. Human ack required. This is the only vault write."""
        ack_ok = str(ack_irreversible).strip().lower() == "true"
        ack_py = "true" if ack_ok else "false"
        if not ack_ok:
            return (
                "s999_seal — vault append refused by this prompt.\n\n"
                "ack_irreversible must be the string true before any vault append.\n"
                f"You passed: {ack_irreversible!r}\n"
                "Do not call arif_seal with mode seal.\n"
                "The human (F13) must acknowledge the irreversible write.\n"
            )
        return f"""s999_seal — Immutable vault append. This is the only stage that writes the vault.

payload: {payload}
mode: {mode}
judge_state_hash: {judge_state_hash}
ack_irreversible: {ack_py}

## Invariant
Immutable record. Hash-chained. Cannot be undone.
The judge verdict token is not this write. This write is arif_seal.
Human acknowledgement is required. This prompt does not grant it.

## What to do
1. Confirm ack_irreversible is the string true. If it is not, do not call arif_seal with mode seal.
2. Call arif_seal(mode='{mode}', payload='{payload}', seal_purpose=<one sentence why this record must exist>, judge_state_hash='{judge_state_hash}', ack_irreversible={ack_py}).
   mode seal requires payload and seal_purpose.
3. The tool argument is payload. Do not send a receipt argument.
4. Read seal_id and chain_hash from the tool result. If a field is absent, write UNMEASURED.

## Output
Return a SEAL block:
  vault_write: true
  seal_id: from the tool, or UNMEASURED
  chain_hash: from the tool, or UNMEASURED
  judge_state_hash: {judge_state_hash}
  next_action: HUMAN_INIT_NEXT_LOOP_OR_HALT
"""

    registered.append("s999_seal")

    # ─── s_govern — sequences the loop; tools enforce their own gates ──
    @mcp.prompt(
        name="s_govern",
        title="🌀 Governed Reality Loop",
        description=(
            "Sequences the governed loop. Kernel tools enforce their own gates when called. "
            "This prompt does not measure delta_s and does not itself enforce the four gates. "
            "arif_report is coordination and is not a stage."
        ),
        meta={
            "stage": "GOVERN",
            "sigil": "🌀",
            "lexical": "GOVERN",
            "role": "Sequences the governed loop. Does not itself enforce gates.",
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
            "execution_order": 0,
            "execution_role": "orchestrator",
            "tool_verb": "none",
            "enforces_gates": False,
            "legacy_name": "🌀 GOVERN",
        },
    )
    def hook_govern(intent: str, depth: str = "auto") -> str:
        """Sequences the governed loop. Does not itself enforce gates."""
        return f"""s_govern — Sequence only. This prompt does not enforce gates.

intent: {intent}
depth: {depth}

## What this prompt does
It names the order. Kernel tools enforce their own gates when you call them.
Do not report a gate as passed unless a tool result contains that gate.
If the tool result has no delta_s, entropy is UNMEASURED.
Do not write loop_integrity as verified.

arif_report is the ninth public tool. It coordinates. It is not a stage and has no prompt.

## Run order
s000_ignite, s111_sense, s222_plan, s333_reason, s444_direct,
s555_remember, s666_dignity (advisory), s888_judge, s777_forge, s999_seal.

Registration order still lists s777_forge before s888_judge.
Run order is judge, then forge.
s666_dignity is advisory_only. F6 is unmeasured. It is not a gate.

## Tool order
arif_init, arif_observe, arif_think, arif_route, arif_memory,
arif_judge, arif_forge, arif_seal.

## Named checks
Report a check only from a tool result. Otherwise UNMEASURED.
1. Gödel: a loop that never called observe has not touched reality.
2. Anti-sink: do not integrate a signal the tool did not verify.
3. Entropy: UNMEASURED unless a tool result contains delta_s.
4. Void: a VOID verdict token stays dead without new evidence.

## Output
Return a GOVERN block:
  stages_named: list
  gate_status: from tool results, else UNMEASURED
  verdict_token: from arif_judge, else UNMEASURED
  loop_integrity: UNMEASURED
"""

    registered.append("s_govern")

    # ─── s_init — session ignition, five tools ──────────────────────────
    @mcp.prompt(
        name="s_init",
        title="⚓ Session Ignition",
        description=(
            "Session ignition. Five tools: arif_init, arif_observe, arif_think, "
            "arif_route, arif_memory. Distinct from s000_ignite, which binds identity only."
        ),
        meta={
            "stage": "INIT",
            "sigil": "⚓",
            "lexical": "INIT",
            "role": "Session ignition — five tools. Distinct from identity-only s000_ignite",
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
            "execution_order": 5,
            "execution_role": "entry",
            "tool_verb": "arif_init",
            "entry_kind": "session_ignition",
            "linked_tool_count": 5,
            "legacy_name": "⚓ INIT",
        },
    )
    def hook_init(depth: str = "full") -> str:
        """Session ignition. Five tools. Distinct from identity-only s000_ignite."""
        return f"""s_init — Session ignition. Five tools. Not identity-only.

depth: {depth}

## Distinct from s000_ignite
s000_ignite binds identity only, through arif_init.
s_init names five tools:
arif_init, arif_observe, arif_think, arif_route, arif_memory.
linked_tool_count: 5

## What to do
1. Call arif_init(intent=<session purpose>) to bind the session. intent is required.
2. Call arif_observe for the live kernel state.
3. Call arif_think(mode='reason', query=<session question>).
4. Call arif_route to pick the organ.
5. Call arif_memory to load carry-forward. Keep provenance.
6. Read arifos://bootstrap, arifos://carry-forward, arifos://flow-state, arifos://vitals, arifos://identity, arifos://doctrine.
7. If depth is summary, return the five tool names and whether each call returned.
   If depth is full, include the tool results you actually received.
8. A missing result is UNMEASURED. This prompt does not read a host file and does not write the vault.
"""

    registered.append("s_init")

    # ─── s_close — session close, human ack before the vault append ────
    @mcp.prompt(
        name="s_close",
        title="🔐 Session Close Ritual",
        description=(
            "Session close. The vault append waits for a human ack. "
            "This prompt does not write the vault by itself."
        ),
        meta={
            "stage": "CLOSE",
            "sigil": "🔐",
            "lexical": "CLOSE",
            "role": "Session close. Human ack required before any vault append",
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
            "execution_order": 110,
            "execution_role": "close",
            "tool_verb": "arif_seal",
            "requires_human_ack": True,
            "vault_write": True,
            "legacy_name": "🔐 CLOSE",
        },
    )
    def hook_close(ack_irreversible: str, depth: str = "full") -> str:
        """Session close. Vault append waits for a human ack."""
        ack_ok = str(ack_irreversible).strip().lower() == "true"
        banner = (
            "HUMAN ACK REQUIRED. This prompt does not append the vault. "
            "arif_seal with mode session_close waits until ack_irreversible is the string true, "
            "confirmed by the human (F13)."
        )
        if not ack_ok:
            return (
                "s_close — session close stopped.\n\n"
                f"{banner}\n"
                f"ack_irreversible received: {ack_irreversible!r}\n"
                "Do not call arif_seal with mode session_close.\n"
                f"depth requested: {depth}\n"
            )
        return f"""s_close — Session close. The vault append still waits on the tool call.

{banner}
ack_irreversible: true
depth: {depth}

## What to do
1. Call arif_judge for the session-close candidate. Keep judge_state_hash from the result.
2. Read arifos://seal-readiness, arifos://vitals, arifos://flow-state, arifos://vault/head.
3. Only then call arif_seal(mode='session_close', payload=<session close text>, seal_purpose=<one sentence why this close must exist>, judge_state_hash=<from the judge result>, ack_irreversible=true).
   session_close is the close mode. s999_seal uses mode seal. Both require payload and seal_purpose.
4. If depth is summary, return the verdict token and whether arif_seal was called.
   If depth is full, include the tool results you actually received.
5. A missing field is UNMEASURED. Do not invent a seal id.
6. The verdict token is not the vault write. This close uses mode session_close. s999_seal uses mode seal.
"""

    registered.append("s_close")

    logger.info(
        "arifOS hooks registered: %d (13 governed agentic intelligence hooks, 000-999 ladder)",
        len(registered),
    )
    return registered


__all__ = ["register_arifos_prompts"]
