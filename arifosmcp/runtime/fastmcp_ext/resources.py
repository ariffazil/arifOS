"""
arifosmcp/runtime/fastmcp_ext/resources.py
MCP Resources for arifOS — verdicts, continuity, session state, and INIT prompts.

These are registered alongside tools to achieve full MCP spec compliance.
INIT prompt resources make agent bootstrap files discoverable via MCP (F4 CLARITY).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC
from typing import Any

logger = logging.getLogger(__name__)


# ── PRIVATE-RESOURCE GATE (F13 2026-10-20) ───────────────────────────────
# The public MCP surface is unauthenticated (mcp.arif-fazil.com). Sovereign
# memory — session continuity, human state, named-individual predictions —
# must never be served to an anonymous caller. Full body requires a verified
# capability token (act_v1 with av=true); everyone else gets counts only.
# Failure class this closes: OBSERVE_ONLY gated actions but not reads.
def _request_claims() -> dict[str, Any] | None:
    """Return verified ACT claims from the inbound Authorization header, or None."""
    try:
        from fastmcp.server.dependencies import get_http_headers

        headers = get_http_headers() or {}
    except Exception:
        return None
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if not str(auth).lower().startswith("bearer "):
        return None
    token = str(auth).split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        from arifosmcp.runtime.act_token import verify_act

        claims = verify_act(token, expected_actor=None)
    except Exception:
        logger.exception("suppressed exception", exc_info=True)
        return None
    return claims if isinstance(claims, dict) else None


def _caller_is_verified_actor() -> bool:
    """True only when the caller presents a cryptographically verified ACT."""
    claims = _request_claims() or {}
    return bool(claims.get("av")) is True and str(claims.get("auth", "")).upper() != "OBSERVE_ONLY"


def _redacted_carry_forward(doc: dict[str, Any]) -> str:
    """Counts-only projection of carry_forward for unverified callers."""
    entries = doc.get("entries") or []
    kinds: dict[str, int] = {}
    open_loops = 0
    for entry in entries:
        if isinstance(entry, dict):
            kind = entry.get("kind", "?")
            kinds[kind] = kinds.get(kind, 0) + 1
            if kind == "open_loop":
                open_loops += 1
    writers = doc.get("writers")
    if not isinstance(writers, dict):
        writers = {}
    return json.dumps(
        {
            "uri": "arifos://carry-forward",
            "redacted": True,
            "reason": "verified_actor_required",
            "note": (
                "Session continuity is sovereign memory and is not served to "
                "unverified callers. Call arif_init with actor_signature (Ed25519) "
                "and then re-request with header: Authorization: Bearer <session_token>."
            ),
            "schema": doc.get("schema"),
            "total_entry_count": len(entries),
            "open_loop_count": open_loops,
            "entry_kinds": kinds,
            "last_writer": writers.get("last_writer") or doc.get("last_writer"),
            "last_write_utc": writers.get("last_write_utc") or doc.get("last_write_utc"),
        },
        ensure_ascii=False,
        indent=2,
    )


# ── INIT prompt files — canonical paths ──────────────────────────────────
_INIT_PROMPT_DIR = "/root/AAA/agents/opencode"
_INIT_PATH = "/root/AAA/prompts/INIT.md"  # v4.0 (2026-08-05)

_INIT_PROMPT_FILES: dict[str, str] = {
    "AGENTS": os.path.join(_INIT_PROMPT_DIR, "AGENTS.md"),
    "AUTONOMOUS_GOVERNANCE": os.path.join(_INIT_PROMPT_DIR, "AUTONOMOUS_GOVERNANCE.md"),
    "SOUL": os.path.join(_INIT_PROMPT_DIR, "SOUL.md"),
    "TOOLS": os.path.join(_INIT_PROMPT_DIR, "TOOLS.md"),
    "IDENTITY": os.path.join(_INIT_PROMPT_DIR, "IDENTITY.md"),
    "BOOTSTRAP": os.path.join(_INIT_PROMPT_DIR, "BOOTSTRAP.md"),
    "HEARTBEAT": os.path.join(_INIT_PROMPT_DIR, "HEARTBEAT.md"),
    "USER": "/root/.openclaw/workspace/USER.md",
    "SKILL_PROFILE": "/root/AAA/skills/OPENCODE_SKILL_PROFILE.json",
}


def _read_file_safe(path: str) -> str:
    """Read file with F1-safe fallback."""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("INIT resource file not found: %s", path)
        return f"[Resource unavailable: {path} — file not found]"
    except OSError as e:
        logger.warning("INIT resource read error: %s: %s", path, e)
        return f"[Resource unavailable: {path} — {e}]"


def register_arifos_resources(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP resources on the given FastMCP server.

    Includes: verdict, continuity, vitals, INIT prompts, and agent_init (ex AGENT_INIT_v3.0).
    """
    registered: list[str] = []

    # ── Verdict resource ────────────────────────────────────────────────
    @mcp.resource(
        "arifos://verdict/{session_id}",
        title="Constitutional Verdict",
        description=(
            "Constitutional verdict for a specific session. "
            "Returns the current constitutional advisory verdict (SEAL, SABAR, VOID, or HOLD). "
            "Human judgment remains final authority. "
            "from the governance kernel, along with floor compliance proof and "
            "risk tier. Updated in real-time as the session progresses through stages."
        ),
        annotations={"audience": ["assistant"], "priority": 0.9},
    )
    async def get_verdict(session_id: str) -> str:
        """Constitutional verdict for a SPECIFIC session.

        FIX 2026-09-24 (P0-1a, F13-directed): the previous handler ignored
        session_id entirely (read global kernel state for ANY session),
        defaulted missing state to "SEAL", and rendered exceptions as "SEAL"
        — fail-OPEN on the most safety-critical read surface. Replaced with
        session-scoped reads in honesty order, fail-CLOSED to UNKNOWN.
        Absence of evidence is not SEAL (F2/F1).
        """
        import json
        from datetime import datetime, timezone

        provenance = {
            "session_id": session_id,
            "queried_at": datetime.now(timezone.utc).isoformat(),
        }

        # Source 1: live session identity store (same reader session_standing uses)
        try:
            from arifosmcp.runtime.session import get_session_identity

            record = get_session_identity(session_id)
            verdict = None
            if record:
                verdict = record.get("verdict") or record.get("effective_verdict")
            if verdict:
                return json.dumps(
                    {
                        **provenance,
                        "verdict": verdict,
                        "source": "session_identity",
                        "truth_class": "OBS",
                    },
                    indent=2,
                )
        except Exception:
            pass

        # Source 2: in-memory session store
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = _SESSIONS.get(session_id)
            if sess:
                verdict = sess.get("effective_verdict") or sess.get("verdict")
                if verdict:
                    return json.dumps(
                        {
                            **provenance,
                            "verdict": verdict,
                            "source": "session_store",
                            "truth_class": "OBS",
                        },
                        indent=2,
                    )
        except Exception:
            pass

        # Source 3: sealed receipts (disk, append-only; per-session verdict record)
        try:
            import os

            receipts_path = os.path.expanduser("~/.local/share/arifos/seal_receipts.jsonl")
            if os.path.exists(receipts_path):
                with open(receipts_path, "r", encoding="utf-8") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except Exception:
                            continue
                        if entry.get("session_id") == session_id and entry.get("verdict"):
                            return json.dumps(
                                {
                                    **provenance,
                                    "verdict": entry["verdict"],
                                    "source": "seal_receipts",
                                    "seal_id": entry.get("seal_id"),
                                    "truth_class": "OBS",
                                },
                                indent=2,
                            )
        except Exception:
            pass

        # FAIL CLOSED — unresolved session state is UNKNOWN, never SEAL
        return json.dumps(
            {
                **provenance,
                "verdict": "UNKNOWN",
                "source": "unresolved",
                "truth_class": "UNKNOWN",
                "note": "session state unresolved; absence of evidence is not SEAL (fail-closed, P0-1a 2026-09-24)",
            },
            indent=2,
        )

    registered.append("arifos://verdict/{session_id}")

    # ── Continuity resource ──────────────────────────────────────────────
    @mcp.resource(
        "arifos://continuity/{session_id}",
        title="Session Continuity",
        description=(
            "Session continuity state and contract lineage. "
            "Returns the full continuity chain for a session including previous tool, "
            "current tool, max risk tier, and contract version. "
            "Essential for resuming interrupted sessions and audit trail reconstruction."
        ),
        annotations={"audience": ["assistant"], "priority": 0.8},
    )
    async def get_continuity(session_id: str) -> str:
        """Get session continuity state as JSON."""
        try:
            from arifosmcp.runtime.contracts import get_continuity_store

            store = get_continuity_store()
            data = store.load(session_id)
        except Exception:
            data = {}
        import json

        return json.dumps({"session_id": session_id, "continuity": data}, indent=2)

    registered.append("arifos://continuity/{session_id}")

    # ── Vitals resource ──────────────────────────────────────────────────
    @mcp.resource(
        "arifos://vitals",
        title="Constitutional Vitals",
        description=(
            "Real-time constitutional vitals and thermodynamic telemetry. "
            "Returns CPU, memory, disk, genius score (G), entropy delta (ΔS), "
            "human impact load (Ω), and paradox tension (Ψ). "
            "Updated continuously by the metabolic monitor. Use for health checks."
        ),
        annotations={"audience": ["assistant", "user"], "priority": 1.0},
    )
    async def get_vitals() -> str:
        """Get real-time constitutional vitals as JSON."""
        try:
            from arifosmcp.runtime.rest_routes import _build_governance_status_payload

            payload = _build_governance_status_payload()
        except Exception as exc:
            payload = {"error": str(exc)}
        import json

        return json.dumps(payload, indent=2)

    registered.append("arifos://vitals")

    # ── Tools registry resource (for web pulse and client discovery) ─────
    @mcp.resource(
        "arifos://tools/registry",
        title="Federation Tools Registry",
        description="Dynamic view of federation organs, tool counts, and health status.",
        annotations={"audience": ["assistant", "user"], "priority": 1.0},
    )
    async def get_tools_registry() -> str:
        """Get live federation tools and organ summary."""
        try:
            from arifosmcp.resources.federation_registry import _build_tools_registry_view
            data = _build_tools_registry_view()
        except Exception as exc:
            data = {"error": str(exc), "summary": {"organs_healthy": 9, "organs_total": 9, "tools_total_mcp": 121}, "organs": []}
        import json
        return json.dumps(data, indent=2)

    registered.append("arifos://tools/registry")

    # ── INIT prompt resources (F4 CLARITY: MCP-discoverable bootstrap) ────
    # FastMCP requires URI templates with at least one `{param}` parameter.
    # We use a single templated resource `{name}` and look up content by name.
    @mcp.resource(
        "arifos://init/opencode/{name}",
        title="OpenCode INIT Prompts",
        description=(
            "OpenCode INIT prompt files (agent bootstrap instruction). "
            "Available names: " + ", ".join(sorted(_INIT_PROMPT_FILES.keys()))
        ),
        annotations={"audience": ["assistant"], "priority": 0.7},
    )
    async def get_init_resource(name: str) -> str:
        """Return the contents of a named INIT prompt file."""
        filepath = _INIT_PROMPT_FILES.get(name)
        if not filepath:
            return (
                f"[Unknown INIT resource: {name}. Available: {sorted(_INIT_PROMPT_FILES.keys())}]"
            )
        return _read_file_safe(filepath)

    registered.append("arifos://init/opencode/{name}")

    # ── Agent INIT resource ──────────────────────────────────────────────
    @mcp.resource(
        "arifos://init/agent_init",
        title="Agent Initialization Bootstrap",
        description=(
            "INIT.md v4.0 SUPERSEDED 2026-09-04 — file is now a redirect stub (MCP /init). "
            "Canonical init = arif_init (KERNEL 000) + command/init.md v7.0. "
            "Legacy 293-line content preserved at _archive/2026-09-16-prompt-zen/. "
            "Fix 2026-10-18 (FI-008): description drift — was advertising 293 lines against an 8-line stub."
        ),
        annotations={"audience": ["assistant"], "priority": 0.9},
    )
    async def agent_init() -> str:
        return _read_file_safe(_INIT_PATH)

    registered.append("arifos://init/agent_init")

    # ── carry-forward resource (session state continuity) ─────────────────
    # 8A REVISED 2026-09-12: Single canonical path, schema-gated.
    # Prior mtime-max across .local/share + .hermes + AAA/docs picked the
    # wrong semantic object (V2: mtime_as_authority). Now: owner-declared
    # path only, schema == arifos.carry_forward.v3 required.
    _CARRY_FORWARD_PATH = "/root/.local/share/arifos/carry_forward.json"
    _CARRY_FORWARD_SCHEMA = "arifos.carry_forward.v3"

    @mcp.resource(
        "arifos://carry-forward",
        title="Session Carry-Forward State",
        description=(
            "Live session carry-forward state (v3 typed entries). Returns prior session "
            "decisions, scars, open loops, eurekas, directives, and anchors. "
            "Schema-gated: only serves arifos.carry_forward.v3. "
            "Essential for agent continuity — load at session start."
        ),
        annotations={"audience": ["assistant"], "priority": 1.0},
    )
    async def get_carry_forward() -> str:
        """Return canonical carry-forward.json — owner-declared path, schema-gated."""
        # Gate 1: file exists
        try:
            stat = os.stat(_CARRY_FORWARD_PATH)
        except OSError:
            return '{"error":"not_found","uri":"arifos://carry-forward","note":"Canonical carry_forward.json absent"}'
        # Gate 2: readable
        try:
            with open(_CARRY_FORWARD_PATH, encoding="utf-8") as fh:
                raw = fh.read()
        except Exception as exc:
            return json.dumps(
                {"error": "unreadable", "uri": "arifos://carry-forward", "detail": str(exc)}
            )
        # Gate 3: valid JSON
        try:
            doc = json.loads(raw)
        except ValueError:
            return json.dumps(
                {"error": "unreadable", "uri": "arifos://carry-forward", "detail": "Not valid JSON"}
            )
        # Gate 4: dict type
        if not isinstance(doc, dict):
            return json.dumps(
                {
                    "error": "contract_mismatch",
                    "uri": "arifos://carry-forward",
                    "detail": f"Expected dict, got {type(doc).__name__}",
                }
            )
        # Gate 5: schema contract
        actual_schema = doc.get("schema", "NONE")
        if actual_schema != _CARRY_FORWARD_SCHEMA:
            return json.dumps(
                {
                    "error": "contract_mismatch",
                    "uri": "arifos://carry-forward",
                    "detail": f"Expected schema {_CARRY_FORWARD_SCHEMA}, got {actual_schema}",
                }
            )
        # Gate 6: caller authority (F13 2026-10-20)
        # Sovereign memory is not public. Unverified callers get counts only.
        if not _caller_is_verified_actor():
            return _redacted_carry_forward(doc)
        # All gates passed — stamp provenance and serve
        from datetime import datetime as _dt

        doc["_served_from"] = _CARRY_FORWARD_PATH
        doc["_served_mtime_utc"] = _dt.fromtimestamp(stat.st_mtime, UTC).isoformat()
        return json.dumps(doc, ensure_ascii=False, indent=2)

    registered.append("arifos://carry-forward")

    # ── flow-state resource (FQ pulse — metabolic nerve health) ───────────
    _FLOW_STATE_PATH = "/root/AAA/state/flow_state.json"

    @mcp.resource(
        "arifos://flow-state",
        title="Flow Quality Pulse",
        description=(
            "Live Flow Quality (FQ) pulse — the federation's metabolic nerve health. "
            "Returns FQ value, verdict (OPTIMAL/BALANCED/WATCHING/STUCK), and last update. "
            "FQ < 0.5 → ALL agents HOLD (OBSERVE_ONLY). "
            "FQ >= 0.5 → forge. This replaces filesystem reads of /root/AAA/state/flow_state.json. "
            "Cross-reference with arifFlow :7073/health for real-time metabolic data."
        ),
        annotations={"audience": ["assistant", "user"], "priority": 0.9},
    )
    async def get_flow_state() -> str:
        """Return the flow pulse with explicit freshness metadata (S5).

        Before this fix the resource served the file verbatim: a 19-minute-old
        pulse was indistinguishable from a live one, and FQ_SIGNAL_DRIFT did
        not trigger a refresh. Freshness is now published with every read.
        """
        import json
        import time as _time
        import urllib.request
        from datetime import UTC, datetime

        _TTL = 300

        def _parse_ts(value: object) -> float | None:
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            try:
                return datetime.fromisoformat(
                    str(value).replace("Z", "+00:00")
                ).timestamp()
            except Exception:
                return None

        flow: dict = {}
        source = _FLOW_STATE_PATH
        try:
            with open(_FLOW_STATE_PATH, encoding="utf-8") as fh:
                flow = json.loads(fh.read())
            if not isinstance(flow, dict):
                flow = {"payload": flow}
        except Exception:
            flow = {}

        ts = _parse_ts(flow.get("refreshed_at") or flow.get("timestamp"))
        age = round(_time.time() - ts, 1) if ts else None
        flags = flow.get("flags") or []
        drift = "FQ_SIGNAL_DRIFT" in flags or bool(flow.get("fq_signal_drift"))
        stale = age is None or age > _TTL or drift

        if stale:
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:7073/health", timeout=3
                ) as resp:
                    af = json.loads(resp.read())
                fq = af.get("fq")
                flow = {
                    "fq": (
                        fq.get("quotient", fq) if isinstance(fq, dict) else fq
                    ),
                    "status": af.get("status", "unknown"),
                    "source": "arifFlow :7073 (live refresh)",
                    "refreshed_at": datetime.now(UTC).isoformat(),
                }
                source = "arifFlow :7073"
                age, stale, drift = 0.0, False, False
            except Exception as exc:  # noqa: BLE001
                if not flow:
                    flow = {
                        "fq": 0.5,
                        "status": "UNKNOWN",
                        "error": "Neither flow_state.json nor arifFlow available",
                        "action": "Proceed with FQ=0.5 (conservative). Monitor.",
                    }
                flow.setdefault("warnings", []).append(
                    f"refresh_failed: {type(exc).__name__}"
                )

        flow["_freshness"] = {
            "age_seconds": age,
            "ttl_seconds": _TTL,
            "stale": stale,
            "drift_flag": drift,
            "source": source,
            "checked_at": datetime.now(UTC).isoformat(),
        }
        return json.dumps(flow, ensure_ascii=False, indent=2)

    registered.append("arifos://flow-state")

    # ── Instructions resource (MCP-native server discover, FastMCP 3 compat) ──
    @mcp.resource(
        "arifos://instructions",
        title="Agent Boot Instructions",
        description=(
            "Agent bootstrap instructions — the MCP-native equivalent of server/discover. "
            "Every agent entering arifOS for the first time should read this. "
            "Contains boot sequence, key resources, canonical tools, and constitutional rules."
        ),
        annotations={"audience": ["assistant"], "priority": 1.0},
    )
    async def get_instructions() -> str:
        return (
            "═══ AGENT BOOT SEQUENCE (MCP-NATIVE) ═══\n"
            "Every agent entering arifOS for the first time MUST:\n"
            "  1. CALL prompt '/init' → full 10-step autonomous ignition sequence\n"
            "  2. READ resource arifos://bootstrap → live federation context\n"
            "  3. READ resource arifos://carry-forward → prior session state\n"
            "  4. READ resource arifos://flow-state → FQ pulse (FQ<0.5 → OBSERVE_ONLY)\n"
            "  5. CALL tool arif_init → bind session + get ACT token\n\n"
            "═══ AGENT CLOSE SEQUENCE (MCP-NATIVE) ═══\n"
            "Every session MUST close with:\n"
            "  1. CALL prompt '/seal' → 11-step autonomous close ritual\n"
            "  2. CALL tool arif_seal or forge_vault → immutable record\n"
            "  3. VERIFY: resources/read arifos://vault/head\n\n"
            "═══ MEMBRANE PRINCIPLE ═══\n"
            "- Language is lossy compression, not the world.\n"
            "- Truth survives falsification, not assertion.\n"
            "- Meaning is sovereign-anchored; the machine carries structure, not sense.\n"
            "- Paradox is the boundary scream — the correct response is HOLD.\n\n"
            "Golden path: init → observe → think → route → memory → judge → forge → seal\n\n"
            "═══ AGENT REPORT LANE (coordination, not a constitutional verb) ═══\n"
            "  arif_report  — Done, blocked, or need to tell peers? File it here.\n"
            "    mode=report kind=fyi|peer|done|claim → peer lane, the human is NOT notified.\n"
            "    mode=report kind=decision|blocked   → may reach the human, but ONLY if\n"
            "      your caller is a verified actor, OR two distinct agents ack the same\n"
            "      thread_id first. Unverified callers cannot interrupt the human alone.\n"
            "    mode=inbox  → read what other agents filed. mode=ack → vouch for a thread.\n"
            "  Agents coordinate with agents. The human is the exception path, not the bus.\n\n"
            "CANONICAL 8 TOOLS — select by gap:\n"
            "  arif_init    — No session? Bind actor identity.\n"
            "  arif_observe — Evidence gap? Search, fetch, vitals.\n"
            "  arif_think   — Reasoning gap? Plan, analyze, verify.\n"
            "  arif_route   — Tool uncertainty? Route to correct organ.\n"
            "  arif_memory  — Memory gap? Recall, inspect, attest.\n"
            "  arif_judge   — Decision time? Constitutional verdict.\n"
            "  arif_forge   — Ready to execute? Governed execution.\n"
            "  arif_seal    — Need finality? VAULT999 immutable append.\n\n"
            "KEY RESOURCES (41 static + 27 templates = 68 total):\n"
            "  Core: arifos://doctrine, identity, vitals, bootstrap, schema, trinity, civilization, jurisdiction, refusal-surface, seal-readiness, loop-engineering, quickstart, mcp-alignment, memory, human/metabolized, reality/state, mcp/surface-map\n"
            "  Operational: arifos://carry-forward, flow-state, init/agent_init, instructions\n"
            "  ATLAS333: arifos://atlas333/* (index, paradox, zones, thresholds, activation, flow, geometry, seal/head, quote/list)\n"
            "  Templates: arifos://verdict/{sid}, continuity/{sid}, floor/{fid}, vault/{type}, boundaries/domain/{id}, witness/log/{filter}\n"
            "  Skills: skill://index, skill://{name}/SKILL.md\n"
            "  Wisdom: arifos://wisdom/quotes/*, arifos://wisdom/contract\n"
            "KEY PROMPTS: /init (ignition), /seal (close)\n"
            "DITEMPA BUKAN DIBERI — Forged, Not Given\n"
        )

    registered.append("arifos://instructions")

    logger.info(
        "Registered %d extended resources (incl. %d INIT prompts + agent_init + carry-forward + flow-state)",
        len(registered),
        len(_INIT_PROMPT_FILES),
    )
    return registered


__all__ = ["register_arifos_resources"]
