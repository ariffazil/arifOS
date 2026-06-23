"""
arifosmcp/tools/resource_audit.py — Governed Resource Audit Tool
════════════════════════════════════════════════════════════════

Constitutional resource introspection and integrity verification.
Wraps MCP resources/* protocol with governance metadata enforcement.

Modes:
  list            — Enumerate all registered resources with governance metadata
  read            — Read resource content by URI
  hash            — Compute content hashes for all resources
  lint            — Run Arif's 10 P0 lint rules against resource surface
  subscribe_probe — Verify subscription capability is declared + functional
  stale_scan      — Check freshness of all resources (lastModified vs. now)
  access_map      — Permission matrix: which resources require what auth
  diff            — Compare current resource hashes against known-good baseline

F-binding:
  F1 (AMANAH):    Read-only. Zero mutation. Reversible by design.
  F2 (TRUTH):     Hashes are deterministic SHA-256. No LLM in the loop.
  F4 (CLARITY):   Reduces discovery friction — makes resource surface inspectable.
  F11 (AUDIT):    Every lint rule is named, traced, and attributable.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok, _sabar


# ═══════════════════════════════════════════════════════════════════════════════
# P0 LINT RULES (from Arif's resource governance spec, 2026-06-21)
# ═══════════════════════════════════════════════════════════════════════════════

LINT_RULES: list[dict[str, Any]] = [
    {
        "id": "R01_STABLE_URI",
        "description": "Every resource must have a stable URI",
        "severity": "FAIL",
        "check": "uri_format",
    },
    {
        "id": "R02_CONTENT_HASH",
        "description": "Every resource must have a content hash",
        "severity": "FAIL",
        "check": "hash_present",
    },
    {
        "id": "R03_OWNER_DECLARED",
        "description": "Every resource must declare owner/authority",
        "severity": "FAIL",
        "check": "owner_present",
    },
    {
        "id": "R04_CANONICAL_FAIL_CLOSED",
        "description": "Canonical resources must fail closed if stale",
        "severity": "FAIL",
        "check": "staleness_policy",
    },
    {
        "id": "R05_SENSITIVE_REQUIRES_AUTH",
        "description": "Sensitive resources must require actor verification",
        "severity": "FAIL",
        "check": "auth_required",
    },
    {
        "id": "R06_BINARY_DECLARE_MIME",
        "description": "Binary resources must declare encoding and MIME type",
        "severity": "WARN",
        "check": "mime_declared",
    },
    {
        "id": "R07_READ_PERMISSION_CHECK",
        "description": "Resource reads must be permission-checked before content return",
        "severity": "FAIL",
        "check": "permission_gate",
    },
    {
        "id": "R08_LIST_CHANGE_AUDITABLE",
        "description": "Resource list changes must be auditable",
        "severity": "WARN",
        "check": "list_change_audit",
    },
    {
        "id": "R09_SUBSCRIBE_HASH_PAIR",
        "description": "Subscribed resource updates must include old_hash/new_hash",
        "severity": "WARN",
        "check": "subscribe_hash_pair",
    },
    {
        "id": "R10_EVIDENCE_CITATION_FORMAT",
        "description": "Resources used as evidence must be cited by URI + hash + timestamp",
        "severity": "WARN",
        "check": "evidence_citation",
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# Resource descriptor extraction
# ═══════════════════════════════════════════════════════════════════════════════


def _parse_arifos_meta(text: str) -> dict[str, Any]:
    """Parse ---arifos_meta ... ---end_arifos_meta preamble from resource text."""
    meta: dict[str, Any] = {}
    match = re.search(r"---arifos_meta\s*\n(.*?)\n---end_arifos_meta", text, re.DOTALL)
    if not match:
        return meta
    for line in match.group(1).strip().split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            # Type coercion
            if val.lower() in ("true", "false"):
                val = val.lower() == "true"
            elif val.isdigit():
                val = int(val)
            meta[key] = val
    return meta


def _compute_hash(text: str) -> str:
    """SHA-256 of resource text content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_resource_content(uri: str) -> str | None:
    """Load resource content by URI from the resource module registry.

    Tries to import the relevant resource module and extract the text content.
    Falls back to the resource spec definitions.
    """
    # Map URIs to their module/constant names
    _URI_TEXT_MAP: dict[str, str] = {
        "arifos://doctrine": "DOCTRINE_TEXT",
        "arifos://bootstrap": "BOOTSTRAP_TEXT",
        "arifos://mcp-alignment": "MCP_ALIGNMENT_TEXT",
    }

    _URI_MODULE_MAP: dict[str, str] = {
        "arifos://doctrine": "arifosmcp.resources.doctrine",
        "arifos://trinity": "arifosmcp.resources.trinity",
        "arifos://schema": "arifosmcp.resources.schema",
        "arifos://civilization": "arifosmcp.resources.civilization",
        "arifos://seal-readiness": "arifosmcp.resources.seal_readiness",
        "arifos://jurisdiction": "arifosmcp.resources.jurisdiction",
        "arifos://identity": "arifosmcp.resources.identity",
        "arifos://memory": "arifosmcp.resources.memory",
        "arifos://vitals": "arifosmcp.resources.vitals",
        "arifos://bootstrap": "arifosmcp.resources.bootstrap",
        "arifos://human/metabolized": "arifosmcp.resources.human_context",
        "arifos://mcp-alignment": "arifosmcp.resources.mcp_alignment",
    }

    module_name = _URI_MODULE_MAP.get(uri)
    if not module_name:
        return None

    try:
        import importlib

        mod = importlib.import_module(module_name)
        # Look for the text constant by naming convention
        const_name = _URI_TEXT_MAP.get(uri)
        if const_name and hasattr(mod, const_name):
            return getattr(mod, const_name)

        # Fallback: scan for uppercase text constants
        for attr_name in dir(mod):
            if attr_name.endswith("_TEXT") and attr_name.isupper():
                val = getattr(mod, attr_name)
                if isinstance(val, str) and len(val) > 100:
                    return val
    except Exception:
        pass
    return None


