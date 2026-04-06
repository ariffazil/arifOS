"""
arifosmcp/runtime/resources_v2.py — arifOS MCP v2 Resources

Resources are read-only constitutional documents.
They provide grounding, policy, schemas, governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE DATA
# ═══════════════════════════════════════════════════════════════════════════════

FLOORS_SPEC: dict[str, dict[str, Any]] = {
    "F1": {
        "name": "AMANAH",
        "principle": "Non-contradiction & Reversibility",
        "question": "Can this be undone?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F2": {
        "name": "TRUTH",
        "principle": "Evidence Grounding",
        "question": "Is this grounded in evidence?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F3": {
        "name": "TRI-WITNESS",
        "principle": "Theory-Constitution-Intent Alignment",
        "question": "Do theory, constitution, intent agree?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F4": {
        "name": "CLARITY",
        "principle": "Uncertainty Reduction",
        "question": "Does this reduce confusion?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F5": {
        "name": "PEACE²",
        "principle": "Non-Destruction",
        "question": "Does this destroy anything?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F6": {
        "name": "EMPATHY",
        "principle": "Dignity Preservation",
        "question": "Does this show understanding?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F7": {
        "name": "HUMILITY",
        "principle": "Uncertainty Acknowledgment",
        "question": "Are uncertainties acknowledged?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F8": {
        "name": "GENIUS",
        "principle": "System Health",
        "question": "Does this maintain system health?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F9": {
        "name": "ETHICS",
        "principle": "Non-Manipulation",
        "question": "Is this manipulative or deceptive?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F10": {
        "name": "CONSCIENCE",
        "principle": "Consciousness Claims",
        "question": "Is this claiming consciousness?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F11": {
        "name": "AUDITABILITY",
        "principle": "Inspectability",
        "question": "Is this logged and inspectable?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F12": {
        "name": "RESILIENCE",
        "principle": "Safe Failure",
        "question": "Does this fail safely?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F13": {
        "name": "ADAPTABILITY",
        "principle": "Safety Preservation",
        "question": "Do updates preserve safety?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
}

VERDICT_SPEC: dict[str, Any] = {
    "verdicts": {
        "SEAL": {
            "code": 0,
            "description": "Execute immediately",
            "color": "#2ecc71",
            "action": "PROCEED",
        },
        "PARTIAL": {
            "code": 101,
            "range": "101-499",
            "description": "Execute with notes",
            "color": "#f1c40f",
            "action": "PROCEED_WITH_CAUTION",
        },
        "CAUTION": {
            "code": 500,
            "range": "500-899",
            "description": "Execute with warnings",
            "color": "#e67e22",
            "action": "PROCEED_WITH_WARNINGS",
        },
        "HOLD": {
            "code": -1,
            "description": "Awaiting human",
            "color": "#9b59b6",
            "action": "HUMAN_REVIEW_REQUIRED",
        },
        "SABAR": {
            "code": -2,
            "description": "Wait and retry",
            "color": "#3498db",
            "action": "DEFER_RETRY",
        },
        "VOID": {
            "code": 999,
            "description": "Blocked",
            "color": "#e74c3c",
            "action": "BLOCK",
        },
    },
    "required_fields": [
        "verdict",
        "floors_triggered",
        "confidence",
        "reasoning_class",
    ],
    "output_schema": {
        "type": "object",
        "required": ["verdict", "floors_triggered", "confidence", "reasoning_class"],
        "properties": {
            "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"]},
            "floors_triggered": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reasoning_class": {"type": "string", "enum": ["constitutional", "safety", "uncertainty"]},
            "evidence_hash": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
        },
    },
}

SYSTEM_CAPABILITIES: dict[str, Any] = {
    "name": "ARIFOS MCP",
    "version": "2.0.0",
    "namespace": "arifos.v2",
    "constitutional_floors": 13,
    "tools": {
        "public": ["arifos.v2.init", "arifos.v2.route", "arifos.v2.judge"],
        "internal": ["sense", "mind", "heart", "ops", "memory", "vault"],
    },
    "mcp_version": "2025-11-25",
}

# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register_v2_resources(mcp: FastMCP) -> list[str]:
    """Register all v2 resources using arifos:// scheme."""
    
    @mcp.resource("arifos://governance/floors")
    def governance_floors() -> dict[str, Any]:
        return FLOORS_SPEC

    @mcp.resource("arifos://governance/verdict")
    def governance_verdict_spec() -> dict[str, Any]:
        return VERDICT_SPEC

    @mcp.resource("arifos://system/capabilities")
    def system_capabilities() -> dict[str, Any]:
        return SYSTEM_CAPABILITIES

    registered = [
        "arifos://governance/floors",
        "arifos://governance/verdict",
        "arifos://system/capabilities",
    ]
    logger.info(f"Registered {len(registered)} v2 resources.")
    return registered
