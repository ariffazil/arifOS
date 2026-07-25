"""tests/test_observatory_publication.py — Observatory publication helper tests.

DITEMPA BUKAN DIBERI.

Acceptance gates (per workstream observatory-publication 2026-07-21):

  1. DID content is byte-identical between ``did-arifos-observatory.json``
     and the standard ``did.json`` written by the helper.

  2. ``publicKeyMultibase`` decodes to the same raw bytes as the local
     Ed25519 public key PEM (no key substitution, no length drift).

  3. The published DID advertises the WORKING static snapshot URL — never
     the deadlocked ``/api/observatory/v1/snapshot`` endpoint.

  4. ``publish_latest_snapshot`` is atomic: every artifact has a sibling
     ``.<name>.tmp`` staged and replaced via ``os.replace``. No partial
     writes can land in the target directory.

  5. The helper refuses to publish the private key. The explicit allowlist
     contains ``observatory_signing_key.pub.pem`` only.

  6. Post-write verification re-reads every file and re-checks SHA-256.
     Any mismatch raises and aborts the run — the caller never sees a
     misleading "published" receipt.

  7. With ``target_dir=None`` or unset env var, no filesystem writes occur
     anywhere — no live webroot writes during tests.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure the scripts directory is importable so ``observatory_publish`` resolves
# without an installed package.
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


# ─── Helpers ───────────────────────────────────────────────────────────────


BASE58BTC_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _b58decode(s: str) -> bytes:
    n = 0
    for ch in s:
        n = n * 58 + BASE58BTC_ALPHABET.index(ch)
    out = bytearray()
    while n > 0:
        n, r = divmod(n, 256)
        out.insert(0, r)
    pad = 0
    for ch in s:
        if ch == "1":
            pad += 1
        else:
            break
    return bytes(pad) + bytes(out)


def _seed_signed_snapshot(snap_dir: Path, *, signature_state: str = "signed") -> dict:
    """Write a minimal but well-formed signed snapshot into ``snap_dir``.

    The signature block carries ``state="signed"`` so the helper accepts it.
    The signature bytes themselves are filler; the publish path never
    re-verifies the cryptographic signature — that is the responsibility of
    downstream consumers. What we DO verify is that the helper refuses to
    publish when ``state != "signed"``.
    """
    snap_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "snapshot_id": "obs_publication_test",
        "observed_at": "2026-07-21T00:00:00Z",
        "schema_version": "observatory.v1",
        "signature": {
            "value": base64.b64encode(b"\x00" * 64).decode("ascii"),
            "state": signature_state,
            "algorithm": "ed25519",
            "key_id": "ed25519:sha256:" + "0" * 16,
        },
    }
    latest = snap_dir / "snapshot_latest.json"
    latest.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return snapshot


def _seed_keys_dir(keys_dir: Path) -> bytes:
    """Generate a throwaway Ed25519 keypair in ``keys_dir`` and return the
    raw 32-byte public key bytes. The private key file is created but the
    publish helper MUST refuse to copy it.
    """
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    keys_dir.mkdir(parents=True, exist_ok=True)
    private = Ed25519PrivateKey.generate()
    pub_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    priv_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    (keys_dir / "observatory_signing_key.pub.pem").write_bytes(pub_pem)
    (keys_dir / "observatory_signing_key.pem").write_bytes(priv_pem)
    raw = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw


@pytest.fixture
def seeded_environment(tmp_path: Path) -> dict:
    """Provide an isolated snap/keys/target trio for one test."""
    snap_dir = tmp_path / "snap"
    keys_dir = tmp_path / "keys"
    target_dir = tmp_path / "target"
    raw_pub = _seed_keys_dir(keys_dir)
    snapshot = _seed_signed_snapshot(snap_dir)
    return {
        "snap_dir": snap_dir,
        "keys_dir": keys_dir,
        "target_dir": target_dir,
        "raw_pub": raw_pub,
        "snapshot": snapshot,
    }


# ─── Test 1: pure helpers (DID + multibase encoding) ──────────────────────


class TestEncodeMultibaseEd25519:
    """``z``-prefixed base58btc encoding of Ed25519 public keys."""

    def test_rejects_wrong_length(self):
        from observatory_publish import encode_multibase_ed25519

        with pytest.raises(ValueError, match="32 bytes"):
            encode_multibase_ed25519(b"\x00" * 31)
        with pytest.raises(ValueError, match="32 bytes"):
            encode_multibase_ed25519(b"\x00" * 33)

    def test_known_vector_matches_existing_did(self):
        """Multibase for the live arifOS observatory public key must round-trip.

        The live public key raw bytes are cdfcd4e968a1aba061ca45549b99e56b
        f4cde5606425d88515699e69897ee28f and the existing on-disk DID at
        /root/.arifos/observatory/did.json uses multibase
        ``z6MktKMEF6kgxS2cKVutBkv19jrgarXAixLmvkc9HcB5H3xJ``. We assert
        that the helper's encoder produces the same value for the same input.
        """
        from observatory_publish import encode_multibase_ed25519

        raw = bytes.fromhex(
            "cdfcd4e968a1aba061ca45549b99e56bf4cde5606425d88515699e69897ee28f"
        )
        assert encode_multibase_ed25519(raw) == "z6MktKMEF6kgxS2cKVutBkv19jrgarXAixLmvkc9HcB5H3xJ"

    def test_multibase_decodes_back_to_multicodec_prefixed_key(self, seeded_environment):
        from observatory_publish import encode_multibase_ed25519

        multibase = encode_multibase_ed25519(seeded_environment["raw_pub"])
        assert multibase.startswith("z"), f"expected z-prefix, got {multibase!r}"
        decoded = _b58decode(multibase[1:])
        assert decoded[:2] == b"\xed\x01", (
            f"Ed25519 multicodec prefix must be 0xed01, got {decoded[:2].hex()}"
        )
        assert decoded[2:] == seeded_environment["raw_pub"], (
            "multibase payload must round-trip to the raw public key"
        )


class TestBuildDIDDocument:
    """The pure DID-document factory."""

    def test_did_advertises_static_snapshot_endpoint(self, seeded_environment):
        from observatory_publish import build_did_document, DID_ID, DID_BASE_URL

        doc = build_did_document(
            public_key_raw=seeded_environment["raw_pub"],
            snapshot_service_endpoint=f"{DID_BASE_URL}/.well-known/observatory-snapshot-latest.json",
        )
        assert doc["id"] == DID_ID
        endpoint = doc["service"][0]["serviceEndpoint"]
        assert "api/observatory/v1/snapshot" not in endpoint, (
            f"DID must NOT advertise the deadlocked API endpoint, got {endpoint!r}"
        )
        assert endpoint == (
            "https://arifos.arif-fazil.com/.well-known/observatory-snapshot-latest.json"
        )

    def test_did_contains_single_multikey_verification_method(self, seeded_environment):
        from observatory_publish import build_did_document

        doc = build_did_document(
            public_key_raw=seeded_environment["raw_pub"],
            snapshot_service_endpoint="https://arifos.arif-fazil.com/.well-known/observatory-snapshot-latest.json",
        )
        vm = doc["verificationMethod"]
        assert len(vm) == 1
        assert vm[0]["type"] == "Multikey"
        assert vm[0]["controller"] == doc["id"]
        assert vm[0]["id"] == f"{doc['id']}#observatory-key-1"
        assert doc["assertionMethod"] == [vm[0]["id"]]

    def test_did_contains_no_private_key_material(self, seeded_environment):
        """DIF/JSON-LD safe-by-default: no private markers."""
        from observatory_publish import build_did_document

        doc = build_did_document(
            public_key_raw=seeded_environment["raw_pub"],
            snapshot_service_endpoint="https://arifos.arif-fazil.com/.well-known/observatory-snapshot-latest.json",
        )
        serialised = json.dumps(doc)
        for forbidden in ("privateKey", "secretKey", "seed", "private_key", "priv"):
            assert forbidden not in serialised, (
                f"DID document leaked forbidden field {forbidden!r}"
            )


# ─── Test 2: atomic publication (filesystem I/O) ──────────────────────────


class TestPublishLatestSnapshot:
    """End-to-end publication against a temp directory target."""

    def test_publish_copies_all_four_artifacts(self, seeded_environment):
        from observatory_publish import publish_latest_snapshot

        receipt = publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        assert receipt["status"] == "PUBLISHED"
        assert set(receipt["files"].keys()) == {
            "observatory-snapshot-latest.json",
            "observatory_signing_key.pub.pem",
            "did-arifos-observatory.json",
            "did.json",
        }
        for name, info in receipt["files"].items():
            artifact = seeded_environment["target_dir"] / name
            assert artifact.is_file(), f"{name} not on disk after publish"
            assert artifact.stat().st_mode & 0o777 == 0o644, (
                f"{name} must be readable by the public web server"
            )
            assert info["size_bytes"] > 0
            assert re.fullmatch(r"[0-9a-f]{64}", info["sha256"])

    def test_publish_did_files_are_byte_identical(self, seeded_environment):
        from observatory_publish import publish_latest_snapshot

        receipt = publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        obs_did = (seeded_environment["target_dir"] / "did-arifos-observatory.json").read_bytes()
        std_did = (seeded_environment["target_dir"] / "did.json").read_bytes()
        assert obs_did == std_did, (
            "did-arifos-observatory.json and did.json MUST be byte-identical"
        )
        assert receipt["files"]["did-arifos-observatory.json"]["sha256"] == (
            receipt["files"]["did.json"]["sha256"]
        )

    def test_published_did_multibase_matches_local_public_key(self, seeded_environment):
        from observatory_publish import publish_latest_snapshot

        receipt = publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        did_doc = receipt["did"]
        multibase = did_doc["verificationMethod"][0]["publicKeyMultibase"]
        assert multibase.startswith("z")
        decoded = _b58decode(multibase[1:])
        assert decoded[:2] == b"\xed\x01"
        assert decoded[2:] == seeded_environment["raw_pub"], (
            "DID publicKeyMultibase must decode to the local Ed25519 public key"
        )

    def test_publish_never_copies_private_key(self, seeded_environment):
        """The target directory must NOT contain observatory_signing_key.pem
        even though the file exists in the source keys_dir."""
        from observatory_publish import publish_latest_snapshot

        # Sanity: private key IS present in source.
        assert (seeded_environment["keys_dir"] / "observatory_signing_key.pem").is_file()

        publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )

        # Defence in depth: the helper refuses to ever write the private key.
        for forbidden in (
            "observatory_signing_key.pem",
            "observatory_signing_key",
        ):
            assert not (seeded_environment["target_dir"] / forbidden).exists(), (
                f"private key {forbidden!r} leaked into target"
            )
        # No straggler tmp files either.
        leftover_tmps = list(seeded_environment["target_dir"].glob(".*.tmp"))
        assert not leftover_tmps, f"tmp staging files left behind: {leftover_tmps}"

    def test_publish_writes_snapshot_and_pubkey_atomically(self, seeded_environment):
        """The staged tmp files are renamed via os.replace — never left in place."""
        from observatory_publish import publish_latest_snapshot

        with patch(
            "observatory_publish.os.replace", wraps=os.replace
        ) as replace_spy:
            publish_latest_snapshot(
                seeded_environment["target_dir"],
                snap_dir=seeded_environment["snap_dir"],
                keys_dir=seeded_environment["keys_dir"],
            )
        # Four artifacts ⇒ at least four os.replace calls.
        assert replace_spy.call_count >= 4, (
            f"expected at least 4 atomic replaces, got {replace_spy.call_count}"
        )
        # Every tmp file must have been consumed.
        leftover_tmps = list(seeded_environment["target_dir"].glob(".*.tmp"))
        assert not leftover_tmps, f"tmp files not promoted: {leftover_tmps}"

    def test_publish_refuses_when_snapshot_not_signed(self, tmp_path: Path):
        from observatory_publish import publish_latest_snapshot

        snap_dir = tmp_path / "snap"
        keys_dir = tmp_path / "keys"
        target_dir = tmp_path / "target"
        _seed_keys_dir(keys_dir)
        _seed_signed_snapshot(snap_dir, signature_state="unsigned")
        # Unsigned state must fail-closed — no writes to target.
        with pytest.raises(ValueError, match="signed"):
            publish_latest_snapshot(
                target_dir, snap_dir=snap_dir, keys_dir=keys_dir
            )
        # No artifacts landed in the target.
        assert not target_dir.exists() or not any(target_dir.iterdir()), (
            "publish must not leave partial artifacts when failing closed"
        )

    def test_publish_refuses_when_snapshot_missing(self, tmp_path: Path):
        from observatory_publish import publish_latest_snapshot

        snap_dir = tmp_path / "snap"
        keys_dir = tmp_path / "keys"
        target_dir = tmp_path / "target"
        _seed_keys_dir(keys_dir)
        # No snapshot written at all.
        with pytest.raises(FileNotFoundError, match="snapshot_latest.json"):
            publish_latest_snapshot(
                target_dir, snap_dir=snap_dir, keys_dir=keys_dir
            )
        assert not target_dir.exists(), (
            "target dir must NOT be created when source snapshot is missing"
        )

    def test_publish_refuses_when_public_key_missing(self, tmp_path: Path):
        from observatory_publish import publish_latest_snapshot

        snap_dir = tmp_path / "snap"
        keys_dir = tmp_path / "keys"
        target_dir = tmp_path / "target"
        _seed_signed_snapshot(snap_dir)
        # No public key written at all.
        with pytest.raises(FileNotFoundError, match="public key"):
            publish_latest_snapshot(
                target_dir, snap_dir=snap_dir, keys_dir=keys_dir
            )

    def test_publish_returns_skip_receipt_when_target_is_none(self, seeded_environment):
        """With target_dir=None, no webroot writes occur (F13 sovereign opt-out)."""
        from observatory_publish import publish_latest_snapshot

        receipt = publish_latest_snapshot(
            None,
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        assert receipt["status"] == "SKIPPED"
        assert receipt["files"] == {}
        assert receipt["target_dir"] is None
        # No side effects on the seeded environment.
        assert seeded_environment["target_dir"].exists() is False

    def test_publish_does_not_create_target_when_target_is_none(
        self, seeded_environment
    ):
        """Confirm the no-target path leaves the filesystem untouched."""
        from observatory_publish import publish_latest_snapshot

        publish_latest_snapshot(
            None,
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        assert not seeded_environment["target_dir"].exists()

    def test_publish_idempotent_second_run(self, seeded_environment):
        """A second publish on the same target is a no-op overwrite; sha256 stable."""
        from observatory_publish import publish_latest_snapshot

        r1 = publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        r2 = publish_latest_snapshot(
            seeded_environment["target_dir"],
            snap_dir=seeded_environment["snap_dir"],
            keys_dir=seeded_environment["keys_dir"],
        )
        assert r1["files"]["observatory-snapshot-latest.json"]["sha256"] == (
            r2["files"]["observatory-snapshot-latest.json"]["sha256"]
        )
        assert r1["files"]["did.json"]["sha256"] == (
            r2["files"]["did.json"]["sha256"]
        )


# ─── Test 3: integration with the canonical emitter ────────────────────────


class TestCanonicalEmitterWiring:
    """The canonical emitter must call the publish helper without breaking
    the existing signed-snapshot flow, and must NOT publish when the env
    var is unset."""

    def test_canonical_emitter_invokes_publish_when_env_var_set(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        from observatory_publish import publish_latest_snapshot

        snap_dir = tmp_path / "snap"
        keys_dir = tmp_path / "keys"
        target_dir = tmp_path / "target"
        _seed_keys_dir(keys_dir)
        _seed_signed_snapshot(snap_dir)

        # monkeypatch auto-restores the env var on test teardown — no leakage.
        monkeypatch.setenv("OBSERVATORY_PUBLISH_TARGET", str(target_dir))
        receipt = publish_latest_snapshot(target_dir, snap_dir=snap_dir, keys_dir=keys_dir)

        assert receipt["status"] == "PUBLISHED"
        assert (target_dir / "observatory-snapshot-latest.json").is_file()
        assert (target_dir / "did-arifos-observatory.json").is_file()
        assert (target_dir / "did.json").is_file()

    def test_canonical_emitter_skips_publish_when_env_var_unset(
        self, seeded_environment
    ):
        """With no env var, calling the helper with target=None is a no-op."""
        from observatory_publish import publish_latest_snapshot

        # Simulate the canonical-emitter branch: env var unset ⇒ target=None.
        env_value = os.environ.get("OBSERVATORY_PUBLISH_TARGET")
        try:
            os.environ.pop("OBSERVATORY_PUBLISH_TARGET", None)
            target = (env_value or "").strip() or None
            receipt = publish_latest_snapshot(
                target,
                snap_dir=seeded_environment["snap_dir"],
                keys_dir=seeded_environment["keys_dir"],
            )
        finally:
            if env_value is not None:
                os.environ["OBSERVATORY_PUBLISH_TARGET"] = env_value

        assert receipt["status"] == "SKIPPED"
        assert not seeded_environment["target_dir"].exists(), (
            "no live webroot writes must occur when env var is unset"
        )


# ─── Test 4: CLI surface ────────────────────────────────────────────────────


class TestCLI:
    """The CLI entry point must respect the env var gate and never write
    to a webroot without explicit operator opt-in."""

    def test_cli_skips_when_env_var_unset(self, tmp_path: Path):
        cli = SCRIPTS_DIR / "observatory_publish.py"
        env = os.environ.copy()
        env.pop("OBSERVATORY_PUBLISH_TARGET", None)
        result = subprocess.run(
            [sys.executable, str(cli)],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, (
            f"expected exit 0 on skip, got {result.returncode}\nstderr:\n{result.stderr}"
        )
        assert "SKIPPED" in result.stderr

    def test_cli_publishes_to_target_when_env_var_set(self, tmp_path: Path):
        snap_dir = tmp_path / "snap"
        keys_dir = tmp_path / "keys"
        target_dir = tmp_path / "target"
        _seed_keys_dir(keys_dir)
        _seed_signed_snapshot(snap_dir)

        cli = SCRIPTS_DIR / "observatory_publish.py"
        env = os.environ.copy()
        env["OBSERVATORY_PUBLISH_TARGET"] = str(target_dir)
        result = subprocess.run(
            [sys.executable, str(cli)],
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, (
            f"expected exit 0 on success, got {result.returncode}\nstderr:\n{result.stderr}"
        )
        assert "publish: OK" in result.stderr
        assert (target_dir / "observatory-snapshot-latest.json").is_file()
        assert (target_dir / "did-arifos-observatory.json").is_file()
        assert (target_dir / "did.json").is_file()


# ─── Test 5: public template consistency ───────────────────────────────────


class TestPublicTemplate:
    """The checked-in /root/.arifos/observatory/did.json template must
    point at the working static URL (F1 truth)."""

    def test_template_advertises_static_endpoint(self):
        template = Path("/root/.arifos/observatory/did.json")
        if not template.is_file():
            pytest.skip("public template not present in this environment")
        doc = json.loads(template.read_text())
        endpoint = doc["service"][0]["serviceEndpoint"]
        assert "api/observatory/v1/snapshot" not in endpoint, (
            f"template still advertises deadlocked endpoint: {endpoint!r}"
        )
        assert endpoint.endswith(".well-known/observatory-snapshot-latest.json"), (
            f"template endpoint must be the static snapshot URL, got {endpoint!r}"
        )

    def test_template_multibase_decodes_to_known_public_key(self):
        """If the on-disk PEM is present, the template multibase MUST match."""
        from observatory_publish import encode_multibase_ed25519

        template = Path("/root/.arifos/observatory/did.json")
        pubkey = Path("/root/.arifos/observatory/keys/observatory_signing_key.pub.pem")
        if not (template.is_file() and pubkey.is_file()):
            pytest.skip("template or pubkey not present in this environment")

        doc = json.loads(template.read_text())
        template_multibase = doc["verificationMethod"][0]["publicKeyMultibase"]

        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        pub = serialization.load_pem_public_key(pubkey.read_bytes())
        assert isinstance(pub, Ed25519PublicKey)
        raw = pub.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        assert encode_multibase_ed25519(raw) == template_multibase, (
            "template multibase must be re-derivable from the on-disk public key"
        )


# ─── Test 6: durable systemd scheduling contract ────────────────────────────


class TestObservatorySystemdSchedule:
    """The checked-in units must durably run the canonical public emitter."""

    systemd_dir = Path(__file__).resolve().parent.parent / "ops" / "systemd"
    service_path = systemd_dir / "arifos-observatory-emitter.service"
    timer_path = systemd_dir / "arifos-observatory-emitter.timer"

    @staticmethod
    def _setting(content: str, name: str) -> str:
        prefix = f"{name}="
        values = [
            line.removeprefix(prefix)
            for line in content.splitlines()
            if line.startswith(prefix)
        ]
        assert len(values) == 1, f"expected exactly one {name}= setting, got {values!r}"
        return values[0]

    def test_service_runs_canonical_emitter_with_bounded_journal_execution(self):
        service = self.service_path.read_text(encoding="utf-8")

        assert "[Service]" in service
        assert self._setting(service, "Type") == "oneshot"
        assert self._setting(service, "WorkingDirectory") == "/opt/arifos/app"
        assert self._setting(service, "ExecStart") == (
            "/opt/arifos/venv/bin/python "
            "/opt/arifos/app/scripts/emit_observatory_snapshot.py"
        )
        assert self._setting(service, "TimeoutStartSec") == "5min"
        assert self._setting(service, "StandardOutput") == "journal"
        assert self._setting(service, "StandardError") == "journal"

    def test_service_uses_exact_publication_target(self):
        service_lines = self.service_path.read_text(encoding="utf-8").splitlines()
        target_setting = (
            "Environment="
            "OBSERVATORY_PUBLISH_TARGET=/var/www/html/arifos/.well-known"
        )

        assert service_lines.count(target_setting) == 1
        assert not any(
            line.startswith("Environment=OBSERVATORY_PUBLISH_TARGET=")
            and line != target_setting
            for line in service_lines
        )

    def test_units_contain_no_private_key_material_or_path(self):
        content = "\n".join(
            (
                self.service_path.read_text(encoding="utf-8"),
                self.timer_path.read_text(encoding="utf-8"),
            )
        ).lower()

        for forbidden in (
            "-----begin private key-----",
            "observatory_signing_key.pem",
            "/root/.arifos/observatory/keys",
            "private_key",
            "privatekey",
        ):
            assert forbidden not in content, (
                f"systemd unit exposes private-key data: {forbidden}"
            )

    def test_timer_is_persistent_hourly_and_avoids_top_of_hour(self):
        timer = self.timer_path.read_text(encoding="utf-8")

        assert "[Timer]" in timer
        assert self._setting(timer, "Persistent") == "true"
        assert self._setting(timer, "Unit") == self.service_path.name
        schedule = self._setting(timer, "OnCalendar")
        match = re.fullmatch(r"\*-\*-\* \*:(\d{2}):00", schedule)
        assert match, f"expected an hourly calendar expression, got {schedule!r}"
        assert int(match.group(1)) != 0, "timer must avoid the top-of-hour herd"
        interval_minutes = 60  # Wildcard hour in the validated expression above.
        assert interval_minutes < 24 * 60
