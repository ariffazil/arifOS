#!/usr/bin/env python3
"""emit_release_attestation.py — G1: signed release provenance attestation.

Binds one release into a single signed statement:

    Source (commit, tree hash, dirty) → Build (wheel sha256, canon manifest
    sha) → Governance (capability hash) → Runtime (deployed commit, drift,
    status) — Ed25519-signed (sovereign key, agent-autonomous per doctrine).

Ledger: /opt/arifos/releases/attestations/<ts>-<commit>.json (append-only)
+ latest.json. --verify independently recomputes every re-computable field
and checks the signature against the embedded public key. The runtime block
is a historical record (witnessed at emit time); live state checks compare
the stamp and the kernel's own drift flag.

Chain source: release-manifest.json (wheel sha, canon sha) from
deploy-release.sh Step 5 — this emitter binds it, never re-derives it.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import rfc8785
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

REPO = Path("/root/arifOS")
RELEASES = Path("/opt/arifos/releases")
LEDGER = RELEASES / "attestations"
PEM_PATH = Path("/root/.secrets/aaa-identity/keys/arif_private.pem")
KEY_ID = "arif-f13-rootkey-ed25519"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def _jcs_sha(obj) -> str:
    return "sha256:" + hashlib.sha256(rfc8785.dumps(obj)).hexdigest()


def build_body(manifest: dict) -> dict:
    commit = manifest["git_commit"]
    tree_hash = _git("rev-parse", f"{commit}^{{tree}}")
    dirty = bool(_git("status", "--porcelain"))
    cap_state = json.loads(
        _git("show", f"{commit}:static/.well-known/capability_hash.json")
    )
    health = {}
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1:8088/health", timeout=8
        ) as r:
            health = json.load(r).get("software_release", {})
    except Exception:
        health = {}
    return {
        "attestation_version": 1,
        "emitted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "repo": "ariffazil/arifOS",
            "commit": commit,
            "tree_hash": tree_hash,
            "dirty_at_emit": dirty,
        },
        "build": {
            "wheel_name": manifest.get("wheel_name"),
            "wheel_sha256": manifest.get("wheel_sha256"),
            "build_timestamp": manifest.get("build_timestamp"),
            "canon_manifest_sha256": manifest.get("canon_manifest_sha256"),
            "canon_version": manifest.get("canon_version"),
            "venv_python": manifest.get("venv_python"),
        },
        "governance": {
            "capability_hash": cap_state.get("capability_hash"),
            "capability_record_count": cap_state.get("record_count"),
            "constitution_binding": manifest.get("canon_manifest_sha256"),
        },
        "runtime_witnessed": {
            "deployed_commit": str(health.get("deployed_commit", ""))[:9] or None,
            "drift": health.get("drift"),
            "note": "historical record at emit time; live truth = stamp + /health",
        },
    }


def sign(body: dict) -> dict:
    payload = rfc8785.dumps(body)
    key = serialization.load_pem_private_key(PEM_PATH.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise SystemExit("FATAL: sovereign key is not Ed25519")
    sig = base64.b64encode(key.sign(payload)).decode()
    pub = base64.b64encode(
        key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode()
    return {
        **body,
        "body_sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "signature": {
            "algorithm": "Ed25519",
            "key_id": KEY_ID,
            "public_key_raw_b64": pub,
            "value_b64": sig,
        },
    }


def emit() -> int:
    manifest = json.loads((RELEASES / "release-manifest.json").read_text())
    att = sign(build_body(manifest))
    LEDGER.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = LEDGER / f"{ts}-{att['source']['commit'][:9]}.json"
    path.write_text(json.dumps(att, indent=2, sort_keys=True) + "\n")
    (LEDGER / "latest.json").write_text(json.dumps(att, indent=2, sort_keys=True) + "\n")
    print(f"attested {att['source']['commit'][:9]} -> {path}")
    print(f"  capability: {att['governance']['capability_hash']}")
    print(f"  wheel:      {att['build']['wheel_sha256']}")
    print(f"  body_sha:   {att['body_sha256']}")
    return 0


def verify() -> int:
    att = json.loads((LEDGER / "latest.json").read_text())
    problems = []
    sig = att.pop("signature")
    body_sha = att.pop("body_sha256")
    payload = rfc8785.dumps(att)

    if "sha256:" + hashlib.sha256(payload).hexdigest() != body_sha:
        problems.append("body_sha256 mismatch (attestation body altered)")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    pub = Ed25519PublicKey.from_public_bytes(base64.b64decode(sig["public_key_raw_b64"]))
    try:
        pub.verify(base64.b64decode(sig["value_b64"]), payload)
    except Exception:
        problems.append("Ed25519 signature INVALID")

    commit = att["source"]["commit"]
    if att["source"]["tree_hash"] != _git("rev-parse", f"{commit}^{{tree}}"):
        problems.append("source.tree_hash mismatch")
    manifest = json.loads((RELEASES / "release-manifest.json").read_text())
    if manifest.get("git_commit", "").startswith(commit[:7]):
        if att["build"]["wheel_sha256"] != manifest.get("wheel_sha256"):
            problems.append("wheel_sha256 vs release-manifest mismatch")
        cap = json.loads(
            _git("show", f"{commit}:static/.well-known/capability_hash.json")
        )
        if att["governance"]["capability_hash"] != cap.get("capability_hash"):
            problems.append("capability_hash vs committed witness mismatch")
    stamp = (RELEASES / "deployed-commit").read_text().strip()
    if not stamp.startswith(commit[:7]):
        problems.append(f"stamp {stamp[:9]} != attested {commit[:9]} (newer deploy exists)")

    if problems:
        print("ATTESTATION VERIFY FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"attestation VERIFIED: {commit[:9]} · capability {att['governance']['capability_hash'][:23]}… · signature valid")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        return verify()
    return emit()


if __name__ == "__main__":
    sys.exit(main())
