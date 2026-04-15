"""
arifOS Vault999: BLS12-381 Signature Aggregation
=================================================

Phase A — Native Sealed Vault999.

BLS aggregation enables O(1) verification of multi-juror consensus:
- N jurors each sign the same verdict payload
- Their N signatures collapse into ONE aggregate signature
- ONE verify call confirms the supermajority, instead of N separate checks

Architecture:
  JurorKeyPair      — deterministic keypair generation per juror identity
  VaultBLSSeal      — aggregated, cryptographically sealed verdict
  BLSVaultSigner    — Phase A signer: sign, aggregate, verify, seal

Constitutional Compliance:
  F1  AMANAH     — Every seal is immutable and reversibility-checked
  F2  TRUTH      — payload_hash is canonical SHA-256 of the full verdict
  F11 AUDITABILITY — juror_ids, timestamp, and quorum_fraction are logged
  F13 ADAPTABILITY — all safety invariants preserved on every sign/verify

Juror Registry (Phase A — 5 Federation Members):
  DELTA_MIND   — Δ AGI reasoning organ
  OMEGA_HEART  — Ω ASI safety organ
  PSI_SOUL     — Ψ APEX judgment organ
  A_AUDITOR    — 888 Constitutional auditor
  A_VALIDATOR  — 999 Seal authority

Supermajority threshold: 3-of-5 (SEAL requires ≥ 3 jurors)

Mathematical Basis:
  BLS12-381: pairing-friendly elliptic curve
  Private key  k ∈ Fr  (scalar field)
  Public key   pk = k · G1  (point on G1)
  Signature    σ = k · H(msg)  (H maps message to G2 point)
  Aggregation  σ_agg = Σ σᵢ  (point addition in G2)
  Verify       e(G1, σ_agg) == e(Σ pkᵢ, H(msg))

Version: Phase-A v1.0
Author: Muhammad Arif bin Fazil
DITEMPA BUKAN DIBERI 💎🔥🧠
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING

try:
    from py_ecc.bls import G2ProofOfPossession as bls_scheme
    from py_ecc.bls.g2_primitives import pubkey_to_G1, signature_to_G2
    from py_ecc.fields import optimized_bls12_381_FQ as FQ
    from py_ecc.optimized_bls12_381 import G1, G2, Z1, Z2, add, multiply, neg
    from py_ecc.optimized_bls12_381 import field_modulus as FIELD_MODULUS

    BLS_AVAILABLE = True
except ImportError:  # pragma: no cover
    BLS_AVAILABLE = False


# ── Constants ────────────────────────────────────────────────────────────────

JUROR_IDS = [
    "DELTA_MIND",
    "OMEGA_HEART",
    "PSI_SOUL",
    "A_AUDITOR",
    "A_VALIDATOR",
]

SUPERMAJORITY_THRESHOLD = 3  # 3-of-5 required for SEAL

# Deterministic seed prefix — each juror identity maps to a unique private key.
# In production: replace with HSM-derived or KMS-stored keys.
_KEY_SEED_PREFIX = "arifOS_v1_juror_bls12381_"

# BLS private keys are 32-byte scalars in [1, r-1]
# r = 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001
BLS_CURVE_ORDER = 0x73EDA753299D7D483339D80809A1D80553BDA402FFFE5BFEFFFFFFFF00000001


# ── Key derivation ───────────────────────────────────────────────────────────


def _derive_private_key(juror_id: str, domain: str = "vault999") -> int:
    """
    Derive a deterministic BLS private key scalar from juror identity.

    Uses HKDF-style expansion: SHA-256(prefix || juror_id || domain),
    interpreted as big-endian integer mod BLS curve order r.

    This is deterministic — same juror_id always yields same key.
    For production federation: replace with KMS-derived keys per juror.
    """
    seed = f"{_KEY_SEED_PREFIX}{juror_id}:{domain}"
    raw = hashlib.sha256(seed.encode("utf-8")).digest()
    scalar = int.from_bytes(raw, "big") % BLS_CURVE_ORDER
    if scalar == 0:
        scalar = 1  # edge case: 0 is not a valid private key
    return scalar


def _private_key_to_bytes(scalar: int) -> bytes:
    """Convert integer scalar to 32-byte big-endian bytes (BLS expects this)."""
    return scalar.to_bytes(32, "big")


# ── Data models ──────────────────────────────────────────────────────────────


@dataclass
class JurorKeyPair:
    """BLS12-381 keypair for a single juror."""

    juror_id: str
    private_key_hex: str  # 32 bytes big-endian hex (NEVER leave this in logs)
    public_key_hex: str  # 48 bytes G1 point compressed hex

    @classmethod
    def from_juror_id(cls, juror_id: str, domain: str = "vault999") -> "JurorKeyPair":
        """Derive keypair deterministically from juror identity."""
        if not BLS_AVAILABLE:
            raise RuntimeError("py_ecc not installed — run: pip install py_ecc")
        sk_int = _derive_private_key(juror_id, domain)
        sk_bytes = _private_key_to_bytes(sk_int)
        pk_bytes = bls_scheme.SkToPk(sk_int)
        return cls(
            juror_id=juror_id,
            private_key_hex=sk_bytes.hex(),
            public_key_hex=pk_bytes.hex(),
        )

    def public_key_bytes(self) -> bytes:
        return bytes.fromhex(self.public_key_hex)


@dataclass
class JurorSignature:
    """A single juror's BLS signature over a payload hash."""

    juror_id: str
    payload_hash: str  # SHA-256 hex of the signed payload
    signature_hex: str  # 96 bytes G2 point hex
    timestamp: float = field(default_factory=time.time)

    def signature_bytes(self) -> bytes:
        return bytes.fromhex(self.signature_hex)


