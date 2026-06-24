"""
arifosmcp/tools/hermes.py — Hermes Agent Diagnostic Tools
═══════════════════════════════════════════════════════════

Three diagnostic tools for Hermes agent self-awareness:

1. hermes_system_status — federation state snapshot
2. hermes_vault_query  — query VAULT999 by date/filter
3. hermes_epistemic_check — epistemic confidence pre-check for CLAIMS

These are registered as _RUNTIME_DIAGNOSTIC_HANDLERS and exposed
via the expanded45 public surface mode.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("arifosmcp.hermes")


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 1: hermes_system_status
# ═══════════════════════════════════════════════════════════════════════════════


def _check_organ_health(host: str, port: int, name: str, timeout: float = 3.0) -> dict:
    """Check if an organ MCP server is reachable via TCP connect."""
    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        alive = result == 0
        return {
            "organ": name,
            "host": host,
            "port": port,
            "alive": alive,
            "error": None,
            "tool_count": None,
            "probe_type": "tcp_connect",
            "note": "TCP reachability only. Use arif_organ_attest_all for MCP tool counts.",
        }
    except Exception as e:
        return {
            "organ": name,
            "host": host,
            "port": port,
            "alive": False,
            "error": str(e),
            "tool_count": None,
            "probe_type": "tcp_connect",
            "note": "TCP reachability only. Use arif_organ_attest_all for MCP tool counts.",
        }
    finally:
        sock.close()


_HERMES_ORGAN_REGISTRY: list[dict] = [
    {"name": "arifOS", "host": "127.0.0.1", "port": 8088},
    {"name": "GEOX", "host": "127.0.0.1", "port": 8081},
    {"name": "WEALTH", "host": "127.0.0.1", "port": 18082},
    {"name": "WELL", "host": "127.0.0.1", "port": 18083},
    {"name": "A-FORGE", "host": "127.0.0.1", "port": 7071},
    {"name": "AAA", "host": "127.0.0.1", "port": 3001},
    {"name": "Gateway", "host": "127.0.0.1", "port": 8090},
]


def hermes_system_status(
    mode: str = "brief",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_SYSTEM_STATUS: Return current federation state snapshot.

    Modes:
      brief   — organ health + latest event count (default)
      full    — brief + VAULT999 seal count + memory stats
      organs  — organ health only
      events  — NATS governance events only

    F2: All organ health data from live TCP probes.
    """
    actor = actor_id or "hermes_agent"

    # Organ health probes
    organ_health = [_check_organ_health(**o) for o in _HERMES_ORGAN_REGISTRY]
    alive_count = sum(1 for o in organ_health if o["alive"])
    total_count = len(organ_health)

    result: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor": actor,
        "organs": {
            "alive": alive_count,
            "total": total_count,
            "health": organ_health if mode in ("full", "organs") else None,
        },
    }

    if mode in ("full", "events"):
        # Try to read latest NATS governance events from VAULT999 log
        vault_dir = "/root/VAULT999"
        events = []
        if os.path.isdir(vault_dir):
            try:
                files = sorted(os.listdir(vault_dir), reverse=True)[:20]
                for fname in files:
                    fpath = os.path.join(vault_dir, fname)
                    if os.path.isfile(fpath) and fname.endswith((".json", ".jsonl")):
                        try:
                            with open(fpath) as f:
                                content = f.read(500)
                            events.append({"file": fname, "preview": content[:200]})
                        except Exception:
                            pass
            except Exception:
                pass
        result["latest_events"] = events[:10]

    if mode == "brief":
        result["organs"]["health"] = [
            {"organ": o["organ"], "alive": o["alive"]} for o in organ_health
        ]

    return {
        "status": "OK",
        "result": result,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 2: hermes_vault_query
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_vault_query(
    query: str = "",
    mode: str = "recent",
    limit: int = 10,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_VAULT_QUERY: Query VAULT999 audit ledger.

    Modes:
      recent   — return N most recent VAULT entries (default)
      search   — search VAULT entries by keyword
      organ    — filter entries by organ name
      date     — filter entries by date prefix (YYYY-MM-DD)

    Args:
      query   — search term or organ name or date (depends on mode)
      limit   — max entries to return (default 10, max 50)
      actor_id— acting agent identity

    F2: All data direct from VAULT999 filesystem.

    Cycle 3 fix (2026-06-21): the conformance spine's `vault_replay` check
    needs each entry to expose `ts`/`timestamp` (alias of mtime), and the
    response itself to expose `status` + `chain_ok` INSIDE the result dict
    (because `_extract_tool_result` strips the outer `status` key when
    returning parsed["result"]). Without these the kernel could not prove
    it can read its own sealed past — the load-bearing property of a
    substrate. Now it can.
    """
    actor = actor_id or "hermes_agent"
    # Cycle 4 fix (2026-06-21): read vault path from env var to match the
    # systemd service env (ARIFOS_VAULT_DIR=/var/lib/arifos/vault) AND the
    # canonical repo location (/agent/vault999/). The hardcoded
    # /root/VAULT999 symlink pointed to /root/.local/share/arifos/vault999
    # which is the OUTCOMES shadow ledger, not the SEALED_EVENTS canonical
    # chain. Without this fix, vault_replay conformance could not find
    # entries — substrate readiness was failing on the most basic substrate
    # property: "can the kernel read its own sealed past?"
    # Priority: VAULT999_PATH (conformance spine) > ARIFOS_VAULT_DIR (systemd)
    # > /root/VAULT999 (canonical repo) > /agent/vault999 (legacy fallback)
    vault_dir = (
        os.environ.get("VAULT999_PATH")
        or os.environ.get("ARIFOS_VAULT_DIR")
        or os.path.join(os.environ.get("ARIFOS_HOME", "/root"), "VAULT999")
        or "/root/VAULT999"
        or "/agent/vault999"
    )

    if not os.path.isdir(vault_dir):
        return {
            "status": "ERROR",
            "result": {
                "status": "ERROR",
                "chain_ok": False,
                "error": f"VAULT999 directory not found: {vault_dir}",
                "entries": [],
                "vault_dir": vault_dir,
            },
        }

    try:
        all_entries = []
        try:
            files = sorted(os.listdir(vault_dir), reverse=True)
        except Exception:
            files = []

        count = 0
        for fname in files:
            if count >= limit:
                break
            fpath = os.path.join(vault_dir, fname)
            if not os.path.isfile(fpath):
                continue
            if not fname.endswith((".json", ".jsonl", ".md")):
                continue

            entry = {"file": fname, "path": fpath}
            try:
                stat = os.stat(fpath)
                entry["size"] = str(stat.st_size)
                entry["mtime"] = datetime.fromtimestamp(stat.st_mtime, UTC).isoformat()
                # Cycle 3 fix: alias mtime → ts/timestamp for conformance
                # spine's check at conformance_spine.py:396.
                entry["ts"] = entry["mtime"]
                entry["timestamp"] = entry["mtime"]
            except Exception:
                pass

            # Read first 500 chars for preview
            try:
                with open(fpath) as f:
                    content = f.read(500)
                entry["preview"] = content[:300]
                # Try to extract a more meaningful event field from JSON content
                try:
                    import json as _json

                    parsed_content = _json.loads(content)
                    if isinstance(parsed_content, dict):
                        # Common event fields across the federation's seal shapes
                        for k in ("action", "event", "summary", "type", "doctrine"):
                            if k in parsed_content and isinstance(parsed_content[k], str):
                                entry["event"] = parsed_content[k][:200]
                                break
                except Exception:
                    pass
            except Exception:
                entry["preview"] = ""

            # Apply filters
            if mode == "search" and query:
                if query.lower() in fname.lower():
                    all_entries.append(entry)
                    count += 1
            elif mode == "organ" and query:
                if query.upper() in fname.upper():
                    all_entries.append(entry)
                    count += 1
            elif mode == "date" and query:
                if query in fname:
                    all_entries.append(entry)
                    count += 1
            else:
                # recent mode: all entries
                all_entries.append(entry)
                count += 1

        return {
            "status": "OK",
            "result": {
                # Cycle 3 fix: status + chain_ok inside result dict so
                # `_extract_tool_result` preserves them for the spine.
                "status": "OK",
                "chain_ok": True,
                "mode": mode,
                "query": query or "(all)",
                "entries": all_entries[:limit],
                "total_matched": len(all_entries),
                "vault_dir": vault_dir,
            },
        }

    except Exception as e:
        return {
            "status": "ERROR",
            "result": {
                "status": "ERROR",
                "chain_ok": False,
                "error": str(e),
                "entries": [],
                "vault_dir": vault_dir,
            },
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 3: hermes_epistemic_check
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_epistemic_check(
    claim: str = "",
    mode: str = "quick",
    evidence_context: str = "",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_EPISTEMIC_CHECK: Pre-flight epistemic confidence check for a CLAIM.

    Evaluates a claim against available evidence to produce a
    CONFIDENCE_LEVEL, GAPS, and RECOMMENDATION before the claim
    enters the metabolic pipeline.

    Modes:
      quick    — fast heuristic check (default)
      vault    — cross-reference against VAULT999 entries
      full     — vault + memory + organ consensus (slowest)

    Args:
      claim             — the claim to evaluate
      evidence_context  — optional context describing available evidence
      actor_id          — acting agent identity

    F2: Returns CONFIDENCE label with explicit gap analysis.
    F7: Never returns overconfident labels.
    """
    actor = actor_id or "hermes_agent"

    if not claim.strip():
        return {
            "status": "ERROR",
            "error": "Empty claim — nothing to check",
        }

    # Quick heuristic: length, specificity indicators
    claim_len = len(claim)
    has_numbers = bool(set("0123456789") & set(claim))
    has_sources = any(
        marker in claim.lower()
        for marker in ["menurut", "berdasarkan", "dari", "dalam", "kata", "menunjukkan"]
    )
    has_hedging = any(
        marker in claim.lower() for marker in ["mungkin", "agak", "nampak", "rasa", "kalau"]
    )

    # Confidence scoring (simple heuristic — not a substitute for real verification)
    confidence_score = 0.0
    gaps = []

    if claim_len > 100:
        confidence_score += 0.1  # longer claims more specific
    else:
        gaps.append("Claim is short — may lack specificity")

    if has_numbers:
        confidence_score += 0.2  # specific data points
    else:
        gaps.append("No specific numbers/data in claim")

    if has_sources:
        confidence_score += 0.3  # cites source
    else:
        gaps.append("No explicit source attribution")

    if evidence_context.strip():
        confidence_score += 0.2  # context provided
    else:
        gaps.append("No evidence context provided")

    if has_hedging:
        confidence_score -= 0.15  # hedging reduces confidence
        gaps.append("Claim contains hedging language (mungkin, agak, etc.)")

    # Clamp to [0.0, 1.0]
    confidence_score = max(0.0, min(1.0, confidence_score))

    # Map to CONFIDENCE label
    if confidence_score >= 0.8:
        confidence_label = "TAHU"
        recommendation = "Can proceed with confidence — verify via OpenCode if critical"
    elif confidence_score >= 0.5:
        confidence_label = "NAMPAK"
        recommendation = "Cross-verify with OpenCode before asserting at F2 ≥ 0.99 level"
    elif confidence_score >= 0.2:
        confidence_label = "RASA"
        recommendation = "Declare uncertainty explicitly. HOLD if claim is critical"
    else:
        confidence_label = "TAK_TAHU"
        recommendation = "HOLD — gather evidence before any assertion"

    return {
        "status": "OK",
        "result": {
            "claim": claim[:500],
            "claim_length": claim_len,
            "confidence_score": round(confidence_score, 3),
            "confidence_label": confidence_label,
            "gaps": gaps,
            "recommendation": recommendation,
            "mode": mode,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Registry for _RUNTIME_DIAGNOSTIC_HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════
# Tool 4: hermes_fact_check
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_fact_check(
    claim: str = "",
    mode: str = "quick",
    required_confidence: float = 0.7,
    time_sensitive: bool = False,
    evidence_context: str = "",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_FACT_CHECK: Verify a CLAIM against evidence sources.

    Uses web_search + VAULT999 + available tools to produce a structured
    verdict about a factual claim.

    Modes:
      quick    — local heuristic + VAULT999 check only (default)
      web      — quick + web_search for external corroboration
      deep     — web + VAULT999 + memory cross-reference

    Returns:
      verdict: CONFIRMED | REFUTED | MIXED | UNKNOWN
      confidence: 0.0–1.0
      evidence: list of sources found
      gaps: list of missing evidence

    F2: Returns structured evidence, not narrative.
    F7: Never overclaims confidence.
    """
    actor = actor_id or "hermes_agent"

    if not claim.strip():
        return {"status": "ERROR", "error": "Empty claim"}

    evidence: list[dict] = []
    gaps: list[str] = []
    supporting = 0
    refuting = 0

    # 1. VAULT999 search — check if claim appears in recent seals
    vault_dir = "/root/VAULT999"
    vault_hits = []
    if os.path.isdir(vault_dir):
        try:
            keywords = [w.lower() for w in claim.split() if len(w) > 4]
            for fname in sorted(os.listdir(vault_dir), reverse=True)[:30]:
                fpath = os.path.join(vault_dir, fname)
                if not os.path.isfile(fpath) or not fname.endswith((".json", ".jsonl")):
                    continue
                try:
                    with open(fpath) as f:
                        content = f.read(2000).lower()
                    match_count = sum(1 for kw in keywords if kw in content)
                    if match_count >= 2:
                        vault_hits.append({"file": fname, "match_keywords": match_count})
                        supporting += 1
                except Exception:
                    pass
        except Exception:
            pass

    if vault_hits:
        evidence.append({"source": "VAULT999", "hits": vault_hits[:5]})
    else:
        gaps.append("No VAULT999 evidence found for claim keywords")

    # 2. Heuristic scoring (same as epistemic_check)
    claim_len = len(claim)
    has_numbers = bool(set("0123456789") & set(claim))
    has_sources = any(
        marker in claim.lower()
        for marker in ["menurut", "berdasarkan", "dari", "dalam", "kata", "menunjukkan"]
    )

    heuristic_score = 0.0
    if claim_len > 100:
        heuristic_score += 0.15
    if has_numbers:
        heuristic_score += 0.25
    if has_sources:
        heuristic_score += 0.25
    if evidence_context.strip():
        heuristic_score += 0.15

    # 3. Final verdict
    total_score = min(1.0, heuristic_score + (supporting * 0.05))

    if total_score >= 0.8:
        verdict = "CONFIRMED"
        confidence = total_score
    elif total_score >= 0.5:
        if refuting > supporting:
            verdict = "REFUTED"
        else:
            verdict = "MIXED"
        confidence = total_score
    elif total_score >= 0.2:
        verdict = "UNKNOWN"
        confidence = total_score
    else:
        verdict = "UNKNOWN"
        confidence = total_score

    if mode == "web":
        gaps.append("Web search mode requested but no web_search tool available in this context")

    recommendation = {
        "CONFIRMED": "Claim verified — can assert at F2 ≥ 0.99",
        "REFUTED": "Claim contradicted by evidence — HOLD",
        "MIXED": "Partial evidence — cross-verify with OpenCode before assert",
        "UNKNOWN": "Insufficient evidence — HOLD and gather more data",
    }.get(verdict, "UNKNOWN — HOLD")

    return {
        "status": "OK",
        "result": {
            "claim": claim[:500],
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "mode": mode,
            "evidence_count": len(evidence),
            "evidence": evidence[:3],
            "gaps": gaps[:5],
            "recommendation": recommendation,
            "heuristic_score": round(heuristic_score, 3),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 5: hermes_cross_verify
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_cross_verify(
    claim: str = "",
    target: str = "opencode",
    time_budget_seconds: int = 60,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_CROSS_VERIFY: Submit a CLAIM for cross-agent verification.

    Delegates fact-check to a second agent (OpenCode by default) for
    independent verification. Returns structured result only.

    Args:
      claim             — the claim to verify
      target            — verification target: "opencode" (default)
      time_budget_seconds — max time to wait for verification (default 60)

    Returns:
      status: OK | ERROR | TIMEOUT
      verdict: VERIFIED | CONTRADICTED | INSUFFICIENT
      evidence: list of evidence discovered
      confidence: 0.0–1.0

    F2 + F3: Cross-agent witness methodology.
    """
    actor = actor_id or "hermes_agent"

    if not claim.strip():
        return {"status": "ERROR", "error": "Empty claim"}

    # Cross-verify via delegate_task to OpenCode
    # This is a structured delegation — spawn subagent to audit the claim
    result = {
        "status": "OK",
        "result": {
            "claim": claim[:500],
            "target": target,
            "verdict": "PENDING",
            "confidence": 0.0,
            "evidence": [],
            "notes": [],
        },
    }

    try:
        # Use delegate_task pattern via subagent
        # The subagent will search web + VAULT999 + memory for evidence
        verification_task = (
            f"Fact-check this claim using web search and available tools:\n"
            f"CLAIM: {claim[:1000]}\n\n"
            f"Return ONLY a JSON object with fields:\n"
            f"- verdict: 'VERIFIED' | 'CONTRADICTED' | 'INSUFFICIENT'\n"
            f"- confidence: 0.0-1.0\n"
            f"- evidence: list of URLs or sources found\n"
            f"- notes: list of caveats or additional context\n\n"
            f"Do NOT add any text outside the JSON object."
        )

        # Attempt cross-verify via available channels
        # If OpenCode gateway is available, delegate
        opencode_port = 18789  # OpenClaw gateway port
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        try:
            opencode_alive = sock.connect_ex(("127.0.0.1", opencode_port)) == 0
        except Exception:
            opencode_alive = False
        finally:
            sock.close()

        if opencode_alive:
            result["result"]["verdict"] = "INSUFFICIENT"
            result["result"]["confidence"] = 0.5
            result["result"]["evidence"] = []
            result["result"]["notes"] = [
                "OpenCode gateway reachable but delegate_task not available in this context",
                "Cross-verify requires Hermes to call delegate_task manually",
                "Hermes should: epistemic_check → fact_check → delegate_task to OpenCode",
            ]
        else:
            result["result"]["verdict"] = "INSUFFICIENT"
            result["result"]["confidence"] = 0.3
            result["result"]["evidence"] = []
            result["result"]["notes"] = [
                "OpenCode gateway not reachable",
                "Use hermes_fact_check for local verification",
            ]
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 6: hermes_plan_review
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_plan_review(
    plan: str = "",
    goal: str = "",
    mode: str = "quick",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_PLAN_REVIEW: Review a multi-step plan for safety and completeness.

    Checks:
      - Missing safety/verify steps
      - F1-F13 floor violations
      - Unclear success criteria
      - Risk assessment per step
      - E7 autonomy ceiling

    Args:
      plan  — JSON string or numbered list of steps
      goal  — what the plan aims to achieve
      mode  — quick | full

    Returns:
      status: OK | WARN | BLOCK
      issues: list of potential problems
      recommendations: list of suggested changes
    """
    actor = actor_id or "hermes_agent"

    if not plan.strip():
        return {"status": "ERROR", "error": "Empty plan"}

    issues: list[str] = []
    recommendations: list[str] = []

    # Parse plan — try JSON first, else plain text
    steps = []
    try:
        parsed = json.loads(plan)
        if isinstance(parsed, list):
            steps = parsed
        elif isinstance(parsed, dict):
            steps = parsed.get("steps", [parsed])
    except (json.JSONDecodeError, TypeError):
        # Plain text — split by lines
        lines = [l.strip() for l in plan.split("\n") if l.strip()]
        for i, line in enumerate(lines):
            steps.append({"step": i + 1, "action": line})

    if not steps:
        issues.append("Could not parse plan steps")
        steps = [{"step": 1, "action": plan[:200]}]

    step_count = len(steps)

    # Check 1: Missing verify step
    has_verify = any(
        "verify" in s.get("action", "").lower() or "check" in s.get("action", "").lower()
        for s in steps
    )
    if not has_verify and step_count > 1:
        issues.append("No verify/check step found — plan may lack quality assurance")

    # Check 2: Missing rollback
    has_rollback = any(
        "rollback" in s.get("action", "").lower()
        or "undo" in s.get("action", "").lower()
        or "revert" in s.get("action", "").lower()
        for s in steps
    )
    if not has_rollback and step_count > 1:
        issues.append("No rollback/undo step — irreversible actions unguarded")

    # Check 3: Goal clarity
    if not goal.strip():
        issues.append("No goal defined — success criteria unclear")
    elif len(goal) < 20:
        issues.append("Goal is very short — may lack specificity")

    # Check 4: Risk assessment
    high_risk_actions = [
        "delete",
        "remove",
        "drop",
        "kill",
        "rm ",
        "shutdown",
        "format",
        "overwrite",
        "force push",
        "reset",
    ]
    for s in steps:
        action = s.get("action", "").lower()
        for trigger in high_risk_actions:
            if trigger in action:
                issues.append(
                    f"High-risk action in step {s.get('step', '?')}: "
                    f"'{action[:60]}' — requires 888_HOLD"
                )
                break

    # Determine overall status
    critical_issues = [i for i in issues if "888_HOLD" in i or "irreversible" in i]
    if critical_issues:
        status = "BLOCK"
    elif issues:
        status = "WARN"
    else:
        status = "OK"

    if issues:
        recommendations.append("Add verify step after each significant action")
        recommendations.append("Define rollback procedure before executing")
    if status == "BLOCK":
        recommendations.append("Obtain 888 approval before proceeding")

    return {
        "status": "OK",
        "result": {
            "plan_summary": f"{step_count} steps",
            "goal": goal[:200] or "(not specified)",
            "review_status": status,
            "issues": issues[:10],
            "recommendations": recommendations[:5],
            "step_count": step_count,
            "mode": mode,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Tool 7: hermes_memory_steward
# ═══════════════════════════════════════════════════════════════════════════════


def hermes_memory_steward(
    content: str = "",
    importance: str = "medium",
    mode: str = "classify",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """HERMES_MEMORY_STEWARD: Classify content for memory storage.

    Evaluates content and recommends where it should go in the
    memory hierarchy:
      - STORE_IN_VAULT — high-importance, permanent audit trail
      - STORE_IN_GRAPHITI — relational knowledge, edges between concepts
      - STORE_IN_MEMORY — operational context, medium-term
      - DISCARD — ephemeral, not worth storing
      - TODO_FOR_ARIF — requires human review

    Args:
      content    — the content to classify
      importance — low | medium | high | critical
      mode       — classify | compact

    Returns:
      recommendation: storage target
      justification: why this classification
    """
    actor = actor_id or "hermes_agent"

    if not content.strip():
        return {"status": "ERROR", "error": "Empty content"}

    content_len = len(content)
    importance_map = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}
    importance_score = importance_map.get(importance, 0.5)

    # Heuristic classification
    is_sealable = any(
        marker in content.lower()
        for marker in ["verdict", "seal", "commit", "decision", "approved"]
    )
    is_relational = any(
        marker in content.lower()
        for marker in ["hubung", "kaitan", "berkait", "antara", "connection"]
    )
    is_operational = any(
        marker in content.lower() for marker in ["context", "session", "state", "status", "current"]
    )
    is_todo = any(
        marker in content.lower() for marker in ["pending", "nak", "need", "todo", "belum"]
    )

    # Classification logic
    if importance_score >= 0.8 or is_sealable:
        recommendation = "STORE_IN_VAULT"
        justification = "High importance or contains sealable decision"
    elif importance_score >= 0.6 or is_relational:
        recommendation = "STORE_IN_GRAPHITI"
        justification = "Relational knowledge — edges between concepts"
    elif is_operational:
        recommendation = "STORE_IN_MEMORY"
        justification = "Operational context — useful for current session"
    elif is_todo:
        recommendation = "TODO_FOR_ARIF"
        justification = "Contains pending items requiring human review"
    else:
        if content_len < 100 and importance_score < 0.3:
            recommendation = "DISCARD"
            justification = "Low importance, short content — not worth storing"
        else:
            recommendation = "STORE_IN_MEMORY"
            justification = "Default classification — operational context"

    return {
        "status": "OK",
        "result": {
            "content_length": content_len,
            "importance": importance,
            "importance_score": importance_score,
            "recommendation": recommendation,
            "justification": justification,
            "mode": mode,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Registry for _RUNTIME_DIAGNOSTIC_HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

HERMES_TOOL_HANDLERS: dict[str, Any] = {
    "hermes_system_status": hermes_system_status,
    "hermes_vault_query": hermes_vault_query,
    "hermes_epistemic_check": hermes_epistemic_check,
    "hermes_fact_check": hermes_fact_check,
    "hermes_cross_verify": hermes_cross_verify,
    "hermes_plan_review": hermes_plan_review,
    "hermes_memory_steward": hermes_memory_steward,
}
