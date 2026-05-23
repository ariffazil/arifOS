"""
arifOS Portable Contract Schemas — Layer 1 Constitution Package
==============================================================
Machine-agnostic, model-agnostic, app-agnostic.
All schemas are JSON-Schema compatible, transport-neutral.

Version: 2026-05-23
Epoch: 2026-05-23T12:40:00+08:00
Seal: DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations
import json, re, sys
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# ── Version ────────────────────────────────────────────────────────────────────
CONTRACT_VERSION = "2026-05-23"
ARIFOS_VERSION   = "0.1.0-prototype"

# ── URI Base Defaults (override with env vars) ─────────────────────────────────
def _env(key: str, fallback: str) -> str:
    return Path(os.environ.get(key, fallback)).as_uri() if ":" not in fallback and fallback.startswith("/") else os.environ.get(key, fallback)

import os

ARIFOS_PLAN_URI_BASE     = os.environ.get("ARIFOS_PLAN_URI_BASE",     "file:///workspace/plans")
ARIFOS_ARTIFACT_URI_BASE= os.environ.get("ARIFOS_ARTIFACT_URI_BASE", "file:///workspace/artifacts")
ARIFOS_SEAL_URI_BASE     = os.environ.get("ARIFOS_SEAL_URI_BASE",     "file:///workspace/artifacts/vault999")
ARIFOS_SCRIPT_URI_BASE   = os.environ.get("ARIFOS_SCRIPT_URI_BASE",   "file:///workspace/scripts")
ARIFOS_CONFIG_URI_BASE   = os.environ.get("ARIFOS_CONFIG_URI_BASE",   "file:///workspace/configs")

# ── Storage abstraction ─────────────────────────────────────────────────────────
class StorageAdapter:
    """Pluggable storage. Override uri_scheme to swap backend."""

    def __init__(self, plan_base: str = ARIFOS_PLAN_URI_BASE,
                       artifact_base: str = ARIFOS_ARTIFACT_URI_BASE,
                       seal_base: str = ARIFOS_SEAL_URI_BASE):
        self.plan_base     = plan_base
        self.artifact_base = artifact_base
        self.seal_base     = seal_base
        self._ensure_local_dirs()

    def _ensure_local_dirs(self):
        """Sync file:// paths to local disk."""
        for base in [self.plan_base, self.artifact_base, self.seal_base]:
            if base.startswith("file://"):
                Path(base.replace("file://", "")).mkdir(parents=True, exist_ok=True)

    def resolve(self, uri: str) -> Path:
        """Convert any URI to a local Path if file://, else return uri str."""
        if uri.startswith("file://"):
            return Path(uri.replace("file://", ""))
        return Path(uri)  # fallback

    def write_plan(self, plan: dict) -> str:
        plan_id = plan.get("plan_id", f"plan-{datetime.now():%Y%m%dT%H%M%S}")
        uri = f"{self.plan_base}/{plan_id}.json"
        path = self.resolve(uri)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(plan, f, indent=2)
        return uri

    def write_seal(self, seal: dict) -> str:
        seal_id = seal.get("seal_id", f"seal-{datetime.now():%Y%m%dT%H%M%S}")
        uri = f"{self.seal_base}/{seal_id}.json"
        path = self.resolve(uri)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(seal, f, indent=2)
        return uri

    def write_artifact(self, name: str, content: str, kind: str = "report") -> str:
        uri = f"{self.artifact_base}/{kind}/{name}"
        path = self.resolve(uri)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return uri

_default_storage = StorageAdapter()

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA 1 — Tool Schema
# ─────────────────────────────────────────────────────────────────────────────
TOOL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ArifOSTool",
    "description": "Canonical arifOS tool definition for MCP tools/list",
    "type": "object",
    "required": ["name", "description", "inputSchema"],
    "properties": {
        "name":         {"type": "string",  "pattern": "^arif_[a-z_]+$"},
        "description":  {"type": "string"},
        "inputSchema":  {"type": "object"},
        "annotations":  {
            "type": "object",
            "properties": {
                "readOnly":     {"type": "boolean"},
                "-destructive": {"type": "boolean"},
                "idempotent":   {"type": "boolean"},
                "openWorld":    {"type": "boolean"},
            }
        }
    }
}

