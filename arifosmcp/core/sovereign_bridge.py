"""
arifOS Sovereign Fabric — /000 + /999 Bridge
═════════════════════════════════════════════

Wires the public /000 (Genesis) and /999 (Verification) surfaces
into the runtime Sovereign Fabric.

This is the bridge between "public-facing constitutional pages"
and "runtime governance enforcement."

/000 = Human Root — who the sovereign is, what doctrine governs
/999 = Verification Room — what is provably true, what keys are active

Every agent session loads this context. Every policy check references it.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────

_GENESIS_DIR = Path("/var/www/html/arif/000")
_VERIFICATION_DIR = Path("/var/www/html/arif/999")
_ARIFOS_STATIC = Path("/root/arifOS/static/arifos")


# ── Sovereign Anchor (/000) ────────────────────────────────────────────


@dataclass
class SovereignAnchor:
    """
    The human root — loaded from /000/genesis-statement.json.
    This is the constitutional anchor that prevents self-authorization.
    """

    human_name: str = ""
    did: str = ""
    root_domain: str = ""
    root_key_id: str = ""
    statement_summary: str = ""
    statement_full: str = ""
    evidence_proves: list[str] = field(default_factory=list)
    evidence_does_not_prove: list[str] = field(default_factory=list)
    wisdom_laws: list[dict[str, str]] = field(default_factory=list)
    loaded_at: float = 0.0
    source: str = ""

    def is_loaded(self) -> bool:
        return bool(self.human_name and self.did)

    def to_context_dict(self) -> dict[str, Any]:
        """Compact dict for injection into agent context."""
        return {
            "sovereign": self.human_name,
            "did": self.did,
            "domain": self.root_domain,
            "statement": self.statement_summary,
            "evidence_boundary": {
                "proves": self.evidence_proves,
                "does_not_prove": self.evidence_does_not_prove,
            },
        }


# ── Verification State (/999) ─────────────────────────────────────────


@dataclass
class VerificationState:
    """
    The evidence room — loaded from /999/ surfaces.
    What is provably true right now.
    """

    did: str = ""
    did_status: str = ""  # VERIFIED / UNVERIFIED
    public_key_fingerprint: str = ""
    verification_method: str = ""
    seal_id: str = ""
    seal_status: str = ""  # active / revoked
    seal_scope: list[str] = field(default_factory=list)
    vault_epoch: str = ""
    key_rotation_date: str = ""
    runtime_snapshot_hash: str = ""
    active_holds: list[str] = field(default_factory=list)
    loaded_at: float = 0.0
    source: str = ""

    def is_loaded(self) -> bool:
        return bool(self.did and self.did_status)

    def is_seal_active(self) -> bool:
        return self.seal_status == "active"

    def to_context_dict(self) -> dict[str, Any]:
        """Compact dict for injection into agent context."""
        return {
            "did_status": self.did_status,
            "seal_status": self.seal_status,
            "seal_scope": self.seal_scope,
            "key_fingerprint": self.public_key_fingerprint[:16] + "...",
            "active_holds": len(self.active_holds),
        }


# ── Loaders ────────────────────────────────────────────────────────────


def load_sovereign_anchor() -> SovereignAnchor:
    """Load /000 genesis statement into a SovereignAnchor."""
    anchor = SovereignAnchor(source="https://arif-fazil.com/000/", loaded_at=time.time())

    genesis_path = _GENESIS_DIR / "genesis-statement.json"
    if not genesis_path.exists():
        logger.warning(f"Genesis statement not found: {genesis_path}")
        return anchor

    try:
        data = json.loads(genesis_path.read_text())
        human = data.get("human", {})
        anchor.human_name = human.get("name", "")
        anchor.did = human.get("did", "")
        anchor.root_domain = human.get("root_domain", "")
        anchor.root_key_id = human.get("root_key", "")

        statement = data.get("statement", {})
        anchor.statement_summary = statement.get("summary", "")
        anchor.statement_full = statement.get("full_text", "")

        evidence = data.get("evidence_scope", {})
        anchor.evidence_proves = evidence.get("proves", [])
        anchor.evidence_does_not_prove = evidence.get("does_not_prove", [])

        laws = data.get("wisdom_laws", {})
        for law in laws.get("field_laws", []):
            anchor.wisdom_laws.append(
                {
                    "id": law.get("id", ""),
                    "title": law.get("title", ""),
                    "meaning": law.get("meaning", ""),
                }
            )

        logger.info(f"Sovereign anchor loaded: {anchor.human_name} ({anchor.did})")
    except Exception as e:
        logger.error(f"Failed to load genesis statement: {e}")

    return anchor


def load_verification_state() -> VerificationState:
    """Load /999 verification surfaces into a VerificationState."""
    state = VerificationState(source="https://arif-fazil.com/999/", loaded_at=time.time())

    # DID status
    did_path = _VERIFICATION_DIR / "did-status.json"
    if did_path.exists():
        try:
            data = json.loads(did_path.read_text())
            state.did = data.get("did", "")
            state.did_status = data.get("id_check", "")
            state.public_key_fingerprint = data.get("public_key_fingerprint", "")
            state.verification_method = data.get("verification_method_id", "")
        except Exception as e:
            logger.error(f"Failed to load DID status: {e}")

    # Seal
    seal_path = _VERIFICATION_DIR / "seal.json"
    if seal_path.exists():
        try:
            data = json.loads(seal_path.read_text())
            state.seal_id = data.get("seal_id", "")
            state.seal_status = data.get("status", "")
            state.seal_scope = data.get("scope", [])
        except Exception as e:
            logger.error(f"Failed to load seal: {e}")

    # Runtime snapshot hash
    snapshot_path = _VERIFICATION_DIR / "runtime-snapshot.sha256"
    if snapshot_path.exists():
        try:
            state.runtime_snapshot_hash = snapshot_path.read_text().strip()
        except Exception:
            pass

    # Key rotation
    key_path = _VERIFICATION_DIR / "key-rotation-2026-05-03.json"
    if key_path.exists():
        try:
            data = json.loads(key_path.read_text())
            state.key_rotation_date = data.get("rotated_at", "")
        except Exception:
            pass

    # Active holds
    hold_path = _VERIFICATION_DIR / "888-hold-list.md"
    if hold_path.exists():
        try:
            content = hold_path.read_text()
            # Parse hold items (lines starting with -)
            state.active_holds = [
                line.strip("- ").strip()
                for line in content.split("\n")
                if line.strip().startswith("-") and line.strip() != "-"
            ]
        except Exception:
            pass

    logger.info(f"Verification state loaded: DID={state.did_status}, Seal={state.seal_status}")
    return state


# ── Sovereign Context (combined) ───────────────────────────────────────


@dataclass
class SovereignContext:
    """
    Combined /000 + /999 context — loaded once per session.
    This is what every agent sees when it asks "who governs me and what is true."
    """

    anchor: SovereignAnchor = field(default_factory=SovereignAnchor)
    verification: VerificationState = field(default_factory=VerificationState)
    loaded_at: float = 0.0

    def is_complete(self) -> bool:
        """Both /000 and /999 loaded successfully."""
        return self.anchor.is_loaded() and self.verification.is_loaded()

    def to_agent_context(self) -> dict[str, Any]:
        """
        Compact dict suitable for injection into agent prompts.
        This is what goes into the agent's context window.
        """
        return {
            "sovereign_anchor": self.anchor.to_context_dict(),
            "verification_state": self.verification.to_context_dict(),
            "constitutional_hash": "arifos-constitution-v2026.05.05-SSCT",
            "governance_note": "Human judgment remains final. AI is an instrument. Verify before acting.",
        }

    def assert_sovereignty(self) -> tuple[bool, str]:
        """
        Pre-flight check: is the sovereign anchor valid?
        Returns (ok, reason).
        """
        if not self.anchor.is_loaded():
            return False, "Sovereign anchor not loaded — /000 unavailable"
        if not self.anchor.did:
            return False, "No DID in sovereign anchor — identity unverifiable"
        if not self.verification.is_loaded():
            return False, "Verification state not loaded — /999 unavailable"
        if not self.verification.is_seal_active():
            return False, f"Federation seal is {self.verification.seal_status} — not active"
        if self.verification.did_status != "VERIFIED":
            return False, f"DID status is {self.verification.did_status} — not verified"
        return True, "Sovereignty verified — /000 anchor + /999 evidence valid"


# ── Singleton ──────────────────────────────────────────────────────────

_context: Optional[SovereignContext] = None


def get_sovereign_context(force_reload: bool = False) -> SovereignContext:
    """Get or load the sovereign context (singleton)."""
    global _context
    if _context is None or force_reload:
        anchor = load_sovereign_anchor()
        verification = load_verification_state()
        _context = SovereignContext(
            anchor=anchor,
            verification=verification,
            loaded_at=time.time(),
        )
    return _context
