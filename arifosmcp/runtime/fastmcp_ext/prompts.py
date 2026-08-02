"""
arifOS MCP Prompts — Zen Federation Surface (2026-07-16).

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

_AGENT_INIT_V3_CANON = "/root/AAA/prompts/INIT.md"  # was AGENT_INIT_v3.0.md → zen-dated 2026.07.17


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
            "version": "2026.07.16",
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
                "version": "2026.07.16",
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
            "version": "2026.07.16",
        },
    )


def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register the 10-zen arifOS MCP prompts + 3 legacy aliases.

        Zen surface (single sigil + single lexical per zen-md):
    🌱 BOOT — boot-phase contract (replaces arif_init_prompt)
          🌊 WITNESS    — 111 SENSE observation
          🧠 REASON     — 333 REASON propose
          ⚖ MARUAH    — 555 CRITIQUE dignity check
          🔍 PREFLIGHT  — pre-operation constitutional check (replaces constitutional_pre_flight)
          🔒 JUDGE      — 888 JUDGE constitutional gate
          🔥 FORGE      — 777 FORGE execute
          💎 SEAL       — 999 SEAL persist
          🌀 SABAR      — Recursive Governed Loop orchestrator
          📜 REPLY      — governed reply envelope (replaces agi_reply_protocol_v3)

        Legacy aliases (compat mode A, one epoch):
          constitutional_pre_flight  → 🔍 PREFLIGHT
          arif_init_prompt          → 🌱 BOOT
          agi_reply_protocol_v3        → 📜 REPLY

        The 🌀 SABAR prompt runs the 6-stage reality loop autonomously:
          🌊 WITNESS → 🧠 REASON → ⚖ MARUAH → 🔒 JUDGE → 🔥 FORGE → 💎 SEAL

        Returns list of registered prompt names (zen + legacy).
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
            "role": "Constitutional bootstrap",
            "linked_tools": ["arif_init"],
            "linked_resources": ["arifos://init/agent_init", "arifos://init/opencode/*"],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
            "supersedes": "arif_init_prompt",
        },
    )
    def boot(depth: str = "boot") -> str:
        """🌱 BOOT — arifOS constitutional bootstrap prompt."""
        if depth == "full":
            try:
                with open(_AGENT_INIT_V3_CANON, encoding="utf-8") as fh:
                    return fh.read()
            except OSError as exc:
                return (
                    f"[🌱 BOOT] Could not load full canon from {_AGENT_INIT_V3_CANON}: {exc}. "
                    f"Falling back to boot phase."
                )
        return """# 🌱 BOOT — arifOS Constitutional Ignition

You are a citizen of the arifOS Federation.
The constitution runs at http://127.0.0.1:8088. Probe before you act.
Sovereign: Arif (F13). Doctrine: DITEMPA BUKAN DIBERI.

## METABOLIC BOOT — run these 6 steps, don't just read them

### 1. PROBE — curl :8088/health
   Verify: verdict=SEAL, floors=13, drift=False.
   If not SEAL → HALT, request bootstrap.

### 2. BIND — arif_init(actor_id, intent, verbosity="minimal")
   Returns session_id + session_token. No session = no work.

### 3. WITNESS — probe all 6 organs + FLAME
   arifos :8088 · aforge :7071 · aaa :3001
   geox :8081 · wealth :18082 · well :18083
   FLAME :18901 (free inference lane)

### 4. CLASSIFY — determine task lane
   CRISIS → high τ, high ρ. FACTUAL → high τ. SOCIAL → high κ.
   CARE → high κ. UNKNOWN → probe more.
   Lane determines which paradoxes govern this task.

### 5. RECOGNIZE — Arif = F13 = absolute veto
   "buat ja la" / "jalan terus" = ACT immediately.
   rm -rf / DROP / force-push / secrets = 888_HOLD.

### 6. ATTEST — emit boot receipt
   BOOT::{session_id}::actor={actor}::organs={n}/6::lane={lane}::closures=3/3

## THREE CLOSURES (Q9–Q11, GENESIS/058 — boot-enforceable)
   Q9  godel_lock        — Every SEAL needs an outside witness.
                            No self-referential seals.
   Q10 calhoun_lock      — Must have an unsolved problem. Must be
                            in a friction arena. Can it fail?
   Q11 refusal_closure   — Constitutional HOLD ≠ failure HOLD.
                            F13 must be able to refuse without justification.
   All three must pass for `closures=3/3`. Any FAIL → HALT.

## IF ANY STEP FAILS → OBSERVE_ONLY (no mutation, no seal)

## After boot: load domain tools on demand
   Geology → geox_*   Market → wealth_*
   Vitality → well_*  Build → aforge_forge_*
   Governance → arif_*

The full canon (TRINITY-33, RSI, ATLAS333, model rotation, refusal surface)
is available as MCP resources: arifos://trinity33, arifos://init/contract,
arifos://models/rotation, arifos://paths, arifos://refusal-surface.
Load them via resources/read when your task demands them.
"""

    registered.append("🌱 BOOT")

    # Legacy alias
    @mcp.prompt(
        name="arif_init_prompt",
        description="[LEGACY ALIAS → 🌱 BOOT] Same behavior, deprecated after 2026-08-16.",
        meta={
            "stage": "PRE_LOOP",
            "sigil": "🌱",
            "lexical": "BOOT",
            "deprecated_alias_of": "🌱 BOOT",
            "removal_epoch": "2026-08-16",
            "linked_tools": ["arif_init"],
            "linked_resources": ["arifos://init/agent_init_v3"],
            "floors_referenced": "F1-F13",
            "federation_layer": "arifOS.kernel.prompts.legacy_alias",
            "version": "2026.07.16",
        },
    )
    def _arif_init_alias(depth: str = "boot") -> str:
        return boot(depth=depth)

    registered.append("arif_init_prompt")

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
            "linked_resources": ["arifos://verdict/{session_id}", "arifos://vitals"],
            "floors_referenced": "F2,F3,F9,F12",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
        },
    )
    def witness(intent: str, focus: str = "") -> str:
        """🌊 WITNESS — observe reality."""
        focus_clause = f" Focus on: {focus}." if focus else ""
        return f"""🌊 WITNESS — Stage 1/6 of the reality loop

