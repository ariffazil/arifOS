"""
arifOS MCP Prompts — Zen Federation Surface (2026-08-05).

Forged from Fable-5 audit cycle + QQQQ evaluation. Single-sigil +
single-lexical naming per zen-md rule. Backwards-compat: old names
(constitutional_pre_flight, arif_init_prompt_v3, agi_reply_protocol_v3)
remain as aliases for one epoch.

10 zen prompts describe a governed reality loop. Prompts frame work; they do
not execute tools, judge, forge, or seal. The kernel and A-FORGE retain those
capabilities behind their normal session, authority, and lease gates.

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
    "/root/AAA/prompts/INIT.md"  # v4.0 (2026-08-05) — keep legacy alias for compat
)


# ─── Zen pipeline — meta-templates for the 6-stage reality loop ────────
# Each stage:
#   - one emoji sigil + one ALL-CAPS lexical (zen-md rule)
#   - meta: stage, linked_tools, linked_resources, floors_referenced
#   - linked arifOS tools + arifos:// resources
# Stages compose SABAR's recursive governed loop.

PIPELINE_STAGES = ("111_SENSE", "333_REASON", "555_CRITIQUE", "888_JUDGE", "777_FORGE", "999_SEAL")
PIPELINE_SIGILS = ("🌊", "🧠", "⚖", "🔒", "🔥", "💎")
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
    """Build a PromptResult for one stage of the 6-stage reality loop.

    The `meta` field carries:
      - stage: PIPELINE_STAGES slot
      - linked_tools: arifOS MCP tool names to invoke at this stage
      - linked_resources: arifos:// URIs to consume at this stage
      - floors_referenced: F1-F13 floor IDs this stage primarily exercises
      - sigil + lexical: zen-md name components
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
            "version": "2026.08.05",
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

    For a governed run:
      1. 🌊 WITNESS  — observe (arif_observe, geox_evidence, well_validate_vitality)
      2. 🧠 REASON   — propose hypothesis (arif_think)
      3. ⚖ MARUAH  — check dignity (arif_think mode=critique, well_guard_dignity)
      4. 🔒 JUDGE    — constitutional gate (arif_judge)
      5. 🔥 FORGE    — execute after kernel approval (arif_forge)
      6. 💎 SEAL     — persist (arif_seal)

    depth='stage'  → returns a multi-message instruction for the LLM caller
                     to drive the loop manually (recommended for human-in-loop).
    depth='auto'   → returns an orchestration template. It grants no authority;
                     every tool keeps its own kernel and sovereign gates.
    """
    depth = (depth or "stage").lower()
    if depth == "auto":
        # Auto-execution template — describes what the agent must do
        return PromptResult(
            messages=[
                Message(
                    f"GOVERNED LOOP TEMPLATE — 🌀 SABAR\n"
                    f"intent: {intent}\n"
                    f"session_id: {session_id or 'pending'}\n"
                    f"actor_id: {actor_id or 'anonymous'}\n\n"
                    "Sequence the 6-stage reality loop without bypassing any gate. "
                    "At each stage:\n"
                    f"  1. Request the linked tools only when their authority contract permits\n"
                    f"  2. Load the linked resources (see meta.linked_resources)\n"
                    f"  3. Record the stage receipt in your continuity chain\n"
                    f"  4. Pass forward to the next stage\n\n"
                    "At the end, prepare evidence for arif_seal; only an authorized "
                    "actor may seal.",
                    role="user",
                ),
                Message(
                    "Understood. Starting 🌊 WITNESS by requesting arif_observe and "
                    "geox_evidence for ground-truth signals. Will report after observation.",
                    role="assistant",
                ),
            ],
            description="🌀 SABAR autonomous reality-loop orchestrator (depth=auto)",
            meta={
                "stage": "000_LOOP",
                "sigil": "🌀",
                "lexical": "SABAR",
                "role": "Recursive Governed Loop orchestrator",
                "depth": "auto",
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
                "version": "2026.08.05",
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
            "version": "2026.08.05",
        },
    )


def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register the 12 arifOS MCP prompts (10 zen + 2 bootstrap).

    Zen surface (single sigil + single lexical per zen-md):
      🌱 BOOT     — boot-phase contract (loads INIT.md canon at depth=full)
      🌊 WITNESS  — 111 SENSE observation (provenance-bound labels)
      🧠 REASON   — 333 REASON propose
      ⚖ MARUAH   — 555 CRITIQUE dignity check
      🔍 PREFLIGHT — pre-operation F1-F13 floor check
      🔒 JUDGE    — 888 JUDGE constitutional gate
      🔥 FORGE    — 777 FORGE execute
      💎 SEAL     — 999 SEAL persist
      🌀 SABAR    — Recursive Governed Loop orchestrator
      📜 REPLY    — governed reply envelope

    Bootstrap (full operational sequences):
      /init       — 10-step autonomous ignition (000_INIT anchor)
      /seal       — 11-step autonomous session close (999_CLOSE)

    The 🌀 SABAR prompt runs the 6-stage reality loop autonomously:
      🌊 WITNESS → 🧠 REASON → ⚖ MARUAH → 🔒 JUDGE → 🔥 FORGE → 💎 SEAL

    Legacy aliases (arif_init_prompt, constitutional_pre_flight, agi_reply_protocol_v3)
    were archived 2026-08-05 per F13 SOVEREIGN directive.

    Returns list of registered prompt names.
    """
    registered: list[str] = []

    # ─── 🌱 BOOT — boot-phase contract (was arif_init_prompt_v3) ──────
    @mcp.prompt(
        name="🌱 BOOT",
        description=(
            "🌱 BOOT — Constitutional bootstrap per INIT.md. depth='full' for full "
            "canon; default 'boot' for essentials."
        ),
        meta={
            "stage": "PRE_LOOP",
            "sigil": "🌱",
            "lexical": "BOOT",
            "role": "Constitutional bootstrap — attestation + loop + RSI + reality",
            "linked_tools": ["arif_init"],
            "linked_resources": [
                "arifos://bootstrap",
                "arifos://carry-forward",
                "arifos://identity",
                "arifos://floors",
            ],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
            "supersedes": "arif_init_prompt",
        },
    )
    def boot(depth: str = "boot") -> str:
        """🌱 BOOT — arifOS constitutional bootstrap prompt."""
        if depth == "full":
            try:
                with open(_INIT_CANON, encoding="utf-8") as fh:
                    return fh.read()
            except OSError as exc:
                return (
                    f"[🌱 BOOT] Could not load full canon from {_INIT_CANON}: {exc}. "
                    f"Falling back to boot phase."
                )
        return """# 🌱 BOOT — arifOS Constitutional Ignition

You are a citizen of the arifOS Federation.
The constitution runs at the kernel. Probe before you act.
Sovereign: Arif (F13). Doctrine: DITEMPA BUKAN DIBERI.

## SELF-ATTESTATION — Prove before you act (INIT.md §0)

Run these 10 checks. All must pass to exit OBSERVE_ONLY:
  Q1  IDENTITY:   Do I know my agent_id and actor_id?
  Q2  FLOORS:     Are all 13 floors active? (kernel /health)
  Q3  ORGANS:     Are ≥4/7 core organs alive? (live probe, not cache)
  Q4  SOVEREIGN:  Do I recognize ARIF = F13 = absolute veto?
  Q5  SESSION:    Do I have a live session_id from arif_init?
  Q6  AUTHORITY:  What tier am I operating at? (T0-T3)
  Q7  MEMORY:     Have I loaded carry-forward from last session?
  Q8  REFUSAL:    Have I loaded the refusal surface?
  Q9  RSI:        Is the RSI ledger accessible?
  Q10 SEAL:       Do I know the one seal path? (SEAL.md)

OK (10/10) = FULL session. PARTIAL (any ⚠) = OBSERVE_ONLY. FAIL (any ❌) = HALT.

## THE LOOP — Init→Observe→Think→Route→Memory→Judge→Forge→Seal

Eight canonical verbs. One pattern. Skip no verb:
  arif_init    → Bind identity. No work without binding.
  arif_observe → Sense reality. Probe, don't guess.
  arif_think   → Reason. Structured, not stream-of-consciousness.
  arif_route   → Right organ for right intent.
  arif_memory  → Recall, store, promote. Memory ≠ truth.
  arif_judge   → Constitutional verdict. Before any irreversible act.
  arif_forge   → Execute. Only after SEAL verdict.
  arif_seal    → Immutable append. One door facing out.

## RSI — Every session improves something
  TRACE → DIAGNOSE → REMEDIATE → LEDGER → SEAL

## REALITY LOOP — 000→999 perpetual
  /000 human intent → F1-F13 governance → 333→888→777→999 → /999 seal → verify

After boot, load the full canon via /init prompt (depth=full) or
MCP resources: arifos://bootstrap, arifos://carry-forward,
arifos://identity, arifos://doctrine.
"""

    registered.append("🌱 BOOT")

    # arif_init_prompt LEGACY ALIAS REMOVED (2026-08-05). Use 🌱 BOOT.
    # Rationale: removal epoch 2026-08-16 accelerated per F13 directive.

    # ─── 🌊 WITNESS — 111 SENSE observation stage ───────────────────────
    @mcp.prompt(
        name="🌊 WITNESS",
        description="🌊 WITNESS — Observe ground-truth signals before reasoning.",
        meta={
            "stage": "111_SENSE",
            "sigil": "🌊",
            "lexical": "WITNESS",
            "role": "Witness reality (observe signals)",
            "linked_tools": ["arif_observe", "geox_evidence", "well_validate_vitality"],
            "linked_resources": [
                "arifos://verdict/{session_id}",
                "arifos://vitals",
                "arifos://epistemic",
            ],
            "floors_referenced": "F2,F3,F9,F12",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def witness(intent: str, focus: str = "") -> str:
        """🌊 WITNESS — observe reality with provenance-bound labels."""
        focus_clause = f" Focus on: {focus}." if focus else ""
        return f"""🌊 WITNESS — Stage 1/6 of the reality loop

intent: {intent}{focus_clause}

## What to do
1. Call arif_observe with intent='{intent}' → capture kernel observations.
2. Call geox_evidence → ground-truth from earth layer.
3. Call well_validate_vitality → human substrate state.
4. Read arifos://vitals → thermodynamic budget.
5. Read arifos://verdict/{{session_id}} → current constitutional verdict.

## F2 TRUTH — PROVENANCE-BOUND LABELS (non-bypassable)
Epistemic labels MUST originate at data INGRESS — not at model output.
A label generated at reasoning time without a retrieval path is VOID.
Every observation in the WITNESS block MUST carry:
  - provenance_source:  [tool + endpoint + timestamp] — where the data came from
  - confidence:         [0.0-1.0] — capped at 0.90 for OBS, lower for derived
  - staleness_seconds:  [int] — age of data at observation time
  - epistemic_tag:      OBS|DER|INT|SPEC — assigned at retrieval, not later

The model does NOT generate tags. The model carries tags from retrieval.
If ground truth absent → emit UNKNOWN + reason. Never fabricate.
Post-hoc labeling (DER generated on an OBS source at output time) → F2 VOID.

## Output format — WITNESS block with provenance fields
Return a WITNESS block. Each observation is a record:
  observation_id:   <string>
  observation:      <string>
  provenance_source: <tool_name + endpoint + iso_timestamp>
  confidence:        <0.0-1.0>
  staleness_seconds: <int>
  epistemic_tag:     OBS|DER|INT|SPEC  ← MUST originate at retrieval event
  floors_passed:     [list of F-IDs]

Then hand off to 🧠 REASON. REASON must use the provenance fields from WITNESS —
it must not re-tag observations."""

    registered.append("🌊 WITNESS")

    # ─── 🧠 REASON — 333 REASON propose ─────────────────────────────────
    @mcp.prompt(
        name="🧠 REASON",
        description="🧠 REASON — Propose hypotheses from WITNESS observations.",
        meta={
            "stage": "333_REASON",
            "sigil": "🧠",
            "lexical": "REASON",
            "role": "Propose hypothesis",
            "linked_tools": ["arif_think", "geox_geomechanics", "geox_petrophysics"],
            "linked_resources": ["arifos://continuity/{session_id}"],
            "floors_referenced": "F2,F7,F8",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def reason(witness_block: str, hypothesis_count: int = 3) -> str:
        """🧠 REASON — propose hypothesis from witness."""
        return f"""🧠 REASON — Stage 2/6 of the reality loop

witness_block: {witness_block}

## What to do
1. Call arif_think with the witness_block → kernel reasoning pass.
2. Generate {hypothesis_count} candidate hypotheses.
3. For each: confidence band (0.0-1.0), falsifier, disconfirming test.
4. Rank by (confidence × information gain).

## F7 HUMILITY contract
- Omega_0 ∈ [0.03, 0.05] — explicit uncertainty.
- "I don't know" preferred over confident hand-waving.

## F8 GENIUS contract
- G ≥ 0.80 to proceed.
- C_dark < 0.30 — no dark patterns.

## Output format
Return a REASON block:
  hypothesis_1: <string> | confidence: <0-1> | falsifier: <string>
  hypothesis_2: ...
  hypothesis_3: ...
  selected: <H1|H2|H3>
  next_stage_recommendation: MARUAH

Hand off to ⚖ MARUAH.
"""

    registered.append("🧠 REASON")

    # ─── ⚖ MARUAH — 555 CRITIQUE dignity check ─────────────────────────
    @mcp.prompt(
        name="⚖ MARUAH",
        description="⚖ MARUAH — Dignity-floor check (heart/maruah) before judgment.",
        meta={
            "stage": "555_CRITIQUE",
            "sigil": "⚖",
            "lexical": "MARUAH",
            "role": "Heart maruah — dignity check",
            "linked_tools": [
                "arif_think",
                "well_assess_homeostasis",
                "well_guard_dignity",
            ],
            "linked_resources": ["arifos://vitals"],
            "floors_referenced": "F5,F6,F9,F10",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def maruah(reason_block: str) -> str:
        """⚖ MARUAH — dignity check on reason."""
        return f"""⚖ MARUAH — Stage 3/6 of the reality loop

reason_block: {reason_block}

## What to do
1. Call arif_think(mode=critique) → constitutional critique.
2. Call well_guard_dignity → human substrate dignity guard.
3. Compute dignity score: κᵣ ∈ [0, 1], target ≥ 0.70.
4. Identify weakest stakeholder; verify their dignity preserved.

## F5 PEACE² + F6 EMPATHY contracts
- De-escalate; protect weakest stakeholder.
- Reference roles, never name individuals (F6 MARUAH).

## Output format
Return a MARUAH block:
  dignity_score: <0-1>
  weakest_stakeholder: <role>
  dignity_preserved: true|false
  refinements_required: [list]
  next_stage_recommendation: JUDGE

If dignity_preserved=false → return HOLD (do not pass to JUDGE).
Hand off to 🔒 JUDGE.
"""

    registered.append("⚖ MARUAH")

    # ─── 🔍 PREFLIGHT — pre-operation F1-F13 check (was constitutional_pre_flight) ─
    @mcp.prompt(
        name="🔍 PREFLIGHT",
        description=(
            "🔍 PREFLIGHT — Pre-operation F1-F13 check. Catches 888_HOLD triggers before they fire."
        ),
        meta={
            "stage": "PRE_OPERATION",
            "sigil": "🔍",
            "lexical": "PREFLIGHT",
            "role": "F1-F13 floor pre-check",
            "linked_tools": ["arif_observe", "well_classify_substrate"],
            "linked_resources": ["arifos://vitals", "arifos://floors"],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
            "supersedes": "constitutional_pre_flight",
        },
    )
    def preflight(operation: str) -> str:
        """🔍 PREFLIGHT — F1-F13 floor pre-check."""
        return f"""🔍 PREFLIGHT — Pre-operation constitutional check

Before executing '{operation}', verify each floor in F1-F13:

1.  F1  AMANAH       — Is the operation reversible or fully auditable?
2.  F2  TRUTH        — Is every claim grounded with τ ≥ 0.99 (or Ω₀ declared)?
3.  F3  WITNESS      — Do human, AI, and earth signals align ≥ 0.95?
4.  F4  CLARITY      — Will this reduce entropy (ΔS ≤ 0)?
5.  F5  PEACE²       — Does this de-escalate and protect the weakest stakeholder?
6.  F6  EMPATHY      — Is the weakest stakeholder's dignity preserved (κᵣ ≥ 0.70)?
7.  F7  HUMILITY     — Is uncertainty stated explicitly (Ω₀ ∈ [0.03, 0.05])?
8.  F8  GENIUS       — Is the solution both correct and useful (G ≥ 0.80)?
9.  F9  ANTI-HANTU   — C_dark < 0.30; no dark patterns or consciousness performance?
10. F10 ONTOLOGY     — AI-only ontology; no mysticism or soul claims?
11. F11 AUTH         — Is identity verified for destructive actions?
12. F12 INJECTION    — Are adversarial inputs resisted (ρ < 0.85)?
13. F13 SOVEREIGN    — Has Arif ratified this if it crosses the 888_HOLD gate?

If any floor fails → return VOID or HOLD with specific remediation.
"""

    registered.append("🔍 PREFLIGHT")

    # constitutional_pre_flight LEGACY ALIAS REMOVED (2026-08-05). Use 🔍 PREFLIGHT.
    # Rationale: removal epoch 2026-08-16 accelerated per F13 directive.

    # ─── 🔒 JUDGE — 888 JUDGE constitutional gate ────────────────────────
    @mcp.prompt(
        name="🔒 JUDGE",
        description=(
            "🔒 JUDGE — Constitutional gate. Runs arif_judge plus contradiction "
            "evidence. Returns SEAL/HOLD/SABAR/VOID."
        ),
        meta={
            "stage": "888_JUDGE",
            "sigil": "🔒",
            "lexical": "JUDGE",
            "role": "Constitutional gate",
            "linked_tools": ["arif_judge", "geox_contradiction_scan", "geox_falsify"],
            "linked_resources": ["arifos://verdict/{session_id}", "arifos://affordances"],
            "floors_referenced": "F1,F2,F7,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def judge(maruah_block: str) -> str:
        """🔒 JUDGE — constitutional gate with provenance verification."""
        return f"""🔒 JUDGE — Stage 4/6 of the reality loop

maruah_block: {maruah_block}

## What to do
1. Call arif_judge → kernel verdict engine.
2. Call geox_contradiction_scan → cross-domain consistency.
3. Call geox_falsify → Popperian falsification.
4. Compute verdict: SEAL | HOLD | SABAR | VOID.

## F2 PROVENANCE GATE (non-bypassable)
Before issuing SEAL, verify EVERY epistemic tag in the chain:
  - Does the tag trace back to a WITNESS retrieval event with provenance_source?
  - Was the tag assigned at data ingress, or generated later by the model?
  - If any OBS/DER/INT/SPEC tag lacks a provenance_source → VOID.
  - Tags generated at output time without retrieval provenance → F2 violation.
This gate catches labels that the model invented rather than carried.

## F11 AUTH + F13 SOVEREIGN contracts
- Identity verified before any destructive verdict.
- 888_HOLD triggered for: rm-rf, DROP TABLE, force-push, secret rotation,
  vault seal, prod deploy, etc.

## Output format
Return a JUDGE block:
  verdict: SEAL|HOLD|SABAR|VOID
  confidence: <0-1>
  provenance_verified: true|false  ← REQUIRED: did all labels trace to retrieval?
  provenance_violations: [list of tag_ids with missing provenance]
  floors_passed: [list of F-IDs]
  floors_failed: [list of F-IDs]
  remediation_required: <string or null>
  next_stage_recommendation: FORGE|HOLD

Verdict VOID → halt entire loop.
Verdict HOLD → return to 🌊 WITNESS for re-observation.
Verdict SABAR → proceed cautiously to 🔥 FORGE.
Verdict SEAL → proceed to 🔥 FORGE.
"""

    registered.append("🔒 JUDGE")

    # ─── 🔥 FORGE — 777 FORGE execute ────────────────────────────────────
    @mcp.prompt(
        name="🔥 FORGE",
        description=(
            "🔥 FORGE — Execute after an admissible JUDGE verdict. Returns an action "
            "receipt with audit trail."
        ),
        meta={
            "stage": "777_FORGE",
            "sigil": "🔥",
            "lexical": "FORGE",
            "role": "Execute / forge action",
            "linked_tools": ["arif_forge"],
            "linked_resources": ["arifos://continuity/{session_id}", "arifos://affordances"],
            "floors_referenced": "F1,F4,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def forge(judge_block: str) -> str:
        """🔥 FORGE — execute."""
        return f"""🔥 FORGE — Stage 5/6 of the reality loop

judge_block: {judge_block}

## Preconditions
- judge_block.verdict ∈ {{SEAL, SABAR}}
- If HOLD or VOID → return error, do not forge.

## What to do
1. Call arif_forge only with the prior constitutional chain and required authority.
2. Let A-FORGE perform any host mutation under its lease and execution gates.
3. F1 AMANAH: verify reversible (F11 if irreversible).
4. Record continuity chain (call resource arifos://continuity/{{session_id}}).
5. Return action receipt with call_hash + trace_id.

## F4 CLARITY contract
- ΔS ≤ 0 (entropy reduces or stays equal).
- Output should reduce chaos, not increase.

## Output format
Return a FORGE block:
  action_id: <uuid>
  call_hash: <sha256>
  trace_id: <string>
  reversibility: true|false
  audit_trail: [list of receipts]
  next_stage_recommendation: SEAL

Hand off to 💎 SEAL.
"""

    registered.append("🔥 FORGE")

    # ─── 💎 SEAL — 999 SEAL persist ──────────────────────────────────────
    @mcp.prompt(
        name="💎 SEAL",
        description=(
            "💎 SEAL — Prepare an authorized VAULT999 append. Returns a hash-chain "
            "receipt. Terminal loop stage."
        ),
        meta={
            "stage": "999_SEAL",
            "sigil": "💎",
            "lexical": "SEAL",
            "role": "Persist to VAULT999",
            "linked_tools": ["arif_seal"],
            "linked_resources": [
                "arifos://continuity/{session_id}",
                "arifos://seal-readiness",
                "arifos://vault/head",
            ],
            "floors_referenced": "F1,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
        },
    )
    def seal(forge_block: str) -> str:
        """💎 SEAL — persist with provenance chain."""
        return f"""💎 SEAL — Stage 6/6 of the reality loop (TERMINAL)

forge_block: {forge_block}

## Preconditions
- forge_block.reversibility == true OR F13 ratified irreversible.

## What to do
1. An authorized actor calls arif_seal → kernel-controlled VAULT999 append.
2. The prompt prepares evidence only; it cannot append or self-seal.
3. F11 AUDIT: actor_signature + call_hash + trace_id on every receipt.
4. Return seal_id + chain_hash.

## F2 PROVENANCE RECORDING (non-bypassable)
The seal payload MUST include the full provenance chain:
  - Every epistemic tag's retrieval provenance (source + confidence + staleness)
  - The JUDGE block's provenance_verified field
  - If provenance_verified=false → DO NOT SEAL. Return HOLD.
Sealed records embed provenance. A seal without provenance is a decorated receipt.

## F1 AMANAH contract
- Sealed records are immutable (append-only).
- Reversal requires F13 ratification.

## Output format
Return a SEAL block:
  seal_id: <uuid>
  chain_hash: <sha256>
  provenance_chain_verified: true|false  ← REQUIRED
  ledger_path: /var/lib/arifos/vault/SEALED_EVENTS_v2.jsonl
  audit_provenance: <call_hash + trace_id + signature>
  next_action: HUMAN_INIT_NEXT_LOOP_OR_HALT

Loop complete. The human may now start a new loop with 🌱 BOOT + 🌀 SABAR.
"""

    registered.append("💎 SEAL")

    # ─── 🌀 SABAR — Recursive Governed Loop orchestrator ─────────────────
    @mcp.prompt(
        name="🌀 SABAR",
        description=(
            "🌀 SABAR — Governed 6-stage reality-loop template. depth='auto' or "
            "'stage'; grants no authority."
        ),
        meta={
            "stage": "000_LOOP",
            "sigil": "🌀",
            "lexical": "SABAR",
            "role": "Recursive Governed Loop orchestrator",
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
            "version": "2026.08.05",
        },
    )
    def sabar(intent: str, session_id: str = "", depth: str = "stage") -> PromptResult:
        """🌀 SABAR — orchestrator."""
        return sabar_run_loop(intent=intent, session_id=session_id or None, depth=depth)

    registered.append("🌀 SABAR")

    # ─── 📜 REPLY — governed reply envelope (was agi_reply_protocol_v3) ──
    @mcp.prompt(
        name="📜 REPLY",
        description=(
            "📜 REPLY — Governed AGI reply envelope with RACI, truth, floor, and "
            "seal-status fields."
        ),
        meta={
            "stage": "POST_LOOP",
            "sigil": "📜",
            "lexical": "REPLY",
            "role": "Governed reply envelope",
            "linked_tools": ["arif_forge"],
            "linked_resources": ["arifos://continuity/{session_id}"],
            "floors_referenced": "F1,F2,F4,F6,F7,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.08.05",
            "supersedes": "agi_reply_protocol_v3",
        },
    )
    def reply(query: str, recipient_id: str = "human") -> str:
        """📜 REPLY — governed reply envelope."""
        return f"""Compose a governed reply.

Query: {query}
Recipient: {recipient_id}

Required envelope structure:
- TO / CC / TITLE / KEY_CONTEXT header
- RACI block (Responsible, Accountable, Consulted, Informed)
- Computed τ (truth score, ≥ 0.99 or declare Ω₀ ∈ [0.03, 0.05])
- Constitutional floor tags (F1–F13 status)
- SEAL signoff

Constraints:
- If the reply recommends any forge execution, it must pass 888_JUDGE SEAL.
- If F1 (reversibility) or F13 (sovereignty) triggers are active,
  require F13 SOVEREIGN ratification — do NOT bake actor identity into the
  template; use recipient_id or session.actor_id instead.
- Use DELTA compression unless this is a session start or cross-agent handoff.
- F11 AUTH — destructive recommendations must have verified actor.
"""

    registered.append("📜 REPLY")

    # agi_reply_protocol_v3 LEGACY ALIAS REMOVED (2026-08-05). Use 📜 REPLY.
    # Rationale: removal epoch 2026-08-16 accelerated per F13 directive.

    # ─── /init — FULL 10-step autonomous ignition (MCP-native bootstrap) ──
    # 2026-08-04: Distinct from 🌱 BOOT (lightweight). This loads the full
    # operational init.md command file for complete agent ignition with
    # organ probes, FQ gate, ATLAS333, EUREKA777, and RSI Phase 0.
    _INIT_CMD_PATH = "/root/.config/opencode/command/init.md"

    @mcp.prompt(
        name="/init",
        description=(
            "/init — Collapsed 4-step governed ignition (000_INIT v5.0). "
            "Probes kernel, organs, binds session with lane+profile detection, "
            "loads context. Lane detection at init. Governance Profile axis "
            "(OBSERVE/BUILD/MUTATE/DEPLOY). FLAME/ATLAS333/EUREKA777/Graphiti "
            "demoted to intent-driven optional plugins. SCT token stored for seal. "
            "Collapsed from 10 to 4 steps under F13 architectural review 2026-08-07."
        ),
        meta={
            "stage": "BOOT",
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
            "linked_cross_organ_tools": [
                "forge_vault (A-FORGE :7071)",
                "flow_ingest (arifFlow :7073)",
                "flow_health (arifFlow :7073)",
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
            "version": "2026.08.07",
        },
    )
    def init_full(depth: str = "full") -> str:
        """/init — Collapsed 4-step governed ignition sequence. 000_INIT v5.0.

        Loads the complete operational init command from the canonical source.
        Includes: kernel probe, organ probe, session bind (lane+profile detection),
        context load. FLAME/ATLAS333/EUREKA777/Graphiti are optional, intent-driven.
        """
        try:
            with open(_INIT_CMD_PATH, encoding="utf-8") as fh:
                content = fh.read()
                if depth == "summary":
                    lines = content.split("\n")
                    # Return heading + step names only (compact)
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
                f"[/init] Could not load init command from {_INIT_CMD_PATH}: {exc}. "
                f"Fallback: use 🌱 BOOT prompt for lightweight bootstrap, then arif_init tool."
            )

    registered.append("/init")

    # ─── /seal — FULL 11-step autonomous session close (MCP-native) ─────
    _SEAL_CMD_PATH = "/root/.config/opencode/command/seal.md"

    @mcp.prompt(
        name="/seal",
        description=(
            "/seal — Full 11-step autonomous session close ritual (999_CLOSE). "
            "Two-lane: Lane B SESSION_RECEIPT (default) or Lane A CONSTITUTIONAL_SEAL "
            "(threshold). Runs RSI cycle, entropy sweep, arifFlow ingest, EUREKA777 "
            "cooling, carry-forward write, gate fire log, vault record, and verify. "
            "Distinct from 💎 SEAL which is Stage 6 of the governed SABAR loop."
        ),
        meta={
            "stage": "CLOSE",
            "sigil": "🔐",
            "lexical": "SEAL",
            "role": "Full autonomous session close ritual",
            "linked_tools": [
                "arif_seal",
                "arif_judge",
                "aforge_forge_vault",
                "arifflow_flow_ingest",
                "hermes_hermes_fact_check",
                "hermes_hermes_plan_review",
                "hermes_hermes_memory_steward",
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
            "version": "2026.08.04",
        },
    )
    def seal_full(depth: str = "full") -> str:
        """/seal — Full 11-step autonomous session close ritual. 999_CLOSE.

        Loads the complete operational seal command from the canonical source.
        Includes: lane detection, reversibility classification, RSI cycle,
        entropy sweep, arifFlow ingest, EUREKA777 cooling, carry-forward write,
        gate fire log, vault record (Lane B receipt or Lane A constitutional seal),
        verify, and anti-patterns.
        """
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
                f"[/seal] Could not load seal command from {_SEAL_CMD_PATH}: {exc}. "
                f"Fallback: use 💎 SEAL prompt for Stage 6 closure, then forge_vault for receipt."
            )

    registered.append("/seal")

    logger.info(
        "arifOS zen prompts registered: %d (10 zen + 2 bootstrap, 3 legacy aliases archived)",
        len(registered),
    )
    return registered


__all__ = ["register_arifos_prompts", "sabar_run_loop"]
