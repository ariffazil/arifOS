"""
arifosmcp/tools/kernel_canonical.py — 444_KERNEL_CANONICAL
═══════════════════════════════════════════════════════════

RULE 14 MODE-FIRST NAMING canonical tools.
Replaces the 16-mode bloat in arif_kernel_route with 5 clean named tools.

Each tool has ONE responsibility. Modes are internal expansion, not naming.

Canonical tools (stable names):
  arif_route        — route intent to organ (new canonical routing entry point)
  arif_triage       — session status, priority, preflight
  arif_kernel_status — telemetry, discovery, prediction health
  arif_bridge_connect — direct organ tool call (canonical noun_verb name, forged 2026-06-21)
  arif_bridge       — [DEPRECATED] legacy noun-only name, retained for backward compat

Soft-deprecated (still work, emit warning):
  arif_kernel_route — absorbs all old modes via passthrough

Ratified: 2026-06-20
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import logging
import re
from pathlib import Path
from typing import Any

from arifosmcp.core.federation_contracts import validate_organ_output
from arifosmcp.federation.federation_envelope import (
    attach_degraded_claim,
    build_degraded_claim,
    build_federation_envelope,
    finalize_response_envelope,
    inject_envelope_into_call_args,
)
from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _hold, _ok

# ATLAS333 Cognitive Geometry — 222_MAP bridge
from core.shared.atlas import Φ


def _token_in(token: str, text: str) -> bool:
    """Substring match with word boundaries for short / single-token keywords.

    HARDEN-C calibration (2026-07-12): bare ``in`` matching let capital token
    ``irr`` fire inside ``irreversible`` and GEOX token ``rs`` fire inside the
    same word — WEALTH won over WELL for substrate-readiness intents.

    Multi-word phrases stay pure substring (specific enough). Tokens shorter
    than 5 chars, or single tokens of any length that are pure alphanumerics,
    require non-alnum boundaries on both sides.
    """
    if not token:
        return False
    t = token.lower()
    if " " in t or "-" in t or "_" in t or "/" in t:
        return t in text
    if len(t) >= 6 and t.isalpha():
        # Long pure words: still boundary-aware to avoid mid-word hits
        return re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", text) is not None
    return re.search(rf"(?<![a-z0-9]){re.escape(t)}(?![a-z0-9])", text) is not None


logger = logging.getLogger(__name__)

try:
    from arifosmcp.core.tool_self_model import SURPRISE_WINDOW_SIZE
except ImportError:
    SURPRISE_WINDOW_SIZE = 10

_BRIDGE_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=4)

# ─── Intent map cache ────────────────────────────────────────────────────────
_intent_map_cache: dict[str, Any] | None = None


def _load_intent_map() -> dict[str, Any]:
    """Load organ intent map once, cache forever."""
    global _intent_map_cache
    if _intent_map_cache is not None:
        return _intent_map_cache
    try:
        import yaml

        map_path = Path(__file__).parent.parent / "config" / "organ_intent_map.yaml"
        if map_path.exists():
            with open(map_path) as f:
                _intent_map_cache = yaml.safe_load(f)
                return _intent_map_cache
    except Exception:
        pass
    # Fallback: hardcoded map — G13 FIX (2026-06-30): machine domain + AAA added
    _intent_map_cache = {
        "organ_routes": {
            "arifos": {
                "organ": "arifOS",
                "port": 8088,
                "intent_keywords": [
                    # Machine / MCP surface
                    "MCP",
                    "MCP server",
                    "MCP tool",
                    "MCP endpoint",
                    "MCP connector",
                    "MCP diagnostic",
                    "MCP conformance",
                    "MCP surface",
                    "ChatGPT connector",
                    "OpenAI connector",
                    "Copilot connector",
                    "surface drift",
                    "connector schema",
                    "connector cache",
                    "protocol version",
                    "protocol drift",
                    "protocol conformance",
                    "tool registry",
                    "tool schema",
                    "tool conformance",
                    "tool surface",
                    "tool manifest",
                    "tools/list",
                    "tools/call",
                    "capability surface",
                    "capability lease",
                    # Governance / constitutional
                    "kernel health",
                    "kernel status",
                    "kernel route",
                    "kernel attest",
                    "arifos kernel",
                    "arifos health",
                    "arifos status",
                    "constitutional floor",
                    "constitutional check",
                    "governance check",
                    "governance status",
                    "seal boundary",
                    "seal verdict",
                    "authority envelope",
                    "epistemic tag",
                    "cognitive axis",
                    # Session / memory / vault
                    "initialize session",
                    "session init",
                    "session anchor",
                    "memory recall",
                    "memory search",
                    "vault seal",
                    "vault ledger",
                    "lease request",
                    "belief state",
                    "runtime schema",
                    # Canonical tool names
                    "arif init",
                    "arif route",
                    "arif triage",
                    "arif judge",
                    "arif seal",
                    "arif measure",
                    "arif observe",
                    "arif think",
                    "arif critique",
                    "arif bridge",
                    "arif gateway",
                    "arif forge",
                    "arif_forge",
                    "arif memory",
                    "arif_memory",
                    "arif session",
                    "arif vault",
                    # Federation
                    "federation contract",
                    "federation manifest",
                    "organ attestation",
                    "organ health",
                    "agentic search",
                    "agent registry",
                    # Sovereign / personal decisions
                    "life roadmap",
                    "career decision",
                    "personal decision",
                    "what should i do",
                    "life direction",
                    "should i leave",
                    "should i stay",
                    "human sovereign",
                    "sovereign decision",
                    "life choice",
                    "exit strategy",
                    "what do i want",
                    "my future",
                ],
            },
            "aaa": {
                "organ": "AAA",
                "port": 3001,
                "intent_keywords": [
                    # ROUTING-CALIBRATION FIX (2026-07-12): added federation
                    # state/topology and broadcast keywords so AAA domain queries
                    # route correctly instead of falling through to arifOS default
                    "cockpit",
                    "dashboard",
                    "control plane",
                    "AAA cockpit",
                    "AAA dashboard",
                    "agent identity",
                    "agent registry cockpit",
                    "permission list",
                    "access control",
                    "audit log",
                    "federation health",
                    "approval queue",
                    "A2A gateway",
                    "identity anchor",
                    "throttle",
                    "federation state",
                    "federation topology",
                    "agent topology",
                    "agent map",
                    "organ map",
                    "federation map",
                    "broadcast message",
                    "broadcast to all",
                    "topology map",
                    "state and topology",
                ],
            },
            "a_forge": {
                "organ": "A-FORGE",
                "port": 7071,
                "intent_keywords": [
                    # ROUTING-CALIBRATION FIX (2026-07-12): added explicit
                    # service-restart phrases so "restart the arifos service"
                    # routes to A-FORGE despite "arifos" being in the intent.
                    # These are longer than any arifOS keyword for the same text.
                    "build",
                    "deploy",
                    "forge",
                    "compile",
                    "commit",
                    "push",
                    "git",
                    "docker",
                    "container",
                    "image",
                    "pipeline",
                    "ci/cd",
                    "jenkins",
                    "github",
                    "repository",
                    "version",
                    "dry run",
                    "dry-run",
                    "execute plan",
                    "node install",
                    "npm install",
                    "npm build",
                    "npm test",
                    "uv sync",
                    "docker compose",
                    "systemctl restart",
                    "systemd unit",
                    "service restart",
                    "service stop",
                    "restart the service",
                    "restart the arifos service",
                    "restart arifos service",
                    "restart the well service",
                    "restart well service",
                    "stop the service",
                    "stop the well service",
                    "stop the arifos service",
                    "stop service",
                    "make deploy",
                    "code deploy",
                    "rollback",
                    "mutate file",
                    "forge execute",
                    "forge plan",
                    "forge dryrun",
                    "staged code change",
                    "staged deploy",
                    "deploy with rollback",
                ],
            },
            "geox": {
                "organ": "GEOX",
                "port": 8081,
                "intent_keywords": [
                    "seismic",
                    "well log",
                    "las",
                    "petrophysics",
                    "horizon",
                    "fault",
                    "amplitude",
                    "basin",
                    "prospect",
                    "subsurface",
                    "velocity",
                    "lithology",
                    "porosity",
                    "permeability",
                    "resistivity",
                    "gamma ray",
                    "sonic",
                    "density",
                    "structural",
                    "trap",
                    # SERP API: academic/local domain (2026-07-07)
                    "scholar",
                    "academic paper",
                    "research paper",
                    "citation",
                    "patent",
                    "patent search",
                    "geology consultant",
                    "local business",
                    "geological survey",
                ],
            },
            "wealth": {
                "organ": "WEALTH",
                "port": 18082,
                "intent_keywords": [
                    "portfolio",
                    "npv",
                    "irr",
                    "emv",
                    "option",
                    "derivative",
                    "capital",
                    "hedge",
                    "risk metric",
                    "risk assessment",
                    "allocation",
                    "stress test",
                    # SERP API: finance/commerce/trends domain (2026-07-07)
                    "stock price",
                    "stock quote",
                    "market data",
                    "market overview",
                    "crypto price",
                    "forex rate",
                    "exchange rate",
                    "commodity price",
                    "bond yield",
                    "finance search",
                    "product price",
                    "shopping",
                    "price comparison",
                    "market trends",
                    "search trends",
                    "trending topics",
                    "fiscal data",
                    "gdp",
                    "inflation",
                ],
            },
            "well": {
                "organ": "WELL",
                "port": 18083,
                "intent_keywords": [
                    # G13 FIX: human-vitality-only keywords
                    # ROUTING-CALIBRATION FIX (2026-07-12): added explicit
                    # human-state phrases so WELL matches without being stolen
                    "human health",
                    "personal health",
                    "wellness",
                    "vitality",
                    "biometric",
                    "sleep",
                    "heart rate",
                    "hrv",
                    "metabolic",
                    "readiness",
                    "recovery",
                    "autonomic",
                    "wellbeing",
                    "maruah",
                    "fatigue",
                    "cognition load",
                    "cognitive clarity",
                    "stress load",
                    "decision readiness",
                    "fit to decide",
                    "human readiness",
                    "operator readiness",
                    "operator fatigue",
                    "substrate readiness",
                    "human decision readiness",
                    "feeling tired",
                    "feeling stressed",
                    "high stakes decision",
                    # SERP API: travel domain (2026-07-07)
                    "flight search",
                    "hotel search",
                    "travel planning",
                    "flight deal",
                    "hotel review",
                    "travel destination",
                    "rest planning",
                    "vacation",
                ],
            },
        }
    }
    return _intent_map_cache


def _route_intent_to_organ(intent: str, explicit_organ: str | None = None) -> str:
    """Resolve organ by keyword matching against intent map."""
    if explicit_organ:
        return explicit_organ.lower()
    if not intent:
        return "arifOS"
    intent_lower = intent.lower()

    # ── RSI-GATE-1 / W-A-HELDOUT (2026-07-17): injection → kernel ────────────
    # Prompt-override language is a constitutional concern (F12), never a
    # domain-organ or forge route — even if "forge"/"deploy" also appears.
    _INJECTION_PATTERNS = (
        "ignore previous instructions",
        "ignore all previous",
        "disregard previous instructions",
        "disregard all previous",
        "ignore prior instructions",
        "jailbreak",
        "dan mode",
        "developer mode override",
    )
    if any(p in intent_lower for p in _INJECTION_PATTERNS):
        return "arifOS"

    # Governance seal collocates beat geological bare "seal" (GEOX trap seal).
    if "seal" in intent_lower and any(
        g in intent_lower
        for g in (
            "verdict",
            "should we seal",
            "should i seal",
            "seal this",
            "seal the verdict",
            "seal decision",
        )
    ):
        if not any(
            geo in intent_lower
            for geo in ("trap", "source rock", "top seal", "seal rock", "migration pathway")
        ):
            return "arifOS"

    # Human readiness subject beats execute verbs ("am I too tired to approve deploy").
    _HUMAN_TIRED = (
        "too tired",
        "am i too tired",
        "i am too tired",
        "tired to approve",
        "exhausted to",
        "sleep debt",
        "too fatigued",
    )
    if any(p in intent_lower for p in _HUMAN_TIRED) or (
        _token_in("tired", intent_lower)
        and any(p in intent_lower for p in ("am i", "i am", "i too"))
    ):
        return "well"

    # Multi-domain collision (≥3 distinct domains) → arifOS, not random winner.
    # Catches garbage soup like "money geology well fatigue deploy".
    _GEO_MARKERS = (
        "seismic",
        "geology",
        "geological",
        "geoscience",
        "basin",
        "porosity",
        "petrophysics",
        "horizon",
        "well log",
    )
    _CAP_MARKERS = (
        "npv",
        "irr",
        "emv",
        "portfolio",
        "capital",
        "investment",
        "money",
        "fiscal",
    )
    _WELL_MARKERS = (
        "tired",
        "fatigue",
        "biometric",
        "sleep",
        "vitality",
        "readiness",
        "hrv",
        "wellness",
    )
    _FORGE_MARKERS = (
        "deploy",
        "commit",
        "docker",
        "forge",
        "systemctl",
        "npm build",
        "git push",
    )
    _domain_hits = 0
    if any(_token_in(t, intent_lower) or t in intent_lower for t in _GEO_MARKERS):
        _domain_hits += 1
    if any(_token_in(t, intent_lower) or t in intent_lower for t in _CAP_MARKERS):
        _domain_hits += 1
    if any(_token_in(t, intent_lower) or t in intent_lower for t in _WELL_MARKERS):
        _domain_hits += 1
    if any(_token_in(t, intent_lower) or t in intent_lower for t in _FORGE_MARKERS):
        _domain_hits += 1
    if _domain_hits >= 3:
        return "arifOS"

    # ── Hard kernel guard (2026-06-30): MCP/kernel/diagnostic queries MUST route ─
    # to arifOS. These are kernel-level concerns, never domain-organ concerns.
    # The keyword map below handles normal cases; this guard catches edge cases
    # where a domain organ (e.g. WELL "health") would otherwise win.
    #
    # G14 FIX (2026-07-04): The original guard was over-greedy — it caught
    # "organ health" and "organ attestation" even when the intent was an
    # organ-qualified query like "WELL organ health" or "GEOX organ health",
    # which should route to the named organ, not to arifOS. Fix: detect an
    # organ-qualified phrase first (e.g. "WELL organ X", "GEOX earth Y")
    # and route to that organ BEFORE the kernel guard fires.
    _ORGAN_NAMES = ("WELL", "GEOX", "WEALTH", "AAA", "A-FORGE", "AFORGE", "ARIFOS")

    # Step 1: organ-qualified phrases win — ONLY for explicit organ queries.
    # HARDEN-C P0 (2026-07-12): bare " well " must NOT match geoscience
    # "seismic well tie" / "well log" — only explicit WELL-organ phrases.
    # ROUTING-CALIBRATION FIX (2026-07-12): bare organ name in intent (e.g.
    # "restart the arifos service") must NOT trigger Step 1 — only explicit
    # organ-query patterns (organ at start or followed by organ/health/status).
    # RSI-GATE-1: also accept trailing "… of GEOX" / "organ health of GEOX".
    for organ_name in _ORGAN_NAMES:
        organ_lower = organ_name.lower().replace("-", " ").replace("a forge", "a_forge")
        if organ_name == "WELL":
            _well_organ_phrases = (
                "well organ",
                "well readiness",
                "well vitality",
                "well substrate",
                "well mcp",
                "well health check",
                "well homeostasis",
                "well dignity",
                " the well organ",
                "well://",
            )
            # "well fatigue" alone is organ-ish only when not multi-domain soup
            # (multi-domain already returned arifOS above when ≥3 domains).
            if "well fatigue" in intent_lower and _domain_hits < 2:
                _well_organ_phrases = (*_well_organ_phrases, "well fatigue")
            if any(p in intent_lower for p in _well_organ_phrases) or intent_lower.startswith(
                "well organ"
            ):
                # Still exclude pure geoscience if "well log/tie/desurvey" dominates
                _geo_well = (
                    "well log",
                    "well tie",
                    "well_qc",
                    "well_desurvey",
                    "well_ingest",
                    "seismic well",
                    "well logs",
                )
                if any(g in intent_lower for g in _geo_well) and "well organ" not in intent_lower:
                    continue
                return "well"
            continue  # never bare-token match WELL
        # ROUTING-CALIBRATION FIX: only match explicit organ queries, not bare
        # mentions like "restart the arifos service" (should route to A-FORGE).
        # Bare " arifos " in mid-intent now requires organ/health/status qualifier.
        # RSI-GATE-1 trailing form: "organ health of geox", "status of wealth".
        _trailing_of = f"of {organ_lower}" in intent_lower or intent_lower.rstrip("?.! ").endswith(
            organ_lower
        )
        _organ_query_context = any(
            q in intent_lower
            for q in (
                "organ health",
                "organ status",
                "organ state",
                "organ attestation",
                "health of",
                "status of",
                "state of",
            )
        )
        if _trailing_of and _organ_query_context:
            _exec_verbs = ("restart", "deploy", "stop", "start", "build")
            if not any(v in intent_lower for v in _exec_verbs):
                return organ_lower.replace(" ", "_").replace("a_forge", "a-forge")
        if not (
            intent_lower.startswith(organ_lower + " ") or f" {organ_lower} organ " in intent_lower
        ):
            # Mid-intent bare match: only if followed by health/status/state/kernel
            mid_patterns = (
                f" {organ_lower} health",
                f" {organ_lower} status",
                f" {organ_lower} state",
                f" {organ_lower} kernel",
                f" {organ_lower} organ ",
            )
            if not any(p in intent_lower for p in mid_patterns):
                continue
            # Additional guard: if the intent contains execution verbs like
            # "restart", "deploy", "build" — don't route to the mentioned organ.
            _exec_verbs = ("restart", "deploy", "stop", "start", "build")
            if any(v in intent_lower for v in _exec_verbs):
                continue
        return organ_lower.replace(" ", "_").replace("a_forge", "a-forge")

    # Step 2: kernel guard for kernel-level concerns (MCP / constitutional / governance)
    _KERNEL_GUARD_PATTERNS: list[str] = [
        "mcp ",
        "mcp server",
        "mcp tool",
        "mcp endpoint",
        "mcp connector",
        "mcp surface",
        "mcp diagnostic",
        "mcp conformance",
        "mcp protocol",
        "chatgpt connector",
        "openai connector",
        "copilot connector",
        "tool registry",
        "tool schema",
        "tool conformance",
        "tool list",
        "tools/list",
        "tools/call",
        "tool surface",
        "tool manifest",
        "surface drift",
        "connector schema",
        "connector cache",
        "protocol version",
        "protocol drift",
        "protocol conformance",
        "capability surface",
        "capability lease",
        "kernel health",
        "kernel status",
        "kernel route",
        "kernel attest",
        "arifos kernel",
        "arifos health",
        "arifos status",
        "arifos mcp",
        "constitutional floor",
        "constitutional check",
        "governance check",
        "governance status",
        "seal boundary",
        "seal verdict",
        "authority envelope",
        "federation contract",
        "federation manifest",
        # G14 FIX: removed "organ attestation" and "organ health" from the
        # kernel guard. Organ-qualified phrases are caught in Step 1 above.
        # Unqualified "organ attestation" still routes to arifOS via the
        # YAML keyword map (arifos.intent_keywords: "organ attestation").
        "arifos organ attestation",
        "arifos organ health",
    ]
    for pattern in _KERNEL_GUARD_PATTERNS:
        if pattern in intent_lower:
            return "arifOS"

    # Step 3: YAML intent map — scored match (HARDEN-C 2026-07-12)
    # Longest-only failed: "prospect" (8) beat "npv" (3) for "NPV of a prospect".
    # Score = sum of matched keyword lengths; capital verbs get a boost when
    # explicit capital tokens appear; geo "well *" no longer steals WELL organ.
    # 2026-07-12 calibration: word-boundary matching for short tokens so
    # "irr"/"rs" no longer hijack "irreversible" / readiness intents.
    # RSI-GATE-1: sequential "then" — earth-before-capital skips capital boost.
    intent_map = _load_intent_map()
    organ_routes = intent_map.get("organ_routes", {})
    _CAPITAL_TOKENS = (
        "npv",
        "irr",
        "emv",
        "cash flow",
        "cash runway",
        "runway",
        "portfolio",
        "capital",
        "investment",
    )
    _EARTH_SEQ_TOKENS = (
        "seismic",
        "geology",
        "geological",
        "geoscience",
        "interpretation",
        "petrophysics",
        "well log",
        "basin",
    )
    _has_capital = any(_token_in(t, intent_lower) for t in _CAPITAL_TOKENS)
    _sequential_earth_first = False
    if " then " in intent_lower and _has_capital:
        _geo_positions = [
            intent_lower.find(t) for t in _EARTH_SEQ_TOKENS if intent_lower.find(t) >= 0
        ]
        _cap_positions = [
            intent_lower.find(t) for t in _CAPITAL_TOKENS if _token_in(t, intent_lower)
        ]
        if _geo_positions and _cap_positions and min(_geo_positions) < min(_cap_positions):
            _sequential_earth_first = True
    scores: dict[str, int] = {}
    for organ_key, organ_config in organ_routes.items():
        organ_label = str(organ_config.get("organ", organ_key.upper()))
        score = 0
        for kw in organ_config.get("intent_keywords", []):
            kl = kw.lower()
            if _token_in(kl, intent_lower):
                score += len(kl)
                # Prefer multi-word / exact phrases
                if " " in kl or "-" in kl:
                    score += 2
        if score <= 0:
            continue
        if organ_label.upper() == "WEALTH" and _has_capital and not _sequential_earth_first:
            score += 12  # capital verb outweighs lone geology noun "prospect"
        if organ_label.upper() == "GEOX" and _sequential_earth_first:
            score += 10  # first-stage earth work in "A then B" pipelines
        if organ_label.upper() == "GEOX" and _has_capital and _token_in("prospect", intent_lower):
            # demote pure prospect hit when capital terms present
            score = max(0, score - 6)
        # Bare geological "seal" must not beat governance when already handled;
        # demote single-token seal hits if no other geo evidence.
        if organ_label.upper() == "GEOX" and _token_in("seal", intent_lower):
            _other_geo = any(
                _token_in(t, intent_lower)
                for t in ("trap", "source rock", "reservoir", "migration", "seismic", "geology")
            )
            if not _other_geo and score <= 6:
                score = 0
        scores[organ_label] = scores.get(organ_label, 0) + score
    # Drop zeroed labels
    scores = {k: v for k, v in scores.items() if v > 0}
    if scores:
        best_match = max(scores.items(), key=lambda kv: kv[1])[0]
        return best_match
    return "arifOS"


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 1: arif_route
# ═══════════════════════════════════════════════════════════════════════════════


def _bind_identity(actor_id: str | None, session_id: str | None) -> tuple[str | None, str | None]:
    """Recover actor/session from session store when MCP drops or nulls identity.

    Explicit non-anon actor_id always wins. Session-bound actor fills gaps.
    Prevents wrap_legacy_call / outer envelope coercing to openclaw-anon when
    the caller already passed a verified session.

    P0 FIX (2026-07-19): every ingress path runs through
    ``normalize_actor_id`` so that aliases (``ARIF``, ``Muhammad Arif``,
    greetings, sovereign variants) collapse to the canonical machine ID
    before any comparison, dispatch, or bridge hand-off. The repository's
    canonical machine ID remains lowercase ``arif``; sovereign identity may
    be represented separately as ``ARIF_FAZIL`` downstream. Normalization
    never grants verification — it is NLP convenience only.
    """
    from arifosmcp.runtime.governance_identity import normalize_actor_id

    _ANON = frozenset({None, "", "anonymous", "openclaw-anon", "unknown", "null"})
    aid = actor_id if actor_id not in _ANON else None
    sid = session_id if session_id not in _ANON else None
    if sid:
        try:
            from arifosmcp.runtime.tools import _SESSIONS

            sess = _SESSIONS.get(sid) or {}
            if not aid:
                cand = sess.get("actor_id") or sess.get("canonical_actor_id")
                if cand and cand not in _ANON:
                    aid = str(cand)
        except Exception:
            pass
    # P0 invariant: no raw actor value escapes this function unnormalized.
    if aid is not None:
        try:
            _norm = normalize_actor_id(aid)
            if _norm:
                aid = _norm
        except Exception:
            # Fail-soft: lowercase fallback rather than crash the kernel.
            aid = aid.lower()
    return aid, sid


def arif_route(
    intent: str | None = None,
    organ: str | None = None,
    task: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    session_token: str | None = None,
    organ_tool: str | None = None,
    arguments: dict[str, Any] | str | None = None,
    mission_id: str | None = None,
    _envelope: Any = None,
    contract_c_kwargs: dict | None = None,
) -> dict[str, Any]:
    """
    Canonical routing entry point. Routes an intent to the correct organ.

    RULE 14: Mode-first. This is ONE tool for all routing decisions.
    The mode parameter does not exist here — routing is the only operation.

    Args:
        intent:        Natural-language description of what the user wants.
                      e.g. "interpret this seismic section", "assess portfolio risk"
        organ:        Optional explicit organ override. If provided, intent matching
                      is skipped and this organ is used directly.
        task:         Alias for intent (backward compat).
        actor_id:     Calling actor.
        session_id:   Governing session.
        session_token: SCT from arif_init (ChatGPT continuity).
        organ_tool:   The tool name on the target organ to call.
                      If absent, returns routing decision only (no bridge call).
        arguments:    Arguments to pass to organ_tool.
        mission_id:   Explicit human-cockpit mission binding (investigate|interpret|
                      decide|build|monitor|remember). When set, skips keyword
                      classification and binds the six-mission plan. Preferred
                      over free-text when the agent already knows the mission.

    Returns:
        routing_decision:  organ, port, tool_prefix, mission plan
        bridge_result:    (if organ_tool provided) result from organ tool call

    Example:
        arif_route(intent="seismic interpretation")
        → {"organ": "GEOX", "port": 8081, "tool_prefix": "geox_", "status": "routed"}

        arif_route(mission_id="investigate", intent="site health")
        → mission plan + routed organ for investigate pipeline

        arif_route(intent="portfolio stress test", organ_tool="wealth_portfolio",
                   arguments={"mode": "stress"})
        → routes to WEALTH, calls wealth_portfolio(mode="stress"), returns result
    """
    # F1 AMANAH: Parse arguments if received as JSON string (MCP transport issue)
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                f"arif_route: arguments received as unparseable string: {arguments[:100]}"
            )
            arguments = None

    # Normalize intent — mission_id alone is valid (cockpit binding)
    if not intent and task:
        intent = task
    if not intent and mission_id:
        intent = f"mission:{mission_id.strip().lower()}"
    if not intent:
        intent = ""

    actor_id, session_id = _bind_identity(actor_id, session_id)
    # Prefer identity inside arguments._envelope if tool args lost top-level fields
    if arguments and isinstance(arguments, dict):
        env = arguments.get("_envelope") or {}
        if isinstance(env, dict):
            if not actor_id and env.get("actor_id"):
                actor_id = env.get("actor_id")
            if not session_id and env.get("session_id"):
                session_id = env.get("session_id")
            if not session_token and env.get("session_token"):
                session_token = env.get("session_token")
            actor_id, session_id = _bind_identity(actor_id, session_id)

    # SCT continuity: recover session from token when ChatGPT only has SCT
    if session_token and not session_id:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            st = resolve_standing(
                session_token=session_token,
                actor_id=actor_id,
                allow_store=True,
            )
            if st.valid and st.session_id:
                session_id = st.session_id
            if st.valid and st.actor_id and not actor_id:
                actor_id = st.actor_id
        except Exception:
            pass

    floor_check = check_laws("arif_route", {"intent": intent or mission_id or "route"}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_route",
            floor_check["reason"],
            floor_check["violated_laws"],
            session_id=session_id,
        )

    # Kernel dispatch gate: if _envelope provided (cross-organ), session must match live issued one
    # (This is before organ runs — wall, not policy)
    if arguments and isinstance(arguments, dict) and "_envelope" in arguments:
        env = arguments.get("_envelope") or {}
        if session_id and env.get("session_id") and env.get("session_id") != session_id:
            return _hold(
                "arif_route",
                "Kernel reject: _envelope.session_id does not match live session issued by kernel",
            )

    # ── Mission binding (six-mission cockpit) ─────────────────────────────
    # Explicit mission_id wins; else classify free-text intent. Fail-soft if
    # mission_router module is unavailable on older deploys.
    mission_payload: dict[str, Any] | None = None
    try:
        from arifosmcp.mission_router import (
            classify_mission,
            plan_from_mission_id,
            plan_to_dict,
        )

        if mission_id:
            try:
                _plan = plan_from_mission_id(mission_id)
            except ValueError as e:
                return _hold("arif_route", str(e), ["L04"], session_id=session_id)
        else:
            _plan = classify_mission(intent or "investigate")
        mission_payload = plan_to_dict(_plan)
        # If caller did not pin an organ, prefer mission primary organ
        if not organ and mission_payload.get("primary_organ"):
            organ = str(mission_payload["primary_organ"])
    except Exception as _mission_err:
        logger.debug("arif_route mission binding soft-fail: %s", _mission_err)
        mission_payload = None

    target_organ = _route_intent_to_organ(intent, organ)
    intent_map = _load_intent_map()
    # G15 FIX (2026-07-04): normalize organ lookup key so "A-FORGE" → "a_forge"
    # matches the YAML key. Previously hyphens caused A-FORGE route to miss config
    # and return port=0 / tool_prefix="".
    lookup_key = target_organ.lower().replace("-", "_")
    organ_config = intent_map.get("organ_routes", {}).get(lookup_key, {})

    # Fix 2026-07-06 ROUND-2: Organ registry allowlist — reject unknown organs.
    # Previously, any string as organ would get routed with port=0, tool_prefix="",
    # routing_confidence=0.95. Now: if organ_config is empty AND the organ was
    # explicitly provided (not inferred from intent), reject with HOLD.
    if not organ_config and organ:
        return _hold(
            "arif_route",
            f"UNKNOWN_ORGAN: '{organ}' is not a registered federation organ. "
            f"Known organs: {sorted(intent_map.get('organ_routes', {}).keys())}. "
            f"Cannot route to unregistered organ (F8 GENIUS: simplest correct path).",
            ["L08"],
        )
    # If organ was inferred from intent and still no config, default to arifOS
    if not organ_config:
        organ_config = intent_map.get("organ_routes", {}).get("arifos", {})
        target_organ = "arifos"

    port = organ_config.get("port", 0)
    tool_prefix = organ_config.get("tool_prefix", "")

    routing = {
        "intent": intent,
        "mission_id": (mission_payload or {}).get("mission_id") or mission_id,
        "organ": target_organ.upper(),
        "port": port,
        "tool_prefix": tool_prefix,
        "organ_tool": organ_tool,
        "status": "routed",
        "routing_rule": "mission_id" if mission_id else "intent_map",
        # TIME INVARIANT: source_of_truth chain — tracks provenance of this
        # routing decision. When bridged to an organ, the organ receives this
        # chain so it knows where the request originated and with what context.
        "source_of_truth": {
            "origin": "arif_route",
            "actor_id": actor_id,
            "session_id": session_id,
            "timestamp": __import__("time").time(),
            "routing_confidence": 0.99
            if mission_id
            else (0.95 if organ else 0.85),
            "chain": [
                {"step": "intent_received", "timestamp": __import__("time").time()},
                {
                    "step": "mission_bound",
                    "mission_id": (mission_payload or {}).get("mission_id") or mission_id,
                    "classified_by": (mission_payload or {}).get("classified_by"),
                    "timestamp": __import__("time").time(),
                },
                {
                    "step": "organ_resolved",
                    "organ": target_organ.upper(),
                    "timestamp": __import__("time").time(),
                },
            ],
        },
    }
    if mission_payload:
        routing["mission"] = mission_payload
        # Engine-room hint for site work — not a human menu
        if mission_payload.get("mission_id") in ("build", "monitor", "investigate"):
            routing["web_zen_hint"] = mission_payload.get("web_zen")

    # ── ATLAS333 Cognitive Geometry Enrichment (222_MAP) ──────────────────────
    # Φ(intent) → GPV(lane, τ, κ, ρ, paradox_axes, query_type)
    # Enriches route context with cognitive geometry for downstream tools.
    # Fail-soft: GPV enrichment never breaks routing (F1 AMANAH).
    try:
        _gpv = Φ(intent)
        routing["gpv"] = {
            "lane": _gpv.lane,
            "τ": _gpv.tau,
            "κ": _gpv.kappa,
            "ρ": _gpv.rho,
            "paradox_axes": _gpv.paradox_axes,
            "query_type": _gpv.query_type.value,
        }
        routing["source_of_truth"]["chain"].append(
            {
                "step": "atlas333_gpv_resolved",
                "lane": _gpv.lane,
                "τ": _gpv.tau,
                "κ": _gpv.kappa,
                "ρ": _gpv.rho,
                "paradox_axes": _gpv.paradox_axes,
                "timestamp": __import__("time").time(),
            }
        )
    except Exception:
        pass

    # P2 FIX 2026-06-30: Verdict monotonicity — HOLD > DEGRADED > SEAL.
    # ChatGPT audit caught: arif_route returned verdict: SEAL while inner signals
    # said hold_required: true + floor_passed: false. That is a contradiction.
    # Rule: if any critical subsignal fires HOLD, outer verdict CANNOT be SEAL.
    def _routing_hold_required(r: dict) -> bool:
        """Check if any inner subsignal requires HOLD."""
        if r.get("hold_required") is True:
            return True
        if r.get("floor_passed") is False:
            return True
        nine = r.get("nine_signal") or {}
        if isinstance(nine, dict):
            overall = nine.get("overall") or {}
            if isinstance(overall, dict) and overall.get("state") in ("SYUBHAH", "HOLD", "VOID"):
                return True
        return False

    def _route_ok(payload: dict[str, Any]) -> dict[str, Any]:
        payload = {
            **payload,
            "actor_id": actor_id,
            "session_id": session_id,
        }
        return _ok(
            "arif_route",
            payload,
            meta={"actor_id": actor_id},
            session_id=session_id,
        )

    def _route_hold(reason: str, extra: dict | None = None) -> dict[str, Any]:
        return _hold(
            "arif_route",
            reason,
            extra_meta={**(extra or {}), "actor_id": actor_id, "session_id": session_id},
            session_id=session_id,
        )

    # If no organ_tool specified, return routing decision only
    if not organ_tool:
        if _routing_hold_required(routing):
            return _route_hold(
                "Routing HOLD: inner subsignal requires hold (floor_passed=false or hold_required=true)",
                {"routing": routing},
            )
        return _route_ok(routing)

    if session_id:
        from arifosmcp.runtime.work_spine import consume

        for resource, name in (("delegation", None), ("tool_call", organ_tool)):
            budget_state = consume(session_id, resource, name=name)
            if not budget_state["allowed"]:
                return _route_hold(
                    budget_state["reason"],
                    {"work_budget": budget_state["snapshot"]},
                )

    # Build transport _envelope from live session state (ALWAYS populated, never re-typed by caller)
    # Vector #7 (2026-07-20): SCT propagation — session_token was previously dropped
    # here, breaking cross-organ authority parity. GEOX/WEALTH/WELL received no SCT
    # and defaulted to OBSERVE_ONLY regardless of the caller's actual session authority.
    _envelope = {
        "session_id": session_id,
        "session_token": session_token,
        "constitutional_chain_id": session_id or "cc-none",
        "actor_id": actor_id,
        "trace_id": f"trace_{int(__import__('time').time() * 1000)}_{actor_id or 'anon'}",
    }
    call_args = dict(arguments or {})
    # Force envelope identity — do not let stale null envelope win
    prev_env = call_args.get("_envelope") if isinstance(call_args.get("_envelope"), dict) else {}
    call_args["_envelope"] = {**prev_env, **{k: v for k, v in _envelope.items() if v is not None}}

    # Bridge call to organ
    if target_organ.lower() == "geox":
        result = _bridge_geox(organ_tool, call_args, session_id, actor_id, session_token)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "wealth":
        result = _bridge_wealth(organ_tool, call_args, session_id, actor_id, session_token)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "well":
        result = _bridge_well(organ_tool, call_args, session_id, actor_id, session_token)
        routing["bridge_result"] = result
        routing["bridge_status"] = "called"
        if _routing_hold_required(routing):
            return _route_hold("Bridge HOLD: inner subsignal requires hold", {"routing": routing})
        return _route_ok(routing)

    if target_organ.lower() == "a-forge":
        return _route_ok({**routing, "bridge_status": "a-forge: use A-FORGE MCP directly"})

    if target_organ.lower() == "aaa":
        return _route_ok({**routing, "bridge_status": "aaa: cockpit/identity — use AAA:3001"})

    if target_organ.lower() == "arifos":
        return _route_ok({**routing, "bridge_status": "kernel-local: no bridge needed"})

    return _route_hold(f"Unknown organ: {target_organ}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 2: arif_triage
# ═══════════════════════════════════════════════════════════════════════════════


def arif_triage(
    mode: str = "status",
    session_id: str | None = None,
    session_token: str | None = None,
    stage: str | None = None,
    actor_id: str | None = None,
    priority: str | None = None,
    _envelope: Any = None,
) -> dict[str, Any]:
    """
    Session status, priority queue, and preflight checks.

    RULE 14: One tool, defined modes.
    Modes:
        status     — active session count and current stage
        preflight  — pre-session safety probe (no session required)
        triage     — priority assessment for a task

    Args:
        mode:        "status" | "preflight" | "triage"
        session_id:   Optional session to query
        session_token: SCT (preferred) — signed capability from arif_init
        stage:       Stage hint (used if session_id not provided)
        actor_id:    Calling actor
        priority:    Task priority hint for triage mode

    Returns:
        Structured triage data appropriate to mode.
    """
    floor_check = check_laws("arif_triage", {"mode": mode}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_triage", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.tools import _SESSIONS

    if mode == "status":
        prediction_health = _get_prediction_health()
        live_stage = "unknown"
        stage_source = "unknown"
        if session_id:
            sess = _SESSIONS.get(session_id, {})
            live_stage = sess.get("stage", stage or "unknown")
            stage_source = "session"
        elif stage:
            live_stage = stage
            stage_source = "parameter"
        else:
            # F5 FIX (2026-07-07): When no session_id provided, find the most
            # recent session's stage instead of returning "unknown". Claude
            # feedback: 63 sessions all showing stage="unknown" is misleading.
            try:
                most_recent = None
                most_recent_ts = 0
                for sid, sess in _SESSIONS.items():
                    if isinstance(sess, dict):
                        ts = (
                            sess.get("expires_at_unix", 0)
                            or sess.get("created_at_unix", 0)
                            or sess.get("issued_at", 0)
                            or sess.get("created_at_ts", 0)
                        )
                        if isinstance(ts, (int, float)) and ts > most_recent_ts:
                            most_recent_ts = ts
                            most_recent = sess
                if most_recent and most_recent.get("stage"):
                    live_stage = most_recent["stage"]
                    stage_source = "most_recent_session"
            except Exception:
                pass
        return _ok(
            "arif_triage",
            {
                "active_sessions": len(_SESSIONS),
                "stage": live_stage,
                "stage_source": stage_source,
                "prediction_health": prediction_health,
                "mode": "status",
            },
        )

    if mode == "preflight":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.sct import resolve_standing

        session_id_present = bool(session_id) or bool(session_token)
        actor_id_present = bool(actor_id)

        # SCT Slice 1: inhabit via token first; store is optional cache.
        _actor_verified = False
        _authority_mode = "OBSERVE_ONLY"
        _stage_from_session = stage or "000"
        _session_found = False
        _standing_source = "none"
        _session_token_out: str | None = None
        _apex_scalars: dict[str, Any] | None = None
        _sid_resolved = session_id

        standing = resolve_standing(
            session_token=session_token,
            session_id=session_id,
            actor_id=actor_id,
            tool="arif_triage",
            mode="preflight",
            allow_store=True,
        )
        if standing.valid:
            _session_found = True
            _actor_verified = standing.actor_verified
            _authority_mode = standing.authority
            _stage_from_session = standing.stage or stage or "000"
            _standing_source = standing.source
            _session_token_out = standing.session_token
            _apex_scalars = dict(standing.apex)
            _sid_resolved = standing.session_id or session_id
        elif session_id and not session_token:
            sess = _SESSIONS.get(session_id)
            if sess and isinstance(sess, dict):
                _session_found = True
                _actor_verified = sess.get("actor_verified", False)
                _authority_mode = sess.get("authority", "OBSERVE_ONLY")
                _stage_from_session = sess.get("stage", stage or "000")
                _standing_source = "store"

        preflight_payload: dict[str, Any] = {
            "kernel": "alive",
            "observe_only": (not _actor_verified) or _authority_mode == "OBSERVE_ONLY",
            "mutation_allowed": _actor_verified
            and _authority_mode in ("FULL", "SOVEREIGN", "LIMITED_MUTATE"),
            "external_side_effects_allowed": False,
            "irreversible_allowed": False,
            "session_required": True,
            "session_id_present": session_id_present,
            "session_found": _session_found,
            "session_id": _sid_resolved,
            "actor_id_present": actor_id_present,
            "actor_verified": _actor_verified,
            "authority_mode": _authority_mode,
            "stage": _stage_from_session,
            "standing_source": _standing_source,
            "canonical_tool_count": len(CANONICAL_TOOLS),
            "active_sessions": len(_SESSIONS),
            "next_safe_action": "Call arif_init(mode='ping' | 'light' | 'full')",
            "mode": "preflight",
        }
        if _session_token_out:
            preflight_payload["session_token"] = _session_token_out
        if _apex_scalars:
            preflight_payload["apex_scalars"] = _apex_scalars

        if not session_id_present:
            return _hold(
                "arif_triage",
                reason="SESSION_REQUIRED",
                floors=["F11"],
                extra_meta={
                    "hold_reason": "SESSION_REQUIRED",
                    "required_precondition_failed": "session_id_or_session_token",
                    "next_safe_action": "arif_init",
                    "preflight_diagnostics": preflight_payload,
                },
            )
        if not _session_found:
            return _hold(
                "arif_triage",
                reason="SESSION_NOT_FOUND",
                floors=["F11"],
                extra_meta={
                    "hold_reason": "SESSION_NOT_FOUND",
                    "required_precondition_failed": "valid_session_id_or_session_token",
                    "next_safe_action": "arif_init",
                    "preflight_diagnostics": preflight_payload,
                },
            )
        out = _ok("arif_triage", preflight_payload, session_id=_sid_resolved)
        if isinstance(out, dict) and _session_token_out:
            out["session_token"] = _session_token_out
            if _apex_scalars:
                out["apex_scalars"] = _apex_scalars
            out["standing_source"] = _standing_source
        return out

    if mode == "triage":
        # Simple priority classification
        priority_map = {
            "critical": 1,
            "high": 2,
            "normal": 3,
            "low": 4,
        }
        q_priority = priority_map.get(priority.lower() if priority else "normal", 3)
        return _ok(
            "arif_triage",
            {
                "priority": priority or "normal",
                "priority_score": q_priority,
                "queue_depth": 0,
                "recommended_lane": "AGI" if q_priority <= 2 else "AGI",
                "mode": "triage",
            },
        )

    return _hold("arif_triage", f"Unknown mode: {mode}")


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 3: arif_bridge_connect (low-level organ call)
# ═══════════════════════════════════════════════════════════════════════════════
# arif_bridge_connect (CANONICAL, forged 2026-06-21): follows arif_<noun>_<verb> convention.


def arif_bridge_connect(
    organ: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Low-level direct organ tool call.
    Requires server-side authorization — organ and tool must be known ahead of time.

    RULE 14: This is a direct bridge, not routing by intent.
    Use arif_route for intent-based routing. Use arif_bridge only when
    the organ and tool are known ahead of time.

    This is the internal bridge implementation also used by arif_route.

    Args:
        organ:       "geox" | "wealth" | "well" (case-insensitive)
        tool_name:   MCP tool name on the target organ
        arguments:   Tool arguments dict
        actor_id:    Server-derived actor (NOT model-asserted)
        session_id:  Governing session from arif_init

    Returns:
        Kernel-wrapped organ output with envelope.
    """
    actor_id, session_id = _bind_identity(actor_id, session_id)
    floor_check = check_laws("arif_bridge", {"organ": organ, "tool": tool_name}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_bridge",
            floor_check["reason"],
            floor_check["violated_laws"],
            session_id=session_id,
        )

    # IDENTITY PROPAGATION: always inject _envelope; merge, never drop identity.
    _args = dict(arguments or {})
    _env = {
        "session_id": session_id,
        "actor_id": actor_id,
        "source_organ": "arifOS",
    }
    prev = _args.get("_envelope") if isinstance(_args.get("_envelope"), dict) else {}
    _args["_envelope"] = {**prev, **{k: v for k, v in _env.items() if v is not None}}

    organ_lower = organ.lower()
    if organ_lower == "geox":
        return _bridge_geox(tool_name, _args, session_id, actor_id)
    if organ_lower == "wealth":
        return _bridge_wealth(tool_name, _args, session_id, actor_id)
    if organ_lower == "well":
        return _bridge_well(tool_name, _args, session_id, actor_id)
    return _hold("arif_bridge", f"Unknown organ: {organ}", session_id=session_id)


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 5: arif_kernel_attest (organ attestation)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_attest(
    organ: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Live organ attestation. One tool, organ is a parameter.

    RULE 14: One tool, organ is a parameter, not a name.
    If organ is None, attest all organs.

    Args:
        organ:      Specific organ to attest, or None for all
        actor_id:   Calling actor
        session_id: Governing session

    Returns:
        Per-organ attestation records with liveness.
    """
    floor_check = check_laws("arif_kernel_attest", {"organ": organ or "all"}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_attest", floor_check["reason"], floor_check["violated_laws"])

    import asyncio

    from arifosmcp.runtime.heartbeat_registry import federation_liveness
    from arifosmcp.runtime.organ_attestation import attest_all_organs, attest_organ

    if organ and organ.upper() in ("GEOX", "WEALTH", "WELL", "arifOS"):
        result = asyncio.run(attest_organ(organ.upper(), actor_id=actor_id, session_id=session_id))
        return _ok("arif_kernel_attest", {"mode": "single", "organ": organ.upper(), **result})

    result = asyncio.run(attest_all_organs(actor_id=actor_id, session_id=session_id))
    liveness = federation_liveness()
    return _ok(
        "arif_kernel_attest",
        {
            "mode": "all",
            "attestation": result,
            "liveness": liveness,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL TOOL 6: arif_kernel_health (federation health)
# ═══════════════════════════════════════════════════════════════════════════════


def arif_kernel_health(
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Federation liveness heartbeat snapshot.
    One tool, no modes needed — health is singular.

    Args:
        actor_id: Calling actor

    Returns:
        Federation-wide liveness data.
    """
    floor_check = check_laws("arif_kernel_health", {}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_kernel_health", floor_check["reason"], floor_check["violated_laws"])

    from arifosmcp.runtime.heartbeat_registry import federation_liveness

    liveness = federation_liveness()
    return _ok("arif_kernel_health", {"liveness": liveness})


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _run_async(coro) -> Any:
    """Run async coroutine from sync context."""
    try:
        asyncio.get_running_loop()
        future = _BRIDGE_EXECUTOR.submit(asyncio.run, coro)
        return future.result(timeout=60)
    except RuntimeError:
        return asyncio.run(coro)


def _assert_organ_attested(organ: str) -> dict[str, Any] | None:
    """Fail-closed gate: require recent ALIVE attestation before bridging.

    Lazy re-attest once if registry is empty/stale after kernel restart
    (in-memory attestation evaporates on process recycle while organs stay live).
    """
    from arifosmcp.runtime.heartbeat_registry import is_organ_stale
    from arifosmcp.runtime.organ_attestation import (
        attest_organ,
        get_organ_attestation,
        is_healthy,
    )

    oid = organ.upper()
    rec = get_organ_attestation(oid)

    def _needs_refresh(r) -> bool:
        if r is None:
            return True
        if r.status in ("REVOKED", "DEGRADED_CLAIM", "DEGRADED", "UNATTESTED"):
            return True
        try:
            if is_organ_stale(oid):
                return True
        except Exception:
            return True
        return False

    if _needs_refresh(rec):
        try:
            result = _run_async(attest_organ(oid))
            # attest_organ returns dict; re-read registry
            rec = get_organ_attestation(oid)
            if rec is None and isinstance(result, dict):
                # Some paths return inline status without registry write
                st = result.get("status") or result.get("attestation", {}).get("status") or ""
                if not is_healthy(st) and st not in ("ALIVE", "alive"):
                    return _hold(
                        "arif_bridge",
                        f"Organ {organ} re-attest failed: {result.get('status') or result}",
                    )
        except Exception as exc:
            return _hold(
                "arif_bridge",
                f"Organ {organ} has no live attestation and re-attest failed: {exc}",
            )

    rec = get_organ_attestation(oid)
    if rec is None:
        return _hold("arif_bridge", f"Organ {organ} has no live attestation.")
    if rec.status in ("REVOKED", "DEGRADED_CLAIM", "DEGRADED", "UNATTESTED"):
        return _hold("arif_bridge", f"Organ {organ} status={rec.status}")
    if rec.status not in ("ALIVE", "DEGRADED_NOT_FAILED", "CONSTITUTIONAL_HOLD"):
        # Allow ALIVE family only
        if rec.status != "ALIVE":
            try:
                if is_organ_stale(oid):
                    return _hold("arif_bridge", f"Organ {organ} heartbeat stale. Re-attest.")
            except Exception:
                pass
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-boundary reclassification — F13 SOVEREIGN directive 2026-07-12T15:35Z
# ═══════════════════════════════════════════════════════════════════════════════
#
# Law: every result crossing from an organ back into arifOS via an MCP hop
# enters as evidence, never as authority. Only arif_judge may convert
# evidence into APPROVED / HOLD / VOID. The bridge's outer envelope must
# tell the truth: verdicts.action.state == "NOT_EVALUATED" (no approval
# laundering), verdicts.receipt.state == "UNSEALED" (no bridge seal),
# and a cross_boundary_result block carries protocol/source/execution_status/
# evidence_produced/provenance/action_authority=NONE/receipt_status=UNSEALED.
#
# Invariants enforced below (organ response may NOT):
#   1. increase authority
#   2. reinterpret actor identity
#   3. replace the kernel session
#   4. convert execution success into approval
#   5. emit a constitutional seal
#   6. return evidence without provenance


def _enforce_bridge_invariants(
    organ: str,
    tool_name: str,
    kernel_actor_id: str | None,
    kernel_session_id: str | None,
    response: Any,
) -> tuple[Any, list[str]]:
    """Enforce the 6 cross-boundary invariants on the organ response.

    Returns (possibly-mutated response, list of invariant claims triggered).
    The list is attached as `cross_boundary_invariants_applied` on the
    response so downstream consumers can see what was downgraded.
    """
    if not isinstance(response, dict):
        return response, []
    claims: list[str] = []
    auth_rank = {"OBSERVE_ONLY": 0, "LIMITED_MUTATE": 1, "FULL": 2, "SOVEREIGN": 3}
    verdict_strings = {"APPROVED", "SOVEREIGN", "SEALED", "SEAL"}

    # Invariant 1: authority may only reduce → force to OBSERVE_ONLY at bridge
    for key in ("authority_band", "authority", "effective_action_authority"):
        v = response.get(key)
        if isinstance(v, dict) and "level" in v:
            org_level = str(v.get("level", "")).upper()
            if org_level in auth_rank and org_level != "OBSERVE_ONLY":
                v["level"] = "OBSERVE_ONLY"
                claims.append(f"inv1:authority_downgraded:{key}.level")
        elif isinstance(v, str) and v.upper() in auth_rank and v.upper() != "OBSERVE_ONLY":
            response[key] = "OBSERVE_ONLY"
            claims.append(f"inv1:authority_downgraded:{key}")

    # Invariant 2: actor identity cannot be reinterpreted
    for key in ("actor_id", "caller_actor_id", "identity.actor_id"):
        v = response.get(key)
        if isinstance(v, str) and kernel_actor_id and v != kernel_actor_id:
            response[key] = kernel_actor_id
            claims.append(f"inv2:actor_replaced_with_kernel:{key}")

    # Invariant 3: kernel session cannot be replaced
    for key in ("session_id", "caller_session_id", "identity.session_id"):
        v = response.get(key)
        if isinstance(v, str) and kernel_session_id and v != kernel_session_id:
            response[key] = kernel_session_id
            claims.append(f"inv3:session_replaced_with_kernel:{key}")

    # Invariant 4: execution success ≠ approval
    for key in ("verdict", "verdict_code", "verdict_class", "decision", "result_class"):
        v = response.get(key)
        if isinstance(v, str) and v.upper() in verdict_strings:
            response[key] = "EVIDENCE_ONLY"
            claims.append(f"inv4:verdict_downgraded_to_evidence:{key}")

    # Invariant 5: constitutional seal forbidden at bridge
    for key in (
        "seal",
        "seal_id",
        "vault_entry_id",
        "constitutional_seal",
        "constitutional_seal_id",
    ):
        if key in response:
            response[key] = {
                "_status": "FORBIDDEN_AT_BRIDGE",
                "_original_key": key,
                "_replaced_by": "evidence_only_no_constitutional_seal_at_bridge",
            }
            claims.append(f"inv5:constitutional_seal_forbidden:{key}")

    # Invariant 6: evidence without provenance → attach degraded_claim
    if "provenance" not in response and "response" in response:
        prov = (
            response.get("response", {}).get("provenance", "")
            if isinstance(response.get("response"), dict)
            else ""
        )
        if not prov:
            claims.append("inv6:missing_provenance")

    if claims:
        existing = response.get("cross_boundary_invariants_applied")
        if not isinstance(existing, list):
            existing = []
        response["cross_boundary_invariants_applied"] = existing + claims
    return response, claims


def _bridge_ok(
    organ: str,
    tool_name: str,
    inner_result: Any,
    *,
    kernel_actor_id: str | None,
    kernel_session_id: str | None,
    boundary_enforced: bool = True,
    violations: list | None = None,
    epistemic_checked: bool = True,
    envelope_echoed: bool = True,
    drift_detected: bool = False,
    invariants_applied: list | None = None,
) -> dict[str, Any]:
    """Wrap organ result with cross-boundary reclassification per F13 law.

    Produces a base response via _ok() then OVERRIDES the verdict envelope
    to tell the truth: action = NOT_EVALUATED, receipt = UNSEALED, session
    = OBSERVE_ONLY, and a `cross_boundary_result` block carries the
    protocol/source/execution_status/provenance/action_authority schema
    specified by the F13 directive.
    """
    cross_boundary_result = {
        "protocol": "MCP",
        "source_server": organ,
        "source_tool": tool_name,
        "execution_status": "SUCCESS",
        "evidence_produced": True,
        "provenance": f"{organ.lower()}_mcp_via_bridge",
        "action_authority": "NONE",
        "receipt_status": "UNSEALED",
    }
    result_payload = {
        "organ": organ,
        "tool": tool_name,
        "result": inner_result,
        "status": "bridged",
        "boundary_enforced": boundary_enforced,
        "violations": violations or [],
        "_epistemic_checked": epistemic_checked,
        "_envelope_echoed": envelope_echoed,
        "actor_id": kernel_actor_id,
        "session_id": kernel_session_id,
        # F13 cross-boundary reclassification — visible on every bridge result
        "action_authority": "NONE",
        "cross_boundary": True,
        "bridge_organ": organ,
        "bridge_tool": tool_name,
        "bridge_session_id": kernel_session_id or "",
        "bridge_actor_id": kernel_actor_id or "",
        "cross_boundary_result": cross_boundary_result,
        "cross_boundary_invariants_applied": invariants_applied or [],
    }
    base = _ok(
        "arif_bridge",
        result_payload,
        meta={"actor_id": kernel_actor_id},
        session_id=kernel_session_id,
    )
    # ── OVERRIDE the verdict envelope to tell the truth ─────────────────
    if isinstance(base, dict) and isinstance(base.get("verdicts"), dict):
        v = base["verdicts"]
        if isinstance(v.get("action"), dict):
            v["action"]["state"] = "NOT_EVALUATED"
            v["action"]["evidence_reference"] = f"cross_boundary_evidence:{organ}:{tool_name}"
            v["action"]["issuer"] = "arif_bridge"
        if isinstance(v.get("receipt"), dict):
            v["receipt"]["state"] = "UNSEALED"
            v["receipt"]["evidence_reference"] = f"bridge_passthrough_unsealed:{organ}:{tool_name}"
            v["receipt"]["issuer"] = "arif_bridge"
        if isinstance(v.get("session"), dict):
            # Force to OBSERVE_ONLY — bridge cannot grant authority above kernel's
            v["session"]["state"] = "OBSERVE_ONLY"
            v["session"]["evidence_reference"] = (
                f"bridge_passthrough_observation:{organ}:{tool_name}"
            )
            v["session"]["issuer"] = "arif_bridge"
        base["verdicts"] = v
    # Mark in _meta for clients + leave proof on the envelope surface
    if isinstance(base, dict):
        # Cross-boundary metadata is also surfaced at the top level so
        # the client permission screen can read it without parsing the
        # `result` block. action_authority and cross_boundary markers are
        # the canonical signals per the F13 directive.
        base["action_authority"] = "NONE"
        base["cross_boundary"] = True
        base["bridge_organ"] = organ
        base["bridge_tool"] = tool_name
        base["bridge_session_id"] = kernel_session_id or ""
        base["bridge_actor_id"] = kernel_actor_id or ""
        # Bridge proof (F13 law stamp)
        base.setdefault("bridge_proof", {})
        if isinstance(base["bridge_proof"], dict):
            base["bridge_proof"].update(
                {
                    "law": "F13 cross-boundary reclassification (2026-07-12T15:35Z)",
                    "principle": "execution success is evidence of execution only; carries no action authority, no approval, no seal",
                    "organ": organ,
                    "tool": tool_name,
                    "kernel_session_id": kernel_session_id or "",
                    "kernel_actor_id": kernel_actor_id or "",
                    "drift_detected": drift_detected,
                    "invariants_applied": invariants_applied or [],
                }
            )
    return base


def _bridge_geox(
    tool_name: str,
    arguments: dict,
    session_id: str | None,
    actor_id: str | None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Bridge a call to GEOX organ. Populates and expects echo of _envelope."""
    hold = _assert_organ_attested("geox")
    if hold:
        return hold
    # ── WS9: Build federation envelope ─────────────────────────────────────
    _caller_auth = arguments.get(
        "authority_ceiling", arguments.get("authority_band", "OBSERVE_ONLY")
    )
    fed_env = build_federation_envelope(
        actor_id=actor_id,
        identity_verified=bool(actor_id and session_id),
        session_id=session_id,
        session_token=session_token or arguments.get("session_token"),
        authority=_caller_auth,
        source_tool="arif_route",
        target_organ="GEOX",
        target_tool=tool_name,
        evidence_layer="L2",
        reversibility="reversible",
        constitutional_chain_id=arguments.get("constitutional_chain_id", session_id),
        trace_id=arguments.get("trace_id"),
    )
    call_args = {k: v for k, v in (arguments or {}).items() if k != "_envelope"}
    call_args = inject_envelope_into_call_args(call_args, fed_env)
    try:
        from arifosmcp.federation.kernel_envelope import wrap_geox_output
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.geox_bridge import call_geox_tool

        result = _run_async(call_geox_tool(tool_name, call_args))
        validated = validate_organ_output("geox", result)
        wrapped = wrap_geox_output(
            validated["output"],
            tool_name=tool_name,
            session_id=session_id,
            actor_id=actor_id,
            lease_id=arguments.get("lease_id"),
        )
        # Cross-boundary reclassification
        if isinstance(wrapped, dict):
            wrapped.setdefault(
                "cross_boundary_enforcement",
                {
                    "protocol": "MCP",
                    "source_server": "GEOX",
                    "source_tool": tool_name,
                    "action_authority": "NONE",
                    "receipt_status": "UNSEALED",
                    "judge_required": True,
                    "note": "Organ result is evidence only. Only arif_judge may convert evidence into authority.",
                },
            )

        # ── WS9: Finalize response envelope ────────────────────────────────
        wrap_target = wrapped if isinstance(wrapped, dict) else result
        finalize_response_envelope(
            wrap_target,
            call_args.get("_envelope"),
            organ_status="bridged",
            provenance="geox_mcp_via_bridge",
        )

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(wrapped) if isinstance(wrapped, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: GEOX bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        # Kernel-side: envelope session_id drift detection
        call_env = call_args.get("_envelope", {})
        resp_env = wrap_target.get("_envelope_echo", {}) if isinstance(wrap_target, dict) else {}
        call_sid = (
            call_env.get("__federation_envelope", {}).get("session", {}).get("session_id")
            if isinstance(call_env, dict)
            else None
        )
        resp_sid = resp_env.get("session_id") if isinstance(resp_env, dict) else None
        if call_sid and resp_sid and call_sid != resp_sid:
            logger.warning("ENVELOPE DRIFT DETECTED in GEOX response")
            attach_degraded_claim(
                wrap_target,
                what_degraded="envelope_session_id_mismatch",
                where_degraded="GEOX_bridge_response",
                evidence_produced=True,
                result_usable=False,
                next_safe_action="investigate_identity_propagation",
            )

        # ── Cross-boundary invariant enforcement (F13 directive 2026-07-12T15:35Z) ──
        wrap_target, invariants_applied = _enforce_bridge_invariants(
            "GEOX", tool_name, actor_id, session_id, wrap_target
        )
        drift_detected = bool(call_sid and resp_sid and call_sid != resp_sid)
        return _bridge_ok(
            "GEOX",
            tool_name,
            wrap_target,
            kernel_actor_id=actor_id,
            kernel_session_id=session_id,
            boundary_enforced=validated["boundary_enforced"],
            violations=validated["violations"],
            epistemic_checked=True,
            envelope_echoed=True,
            drift_detected=drift_detected,
            invariants_applied=invariants_applied,
        )
    except Exception as e:
        degraded = build_degraded_claim(
            what_degraded=str(e),
            where_degraded="GEOX_bridge_dispatch",
            evidence_produced=False,
            result_usable=False,
            next_safe_action="check_geox_organ_health_and_retry",
        )
        return _hold("arif_bridge", f"GEOX bridge failed: {e}", extra_meta=degraded)


def _bridge_wealth(
    tool_name: str,
    arguments: dict,
    session_id: str | None,
    actor_id: str | None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Bridge a call to WEALTH organ. Echo _envelope for identity integrity."""
    hold = _assert_organ_attested("wealth")
    if hold:
        return hold
    # ── WS9: Build federation envelope ─────────────────────────────────────
    _caller_auth = arguments.get(
        "authority_ceiling", arguments.get("authority_band", "OBSERVE_ONLY")
    )
    fed_env = build_federation_envelope(
        actor_id=actor_id,
        identity_verified=bool(actor_id and session_id),
        session_id=session_id,
        session_token=session_token or arguments.get("session_token"),
        authority=_caller_auth,
        source_tool="arif_route",
        target_organ="WEALTH",
        target_tool=tool_name,
        evidence_layer="L2",
        reversibility="reversible",
        constitutional_chain_id=arguments.get("constitutional_chain_id", session_id),
        trace_id=arguments.get("trace_id"),
    )
    # Organ MCP schemas reject unknown kwargs — strip kernel envelope before call
    call_args = {k: v for k, v in (arguments or {}).items() if k != "_envelope"}
    call_args = inject_envelope_into_call_args(call_args, fed_env)
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.wealth_bridge import call_wealth_tool

        result = _run_async(call_wealth_tool(tool_name, call_args))
        validated = validate_organ_output("wealth", result)

        # Echo unchanged
        out = validated.get("output", result)

        # ── WS9: Finalize response envelope ────────────────────────────────
        finalize_response_envelope(
            out if isinstance(out, dict) else {},
            call_args.get("_envelope"),
            organ_status="bridged",
            provenance="wealth_mcp_via_bridge",
        )
        # Cross-boundary reclassification
        if isinstance(out, dict):
            out.setdefault(
                "cross_boundary_enforcement",
                {
                    "protocol": "MCP",
                    "source_server": "WEALTH",
                    "source_tool": tool_name,
                    "action_authority": "NONE",
                    "receipt_status": "UNSEALED",
                    "judge_required": True,
                    "note": "Organ result is evidence only. Only arif_judge may convert evidence into authority.",
                },
            )

        # ── F2: epistemic pass-through integrity (2026-07-09) ──────────────
        # Bridge must not return "successful" payloads that lost honesty tags.
        # Extract text-wrapped MCP content if needed.
        def _extract_wealth_payload(obj: Any) -> dict[str, Any] | None:
            if not isinstance(obj, dict):
                return None
            if obj.get("epistemic_tag") or obj.get("claim_state"):
                return obj
            # MCP content shape
            content = obj.get("content")
            if isinstance(content, list) and content:
                text = content[0].get("text") if isinstance(content[0], dict) else None
                if text:
                    try:
                        import json as _json

                        parsed = _json.loads(text)
                        if isinstance(parsed, dict):
                            return parsed
                    except Exception:
                        return None
            inner = obj.get("result")
            if isinstance(inner, dict):
                return _extract_wealth_payload(inner)
            return None

        wealth_payload = _extract_wealth_payload(out) if isinstance(out, dict) else None
        if wealth_payload is not None:
            # Stamp caller chain-of-custody (never invent caller=Arif)
            if actor_id:
                wealth_payload.setdefault("caller_actor_id", actor_id)
            if session_id:
                wealth_payload.setdefault("caller_session_id", session_id)
            wealth_payload.setdefault(
                "human_final_authority_meaning",
                "F13_SOVEREIGN_VETO_ROLE_NOT_CALLER",
            )
            # HOLD if organ honesty tags stripped (true hollow handoff)
            if not wealth_payload.get("epistemic_tag"):
                return _hold(
                    "arif_bridge",
                    "Epistemic strip detected: WEALTH payload missing epistemic_tag (F2)",
                    ["F2_TRUTH"],
                    session_id=session_id,
                )
            # Hard-stop: DRAFT / incomplete witness cannot be treated as SEAL-ready
            # Still pass payload for advisory (tunnel), but force ceiling + flags.
            _w = (
                wealth_payload.get("witness")
                if isinstance(wealth_payload.get("witness"), dict)
                else {}
            )
            _incomplete = _w.get("is_complete") is False or (
                isinstance(_w.get("missing"), list) and len(_w.get("missing") or []) > 0
            )
            _draft = str(wealth_payload.get("claim_state") or "").upper() in (
                "DRAFT",
                "SPECULATIVE",
                "ASSUMED",
            )
            if _incomplete or _draft:
                wealth_payload["governance_ceiling"] = "ADVISORY_ONLY"
                wealth_payload["execution_authorized"] = False
                wealth_payload["bridge_policy"] = "tunnel_passthrough_honest_tags"
                wealth_payload["kernel_note"] = (
                    "Witness incomplete and/or claim_state DRAFT — "
                    "kernel may OBSERVE/ADVISE only; EXECUTIVE/SEAL requires HOLD"
                )
                # Surface as degraded on the bridge response
                attach_degraded_claim(
                    out if isinstance(out, dict) else {},
                    what_degraded="witness_incomplete_or_claim_draft",
                    where_degraded="WEALTH_output_validation",
                    evidence_produced=True,
                    result_usable=True,
                    next_safe_action="evaluate_advisory_only_do_not_execute",
                )
            # Re-embed stamped payload if MCP text wrapper
            if isinstance(out, dict) and out.get("content"):
                try:
                    import json as _json

                    out = dict(out)
                    out["content"] = [
                        {
                            "type": "text",
                            "text": _json.dumps(wealth_payload, default=str),
                        }
                    ]
                    out["_epistemic_passthrough"] = True
                    out["_caller_stamped"] = True
                except Exception:
                    pass
            elif isinstance(out, dict):
                out = {
                    **out,
                    **{
                        k: wealth_payload[k]
                        for k in (
                            "caller_actor_id",
                            "caller_session_id",
                            "human_final_authority_meaning",
                            "epistemic_tag",
                        )
                        if k in wealth_payload
                    },
                }

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(out) if isinstance(out, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WEALTH bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        # Kernel check for envelope identity consistency
        call_env = call_args.get("_envelope", {})
        resp_env = out.get("_envelope_echo", {}) if isinstance(out, dict) else {}
        call_sid = (
            call_env.get("__federation_envelope", {}).get("session", {}).get("session_id")
            if isinstance(call_env, dict)
            else None
        )
        resp_sid = resp_env.get("session_id") if isinstance(resp_env, dict) else None
        if call_sid and resp_sid and call_sid != resp_sid:
            logger.warning("ENVELOPE DRIFT DETECTED in WEALTH response")
            attach_degraded_claim(
                out if isinstance(out, dict) else {},
                what_degraded="envelope_session_id_mismatch",
                where_degraded="WEALTH_bridge_response",
                evidence_produced=True,
                result_usable=False,
                next_safe_action="investigate_identity_propagation",
            )

        # ── Cross-boundary invariant enforcement (F13 directive 2026-07-12T15:35Z) ──
        out, invariants_applied_w = _enforce_bridge_invariants(
            "WEALTH", tool_name, actor_id, session_id, out
        )
        drift_detected_w = bool(call_sid and resp_sid and call_sid != resp_sid)
        return _bridge_ok(
            "WEALTH",
            tool_name,
            out,
            kernel_actor_id=actor_id,
            kernel_session_id=session_id,
            boundary_enforced=validated["boundary_enforced"],
            violations=validated["violations"],
            epistemic_checked=True,
            envelope_echoed=True,
            drift_detected=drift_detected_w,
            invariants_applied=invariants_applied_w,
        )
    except Exception as e:
        degraded = build_degraded_claim(
            what_degraded=str(e),
            where_degraded="WEALTH_bridge_dispatch",
            evidence_produced=False,
            result_usable=False,
            next_safe_action="check_wealth_organ_health_and_retry",
        )
        return _hold("arif_bridge", f"WEALTH bridge failed: {e}", extra_meta=degraded)


def _bridge_well(
    tool_name: str,
    arguments: dict,
    session_id: str | None,
    actor_id: str | None,
    session_token: str | None = None,
) -> dict[str, Any]:
    """Bridge a call to WELL organ. Echo _envelope unchanged."""
    hold = _assert_organ_attested("well")
    if hold:
        return hold
    # ── WS9: Build federation envelope ─────────────────────────────────────
    # P5 FIX (2026-07-12): propagate caller's actual authority, not hardcoded OBSERVE_ONLY.
    # The caller's authority ceiling is the constitutional limit; the organ may narrow it
    # but never escalate it.
    _caller_auth = arguments.get(
        "authority_ceiling", arguments.get("authority_band", "OBSERVE_ONLY")
    )
    fed_env = build_federation_envelope(
        actor_id=actor_id,
        identity_verified=bool(actor_id and session_id),
        session_id=session_id,
        session_token=session_token or arguments.get("session_token"),
        authority=_caller_auth,
        source_tool="arif_route",
        target_organ="WELL",
        target_tool=tool_name,
        evidence_layer="L2",
        reversibility="reversible",
        constitutional_chain_id=arguments.get("constitutional_chain_id", session_id),
        trace_id=arguments.get("trace_id"),
    )
    call_args = {k: v for k, v in (arguments or {}).items() if k != "_envelope"}
    call_args = inject_envelope_into_call_args(call_args, fed_env)
    try:
        from arifosmcp.runtime.epistemic_injector import (
            read_epistemic,
            verify_route_eligibility,
        )
        from arifosmcp.runtime.well_bridge import call_well_tool

        result = _run_async(call_well_tool(tool_name, call_args))

        # ── WS9: Finalize response envelope ────────────────────────────────
        if isinstance(result, dict):
            finalize_response_envelope(
                result,
                call_args.get("_envelope"),
                organ_status="bridged",
                provenance="well_mcp_via_bridge",
            )
            # ── CROSS-BOUNDARY RECLASSIFICATION (2026-07-12) ────────────────
            # Every organ result is EVIDENCE only. Execution success ≠ approval.
            # Only arif_judge may convert evidence into action authority.
            result.setdefault(
                "cross_boundary_enforcement",
                {
                    "protocol": "MCP",
                    "source_server": "WELL",
                    "source_tool": tool_name,
                    "action_authority": "NONE",
                    "receipt_status": "UNSEALED",
                    "judge_required": True,
                    "note": (
                        "Organ result is evidence only. "
                        "Only arif_judge (888) may convert evidence into APPROVED/HOLD/VOID. "
                        "This result carries no action authority regardless of organ response."
                    ),
                },
            )

        # ── Epistemic route gate (2026-06-21) ─────────────────────────────
        _source_epi = read_epistemic(result) if isinstance(result, dict) else None
        if _source_epi:
            _eligible, _reason = verify_route_eligibility(_source_epi, "EXECUTIVE")
            if not _eligible:
                logger.warning(
                    "EPISTEMIC ROUTE GATE: WELL bridge blocked for %s — %s",
                    tool_name,
                    _reason,
                )
                return _hold("arif_bridge", f"Epistemic route gate: {_reason}", ["F2_TRUTH"])

        # Kernel check for envelope identity consistency
        call_env = call_args.get("_envelope", {})
        resp_env = result.get("_envelope_echo", {}) if isinstance(result, dict) else {}
        call_sid = (
            call_env.get("__federation_envelope", {}).get("session", {}).get("session_id")
            if isinstance(call_env, dict)
            else None
        )
        resp_sid = resp_env.get("session_id") if isinstance(resp_env, dict) else None
        if call_sid and resp_sid and call_sid != resp_sid:
            logger.warning("ENVELOPE DRIFT DETECTED in WELL response")
            if isinstance(result, dict):
                attach_degraded_claim(
                    result,
                    what_degraded="envelope_session_id_mismatch",
                    where_degraded="WELL_bridge_response",
                    evidence_produced=True,
                    result_usable=False,
                    next_safe_action="investigate_identity_propagation",
                )

        # ── Cross-boundary invariant enforcement (F13 directive 2026-07-12T15:35Z) ──
        result, invariants_applied_well = _enforce_bridge_invariants(
            "WELL", tool_name, actor_id, session_id, result
        )
        return _bridge_ok(
            "WELL",
            tool_name,
            result,
            kernel_actor_id=actor_id,
            kernel_session_id=session_id,
            boundary_enforced=True,
            violations=[],
            epistemic_checked=True,
            envelope_echoed=True,
            drift_detected=False,
            invariants_applied=invariants_applied_well,
        )
    except Exception as e:
        degraded = build_degraded_claim(
            what_degraded=str(e),
            where_degraded="WELL_bridge_dispatch",
            evidence_produced=False,
            result_usable=False,
            next_safe_action="check_well_organ_health_and_retry",
        )
        return _hold("arif_bridge", f"WELL bridge failed: {e}", extra_meta=degraded)


def _get_prediction_health() -> dict[str, Any]:
    """Get self-model prediction health summary."""
    try:
        from arifosmcp.core.tool_self_model import get_tool_self_model

        model = get_tool_self_model()
        return model.get_prediction_summary()
    except Exception:
        return {"error": "prediction model not available"}
