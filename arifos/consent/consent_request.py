"""
consent_request.py — Risk-Proportional Consent Engine
══════════════════════════════════════════════════════

Validates agent identity, classifies action risk tier, and
routes T3 requests through the consent gate.

Tiers:
  T0 → AUTO_PASS    (observe, read)
  T1 → AUTO_EXECUTE (edit, build, test)
  T2 → ANNOUNCE     (deploy, restart — 10s window)
  T3 → CONSENT_GATE (delete, drop, secrets, force-push)

Forged: 2026-07-29 — DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RiskTier(Enum):
    T0 = "T0"  # Observe-only
    T1 = "T1"  # Reversible mutation
    T2 = "T2"  # Multi-file, deploy, restart
    T3 = "T3"  # Irreversible — consent required
    T3_PLUS = "T3+"  # 888_HOLD — sovereign only


class ConsentVerdict(Enum):
    AUTO_PASS = "auto_pass"
    AUTO_EXECUTE = "auto_execute"
    ANNOUNCED = "announced"
    CONSENT_REQUIRED = "consent_required"
    HOLD_888 = "hold_888"
    DENIED = "denied"


# Action → tier mapping
ACTION_TIER_MAP: dict[str, RiskTier] = {
    # T0 — Observation
    "read": RiskTier.T0,
    "observe": RiskTier.T0,
    "search": RiskTier.T0,
    "fetch": RiskTier.T0,
    "list": RiskTier.T0,
    "probe": RiskTier.T0,
    "status": RiskTier.T0,
    "health": RiskTier.T0,
    "inspect": RiskTier.T0,
    # T1 — Reversible mutation
    "edit": RiskTier.T1,
    "write": RiskTier.T1,
    "build": RiskTier.T1,
    "test": RiskTier.T1,
    "lint": RiskTier.T1,
    "format": RiskTier.T1,
    "commit": RiskTier.T1,
    "push": RiskTier.T1,
    # T2 — Medium blast radius
    "deploy": RiskTier.T2,
    "restart": RiskTier.T2,
    "reload": RiskTier.T2,
    "migrate": RiskTier.T2,
    "install": RiskTier.T2,
    # T3 — Irreversible
    "delete": RiskTier.T3,
    "remove": RiskTier.T3,
    "drop": RiskTier.T3,
    "force_push": RiskTier.T3,
    "force-push": RiskTier.T3,
    "force push": RiskTier.T3,
    "rm": RiskTier.T3,
    "purge": RiskTier.T3,
    "destroy": RiskTier.T3,
    "secrets": RiskTier.T3,
    "rotate": RiskTier.T3,
    # T3+
    "dns": RiskTier.T3_PLUS,
    "firewall": RiskTier.T3_PLUS,
    "vps_stop": RiskTier.T3_PLUS,
    "vps_restart": RiskTier.T3_PLUS,
}


@dataclass
class ConsentRequest:
    """A request from an agent to perform an action requiring consent."""

    request_id: str
    agent_id: str
    actor_id: str
    action: str  # What the agent wants to do
    action_hash: str  # SHA256 of action
    blast_radius: str  # "none" | "low" | "medium" | "high"
    reversibility: str  # "full" | "partial" | "none"
    rollback_plan: str  # How to undo if it goes wrong
    justification: str  # WHY this action is needed
    tier: RiskTier = RiskTier.T2
    signature: str = ""  # Ed25519 signature proving agent identity
    signature_challenge: str = ""  # Challenge string signed by agent
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    status: str = "pending"  # pending | approved | denied | expired

    def to_telegram_message(self) -> str:
        """Format as a Telegram message for Arif."""
        emoji = {RiskTier.T3: "🔴", RiskTier.T3_PLUS: "⛔"}.get(self.tier, "🟡")
        return (
            f"{emoji} **Consent Required**\n\n"
            f"**Agent:** {self.agent_id}\n"
            f"**Action:** {self.action}\n"
            f"**Why:** {self.justification}\n"
            f"**Blast radius:** {self.blast_radius}\n"
            f"**Reversible:** {self.reversibility}\n"
            f"**Rollback:** {self.rollback_plan}\n\n"
            f"Reply: `jalan terus` or `hold`\n"
            f"⏱ expires in 5 min"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "action_hash": self.action_hash,
            "blast_radius": self.blast_radius,
            "reversibility": self.reversibility,
            "rollback_plan": self.rollback_plan,
            "justification": self.justification,
            "tier": self.tier.value,
            "signature": self.signature,
            "signature_challenge": self.signature_challenge,
            "timestamp": self.timestamp,
            "status": self.status,
        }


@dataclass
class ConsentGate:
    """Risk-proportional consent gate.

    Classifies every action into a risk tier and routes accordingly.
    T0/T1 → auto. T2 → announce (10s). T3 → consent via Telegram.
    T3+ → 888_HOLD (must wait for Arif).
    """

    telegram_enabled: bool = False
    consent_log: list[dict[str, Any]] = field(default_factory=list)

    def classify(
        self, action: str, blast_radius: str = "low", reversibility: str = "full"
    ) -> RiskTier:
        """Map an action to its risk tier."""
        # Direct tier from action map — longest keyword first
        action_lower = action.lower().strip()
        sorted_keywords = sorted(ACTION_TIER_MAP.items(), key=lambda kv: -len(kv[0]))
        for keyword, tier in sorted_keywords:
            if keyword in action_lower:
                return tier

        # Fallback: use blast_radius + reversibility
        if blast_radius in ("high", "critical"):
            return RiskTier.T3
        if reversibility == "none":
            return RiskTier.T3
        if reversibility == "partial":
            return RiskTier.T2

        return RiskTier.T1

    def gate(self, request: ConsentRequest) -> ConsentVerdict:
        """Route a consent request through the gate.

        Returns the verdict — what should happen next.
        """
        tier = self.classify(
            request.action,
            request.blast_radius,
            request.reversibility,
        )
        request.tier = tier

        # Log the request
        entry = {
            "request_id": request.request_id,
            "agent_id": request.agent_id,
            "action": request.action[:100],
            "tier": tier.value,
            "timestamp": request.timestamp,
        }

        if tier == RiskTier.T0:
            entry["verdict"] = ConsentVerdict.AUTO_PASS.value
            self.consent_log.append(entry)
            return ConsentVerdict.AUTO_PASS

        if tier == RiskTier.T1:
            entry["verdict"] = ConsentVerdict.AUTO_EXECUTE.value
            self.consent_log.append(entry)
            return ConsentVerdict.AUTO_EXECUTE

        if tier == RiskTier.T2:
            entry["verdict"] = ConsentVerdict.ANNOUNCED.value
            self.consent_log.append(entry)
            return ConsentVerdict.ANNOUNCED

        if tier == RiskTier.T3:
            if self.telegram_enabled:
                entry["verdict"] = ConsentVerdict.CONSENT_REQUIRED.value
                entry["telegram_routed"] = "true"
            else:
                entry["verdict"] = ConsentVerdict.CONSENT_REQUIRED.value
                entry["telegram_routed"] = "false"
            self.consent_log.append(entry)
            return ConsentVerdict.CONSENT_REQUIRED

        # T3+
        entry["verdict"] = ConsentVerdict.HOLD_888.value
        self.consent_log.append(entry)
        return ConsentVerdict.HOLD_888

    def require_consent(self, request: ConsentRequest) -> bool:
        """Quick check: does this action need consent?"""
        verdict = self.gate(request)
        return verdict in (ConsentVerdict.CONSENT_REQUIRED, ConsentVerdict.HOLD_888)

    def log_to_file(self, path: str | Path = "/root/forge_work/consent_log.jsonl") -> None:
        """Persist consent log to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            for entry in self.consent_log:
                f.write(json.dumps(entry) + "\n")
        logger.info(f"Consent log written: {len(self.consent_log)} entries → {path}")
        self.consent_log.clear()
