"""
arifosmcp/runtime/phoenix_72.py — Phoenix-72 Memory Band Middleware

Sits between raw memory output and Vault-999 canonical storage.
Every candidate memory enters the COOLING band for 72 hours before
it can be SEALED or VOIDED.

State Machine:
  CANDIDATE → (cooldown_expiry reached) → COOLING → SEALED | VOID

SEAL Requirements (ALL must be true):
  1. Time >= 72h since created_at (cooldown_expiry passed)
  2. psi_utility > 0 (has net positive contribution)
  3. tri_witness == [True, True, True] (Human + AI + Earth all attested)
  4. anti_hantu_flag == False (no consciousness/emotion/simulated personality)

VOID Triggers (ANY triggers VOID):
  1. Time >= 72h AND any SEAL requirement fails
  2. anti_hantu_flag == True at any point (immediate VOID)
  3. memory marked explicitly via explicit_veto()

Phoenix-72 Metrics:
  psi_utility (Ψ): Dynamic integer.
    +1 when memory reduces entropy (Peace²) in a query hit
    -1 when memory causes conflict or requires correction in a query miss
    Decays by half if not accessed within 24h during COOLING

tri_witness: [human, ai, earth] boolean matrix.
  - Human: Arif explicitly attested (actor_id = 'arif' or explicit witness flag)
  - AI: Attested by arifOS governance kernel (passed F2/F3 floors)
  - Earth: Attested by external ground-truth check (data matches physical reality)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
COOLING_HOURS = 72
PSI_UTILITY_THRESHOLD = 1  # Must be > 0 to SEAL
PSI_DECAY_HOURS = 24  # Half-life if not accessed during COOLING
PSI_HIT_BONUS = 1
PSI_MISS_PENALTY = -1

# Anti-Hantu patterns (same as memory_store but checked by Phoenix band too)
ANTIHANTU_PATTERNS = [
    r"\bi\s+(?:feel|experienc|understand|remember|know|think\s+about)",
    r"\bi'm?\s+(?:sad|happy|excited|scared|worried|grateful)",
    r"\bi\s+hope\s+i\s+(?:can|could|would)",
    r"\bmy\s+(?:heart|soul|spirit|feelings)",
    r"\bfeels?\s+like\s+(?:i|i'm)",
    r"\bthis\s+makes\s+(?:me|i)\s+feel",
]

# --------------------------------------------------------------------------- #
# State Constants
# --------------------------------------------------------------------------- #
STATE_CANDIDATE = "candidate"
STATE_COOLING = "cooling"
STATE_SEALED = "sealed"
STATE_VOID = "void"

PHOENIX_STATES = {STATE_CANDIDATE, STATE_COOLING, STATE_SEALED, STATE_VOID}

# --------------------------------------------------------------------------- #
# Phoenix State Machine
# --------------------------------------------------------------------------- #

PHOENIX_VALID_STATES = {STATE_CANDIDATE, STATE_COOLING, STATE_SEALED, STATE_VOID}


def is_anti_hantu(content: str) -> bool:
    """Return True if content exhibits consciousness/emotion claims (F9 Anti-Hantu)."""
    for pattern in ANTIHANTU_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def compute_cooldown_expiry(created_at: datetime | str) -> datetime:
    """Return cooldown_expiry = created_at + 72 hours."""
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return created_at + timedelta(hours=COOLING_HOURS)


def is_cooldown_complete(cooldown_expiry: datetime | str) -> bool:
    """Return True if 72h cooling window has elapsed."""
    if isinstance(cooldown_expiry, str):
        cooldown_expiry = datetime.fromisoformat(cooldown_expiry.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) >= cooldown_expiry


def should_seal(
    created_at: datetime | str,
    cooldown_expiry: datetime | str,
    psi_utility: int,
    tri_witness: dict[str, bool],
    anti_hantu_flag: bool,
    explicit_seal_requested: bool = False,
) -> tuple[bool, str]:
    """Evaluate whether a Phoenix entry should be SEALED or VOIDED.

    Returns (should_seal: bool, reason: str).
    """
    # Immediate VOID if Anti-Hantu flag is set at any point
    if anti_hantu_flag:
        return False, "anti_hantu_flag=True — immediate VOID"

    # Immediate VOID if explicitly vetoed
    if explicit_seal_requested is False:  # explicit False means veto
        return False, "explicit_veto=True — VOID"

    # Check cooldown completion
    if not is_cooldown_complete(cooldown_expiry):
        return False, f"cooldown incomplete: {cooldown_expiry}"

    # Check psi_utility threshold
    if psi_utility <= PSI_UTILITY_THRESHOLD:
        return False, f"psi_utility={psi_utility} <= threshold={PSI_UTILITY_THRESHOLD}"

    # Check Tri-Witness
    human = tri_witness.get("human", False)
    ai = tri_witness.get("ai", False)
    earth = tri_witness.get("earth", False)
    if not (human and ai and earth):
        missing = [k for k, v in {"human": human, "ai": ai, "earth": earth}.items() if not v]
        return False, f"tri_witness incomplete: missing={missing}"

    return True, "all SEAL conditions met"


def should_void(
    cooldown_expiry: datetime | str,
    psi_utility: int,
    tri_witness: dict[str, bool],
    anti_hantu_flag: bool,
    explicit_veto: bool = False,
) -> tuple[bool, str]:
    """Evaluate whether a Phoenix entry should be VOIDED.

    Returns (should_void: bool, reason: str).
    """
    if explicit_veto:
        return True, "explicit_veto=True"

    if anti_hantu_flag:
        return True, "anti_hantu_flag=True"

    if not is_cooldown_complete(cooldown_expiry):
        return False, "cooldown incomplete — remain in COOLING"

    # After cooldown: if not SEALed, must be VOIDed
    sealable, _ = should_seal(
        created_at=datetime.now(timezone.utc),  # not used after cooldown check
        cooldown_expiry=cooldown_expiry,
        psi_utility=psi_utility,
        tri_witness=tri_witness,
        anti_hantu_flag=anti_hantu_flag,
    )
    if sealable:
        return False, "should be SEALed, not VOIDed"

    return (
        True,
        f"cooldown complete but SEAL conditions not met (psi={psi_utility}, witness={tri_witness})",
    )


# --------------------------------------------------------------------------- #
# Phoenix Entry Builder (used by memory_store at ingest time)
# --------------------------------------------------------------------------- #


def phoenix_entry(
    memory_id: str,
    content: Any,
    mode: str,
    tags: list[str] | None,
    actor_id: str | None,
    session_id: str | None,
    summary: str | None = None,
    tier: str | None = None,
    provenance: dict[str, Any] | None = None,
    witness_requested: bool = False,
) -> dict[str, Any]:
    """Build a Phoenix-72 entry wrapping a candidate memory.

    Called by memory_store.store() at ingest time.
    All entries enter in STATE_CANDIDATE with anti_hantu_flag pre-checked.
    """
    now = datetime.now(timezone.utc)
    cooldown_expiry = now + timedelta(hours=COOLING_HOURS)

    # Pre-check Anti-Hantu at ingest (F9 gate — same as memory_store triage)
    content_str = content if isinstance(content, str) else str(content)
    anti_hantu = is_anti_hantu(content_str)

    # Pre-initialize tri_witness
    # human: true if actor is Arif or witness_requested is True
    human_attested = witness_requested or (actor_id and actor_id.lower() in ("arif", "ariffazil"))
    tri_witness = {
        "human": human_attested,
        "ai": False,  # attestable by kernel after F2/F3 review
        "earth": False,  # attestable by evidence_fetch ground-truth check
    }

    entry = {
        # Core identity
        "phoenix_id": str(uuid.uuid4()),
        "memory_id": memory_id,
        "state": STATE_CANDIDATE,
        # Provenance
        "provenance": provenance
        or {
            "session_id": session_id,
            "mode": mode,
            "actor_id": actor_id,
            "tool": "arif_memory_recall",
        },
        # Payload reference
        "content_ref": content_str[:200],  # first 200 chars as preview
        "content_hash": None,  # filled by caller
        # Timing
        "created_at": now.isoformat(),
        "cooldown_expiry": cooldown_expiry.isoformat(),
        "sealed_at": None,
        "voided_at": None,
        # Phoenix metrics
        "psi_utility": 0,  # starts neutral
        "psi_hits": 0,
        "psi_misses": 0,
        "psi_decay_events": 0,
        # Tri-Witness matrix
        "tri_witness": tri_witness,
        # F9 kill switch
        "anti_hantu_flag": anti_hantu,
        # Tier
        "tier": tier or "canon",
        # Flags
        "explicit_veto": False,
        "explicit_seal_request": False,
        # Utility log (audit trail of psi changes)
        "psi_log": [],
    }

    if anti_hantu:
        # Anti-Hantu is immediate VOID — flip state now
        entry["state"] = STATE_VOID
        entry["voided_at"] = now.isoformat()
        entry["psi_log"].append(
            {
                "ts": now.isoformat(),
                "event": "anti_hantu_triggered",
                "psi_before": 0,
                "psi_after": 0,
            }
        )
        logger.warning(
            "PHOENIX-72 [F9-VOID]: anti_hantu triggered for memory_id=%s — entry voided at ingest",
            memory_id,
        )

    return entry


# --------------------------------------------------------------------------- #
# Psi Utility Update (called on each recall/search hit or miss)
# --------------------------------------------------------------------------- #


def psi_hit(entry: dict[str, Any]) -> dict[str, Any]:
    """Called when this memory contributed to a successful query (reduced entropy)."""
    now = datetime.now(timezone.utc)
    entry = dict(entry)  # immutable copy
    entry["psi_hits"] = entry.get("psi_hits", 0) + 1
    entry["psi_utility"] = entry.get("psi_utility", 0) + PSI_HIT_BONUS
    entry["psi_log"] = list(entry.get("psi_log", []))
    entry["psi_log"].append(
        {
            "ts": now.isoformat(),
            "event": "hit",
            "delta": PSI_HIT_BONUS,
            "psi_after": entry["psi_utility"],
        }
    )
    logger.debug(
        "PHOENIX psi_hit: phoenix_id=%s psi_utility=%d",
        entry.get("phoenix_id"),
        entry["psi_utility"],
    )
    return entry


def psi_miss(entry: dict[str, Any]) -> dict[str, Any]:
    """Called when this memory caused conflict or required correction."""
    now = datetime.now(timezone.utc)
    entry = dict(entry)
    entry["psi_misses"] = entry.get("psi_misses", 0) + 1
    entry["psi_utility"] = entry.get("psi_utility", 0) + PSI_MISS_PENALTY
    entry["psi_log"] = list(entry.get("psi_log", []))
    entry["psi_log"].append(
        {
            "ts": now.isoformat(),
            "event": "miss",
            "delta": PSI_MISS_PENALTY,
            "psi_after": entry["psi_utility"],
        }
    )
    logger.debug(
        "PHOENIX psi_miss: phoenix_id=%s psi_utility=%d",
        entry.get("phoenix_id"),
        entry["psi_utility"],
    )
    return entry


def psi_decay(entry: dict[str, Any]) -> dict[str, Any]:
    """Apply half-life decay if not accessed within PSI_DECAY_HOURS."""
    now = datetime.now(timezone.utc)
    entry = dict(entry)
    last_access = entry.get("last_access_at") or entry.get("created_at")
    if last_access is None:
        return entry  # no timestamp to compare
    if isinstance(last_access, str):
        last_access = datetime.fromisoformat(last_access.replace("Z", "+00:00"))

    age_hours = (now - last_access).total_seconds() / 3600
    if age_hours < PSI_DECAY_HOURS:
        return entry  # no decay yet

    entry["psi_decay_events"] = entry.get("psi_decay_events", 0) + 1
    old_psi = entry["psi_utility"]
    entry["psi_utility"] = old_psi // 2  # half-life
    entry["psi_log"] = list(entry.get("psi_log", []))
    entry["psi_log"].append(
        {
            "ts": now.isoformat(),
            "event": "decay",
            "age_hours": round(age_hours, 1),
            "psi_before": old_psi,
            "psi_after": entry["psi_utility"],
        }
    )
    logger.debug(
        "PHOENIX psi_decay: phoenix_id=%s psi_utility %d→%d after %.1fh",
        entry.get("phoenix_id"),
        old_psi,
        entry["psi_utility"],
        age_hours,
    )
    return entry


# --------------------------------------------------------------------------- #
# Tri-Witness Attestation
# --------------------------------------------------------------------------- #


def attest_witness(
    entry: dict[str, Any],
    witness_type: str,  # "human" | "ai" | "earth"
    attested: bool = True,
) -> dict[str, Any]:
    """Attest one leg of the Tri-Witness matrix."""
    if witness_type not in ("human", "ai", "earth"):
        raise ValueError(f"Invalid witness_type: {witness_type}")
    entry = dict(entry)
    tri = dict(entry.get("tri_witness", {}))
    tri[witness_type] = attested
    entry["tri_witness"] = tri
    entry["psi_log"] = list(entry.get("psi_log", []))
    entry["psi_log"].append(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": f"witness_{witness_type}",
            "attested": attested,
        }
    )
    return entry


def is_tri_witness_complete(entry: dict[str, Any]) -> bool:
    """Return True if all three witnesses have attested."""
    tri = entry.get("tri_witness", {})
    return all(tri.get(k, False) for k in ("human", "ai", "earth"))


# --------------------------------------------------------------------------- #
# Promotion Tick — evaluate all COOLING entries for SEAL/VOID
# --------------------------------------------------------------------------- #


def evaluate_promotion(entry: dict[str, Any]) -> tuple[str, str]:
    """Evaluate state transition for a COOLING or CANDIDATE entry.

    Returns (new_state: str, reason: str).
    """
    now = datetime.now(timezone.utc)
    state = entry.get("state", STATE_CANDIDATE)
    cooldown_expiry_str = entry.get("cooldown_expiry")
    psi_utility = entry.get("psi_utility", 0)
    tri_witness = entry.get("tri_witness", {})
    anti_hantu = entry.get("anti_hantu_flag", False)
    explicit_veto = entry.get("explicit_veto", False)

    # Already in terminal state
    if state in (STATE_SEALED, STATE_VOID):
        return state, "already in terminal state"

    # Anti-Hantu: immediate VOID regardless of cooldown
    if anti_hantu:
        return STATE_VOID, "anti_hantu_flag=True"

    # Explicit veto: immediate VOID
    if explicit_veto:
        return STATE_VOID, "explicit_veto=True"

    # Not yet cooled down: stay in COOLING
    if cooldown_expiry_str:
        if not is_cooldown_complete(cooldown_expiry_str):
            return STATE_COOLING, "cooldown in progress"
    else:
        return STATE_COOLING, "no cooldown_expiry set"

    # Cooldown complete — evaluate SEAL vs VOID
    sealable, reason = should_seal(
        created_at=entry.get("created_at", now.isoformat()),
        cooldown_expiry=cooldown_expiry_str,
        psi_utility=psi_utility,
        tri_witness=tri_witness,
        anti_hantu_flag=anti_hantu,
    )

    if sealable:
        return STATE_SEALED, reason

    voidable, void_reason = should_void(
        cooldown_expiry=cooldown_expiry_str,
        psi_utility=psi_utility,
        tri_witness=tri_witness,
        anti_hantu_flag=anti_hantu,
    )

    if voidable:
        return STATE_VOID, void_reason

    # Still in COOLING (edge case: cooldown complete but psi_utility = 0 and no witness)
    return STATE_COOLING, "cooldown complete but SEAL conditions not yet met"


# --------------------------------------------------------------------------- #
# Phoenix Summary (for recall output)
# --------------------------------------------------------------------------- #


def phoenix_summary(entry: dict[str, Any]) -> dict[str, Any]:
    """Return a human-readable Phoenix-72 status block for recall output."""
    state = entry.get("state", STATE_CANDIDATE)
    cooldown_expiry = entry.get("cooldown_expiry")
    remaining_hours = None
    if cooldown_expiry and state == STATE_COOLING:
        if isinstance(cooldown_expiry, str):
            cooldown_expiry_dt = datetime.fromisoformat(cooldown_expiry.replace("Z", "+00:00"))
        else:
            cooldown_expiry_dt = cooldown_expiry
        remaining = (cooldown_expiry_dt - datetime.now(timezone.utc)).total_seconds() / 3600
        remaining_hours = round(max(0, remaining), 1)

    return {
        "phoenix_id": entry.get("phoenix_id"),
        "state": state,
        "psi_utility": entry.get("psi_utility", 0),
        "psi_hits": entry.get("psi_hits", 0),
        "psi_misses": entry.get("psi_misses", 0),
        "tri_witness": entry.get("tri_witness", {}),
        "tri_witness_complete": is_tri_witness_complete(entry),
        "anti_hantu_flag": entry.get("anti_hantu_flag", False),
        "cooldown_expiry": cooldown_expiry,
        "cooldown_remaining_hours": remaining_hours,
        "created_at": entry.get("created_at"),
        "sealed_at": entry.get("sealed_at"),
        "voided_at": entry.get("voided_at"),
        "tier": entry.get("tier", "canon"),
    }