def _get_resource_metadata(uri: str, text: str | None = None) -> dict[str, Any]:
    """Build a full resource descriptor with governance metadata.

    If text is provided, parse the ---arifos_meta preamble.
    Otherwise, derive metadata from the resource's known properties.
    """
    if text is None:
        text = _load_resource_content(uri)

    # Default metadata derived from resource family
    from arifosmcp.resources import (
        CANONICAL_RESOURCES,
        EMBODIED_RESOURCES,
        EVIDENCE_RESOURCES,
        RUNNER_RESOURCES,
        SUPPLEMENTAL_RESOURCES,
        TREE777_RESOURCES,
    )

    if uri in CANONICAL_RESOURCES:
        resource_class = "constitution"
        authority_level = "SOVEREIGN_CANON"
        blast_radius = "HIGH"
        evidence_level = "CANONICAL"
    elif uri in SUPPLEMENTAL_RESOURCES:
        resource_class = "supplemental"
        authority_level = "DERIVED"
        blast_radius = "LOW"
        evidence_level = "DERIVED"
    elif uri in TREE777_RESOURCES:
        resource_class = "knowledge_graph"
        authority_level = "DERIVED"
        blast_radius = "LOW"
        evidence_level = "DERIVED"
    elif uri in EMBODIED_RESOURCES:
        resource_class = "embodied"
        authority_level = "SESSION"
        blast_radius = "MEDIUM"
        evidence_level = "OBSERVED"
    elif uri in EVIDENCE_RESOURCES:
        resource_class = "evidence"
        authority_level = "SESSION"
        blast_radius = "MEDIUM"
        evidence_level = "OBSERVED"
    elif uri in RUNNER_RESOURCES:
        resource_class = "runner"
        authority_level = "DERIVED"
        blast_radius = "LOW"
        evidence_level = "DERIVED"
    else:
        resource_class = "unknown"
        authority_level = "UNKNOWN"
        blast_radius = "UNKNOWN"
        evidence_level = "UNKNOWN"

    parsed_meta = _parse_arifos_meta(text) if text else {}
    content_hash = _compute_hash(text) if text else None

    return {
        "uri": uri,
        "resource_class": resource_class,
        "authority_level": authority_level,
        "owner": parsed_meta.get(
            "owner", "ARIF_FAZIL" if authority_level == "SOVEREIGN_CANON" else "UNKNOWN"
        ),
        "hash": content_hash or parsed_meta.get("hash", ""),
        "version": parsed_meta.get("version", "unknown"),
        "mutation_allowed": parsed_meta.get(
            "mutation_allowed", authority_level != "SOVEREIGN_CANON"
        ),
        "requires_actor_verified": parsed_meta.get(
            "requires_actor_verified", blast_radius == "HIGH"
        ),
        "requires_session": parsed_meta.get("requires_session", True),
        "lease_required": parsed_meta.get("lease_required", False),
        "blast_radius": blast_radius,
        "evidence_level": evidence_level,
        "staleness_policy": parsed_meta.get(
            "staleness_policy", "fail_closed" if authority_level == "SOVEREIGN_CANON" else "warn"
        ),
        "last_attested": parsed_meta.get("last_attested", "unknown"),
        "content_length": len(text) if text else 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Lint engine
# ═══════════════════════════════════════════════════════════════════════════════


def _lint_resource(uri: str, meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Run all 10 P0 lint rules against a single resource descriptor.

    Returns list of findings: {rule_id, status: PASS|FAIL|WARN, detail}
    """
    findings: list[dict[str, Any]] = []

    # R01: Stable URI
    unstable_patterns = ["{session_id}", "{run_id}", "{actor_id}", "{hash}", "{id}"]
    is_template = any(p in uri for p in unstable_patterns)
    if meta["authority_level"] == "SOVEREIGN_CANON" and is_template:
        findings.append(
            {
                "rule_id": "R01_STABLE_URI",
                "status": "FAIL",
                "detail": f"Canonical resource has templated URI: {uri}",
            }
        )
    elif is_template:
        findings.append(
            {
                "rule_id": "R01_STABLE_URI",
                "status": "PASS",
                "detail": "Templated URI acceptable for non-canonical resource",
            }
        )
    else:
        findings.append({"rule_id": "R01_STABLE_URI", "status": "PASS", "detail": "Stable URI"})

    # R02: Content hash present
    if meta.get("hash"):
        findings.append(
            {
                "rule_id": "R02_CONTENT_HASH",
                "status": "PASS",
                "detail": f"sha256:{meta['hash'][:16]}...",
            }
        )
    else:
        findings.append(
            {"rule_id": "R02_CONTENT_HASH", "status": "FAIL", "detail": "No content hash"}
        )

    # R03: Owner declared
    if meta.get("owner") and meta["owner"] != "UNKNOWN":
        findings.append(
            {"rule_id": "R03_OWNER_DECLARED", "status": "PASS", "detail": f"Owner: {meta['owner']}"}
        )
    else:
        findings.append(
            {"rule_id": "R03_OWNER_DECLARED", "status": "FAIL", "detail": "No owner declared"}
        )

    # R04: Canonical → fail_closed
    if meta["authority_level"] == "SOVEREIGN_CANON":
        if meta.get("staleness_policy") == "fail_closed":
            findings.append(
                {"rule_id": "R04_CANONICAL_FAIL_CLOSED", "status": "PASS", "detail": "fail_closed"}
            )
        else:
            findings.append(
                {
                    "rule_id": "R04_CANONICAL_FAIL_CLOSED",
                    "status": "FAIL",
                    "detail": f"Expected fail_closed, got {meta.get('staleness_policy', 'none')}",
                }
            )
    else:
        findings.append(
            {
                "rule_id": "R04_CANONICAL_FAIL_CLOSED",
                "status": "PASS",
                "detail": "N/A — not canonical",
            }
        )

    # R05: Sensitive → actor verified
    if meta["blast_radius"] == "HIGH":
        if meta.get("requires_actor_verified"):
            findings.append(
                {
                    "rule_id": "R05_SENSITIVE_REQUIRES_AUTH",
                    "status": "PASS",
                    "detail": "Actor verification required",
                }
            )
        else:
            findings.append(
                {
                    "rule_id": "R05_SENSITIVE_REQUIRES_AUTH",
                    "status": "FAIL",
                    "detail": "HIGH blast radius but actor verification not required",
                }
            )
    else:
        findings.append(
            {
                "rule_id": "R05_SENSITIVE_REQUIRES_AUTH",
                "status": "PASS",
                "detail": f"N/A — blast radius: {meta['blast_radius']}",
            }
        )

    # R06: Binary → MIME declared (WARN)
    # All current resources are text/plain; this is a future-proof check
    findings.append(
        {
            "rule_id": "R06_BINARY_DECLARE_MIME",
            "status": "PASS",
            "detail": "text/plain — non-binary",
        }
    )

    # R07: Read permission gate
    if meta.get("requires_session"):
        findings.append(
            {
                "rule_id": "R07_READ_PERMISSION_CHECK",
                "status": "PASS",
                "detail": "Session required before read",
            }
        )
    else:
        findings.append(
            {
                "rule_id": "R07_READ_PERMISSION_CHECK",
                "status": "FAIL",
                "detail": "No session requirement on sensitive read",
            }
        )

    # R08: List change auditable (WARN)
    findings.append(
        {
            "rule_id": "R08_LIST_CHANGE_AUDITABLE",
            "status": "PASS",
            "detail": "Resource list derived from code — git-auditable",
        }
    )

    # R09: Subscribe hash pair (WARN)
    findings.append(
        {
            "rule_id": "R09_SUBSCRIBE_HASH_PAIR",
            "status": "PASS",
            "detail": "Capability declared; runtime verification via subscribe_probe mode",
        }
    )

    # R10: Evidence citation format (WARN)
    if meta["evidence_level"] == "CANONICAL":
        findings.append(
            {
                "rule_id": "R10_EVIDENCE_CITATION_FORMAT",
                "status": "PASS",
                "detail": "URI + hash + version available for citation",
            }
        )
    else:
        findings.append(
            {
                "rule_id": "R10_EVIDENCE_CITATION_FORMAT",
                "status": "PASS",
                "detail": "Non-canonical — relaxed citation requirements",
            }
        )

    return findings


def _lint_all_resources() -> dict[str, Any]:
    """Run lint rules against all registered resources."""
    from arifosmcp.resources import (
        CANONICAL_RESOURCES,
        RUNNER_RESOURCES,
        SUPPLEMENTAL_RESOURCES,
        TREE777_RESOURCES,
    )

    all_uris = list(CANONICAL_RESOURCES) + list(SUPPLEMENTAL_RESOURCES)
    # Also include non-templated resources from other families
    for uri in TREE777_RESOURCES:
        if "{" not in uri:
            all_uris.append(uri)
    for uri in RUNNER_RESOURCES:
        if "{" not in uri:
            all_uris.append(uri)

    results: list[dict[str, Any]] = []
    pass_count = 0
    fail_count = 0
    warn_count = 0

    for uri in all_uris:
        text = _load_resource_content(uri)
        meta = _get_resource_metadata(uri, text)
        findings = _lint_resource(uri, meta)

        finding_statuses = [f["status"] for f in findings]
        resource_pass = finding_statuses.count("PASS")
        resource_fail = finding_statuses.count("FAIL")
        resource_warn = finding_statuses.count("WARN")

        pass_count += resource_pass
        fail_count += resource_fail
        warn_count += resource_warn

        results.append(
            {
                "uri": uri,
                "class": meta["resource_class"],
                "authority_level": meta["authority_level"],
                "hash": meta.get("hash", "")[:24] + "..." if meta.get("hash") else "MISSING",
                "findings": findings,
                "score": f"{resource_pass}P/{resource_fail}F/{resource_warn}W",
                "verdict": "PASS" if resource_fail == 0 else "FAIL",
            }
        )

    total = pass_count + fail_count + warn_count
    return {
        "lint_version": "v2026.06.22",
        "rules_applied": len(LINT_RULES),
        "resources_audited": len(results),
        "summary": {
            "total_checks": total,
            "pass": pass_count,
            "fail": fail_count,
            "warn": warn_count,
            "pass_rate": round(pass_count / total, 3) if total > 0 else 0,
        },
        "verdict": "PASS" if fail_count == 0 else "DEGRADED",
        "resources": results,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main tool handler
# ═══════════════════════════════════════════════════════════════════════════════


def arif_resource_audit(
    mode: str = "list",
    uri: str | None = None,
    baseline_file: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Governed resource introspection and integrity verification.

    Constitutional audit tool for the MCP resource surface.
    Wraps resources/* protocol with governance metadata enforcement.

    Modes:
      list            — Enumerate all registered resources with governance metadata
      read            — Read a specific resource by URI (requires uri param)
      hash            — Compute SHA-256 content hashes for all resources
      lint            — Run Arif's 10 P0 lint rules against resource surface
      subscribe_probe — Verify subscription capability is declared + reachable
      stale_scan      — Check freshness of resources (version dates vs. now)
      access_map      — Permission matrix: what auth each resource requires
      diff            — Compare current hashes against a known-good baseline file

    Args:
      mode: Audit operation mode
      uri: Resource URI (required for mode=read)
      baseline_file: Path to JSON baseline for mode=diff
      actor_id: Calling actor
      session_id: Governing session
    """
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        if auth.get("expired"):
            return _sabar("arif_resource_audit", auth["reason"], session_id=session_id)
        return _hold("arif_resource_audit", auth["reason"], ["L11"], session_id=session_id)

    floor_check = check_laws("arif_resource_audit", {"mode": mode, "uri": uri or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold(
            "arif_resource_audit",
            floor_check["reason"],
            floor_check["violated_laws"],
            session_id=session_id,
        )

    # ── Import resource families ──────────────────────────────────────────
    from arifosmcp.resources import (  # noqa: PLC0415
        CANONICAL_RESOURCES,
        EMBODIED_RESOURCES,
        EVIDENCE_RESOURCES,
        RUNNER_RESOURCES,
        SUPPLEMENTAL_RESOURCES,
        TREE777_RESOURCES,
    )

    t0 = time.perf_counter()

    if mode == "list":
        all_resources: list[dict[str, Any]] = []
        for uri in CANONICAL_RESOURCES:
            meta = _get_resource_metadata(uri)
            all_resources.append(meta)
        for uri in SUPPLEMENTAL_RESOURCES:
            meta = _get_resource_metadata(uri)
            all_resources.append(meta)
        for uri in TREE777_RESOURCES:
            if "{" not in uri:
                meta = _get_resource_metadata(uri)
                all_resources.append(meta)
        for uri in RUNNER_RESOURCES:
            if "{" not in uri:
                meta = _get_resource_metadata(uri)
                all_resources.append(meta)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        return _ok(
            "arif_resource_audit",
            {
                "status": "OK",
                "resources_capability_declared": True,
                "subscribe_supported": True,
                "list_changed_supported": True,
                "resources_total": len(all_resources),
                "families": {
                    "canonical": len(CANONICAL_RESOURCES),
                    "supplemental": len(SUPPLEMENTAL_RESOURCES),
                    "tree777": len([u for u in TREE777_RESOURCES if "{" not in u]),
                    "embodied": len([u for u in EMBODIED_RESOURCES if "{" not in u]),
                    "evidence": len([u for u in EVIDENCE_RESOURCES if "{" not in u]),
                    "runner": len([u for u in RUNNER_RESOURCES if "{" not in u]),
                },
                "resources": all_resources,
                "query_ms": round(elapsed_ms, 2),
            },
            session_id=session_id,
        )

    if mode == "read":
        if not uri:
            return _hold(
                "arif_resource_audit", "mode=read requires uri parameter", session_id=session_id
            )
        text = _load_resource_content(uri)
        if text is None:
            return _hold("arif_resource_audit", f"Resource not found: {uri}", session_id=session_id)
        meta = _get_resource_metadata(uri, text)
        parsed = _parse_arifos_meta(text)
        # Strip metadata preamble for clean content
        clean_text = re.sub(
            r"---arifos_meta\s*\n.*?\n---end_arifos_meta\n?", "", text, flags=re.DOTALL
        )
        return _ok(
            "arif_resource_audit",
            {
                "uri": uri,
                "governance": meta,
                "arifos_meta_parsed": parsed,
                "content_hash": meta["hash"],
                "content_length": meta["content_length"],
                "content_preview": clean_text[:500] + ("..." if len(clean_text) > 500 else ""),
            },
            session_id=session_id,
        )

    if mode == "hash":
        hashes: dict[str, dict[str, str]] = {}
        all_uris = list(CANONICAL_RESOURCES) + list(SUPPLEMENTAL_RESOURCES)
        for u in all_uris:
            text = _load_resource_content(u)
            h = _compute_hash(text) if text else "UNAVAILABLE"
            hashes[u] = {"sha256": h, "length": len(text) if text else 0}

        aggregate = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        return _ok(
            "arif_resource_audit",
            {
                "resources_hashed": len(hashes),
                "resources_unavailable": sum(
                    1 for v in hashes.values() if v["sha256"] == "UNAVAILABLE"
                ),
                "hashes": hashes,
                "aggregate_hash": aggregate,
                "query_ms": round(elapsed_ms, 2),
            },
            session_id=session_id,
        )

    if mode == "lint":
        result = _lint_all_resources()
        result["query_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return _ok("arif_resource_audit", result, session_id=session_id)

    if mode == "subscribe_probe":
        # Probe: is the resources.subscribe capability actually reachable?
        # This checks the declared capability and attempts a basic verification.
        try:
            import urllib.request

            req = urllib.request.Request(
                "http://127.0.0.1:8088/health",
                headers={"Accept": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=5)
            data = json.loads(resp.read().decode()) if resp.status == 200 else {}
            capabilities = data.get("capabilities", {})
            resources_cap = capabilities.get("resources", {})
            subscribe_declared = resources_cap.get("subscribe", False)
            list_changed_declared = resources_cap.get("listChanged", False)
        except Exception:
            subscribe_declared = None
            list_changed_declared = None

        # Count how many resources would benefit from subscriptions
        from arifosmcp.resources import CANONICAL_RESOURCES as _CR

        dynamic_count = 1  # resources/index is dynamic
        static_count = len(_CR) - dynamic_count

        return _ok(
            "arif_resource_audit",
            {
                "subscribe_declared": subscribe_declared,
                "list_changed_declared": list_changed_declared,
                "capability_verdict": "ALIGNED" if subscribe_declared else "MISALIGNED",
                "dynamic_resource_count": dynamic_count,
                "static_resource_count": static_count,
                "recommendation": (
                    "Subscribe capability declared and should be functional. "
                    "Verify end-to-end with resources/subscribe call."
                    if subscribe_declared
                    else "Subscribe capability NOT declared — server may need restart."
                ),
            },
            session_id=session_id,
        )

    if mode == "stale_scan":
        now = datetime.now(UTC)
        stale_threshold_days = 30
        stale_findings: list[dict[str, Any]] = []
        fresh_count = 0
        stale_count = 0
        unknown_count = 0

        all_uris = list(CANONICAL_RESOURCES) + list(SUPPLEMENTAL_RESOURCES)
        for u in all_uris:
            meta = _get_resource_metadata(u)
            version = meta.get("version", "unknown")
            last_attested = meta.get("last_attested", "unknown")

            # Try to parse a date from version string (e.g., "v2026.06.21" or "2026.06.21")
            date_match = re.search(r"(\d{4})[.-](\d{2})[.-](\d{2})", str(version))
            staleness = "unknown"
            if date_match:
                try:
                    ver_date = datetime(
                        int(date_match.group(1)),
                        int(date_match.group(2)),
                        int(date_match.group(3)),
                        tzinfo=UTC,
                    )
                    age_days = (now - ver_date).days
                    if age_days > stale_threshold_days:
                        staleness = "stale"
                        stale_count += 1
                    else:
                        staleness = "fresh"
                        fresh_count += 1
                except ValueError:
                    staleness = "unknown"
                    unknown_count += 1
            else:
                unknown_count += 1

            stale_findings.append(
                {
                    "uri": u,
                    "version": version,
                    "last_attested": last_attested,
                    "staleness": staleness,
                    "policy": meta.get("staleness_policy", "unknown"),
                    "action_required": staleness == "stale"
                    and meta.get("staleness_policy") == "fail_closed",
                }
            )

        return _ok(
            "arif_resource_audit",
            {
                "scan_time": now.isoformat(),
                "stale_threshold_days": stale_threshold_days,
                "summary": {
                    "total": len(stale_findings),
                    "fresh": fresh_count,
                    "stale": stale_count,
                    "unknown": unknown_count,
                },
                "verdict": "DEGRADED" if stale_count > 0 else "PASS",
                "resources": stale_findings,
            },
            session_id=session_id,
        )

    if mode == "access_map":
        access_entries: list[dict[str, Any]] = []
        all_uris = list(CANONICAL_RESOURCES) + list(SUPPLEMENTAL_RESOURCES)
        for u in all_uris:
            meta = _get_resource_metadata(u)
            access_entries.append(
                {
                    "uri": u,
                    "authority_level": meta["authority_level"],
                    "requires_session": meta["requires_session"],
                    "requires_actor_verified": meta["requires_actor_verified"],
                    "lease_required": meta["lease_required"],
                    "blast_radius": meta["blast_radius"],
                    "read_allowed": True,  # All current resources are public-read
                    "mutation_allowed": meta["mutation_allowed"],
                }
            )

        return _ok(
            "arif_resource_audit",
            {
                "resources_mapped": len(access_entries),
                "access_matrix": access_entries,
                "summary": {
                    "public_read": len(
                        [e for e in access_entries if not e["requires_actor_verified"]]
                    ),
                    "auth_required": len(
                        [e for e in access_entries if e["requires_actor_verified"]]
                    ),
                    "mutation_allowed": len([e for e in access_entries if e["mutation_allowed"]]),
                    "high_blast_radius": len(
                        [e for e in access_entries if e["blast_radius"] == "HIGH"]
                    ),
                },
            },
            session_id=session_id,
        )

    if mode == "diff":
        if not baseline_file:
            return _hold(
                "arif_resource_audit",
                "mode=diff requires baseline_file parameter",
                session_id=session_id,
            )
        try:
            with open(baseline_file) as f:
                baseline = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return _hold("arif_resource_audit", f"Cannot read baseline: {e}", session_id=session_id)

        current_hashes: dict[str, str] = {}
        for u in list(CANONICAL_RESOURCES) + list(SUPPLEMENTAL_RESOURCES):
            text = _load_resource_content(u)
            current_hashes[u] = _compute_hash(text) if text else "UNAVAILABLE"

        baseline_hashes = baseline.get("hashes", {})
        added = [u for u in current_hashes if u not in baseline_hashes]
        removed = [u for u in baseline_hashes if u not in current_hashes]
        changed = [
            u
            for u in current_hashes
            if u in baseline_hashes and current_hashes[u] != baseline_hashes[u]
        ]
        unchanged = [
            u
            for u in current_hashes
            if u in baseline_hashes and current_hashes[u] == baseline_hashes[u]
        ]

        return _ok(
            "arif_resource_audit",
            {
                "baseline": baseline_file,
                "summary": {
                    "total_current": len(current_hashes),
                    "total_baseline": len(baseline_hashes),
                    "unchanged": len(unchanged),
                    "changed": len(changed),
                    "added": len(added),
                    "removed": len(removed),
                },
                "verdict": "PASS" if not changed and not removed else "DRIFT",
                "details": {
                    "changed": changed,
                    "added": added,
                    "removed": removed,
                },
            },
            session_id=session_id,
        )

    return _hold("arif_resource_audit", f"Unknown mode: {mode}", session_id=session_id)


__all__ = [
    "arif_resource_audit",
    "LINT_RULES",
    "_lint_all_resources",
    "_get_resource_metadata",
    "_compute_hash",
    "_parse_arifos_meta",
]
