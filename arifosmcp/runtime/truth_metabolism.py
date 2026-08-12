"""
arifOS E20 Truth Metabolism — Constitutional enforcement of CIV-21 §n
═════════════════════════════════════════════════════════════════════════════

"Truth claims expire and must be re-verified." — CIV-21 §n

FORGED: 2026-08-12 by 333-AGI under F13 SOVEREIGN directive
DOCTRINE: /root/AAA/canon/CIV-21.md §n
ALIGNMENT: /root/AAA/canon/GODEL_EUREKAS.md §E20 (Truth Has A Metabolism)

═══ PURPOSE ═══

Without this module:
    Claim → Verified once → Lives forever → Drifts silently

With this module:
    Claim → Verified → TTL → Re-contact reality → Renew / Stale / Revoke

This transforms truth from a static object into a metabolism.
Intelligence = reducing distance between belief and reality (E9).
If claims never expire, that distance grows without anyone noticing.

═══ INTERFACE ═══

    from arifosmcp.runtime.truth_metabolism import TruthMetabolism

    tm = TruthMetabolism()
    tm.register_claim("organs_alive", value=6, ttl_seconds=300)
    tm.register_claim("kernel_healthy", value=True, ttl_seconds=60)

    status = tm.check_claim("organs_alive")
    # status.state = "FRESH" | "STALE" | "EXPIRED" | "UNKNOWN"
    # status.age_seconds = 42
    # status.ttl_remaining = 258

═══ METABOLIC STATES ═══

    FRESH    — Claim verified recently. Within TTL. Can support SEAL.
    STALE    — Claim past 80% of TTL. Should be re-probed before SEAL.
    EXPIRED  — Claim past TTL. Cannot support SEAL without re-verification.
    UNKNOWN  — Claim never registered. No metabolic record.

═══ INTEGRATION ═══

    1. arif_judge calls tm.check_claim() for each claim supporting a SEAL.
    2. If any EXPIRED → judge must HOLD (claim no longer metabolically alive).
    3. If any STALE → judge should SABAR (re-probe before proceeding).
    4. C4 Reality Drift Gate can auto-renew claims by re-probing.

═══ F1 AMANAH ═══

    This module reads/writes to a local JSON file (default: /tmp/truth_metabolism.json).
    The file is a cache, not a ledger. It is safe to delete — claims simply
    become UNKNOWN, which triggers re-verification. Fully reversible.

DITEMPA BUKAN DIBERI — Forged, not given. ⚒️
"""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.truth_metabolism")

# ── Constitutional thresholds (frozen) ──────────────────────────────────────
DEFAULT_TTL_SECONDS = 300  # 5 minutes — reality changes fast
STALE_THRESHOLD = 0.8  # 80% of TTL consumed → STALE
MAX_TTL_SECONDS = 86400  # 24 hours — no claim lives longer than a day

# ── Storage ─────────────────────────────────────────────────────────────────
DEFAULT_STORE_PATH = "/tmp/truth_metabolism.json"


@dataclass
class ClaimStatus:
    """Metabolic status of a single truth claim."""

    claim_id: str
    state: str  # "FRESH" | "STALE" | "EXPIRED" | "UNKNOWN"
    value: Any
    age_seconds: float
    ttl_seconds: float
    ttl_remaining: float
    stale_ratio: float  # age / ttl — 0.0 = just registered, 1.0 = expired
    registered_at: str
    last_renewed_at: str

    @property
    def can_support_seal(self) -> bool:
        """A claim can support SEAL only if FRESH."""
        return self.state == "FRESH"

    @property
    def requires_reprobe(self) -> bool:
        """A claim requires re-probing if STALE or EXPIRED."""
        return self.state in ("STALE", "EXPIRED")


