"""
External Agent Onboarding Protocol
═══════════════════════════════════════════════════════════════════════════════
Commission Hermes / OpenClaw / VPS agents as constitutional subjects — not
"trusted chat bots". Unknown actors stay OBSERVE_ONLY / HOLD on mutation.

Steps (executable checklist):
  1. Identity card exists under AAA agent-cards (or registry path)
  2. Public key (Ed25519 PEM) registered under identity keys dir
     — CONTENT-AWARE since 2026-10-29: the PEM must parse as an Ed25519
       SPKI public key, and when the card declares key material the raw
       key bytes must match. A correctly-named file of any content no
       longer buys EXECUTE_APPROVED (p1-commission-gate-content-aware).
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

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

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
    COMMISSIONED = "COMMISSIONED"  # card + VALID matching key; may request session
    CARD_ONLY = "CARD_ONLY"  # known identity, no key file → no mutation
    KEY_ONLY = "KEY_ONLY"  # valid key without card → quarantine
    KEY_INVALID = "KEY_INVALID"  # key file present but NOT a valid Ed25519 SPKI PEM
    KEY_MISMATCH = "KEY_MISMATCH"  # valid key, but ≠ card-declared registry key
    CARD_KEY_UNREADABLE = "CARD_KEY_UNREADABLE"  # card declares key that cannot load
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
    # Content-aware fields (2026-10-29). None = no key file (key_valid) /
    # no comparison possible (card_key_match: no key file OR card declares
    # no key material — registry check not applicable, not passed).
    key_valid: bool | None = None
    card_key_match: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


def _load_ed25519_public_key(path: Path) -> tuple[bytes | None, str]:
    """Parse a PEM file as an Ed25519 SPKI public key.

    Returns (raw32, reason). raw32 is None when the content does not
    constitute a valid Ed25519 public key; reason names the failure class.
    """
    try:
        blob = path.read_bytes()
    except OSError as exc:
        return None, f"key file unreadable: {exc.__class__.__name__}"
    if not blob.strip():
        return None, "key file is empty"
    try:
        parsed = serialization.load_pem_public_key(blob)
    except (ValueError, TypeError):
        return None, "content is not a parseable PEM public key"
    if not isinstance(parsed, Ed25519PublicKey):
        return None, "PEM parses but algorithm is not Ed25519"
    raw = parsed.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw, "valid Ed25519 SPKI PEM"


def _card_declared_key(card_path: Path) -> tuple[bytes | None, str | None]:
    """Extract the raw Ed25519 key bytes an agent card declares, if any.

    Returns (raw32, source). raw32 is None with source=None when the card
    declares no key material (registry check not applicable). When the card
    DOES declare key material but it cannot be loaded, raw32 is None and
    source names the failure (caller maps that to CARD_KEY_UNREADABLE).
    """
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if not isinstance(card, dict):
        return None, None
    pk = card.get("public_key")
    if not isinstance(pk, dict):
        return None, None
    hexval = str(pk.get("hex") or "").strip()
    if hexval:
        try:
            raw = bytes.fromhex(hexval)
        except ValueError:
            return None, "card public_key.hex is malformed hex"
        if len(raw) == 32:
            return raw, "card public_key.hex"
        return None, f"card public_key.hex wrong length ({len(raw)} bytes, want 32)"
    ref = str(pk.get("path") or "").strip()
    if ref:
        p = Path(ref)
        if not p.is_file():
            return None, f"card public_key.path does not exist: {ref}"
        raw, _reason = _load_ed25519_public_key(p)
        if raw is None:
            return None, f"card public_key.path is not a valid Ed25519 PEM: {ref}"
        return raw, f"card public_key.path {ref}"
    return None, None


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
    names = candidates + extra
    for d in dirs:
        if not d.is_dir():
            continue
        for name in names:
            p = d / name
            if p.is_file():
                return p
    # Nested registry layout (identity/, roles/, organs/, federation/,
    # extensions/) — discovered 2026-10-29: flat lookup alone never found
    # any card on this host, making the registry side of the gate dead.
    for d in dirs:
        if not d.is_dir():
            continue
        for name in names:
            matches = sorted(d.rglob(name))
            if matches:
                return matches[0]
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
    """Assess whether an external agent is safe to treat as commissioned.

    Content-aware since 2026-10-29: a key file must parse as an Ed25519
    SPKI public key (KEY_INVALID otherwise), and when the agent card
    declares key material the raw bytes must match (KEY_MISMATCH /
    CARD_KEY_UNREADABLE otherwise). Only card + valid matching key
    yields can_mutate=True.
    """
    card = _find_card(agent_id, card_dirs)
    key_path = _find_public_key(agent_id, keys_dir)
    reasons: list[str] = []
    handshake = [
        "arif_init(mode=init, actor_id=..., actor_signature=Ed25519)",
        "session_id bound before any mutate tool",
        "SFAG evaluate_sfag on mutation proposals",
        "F13 human path for IRREVERSIBLE",
    ]

    key_raw: bytes | None = None
    key_reason = ""
    if key_path is not None:
        key_raw, key_reason = _load_ed25519_public_key(key_path)

    card_raw: bytes | None = None
    card_key_src: str | None = None
    if card is not None:
        card_raw, card_key_src = _card_declared_key(card)

    key_valid: bool | None = None if key_path is None else key_raw is not None

    if card and key_path and key_raw is not None and card_key_src is None:
        status = CommissionStatus.COMMISSIONED
        authority = "EXECUTE_APPROVED"  # still lease-gated; not SOVEREIGN
        can_mutate = True
        reasons.append(
            "card present + valid Ed25519 SPKI key; card declares no key "
            "material — content gate only (registry match N/A)"
        )
        card_key_match: bool | None = None
    elif card and key_path and key_raw is not None and card_raw == key_raw:
        status = CommissionStatus.COMMISSIONED
        authority = "EXECUTE_APPROVED"  # still lease-gated; not SOVEREIGN
        can_mutate = True
        reasons.append(f"card + valid Ed25519 key matching registry ({card_key_src})")
        card_key_match = True
    elif card and key_path and key_raw is not None and card_raw is not None:
        # card_raw != key_raw necessarily (equality handled above)
        status = CommissionStatus.KEY_MISMATCH
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append(
            f"valid Ed25519 key but does NOT match card-declared key "
            f"({card_key_src}) — mutation blocked"
        )
        card_key_match = False
        handshake.insert(
            0,
            f"resolve key mismatch: keys-dir PEM ≠ card registry key ({card_key_src})",
        )
    elif card and key_path and key_raw is not None and card_key_src is not None:
        # valid key; card declared key material we could not load
        status = CommissionStatus.CARD_KEY_UNREADABLE
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append(
            f"card-declared key unreadable — mutation blocked ({card_key_src})"
        )
        card_key_match = None
        handshake.insert(0, f"repair card key reference ({card_key_src})")
    elif key_path and key_raw is None:
        status = CommissionStatus.KEY_INVALID
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append(
            f"key file present but content fails Ed25519 SPKI check "
            f"({key_reason}) — mutation blocked"
        )
        card_key_match = None
        handshake.insert(0, f"replace {key_path} with a valid Ed25519 SPKI public PEM")
    elif card and not key_path:
        status = CommissionStatus.CARD_ONLY
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append("agent card exists but Ed25519 public key missing — no mutation")
        handshake.insert(
            0, f"place Ed25519 public PEM at {DEFAULT_KEYS_DIR}/{agent_id}.pem"
        )
        card_key_match = None
    elif key_path:
        status = CommissionStatus.KEY_ONLY
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append(
            "valid key without card — quarantine until AAA agent-card forged"
        )
        card_key_match = None
    else:
        status = CommissionStatus.UNKNOWN
        authority = "OBSERVE_ONLY"
        can_mutate = False
        reasons.append("unknown actor — F11/HOLD on mutation until onboarded")
        card_key_match = None

    return OnboardResult(
        agent_id=agent_id,
        status=status,
        card_path=str(card) if card else None,
        public_key_path=str(key_path) if key_path else None,
        allowed_authority=authority,
        handshake_required=handshake,
        reasons=reasons,
        can_mutate=can_mutate,
        key_valid=key_valid,
        card_key_match=card_key_match,
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
    commissioned = sum(
        1 for r in results if r["status"] == CommissionStatus.COMMISSIONED.value
    )
    return {
        "protocol": "EXTERNAL_AGENT_ONBOARDING_v1",
        "content_gate": "ed25519-spki-v1",  # 2026-10-29: key content + registry match enforced
        "keys_dir": str(DEFAULT_KEYS_DIR),
        "card_dirs": [str(d) for d in DEFAULT_CARD_DIRS],
        "agents": results,
        "summary": {
            "total": len(results),
            "commissioned": commissioned,
            "blocked_mutate": sum(1 for r in results if not r["can_mutate"]),
            "key_invalid": sum(
                1 for r in results if r["status"] == CommissionStatus.KEY_INVALID.value
            ),
            "key_mismatch": sum(
                1 for r in results if r["status"] == CommissionStatus.KEY_MISMATCH.value
            ),
            "card_key_unreadable": sum(
                1
                for r in results
                if r["status"] == CommissionStatus.CARD_KEY_UNREADABLE.value
            ),
        },
        "iron_rule": (
            "Never open mutation to UNKNOWN. Card without key = OBSERVE_ONLY. "
            "Key without card = quarantine. Key file must PARSE as Ed25519 SPKI "
            "and MATCH the card registry when one is declared. Commissioned "
            "still needs arif_init + lease."
        ),
    }


def append_commission_receipt(
    result: OnboardResult, *, path: Path | None = None
) -> Path:
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
