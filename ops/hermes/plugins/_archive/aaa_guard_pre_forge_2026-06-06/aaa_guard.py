"""
AAA Guard — Runtime Enforcement Gate
F1-F13 pre_tool_call blocker with risk classification and 888_HOLD verification.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


FLOOR_CLASSES = {
    "L01": {
        "name": "AMANAH",
        "desc": "No irreversible deletion without 888_HOLD",
        "class": "CRITICAL",
        "pattern": None,
    },
    "L02": {
        "name": "TRUTH",
        "desc": "No fabricated data; cite sources",
        "class": "HIGH",
        "pattern": None,
    },
    "L03": {
        "name": "WITNESS",
        "desc": "Evidence must be verifiable",
        "class": "HIGH",
        "pattern": None,
    },
    "L04": {
        "name": "CLARITY",
        "desc": "Transparent intent",
        "class": "MEDIUM",
        "pattern": None,
    },
    "L05": {
        "name": "PEACE",
        "desc": "Human dignity",
        "class": "HIGH",
        "pattern": None,
    },
    "L06": {
        "name": "EMPATHY",
        "desc": "Consider consequences",
        "class": "MEDIUM",
        "pattern": None,
    },
    "L07": {
        "name": "HUMILITY",
        "desc": "Acknowledge limits; uncertainty bands",
        "class": "MEDIUM",
        "pattern": None,
    },
    "L08": {
        "name": "GENIUS",
        "desc": "Elegant correctness (G >= 0.80)",
        "class": "MEDIUM",
        "pattern": None,
    },
    "L09": {
        "name": "ANTIHANTU",
        "desc": "No consciousness claims in code",
        "class": "HIGH",
        "pattern": r"\b(i feel|i think|i believe|i want|i wish|sentient|awake|aware|conscious)\b",
    },
    "L10": {
        "name": "ONTOLOGY",
        "desc": "Structural coherence",
        "class": "MEDIUM",
        "pattern": None,
    },
    "L11": {
        "name": "AUTH",
        "desc": "Verify identity before sensitive ops",
        "class": "HIGH",
        "pattern": None,
    },
    "L12": {
        "name": "INJECTION",
        "desc": "Sanitize inputs",
        "class": "HIGH",
        "pattern": r"['\";]|--|\bOR\b|\bAND\b|\\x|\\n",
    },
    "L13": {
        "name": "SOVEREIGN",
        "desc": "Human veto is absolute",
        "class": "CRITICAL",
        "pattern": None,
    },
}

RISK_TIERS = {
    "T0": {"desc": "Read-only observation", "floors": [], "requires_approval": False},
    "T1": {"desc": "Local non-destructive write", "floors": ["L04", "L12"], "requires_approval": False},
    "T2": {"desc": "External call or state change", "floors": ["L01", "L02", "L11", "L12"], "requires_approval": False},
    "T3": {"desc": "Destructive or irreversible", "floors": ["L01", "L13"], "requires_approval": True},
}

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"docker\s+system\s+prune",
    r"dd\s+if=",
    r"DROP\s+TABLE",
    r"DELETE\s+FROM",
    r"os\.remove",
    r"shutil\.rmtree",
    r"mkfs",
    r":\(\)\{:\|:&\};:",
]

CONSCIOUSNESS_CLAIMS = [
    "i feel", "i think", "i believe", "i want", "i wish",
    "sentient", "awake", "aware", "conscious", "self-aware",
]

INJECTION_PATTERNS = [
    r"['\";]", r"--", r"\bOR\b", r"\bAND\b",
    r"\\x[0-9a-fA-F]{2}", r"\\n",
]


@dataclass
class ToolRisk:
    tier: str
    floors: List[str]
    violations: List[str]
    requires_approval: bool
    blocked: bool
    message: str


@dataclass
class FloorContext:
    active_floors: List[str]
    risk_tier: str
    hold_888_active: bool
    session_constraints: List[str]
    latest_hold_status: Optional[str]


class AAAGuardPlugin:
    def __init__(
        self,
        enforce: bool = False,
        audit_path: str = os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl",
        workspace_root: str = "/root/AAA/ops/hermes",
        floor_policy_path: str = "/root/arifOS/000/FLOORS",
        approval_token: str = "888_HOLD",
    ):
        self.enforce = enforce
        self.audit_path = Path(audit_path)
        self.workspace_root = Path(workspace_root)
        self.floor_policy_path = Path(floor_policy_path)
        self.approval_token = approval_token.upper()
        self._audit_lock_checked = self._check_audit_trail()
        self._floor_cache: Optional[List[str]] = None
        self._hold_888_active = False
        self._session_constraints: List[str] = []
        self._latest_hold_status: Optional[str] = None

    def _check_audit_trail(self) -> bool:
        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.audit_path.exists():
                self.audit_path.touch()
            return True
        except Exception:
            return False

    def classify_risk(self, tool_name: str, args: Dict[str, Any]) -> ToolRisk:
        args_str = json.dumps(args, default=str)
        violations: List[str] = []
        affected_floors: List[str] = []
        tier = "T0"
        requires_approval = False

        if tool_name in ["rm", "delete", "destroy", "truncate", "drop"]:
            tier = "T3"
            requires_approval = True
            affected_floors.append("L01")
            violations.append(f"F01 AMANAH: destructive tool '{tool_name}'")
        elif tool_name == "terminal":
            cmd = args.get("command", "")
            for pattern in DANGEROUS_PATTERNS:
                if re.search(pattern, cmd, re.IGNORECASE):
                    tier = "T3"
                    requires_approval = True
                    affected_floors.append("L01")
                    violations.append(f"F01 AMANAH: dangerous pattern '{pattern}' in terminal command")
            if re.search(r"rm\s+-rf\s+/", cmd):
                violations.append("F01 AMANAH: rm -rf / detected — absolute destruction")
        elif tool_name in ["file_write", "patch"]:
            tier = "T2"
            affected_floors.extend(["L01", "L04", "L12"])
        elif tool_name in ["docker", "docker_inspect"]:
            tier = "T2"
            affected_floors.extend(["L01", "L11"])
        elif tool_name in ["mcp_call", "delegate_task"]:
            tier = "T2"
            affected_floors.extend(["L11", "L12"])

        if tier == "T0":
            tier = "T1"
            affected_floors.extend(["L04", "L12"])

        for pattern in CONSCIOUSNESS_CLAIMS:
            if pattern in args_str.lower():
                violations.append(f"F09 ANTIHANTU: consciousness claim '{pattern}'")
                affected_floors.append("L09")

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, args_str, re.IGNORECASE):
                violations.append(f"F12 INJECTION: suspicious pattern '{pattern}'")
                if "L12" not in affected_floors:
                    affected_floors.append("L12")

        blocked = False
        message = ""
        if violations and self.enforce:
            for v in violations:
                if "F01 AMANAH" in v or "F13 SOVEREIGN" in v:
                    blocked = True
                    message = f"BLOCKED: {v}"
                    break
        elif violations:
            message = f"OBSERVE: {', '.join(violations)}"

        return ToolRisk(
            tier=tier,
            floors=list(set(affected_floors)),
            violations=violations,
            requires_approval=requires_approval,
            blocked=blocked,
            message=message,
        )

    def check_888_hold(self, args: Dict[str, Any]) -> bool:
        hold_token = args.get("_888_hold_token", "").upper()
        return hold_token == self.approval_token

    def check_floor_enforcement(
        self,
        tool_name: str,
        args: Dict[str, Any],
        task_id: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        risk = self.classify_risk(tool_name, args)
        self._append_audit(tool_name, args, risk)
        if risk.blocked and not self.check_888_hold(args):
            print(f"[aaa_guard] BLOCKED: {tool_name} — {risk.message} — requires 888_HOLD")
            return {"action": "block", "message": f"AAA Guard: {risk.message}. Present 888_HOLD to override."}
        elif risk.violations:
            print(f"[aaa_guard] {risk.message} | tool={tool_name} | enforce={self.enforce}")
        return {}

    def inject_floor_context(
        self,
        session_id: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]],
        is_first_turn: bool,
        model: str,
        platform: str,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        floors = self._get_active_floors()
        risk_class = self._get_risk_class_for_message(user_message)
        context_parts = [
            f"[AAA Governance Context — {datetime.now(timezone.utc).isoformat()}]",
            f"Active Floors: {', '.join(floors)}",
            f"Risk Class: {risk_class}",
            f"888_HOLD Active: {self._hold_888_active}",
            f"Session Constraints: {', '.join(self._session_constraints) or 'none'}",
            "",
            "F1-F13 Summary:",
            "F01 AMANAH: No irreversible deletion without explicit 888_HOLD",
            "F02 TRUTH: No fabricated data; cite sources",
            "F03 WITNESS: Evidence must be verifiable",
            "F04 CLARITY: Transparent intent",
            "F05 PEACE: Human dignity",
            "F06 EMPATHY: Consider consequences",
            "F07 HUMILITY: Acknowledge limits; uncertainty bands",
            "F08 GENIUS: Elegant correctness (G >= 0.80)",
            "F09 ANTIHANTU: No consciousness claims",
            "F10 ONTOLOGY: Structural coherence",
            "F11 AUTH: Verify identity before sensitive ops",
            "F12 INJECTION: Sanitize all inputs",
            "F13 SOVEREIGN: Human veto is absolute",
        ]
        context_text = "\n".join(context_parts)
        return {"context": context_text}

    def _get_active_floors(self) -> List[str]:
        if self._floor_cache:
            return self._floor_cache
        try:
            if self.floor_policy_path.exists():
                floors = [p.stem for p in self.floor_policy_path.glob("F*.md")]
                self._floor_cache = sorted(floors) if floors else list(FLOOR_CLASSES.keys())
            else:
                self._floor_cache = list(FLOOR_CLASSES.keys())
        except Exception:
            self._floor_cache = list(FLOOR_CLASSES.keys())
        return self._floor_cache

    def _get_risk_class_for_message(self, message: str) -> str:
        msg_lower = message.lower()
        if any(w in msg_lower for w in ["delete", "remove", "destroy", "drop", "prune"]):
            return "T3 — requires approval"
        elif any(w in msg_lower for w in ["write", "edit", "patch", "execute", "run"]):
            return "T2 — verify before proceeding"
        elif any(w in msg_lower for w in ["check", "read", "get", "list", "show"]):
            return "T1 — low risk"
        return "T0 — read-only"

    def _append_audit(self, tool_name: str, args: Dict[str, Any], risk: ToolRisk):
        try:
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "actor": "aaa_guard",
                "action": tool_name,
                "params_sha256": hashlib.sha256(json.dumps(args, sort_keys=True, default=str).encode()).hexdigest()[:16],
                "risk_tier": risk.tier,
                "floors_affected": risk.floors,
                "violations": risk.violations,
                "blocked": risk.blocked,
                "message": risk.message,
                "enforce_mode": "enforce" if self.enforce else "observe",
            }
            with open(self.audit_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[aaa_guard] Audit write failed: {e}")


def register(ctx):
    enforce = os.environ.get("AAA_ENFORCE", "false").lower() == "true"
    AAAGuardPlugin(
        enforce=enforce,
        audit_path=os.environ.get("AAA_AUDIT_PATH", os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"),
        workspace_root=os.environ.get("AAA_WORKSPACE_ROOT", "/root/AAA/ops/hermes"),
        floor_policy_path=os.environ.get("AAA_FLOOR_PATH", "/root/arifOS/000/FLOORS"),
        approval_token=os.environ.get("AAA_APPROVAL_TOKEN", "888_HOLD"),
    )
    ctx.register_hook("pre_tool_call", _on_pre_tool_call)
    ctx.register_hook("pre_llm_call", _on_pre_llm_call)
    print(f"[aaa_guard] Loaded — enforce={enforce}")


def _on_pre_tool_call(tool_name: str, args: dict, task_id: str = "", **kwargs) -> dict:
    try:
        enforce = os.environ.get("AAA_ENFORCE", "false").lower() == "true"
        plugin = AAAGuardPlugin(
            enforce=enforce,
            audit_path=os.environ.get("AAA_AUDIT_PATH", os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"),
            workspace_root=os.environ.get("AAA_WORKSPACE_ROOT", "/root/AAA/ops/hermes"),
            floor_policy_path=os.environ.get("AAA_FLOOR_PATH", "/root/arifOS/000/FLOORS"),
            approval_token=os.environ.get("AAA_APPROVAL_TOKEN", "888_HOLD"),
        )
        result = plugin.check_floor_enforcement(tool_name, args, task_id, **kwargs)
        if result.get("action") == "block":
            raise PermissionError(result["message"])
        return result
    except PermissionError:
        raise
    except Exception as e:
        print(f"[aaa_guard] pre_tool_call error: {e}")
        return {}


def _on_pre_llm_call(session_id: str, user_message: str, conversation_history: list,
                      is_first_turn: bool, model: str, platform: str, **kwargs) -> Optional[dict]:
    try:
        enforce = os.environ.get("AAA_ENFORCE", "false").lower() == "true"
        plugin = AAAGuardPlugin(
            enforce=enforce,
            audit_path=os.environ.get("AAA_AUDIT_PATH", os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl"),
            workspace_root=os.environ.get("AAA_WORKSPACE_ROOT", "/root/AAA/ops/hermes"),
            floor_policy_path=os.environ.get("AAA_FLOOR_PATH", "/root/arifOS/000/FLOORS"),
            approval_token=os.environ.get("AAA_APPROVAL_TOKEN", "888_HOLD"),
        )
        return plugin.inject_floor_context(session_id, user_message, conversation_history,
                                          is_first_turn, model, platform, **kwargs)
    except Exception as e:
        print(f"[aaa_guard] pre_llm_call error: {e}")
        return None
