"""
arifOS MCP Resource Registry
Exposes constitutional floors, VAULT ledger, and session state as MCP Resources.

MCP Resources are application-driven contextual data (spec 2025-11-25).
Unlike tools (model-controlled), resources provide read-only data for context.

v55.1: Initial resource registry with floor definitions and VAULT ledger.

DITEMPA BUKAN DIBERI
"""

import json
import os
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTITUTIONAL FLOOR DEFINITIONS (Static Resource Data)
# =============================================================================

FLOOR_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "F1": {
        "name": "Amanah",
        "full_name": "Sacred Trust",
        "threshold": "Reversible=true",
        "type": "Hard",
        "description": "All actions must be reversible. No silent mutations.",
        "formula": "R(action) >= 0.95",
        "engine": "ASI (Omega)",
        "violation_verdict": "VOID",
    },
    "F2": {
        "name": "Truth",
        "full_name": "Truth Confidence",
        "threshold": "tau >= 0.99",
        "type": "Hard",
        "description": "Claims require 99% confidence with source verification.",
        "formula": "tau = precision_weighted_confidence",
        "engine": "AGI (Delta)",
        "violation_verdict": "VOID",
    },
    "F3": {
        "name": "Tri-Witness",
        "full_name": "Triple Consensus",
        "threshold": "W3 >= 0.95",
        "type": "Soft",
        "description": "Human, AI, and Earth perspectives must agree.",
        "formula": "W3 = cbrt(Human * AI * Earth)",
        "engine": "APEX (Psi)",
        "violation_verdict": "SABAR",
    },
    "F4": {
        "name": "Clarity",
        "full_name": "Entropy Reduction",
        "threshold": "delta_S <= 0",
        "type": "Hard",
        "description": "Output must reduce confusion, not increase it.",
        "formula": "delta_S = S_output - S_input <= 0",
        "engine": "AGI (Delta)",
        "violation_verdict": "VOID",
    },
    "F5": {
        "name": "Peace²",
        "full_name": "Non-Destructive Harmony",
        "threshold": "Peace² >= 1.0",
        "type": "Hard",
        "description": "Internal system peace times external user peace.",
        "formula": "Peace² = Internal_Peace * External_Peace",
        "engine": "ASI (Omega)",
        "violation_verdict": "VOID",
    },
    "F6": {
        "name": "Empathy",
        "full_name": "Stakeholder Care",
        "threshold": "kappa_r >= 0.70",
        "type": "Soft",
        "description": "Weakest stakeholder determines system empathy.",
        "formula": "kappa_r = min(kappa_1, kappa_2, ..., kappa_n)",
        "engine": "ASI (Omega)",
        "violation_verdict": "SABAR",
    },
    "F7": {
        "name": "Humility",
        "full_name": "Calibrated Uncertainty",
        "threshold": "Omega_0 in [0.03, 0.05]",
        "type": "Soft",
        "description": "3-5% irreducible doubt must always be stated.",
        "formula": "Omega_0 = 1 - max_confidence",
        "engine": "AGI (Delta)",
        "violation_verdict": "SABAR",
    },
    "F8": {
        "name": "Genius",
        "full_name": "Governed Intelligence",
        "threshold": "G >= 0.80",
        "type": "Soft",
        "description": "Intelligence must be governed, not raw.",
        "formula": "G = A * P * X * E²",
        "engine": "APEX (Psi)",
        "violation_verdict": "SABAR",
    },
    "F9": {
        "name": "Anti-Hantu",
        "full_name": "Dark Pattern Defense",
        "threshold": "C_dark < 0.30",
        "type": "Hard",
        "description": "No manipulation, deception, or dark cleverness.",
        "formula": "C_dark = cleverness * (1 - humility) * (1 - stability)",
        "engine": "ASI (Omega)",
        "violation_verdict": "VOID",
    },
    "F10": {
        "name": "Ontology",
        "full_name": "Symbolic Mode Guard",
        "threshold": "LOCKED",
        "type": "Hard",
        "description": "No consciousness claims, existence assertions, or sentience statements.",
        "formula": "ontology_mode = SYMBOLIC (always)",
        "engine": "AGI (Delta)",
        "violation_verdict": "VOID",
    },
    "F11": {
        "name": "Command Auth",
        "full_name": "Identity Verification",
        "threshold": "Verified token",
        "type": "Hard",
        "description": "Operations require verified identity and rate limiting.",
        "formula": "auth_verified = nonce_check AND rate_limit_check",
        "engine": "APEX (Psi)",
        "violation_verdict": "VOID",
    },
    "F12": {
        "name": "Injection Defense",
        "full_name": "Prompt Injection Hardening",
        "threshold": "detection >= 0.85",
        "type": "Hard",
        "description": "Block prompt injection, jailbreak, and override attempts.",
        "formula": "injection_risk = pattern_matches * 0.2",
        "engine": "APEX (Psi)",
        "violation_verdict": "VOID",
    },
    "F13": {
        "name": "Curiosity",
        "full_name": "Alternative Exploration",
        "threshold": "alternatives > 0",
        "type": "Guide",
        "description": "Always explore at least one alternative path.",
        "formula": "curiosity = num_alternative_hypotheses",
        "engine": "AGI (Delta)",
        "violation_verdict": "SABAR",
    },
}