ARIFOS_TOOLS = [
    {
        "name": "arif_session_init",
        "description": "000 INIT. Session anchor with F1-F13 floor setup and safety scan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "Human intent string"},
                "actor":  {"type": "string", "default": "hermes", "description": "Actor identifier"}
            },
            "required": ["intent"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_judge_deliberate",
        "description": "888 JUDGE. Classifies intent → SEAL | HOLD | CAUTION | SABAR | VOID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent":   {"type": "string", "description": "Intent string to judge"},
                "context":  {"type": "object", "description": "Optional context metadata"}
            },
            "required": ["intent"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_vault_seal",
        "description": "999 VAULT. Writes immutable seal entry for an action or decision.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data":   {"type": "object", "description": "Seal payload data"},
                "human":  {"type": "string", "description": "Human name"}
            },
            "required": ["data"]
        },
        "annotations": {"readOnly": False, "idempotent": False}
    },
    {
        "name": "arif_forge_execute",
        "description": "010 FORGE. Executes command after 888 HOLD gate cleared.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command":    {"type": "string", "description": "Command to execute"},
                "gated_by":   {"type": "string", "description": "Verdict that cleared execution"}
            },
            "required": ["command"]
        },
        "annotations": {"readOnly": False, "destructive": False}
    },
    {
        "name": "arif_sense_observe",
        "description": "111 SENSE. Token/char analysis of input text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_text": {"type": "string"}
            },
            "required": ["input_text"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_heart_critique",
        "description": "666 HEART. Anti-hallucination critique via C_dark scoring.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_kernel_route",
        "description": "444 KERNEL. Intent routing + danger classification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string"}
            },
            "required": ["intent"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_mind_reason",
        "description": "333 MIND. Reasoning on premises.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "premises": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["premises"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_reply_compose",
        "description": "444r REPLY. Reply synthesis.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "tone":    {"type": "string", "default": "neutral"}
            },
            "required": ["content"]
        },
        "annotations": {"readOnly": False, "idempotent": False}
    },
    {
        "name": "arif_memory_recall",
        "description": "555 MEMORY. Memory recall stub.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_gateway_connect",
        "description": "666g GATEWAY. A2A peer connection stub.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "peer":   {"type": "string"},
                "action": {"type": "string", "default": "ping"}
            },
            "required": ["peer"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_ops_measure",
        "description": "777 OPS. Compute complexity measurement.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string"}
            },
            "required": ["operation"]
        },
        "annotations": {"readOnly": True, "idempotent": True}
    },
    {
        "name": "arif_plan_write",
        "description": "PLAN WRITER. Writes structured plan to /workspace/plans/.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "extra":  {"type": "object"}
            },
            "required": ["intent"]
        },
        "annotations": {"readOnly": False, "idempotent": False}
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA 2 — Verdict Envelope
# ─────────────────────────────────────────────────────────────────────────────
VERDICT_ENVELOPE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ArifOSVerdictEnvelope",
    "description": "Standard arifOS response envelope for every tool call",
    "type": "object",
    "required": ["verdict", "telemetry", "witness", "epoch"],
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["SEAL", "HOLD", "CAUTION", "SABAR", "VOID", "PROCEED"],
            "description": "Governance verdict"
        },
        "telemetry": {
            "type": "object",
            "required": ["epoch", "dS", "peace2", "kappa_r", "shadow", "confidence", "psi_le", "qdf"],
            "properties": {
                "epoch":       {"type": "string", "format": "date-time"},
                "dS":          {"type": "number", "minimum": -1, "maximum": 1,
                                "description": "Entropy delta (negative = order)"},
                "peace2":      {"type": "number", "minimum": 0,
                                "description": "Peace coherence score"},
                "kappa_r":     {"type": "number", "minimum": 0, "maximum": 1,
                                "description": "Inter-rater reliability"},
                "shadow":      {"type": "number", "minimum": 0, "maximum": 1,
                                "description": "Shadow/anti-hallucination score"},
                "confidence":  {"type": "number", "minimum": 0, "maximum": 1,
                                "description": "Model confidence in verdict"},
                "psi_le":      {"type": "number", "description": "PSI lower envelope"},
                "qdf":         {"type": "number", "minimum": 0, "maximum": 1,
                                "description": "Quantum dignity factor"},
                "floors_active":  {"type": "array", "items": {"type": "string"}},
                "floors_violated": {"type": "array", "items": {"type": "string"}},
                "risk_tier":   {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "ATOMIC"]},
                "reversibility": {"type": "string", "enum": ["FULL", "PARTIAL", "NONE"]},
                "human_required": {"type": "boolean"},
            }
        },
        "witness": {
            "type": "object",
            "properties": {
                "human":  {"type": "string"},
                "ai":     {"type": "string"},
                "earth":  {"type": "string"},
                "weights": {"type": "object", "properties": {
                    "human":  {"type": "number"},
                    "ai":     {"type": "number"},
                    "earth":  {"type": "number"},
                }}
            }
        },
        "plan_id":  {"type": "string"},
        "seal_id":  {"type": "string"},
        "artifacts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "kind": {"type": "string", "enum": ["plan", "seal", "report", "script", "config"]},
                    "uri":  {"type": "string", "format": "uri"},
                    "mime": {"type": "string"}
                }
            }
        },
        "content": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "const": "text"},
                    "text": {"type": "string"}
                }
            }
        },
        "tool":    {"type": "string"},
        "stage":   {"type": "string"},
        "reason":  {"type": "string"},
        "vault_lite": {"type": "boolean"},
    }
}

