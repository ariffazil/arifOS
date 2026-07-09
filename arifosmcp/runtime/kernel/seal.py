"""
arifOS Kernel — 999 VAULT999 Sealing

The final phase of the metabolic pipeline. Immutable append to
civilizational memory. A sealed state cannot be mutated — only
superseded by a new seal with lineage.

Constraints:
  - Only SEAL or SABAR verdicts may seal.
  - Seal produces a permanent record with hash chain anchor.
  - No organ may seal without passing through 888 judgment.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Optional

from .types import GovernanceState, Phase


# ── Seal Record ───────────────────────────────


@dataclass
class SealRecord:
    seal_id: str
    seq: int
    verdict: str
    delta: float
    omega: float
    psi: float
    phase: Phase
    evidence_count: int
    actor_id: str | None = None
    session_id: str | None = None
    prev_seal_hash: str | None = None
    hash: str = ""
    timestamp: str = ""
    note: str | None = None


# ── Seal Chain ────────────────────────────────


@dataclass
class SealChain:
    records: list[SealRecord] = field(default_factory=list)
    last_seq: int = 0
    last_hash: str = ""


# ── 999 — Seal Function ───────────────────────


def seal(
    state: GovernanceState, chain: SealChain | None = None, note: str | None = None
) -> SealRecord:
    """Produce an immutable SealRecord from GovernanceState."""
    if state.verdict not in ("SEAL", "SABAR"):
        raise ValueError(
            f"Cannot seal with verdict '{state.verdict}'. "
            "Only SEAL or SABAR verdicts may be sealed."
        )

    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    prev_hash = chain.last_hash if chain else None

    # Build payload for content hash
    payload = {
        "verdict": state.verdict,
        "delta": state.scalars.delta,
        "omega": state.scalars.omega,
        "psi": state.scalars.psi,
        "phase": state.phase,
        "evidence_count": len(state.evidence),
        "actor_id": state.actor_id,
        "session_id": state.session_id,
        "cc_id": state.cc_id,
        "prev_seal_hash": prev_hash,
        "timestamp": ts,
        "note": note,
    }

    # SHA-256 content hash
    content = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(content.encode()).hexdigest()
    seal_id = f"SEAL-{h[:16]}"
    seq = (chain.last_seq + 1) if chain else 1

    return SealRecord(
        seal_id=seal_id,
        seq=seq,
        verdict=state.verdict,
        delta=state.scalars.delta,
        omega=state.scalars.omega,
        psi=state.scalars.psi,
        phase=state.phase,
        evidence_count=len(state.evidence),
        actor_id=state.actor_id,
        session_id=state.session_id,
        prev_seal_hash=prev_hash,
        hash=h,
        timestamp=ts,
        note=note,
    )


# ── Chain Operations ──────────────────────────


def empty_chain() -> SealChain:
    """Create a genesis seal chain."""
    genesis = SealRecord(
        seal_id="SEAL-GENESIS-0000000000000000",
        seq=0,
        verdict="SEAL",
        delta=0.0,
        omega=0.0,
        psi=1.0,
        phase=0,
        evidence_count=0,
        hash="0" * 64,
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        note="Genesis — seal chain initialized",
    )
    return SealChain(records=[genesis], last_seq=0, last_hash=genesis.hash)


def append_to_chain(chain: SealChain, record: SealRecord) -> SealChain:
    """Append a seal record to a chain. Returns new chain."""
    return SealChain(
        records=[*chain.records, record],
        last_seq=record.seq,
        last_hash=record.hash,
    )


def verify_chain(chain: SealChain) -> tuple[bool, int, str]:
    """Verify chain integrity from genesis to head.

    Returns: (valid, broken_at_index, head_hash)
    """
    for i in range(1, len(chain.records)):
        prev = chain.records[i - 1]
        curr = chain.records[i]
        if curr.prev_seal_hash != prev.hash:
            return False, i, chain.last_hash
    return True, -1, chain.last_hash