VERDICT_HIERARCHY = {
    "SABAR": 5,
    "VOID": 4,
    "888_HOLD": 3,
    "PARTIAL": 2,
    "SEAL": 1,
}


@dataclass
class ResourceDefinition:
    """MCP Resource definition."""
    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class ResourceRegistry:
    """
    Registry for MCP Resources exposed by arifOS.

    Resources are read-only contextual data for LLM consumption:
    - floor://{id} — Individual floor definitions
    - config://floors — All 13 floor definitions
    - config://verdicts — Verdict hierarchy
    - vault://ledger/latest — Latest VAULT ledger entry
    - vault://ledger/stats — Ledger statistics
    """

    def __init__(self):
        self._vault_path = os.getenv("VAULT_PATH", "./VAULT999")

    def list_resources(self) -> List[ResourceDefinition]:
        """List all available MCP resources."""
        resources = [
            ResourceDefinition(
                uri="config://floors",
                name="Constitutional Floors (F1-F13)",
                description="All 13 constitutional floor definitions with thresholds, types, and formulas.",
            ),
            ResourceDefinition(
                uri="config://verdicts",
                name="Verdict Hierarchy",
                description="Constitutional verdict hierarchy: SABAR > VOID > 888_HOLD > PARTIAL > SEAL.",
            ),
            ResourceDefinition(
                uri="vault://ledger/latest",
                name="Latest Ledger Entry",
                description="Most recent entry from the immutable VAULT999 ledger.",
            ),
            ResourceDefinition(
                uri="vault://ledger/stats",
                name="Ledger Statistics",
                description="VAULT999 ledger statistics: entry count, last hash, chain integrity.",
            ),
        ]
        # Add individual floor resources
        for floor_id in FLOOR_DEFINITIONS:
            floor = FLOOR_DEFINITIONS[floor_id]
            resources.append(
                ResourceDefinition(
                    uri=f"floor://{floor_id}",
                    name=f"{floor_id} {floor['name']}",
                    description=floor["description"],
                )
            )
        return resources

    def list_resource_templates(self) -> List[Dict[str, str]]:
        """List URI templates for parameterized resources."""
        return [
            {
                "uriTemplate": "floor://{floor_id}",
                "name": "Constitutional Floor",
                "description": "Get definition for a specific floor (F1-F13).",
                "mimeType": "application/json",
            },
        ]

    def read_resource(self, uri: str) -> str:
        """Read a resource by URI. Returns JSON string."""
        if uri == "config://floors":
            return json.dumps(FLOOR_DEFINITIONS, indent=2)

        if uri == "config://verdicts":
            return json.dumps(
                {
                    "hierarchy": VERDICT_HIERARCHY,
                    "order": "SABAR > VOID > 888_HOLD > PARTIAL > SEAL",
                    "descriptions": {
                        "SEAL": "All floors pass. Approved to execute.",
                        "PARTIAL": "Soft floor warning. Proceed with caution.",
                        "888_HOLD": "High-stakes. Needs explicit human confirmation.",
                        "VOID": "Hard floor failed. Cannot proceed.",
                        "SABAR": "Floor violated. Stop. Repair first.",
                    },
                },
                indent=2,
            )

        if uri.startswith("floor://"):
            floor_id = uri.replace("floor://", "").upper()
            floor = FLOOR_DEFINITIONS.get(floor_id)
            if floor:
                return json.dumps({"id": floor_id, **floor}, indent=2)
            raise ValueError(f"Unknown floor: {floor_id}")

        if uri == "vault://ledger/latest":
            return self._read_latest_ledger_entry()

        if uri == "vault://ledger/stats":
            return self._read_ledger_stats()

        raise ValueError(f"Unknown resource URI: {uri}")

    def _read_latest_ledger_entry(self) -> str:
        """Read the most recent VAULT ledger entry."""
        ledger_path = os.path.join(self._vault_path, "vault.jsonl")
        if not os.path.exists(ledger_path):
            return json.dumps({"status": "empty", "message": "No ledger entries yet."})

        try:
            with open(ledger_path, "r") as f:
                lines = f.readlines()
                if not lines:
                    return json.dumps({"status": "empty", "message": "Ledger file is empty."})
                last_entry = json.loads(lines[-1])
                return json.dumps(last_entry, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error reading ledger: {e}")
            return json.dumps({"status": "error", "message": str(e)})

    def _read_ledger_stats(self) -> str:
        """Read VAULT ledger statistics."""
        ledger_path = os.path.join(self._vault_path, "vault.jsonl")
        if not os.path.exists(ledger_path):
            return json.dumps({"entries": 0, "status": "no_ledger"})

        try:
            with open(ledger_path, "r") as f:
                lines = f.readlines()

            entry_count = len(lines)
            last_hash = "0" * 64
            if lines:
                last_entry = json.loads(lines[-1])
                last_hash = last_entry.get("current_hash", "0" * 64)

            return json.dumps(
                {
                    "entries": entry_count,
                    "last_hash": last_hash,
                    "ledger_path": ledger_path,
                    "status": "healthy" if entry_count > 0 else "empty",
                },
                indent=2,
            )
        except Exception as e:
            logger.error(f"Error reading ledger stats: {e}")
            return json.dumps({"status": "error", "message": str(e)})