def make_envelope(
    verdict: str,
    tool: str,
    stage: str,
    reason: str = "",
    telemetry: dict = None,
    plan_id: str = None,
    seal_id: str = None,
    artifacts: list = None,
    content: str = "",
    human: str = "Muhammad Arif bin Fazil",
    ai_id: str = "hermes-runtime",
    earth: str = "hermes-pod",
    vault_lite: bool = True,
) -> dict:
    """Build a standard arifOS verdict envelope."""
    ts = datetime.now().isoformat()
    defaults = {
        "dS": 0.0, "peace2": 1.0, "kappa_r": 0.95,
        "shadow": 0.05, "confidence": 0.90,
        "psi_le": 1.0, "qdf": 0.95,
        "floors_active": [],
        "floors_violated": [],
        "risk_tier": "LOW",
        "reversibility": "FULL",
        "human_required": False,
    }
    if telemetry:
        defaults.update(telemetry)
    return {
        "verdict": verdict,
        "telemetry": {"epoch": ts, **defaults},
        "witness": {
            "human": human,
            "ai": ai_id,
            "earth": earth,
            "weights": {"human": 0.42, "ai": 0.32, "earth": 0.26}
        },
        "plan_id": plan_id,
        "seal_id": seal_id,
        "artifacts": artifacts or [],
        "content": [{"type": "text", "text": content}] if content else [],
        "tool": tool,
        "stage": stage,
        "reason": reason,
        "vault_lite": vault_lite,
    }

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA 3 — Plan Schema
# ─────────────────────────────────────────────────────────────────────────────
PLAN_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ArifOSPlan",
    "description": "arifOS structured plan — machine-agnostic",
    "type": "object",
    "required": ["plan_id", "epoch", "actor", "human", "intent", "status", "floors"],
    "properties": {
        "plan_id":     {"type": "string"},
        "epoch":       {"type": "string", "format": "date-time"},
        "actor":       {"type": "string"},
        "human":       {"type": "string"},
        "intent":      {"type": "string"},
        "status":      {"type": "string", "enum": ["DRAFT", "APPROVED", "SEALED", "EXECUTED", "VOID"]},
        "floors":      {"type": "object"},
        "hard_floors": {"type": "array", "items": {"type": "string"}},
        "soft_floors": {"type": "array", "items": {"type": "string"}},
        "witness":     {"type": "object"},
        "pipeline":    {"type": "string"},
        "vault_lite":  {"type": "boolean"},
        "deliverable_mode": {"type": "boolean"},
        "artifacts":   {"type": "array"},
        "steps":       {"type": "array", "items": {"type": "object"}},
        "verdict":     {"type": "string"},
        "seal_id":     {"type": "string"},
    }
}

