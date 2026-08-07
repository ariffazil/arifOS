"""
arifOS VAULT999 Index — The Evidentiary Topology Map
════════════════════════════════════════════════════

Maps the VAULT999 witness layer — the bones of the organism.
Where Mind decides, Law authorizes, and Hands execute,
the Witness records what actually happened.

The fourth entropy type:
  arifOS   = Truth Entropy      → competing authority surfaces
  AAA      = Identity Entropy   → competing identity surfaces
  A-FORGE  = Causal Entropy     → competing execution surfaces
  VAULT999 = Attestation Entropy → competing evidence surfaces

41,389 entries in the canonical outcomes.jsonl chain.
Multiple evidence files scattered across two locations.

DITEMPA BUKAN DIBERI. Forged by 333-AGI Δ MIND.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastmcp import FastMCP

VAULT_STATS: dict[str, Any] = {
    "canonical_outcomes_count": 41389,
    "canonical_location": "/root/arifOS/VAULT999/outcomes.jsonl",
    "secondary_location": "/root/.local/share/arifos/vault999/",
    "evidence_files": [
        "outcomes.jsonl (41,389 entries — CANONICAL)",
        "SEALED_EVENTS.jsonl",
        "SEALED_EVENTS_v2.jsonl",
        "local_seals.jsonl",
        "session-seals.jsonl",
        "vault999.jsonl",
        "vault999_legacy.jsonl",
        "cooling/ (cooling receipts)",
        "seals/ (seal archives)",
        "sealed/ (chattr +a immutable)",
        "sessions/ (session seals)",
        "court/ (judicial records)",
        "forge/ (forge receipts)",
    ],
}

PLANE_MAP = [
    {
        "plane": "chain",
        "name": "Hash Chain",
        "canonical": "outcomes.jsonl",
        "entries": 41389,
        "description": "The append-only hash-chained truth ledger. Every entry carries prev_hash and chain_hash. Merkle-anchored every 100 entries. chattr +a (immutable). This is the single source of truth — all other evidence files are derived views.",
    },
    {
        "plane": "seals",
        "name": "Seals Registry",
        "canonical": "sealed/",
        "description": "Constitutional seals — immutable append records with F13 sovereign authority. Lane A (constitutional) and Lane B (session receipt). First-SEAL-wins doctrine.",
    },
    {
        "plane": "receipts",
        "name": "Receipt Store",
        "canonical": "/root/.local/share/arifos/vault999/",
        "description": "Secondary evidence store — session receipts, epoch receipts, audit receipts. Multiple JSONL files with overlapping scope. Entropy: which file has which receipt?",
    },
    {
        "plane": "session",
        "name": "Session Evidence",
        "canonical": "session-seals.jsonl",
        "description": "Per-session seal records — session_id, actor, verdict, receipt_hash. Operational continuity between sessions.",
    },
    {
        "plane": "cooling",
        "name": "Cooling Receipts",
        "canonical": "cooling/",
        "description": "Cooling ledger entries — post-seal convergence tracking. CONVERGING/DIVERGING/STABLE signals after drift detection.",
    },
    {
        "plane": "epoch",
        "name": "Epoch State",
        "canonical": "epoch_state.json",
        "description": "Federation epoch snapshots — state at sovereignty checkpoints. Enables replay and verification of organism state over time.",
    },
]

CRITICAL_FINDINGS = [
    {
        "id": "CF-VLT-01",
        "title": "Multiple evidence files — which one is canonical?",
        "severity": "HIGH",
        "description": "VAULT999 has outcomes.jsonl (canonical, 41k entries) plus SEALED_EVENTS.jsonl, SEALED_EVENTS_v2.jsonl, local_seals.jsonl, session-seals.jsonl, vault999.jsonl, vault999_legacy.jsonl. Plus /root/.local/share/arifos/vault999/ holds additional receipts. 7+ overlapping evidence stores create attestation entropy — multiple surfaces claiming to describe the same events.",
        "remediation": "outcomes.jsonl is canonical (chattr +a, hash-chained). All other files should be derived views or aliases. Deprecate duplicates after verifying content is in canonical chain.",
    },
    {
        "id": "CF-VLT-02",
        "title": "Dual evidence locations",
        "severity": "MEDIUM",
        "description": "Primary vault at /root/arifOS/VAULT999/. Secondary at /root/.local/share/arifos/vault999/. Two locations for evidence creates ambiguity about which is authoritative.",
        "remediation": "Declare primary as canonical. Secondary becomes cache/mirror. Document the relationship.",
    },
    {
        "id": "CF-VLT-03",
        "title": "Merkle anchor cadence undocumented",
        "severity": "LOW",
        "description": "outcomes.jsonl is Merkle-anchored every 100 entries. Cadence, verification procedure, and anchor storage location should be documented in the index.",
        "remediation": "Document anchor cadence in arifos://vault999-index. Add verification procedure.",
    },
]

MIGRATION_RULES = [
    "1. Delete nothing. The chain is immutable (chattr +a).",
    "2. Declare outcomes.jsonl as single source of truth.",
    "3. All other evidence files are derived views or legacy — deprecate after content verified in canonical.",
    "4. Merge /root/.local/share/arifos/vault999/ evidence into VAULT999 or document as cache.",
    "5. Document Merkle anchor cadence and verification procedure.",
]


def build_vault999_index() -> str:
    content_hash = hashlib.sha256(
        json.dumps(
            {
                "findings": [f["id"] for f in CRITICAL_FINDINGS],
                "planes": [p["plane"] for p in PLANE_MAP],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    result = {
        "_meta": {
            "resource": "arifos://vault999-index",
            "title": "arifOS VAULT999 Index — The Evidentiary Topology Map",
            "description": "Maps VAULT999 witness layer: 41,389 outcomes, 7+ evidence files, dual locations. Attestation entropy — competing evidence surfaces.",
            "forged": generated_at,
            "forged_by": "333-AGI Δ MIND",
            "content_hash": content_hash,
            "generated_at": generated_at,
            "generator": "arifOS/arifosmcp/resources/vault999_index.py::build_vault999_index",
            "is_derived": False,
            "annotations": {
                "audience": ["assistant"],
                "priority": 0.8,
                "lastModified": generated_at,
            },
        },
        "entropy": VAULT_STATS,
        "organism_complete": {
            "description": "All four planes are now mapped. The organism can see itself.",
            "planes": {
                "mind": {
                    "resource": "arifos://aaa-index",
                    "governs": "Cognition",
                    "question": "Who should think?",
                },
                "law": {
                    "resource": "arifos://index",
                    "governs": "Authority",
                    "question": "What is permitted?",
                },
                "hands": {
                    "resource": "arifos://a-forge-index",
                    "governs": "Action",
                    "question": "How does reality change?",
                },
                "witness": {
                    "resource": "arifos://vault999-index",
                    "governs": "Evidence",
                    "question": "What actually happened?",
                },
            },
        },
        "architecture": {
            "six_planes_vault999": {
                p["plane"]: {"name": p["name"], "description": p["description"]} for p in PLANE_MAP
            },
        },
        "critical_findings": CRITICAL_FINDINGS,
        "plane_map": PLANE_MAP,
        "migration_rules": MIGRATION_RULES,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)


def register_vault999_index(mcp: FastMCP) -> list[str]:
    @mcp.resource(
        "arifos://vault999-index",
        name="VAULT999 Evidentiary Topology Index",
        mime_type="application/json",
        description="Evidentiary topology map: 41,389 outcomes, 7+ evidence files, dual locations. The witness layer — what actually happened.",
    )
    def vault999_index() -> str:
        """VAULT999 Evidentiary Topology Index — the witness layer's map.

        41,389 entries in the canonical outcomes.jsonl chain.
        Multiple evidence files across dual locations.
        Attestation entropy — competing evidence surfaces.

        The fourth plane completes the organism.
        """
        return build_vault999_index()

    return ["arifos://vault999-index"]
