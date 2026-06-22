"""
arifos://resources/index — Machine-Readable Resource Catalog
════════════════════════════════════════════════════════════

JSON catalog of all registered arifOS MCP resources.
Auto-generated from the live resource registry on each fetch.

Designed for:
  - MCP Registry ingestion (automated discovery)
  - CI verification (resource surface diffs)
  - Client-side caching and indexing
  - Cross-organ resource discovery

F-binding:
  F2: deterministic — derived from registered resource set
  F4: clarity — machine-readable, no ambiguity
  F11: auditable — provenance hashes where available
  F13: read-only — no mutation, no seal

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP


def _build_resource_catalog() -> dict[str, Any]:
    """Build the machine-readable resource catalog.

    Returns a JSON-serializable dict with:
      - catalog metadata (version, generated_at, protocol)
      - resource entries grouped by family
      - summary counts

    Imports are lazy (inside the function) to avoid circular imports
    with __init__.py during module loading.
    """
    from arifosmcp.resources import (  # noqa: PLC0415 — lazy to break circular import
        CANONICAL_RESOURCES,
        EMBODIED_RESOURCES,
        EVIDENCE_RESOURCES,
        RUNNER_RESOURCES,
        TREE777_RESOURCES,
    )

    entries: list[dict[str, Any]] = []

    # Canonical resources
    for uri in CANONICAL_RESOURCES:
        entries.append({
            "uri": uri,
            "family": "canonical",
            "mime_type": "text/plain",
            "dynamic": False,
            "description": _DESCRIPTIONS.get(uri, ""),
            "floors": _FLOOR_MAP.get(uri, []),
        })

    # TREE777 resources
    for uri in TREE777_RESOURCES:
        entries.append({
            "uri": uri,
            "family": "tree777",
            "mime_type": "text/plain",
            "dynamic": "{" in uri,
            "description": _DESCRIPTIONS.get(uri, "TREE777 knowledge graph resource"),
            "floors": ["F2", "F4"],
        })

    # Embodied resources
    for uri in EMBODIED_RESOURCES:
        entries.append({
            "uri": uri,
            "family": "embodied",
            "mime_type": "application/json",
            "dynamic": True,
            "description": _DESCRIPTIONS.get(uri, "Embodied system resource"),
            "floors": ["F2", "F8", "F11"],
        })

    # Evidence resources
    for uri in EVIDENCE_RESOURCES:
        entries.append({
            "uri": uri,
            "family": "evidence",
            "mime_type": "application/json",
            "dynamic": True,
            "description": _DESCRIPTIONS.get(uri, "Evidence resource"),
            "floors": ["F2", "F3"],
        })

    # Runner resources
    for uri in RUNNER_RESOURCES:
        entries.append({
            "uri": uri,
            "family": "runner",
            "mime_type": "application/json",
            "dynamic": "{" in uri,
            "description": _DESCRIPTIONS.get(uri, "Context runner resource"),
            "floors": ["F2", "F11"],
        })

    # Supplemental resources
    entries.append({
        "uri": "arifos://mcp-alignment",
        "family": "supplemental",
        "mime_type": "text/plain",
        "dynamic": False,
        "description": "MCP spec conformance matrix — protocol compliance, extensions, deprecations, client compatibility",
        "floors": ["F2", "F4", "F11"],
    })

    entries.append({
        "uri": "arifos://resources/index",
        "family": "supplemental",
        "mime_type": "application/json",
        "dynamic": False,
        "description": "Machine-readable JSON catalog of all registered arifOS MCP resources with URIs, MIME types, descriptions, and floor linkages",
        "floors": ["F2", "F4", "F11"],
    })

    return {
        "catalog_version": "v2026.06.21",
        "generated_for": "arifOS MCP — Constitutional AI Governance Kernel",
        "protocol": "MCP 2025-11-25",
        "seal": "DITEMPA BUKAN DIBERI",
        "summary": {
            "total_resources": len(entries),
            "canonical": len(CANONICAL_RESOURCES),
            "tree777": len(TREE777_RESOURCES),
            "embodied": len(EMBODIED_RESOURCES),
            "evidence": len(EVIDENCE_RESOURCES),
            "runner": len(RUNNER_RESOURCES),
            "supplemental": 2,
        },
        "resources": entries,
    }


# ── Description map (kept in sync with resource modules) ──────────────────

_DESCRIPTIONS: dict[str, str] = {
    "arifos://doctrine": "Immutable 13-floor constitution (F1–F13). All tools and agents operate within these floors.",
    "arifos://trinity": "AAA Trinity lane architecture: AGI(111) proposes, ASI(444) judges, APEX(888) authorizes, FORGE(010) executes, 999 seals.",
    "arifos://schema": "Complete canonical blueprint of the arifOS MCP surface — tools, Trinity lanes, floors, separation of powers.",
    "arifos://civilization": "Seven federation organs, three intelligence strata, constitutional boundaries, entropy responsibility model.",
    "arifos://seal-readiness": "Vault integrity report, five disambiguated seal types, seven-floor seal gate, non-seal verdicts.",
    "arifos://jurisdiction": "Five autonomy bands (GREEN→BLACK), CapabilityGrant registry, jurisdiction rules.",
    "arifos://identity": "Sovereign identity manifest bound from identity.toml. Root of accountability — all attestation chains begin here.",
    "arifos://memory": "Six-layer memory architecture: L1 ephemeral → L6 immutable (VAULT999). Memory ≠ truth without provenance.",
    "arifos://vitals": "Constitutional vitals reference — metric definitions, green/yellow/red thresholds. For LIVE values use arif_measure.",
    "arifos://bootstrap": "Complete federation knowledge-graph bootstrap context. Full world-model in one call. v2026.06.14.",
    "arifos://human/metabolized": "Metabolized sovereign context — compact human intelligence. The nutrient, not the full testimony.",
    "tree777://index": "TREE777 wiki full index — all skills, concepts, and scars in the canonical knowledge graph.",
    "runner://policy/v1": "Pinned policy of the context_runner bridge. F2 deterministic, F11 source-of-truth.",
    "runner://receipt/{run_id}": "Cached ContextRunReceipt by run_id from the context_runner bridge.",
    "arifos://tools/self-model/{view}": "Self-model introspection by view type.",
    "arifos://tools/permissions/{scope}": "Tool permissions matrix by scope.",
    "arifos://tools/composition-matrix/{format}": "Tool composition matrix by output format.",
    "arifos://witness/log/{filter}": "Witness log entries filtered by criteria.",
    "arifos://witness/stats/{period}": "Witness statistics aggregated by time period.",
    "arifos://boundaries/domain/{domain_id}": "Domain boundary definition by domain identifier.",
    "source://{hash}": "Evidence source by content hash.",
    "receipt://web/{id}": "Web evidence receipt by identifier.",
    "contrast://{id}": "Contrast evidence by identifier.",
    "void://{id}": "Void evidence by identifier.",
}

_FLOOR_MAP: dict[str, list[str]] = {
    "arifos://doctrine": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"],
    "arifos://trinity": ["F1", "F4", "F7", "F13"],
    "arifos://schema": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"],
    "arifos://civilization": ["F1", "F10"],
    "arifos://seal-readiness": ["F2", "F12"],
    "arifos://jurisdiction": ["F11", "F13"],
    "arifos://identity": ["F1", "F13"],
    "arifos://memory": ["F2", "F6", "F12"],
    "arifos://vitals": ["F8"],
    "arifos://bootstrap": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"],
    "arifos://human/metabolized": ["F1", "F6", "F9", "F13"],
}


def register_resources_index(mcp: FastMCP) -> list[str]:
    """Register arifos://resources/index — machine-readable resource catalog.

    Auto-generated from the live CANONICAL_RESOURCES, TREE777_RESOURCES,
    EMBODIED_RESOURCES, EVIDENCE_RESOURCES, and RUNNER_RESOURCES tuples.
    Always reflects current registered state — no manual sync needed.
    """

    @mcp.resource("arifos://resources/index")
    def resources_index() -> dict[str, Any]:
        """Machine-readable catalog of all registered arifOS MCP resources.

        Returns JSON with catalog metadata, resource entries grouped by
        family (canonical, tree777, embodied, evidence, runner, supplemental),
        and summary counts. Designed for MCP Registry ingestion and CI diffs.
        """
        return _build_resource_catalog()

    # ── arifos://resources/audit — Governed resource audit with hashes ──────
    @mcp.resource("arifos://resources/audit")
    def resources_audit() -> dict[str, Any]:
        """Governed resource audit — hash, authority, staleness, permissions.

        Every resource entry carries constitutional metadata:
        - sha256 content hash (where determinable)
        - authority_level: CANONICAL / STRUCTURAL / DYNAMIC / EPHEMERAL
        - owner: sovereign identity
        - mutation_allowed: whether content can change
        - staleness_policy: fail_closed / warn / none
        - requires_actor_verified: session auth needed
        - blast_radius: LOW / MEDIUM / HIGH
        - evidence_level: CANONICAL / DERIVED / OBSERVED / REFERENCE

        Designed for governance audit tools and CI pipelines.
        Returns JSON with full governance metadata per resource.
        """
        import hashlib

        # ── Canonical truth hierarchy table ──────────────────────────────────
        # Integer rank 1 (highest truth) → 7 (lowest). Machine-comparable.
        # SOVEREIGN_CANON > SEALED_VAULT > TRUSTED_REPO > OBSERVED_EXTERNAL
        # > USER_CLAIM > MODEL_INFERENCE > UNTRUSTED
        TRUTH_TABLE: dict[str, tuple[int, str, list[str]]] = {
            "CANONICAL":    (1, "SOVEREIGN_CANON",   ["user_claim", "model_inference", "untrusted_resource", "stale_resource", "observed_external"]),
            "STRUCTURAL":   (2, "SEALED_VAULT",      ["user_claim", "model_inference", "untrusted_resource", "stale_resource"]),
            "TRUSTED_REPO": (3, "TRUSTED_REPO",      ["user_claim", "model_inference", "untrusted_resource"]),
            "DYNAMIC":      (4, "OBSERVED_EXTERNAL", ["model_inference", "untrusted_resource"]),
            "USER_CLAIM":   (5, "USER_CLAIM",        ["model_inference", "untrusted_resource"]),
            "EPHEMERAL":    (6, "MODEL_INFERENCE",   ["untrusted_resource"]),
            "UNTRUSTED":    (7, "UNTRUSTED",         []),
        }

        index = _build_resource_catalog()
        audit_entries = []

        # ── Explicit truth overrides for specific URIs ────────────────────
        # Allow per-URI authority override without restructuring the family system.
        _URI_AUTHORITY_OVERRIDES: dict[str, str] = {
            "arifos://human/metabolized": "STRUCTURAL",       # SEALED_VAULT — nutrient, not canon
            "runner://policy/v1": "TRUSTED_REPO",             # git-versioned policy
            "runner://receipt/{run_id}": "TRUSTED_REPO",       # git-versioned receipts
            "tree777://index": "STRUCTURAL",                  # SEALED_VAULT — knowledge graph index
            "tree777://skills/{category}/{name}": "STRUCTURAL",
            "tree777://concepts/{name}": "STRUCTURAL",
            "tree777://scars/{name}": "STRUCTURAL",
        }

        # ── Authority-level metadata (owner, mutation, staleness, blast, evidence) ──
        _AUTHORITY_META: dict[str, tuple[str, bool, str, str, str]] = {
            "CANONICAL":     ("ARIF_FAZIL", False, "fail_closed", "HIGH",   "CANONICAL"),
            "STRUCTURAL":    ("ARIF_FAZIL", False, "fail_closed", "MEDIUM", "DERIVED"),
            "TRUSTED_REPO":  ("ARIF_FAZIL", False, "fail_closed", "MEDIUM", "DERIVED"),
            "DYNAMIC":       ("RUNTIME",    True,  "warn",        "LOW",    "OBSERVED"),
            "EPHEMERAL":     ("RUNTIME",    True,  "warn",        "LOW",    "MODEL_INFERENCE"),
            "USER_CLAIM":    ("ARIF_FAZIL", True,  "warn",        "LOW",    "USER_CLAIM"),
            "UNTRUSTED":     ("UNKNOWN",    True,  "fail_closed", "HIGH",   "UNTRUSTED"),
        }

        # ── Family → default authority mapping ──────────────────────────────
        _FAMILY_AUTHORITY: dict[str, str] = {
            "canonical":    "CANONICAL",
            "tree777":      "STRUCTURAL",
            "supplemental": "STRUCTURAL",
            "runner":       "TRUSTED_REPO",
            "evidence":     "DYNAMIC",
            "embodied":     "DYNAMIC",
        }

        seen_uris: set[str] = set()

        for entry in index["resources"]:
            uri = entry["uri"]

            # Deduplicate — same URI from multiple families (e.g. tree777://index
            # in both CANONICAL and TREE777_RESOURCES). First occurrence wins.
            if uri in seen_uris:
                continue
            seen_uris.add(uri)

            is_dynamic = entry.get("dynamic", False)
            family = entry.get("family", "unknown")

            # Resolve authority: per-URI override > family default > DYNAMIC
            authority = _URI_AUTHORITY_OVERRIDES.get(uri, _FAMILY_AUTHORITY.get(family, "DYNAMIC"))

            # Resolve metadata from authority
            owner, mutation, staleness, blast, evidence = _AUTHORITY_META.get(
                authority, ("RUNTIME", True, "warn", "LOW", "OBSERVED")
            )

            # Template URIs (containing {param}) are structurally immutable
            if is_dynamic and "{" in uri:
                mutation = False

            # Compute content hash (salted with URI + floors)
            hash_input = f"{uri}:{sorted(entry.get('floors', []))}:v2026.06.21"
            content_hash = f"sha256:{hashlib.sha256(hash_input.encode()).hexdigest()[:32]}"

            # Canonical truth table lookup — rank is an integer 1-7
            rank, truth_label, overrides = TRUTH_TABLE.get(
                authority, (99, "UNTRUSTED", [])
            )

            audit_entry = {
                "uri": uri,
                "family": family,
                "mime_type": entry.get("mime_type", "text/plain"),
                "dynamic": is_dynamic,
                "hash": content_hash,
                "authority_level": authority,
                "truth_level": truth_label,
                "truth_rank": rank,                          # INTEGER 1-7
                "overrides_when_in_conflict": overrides,
                "owner": owner,
                "mutation_allowed": mutation,
                "staleness_policy": staleness,
                "requires_actor_verified": rank <= 2,         # CANONICAL + STRUCTURAL
                "requires_session": rank <= 2,
                "blast_radius": blast,
                "evidence_level": evidence,
                "floors": entry.get("floors", []),
                "description": entry.get("description", ""),
            }
            audit_entries.append(audit_entry)

        return {
            "resource_audit_version": "v2026.06.21",
            "generated_for": "arifOS MCP — Constitutional Resource Governance",
            "protocol": "MCP 2025-11-25",
            "total_resources": len(audit_entries),
            "capabilities_declared": {
                "subscribe": True,
                "listChanged": True,
            },
            "truth_hierarchy": [
                {"rank": 1, "label": "SOVEREIGN_CANON",  "description": "immutable constitution, seals, sovereign directives"},
                {"rank": 2, "label": "SEALED_VAULT",     "description": "append-only ledger entries, signed judgments"},
                {"rank": 3, "label": "TRUSTED_REPO",     "description": "version-controlled source of truth (git)"},
                {"rank": 4, "label": "OBSERVED_EXTERNAL","description": "web evidence, real-time sensor data"},
                {"rank": 5, "label": "USER_CLAIM",       "description": "human input without verification"},
                {"rank": 6, "label": "MODEL_INFERENCE",  "description": "LLM-generated content, may hallucinate"},
                {"rank": 7, "label": "UNTRUSTED",        "description": "unverified external resource, requires quarantine"},
            ],
            "truth_hierarchy_rule": "Lower rank = higher truth. Rank 1 overrides all. Rank 7 overrides nothing.",
            "summary": {
                    "total_unique": len(audit_entries),
                    "by_truth_rank": {
                    1: sum(1 for e in audit_entries if e["truth_rank"] == 1),
                    2: sum(1 for e in audit_entries if e["truth_rank"] == 2),
                    3: sum(1 for e in audit_entries if e["truth_rank"] == 3),
                    4: sum(1 for e in audit_entries if e["truth_rank"] == 4),
                    5: sum(1 for e in audit_entries if e["truth_rank"] == 5),
                    6: sum(1 for e in audit_entries if e["truth_rank"] == 6),
                    7: sum(1 for e in audit_entries if e["truth_rank"] == 7),
                },
                "by_authority": {
                    "CANONICAL": sum(1 for e in audit_entries if e["authority_level"] == "CANONICAL"),
                    "STRUCTURAL": sum(1 for e in audit_entries if e["authority_level"] == "STRUCTURAL"),
                    "TRUSTED_REPO": sum(1 for e in audit_entries if e["authority_level"] == "TRUSTED_REPO"),
                    "DYNAMIC": sum(1 for e in audit_entries if e["authority_level"] == "DYNAMIC"),
                },
                "by_blast": {
                    "HIGH": sum(1 for e in audit_entries if e["blast_radius"] == "HIGH"),
                    "MEDIUM": sum(1 for e in audit_entries if e["blast_radius"] == "MEDIUM"),
                    "LOW": sum(1 for e in audit_entries if e["blast_radius"] == "LOW"),
                },
                "immutable": sum(1 for e in audit_entries if not e["mutation_allowed"]),
                "requires_session": sum(1 for e in audit_entries if e["requires_session"]),
            },
            "resources": audit_entries,
            "seal": "DITEMPA BUKAN DIBERI — Forged, Not Given",
        }

    return ["arifos://resources/index", "arifos://resources/audit"]


__all__ = [
    "register_resources_index",
    "_build_resource_catalog",
]
