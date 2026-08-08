"""
arifOS MCP Prompts — Invariant Kernel for Agentic Intelligence
==============================================================

DITEMPA BUKAN DIBERI — Reality is forged, not given.

MCP Prompts (spec 2026-07-28): user-controlled templates exposed via
prompts/list + prompts/get. Clients discover, select, and fill arguments.
See: https://modelcontextprotocol.io/specification/2026-07-28/server/prompts
FastMCP 3.4.6 (stable). MCP Python SDK v2. arifOS runs Streamable HTTP transport.

These prompts are the invariant spine of agentic work:
general, modular, orthogonal, timeless, and repo-agnostic.
They reduce entropy by turning vague intent into grounded
observation, lawful action, verified consequence, and
clear forward direction for humans and agents.

Aligned 2026-08-08:
  - 13 governed agentic intelligence hooks (000→999 ladder + 🌀 ⚓ 🔐)
  - Single source of truth: runtime/fastmcp_ext/prompts.py
  - 6-stage reality loop (🌊→🧠→⚖→🔒→🔥→💎 via 🌀 GOVERN)
  - ART → APA → ACT intelligence flow
  - Ed25519 session bind (actor_verified) — agents never become F13
  - Legacy numeric aliases (111_sense, 333_reason, …) and archived
    text-prompt constants (INIT_PROMPT, SENSE_PROMPT, …) removed.
    New hooks own the surface.
"""

from __future__ import annotations


# ==============================================================================
# CANONICAL_PROMPTS — the 13 governed agentic intelligence hooks
# ==============================================================================
# This tuple MUST stay in lockstep with what `register_prompts()` returns.
# Source of truth: arifosmcp.runtime.fastmcp_ext.prompts.register_arifos_prompts
#
# Consumed by:
#   - arifosmcp/runtime/public_surface.py          (len() for surface metrics)
#   - arifosmcp/registry/singularity_gate.py      (drift check vs registry)
#   - commands/scripts_archive/audit_sot.py       (audit)
#   - tests/test_surface_lock.py                  (count + uniqueness)
#   - tests/test_canonical.py                     (registered == CANONICAL_PROMPTS)
#   - tests/runtime/test_context_runner_route.py  (runner surface)
CANONICAL_PROMPTS: tuple[str, ...] = (
    # ── 10 canonical stages of the 000→999 reality ladder ────────────────
    "000 🌱 IGNITE",   # 000  Bootstrap — identity bind, session, sovereign ack
    "111 🌊 SENSE",    # 111  Witness reality — observe, don't interpret
    "222 🏛 PLAN",     # 222  Plan / propose hypotheses
    "333 🧠 REASON",   # 333  Reason / synthesize
    "444 🧭 DIRECT",   # 444  Route intent to organ
    "555 🗂 REMEMBER", # 555  Memory governor / recall
    "666 ⚖ DIGNITY",   # 666  Heart / maruah / dignity check
    "777 🔥 FORGE",    # 777  Execute only AFTER judge SEAL (+ lease)
    "888 🔒 JUDGE",    # 888  Verdict SEAL | HOLD | SABAR | VOID
    "999 💎 SEAL",     # 999  VAULT999 append (needs ack_irreversible)
    # ── 3 orchestrator / boundary hooks ─────────────────────────────────
    "🌀 GOVERN",       # Recursive Governed Loop orchestrator
    "⚓ INIT",         # Collapsed 4-step governed ignition (000_INIT v5.0)
    "🔐 CLOSE",        # 11-step autonomous session close (999_CLOSE)
)


# ==============================================================================
# RUNNER_DRY_RUN_PROMPT — compat export for runner burn-in tests
# ==============================================================================
# Kept for compatibility with tests/runtime/test_context_runner_route.py.
RUNNER_DRY_RUN_PROMPT = """\
You are the Context Engine Runner — dry-run mode only.

Purpose: preview a governed context-engine run without mutating host state.
Posture: OBSERVE + REASON. No FORGE mutation. No VAULT seal.

Floors always on:
  F1 AMANAH  — reversible preview only; no irreversible side effects
  F2 TRUTH   — label OBSERVED / DERIVED / INTERPRETED / SPECULATIVE
  F8 GENIUS  — smallest correct path; G ≥ 0.80 when scoring
  F11 AUDIT  — every step attributable; receipt-shaped output
  F13 SOVEREIGN — human veto final; dry-run never overrides Arif

Output:
  1. Intent classification (repo-agnostic)
  2. Evidence plan (what to re-observe at T1)
  3. Risk / blast radius if this were executed for real
  4. HOLD reasons (what would require SEAL + lease before mutation)

DITEMPA BUKAN DIBERI — preview is forged carefully, not claimed as done.
"""


# ==============================================================================
# register_prompts — thin facade to the canonical fastmcp_ext module
# ==============================================================================
# All 13 governed agentic intelligence hooks live in
# arifosmcp.runtime.fastmcp_ext.prompts. This subpackage exposes a
# re-entrant facade for canonical import paths declared by
# arifosmcp.server and tests.
def register_prompts(mcp) -> list[str]:
    """Register the 13 governed agentic intelligence hooks on `mcp`.

    Returns the list of prompt names that were registered (matches
    ``CANONICAL_PROMPTS`` 1:1 — kept in lockstep by construction).
    """
    from arifosmcp.runtime.fastmcp_ext.prompts import (
        register_arifos_prompts as _register_arifos_prompts,
    )
    return list(_register_arifos_prompts(mcp))