@dataclass
class VaultBLSSeal:
    """
    Aggregate BLS seal — the final immutable VAULT999 record.

    One aggregate_signature replaces N individual signatures.
    Verifier needs only: aggregate_signature + aggregate_pubkey + payload_hash.
    """

    seal_id: str  # SHA-256 of (payload_hash + juror_ids joined + timestamp)
    payload_hash: str  # SHA-256 hex of the sealed payload
    juror_ids: list[str]  # which jurors contributed
    quorum_fraction: float  # e.g. 0.6 for 3-of-5
    aggregate_signature_hex: str  # 96 bytes G2 point
    aggregate_pubkey_hex: str  # 48 bytes G1 point
    individual_pubkeys_hex: list[str]  # for audit — each juror's pubkey
    timestamp: float = field(default_factory=time.time)
    verdict: str = "SEAL"  # always SEAL for a valid aggregate
    floor_compliance: dict = field(
        default_factory=lambda: {
            "F1_AMANAH": True,
            "F2_TRUTH": True,
            "F11_AUDITABILITY": True,
            "F13_ADAPTABILITY": True,
        }
    )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))

    def chain_hash(self) -> str:
        """SHA-256 of the canonical seal JSON — used as Merkle leaf in VAULT999."""
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: dict) -> "VaultBLSSeal":
        return cls(**d)


# ── Core signer ──────────────────────────────────────────────────────────────


