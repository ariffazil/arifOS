"""
arifos/runtime/context_contracts.py — arifOS Shared Context Contracts

Canonical JSON schemas used across tools, resources, and prompts.
These are the shared data contracts that make the MCP surface coherent.

Six contracts:
  SessionAnchor        — init_session_anchor, session resources, prompts
  TelemetryEnvelope    — sense_reality, estimate_ops, judge_verdict, vitals
  EvidenceBundle       — multi-agent handoff, reasoning, memory, vault record
  VerdictRecord        — judge_verdict, record_vault_entry, vault/recent resource
  ConstitutionalHealthView — ChatGPT render path and widget
  ToolAuthContext      — restricted tools: memory, vault, VPS execution

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# SessionAnchor
# ---------------------------------------------------------------------------

SESSION_ANCHOR_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/session-anchor",
    "title": "SessionAnchor",
    "description": "Constitutional session identity. Established by init_session_anchor.",
    "type": "object",
    "properties": {
        "session_id": {"type": "string", "description": "Unique session identifier (UUID)"},
        "actor_id": {"type": "string", "description": "Human sovereign or agent identity"},
        "declared_name": {"type": "string", "description": "Optional display name"},
        "intent": {"type": "string", "description": "Session purpose statement"},
        "token": {"type": "string", "description": "Short-lived session token"},
        "floor_audit": {
            "type": "object",
            "description": "F1-F13 pass/fail at session init",
            "additionalProperties": {"type": "boolean"},
        },
        "created_at": {"type": "string", "format": "date-time"},
        "expires_at": {"type": "string", "format": "date-time"},
    },
    "required": ["session_id", "actor_id"],
}

# ---------------------------------------------------------------------------
# TelemetryEnvelope
# ---------------------------------------------------------------------------

TELEMETRY_ENVELOPE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/telemetry-envelope",
    "title": "TelemetryEnvelope",
    "description": "Constitutional metrics snapshot. Canonical field names — never aliases.",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "epoch": {"type": "string", "description": "ISO-8601 date string"},
        "tau_truth": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "F2 Truth score — must be ≥ 0.99 for SEAL",
        },
        "omega_0": {
            "type": "number",
            "minimum": 0.0,
            "description": "F7 Humility — target 0.03–0.05",
        },
        "delta_s": {
            "type": "number",
            "description": "F4 Clarity — must be ≤ 0 (entropy reduction)",
        },
        "peace2": {
            "type": "number",
            "minimum": 0.0,
            "description": "F5 Peace² — harmlessness score ≥ 0.95 target",
        },
        "kappa_r": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "F6 Empathy — vulnerability-adjusted care score",
        },
        "tri_witness": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "F3 Tri-Witness coherence (human × ai × earth)",
        },
        "psi_le": {
            "type": "number",
            "description": "Ψ Life-Energy vitality index",
        },
        "g_score": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "G† Genius score — must be ≥ 0.80 for execution",
        },
        "verdict_hint": {
            "type": "string",
            "enum": ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD"],
            "description": "Indicative verdict (non-binding until apex_soul confirms)",
        },
    },
    "required": ["session_id", "epoch", "tau_truth", "delta_s", "kappa_r"],
}

# ---------------------------------------------------------------------------
# EvidenceBundle
# ---------------------------------------------------------------------------

EVIDENCE_BUNDLE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/evidence-bundle",
    "title": "EvidenceBundle",
    "description": "Structured evidence for multi-agent handoff, memory, and vault records.",
    "type": "object",
    "properties": {
        "bundle_id": {"type": "string"},
        "session_id": {"type": "string"},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_type": {
                        "type": "string",
                        "enum": ["web", "vector_memory", "tool_output", "human_input", "vault"],
                    },
                    "content": {"type": "string"},
                    "confidence": {"type": "number"},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
                "required": ["source_type", "content"],
            },
        },
        "synthesized": {"type": "string", "description": "Synthesized summary across sources"},
        "tau_truth": {"type": "number", "description": "Aggregate truth confidence"},
        "tri_witness": {"type": "number", "description": "Cross-source coherence"},
    },
    "required": ["bundle_id", "session_id", "sources"],
}

# ---------------------------------------------------------------------------
# VerdictRecord
# ---------------------------------------------------------------------------

VERDICT_RECORD_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/verdict-record",
    "title": "VerdictRecord",
    "description": "Immutable constitutional verdict. Sealed in VAULT999 via record_vault_entry.",
    "type": "object",
    "properties": {
        "seal_id": {"type": "string", "description": "Unique seal identifier"},
        "session_id": {"type": "string"},
        "actor_id": {"type": "string"},
        "verdict": {
            "type": "string",
            "enum": ["SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD"],
        },
        "candidate_action": {"type": "string"},
        "floors_passed": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of constitutional floors that passed (e.g. F1, F2, ...)",
        },
        "floors_failed": {
            "type": "array",
            "items": {"type": "string"},
        },
        "telemetry": {"$ref": "arifos://contracts/telemetry-envelope"},
        "bls_aggregate_signature": {"type": "string", "description": "BLS12-381 hex signature"},
        "chain_hash": {"type": "string", "description": "SHA-256 Merkle chain hash"},
        "proof_status": {
            "type": "string",
            "enum": ["Phase A — BLS Ready", "Phase B — pending", "Phase C — federation"],
        },
        "sealed_at": {"type": "string", "format": "date-time"},
        "jurors": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Juror agent IDs that signed",
        },
    },
    "required": ["seal_id", "session_id", "verdict", "candidate_action", "sealed_at"],
}

# ---------------------------------------------------------------------------
# ConstitutionalHealthView
# ---------------------------------------------------------------------------

CONSTITUTIONAL_HEALTH_VIEW_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/constitutional-health-view",
    "title": "ConstitutionalHealthView",
    "description": "Read-only dashboard view for ChatGPT widget and human-facing renders.",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "status": {"type": "string", "enum": ["HEALTHY", "DEGRADED", "CRITICAL", "VOID"]},
        "version": {"type": "string"},
        "floors_active": {"type": "integer", "minimum": 0, "maximum": 13},
        "tools_loaded": {"type": "integer"},
        "telemetry": {"$ref": "arifos://contracts/telemetry-envelope"},
        "recent_verdicts": {
            "type": "array",
            "maxItems": 5,
            "items": {"$ref": "arifos://contracts/verdict-record"},
        },
        "widget_uri": {"type": "string", "description": "Widget render URI"},
        "generated_at": {"type": "string", "format": "date-time"},
    },
    "required": ["status", "floors_active", "tools_loaded"],
}

# ---------------------------------------------------------------------------
# ToolAuthContext
# ---------------------------------------------------------------------------

TOOL_AUTH_CONTEXT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "arifos://contracts/tool-auth-context",
    "title": "ToolAuthContext",
    "description": "Auth context required by restricted tools: memory, vault, VPS execution.",
    "type": "object",
    "properties": {
        "session_id": {"type": "string"},
        "token": {"type": "string", "description": "Session token from init_session_anchor"},
        "actor_id": {"type": "string"},
        "access_class": {
            "type": "string",
            "enum": ["public", "authenticated", "sovereign"],
        },
        "scopes": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Granted capability scopes (e.g. vault:seal, memory:write)",
        },
    },
    "required": ["session_id", "token", "access_class"],
}

# ---------------------------------------------------------------------------
# Registry — all contracts by $id
# ---------------------------------------------------------------------------

CONTEXT_CONTRACTS: dict[str, dict[str, Any]] = {
    "session-anchor": SESSION_ANCHOR_SCHEMA,
    "telemetry-envelope": TELEMETRY_ENVELOPE_SCHEMA,
    "evidence-bundle": EVIDENCE_BUNDLE_SCHEMA,
    "verdict-record": VERDICT_RECORD_SCHEMA,
    "constitutional-health-view": CONSTITUTIONAL_HEALTH_VIEW_SCHEMA,
    "tool-auth-context": TOOL_AUTH_CONTEXT_SCHEMA,
}

TELEMETRY_ENVELOPE_REQUIRED = TELEMETRY_ENVELOPE_SCHEMA["required"]
