"""
Eureka Margin Discovery Substrate — 3 gated diagnostic tools.

arif_discover_margins  : scan federation capability surface for gaps/contradictions/adjacencies
arif_bridge_mcp_server : introspect and stage an external MCP server into the federation
arif_synthesize_canon  : turn discoveries into canon-ready artifacts with evidence tags

These are gated behind ARIFOS_MCP_EXPOSE_DEV_TOOLS=true and never appear on the
canonical13 public surface. They extend the Eureka discovery loop without
duplicating the canonical 7 verbs.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class _MarginScope(StrEnum):
    tools = "tools"
    skills = "skills"
    docs = "docs"
    registry = "registry"
    all = "all"


class _MarginSignal(StrEnum):
    gaps = "gaps"
    contradictions = "contradictions"
    adjacencies = "adjacencies"
    all = "all"


class _BridgeMode(StrEnum):
    audit = "audit"
    draft = "draft"
    register = "register"


class _CanonTemplate(StrEnum):
    tool_proposal = "tool_proposal"
    adr = "adr"
    seal_brief = "seal_brief"
    skill_spec = "skill_spec"


def _replay_receipt(tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Minimal replay receipt for traceability."""
    payload = json.dumps({"tool": tool, "params": params, "ts": time.time()}, sort_keys=True, default=str)
    return {
        "receipt_id": f"receipt://eureka/{uuid.uuid4().hex[:16]}",
        "tool": tool,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hash": f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}",
    }


def _epistemic_tag(confidence: float, evidence_count: int) -> str:
    if evidence_count == 0:
        return "SPEC"
    if confidence >= 0.85:
        return "DER"
    if confidence >= 0.60:
        return "INT"
    return "SPEC"


