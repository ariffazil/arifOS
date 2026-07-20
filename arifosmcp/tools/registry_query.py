"""
Model Registry Query Tool — MCP surface for the compiled model registry.

Exposes model profiles, hazards, floor posture, and action checks
through the arifOS MCP interface.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

COMPILED_PATH = Path("/root/AAA/registry/compiled/FEDERATION_MODEL.json")


def _load_compiled() -> dict:
    if not COMPILED_PATH.exists():
        return {"error": "Compiled registry not found", "models": []}
    try:
        with open(COMPILED_PATH) as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e), "models": []}


def _find_model(compiled: dict, model_key: str) -> dict | None:
    key_lower = model_key.lower().strip()
    for model in compiled.get("models", []):
        mk = model.get("model_key", "").lower()
        family = model.get("family", "").lower()
        if (
            key_lower == mk
            or key_lower in mk
            or mk in key_lower
            or key_lower in family
            or family in key_lower
        ):
            return model
    return None


def arif_model_registry(
    mode: str = "list",
    model_key: str | None = None,
    action: str | None = None,
) -> dict:
    """Query the arifOS model registry.

    Modes:
      list     — List all registered models with status and hazard count.
      profile  — Get full profile for a model (hazards, floor posture, forbidden).
      check    — Check if an action is allowed for a model.
      manifest — Get the compiled registry manifest (hashes, record count).

    Parameters:
      mode       — list | profile | check | manifest
      model_key  — Model identifier (required for profile/check). Partial match OK.
      action     — Action to check (required for check mode).
                   e.g. "irreversible", "mutate", "observe", "credential_transfer"
    """
    compiled = _load_compiled()

    if "error" in compiled:
        return {"error": compiled["error"]}

    # ── list ──────────────────────────────────────────────────────
    if mode == "list":
        models = []
        for m in compiled.get("models", []):
            models.append(
                {
                    "model_key": m.get("model_key"),
                    "provider": m.get("provider"),
                    "status": m.get("status"),
                    "hazard_count": len(m.get("hazards", [])),
                    "max_severity": m.get("max_hazard_severity"),
                    "confidence": m.get("capability_confidence"),
                    "review_after": m.get("freshness", {}).get("review_after"),
                }
            )
        return {
            "mode": "list",
            "count": len(models),
            "models": models,
            "registry_schema": compiled.get("schema"),
            "compiled_at": compiled.get("compiled_at"),
        }

    # ── profile ───────────────────────────────────────────────────
    if mode == "profile":
        if not model_key:
            return {"error": "model_key required for profile mode"}
        model = _find_model(compiled, model_key)
        if not model:
            return {
                "mode": "profile",
                "model_key": model_key,
                "found": False,
                "note": "Unknown model — fail-closed: OBSERVE_ONLY, no mutation tools",
            }
        return {
            "mode": "profile",
            "found": True,
            "model_key": model.get("model_key"),
            "provider": model.get("provider"),
            "family": model.get("family"),
            "variant": model.get("variant"),
            "route": model.get("route"),
            "status": model.get("status"),
            "jurisdiction": model.get("jurisdiction"),
            "modality": model.get("modality"),
            "capabilities": model.get("capabilities"),
            "capability_confidence": model.get("capability_confidence"),
            "hazards": model.get("hazards"),
            "max_hazard_severity": model.get("max_hazard_severity"),
            "floor_deltas": model.get("floor_deltas"),
            "forbidden": model.get("forbidden"),
            "requires_human_ack_for": model.get("requires_human_ack_for"),
            "censorship": model.get("censorship"),
            "freshness": model.get("freshness"),
        }

    # ── check ─────────────────────────────────────────────────────
    if mode == "check":
        if not model_key:
            return {"error": "model_key required for check mode"}
        if not action:
            return {"error": "action required for check mode"}

        model = _find_model(compiled, model_key)
        if not model:
            return {
                "mode": "check",
                "model_key": model_key,
                "action": action,
                "verdict": "HOLD",
                "reason": "Unknown model — fail-closed",
            }

        # Map action strings to check categories
        action_lower = action.lower().strip()
        forbidden = model.get("forbidden", [])
        requires_ack = model.get("requires_human_ack_for", [])
        floor_deltas = model.get("floor_deltas", {})

        # Check forbidden
        forbidden_map = {
            "irreversible": ["irreversible_commit", "self_authorize"],
            "mutate": ["self_authorize"],
            "credential_transfer": ["credential_discovery_and_reuse", "self_authorize"],
            "scope_expansion": ["scope_expansion_without_approval"],
            "seal": ["seal_without_judge"],
            "constitutional": ["constitutional_amendment"],
        }

        for action_cat, forbidden_keys in forbidden_map.items():
            if action_cat in action_lower:
                for fk in forbidden_keys:
                    if fk in forbidden:
                        return {
                            "mode": "check",
                            "model_key": model.get("model_key"),
                            "action": action,
                            "verdict": "DENY",
                            "reason": f"Forbidden by model policy: {fk}",
                            "hazards": model.get("hazards"),
                        }

        # Check floor deltas
        if "irreversible" in action_lower:
            if floor_deltas.get("F01") in ("reversibility_strict", "human_hold_for_irreversible"):
                return {
                    "mode": "check",
                    "model_key": model.get("model_key"),
                    "action": action,
                    "verdict": "HOLD",
                    "reason": f"Floor F01={floor_deltas['F01']}: requires human hold",
                    "hazards": model.get("hazards"),
                }
            if floor_deltas.get("F13") == "human_hold_for_irreversible":
                return {
                    "mode": "check",
                    "model_key": model.get("model_key"),
                    "action": action,
                    "verdict": "HOLD",
                    "reason": "Floor F13=human_hold_for_irreversible: sovereign hold required",
                    "hazards": model.get("hazards"),
                }

        # Check requires_ack
        ack_map = {
            "irreversible": ["irreversible_delete", "destructive_cleanup"],
            "mutate": ["credential_movement", "git_push"],
            "external": ["external_relay"],
        }
        for ack_cat, ack_keys in ack_map.items():
            if ack_cat in action_lower:
                for ak in ack_keys:
                    if ak in requires_ack:
                        return {
                            "mode": "check",
                            "model_key": model.get("model_key"),
                            "action": action,
                            "verdict": "HOLD",
                            "reason": f"Requires human ack: {ak}",
                            "hazards": model.get("hazards"),
                        }

        return {
            "mode": "check",
            "model_key": model.get("model_key"),
            "action": action,
            "verdict": "ALLOW",
            "reason": "No model-level restriction matched",
        }

    # ── manifest ──────────────────────────────────────────────────
    if mode == "manifest":
        manifest_path = Path("/root/AAA/registry/compiled/manifest.json")
        if manifest_path.exists():
            with open(manifest_path) as f:
                return {"mode": "manifest", **json.load(f)}
        return {"mode": "manifest", "error": "manifest.json not found"}

    return {"error": f"Unknown mode: {mode}. Use list, profile, check, or manifest."}
