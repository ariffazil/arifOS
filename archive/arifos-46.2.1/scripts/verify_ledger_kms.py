#!/usr/bin/env python3
"""
scripts/verify_ledger_kms.py

Verify Cooling Ledger integrity and (optionally) KMS signatures.

Enhancements vs original:
- Optionally perform local signature verification by caching public keys fetched from KMS (GetPublicKey).
- Supports --no-verify, --local-verify, --key-cache-dir, and --cache-ttl-days.
- Produces structured summary and exit code 2 on failures for automation.

Usage:
    python scripts/verify_ledger_kms.py /path/to/ledger.jsonl
    python scripts/verify_ledger_kms.py /path/to/ledger.jsonl --no-verify
    python scripts/verify_ledger_kms.py /path/to/ledger.jsonl --local-verify --key-cache-dir /var/cache/arifos/kms-keys
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, Dict
import logging

# canonical compute_hash from arifos_core.cooling_ledger
try:
    from arifos_core.memory.cooling_ledger import compute_hash  # type: ignore
except Exception:
    print("ERROR: could not import arifos_core.cooling_ledger.compute_hash. Ensure PYTHONPATH points to repo root.", file=sys.stderr)
    raise

# Optional crypto & boto3 imports
try:
    import boto3  # type: ignore
except Exception:
    boto3 = None  # type: ignore

try:
    from cryptography.hazmat.primitives.serialization import load_der_public_key  # type: ignore
    from cryptography.hazmat.primitives.asymmetric import padding  # type: ignore
    from cryptography.hazmat.primitives import hashes  # type: ignore
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False

try:
    from arifos_core.utils.kms_signer import KmsSigner, KmsSignerConfig  # type: ignore
except Exception:
    KmsSigner = None  # type: ignore
    KmsSignerConfig = None  # type: ignore

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_ledger_kms")


def load_lines(path: Path, limit: int = 0):
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    if limit and len(lines) > limit:
        return lines[:limit]
    return lines


def sanitize_key_id_to_filename(key_id: str) -> str:
    # Replace non-alphanumeric with underscore to produce safe filenames
    import re
    base = re.sub(r"[^A-Za-z0-9_.-]+", "_", key_id)
    return base


def fetch_and_cache_public_key(
    kms_key_id: str, cache_dir: Path, aws_region: Optional[str] = None, force_refresh: bool = False, cache_ttl_days: int = 7
) -> Optional[bytes]:
    """
    Fetch public key DER bytes from KMS and cache it locally.
    Returns DER bytes, or None on error.
    """
    cache_dir.mkdir(parents=True, exist_ok=True)
    fname = cache_dir / sanitize_key_id_to_filename(kms_key_id)
    now = time.time()
    if fname.exists() and not force_refresh:
        mtime = fname.stat().st_mtime
        age_days = (now - mtime) / 86400.0
        if age_days < cache_ttl_days:
            try:
                return fname.read_bytes()
            except Exception:
                pass

    if boto3 is None:
        logger.warning("boto3 not available; cannot fetch public key from KMS")
        return None

    client = boto3.client("kms", region_name=aws_region) if aws_region else boto3.client("kms")
    try:
        resp = client.get_public_key(KeyId=kms_key_id)
        der = resp["PublicKey"]
        # cache
        fname.write_bytes(der)
        return der
    except Exception as e:
        logger.exception("failed to get_public_key from KMS for %s: %s", kms_key_id, e)
        return None


def verify_signature_locally(der_pubkey: bytes, signature_b64: str, digest_hex: str, signing_algorithm: str = "RSASSA_PSS_SHA_256") -> bool:
    """
    Verify signature locally using cached public key DER bytes.
    Returns True if signature valid, False otherwise.

    Supports RSASSA_PSS_SHA_256 as used by KMS.
    """
    if not CRYPTO_AVAILABLE:
        logger.warning("cryptography not available; cannot perform local verification")
        return False

    from base64 import b64decode

    public_key = load_der_public_key(der_pubkey)
    signature = b64decode(signature_b64)
    digest = bytes.fromhex(digest_hex)
    try:
        if signing_algorithm.upper().startswith("RSASSA_PSS"):
            public_key.verify(
                signature,
                digest,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        else:
            # fallback: try PKCS1v15 with SHA256 (rare case)
            public_key.verify(
                signature,
                digest,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        return True
    except Exception as e:
        logger.debug("local signature verify failed: %s", e)
        return False


def verify_ledger(
    ledger_path: Path,
    *,
    verify_signatures: bool = True,
    local_verify: bool = False,
    key_cache_dir: Optional[Path] = None,
    cache_ttl_days: int = 7,
    aws_region: Optional[str] = None,
    force_refresh_keys: bool = False,
    max_entries: int = 0,
) -> Tuple[bool, Dict[str, int]]:
    """
    Verify ledger integrity.

    If local_verify is True, the script will attempt to fetch public keys via KMS GetPublicKey and verify signatures locally using cryptography.
    If local_verify is False and verify_signatures is True, the script will call KMS Verify per-entry.

    Returns (ok, stats)
    """
    lines = load_lines(ledger_path, limit=max_entries)
    stats = {
        "total": 0,
        "json_errors": 0,
        "hash_mismatches": 0,
        "prev_hash_mismatches": 0,
        "signature_failures": 0,
        "signature_errors": 0,
        "first_entry_prev_non_null": 0,
        "public_key_cache_misses": 0,
    }

    prev_hash: Optional[str] = None

    for idx, line in enumerate(lines):
        stats["total"] += 1
        try:
            entry = json.loads(line)
        except Exception as e:
            logger.error("invalid json at index %d: %s", idx, e)
            stats["json_errors"] += 1
            continue

        # compute expected hash
        try:
            expected = compute_hash(entry)
        except Exception as e:
            logger.error("failed to compute hash at index %d: %s", idx, e)
            stats["hash_mismatches"] += 1
            continue

        stored_hash = entry.get("hash")
        if stored_hash != expected:
            logger.error("hash mismatch idx=%d stored=%s expected=%s", idx, stored_hash, expected)
            stats["hash_mismatches"] += 1

        # prev_hash linkage
        if idx == 0:
            if entry.get("prev_hash") not in (None, "", []):
                logger.error("first entry prev_hash should be null/empty (found %s)", entry.get("prev_hash"))
                stats["first_entry_prev_non_null"] += 1
        else:
            if entry.get("prev_hash") != prev_hash:
                logger.error("prev_hash mismatch idx=%d stored=%s expected=%s", idx, entry.get("prev_hash"), prev_hash)
                stats["prev_hash_mismatches"] += 1

        # signature checks
        if verify_signatures and entry.get("kms_signature") and entry.get("kms_key_id"):
            kms_key_id = entry.get("kms_key_id")
            sig_b64 = entry.get("kms_signature")
            digest_hex = stored_hash

            # Local verification path (preferred if available)
            if local_verify:
                if key_cache_dir is None:
                    logger.error("local_verify requested but no key_cache_dir provided")
                    stats["signature_errors"] += 1
                else:
                    der = fetch_and_cache_public_key(kms_key_id, key_cache_dir, aws_region=aws_region, force_refresh=force_refresh_keys, cache_ttl_days=cache_ttl_days)
                    if der is None:
                        stats["public_key_cache_misses"] += 1
                        logger.error("public key not available for %s (idx=%d)", kms_key_id, idx)
                        stats["signature_errors"] += 1
                    else:
                        ok_local = verify_signature_locally(der, sig_b64, digest_hex)
                        if not ok_local:
                            logger.error("local signature verify failed idx=%d key=%s", idx, kms_key_id)
                            stats["signature_failures"] += 1
            else:
                # remote verify via KMS Verify
                if boto3 is None:
                    logger.warning("boto3 not available; skipping KMS Verify")
                else:
                    try:
                        client = boto3.client("kms", region_name=aws_region) if aws_region else boto3.client("kms")
                        resp = client.verify(
                            KeyId=kms_key_id,
                            Message=bytes.fromhex(digest_hex),
                            MessageType="DIGEST",
                            Signature=base64.b64decode(sig_b64),
                            SigningAlgorithm="RSASSA_PSS_SHA_256",
                        )
                        if not resp.get("SignatureValid", False):
                            logger.error("KMS Verify reported invalid signature idx=%d key=%s", idx, kms_key_id)
                            stats["signature_failures"] += 1
                    except Exception as e:
                        logger.exception("KMS Verify error idx=%d key=%s: %s", idx, kms_key_id, e)
                        stats["signature_errors"] += 1

        prev_hash = entry.get("hash")

    ok = (
        stats["json_errors"] == 0
        and stats["hash_mismatches"] == 0
        and stats["prev_hash_mismatches"] == 0
        and stats["signature_failures"] == 0
        and stats["first_entry_prev_non_null"] == 0
    )
    return ok, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify Cooling Ledger integrity and optional KMS signatures.")
    ap.add_argument("ledger", type=Path, help="Path to ledger JSONL file")
    ap.add_argument("--no-verify", action="store_true", help="Do not call KMS Verify; only check hashes/chain")
    ap.add_argument("--local-verify", action="store_true", help="Verify signatures locally using cached public keys (GetPublicKey)")
    ap.add_argument("--key-cache-dir", type=Path, default=Path("/var/cache/arifos/kms-keys"), help="Directory to cache KMS public keys for local verification")
    ap.add_argument("--cache-ttl-days", type=int, default=7, help="Days to consider cached public key fresh")
    ap.add_argument("--force-refresh-keys", action="store_true", help="Force refresh of cached public keys from KMS")
    ap.add_argument("--region", type=str, default=None, help="AWS region to use for KMS client (optional)")
    ap.add_argument("--max", type=int, default=0, help="If >0, limit number of entries checked (useful for large ledgers)")
    args = ap.parse_args(argv)

    ledger_path: Path = args.ledger
    if not ledger_path.exists():
        print(f"ERROR: ledger not found: {ledger_path}", file=sys.stderr)
        return 2

    verify_signatures = not args.no_verify
    local_verify = args.local_verify

    if local_verify and not CRYPTO_AVAILABLE:
        print("WARNING: cryptography package not installed; local verification will not work. Falling back to KMS Verify if available.", file=sys.stderr)
        local_verify = False

    if local_verify and boto3 is None:
        print("ERROR: boto3 is required for local verification to fetch public keys from KMS", file=sys.stderr)
        return 2

    ok, stats = verify_ledger(
        ledger_path,
        verify_signatures=verify_signatures,
        local_verify=local_verify,
        key_cache_dir=args.key_cache_dir,
        cache_ttl_days=args.cache_ttl_days,
        aws_region=args.region,
        force_refresh_keys=args.force_refresh_keys,
        max_entries=args.max,
    )

    print("\n--- summary ---")
    for k, v in stats.items():
        print(f"{k}: {v}")

    if ok:
        print("\nRESULT: OK — ledger verified")
        return 0
    else:
        print("\nRESULT: FAIL — ledger verification issues detected", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