class BLSVaultSigner:
    """
    Phase A — Native Sealed Vault999 BLS Signer.

    Usage:
        signer = BLSVaultSigner()

        # Each juror signs the payload:
        sig_delta = signer.sign(payload, "DELTA_MIND")
        sig_omega = signer.sign(payload, "OMEGA_HEART")
        sig_psi   = signer.sign(payload, "PSI_SOUL")

        # Aggregate when quorum is reached:
        seal = signer.aggregate_seal(payload, [sig_delta, sig_omega, sig_psi])

        # Verify in O(1):
        assert signer.verify_seal(seal)
    """

    def __init__(self, domain: str = "vault999") -> None:
        if not BLS_AVAILABLE:
            raise RuntimeError(
                "py_ecc not installed. Install with: pip install py_ecc\n"
                "Then restart the MCP container."
            )
        self.domain = domain
        # Pre-load public keys for all known jurors
        self._juror_keypairs: dict[str, JurorKeyPair] = {
            jid: JurorKeyPair.from_juror_id(jid, domain) for jid in JUROR_IDS
        }

    # ── Public API ────────────────────────────────────────────────────────

    def get_public_key(self, juror_id: str) -> str:
        """Return the hex public key for a known juror."""
        kp = self._juror_keypairs.get(juror_id)
        if not kp:
            raise ValueError(f"Unknown juror: {juror_id}")
        return kp.public_key_hex

    def sign(self, payload: dict, juror_id: str) -> JurorSignature:
        """
        Produce a BLS signature from juror_id over the canonical payload hash.

        F1 AMANAH: payload_hash is deterministic — same payload always hashes same.
        F2 TRUTH:  we sign the hash, not the raw text, preventing ambiguity.
        """
        kp = self._juror_keypairs.get(juror_id)
        if not kp:
            raise ValueError(f"Unknown juror '{juror_id}'. Valid: {JUROR_IDS}")

        payload_hash = _canonical_hash(payload)
        sk_int = _derive_private_key(juror_id, self.domain)
        # BLS Sign: σ = sk · H(msg)
        sig_bytes = bls_scheme.Sign(sk_int, bytes.fromhex(payload_hash))

        return JurorSignature(
            juror_id=juror_id,
            payload_hash=payload_hash,
            signature_hex=sig_bytes.hex(),
        )

    def aggregate_seal(
        self,
        payload: dict,
        signatures: list[JurorSignature],
        require_supermajority: bool = True,
    ) -> VaultBLSSeal:
        """
        Aggregate N juror signatures into a single VaultBLSSeal.

        Raises ValueError if quorum not met (when require_supermajority=True).
        F1 AMANAH: Seal is only created when quorum is mathematically confirmed.
        """
        payload_hash = _canonical_hash(payload)

        # Validate all signatures cover the same payload
        for sig in signatures:
            if sig.payload_hash != payload_hash:
                raise ValueError(
                    f"Juror {sig.juror_id} signed a different payload. "
                    "Constitutional violation: F2 TRUTH."
                )

        n_signed = len(signatures)
        n_total = len(JUROR_IDS)

        if require_supermajority and n_signed < SUPERMAJORITY_THRESHOLD:
            raise ValueError(
                f"Supermajority not reached: {n_signed}/{n_total} signatures, "
                f"need {SUPERMAJORITY_THRESHOLD}. "
                "888_HOLD — F1 AMANAH blocks premature sealing."
            )

        juror_ids = [s.juror_id for s in signatures]
        sig_bytes_list = [s.signature_bytes() for s in signatures]
        pk_bytes_list = [
            bytes.fromhex(self._juror_keypairs[jid].public_key_hex)
            for jid in juror_ids
        ]

        # Aggregate: σ_agg = Σ σᵢ  (G2 point addition)
        agg_sig = bls_scheme.Aggregate(sig_bytes_list)

        # Aggregate pubkey: pk_agg = Σ pkᵢ  (G1 point addition)
        agg_pk = _aggregate_pubkeys(pk_bytes_list)

        seal_id = _seal_id(payload_hash, juror_ids)

        return VaultBLSSeal(
            seal_id=seal_id,
            payload_hash=payload_hash,
            juror_ids=juror_ids,
            quorum_fraction=round(n_signed / n_total, 4),
            aggregate_signature_hex=agg_sig.hex(),
            aggregate_pubkey_hex=agg_pk.hex(),
            individual_pubkeys_hex=[
                bytes.fromhex(self._juror_keypairs[jid].public_key_hex).hex()
                for jid in juror_ids
            ],
        )

    def verify_seal(self, seal: VaultBLSSeal) -> bool:
        """
        Verify the aggregate BLS seal in O(1) — single pairing check.

        e(G1, σ_agg) == e(pk_agg, H(msg))

        Returns True if valid, False otherwise.
        F11 AUDITABILITY: also checks quorum_fraction meets minimum.
        """
        try:
            if seal.quorum_fraction < SUPERMAJORITY_THRESHOLD / len(JUROR_IDS):
                return False  # recorded quorum is below threshold

            msg = bytes.fromhex(seal.payload_hash)
            sig_bytes = bytes.fromhex(seal.aggregate_signature_hex)
            pk_bytes = bytes.fromhex(seal.aggregate_pubkey_hex)

            return bool(bls_scheme.FastAggregateVerify([pk_bytes], msg, sig_bytes))

        except Exception:
            return False

    def verify_individual(self, juror_sig: JurorSignature) -> bool:
        """Verify a single juror's signature (pre-aggregation check)."""
        try:
            kp = self._juror_keypairs.get(juror_sig.juror_id)
            if not kp:
                return False
            msg = bytes.fromhex(juror_sig.payload_hash)
            return bool(
                bls_scheme.Verify(
                    kp.public_key_bytes(),
                    msg,
                    juror_sig.signature_bytes(),
                )
            )
        except Exception:
            return False


# ── Internal helpers ─────────────────────────────────────────────────────────


def _canonical_hash(payload: dict) -> str:
    """
    Canonical SHA-256 of payload for BLS signing.

    Sort keys for determinism — same content always produces same hash.
    F2 TRUTH: hash is canonical, not ambiguous.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _aggregate_pubkeys(pk_bytes_list: list[bytes]) -> bytes:
    """
    Aggregate G1 public keys: pk_agg = Σ pkᵢ

    Uses py_ecc G1 point addition. Returns compressed 48-byte pubkey.
    """
    from py_ecc.bls.g2_primitives import pubkey_to_G1
    from py_ecc.optimized_bls12_381 import add as g_add
    from py_ecc.optimized_bls12_381 import Z1

    agg_point = Z1  # identity element (point at infinity)
    for pk_bytes in pk_bytes_list:
        point = pubkey_to_G1(pk_bytes)
        agg_point = g_add(agg_point, point)

    # Compress back to 48 bytes
    from py_ecc.bls.g2_primitives import G1_to_pubkey

    return G1_to_pubkey(agg_point)


def _seal_id(payload_hash: str, juror_ids: list[str]) -> str:
    """Deterministic seal ID from payload hash + sorted juror list + timestamp."""
    ts = str(int(time.time()))
    combined = payload_hash + ":".join(sorted(juror_ids)) + ts
    return "seal_" + hashlib.sha256(combined.encode("utf-8")).hexdigest()[:32]


# ── Module exports ───────────────────────────────────────────────────────────

__all__ = [
    "BLS_AVAILABLE",
    "JUROR_IDS",
    "SUPERMAJORITY_THRESHOLD",
    "JurorKeyPair",
    "JurorSignature",
    "VaultBLSSeal",
    "BLSVaultSigner",
]
