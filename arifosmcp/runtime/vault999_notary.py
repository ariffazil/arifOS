"""
VAULT999 Notary — HMAC-SHA256 signature chain over outcomes.jsonl

Pattern distilled from paperclipai/paperclip decision-signing.ts (MIT)
Doctrine: DITEMPA BUKAN DIBERI

Provides:
  - sign_outcome(outcome_row) → HMAC-SHA256 signature
  - verify_chain(start_seq, end_seq) → walks outcomes.jsonl, verifies chain
  - CLI: python3 -m arifosmcp.runtime.vault999_notary verify --last 200

Key location defined by VAULT999_NOTARY_KEY env var, enforced 0600 + uid.
Pattern: decision-signing.ts lines 24-60.

CRITICAL: outcomes.jsonl is chattr +a append-only — the notary
READS outcomes.jsonl and appends signature stubs to a SIBLING file
outcomes.sig.jsonl (never mutates the sealed file).

Spec: vault999-notary-v1
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import stat
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Configuration ─────────────────────────────────────────────────────

SPEC_VERSION = "vault999-notary-v1"
_KEY_DIR = Path("/root/.config/arifos")
_KEY_NAME = "vault999-notary.key"
KEY_PATH = Path(os.getenv("VAULT999_NOTARY_KEY", str(_KEY_DIR / _KEY_NAME)))
OUTCOMES_PATH = Path(os.getenv("VAULT999_OUTCOMES", "/root/VAULT999/outcomes.jsonl"))
SIG_PATH = Path(os.getenv("VAULT999_SIG", "/root/VAULT999/outcomes.sig.jsonl"))

# ── Key management (pattern: decision-signing.ts lines 24-60) ─────────


def _ensure_key() -> bytes:
    """
    Ensure the HMAC key exists with correct permissions.
    Auto-generates 32-byte random secret if missing.
    Enforces 0600 + process-uid ownership.
    """
    if not KEY_PATH.exists():
        # Atomic key generation via rename (no hard-link race)
        KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        secret = os.urandom(32).hex()
        tmp = KEY_PATH.with_suffix(".tmp")
        tmp.write_text(secret)
        tmp.chmod(0o600)
        tmp.rename(KEY_PATH)
        print(f"[Notary] Generated key at {KEY_PATH}")

    # Enforce permissions
    st = KEY_PATH.stat()
    mode = stat.S_IMODE(st.st_mode)
    if mode != 0o600:
        raise PermissionError(f"Key file {KEY_PATH} has mode {oct(mode)}, expected 0o600")

    # Enforce ownership (must be owned by current process uid)
    if st.st_uid != os.getuid():
        raise PermissionError(
            f"Key file {KEY_PATH} owned by uid {st.st_uid}, expected {os.getuid()}"
        )

    return KEY_PATH.read_text().strip().encode()


# ── Canonical JSON (deterministic serialization) ──────────────────────


def canonical(obj: Dict[str, Any]) -> str:
    """
    Deterministic JSON serialization for signing.
    Keys sorted, no whitespace, consistent encoding.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


# ── Signing ───────────────────────────────────────────────────────────