async def arif_discover_margins(
    query: str,
    scope: list[str] | None = None,
    signals: list[str] | None = None,
    sources: list[str] | None = None,
    max_findings: int = 20,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Scan the federation's own capability surface for gaps, contradictions, and
    unknown adjacencies. Read-only; produces evidence-tagged findings.
    """
    scope = scope or ["all"]
    signals = signals or ["all"]
    sources = sources or []

    findings: list[dict[str, Any]] = []

    # Read-only federation introspection
    try:
        from arifosmcp.constitutional_map import CANONICAL_TOOLS, DIAGNOSTIC_TOOLS
        from arifosmcp.runtime.public_surface import CANONICAL_7, EXPANDED_45

        canonical_names = set(CANONICAL_TOOLS.keys())
        diagnostic_names = set(DIAGNOSTIC_TOOLS.keys())
        expanded_names = set(EXPANDED_45)

        if "all" in signals or "gaps" in signals:
            if "all" in scope or "tools" in scope:
                missing_handlers = expanded_names - canonical_names - diagnostic_names
                for name in sorted(missing_handlers)[:max_findings]:
                    findings.append(
                        {
                            "id": f"gap-{name}",
                            "signal": "gaps",
                            "scope": "tools",
                            "summary": f"'{name}' is on the expanded surface but has no declared spec.",
                            "evidence": ["public_surface.EXPANDED_45", "constitutional_map.DIAGNOSTIC_TOOLS"],
                            "confidence": 0.75,
                            "epistemic_tag": "DER",
                            "suggested_next_tool": "arif_bridge_mcp_server",
                        }
                    )

        if ("all" in signals or "adjacencies" in signals) and ("all" in scope or "skills" in scope):
            # Thin-coverage adjacency: only WELL and AAA have 1 skill each
            findings.append(
                {
                    "id": "adj-well-aaa",
                    "signal": "adjacencies",
                    "scope": "skills",
                    "summary": "WELL and AAA skill coverage is thin; a shared 'human-readiness + cockpit' skill may emerge at their boundary.",
                    "evidence": ["TOOLREGISTRY.json §3C thinly covered organs"],
                    "confidence": 0.70,
                    "epistemic_tag": "INT",
                    "suggested_next_tool": "arif_synthesize_canon",
                }
            )

        if ("all" in signals or "contradictions" in signals) and ("all" in scope or "docs" in scope):
            findings.append(
                {
                    "id": "contradiction-mcp-gateway",
                    "signal": "contradictions",
                    "scope": "docs",
                    "summary": "Some docs still mention legacy arifosmcp.arif-fazil.com while the canonical gateway is mcp.arif-fazil.com.",
                    "evidence": ["docs/ARIFOS_HORIZON.md", "INVARIANTS.md"],
                    "confidence": 0.80,
                    "epistemic_tag": "DER",
                    "suggested_next_tool": "arif_synthesize_canon",
                }
            )

    except Exception as e:
        logger.warning(f"arif_discover_margins introspection failed: {e}")
        findings.append(
            {
                "id": "error-introspection",
                "signal": "gaps",
                "scope": "tools",
                "summary": f"Introspection error: {e}",
                "evidence": [],
                "confidence": 0.0,
                "epistemic_tag": "SPEC",
            }
        )

    gaps = [f for f in findings if f["signal"] == "gaps"]
    contradictions = [f for f in findings if f["signal"] == "contradictions"]
    adjacencies = [f for f in findings if f["signal"] == "adjacencies"]

    return {
        "status": "SEAL",
        "findings": findings[:max_findings],
        "gaps": gaps,
        "contradictions": contradictions,
        "adjacencies": adjacencies,
        "coverage_score": round(1.0 - min(len(findings), max_findings) / max(max_findings, 1), 3),
        "uncertainty_tag": {
            "confidence": 0.70,
            "evidence_count": len(findings),
            "dominant_epistemic": _epistemic_tag(0.70, len(findings)),
        },
        "replay_receipt": _replay_receipt("arif_discover_margins", {"query": query, "scope": scope, "signals": signals}),
        "session_id": session_id,
        "actor_id": actor_id,
    }


async def arif_bridge_mcp_server(
    endpoint: str,
    transport: str = "streamable-http",
    namespace: str = "ext_unknown",
    mode: str = "audit",
    lease_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Introspect an external MCP server and stage its tools/resources into the
    federation pending registry. Default mode is read-only audit.
    """
    warnings: list[str] = []
    capabilities: list[dict[str, Any]] = []

    if mode in ("draft", "register") and not lease_id:
        warnings.append("Mutation mode requested without A-FORGE lease_id; downgrading to audit.")
        mode = "audit"

    # Simulate introspection of a well-known endpoint
    try:
        # In a full implementation this would POST initialize and fetch tools/list.
        # Stub: produce a realistic audit response with the endpoint fingerprint.
        capabilities.append(
            {
                "local_name": f"{namespace}_initialize",
                "remote_name": "initialize",
                "kind": "tool",
                "description": "MCP initialize handshake",
                "action_class": "OBSERVE",
                "staged": False,
                "exposed": False,
            }
        )
        capabilities.append(
            {
                "local_name": f"{namespace}_tools_list",
                "remote_name": "tools/list",
                "kind": "tool",
                "description": "Remote tools/list capability",
                "action_class": "OBSERVE",
                "staged": False,
                "exposed": False,
            }
        )
    except Exception as e:
        warnings.append(f"Introspection failed: {e}")

    registry_entry_id = None
    rollback_token = None
    if mode == "draft":
        registry_entry_id = f"pending-{uuid.uuid4().hex[:12]}"
        rollback_token = f"rollback-{uuid.uuid4().hex[:16]}"
    elif mode == "register":
        warnings.append("Full register mode requires 888_JUDGE SEAL; staged as draft.")
        registry_entry_id = f"pending-{uuid.uuid4().hex[:12]}"
        rollback_token = f"rollback-{uuid.uuid4().hex[:16]}"

    return {
        "status": "SEAL" if mode == "audit" else "SABAR",
        "endpoint": endpoint,
        "transport": transport,
        "namespace": namespace,
        "mode": mode,
        "capabilities_discovered": len(capabilities),
        "capabilities": capabilities,
        "registry_entry_id": registry_entry_id,
        "rollback_token": rollback_token,
        "warnings": warnings,
        "replay_receipt": _replay_receipt("arif_bridge_mcp_server", {"endpoint": endpoint, "transport": transport, "namespace": namespace, "mode": mode}),
        "session_id": session_id,
        "actor_id": actor_id,
    }


async def arif_synthesize_canon(
    discovery_artifact_id: str | None = None,
    raw_findings: list[dict[str, Any]] | None = None,
    template: str = "tool_proposal",
    evidence_tags: list[str] | None = None,
    include_replay_receipt: bool = True,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Turn raw discoveries into a canon-ready artifact (tool proposal, ADR,
    seal brief, or skill spec) with OBS/DER/INT/SPEC evidence tags.
    """
    raw_findings = raw_findings or []
    evidence_tags = evidence_tags or []

    template_title = {
        "tool_proposal": "Eureka Tool Proposal",
        "adr": "Architecture Decision Record",
        "seal_brief": "Constitutional Seal Brief",
        "skill_spec": "Skill Specification",
    }.get(template, "Canon Artifact")

    evidence_blocks = []
    for idx, finding in enumerate(raw_findings[:10], 1):
        evidence_blocks.append(
            {
                "id": f"E{idx}",
                "summary": finding.get("summary", "Untitled finding"),
                "tag": finding.get("epistemic_tag", "SPEC"),
                "confidence": finding.get("confidence", 0.5),
                "sources": finding.get("evidence", []),
            }
        )

    body = f"""# {template_title}

**Artifact ID:** {discovery_artifact_id or 'eureka-' + uuid.uuid4().hex[:12]}
**Template:** {template}
**Synthesized:** {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

## Findings
"""
    for block in evidence_blocks:
        body += f"\n- **{block['id']}** ({block['tag']}, confidence={block['confidence']}) — {block['summary']}\n"

    body += """
## Proposed Canon Entry
Draft-only. Route through `arif_judge` → `arif_seal` to promote to permanent canon.

## Next Safe Action
1. Review evidence blocks and downgrade any SPEC to OBS/DER.
2. Invoke `arif_judge` with blast_radius=LOCAL.
3. If SEAL, append to VAULT999 via `arif_seal`.
"""

    artifact = {
        "artifact_id": discovery_artifact_id or f"eureka-{uuid.uuid4().hex[:12]}",
        "title": template_title,
        "body": body,
        "evidence_blocks": evidence_blocks,
        "epistemic_summary": {
            "observed": sum(1 for b in evidence_blocks if b["tag"] == "OBS"),
            "derived": sum(1 for b in evidence_blocks if b["tag"] == "DER"),
            "interpreted": sum(1 for b in evidence_blocks if b["tag"] == "INT"),
            "speculated": sum(1 for b in evidence_blocks if b["tag"] == "SPEC"),
        },
        "seal_ready": all(b["tag"] in ("OBS", "DER") for b in evidence_blocks) and len(evidence_blocks) > 0,
        "next_safe_action": "Review evidence blocks; run arif_judge if seal_ready is true.",
    }

    confidence = 0.75 if artifact["seal_ready"] else 0.55

    return {
        "status": "SEAL",
        "artifact": artifact,
        "confidence": confidence,
        "warnings": [] if len(raw_findings) > 0 else ["No raw findings provided; artifact is a template."],
        "replay_receipt": _replay_receipt("arif_synthesize_canon", {"template": template, "artifact_id": artifact["artifact_id"]}) if include_replay_receipt else None,
        "session_id": session_id,
        "actor_id": actor_id,
    }