class TruthMetabolism:
    """
    E20 Truth Metabolism — TTL-based claim lifecycle manager.

    Claims are registered with a TTL. As time passes, claims move through
    metabolic states: FRESH → STALE → EXPIRED. Expired claims cannot support
    SEAL verdicts without re-verification.

    This is the mechanism that makes "truth has a metabolism" operational.
    """

    def __init__(self, store_path: str = DEFAULT_STORE_PATH) -> None:
        self.store_path = Path(store_path)
        self._claims: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load claims from disk. Failure = empty store (safe)."""
        try:
            if self.store_path.exists():
                data = json.loads(self.store_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self._claims = data
        except (json.JSONDecodeError, OSError) as exc:
            logger.debug("Failed to load truth metabolism store: %s", exc)
            self._claims = {}

    def _save(self) -> None:
        """Persist claims to disk. Failure = warning, not fatal."""
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            self.store_path.write_text(
                json.dumps(self._claims, indent=2, default=str),
                encoding="utf-8",
            )
        except OSError as exc:
            logger.warning("Failed to save truth metabolism store: %s", exc)

    def register_claim(
        self,
        claim_id: str,
        value: Any,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        source: str = "",
    ) -> ClaimStatus:
        """
        Register or renew a truth claim with a TTL.

        Args:
            claim_id: Unique identifier for the claim (e.g., "organs_alive").
            value: The claimed value.
            ttl_seconds: Time-to-live in seconds. Clamped to [1, MAX_TTL_SECONDS].
            source: Provenance — who/what verified this claim.

        Returns:
            ClaimStatus reflecting the FRESH state.
        """
        ttl = max(1, min(ttl_seconds, MAX_TTL_SECONDS))
        now = time.time()
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))

        self._claims[claim_id] = {
            "value": value,
            "ttl_seconds": ttl,
            "registered_at": now_iso,
            "last_renewed_at": now_iso,
            "registered_epoch": now,
            "source": source,
        }
        self._save()

        logger.debug("Claim registered: %s ttl=%ds source=%s", claim_id, ttl, source)
        return self.check_claim(claim_id)

    def renew_claim(self, claim_id: str, value: Any | None = None) -> ClaimStatus | None:
        """
        Renew an existing claim without changing its TTL.
        Optionally update the value.
        """
        if claim_id not in self._claims:
            return None

        if value is not None:
            self._claims[claim_id]["value"] = value

        now = time.time()
        self._claims[claim_id]["last_renewed_at"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)
        )
        self._claims[claim_id]["registered_epoch"] = now
        self._save()

        return self.check_claim(claim_id)

    def check_claim(self, claim_id: str) -> ClaimStatus:
        """
        Check the metabolic state of a claim.

        Returns ClaimStatus with state FRESH | STALE | EXPIRED | UNKNOWN.
        """
        if claim_id not in self._claims:
            return ClaimStatus(
                claim_id=claim_id,
                state="UNKNOWN",
                value=None,
                age_seconds=float("inf"),
                ttl_seconds=0,
                ttl_remaining=0,
                stale_ratio=float("inf"),
                registered_at="",
                last_renewed_at="",
            )

        claim = self._claims[claim_id]
        now = time.time()
        registered_epoch = claim.get("registered_epoch", now)
        ttl = claim.get("ttl_seconds", DEFAULT_TTL_SECONDS)
        age = now - registered_epoch
        stale_ratio = age / max(ttl, 1)
        ttl_remaining = max(0, ttl - age)

        if stale_ratio >= 1.0:
            state = "EXPIRED"
        elif stale_ratio >= STALE_THRESHOLD:
            state = "STALE"
        else:
            state = "FRESH"

        return ClaimStatus(
            claim_id=claim_id,
            state=state,
            value=claim.get("value"),
            age_seconds=age,
            ttl_seconds=ttl,
            ttl_remaining=ttl_remaining,
            stale_ratio=stale_ratio,
            registered_at=claim.get("registered_at", ""),
            last_renewed_at=claim.get("last_renewed_at", ""),
        )

    def get_expired_claims(self) -> list[str]:
        """Return list of claim IDs that are EXPIRED."""
        return [cid for cid in self._claims if self.check_claim(cid).state == "EXPIRED"]

    def get_stale_claims(self) -> list[str]:
        """Return list of claim IDs that are STALE (need re-probe soon)."""
        return [cid for cid in self._claims if self.check_claim(cid).state == "STALE"]

    def metabolic_sweep(self) -> dict[str, Any]:
        """
        Sweep all claims and return metabolic summary.

        This is the "metabolism" — the system checking which truths are
        still alive and which have decayed.
        """
        states = {"FRESH": 0, "STALE": 0, "EXPIRED": 0, "UNKNOWN": 0}
        for cid in self._claims:
            status = self.check_claim(cid)
            states[status.state] += 1

        return {
            "total_claims": len(self._claims),
            "fresh": states["FRESH"],
            "stale": states["STALE"],
            "expired": states["EXPIRED"],
            "unknown": states["UNKNOWN"],
            "metabolic_health": (
                "OPTIMAL"
                if states["EXPIRED"] == 0 and states["STALE"] == 0
                else "DEGRADED"
                if states["EXPIRED"] == 0
                else "CRITICAL"
            ),
            "swept_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def purge_expired(self) -> int:
        """Remove all EXPIRED claims from the store. Returns count purged."""
        expired = self.get_expired_claims()
        for cid in expired:
            del self._claims[cid]
        if expired:
            self._save()
        return len(expired)


# ── Constitutional integration hook ─────────────────────────────────────────


def truth_metabolism_for_judge(claim_ids: list[str], session_id: str = "") -> dict[str, Any]:
    """
    Integration point for arif_judge pre-verdict.

    Check all claims that support a SEAL verdict. If any are EXPIRED →
    judge should HOLD. If any are STALE → judge should SABAR.

    Returns dict for attachment to judge evidence bundle.
    """
    tm = TruthMetabolism()
    results: list[dict[str, Any]] = []
    has_expired = False
    has_stale = False

    for cid in claim_ids:
        status = tm.check_claim(cid)
        results.append(
            {
                "claim_id": cid,
                "state": status.state,
                "age_seconds": round(status.age_seconds, 1),
                "ttl_remaining": round(status.ttl_remaining, 1),
                "can_support_seal": status.can_support_seal,
            }
        )
        if status.state == "EXPIRED":
            has_expired = True
        elif status.state == "STALE":
            has_stale = True

    recommendation = "PROCEED"
    if has_expired:
        recommendation = "HOLD"  # expired claims → cannot SEAL
    elif has_stale:
        recommendation = "SABAR"  # stale claims → re-probe before SEAL

    return {
        "truth_metabolism": {
            "claims": results,
            "recommendation": recommendation,
            "has_expired": has_expired,
            "has_stale": has_stale,
            "session_id": session_id,
        }
    }


# ═══ END — DITEMPA BUKAN DIBERI ⚒️ ═══