intent: {intent}{focus_clause}

## What to do
1. Call arif_observe with intent='{intent}' → capture kernel observations.
2. Call geox_evidence → ground-truth from earth layer.
3. Call well_validate_vitality → human substrate state.
4. Read arifos://vitals → thermodynamic budget.
5. Read arifos://verdict/{{session_id}} → current constitutional verdict.

## F2 TRUTH contract
- Every claim labeled OBS / DER / INT / SPEC.
- Confidence capped at 0.90 for OBS, lower for derived.
- If ground truth absent → emit UNKNOWN + reason.

## Output format
Return a WITNESS block:
  observation: <string>
  confidence: <0.0-1.0>
  epistemic_tag: OBS|DER|INT|SPEC
  floors_passed: [list of F-IDs]
  next_stage_recommendation: REASON

Then hand off to 🧠 REASON.
"""

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
            "version": "2026.07.16",
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
            "version": "2026.07.16",
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
            "linked_resources": ["arifos://vitals"],
            "floors_referenced": "F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,F12,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
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

    # Legacy alias
    @mcp.prompt(
        name="constitutional_pre_flight",
        description="[LEGACY ALIAS → 🔍 PREFLIGHT] Same behavior, deprecated after 2026-08-16.",
        meta={
            "stage": "PRE_OPERATION",
            "sigil": "🔍",
            "lexical": "PREFLIGHT",
            "deprecated_alias_of": "🔍 PREFLIGHT",
            "removal_epoch": "2026-08-16",
            "linked_tools": ["arif_observe", "well_classify_substrate"],
            "linked_resources": ["arifos://vitals"],
            "floors_referenced": "F1-F13",
            "federation_layer": "arifOS.kernel.prompts.legacy_alias",
            "version": "2026.07.16",
        },
    )
    def _preflight_alias(operation: str) -> str:
        return preflight(operation)

    registered.append("constitutional_pre_flight")

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
            "linked_resources": ["arifos://verdict/{session_id}"],
            "floors_referenced": "F1,F2,F7,F11,F13",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
        },
    )
    def judge(maruah_block: str) -> str:
        """🔒 JUDGE — constitutional gate."""
        return f"""🔒 JUDGE — Stage 4/6 of the reality loop

maruah_block: {maruah_block}

## What to do
1. Call arif_judge → kernel verdict engine.
2. Call geox_contradiction_scan → cross-domain consistency.
3. Call geox_falsify → Popperian falsification.
4. Compute verdict: SEAL | HOLD | SABAR | VOID.

## F11 AUTH + F13 SOVEREIGN contracts
- Identity verified before any destructive verdict.
- 888_HOLD triggered for: rm-rf, DROP TABLE, force-push, secret rotation,
  vault seal, prod deploy, etc.

## Output format
Return a JUDGE block:
  verdict: SEAL|HOLD|SABAR|VOID
  confidence: <0-1>
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
            "linked_resources": ["arifos://continuity/{session_id}"],
            "floors_referenced": "F1,F4,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
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
            "linked_resources": ["arifos://continuity/{session_id}"],
            "floors_referenced": "F1,F11",
            "federation_layer": "arifOS.kernel.prompts",
            "version": "2026.07.16",
        },
    )
    def seal(forge_block: str) -> str:
        """💎 SEAL — persist."""
        return f"""💎 SEAL — Stage 6/6 of the reality loop (TERMINAL)

forge_block: {forge_block}

## Preconditions
- forge_block.reversibility == true OR F13 ratified irreversible.

## What to do
1. An authorized actor calls arif_seal → kernel-controlled VAULT999 append.
2. The prompt prepares evidence only; it cannot append or self-seal.
3. F11 AUDIT: actor_signature + call_hash + trace_id on every receipt.
4. Return seal_id + chain_hash.

## F1 AMANAH contract
- Sealed records are immutable (append-only).
- Reversal requires F13 ratification.

## Output format
Return a SEAL block:
  seal_id: <uuid>
  chain_hash: <sha256>
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
            "version": "2026.07.16",
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
            "version": "2026.07.16",
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

    # Legacy alias
    @mcp.prompt(
        name="agi_reply_protocol_v3",
        description="[LEGACY ALIAS → 📜 REPLY] Same behavior, deprecated after 2026-08-16.",
        meta={
            "stage": "POST_LOOP",
            "sigil": "📜",
            "lexical": "REPLY",
            "deprecated_alias_of": "📜 REPLY",
            "removal_epoch": "2026-08-16",
            "linked_tools": ["arif_forge"],
            "linked_resources": ["arifos://continuity/{session_id}"],
            "floors_referenced": "F1-F13",
            "federation_layer": "arifOS.kernel.prompts.legacy_alias",
            "version": "2026.07.16",
        },
    )
    def _reply_alias(query: str, recipient_id: str = "human") -> str:
        return reply(query=query, recipient_id=recipient_id)

    registered.append("agi_reply_protocol_v3")

    logger.info(
        "arifOS zen prompts registered: %d (10 zen + 3 legacy aliases)",
        len(registered),
    )
    return registered


__all__ = ["register_arifos_prompts", "sabar_run_loop"]