def sign_outcome(outcome: Dict[str, Any], seq: int) -> Dict[str, Any]:
    """
    Sign an outcome row with HMAC-SHA256.

    The signature covers:
      - spec version prefix
      - sequence number
      - canonical JSON of the outcome
      - previous signature hash (chain linkage)

    Returns a signature stub dict for outcomes.sig.jsonl.
    """
    key = _ensure_key()

    # Get previous signature for chain linkage
    prev_hash = _get_last_sig_hash()

    # Build the signable payload
    signable = {
        "spec": SPEC_VERSION,
        "seq": seq,
        "prev_hash": prev_hash,
        "outcome_hash": hashlib.sha256(canonical(outcome).encode()).hexdigest(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    signable_bytes = canonical(signable).encode()
    sig = hmac.new(key, signable_bytes, hashlib.sha256).hexdigest()

    return {
        "seq": seq,
        "outcome_hash": signable["outcome_hash"],
        "signature": sig,
        "prev_hash": prev_hash,
        "timestamp": signable["timestamp"],
        "spec": SPEC_VERSION,
    }


def _get_last_sig_hash() -> str:
    """Get the hash of the last signature for chain linkage."""
    if not SIG_PATH.exists():
        return "0" * 64  # Genesis hash

    lines = SIG_PATH.read_text().strip().split("\n")
    if not lines or not lines[-1].strip():
        return "0" * 64

    try:
        last = json.loads(lines[-1])
        return hashlib.sha256(canonical(last).encode()).hexdigest()
    except (json.JSONDecodeError, KeyError):
        return "0" * 64


def _append_sig(sig_entry: Dict[str, Any]) -> None:
    """Append a signature stub to outcomes.sig.jsonl."""
    SIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SIG_PATH.open("a") as f:
        f.write(json.dumps(sig_entry) + "\n")


# ── Verification ─────────────────────────────────────────────────────


def verify_chain(
    start_seq: int = 1,
    end_seq: Optional[int] = None,
) -> Tuple[bool, List[str], List[str]]:
    """
    Walk outcomes.jsonl and verify the signature chain.

    Returns:
        (all_valid, errors, warnings)

    Verification checks:
      1. Each outcome has a corresponding signature stub
      2. HMAC signature matches (key + canonical JSON + prev_hash)
      3. Chain linkage: prev_hash matches actual previous signature
    """
    key = _ensure_key()
    errors: List[str] = []
    warnings: List[str] = []

    # Read outcomes
    if not OUTCOMES_PATH.exists():
        errors.append(f"outcomes.jsonl not found at {OUTCOMES_PATH}")
        return False, errors, warnings

    outcomes = _read_jsonl(OUTCOMES_PATH)
    sigs = _read_jsonl(SIG_PATH) if SIG_PATH.exists() else []

    if not outcomes:
        warnings.append("outcomes.jsonl is empty")
        return True, errors, warnings

    # Determine range
    total = len(outcomes)
    actual_end = min(end_seq or total, total)
    actual_start = max(1, start_seq)

    if actual_start > actual_end:
        errors.append(f"start_seq ({actual_start}) > end_seq ({actual_end})")
        return False, errors, warnings

    # Build signature index by seq
    sig_index = {}
    for s in sigs:
        seq = s.get("seq")
        if seq is not None:
            sig_index[seq] = s

    prev_hash = "0" * 64  # Genesis
    verified_count = 0

    for i in range(actual_start - 1, actual_end):
        seq = i + 1
        outcome = outcomes[i]

        sig = sig_index.get(seq)
        if not sig:
            warnings.append(f"seq {seq}: no signature stub — unsigned")
            continue

        # Verify outcome hash matches
        outcome_hash = hashlib.sha256(canonical(outcome).encode()).hexdigest()
        if sig.get("outcome_hash") != outcome_hash:
            errors.append(
                f"seq {seq}: outcome_hash mismatch "
                f"(expected {outcome_hash[:16]}..., got {sig.get('outcome_hash', '')[:16]}...)"
            )
            continue

        # Verify chain linkage
        if sig.get("prev_hash") != prev_hash:
            errors.append(
                f"seq {seq}: chain break "
                f"(expected prev_hash={prev_hash[:16]}..., got {sig.get('prev_hash', '')[:16]}...)"
            )
            continue

        # Verify HMAC signature
        signable = {
            "spec": sig.get("spec", SPEC_VERSION),
            "seq": seq,
            "prev_hash": sig.get("prev_hash", prev_hash),
            "outcome_hash": outcome_hash,
            "timestamp": sig.get("timestamp", ""),
        }
        signable_bytes = canonical(signable).encode()
        expected_sig = hmac.new(key, signable_bytes, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, sig.get("signature", "")):
            errors.append(f"seq {seq}: HMAC signature invalid")
            continue

        # Update prev_hash for next iteration
        prev_hash = hashlib.sha256(canonical(sig).encode()).hexdigest()
        verified_count += 1

    all_valid = len(errors) == 0
    if all_valid:
        warnings.append(f"Verified {verified_count} of {actual_end - actual_start + 1} rows")

    return all_valid, errors, warnings


def _read_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Read a JSONL file, tolerating partial/corrupt lines."""
    entries = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


# ── Sign all unsigned outcomes (batch) ────────────────────────────────


def sign_unsigned() -> int:
    """
    Sign all outcomes that don't yet have a signature stub.
    Returns count of newly signed outcomes.
    """
    outcomes = _read_jsonl(OUTCOMES_PATH)
    sigs = _read_jsonl(SIG_PATH) if SIG_PATH.exists() else []

    signed_seqs = {s.get("seq") for s in sigs if s.get("seq") is not None}
    count = 0

    for i, outcome in enumerate(outcomes):
        seq = i + 1
        if seq not in signed_seqs:
            sig_entry = sign_outcome(outcome, seq)
            _append_sig(sig_entry)
            count += 1

    return count


# ── CLI ───────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="VAULT999 Notary — HMAC signature chain")
    sub = parser.add_subparsers(dest="command")

    # verify
    v = sub.add_parser("verify", help="Verify signature chain")
    v.add_argument("--last", type=int, default=200, help="Verify last N rows (default 200)")
    v.add_argument("--start", type=int, default=None, help="Start sequence number")
    v.add_argument("--end", type=int, default=None, help="End sequence number")

    # sign
    s = sub.add_parser("sign", help="Sign all unsigned outcomes")

    args = parser.parse_args()

    if args.command == "verify":
        outcomes = _read_jsonl(OUTCOMES_PATH)
        total = len(outcomes)

        start = args.start
        end = args.end

        if start is None and end is None:
            start = max(1, total - args.last + 1)
            end = total

        valid, errors, warnings = verify_chain(start, end)

        print(f"VAULT999 Notary — Chain Verification")
        print(f"  Range: seq {start}..{end} (total outcomes: {total})")
        print(f"  Spec: {SPEC_VERSION}")
        print(f"  Verdict: {'VALID' if valid else 'INVALID'}")

        for w in warnings:
            print(f"  ⚠️  {w}")
        for e in errors:
            print(f"  ❌ {e}")

        sys.exit(0 if valid else 1)

    elif args.command == "sign":
        count = sign_unsigned()
        print(f"Signed {count} previously-unsigned outcomes")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