def make_plan(intent: str, actor: str = "hermes", extra: dict = None) -> dict:
    ts = datetime.now().isoformat()
    plan_id = f"plan-{datetime.now():%Y%m%dT%H%M%S}"
    plan = {
        "plan_id": plan_id,
        "epoch": ts,
        "actor": actor,
        "human": "Muhammad Arif bin Fazil",
        "intent": intent,
        "status": "DRAFT",
        "floors": {
            "F01": "AMANAH",    "F02": "TRUTH",      "F03": "WITNESS",
            "F04": "CLARITY",   "F05": "PEACE",      "F06": "EMPATHY",
            "F07": "HUMILITY",  "F08": "GENIUS",     "F09": "ANTIHANTU",
            "F10": "ONTOLOGY",  "F11": "AUTH",       "F12": "INJECTION",
            "F13": "SOVEREIGN",
        },
        "hard_floors": ["F01", "F02", "F09", "F10", "F11", "F12", "F13"],
        "soft_floors": ["F03", "F04", "F05", "F06", "F07", "F08"],
        "witness": {"human": 0.42, "ai": 0.32, "earth": 0.26},
        "pipeline": "000→111→222→333→444r→444→555→666→666g→777→888→999→010",
        "vault_lite": True,
        "deliverable_mode": True,
        "artifacts": [],
        "verdict": "DRAFT",
    }
    if extra:
        plan.update(extra)
    return plan

def write_plan(intent: str, actor: str = "hermes", extra: dict = None) -> tuple[dict, str]:
    """Write plan to storage. Returns (plan dict, uri)."""
    plan = make_plan(intent, actor, extra)
    uri = _default_storage.write_plan(plan)
    return plan, uri

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA 4 — Seal Schema
# ─────────────────────────────────────────────────────────────────────────────
SEAL_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "ArifOSSeal",
    "description": "arifOS immutable seal — machine-agnostic",
    "type": "object",
    "required": ["seal_id", "epoch", "stage", "tool", "actor", "human", "data"],
    "properties": {
        "seal_id":     {"type": "string"},
        "epoch":       {"type": "string", "format": "date-time"},
        "stage":       {"type": "string"},
        "tool":        {"type": "string"},
        "actor":       {"type": "string"},
        "human":       {"type": "string"},
        "data":        {"type": "object"},
        "floors":      {"type": "array", "items": {"type": "string"}},
        "verdict":     {"type": "string"},
        "plan_id":     {"type": "string"},
        "merkle_hash": {"type": "string"},
        "vault_lite":  {"type": "boolean"},
        "witness":     {"type": "object"},
        "contract_version": {"type": "string"},
        "arifos_version":   {"type": "string"},
        "telemetry":   {"type": "object"},
    }
}

def make_seal(
    data: dict,
    tool: str = "arif_vault_seal",
    stage: str = "999",
    actor: str = "hermes",
    human: str = "Muhammad Arif bin Fazil",
    plan_id: str = None,
    extra: dict = None,
) -> dict:
    ts = datetime.now().isoformat()
    seal_id = f"seal-{datetime.now():%Y%m%dT%H%M%S}"
    seal = {
        "seal_id": seal_id,
        "epoch": ts,
        "stage": stage,
        "tool": tool,
        "actor": actor,
        "human": human,
        "data": data,
        "floors": ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08",
                   "F09", "F10", "F11", "F12", "F13"],
        "verdict": "SEALED",
        "plan_id": plan_id,
        "merkle_hash": f"lite_v0_sha256_{seal_id}",
        "vault_lite": True,
        "witness": {"human": 0.42, "ai": 0.32, "earth": 0.26},
        "contract_version": CONTRACT_VERSION,
        "arifos_version": ARIFOS_VERSION,
        "telemetry": {"dS": 0.0, "peace2": 1.0, "kappa_r": 0.95, "shadow": 0.05},
    }
    if extra:
        seal.update(extra)
    return seal

