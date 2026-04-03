"""
APEX Structured Communication Format v1.0 (ASF-1)

Implementation for Agent ↔ Agent, Agent ↔ Human, Hybrid communication.

Usage:
    from asf1 import ASF1Message, CommunicationMode, SafetyStatus
    
    msg = ASF1Message.hybrid(
        to="arif_fazil",
        title="Prospect Evaluation",
        context={"situation": "seal_unverified"},
        decision_vector=DecisionVector(emv=0.65, npv_safety=0.72, entropy_delta=-0.12),
        next_actions=[Action("run_model", emv_contribution=0.15)],
    )
    
    print(msg.human_layer())
    print(msg.machine_layer())

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

ASF_VERSION = "1.0"
MACHINE_SEPARATOR = "---MACHINE---"
END_MACHINE = "---END MACHINE---"


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class CommunicationMode(Enum):
    INFORM = "inform"
    EVALUATE = "evaluate"
    DECIDE = "decide"
    ESCALATE = "escalate"
    SIMULATE = "simulate"
    EXECUTE = "execute"


class SafetyStatus(Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TruthTag(Enum):
    CLAIM = "CLAIM"           # ≥0.95 confidence
    PLAUSIBLE = "PLAUSIBLE"   # 0.70-0.94
    ESTIMATE = "ESTIMATE"     # 0.50-0.69
    UNKNOWN = "UNKNOWN"       # <0.50


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DecisionVector:
    """
    Thermodynamic + financial governance metrics.
    
    All values in [0, 1] except entropy_delta which can be negative.
    """
    emv: float                    # Expected Monetary Value
    npv_safety: float             # Downside protection
    entropy_delta: float          # F4 Clarity (≤ 0 is good)
    safety: SafetyStatus = SafetyStatus.GREEN
    
    def __post_init__(self):
        assert 0.0 <= self.emv <= 1.0, "EMV must be in [0, 1]"
        assert 0.0 <= self.npv_safety <= 1.0, "NPV Safety must be in [0, 1]"


@dataclass(frozen=True)
class Action:
    """
    Next action with governance constraints.
    
    All actions must:
    - Increase EMV
    - Protect NPV (safety_invariant)
    - Reduce or maintain entropy (entropy_delta ≤ 0)
    """
    action: str
    rationale: str = ""
    emv_contribution: float = 0.0
    safety_invariant: bool = True
    cost: float | None = None
    entropy_delta: float = 0.0
    
    def __post_init__(self):
        assert self.emv_contribution >= 0, "Action must increase EMV"
        assert self.entropy_delta <= 0, "Action must not increase entropy"


@dataclass(frozen=True)
class ConstitutionalStatus:
    """Floor compliance status."""
    floors_checked: list[str] = field(default_factory=list)
    f1_reversible: bool = True
    f9_clean: bool = True
    f12_guard_active: bool = True
    omega_band: str = "[0.03-0.05]"


@dataclass(frozen=True)
class Request:
    """Response requirement."""
    type: Literal["approval", "input", "execution", "notification"]
    deadline: datetime | None = None
    required_response: bool = True
    budget_request: float | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN MESSAGE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ASF1Message:
    """
    APEX Structured Communication Format message.
    
    Can generate both human-readable and machine-readable layers.
    """
    
    # Header
    to: str
    title: str
    mode: CommunicationMode
    cc: list[str] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    message_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Content
    context: dict[str, Any] = field(default_factory=dict)
    decision_vector: DecisionVector | None = None
    next_actions: list[Action] = field(default_factory=list)
    constitutional_status: ConstitutionalStatus = field(default_factory=ConstitutionalStatus)
    request: Request | None = None
    
    # Tags (for agent→agent advanced)
    tags: dict[TruthTag, list[str]] = field(default_factory=dict)
    
    # Format type
    format_type: Literal["HUMAN", "MACHINE", "HYBRID"] = "HYBRID"
    
    @classmethod
    def human_only(
        cls,
        to: str,
        title: str,
        context: dict[str, Any],
        **kwargs
    ) -> ASF1Message:
        """Create human-only message (narrative layer only)."""
        return cls(
            to=to,
            title=title,
            mode=CommunicationMode.INFORM,
            context=context,
            format_type="HUMAN",
            **kwargs
        )
    
    @classmethod
    def machine_only(
        cls,
        to: str,
        title: str,
        mode: CommunicationMode,
        payload: dict[str, Any],
        **kwargs
    ) -> ASF1Message:
        """Create machine-only message (JSON payload only)."""
        return cls(
            to=to,
            title=title,
            mode=mode,
            context=payload.get("context", {}),
            decision_vector=payload.get("decision_vector"),
            next_actions=payload.get("next_actions", []),
            format_type="MACHINE",
            **kwargs
        )
    
    @classmethod
    def hybrid(
        cls,
        to: str,
        title: str,
        mode: CommunicationMode,
        context: dict[str, Any],
        decision_vector: DecisionVector,
        next_actions: list[Action],
        **kwargs
    ) -> ASF1Message:
        """Create hybrid message (both layers)."""
        return cls(
            to=to,
            title=title,
            mode=mode,
            context=context,
            decision_vector=decision_vector,
            next_actions=next_actions,
            format_type="HYBRID",
            **kwargs
        )
    
    # ═════════════════════════════════════════════════════════════════════════
    # HUMAN LAYER GENERATION
    # ═════════════════════════════════════════════════════════════════════════
    
    def human_layer(self) -> str:
        """Generate human-readable narrative layer."""
        if self.format_type == "MACHINE":
            return ""
        
        lines = [
            "═══════════════════════════════════════════════════════════════",
            f"TO: {self.to}",
        ]
        
        if self.cc:
            lines.append(f"CC: {', '.join(self.cc)}")
        
        lines.extend([
            f"TITLE: {self.title}",
            "",
            f"MODE: {self.mode.value}",
            "",
            "KEY CONTEXT:",
        ])
        
        # Context bullets
        for key, value in self.context.items():
            if isinstance(value, list):
                for item in value:
                    lines.append(f"• {item}")
            else:
                lines.append(f"• {key}: {value}")
        
        # Decision vector
        if self.decision_vector:
            dv = self.decision_vector
            emv_label = "High" if dv.emv > 0.7 else "Medium" if dv.emv > 0.5 else "Low"
            npv_label = "Strong" if dv.npv_safety > 0.8 else "Moderate" if dv.npv_safety > 0.6 else "Weak"
            entropy_icon = "↓" if dv.entropy_delta < 0 else "→" if dv.entropy_delta == 0 else "↑"
            entropy_label = "reducing" if dv.entropy_delta < 0 else "stable" if dv.entropy_delta == 0 else "increasing"
            safety_emoji = "🟢" if dv.safety == SafetyStatus.GREEN else "🟡" if dv.safety == SafetyStatus.AMBER else "🔴"
            
            lines.extend([
                "",
                "DECISION VECTOR:",
                f"├─ EMV: {emv_label} — Expected value of proposed path",
                f"├─ NPV Safety: {npv_label} — Downside protection",
                f"├─ Entropy: {entropy_icon} {entropy_label} — Clarity trend",
                f"└─ Safety: {safety_emoji} {dv.safety.value.upper()} — Hard constraint status",
            ])
        
        # Next actions
        if self.next_actions:
            lines.extend([
                "",
                "NEXT ACTIONS (Forward Path):",
            ])
            for i, action in enumerate(self.next_actions, 1):
                cost_str = f" [${action.cost:,.0f}]" if action.cost else ""
                lines.append(f"{i}. {action.action}{cost_str}")
                if action.rationale:
                    lines.append(f"   Rationale: {action.rationale}")
        
        # Request
        if self.request:
            lines.extend([
                "",
                f"REQUEST: {self.request.type.upper()}",
            ])
            if self.request.budget_request:
                lines.append(f"Budget: ${self.request.budget_request:,.0f}")
            if self.request.deadline:
                deadline_str = self.request.deadline.strftime("%Y-%m-%d")
                lines.append(f"Deadline: {deadline_str}")
        
        lines.append("═══════════════════════════════════════════════════════════════")
        
        return "\n".join(lines)
    
    # ═════════════════════════════════════════════════════════════════════════
    # MACHINE LAYER GENERATION
    # ═════════════════════════════════════════════════════════════════════════
    
    def machine_layer(self) -> str:
        """Generate machine-readable JSON payload."""
        if self.format_type == "HUMAN":
            return ""
        
        payload = {
            "asf_version": ASF_VERSION,
            "header": {
                "to": self.to,
                "cc": self.cc,
                "title": self.title,
                "mode": self.mode.value,
                "timestamp": self.timestamp.isoformat(),
                "session_id": self.session_id,
                "message_id": self.message_id,
            },
            "context": self.context,
        }
        
        if self.decision_vector:
            payload["decision_vector"] = {
                "emv": self.decision_vector.emv,
                "npv_safety": self.decision_vector.npv_safety,
                "entropy_delta": self.decision_vector.entropy_delta,
                "safety": self.decision_vector.safety.value,
            }
        
        if self.next_actions:
            payload["next_actions"] = [
                {
                    "action": a.action,
                    "rationale": a.rationale,
                    "emv_contribution": a.emv_contribution,
                    "safety_invariant": a.safety_invariant,
                    "cost": a.cost,
                    "entropy_delta": a.entropy_delta,
                }
                for a in self.next_actions
            ]
        
        # Constitutional status
        payload["constitutional_status"] = {
            "floors_checked": self.constitutional_status.floors_checked,
            "f1_reversible": self.constitutional_status.f1_reversible,
            "f9_clean": self.constitutional_status.f9_clean,
            "f12_guard_active": self.constitutional_status.f12_guard_active,
            "omega_band": self.constitutional_status.omega_band,
        }
        
        if self.request:
            payload["request"] = {
                "type": self.request.type,
                "deadline": self.request.deadline.isoformat() if self.request.deadline else None,
                "required_response": self.request.required_response,
                "budget_request": self.request.budget_request,
            }
        
        # Tags
        if self.tags:
            payload["tags"] = {
                tag.value: items for tag, items in self.tags.items()
            }
        
        return json.dumps(payload, indent=2)
    
    # ═════════════════════════════════════════════════════════════════════════
    # FULL MESSAGE
    # ═════════════════════════════════════════════════════════════════════════
    
    def __str__(self) -> str:
        """Generate complete message based on format type."""
        if self.format_type == "HUMAN":
            return self.human_layer()
        elif self.format_type == "MACHINE":
            return self.machine_layer()
        else:  # HYBRID
            return f"{self.human_layer()}\n{MACHINE_SEPARATOR}\n{self.machine_layer()}\n{END_MACHINE}"
    
    # ═════════════════════════════════════════════════════════════════════════
    # PARSING
    # ═════════════════════════════════════════════════════════════════════════
    
    @classmethod
    def parse(cls, text: str) -> ASF1Message | None:
        """Parse an ASF-1 message from text."""
        if MACHINE_SEPARATOR in text:
            # Hybrid format
            parts = text.split(MACHINE_SEPARATOR)
            human_part = parts[0].strip()
            machine_part = parts[1].replace(END_MACHINE, "").strip()
            
            try:
                payload = json.loads(machine_part)
                return cls._from_payload(payload, "HYBRID")
            except json.JSONDecodeError:
                return None
        elif text.strip().startswith("{"):
            # Machine only
            try:
                payload = json.loads(text)
                return cls._from_payload(payload, "MACHINE")
            except json.JSONDecodeError:
                return None
        else:
            # Human only - can't fully parse without machine layer
            return None
    
    @classmethod
    def _from_payload(cls, payload: dict, format_type: str) -> ASF1Message:
        """Create message from parsed payload."""
        header = payload.get("header", {})
        
        # Parse decision vector
        dv_data = payload.get("decision_vector", {})
        decision_vector = None
        if dv_data:
            decision_vector = DecisionVector(
                emv=dv_data.get("emv", 0.5),
                npv_safety=dv_data.get("npv_safety", 0.5),
                entropy_delta=dv_data.get("entropy_delta", 0.0),
                safety=SafetyStatus(dv_data.get("safety", "green")),
            )
        
        # Parse actions
        actions_data = payload.get("next_actions", [])
        next_actions = [
            Action(
                action=a.get("action", ""),
                rationale=a.get("rationale", ""),
                emv_contribution=a.get("emv_contribution", 0.0),
                safety_invariant=a.get("safety_invariant", True),
                cost=a.get("cost"),
                entropy_delta=a.get("entropy_delta", 0.0),
            )
            for a in actions_data
        ]
        
        # Parse constitutional status
        cs_data = payload.get("constitutional_status", {})
        constitutional_status = ConstitutionalStatus(
            floors_checked=cs_data.get("floors_checked", []),
            f1_reversible=cs_data.get("f1_reversible", True),
            f9_clean=cs_data.get("f9_clean", True),
            f12_guard_active=cs_data.get("f12_guard_active", True),
            omega_band=cs_data.get("omega_band", "[0.03-0.05]"),
        )
        
        # Parse request
        req_data = payload.get("request", {})
        request = None
        if req_data:
            deadline = None
            if req_data.get("deadline"):
                deadline = datetime.fromisoformat(req_data["deadline"])
            request = Request(
                type=req_data.get("type", "notification"),
                deadline=deadline,
                required_response=req_data.get("required_response", True),
                budget_request=req_data.get("budget_request"),
            )
        
        return cls(
            to=header.get("to", ""),
            title=header.get("title", ""),
            mode=CommunicationMode(header.get("mode", "inform")),
            cc=header.get("cc", []),
            session_id=header.get("session_id", ""),
            message_id=header.get("message_id", ""),
            timestamp=datetime.fromisoformat(header.get("timestamp", datetime.now(timezone.utc).isoformat())),
            context=payload.get("context", {}),
            decision_vector=decision_vector,
            next_actions=next_actions,
            constitutional_status=constitutional_status,
            request=request,
            format_type=format_type,  # type: ignore
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "ASF1Message",
    "CommunicationMode",
    "SafetyStatus",
    "RiskLevel",
    "TruthTag",
    "DecisionVector",
    "Action",
    "ConstitutionalStatus",
    "Request",
    "ASF_VERSION",
    "MACHINE_SEPARATOR",
    "END_MACHINE",
]
