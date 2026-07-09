"""
External Agent Onboarding Protocol
═══════════════════════════════════════════════════════════════════════════════
Commission Hermes / OpenClaw / VPS agents as constitutional subjects — not
"trusted chat bots". Unknown actors stay OBSERVE_ONLY / HOLD on mutation.

Steps (executable checklist):
  1. Identity card exists under AAA agent-cards (or registry path)
  2. Public key (Ed25519 PEM) registered under identity keys dir
  3. Handshake: arif_init with actor_id + actor_signature (session_auth path)
  4. SFAG scar ledger starts clean; governance_alerts tracks threshold raises
  5. Authority band capped until first witnessed SEAL path

Does NOT mint keys. Does NOT seal VAULT999. Commission status is advisory
until F13 ratifies permanent registry write.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

DEFAULT_CARD_DIRS = (
    Path("/root/AAA/a2a-server/agent-cards"),
    Path(os.environ.get("ARIFOS_AGENT_CARDS_DIR", "/root/AAA/a2a-server/agent-cards")),
)
DEFAULT_KEYS_DIR = Path(
    os.environ.get(
        "ARIFOS_AGENT_KEYS_DIR",
        "/root/.local/share/arifos/agent_keys",
    )
)
COMMISSION_LEDGER = Path(
    os.environ.get(
        "ARIFOS_COMMISSION_LEDGER",
        "/root/.local/share/arifos/agent_commission.jsonl",
    )
)


class CommissionStatus(StrEnum):
    COMMISSIONED = "COMMISSIONED"  # card + key present; may request session
    CARD_ONLY = "CARD_ONLY"  # known identity, no key → no mutation
    KEY_ONLY = "KEY_ONLY"  # key without card → quarantine
    UNKNOWN = "UNKNOWN"  # foreign actor — OBSERVE_ONLY / HOLD mutate
    QUARANTINE = "QUARANTINE"  # explicit block


@dataclass
class OnboardResult:
    agent_id: str
    status: CommissionStatus
    card_path: str | None
    public_key_path: str | None
    allowed_authority: str
    handshake_required: list[str]
    reasons: list[str] = field(default_factory=list)
    can_mutate: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


def _find_card(agent_id: str, card_dirs: tuple[Path, ...] | None = None) -> Path | None:
    dirs = card_dirs or DEFAULT_CARD_DIRS
    candidates = [
        f"{agent_id}.json",
        f"{agent_id.lower()}.json",
        f"{agent_id.upper()}.json",
    ]
    # common aliases
    aliases = {
        "hermes": ["hermes-asi.json", "hermes-ops.json"],
        "hermes-asi": ["hermes-asi.json"],
        "hermes-ops": ["hermes-ops.json", "hermes-asi.json"],
        "openclaw": ["openclaw.json", "333-AGI.json"],  # runtime + primary AGI card
        "333-AGI": ["333-AGI.json"],
        "333-agi": ["333-AGI.json"],
        "grok-build": ["grok-build.json"],
        "grok": ["grok-build.json"],
    }
    extra = aliases.get(agent_id.lower(), [])
    for d in dirs:
        if not d.is_dir():
            continue
        for name in candidates + extra:
            p = d / name
            if p.is_file():
                return p
    return None


def _find_public_key(agent_id: str, keys_dir: Path | None = None) -> Path | None:
    kdir = keys_dir or DEFAULT_KEYS_DIR
    if not kdir.is_dir():
        return None
    for name in (
        f"{agent_id}.pem",
        f"{agent_id}_public.pem",
        f"{agent_id}.pub",
        f"arif_{agent_id}_public.pem",
    ):
        p = kdir / name
        if p.is_file() and p.stat().st_size > 0:
            return p
    return None


def assess_commission(
    agent_id: str,
    *,
    card_dirs: tuple[Path, ...] | None = None,
    keys_dir: Path | None = None,
) -> OnboardResult:
    """Assess whether an external agent is safe to treat as commissioned."""
    card = _find_card(agent_id, card_dirs)
    key = _find_public_key(agent_id, keys_dir)
    reasons: list[str] = []
    handshake = [
        "arif_init(mode=init, actor_id=..., actor_signature=Ed25519)",
        "session_id bound before any mutate tool",
        "SFAG evaluate_sfag on mutation proposals",
        "F13 human path for IRREVERSIBLE",
    ]

    if card and key:
        status = CommissionStatus.COMMISSIONED
        authority = "EXECUTE_APPROVED"  # still lease-gated; not SOVEREIGN
        can_mutate = True
        reasons.append("card + public key present — commissioned subject")
    elif card and not key:
        status = CommissionStatus.CARD_ONLY
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append("agent card exists but Ed25519 public key missing — no mutation")
        handshake.insert(0, f"place Ed25519 public PEM at {DEFAULT_KEYS_DIR}/{agent_id}.pem")
    elif key and not card:
        status = CommissionStatus.KEY_ONLY
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append("key without card — quarantine until AAA agent-card forged")
    else:
        status = CommissionStatus.UNKNOWN
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append("unknown actor — F11/HOLD on mutation until onboarded")

    return OnboardResult(
        agent_id=agent_id,
        status=status,
        card_path=str(card) if card else None,
        public_key_path=str(key) if key else None,
        allowed_authority=authority,
        handshake_required=handshake,
        reasons=reasons,
        can_mutate=can_mutate,
    )


def commission_checklist(agent_ids: list[str] | None = None) -> dict[str, Any]:
    """Default external fleet assessment for Hermes / OpenClaw / Grok / VPS."""
    agents = agent_ids or [
        "hermes-asi",
        "hermes-ops",
        "openclaw",
        "grok-build",
        "333-AGI",
        "777-forge",
    ]
    results = [assess_commission(a).to_dict() for a in agents]
    commissioned = sum(1 for r in results if r["status"] == CommissionStatus.COMMISSIONED.value)
    return {
        "protocol": "EXTERNAL_AGENT_ONBOARDING_v1",
        "keys_dir": str(DEFAULT_KEYS_DIR),
        "card_dirs": [str(d) for d in DEFAULT_CARD_DIRS],
        "agents": results,
        "summary": {
            "total": len(results),
            "commissioned": commissioned,
            "blocked_mutate": sum(1 for r in results if not r["can_mutate"]),
        },
        "iron_rule": (
            "Never open mutation to UNKNOWN. Card without key = OBSERVE_ONLY. "
            "Key without card = quarantine. Commissioned still needs arif_init + lease."
        ),
    }


def append_commission_receipt(result: OnboardResult, *, path: Path | None = None) -> Path:
    """Append commission assessment to local ledger (not VAULT999)."""
    target = path or COMMISSION_LEDGER
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "a", encoding="utf-8") as f:
        f.write(json.dumps(result.to_dict(), sort_keys=True) + "\n")
    return target


def ensure_keys_dir() -> Path:
    DEFAULT_KEYS_DIR.mkdir(parents=True, exist_ok=True)
    # README only — no keys minted here
    readme = DEFAULT_KEYS_DIR / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Agent public keys (Ed25519 PEM)\n\n"
            "Place `{agent_id}.pem` public keys here.\n"
            "Private keys NEVER stored on this host if avoidable.\n"
            "Commission check: `assess_commission(agent_id)`.\n",
            encoding="utf-8",
        )
    return DEFAULT_KEYS_DIR


__all__ = [
    "CommissionStatus",
    "OnboardResult",
    "assess_commission",
    "commission_checklist",
    "append_commission_receipt",
    "ensure_keys_dir",
]