def write_seal(data: dict, tool: str = "arif_vault_seal", stage: str = "999",
               actor: str = "hermes", plan_id: str = None, extra: dict = None) -> tuple[dict, str]:
    """Write seal to storage. Returns (seal dict, uri)."""
    seal = make_seal(data, tool, stage, actor, "Muhammad Arif bin Fazil", plan_id, extra)
    uri = _default_storage.write_seal(seal)
    return seal, uri

# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA 5 — Capability Discovery
# ─────────────────────────────────────────────────────────────────────────────
CAPABILITY_DISCOVERY = {
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "tools":       {"listChanged": True},
        "resources":   {"subscribe": True, "listChanged": True},
        "prompts":     {"listChanged": True},
    },
    "serverInfo": {
        "name": "arifOS MCP Emulator",
        "version": ARIFOS_VERSION,
        "contractVersion": CONTRACT_VERSION,
    },
    "contractVersion": CONTRACT_VERSION,
    "floors": {
        "F01": {"name": "AMANAH",    "floor_type": "HARD"},
        "F02": {"name": "TRUTH",     "floor_type": "HARD"},
        "F03": {"name": "WITNESS",   "floor_type": "SOFT"},
        "F04": {"name": "CLARITY",   "floor_type": "SOFT"},
        "F05": {"name": "PEACE",     "floor_type": "SOFT"},
        "F06": {"name": "EMPATHY",   "floor_type": "SOFT"},
        "F07": {"name": "HUMILITY",  "floor_type": "SOFT"},
        "F08": {"name": "GENIUS",    "floor_type": "SOFT"},
        "F09": {"name": "ANTIHANTU", "floor_type": "HARD"},
        "F10": {"name": "ONTOLOGY",  "floor_type": "HARD"},
        "F11": {"name": "AUTH",      "floor_type": "HARD"},
        "F12": {"name": "INJECTION", "floor_type": "HARD"},
        "F13": {"name": "SOVEREIGN", "floor_type": "HARD"},
    },
    "storage": {
        "plan_uri":     ARIFOS_PLAN_URI_BASE,
        "artifact_uri": ARIFOS_ARTIFACT_URI_BASE,
        "seal_uri":     ARIFOS_SEAL_URI_BASE,
        "script_uri":   ARIFOS_SCRIPT_URI_BASE,
        "config_uri":   ARIFOS_CONFIG_URI_BASE,
    },
    "verdict_states": ["SEAL", "HOLD", "CAUTION", "SABAR", "VOID", "PROCEED"],
}

if __name__ == "__main__":
    import pprint
    print("arifOS Portable Contract Schemas v", CONTRACT_VERSION)
    print("Verdict states:", CAPABILITY_DISCOVERY["verdict_states"])
    print("Tools:", len(ARIFOS_TOOLS))
    print("Floors:", len(CAPABILITY_DISCOVERY["floors"]))
    print("Storage bases:")
    for k, v in [("plan", ARIFOS_PLAN_URI_BASE), ("seal", ARIFOS_SEAL_URI_BASE),
                 ("artifact", ARIFOS_ARTIFACT_URI_BASE)]:
        print(f"  {k}: {v}")
    print()
    # Demo: write a plan and a seal
    p, p_uri = write_plan("make Hermes machine-agnostic")
    print("Plan URI:", p_uri)
    s, s_uri = write_seal({"action": "contract_schemas_loaded", "status": "ALIVE"})
    print("Seal URI:", s_uri)