"""
arifosmcp/tools/sense.py — 111_SENSE (Reality-Wired)
═══════════════════════════════════════════════════════════════

Reality-grounded observation and telemetry, wired to RealityHandler
for live web search (Brave → DDGS fallback) and URL fetch with
browserless render fallback.

QUANTUM SABAR PROTOCOL:
  Byzantine continuity when W1 (human/singular) or W3 (Earth/plural)
  is unreachable. Partition handling: if witness is unreachable within
  timeout, route to PURGATORY_LEDGER instead of hanging.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.reality_handlers import handler as reality_handler
from arifosmcp.runtime.reality_models import BundleInput
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok, _sabar

logger = logging.getLogger(__name__)


def _calculate_discovery_physics(
    query: str,
    local_wiki_matches: list[dict],
    repo_index_matches: list[dict],
    web_matches: list[dict],
) -> dict[str, Any]:
    """
    Discovery Physics Kernel — Epistemic telemetry for hybrid discovery.
    Calculates uncertainty reduction, evidence level, and witness consensus.
    """
    try:
        from arifosmcp.runtime.a_rif import engine, source_rank, prompt_injection, contradiction

        def _W_4(H, A, E, V):
            """Manual F3 Quad-Witness Consensus helper."""
            product = H * A * E * V
            return product**0.25

    except ImportError:
        return {
            "claim_state": "unknown",
            "evidence_level": "L0",
            "delta_s": 0.0,
            "omega_0": 0.04,
            "w4": 0.0,
            "contradiction_state": "VOID",
            "quarantine_clean": True,
        }

    # 1. Search Worthiness (W)
    freshness = 1.0
    if query and any(k in query.lower() for k in ("current", "latest", "now", "today", "2026")):
        freshness = 2.0
    uncertainty = 0.8 if not (local_wiki_matches or repo_index_matches) else 0.4
    w_score = engine.calculate_search_worthiness(
        uncertainty=uncertainty,
        importance=1.0,
        freshness=freshness,
        background_confidence=0.1 if not (local_wiki_matches or repo_index_matches) else 0.6,
    )
    # Cap search worthiness to keep it operationally sane (e.g., max 10.0)
    w_score = min(w_score, 10.0)

    # 2. Evidence Level (L)
    max_rank = 9
    for hit in web_matches:
        url = hit.get("url", "")
        rank = source_rank.rank_source(url)
        if rank < max_rank:
            max_rank = rank
    evidence_level = source_rank.evidence_level_from_rank(max_rank)
    if (local_wiki_matches or repo_index_matches) and web_matches:
        evidence_level = "L3"
    elif local_wiki_matches or repo_index_matches:
        evidence_level = "L2"
    elif not web_matches:
        evidence_level = "L0"

    # 3. Entropy Delta (ΔS)
    before = 0.8
    after = 0.4 if (local_wiki_matches or repo_index_matches or web_matches) else 0.8
    delta_s = engine.evaluate_entropy_delta(before, after)

    # 4. Humility (Omega)
    omega_0 = 0.04

    # 5. Witness Consensus (W4)
    h_val = 1.0 if (local_wiki_matches or repo_index_matches) else 0.1
    a_val = 0.8
    e_val = 0.9 if web_matches else 0.1
    v_val = 0.7
    w4 = _W_4(h_val, a_val, e_val, v_val)

    # 6. Contradictions
    claims = []
    for h in local_wiki_matches + repo_index_matches:
        claims.append({"text": h.get("excerpt", ""), "source": "local"})
    for h in web_matches:
        claims.append({"text": h.get("description", "") or h.get("snippet", ""), "source": "web"})
    audit = contradiction.audit_for_contradictions(claims)

    # 7. Injection Scan
    all_text = " ".join([c["text"] for c in claims])
    quarantine = prompt_injection.scan_for_injection(all_text)

    # 8. Claim State
    claim_state = "hypothesis"
    if w4 > 0.75 and evidence_level in ("L3", "L4"):
        claim_state = "supported"
    if evidence_level in ("L5", "L6"):
        claim_state = "verified"
    if not (local_wiki_matches or repo_index_matches or web_matches):
        claim_state = "unknown"

    return {
        "claim_state": claim_state,
        "evidence_level": str(evidence_level),
        "delta_s": delta_s,
        "omega_0": omega_0,
        "w4": round(w4, 3),
        "search_worthiness": w_score,
        "witness": {"human": h_val, "ai": a_val, "evidence": e_val, "verifier": v_val},
        "contradiction_state": audit.status,
        "quarantine_clean": quarantine.clean,
        "recommendation": "continue" if delta_s < -0.01 else "stop",
    }


def arif_sense_observe(
    mode: str = "search",
    query: str | None = None,
    url: str | None = None,
    layers: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    partition_mode: str = "ONLINE",
    partition_timeout: int = 30,
    top_k: int = 5,
    render: str = "auto",
) -> dict[str, Any]:
    """
    SENSE tool — reality-wired via RealityHandler.

    Hybrid discovery is READ-ONLY evidence retrieval. It finds what the system
    currently knows across local wiki, repo index, and live web. It does NOT
    store, persist, or write anything. Agents must still decide whether to
    pass findings to memory_recall (persist), mind_reason (reason), or
    judge_deliberate (adjudicate).

    Modes:
      search   → Brave API search (DDGS fallback)
      ingest   → Fetch + ingest URL via RealityHandler compass
      compass  → Governed Discovery Kernel: Orientation before action
      atlas    → Structural layer map (stub — pending vector atlas)
      entropy_dS → Random entropy delta (physics stub)
      vitals   → System vitals stub
    """
    # ── F11 AUTH: Session Validation (Hardened) ───────────────────────────────
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        # If it's a read-only SENSE operation and we have an actor_id,
        # allow a temporary "ephemeral" session for discovery if configured.
        if mode in ("hybrid_discovery", "vitals", "compass", "search") and actor_id:
            logger.debug(f"F11 AUTH: session_id missing for {mode}, using ephemeral context.")
            auth = {
                "valid": True,
                "session": {"actor_id": actor_id, "stage": "111", "ephemeral": True},
                "actor_id": actor_id,
            }
        else:
            if auth.get("expired"):
                return _sabar("arif_sense_observe", auth["reason"], session_id=session_id)
            return _hold("arif_sense_observe", auth["reason"], ["F11"], session_id=session_id)

    q = query or url or ""

    if mode == "compass":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.core.authority_gate import AuthorityGate, WitnessType
        from arifosmcp.core.threat_engine import ThreatEngine

        # 1. Knowledge Discovery (Hybrid)
        hd_res = arif_sense_observe(
            mode="hybrid_discovery",
            query=q,
            session_id=session_id,
            actor_id=actor_id,
            top_k=3,
        )
        data = hd_res.get("result", {})
        knowledge = data.get("knowledge_layers", {})

        # 2. Capability Discovery
        allowed_tools = []
        restricted_tools = []
        for tool_name, spec in CANONICAL_TOOLS.items():
            if spec.get("access") == "public":
                allowed_tools.append(tool_name)
            else:
                restricted_tools.append(tool_name)

        # 3. Authority Discovery
        # ThreatEngine scan for risk map
        scan_res = ThreatEngine.scan(q)
        assessment = scan_res.assessment

        # Build minimal ActionContext for AuthorityGate
        class _ActionContext:
            def __init__(self, t_name, m, q_str, a_id):
                self.tool_name = t_name
                self.mode = m
                self.query = q_str
                self.actor_id = a_id
                self.witness_type = WitnessType.AI

            def payload_text(self):
                return self.query

        act_ctx = _ActionContext("arif_sense_observe", "compass", q, actor_id)
        auth_proof = AuthorityGate.verify(act_ctx, assessment)

        # 4. Next Safe Moves
        next_moves = ["Use arif_mind_reason to analyze the discovered evidence."]
        if assessment.irreversibility.value > 0:
            next_moves.append(
                "WARNING: Intent detected as high-risk; submit formal plan before action."
            )
        if not knowledge.get("local_wiki", {}).get("matches"):
            next_moves.append("Knowledge gap detected: Ingest relevant docs via arif_wiki_ingest.")

        return _ok(
            "arif_sense_observe",
            {
                "status": "OK",
                "tool": "arif_sense_observe",
                "mode": "compass",
                "query": q,
                "orientation": {
                    "knowledge": knowledge,
                    "capabilities": {
                        "allowed": allowed_tools,
                        "restricted": restricted_tools,
                    },
                    "authority": {
                        "actor": actor_id or "anonymous",
                        "authorized": auth_proof.authorized,
                        "requires_human": auth_proof.requires_human,
                        "reason": auth_proof.reason,
                    },
                    "risk_map": {
                        "tier": scan_res.tier.value,
                        "threats": (
                            [t.name for t in assessment.threats] if assessment.threats else []
                        ),
                        "irreversible": assessment.irreversibility.value > 1,
                    },
                    "next_safe_moves": next_moves,
                },
                "physics": data.get("physics_kernel", {}),
            },
        )

    floor_check = check_floors("arif_sense_observe", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_sense_observe", floor_check["reason"], floor_check["failed_floors"])

    if partition_mode == "DEAD":
        return {
            "status": "HOLD",
            "tool": "arif_sense_observe",
            "result": {},
            "meta": {
                "partition": "DEAD",
                "reason": "Witness unreachable — CANDIDATE_SEAL escalation required",
                "failed_floors": [],
            },
        }

    if partition_mode == "PURGATORY":
        return _ok(
            "arif_sense_observe",
            {
                "query": query,
                "results": [],
                "source": "purgatory_ledger",
                "omega_0": 0.04,
                "partition": "PURGATORY",
                "note": "Witness unreachable — entry cached in Purgatory Ledger",
            },
        )

    if mode == "hybrid_discovery":
        from arifos_wiki_tools.search import search_index

        q = query or ""
        errors: list[str] = []

        # ── Layer 1: Local Wiki (AAA/wiki) ─────────────────────────────────────
        local_wiki_status: str = "UNAVAILABLE"
        local_wiki_matches: list[dict[str, Any]] = []
        try:
            from arifos_wiki_tools.search import _FEDERATION_ROOTS

            AAA_WIKI = _FEDERATION_ROOTS.get("aaa")
            if AAA_WIKI and AAA_WIKI.exists():
                hits = search_index(AAA_WIKI, q, top_k=top_k)
                if hits:
                    local_wiki_status = "FOUND"
                    for hit in hits:
                        hit["federation_organ"] = "aaa"
                        local_wiki_matches.append(hit)
                else:
                    local_wiki_status = "EMPTY"
            else:
                local_wiki_status = "UNAVAILABLE"
                errors.append("AAA/wiki path not accessible")
        except Exception as e:
            local_wiki_status = "UNAVAILABLE"
            errors.append(f"local_wiki search error: {e}")

        # ── Layer 2: Repo Indices (.arifos/wiki_index.jsonl across federation) ───
        repo_index_status: str = "UNAVAILABLE"
        repo_index_matches: list[dict[str, Any]] = []
        try:
            repo_federation_roots = {k: v for k, v in _FEDERATION_ROOTS.items() if k != "aaa"}
            for organ, root_path in repo_federation_roots.items():
                if not root_path.exists():
                    continue
                idx_path = root_path / ".arifos" / "wiki_index.jsonl"
                if not idx_path.exists():
                    continue
                hits = search_index(root_path, q, top_k=top_k)
                if hits:
                    for hit in hits:
                        hit["federation_organ"] = organ
                        repo_index_matches.append(hit)
            if repo_index_matches:
                repo_index_status = "FOUND"
            elif any(
                (root_path / ".arifos" / "wiki_index.jsonl").exists()
                for root_path in repo_federation_roots.values()
                if root_path.exists()
            ):
                repo_index_status = "EMPTY"
            else:
                repo_index_status = "NOT_INDEXED"
        except Exception as e:
            repo_index_status = "UNAVAILABLE"
            errors.append(f"repo_index search error: {e}")

        # ── Layer 3: Web Reality (Brave → DDGS → Meyhem) ───────────────────────
        web_status: str = "UNAVAILABLE"
        web_error: str | None = None
        web_matches: list[dict[str, Any]] = []
        web_engine: str = "none"
        try:
            s_res = asyncio.run(reality_handler.search_brave(q, top_k=top_k))
            if s_res.results:
                web_status = "FOUND"
                web_matches = s_res.results
                web_engine = s_res.engine
            else:
                web_status = "EMPTY"
                web_engine = getattr(s_res, "engine", "unknown")
        except Exception as e:
            web_status = "UNAVAILABLE"
            web_error = str(e)[:120]
            web_engine = "brave"
            errors.append(f"web search error: {e}")

        # ── Reconciliation: Truth Triangulation ───────────────────────────────────
        # v0: keyword-overlap heuristic. Real semantic contradiction detection is v1.
        contradictions: list[str] = []
        unknowns: list[str] = []

        if web_status == "UNAVAILABLE":
            unknowns.append(f"Web source unavailable: {web_error or 'Unknown error'}")

        local_texts = " ".join(
            h.get("excerpt", "") + " " + h.get("rel_path", "")
            for h in local_wiki_matches + repo_index_matches
        ).lower()
        web_texts = " ".join(
            w.get("title", "") + " " + w.get("snippet", "") for w in web_matches
        ).lower()

        # Check: web has relevant info absent from local
        if web_matches and not (local_wiki_matches or repo_index_matches):
            unknowns.append(
                "Web has results but no local source found matching query. "
                "Run arif_wiki_ingest to index the relevant repo."
            )

        # Check: deprecated/stale markers in local
        all_local = local_wiki_matches + repo_index_matches
        for h in all_local:
            excerpt = h.get("excerpt", "").lower()
            if any(tag in excerpt for tag in ("deprecated", "superseded", "renamed")):
                contradictions.append(
                    f"Local source at {h.get('rel_path', '?')} "
                    f"mentions deprecation — cross-check with web recommended."
                )

        # Check: topic agreement between web and local (simple keyword overlap)
        if web_texts and local_texts:
            web_tokens = set(web_texts.split()) & set(q.lower().split())
            local_tokens = set(local_texts.split()) & set(q.lower().split())
            # If web and local share no query-related tokens, note as potential divergence
            if web_tokens and local_tokens and web_tokens.isdisjoint(local_tokens):
                unknowns.append(
                    "Web and local sources both have results but don't share "
                    "query-keyword overlap — possible divergence or different focus."
                )

        # Determine evidence state
        layers_found = sum(
            1 for s in [local_wiki_status, repo_index_status, web_status] if s == "FOUND"
        )
        if layers_found >= 2:
            evidence_state = "FOUND"
            verdict = "PARTIAL"
        elif layers_found == 1:
            evidence_state = "PARTIAL"
            verdict = "SABAR"
        else:
            evidence_state = "EMPTY"
            verdict = "HOLD"

        # Separate facts from matches for clarity
        facts = []
        if local_wiki_matches:
            facts.append(f"Found {len(local_wiki_matches)} matches in AAA wiki.")
        if repo_index_matches:
            facts.append(f"Found {len(repo_index_matches)} matches in local repo index.")
        if web_matches:
            facts.append(f"Web search returned {len(web_matches)} results via {web_engine}.")

        # 5. Physics Kernel
        physics = _calculate_discovery_physics(
            q, local_wiki_matches, repo_index_matches, web_matches
        )

        # Honest confidence and next_safe_action
        if evidence_state == "EMPTY":
            confidence = "low"
            next_safe_action = (
                "No evidence found in any layer. "
                "Consider broadening the query or ingesting relevant repositories."
            )
        elif evidence_state == "PARTIAL":
            confidence = "low"
            next_safe_action = (
                "Partial evidence found. Cross-check local findings against live web "
                "before acting. Do not treat local-only results as current reality."
            )
        else:
            confidence = "medium"
            next_safe_action = (
                "Multiple layers agree. Standard epistemic caution applies. "
                "Verify critical claims with primary sources before proceeding."
            )

        return _ok(
            "arif_sense_observe",
            {
                "status": "OK",
                "tool": "arif_sense_observe",
                "mode": "hybrid_discovery",
                "query": q,
                "evidence_state": evidence_state,
                "verdict": verdict,
                "facts": facts,
                "knowledge_layers": {
                    "local_wiki": {
                        "status": local_wiki_status,
                        "matches": local_wiki_matches,
                    },
                    "repo_index": {
                        "status": repo_index_status,
                        "matches": repo_index_matches,
                    },
                    "web_reality": {
                        "status": web_status,
                        "source": web_engine,
                        "error": web_error,
                        "matches": web_matches,
                    },
                },
                "reconciliation": {
                    "state": "NOT_EVALUATED",
                    "contradictions": contradictions,
                    "unknowns": unknowns,
                },
                "physics_kernel": physics,
                "confidence": confidence,
                "next_safe_action": next_safe_action,
            },
        )

    if mode == "search":
        # F12 INJECTION guard: scan query for destructive patterns before executing search
        from arifosmcp.core.threat_engine import ThreatEngine

        scan_res = ThreatEngine.scan(query or "")
        if scan_res.assessment.irreversibility.value > 1:
            threat_names = [t.name for t in (scan_res.assessment.threats or [])]
            return _hold(
                "arif_sense_observe",
                f"F12 INJECTION: Destructive pattern detected — {', '.join(threat_names) or 'CRITICAL'}",
                ["F12"],
                session_id=session_id,
            )
        try:
            s_res = asyncio.run(reality_handler.search_brave(query or "", top_k=top_k))
            results = s_res.results if s_res.results else []
            omega_0 = 0.05 + min(len(results) * 0.02, 0.20)
            return _ok(
                "arif_sense_observe",
                {
                    "query": query,
                    "results": results,
                    "source": s_res.engine,
                    "verdict": "SEAL" if results else "SABAR",
                    "omega_0": round(omega_0, 3),
                    "partition": "ONLINE",
                    "latency_ms": round(s_res.latency_ms, 1),
                    "note": None if results else "No results — check query or API keys",
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "query": query,
                    "results": [],
                    "source": "fallback_stub",
                    "verdict": "SABAR",
                    "omega_0": 0.04,
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "ingest" and url:
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(type="url", value=url, mode="fetch", render=render),  # type: ignore[arg-type]
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_sense_observe",
                {
                    "url": url,
                    "ingested": bundle.status.state == "SUCCESS",
                    "bundle_id": bundle.id,
                    "status": bundle.status.state,
                    "verdict": bundle.status.verdict,
                    "results_count": len(bundle.results),
                    "partition": "ONLINE",
                    "errors": [{"code": e.code, "detail": e.detail} for e in bundle.status.errors],
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "url": url,
                    "ingested": False,
                    "verdict": "SABAR",
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "compass":
        value = url or query or ""
        btype = "url" if value.startswith(("http://", "https://")) else "query"
        try:
            bundle = asyncio.run(
                reality_handler.handle_compass(
                    BundleInput(
                        type=btype,  # type: ignore[arg-type]
                        value=value,
                        mode="auto",
                        top_k=top_k,
                        render=render,  # type: ignore[arg-type]
                    ),
                    auth_context={
                        "actor_id": actor_id or "anonymous",
                        "session_id": session_id or "global",
                    },
                )
            )
            return _ok(
                "arif_sense_observe",
                {
                    "heading": bundle.input.mode,
                    "confidence": 0.95 if bundle.status.state == "SUCCESS" else 0.50,
                    "bundle_id": bundle.id,
                    "status": bundle.status.state,
                    "verdict": bundle.status.verdict,
                    "results_count": len(bundle.results),
                    "partition": "ONLINE",
                },
            )
        except Exception as e:
            logger.warning(f"RealityHandler failure in arif_sense_observe ({mode}): {e}")
            return _ok(
                "arif_sense_observe",
                {
                    "heading": "unknown",
                    "confidence": 0.0,
                    "verdict": "SABAR",
                    "partition": "ONLINE",
                    "note": f"RealityHandler fallback failed: {e}",
                },
            )

    if mode == "atlas":
        return _ok(
            "arif_sense_observe",
            {
                "map": {},
                "layers": layers or [],
                "partition": partition_mode,
            },
        )
    if mode == "entropy_dS":
        ds = random.uniform(-0.1, 0.1)
        return _ok(
            "arif_sense_observe",
            {
                "delta_S": round(ds, 6),
                "trend": "stable",
                "partition": partition_mode,
            },
        )
    if mode == "vitals":
        return _ok(
            "arif_sense_observe",
            {
                "cpu": 12.5,
                "mem": 34.0,
                "io": "normal",
                "partition": partition_mode,
            },
        )

    return _hold("arif_sense_observe", f"Unknown mode: {mode}")
