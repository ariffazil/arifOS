#!/usr/bin/env python3
"""Atomic, fail-closed publication of the signed Observatory snapshot.

F1 AMANAH guarantees:
  * Only the signed latest snapshot, the public PEM, and the DID documents
    are copied. The private key is NEVER touched, NEVER copied, NEVER logged.
  * Each artifact is staged via a sibling ``.<name>.tmp`` file and then
    promoted with ``os.replace`` — readers always see either the previous
    version or the new version, never a partial write.
  * After every write the bytes are re-read and SHA-256 is re-verified
    against the pre-write digest. Any mismatch raises and aborts the run
    so the caller never sees a misleading "published" receipt.

F11 AUDIT guarantees:
  * A receipt dict is returned that lists every artifact with absolute path,
    byte size, and SHA-256. The receipt is suitable for SEAL-grade audit
    but never leaves the caller's process unless the caller persists it.

F13 SOVEREIGN guarantees:
  * The public DID document advertises the WORKING static snapshot endpoint,
    never the deadlocked ``/api/observatory/v1/snapshot`` endpoint.
  * The ``OBSERVATORY_PUBLISH_TARGET`` env var gates side effects. With the
    variable unset (the default), publish is a no-op — no writes occur to
    ``/var/www``, ``/etc/caddy``, or any webroot. Live publication requires
    explicit operator opt-in (T3 sovereign ack).

Usage as a library::

    from observatory_publish import publish_latest_snapshot
    receipt = publish_latest_snapshot(Path("/var/www/html/arifos/.well-known"))
    print(receipt["files"])

Usage from the canonical emitter is gated by ``OBSERVATORY_PUBLISH_TARGET``.
Tests instantiate a temp target dir and call ``publish_latest_snapshot``
directly with explicit ``snap_dir`` and ``keys_dir`` overrides.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

# cryptography is a hard dep of arifOS runtime; re-use the same primitives
# the canonical signing helper uses (observatory_signing.py).
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# ─── Canonical paths (override at call site for tests) ─────────────────────
DEFAULT_SNAP_DIR: Path = Path("/root/.arifos/observatory/snapshots")
DEFAULT_KEYS_DIR: Path = Path("/root/.arifos/observatory/keys")

# Public web-facing identifiers. The service endpoint is the WORKING static
# snapshot URL — never the deadlocked /api/observatory/v1/snapshot endpoint.
DID_BASE_URL: str = "https://arifos.arif-fazil.com"
DID_ID: str = "did:web:arifos.arif-fazil.com"
DID_KEY_SUFFIX: str = "observatory-key-1"
DID_SERVICE_SUFFIX: str = "observatory-snapshot"
SNAPSHOT_SERVICE_PATH: str = "/.well-known/observatory-snapshot-latest.json"
VERIFICATION_URL: str = f"{DID_BASE_URL}/.well-known/did-arifos-observatory.json"

# Base58btc alphabet used by the multibase 'z' prefix (RFC 4648 base58 + BIP-122 ordering).
BASE58BTC_ALPHABET: str = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ED25519_MULTICODEC_PREFIX: bytes = b"\xed\x01"

# The artifacts publish copies into the target directory. The set is explicit
# so a future stray private key file can never sneak in via a glob.
PUBLIC_ARTIFACT_NAMES: tuple[str, ...] = (
    "snapshot_latest.json",
    "observatory_signing_key.pub.pem",
    "did-arifos-observatory.json",
    "did.json",
)


# ─── Pure helpers (no filesystem I/O) ──────────────────────────────────────


def _b58encode(data: bytes) -> str:
    """RFC 4648 base58btc encoder (used by multibase 'z' prefix)."""
    n = int.from_bytes(data, "big")
    out_chars: list[str] = []
    while n > 0:
        n, r = divmod(n, 58)
        out_chars.append(BASE58BTC_ALPHABET[r])
    # Preserve leading zero bytes (each '1' maps to one 0x00 byte).
    pad = 0
    for byte in data:
        if byte == 0:
            pad += 1
        else:
            break
    return ("1" * pad) + "".join(reversed(out_chars))


def encode_multibase_ed25519(raw_pubkey: bytes) -> str:
    """Multibase encoding for an Ed25519 public key: ``z`` + base58btc(0xed01||raw)."""
    if len(raw_pubkey) != 32:
        raise ValueError(f"Ed25519 public key must be 32 bytes, got {len(raw_pubkey)}")
    return "z" + _b58encode(ED25519_MULTICODEC_PREFIX + raw_pubkey)


def build_did_document(
    *,
    public_key_raw: bytes,
    did_id: str = DID_ID,
    key_id_suffix: str = DID_KEY_SUFFIX,
    snapshot_service_endpoint: str,
) -> dict[str, Any]:
    """Return the canonical Observatory DID document.

    The exact same dict is written to ``did-arifos-observatory.json`` AND
    ``did.json`` so the two filenames are byte-identical and trivially
    verifiable. No private material, no stale API endpoint — just the
    public multikey and the static snapshot URL.
    """
    return {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/multikey/v1",
        ],
        "id": did_id,
        "verificationMethod": [
            {
                "id": f"{did_id}#{key_id_suffix}",
                "type": "Multikey",
                "controller": did_id,
                "publicKeyMultibase": encode_multibase_ed25519(public_key_raw),
            }
        ],
        "assertionMethod": [f"{did_id}#{key_id_suffix}"],
        "service": [
            {
                "id": f"{did_id}#{DID_SERVICE_SUFFIX}",
                "type": "https://arifos.arif-fazil.com/ns/ObservatoryWitness",
                "serviceEndpoint": snapshot_service_endpoint,
            }
        ],
    }


# ─── Filesystem action (the only mutating entry point) ─────────────────────


def _atomic_write_bytes(target_dir: Path, name: str, payload: bytes) -> Path:
    """Stage ``payload`` to ``.<name>.tmp`` then ``os.replace`` into place.

    The temp file is created with restrictive permissions (0o600) so an
    interrupted run does not leak world-readable artifacts. The replace is
    atomic on POSIX, so concurrent readers see either the previous version
    or the new version, never a half-written file.
    """
    target_path = target_dir / name
    tmp_path = target_dir / f".{name}.tmp"
    # Defense in depth — refuse to ever write a file that looks like the
    # private key, even if a caller somehow constructs the call.
    if name in {"observatory_signing_key.pem", "observatory_signing_key"}:
        raise ValueError(f"refusing to publish private-key material: {name!r}")
    # Mode argument is honoured on POSIX; on Windows it is ignored.
    fd = os.open(str(tmp_path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        os.write(fd, payload)
    finally:
        os.close(fd)
    os.replace(str(tmp_path), str(target_path))
    return target_path


def publish_latest_snapshot(
    target_dir: str | os.PathLike[str] | None,
    *,
    snap_dir: str | os.PathLike[str] = DEFAULT_SNAP_DIR,
    keys_dir: str | os.PathLike[str] = DEFAULT_KEYS_DIR,
    did_id: str = DID_ID,
    key_id_suffix: str = DID_KEY_SUFFIX,
    snapshot_service_path: str = SNAPSHOT_SERVICE_PATH,
    overwrite: bool = True,
) -> dict[str, Any]:
    """Atomically copy the signed latest snapshot + public PEM + DID documents.

    Parameters
    ----------
    target_dir
        Destination directory. May be ``None`` to express "skip live
        publication" — the helper returns a no-op receipt instead of raising.
        This is the explicit F13 opt-out: no env var, no implicit webroot.
    snap_dir
        Override the snapshot directory (for tests).
    keys_dir
        Override the keys directory (for tests).
    did_id, key_id_suffix, snapshot_service_path
        Override defaults if a future organ needs its own DID.

    Returns
    -------
    dict
        Receipt with ``status``, ``target_dir``, ``files`` (path/size/sha256
        per artifact), ``did`` (the canonical document), and
        ``verification_url``. If ``target_dir`` is ``None`` the receipt has
        ``status="SKIPPED"`` and an empty ``files`` map.

    Raises
    ------
    FileNotFoundError
        ``snapshot_latest.json`` or ``observatory_signing_key.pub.pem`` is
        missing from the source directories.
    ValueError, TypeError
        Snapshot JSON is malformed, signature is not in ``"signed"`` state,
        or the public key is not Ed25519.
    OSError
        The target directory cannot be created or written to.
    """
    if target_dir is None:
        return {
            "status": "SKIPPED",
            "reason": "target_dir is None; no live publication requested",
            "target_dir": None,
            "files": {},
            "did": None,
            "verification_url": VERIFICATION_URL,
        }

    target = Path(target_dir).resolve()
    snap = Path(snap_dir).resolve()
    keys = Path(keys_dir).resolve()

    src_snapshot = snap / "snapshot_latest.json"
    src_pubkey = keys / "observatory_signing_key.pub.pem"

    # ── Step 1: locate + validate source artifacts (fail-closed) ──────
    if not src_snapshot.is_file():
        raise FileNotFoundError(f"signed latest snapshot missing: {src_snapshot}")
    if not src_pubkey.is_file():
        raise FileNotFoundError(f"observatory public key missing: {src_pubkey}")

    snap_bytes = src_snapshot.read_bytes()
    try:
        snapshot = json.loads(snap_bytes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"snapshot_latest.json is not valid JSON: {exc}") from exc
    if not isinstance(snapshot, dict):
        raise TypeError("snapshot_latest.json must decode to a JSON object")
    sig = snapshot.get("signature")
    if not isinstance(sig, dict) or sig.get("state") != "signed":
        raise ValueError(
            "snapshot_latest.json signature is not in 'signed' state — refusing to publish"
        )

    pub_pem_bytes = src_pubkey.read_bytes()
    public_key = serialization.load_pem_public_key(pub_pem_bytes)
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError("observatory public key is not Ed25519")
    raw_pub = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    # ── Step 2: build the canonical DID document ───────────────────────
    snapshot_service_url = f"{DID_BASE_URL.rstrip('/')}{snapshot_service_path}"
    did_document = build_did_document(
        public_key_raw=raw_pub,
        did_id=did_id,
        key_id_suffix=key_id_suffix,
        snapshot_service_endpoint=snapshot_service_url,
    )
    did_bytes = json.dumps(did_document, indent=2, sort_keys=True).encode("utf-8")

    # ── Step 3: ensure target exists, refuse to descend into source ───
    if target in (snap, keys) or snap in target.parents or keys in target.parents:
        raise ValueError(f"refusing to publish into source tree: {target}")
    target.mkdir(parents=True, exist_ok=True)

    # ── Step 4: atomic writes — single explicit allowlist, no glob ────
    artifacts: dict[str, bytes] = {
        "snapshot_latest.json": snap_bytes,
        "observatory_signing_key.pub.pem": pub_pem_bytes,
        "did-arifos-observatory.json": did_bytes,
        "did.json": did_bytes,
    }

    receipt_files: dict[str, dict[str, Any]] = {}
    written_paths: list[Path] = []

    for name in PUBLIC_ARTIFACT_NAMES:
        payload = artifacts[name]
        if (not overwrite) and (target / name).exists():
            receipt_files[name] = {
                "path": str(target / name),
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "skipped": True,
            }
            continue
        path = _atomic_write_bytes(target, name, payload)
        written_paths.append(path)
        receipt_files[name] = {
            "path": str(path),
            "size_bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }

    # ── Step 5: post-write verification — re-read every file ───────────
    for name, info in receipt_files.items():
        if info.get("skipped"):
            continue
        on_disk = (target / name).read_bytes()
        on_disk_sha = hashlib.sha256(on_disk).hexdigest()
        if on_disk_sha != info["sha256"]:
            # Best-effort cleanup of any partial publish so a retry can run clean.
            for cleanup in written_paths:
                try:
                    cleanup.unlink()
                except OSError:
                    pass
            raise RuntimeError(
                f"post-write verification failed for {name!r}: expected sha256={info['sha256']}, "
                f"on-disk sha256={on_disk_sha}"
            )

    return {
        "status": "PUBLISHED",
        "target_dir": str(target),
        "files": receipt_files,
        "did": did_document,
        "verification_url": VERIFICATION_URL,
    }


def main() -> int:
    """CLI entry point. Reads target from ``OBSERVATORY_PUBLISH_TARGET``.

    Exits 0 on success or skip, 1 on any failure. Never writes to a webroot
    without explicit operator opt-in.
    """
    target = os.environ.get("OBSERVATORY_PUBLISH_TARGET", "").strip() or None
    print("=== arifOS Observatory Publisher — atomic snapshot publication ===", file=sys.stderr)
    try:
        receipt = publish_latest_snapshot(target)
    except Exception as exc:
        print(f"  publish: FAILED {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    if receipt["status"] == "SKIPPED":
        print(
            "  publish: SKIPPED (OBSERVATORY_PUBLISH_TARGET unset — no live webroot writes)",
            file=sys.stderr,
        )
        return 0
    print(f"  publish: OK target={receipt['target_dir']}", file=sys.stderr)
    for name, info in receipt["files"].items():
        flag = "skipped" if info.get("skipped") else "wrote"
        print(
            f"    {flag:7s} {name} ({info['size_bytes']} bytes, sha256={info['sha256'][:12]})",
            file=sys.stderr,
        )
    print(f"  verification_url: {receipt['verification_url']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
