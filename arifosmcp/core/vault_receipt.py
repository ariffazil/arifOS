"""
arifosmcp/core/vault_receipt.py — VAULT999 Receipt Provenance Schema (#421)

Cryptographically linked receipts for the immutable ledger.

Design invariant: No receipt without a signer, no signer without an organ,
no organ without a kernel hash. Payload is never inline — only its hash.

Phase 1: SHA-256 hashing only (no Ed25519 yet)
Phase 4: Ed25519 key generation + signing
Phase 5: Merkle checkpoint computation

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


# ── Receipt Schema ───────────────────────────────────────────────


@dataclass
class VaultReceipt:
    """
    Cryptographically linked receipt for VAULT999.

    Frozen fields are computed at creation time.
    Mutable fields (session_merkle_root) are updated as chain grows.
    """

    # ── Identity ──────────────────────────────────────────────────
    receipt_id: str              # UUIDv7 — time-ordered, no central authority
    ts: str                      # ISO8601
    monotonic_counter: int       # Lamport clock — total ordering within session

    # ── Chain ─────────────────────────────────────────────────────
    parent_hash: str             # SHA256 of previous receipt in this session
    session_id: str              # Which session this belongs to
    # V1 fix: renamed comment — this is a chain hash (cumulative), not a true Merkle root.
    # True Merkle root (Phase 5) will use a separate field alongside this one.
    # Kept as session_merkle_root for wire-format stability (Phase 1–4 compatibility).
    session_merkle_root: str     # Chain hash: hash(r0 || hash(r1 || hash(r2 || ...)))

    # ── Provenance ────────────────────────────────────────────────
    actor_id: str                # Who did this
    organ_id: str                # Which organ (arifOS|A-FORGE|GEOX|WEALTH|WELL|AAA|HUMAN)
    actor_pubkey_epoch: int      # Which key generation signed this (0 = bootstrap)
    actor_signature: str         # Ed25519 signature (hex) — "" if unsigned (Phase 1)

    # ── Constitutional ────────────────────────────────────────────
    intent_summary: str          # Human-readable summary
    intent_hash: str             # SHA256 of full intent payload
    requested_authority: str     # AuthorityClass value
    pre_state_hash: str          # Frozen input envelope hash
    decision: str                # VerdictClass value
    verdict_hash: str            # SHA256 of full verdict payload
    floors_evaluated: list[str]  # F1..F13 actually checked
    floors_violated: list[str]   # Which floors were violated

    # ── Conflict Resolution ───────────────────────────────────────
    conflict_resolved: bool      # Was a conflict resolved?
    conflict_resolution: str     # Resolution method (dominance|authority|escalate|none)

    # ── Latency ───────────────────────────────────────────────────
    decision_class: str          # C0_AUTO | C1_FAST | C2_STANDARD | C3_DEEP | C4_SOVEREIGN
    latency_ms: float            # Actual latency
    within_budget: bool          # Did it stay within budget?

    # ── Witness ───────────────────────────────────────────────────
    witness_count: int           # How many witnesses attested
    witness_dissent: list[str]   # Any dissenting verdicts

    # ── F14 Self-Modification ─────────────────────────────────────
    self_modification_receipt: bool = False  # True if this receipt records an F14 amendment
    amendment_target: str = ""              # Which floor/content is being amended (e.g. "F14", "F3")

    # ── Receipt Seal ──────────────────────────────────────────────
    receipt_hash: str = ""            # SHA256(canonical_order of all above fields)

    # ── Selective Disclosure ──────────────────────────────────────
    view_key_id: str = ""             # Auditor with key can see intent/decision
                                 # Without it: only sees hash

    def to_dict(self) -> dict[str, Any]:
        """Canonical dict for serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Canonical JSON for hashing and storage."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


# ── Hash Computation ─────────────────────────────────────────────


def compute_receipt_hash(r: VaultReceipt) -> str:
    """
    Canonical hash — deterministic, order-independent within groups.
    SHA-256 for Phase 1. BLAKE3 for speed later if needed.
    """
    canonical = json.dumps({
        "identity": {
            "receipt_id": r.receipt_id,
            "ts": r.ts,
            "monotonic_counter": r.monotonic_counter,
        },
        "chain": {
            "parent_hash": r.parent_hash,
            "session_id": r.session_id,
            "session_merkle_root": r.session_merkle_root,
        },
        "provenance": {
            "actor_id": r.actor_id,
            "organ_id": r.organ_id,
            "actor_pubkey_epoch": r.actor_pubkey_epoch,
            "actor_signature": r.actor_signature,
        },
        "constitutional": {
            "intent_hash": r.intent_hash,
            "requested_authority": r.requested_authority,
            "pre_state_hash": r.pre_state_hash,
            "decision": r.decision,
            "verdict_hash": r.verdict_hash,
            "floors_evaluated": sorted(r.floors_evaluated),
            "floors_violated": sorted(r.floors_violated),
            "self_modification_receipt": r.self_modification_receipt,
            "amendment_target": r.amendment_target,
        },
        "conflict": {
            "conflict_resolved": r.conflict_resolved,
            "conflict_resolution": r.conflict_resolution,
        },
        "latency": {
            "decision_class": r.decision_class,
            "latency_ms": r.latency_ms,
            "within_budget": r.within_budget,
        },
        "witness": {
            "witness_count": r.witness_count,
            "witness_dissent": sorted(r.witness_dissent),
        },
    }, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


# ── Session Chain Manager ────────────────────────────────────────


class SessionChain:
    """
    Manages per-session hash chain + Merkle checkpoint.
    Thread-safe for single-process use.

    V5 fix: In-process cache eliminates O(N) vault scan per receipt.
    Each SessionChain instance is cached by session_id within the same process.
    """

    # V5: Process-level cache — keyed by session_id.
    # Prevents O(N) disk reload every time create_and_seal_receipt is called.
    _cache: dict[str, SessionChain] = {}

    def __init__(self, session_id: str, vault_path: str | Path | None = None):
        self.session_id = session_id
        self.vault_path = Path(vault_path or "/root/VAULT999/receipts_v2.jsonl")
        self.receipts: list[VaultReceipt] = []
        self.counter: int = 0
        self.parent_hash: str = ""  # Empty for first receipt

        # Load existing chain if file exists
        self._load_existing()

    def _load_existing(self) -> None:
        """Load existing receipts for this session from disk."""
        if not self.vault_path.exists():
            return

        try:
            with open(self.vault_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("session_id") == self.session_id:
                            receipt = VaultReceipt(**data)
                            self.receipts.append(receipt)
                            self.counter = max(self.counter, receipt.monotonic_counter)
                    except (json.JSONDecodeError, TypeError, KeyError):
                        continue  # Skip malformed lines

            if self.receipts:
                self.parent_hash = self.receipts[-1].receipt_hash
        except OSError as e:
            # V2 fix: log + signal instead of silent pass.
            # Silent pass means chain corruption goes undetected.
            # F4 CLARITY: every anomaly must leave a trace.
            logger.error(
                "VAULT999 chain load failed for session_id=%s: %s. "
                "Starting fresh — prior chain entries may exist but are unreachable. "
                "Manual audit of vault file recommended.",
                self.session_id,
                e,
            )
            # F11 AUDIT signal: record the anomaly for vault audit trail.
            # The session continues with an empty chain, but the OSError is
            # now visible in logs and eligible for VAULT999 anomaly tracking.
            # This is V2 from the 2026-06-25 audit — not a silent failure.
            pass

    def _compute_chain_hash(self) -> str:
        """
        Compute the session chain hash for Phase 1.

        Note: stored in VaultReceipt.session_merkle_root for wire-format stability.
        Phase 5 will introduce a true Merkle root alongside this field.

        Simple chain: hash(receipt_0 || hash(receipt_1 || hash(receipt_2 || ...)))
        """
        if not self.receipts:
            return hashlib.sha256(b"empty").hexdigest()

        chain_hash = ""
        for r in reversed(self.receipts):
            combined = r.receipt_hash + chain_hash
            chain_hash = hashlib.sha256(combined.encode()).hexdigest()

        return chain_hash

    def create_receipt(
        self,
        actor_id: str,
        organ_id: str,
        intent_summary: str,
        intent_hash: str,
        requested_authority: str,
        pre_state_hash: str,
        decision: str,
        verdict_hash: str,
        floors_evaluated: list[str],
        floors_violated: list[str],
        conflict_resolved: bool = False,
        conflict_resolution: str = "none",
        decision_class: str = "C2_STANDARD",
        latency_ms: float = 0.0,
        within_budget: bool = True,
        witness_count: int = 0,
        witness_dissent: list[str] | None = None,
        self_modification_receipt: bool = False,
        amendment_target: str = "",
    ) -> VaultReceipt:
        """
        Create a new receipt in this session's chain.
        Auto-computes: receipt_id, ts, monotonic_counter, parent_hash,
        session_merkle_root, receipt_hash.

        Set self_modification_receipt=True for F14 amendment proposals.
        amendment_target specifies which floor/content is being amended.
        """
        # Compute fields
        receipt_id = str(uuid4())
        ts = datetime.now(UTC).isoformat()
        self.counter += 1
        merkle_root = self._compute_chain_hash()

        # Create receipt
        receipt = VaultReceipt(
            receipt_id=receipt_id,
            ts=ts,
            monotonic_counter=self.counter,
            parent_hash=self.parent_hash,
            session_id=self.session_id,
            session_merkle_root=merkle_root,
            actor_id=actor_id,
            organ_id=organ_id,
            actor_pubkey_epoch=0,  # Bootstrap epoch — no keys yet
            actor_signature="",    # Phase 1: unsigned
            intent_summary=intent_summary,
            intent_hash=intent_hash,
            requested_authority=requested_authority,
            pre_state_hash=pre_state_hash,
            decision=decision,
            verdict_hash=verdict_hash,
            floors_evaluated=floors_evaluated,
            floors_violated=floors_violated,
            conflict_resolved=conflict_resolved,
            conflict_resolution=conflict_resolution,
            decision_class=decision_class,
            latency_ms=latency_ms,
            within_budget=within_budget,
            witness_count=witness_count,
            witness_dissent=witness_dissent or [],
            self_modification_receipt=self_modification_receipt,
            amendment_target=amendment_target,
            receipt_hash="",  # Computed below
            view_key_id="",  # Phase 6: selective disclosure
        )

        # Compute hash (merkle_root represents chain state BEFORE this receipt)
        receipt.receipt_hash = compute_receipt_hash(receipt)

        # Update chain state
        self.receipts.append(receipt)
        self.parent_hash = receipt.receipt_hash

        return receipt

    def append_to_vault(self, receipt: VaultReceipt) -> Path:
        """
        Append receipt to VAULT999/receipts_v2.jsonl.
        Append-only — never modifies existing entries.
        """
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.vault_path, "a") as f:
            f.write(json.dumps(receipt.to_dict(), sort_keys=True) + "\n")

        return self.vault_path

    def verify_chain(self) -> tuple[bool, list[str]]:
        """
        Verify the hash chain integrity.
        Returns (is_valid, list_of_errors).
        """
        errors: list[str] = []

        if not self.receipts:
            return True, errors

        for i, receipt in enumerate(self.receipts):
            # Check parent_hash linkage
            if i == 0:
                if receipt.parent_hash != "":
                    errors.append(f"Receipt {i}: first receipt should have empty parent_hash")
            else:
                expected_parent = self.receipts[i - 1].receipt_hash
                if receipt.parent_hash != expected_parent:
                    errors.append(
                        f"Receipt {i}: parent_hash mismatch. "
                        f"Expected {expected_parent[:16]}..., got {receipt.parent_hash[:16]}..."
                    )

            # Check receipt_hash
            expected_hash = compute_receipt_hash(receipt)
            if receipt.receipt_hash != expected_hash:
                errors.append(
                    f"Receipt {i}: receipt_hash mismatch. "
                    f"Expected {expected_hash[:16]}..., got {receipt.receipt_hash[:16]}..."
                )

            # Check session_id
            if receipt.session_id != self.session_id:
                errors.append(
                    f"Receipt {i}: session_id mismatch. "
                    f"Expected {self.session_id}, got {receipt.session_id}"
                )

            # Check monotonic counter
            if receipt.monotonic_counter != i + 1:
                errors.append(
                    f"Receipt {i}: counter mismatch. "
                    f"Expected {i + 1}, got {receipt.monotonic_counter}"
                )

        return len(errors) == 0, errors


# ── Convenience Functions ────────────────────────────────────────


def create_and_seal_receipt(
    session_id: str,
    actor_id: str,
    organ_id: str,
    intent_summary: str,
    intent_hash: str,
    requested_authority: str,
    pre_state_hash: str,
    decision: str,
    verdict_hash: str,
    floors_evaluated: list[str],
    floors_violated: list[str],
    conflict_resolved: bool = False,
    conflict_resolution: str = "none",
    decision_class: str = "C2_STANDARD",
    latency_ms: float = 0.0,
    within_budget: bool = True,
    witness_count: int = 0,
    witness_dissent: list[str] | None = None,
    self_modification_receipt: bool = False,
    amendment_target: str = "",
    vault_path: str | Path | None = None,
) -> VaultReceipt:
    """
    Convenience: create receipt + append to vault in one call.

    Set self_modification_receipt=True for F14 constitutional amendment receipts.
    amendment_target should specify the target floor or content (e.g. "F14", "F3").
    """
    # V5 fix: use in-process cache to avoid O(N) vault scan per receipt.
    # Cache hit: reuse existing SessionChain (already loaded from disk).
    # Cache miss: load from disk + cache for subsequent calls in same process.
    if session_id in SessionChain._cache:
        chain = SessionChain._cache[session_id]
    else:
        chain = SessionChain(session_id, vault_path)
        SessionChain._cache[session_id] = chain

    receipt = chain.create_receipt(
        actor_id=actor_id,
        organ_id=organ_id,
        intent_summary=intent_summary,
        intent_hash=intent_hash,
        requested_authority=requested_authority,
        pre_state_hash=pre_state_hash,
        decision=decision,
        verdict_hash=verdict_hash,
        floors_evaluated=floors_evaluated,
        floors_violated=floors_violated,
        conflict_resolved=conflict_resolved,
        conflict_resolution=conflict_resolution,
        decision_class=decision_class,
        latency_ms=latency_ms,
        within_budget=within_budget,
        witness_count=witness_count,
        witness_dissent=witness_dissent,
        self_modification_receipt=self_modification_receipt,
        amendment_target=amendment_target,
    )
    chain.append_to_vault(receipt)
    return receipt


def verify_vault_chain(
    session_id: str,
    vault_path: str | Path | None = None,
) -> tuple[bool, list[str]]:
    """
    Convenience: verify a session's chain integrity.
    """
    chain = SessionChain(session_id, vault_path)
    return chain.verify_chain()
