"""Runtime identity registries must intersect before a session can bind."""

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pytest import MonkeyPatch

from arifosmcp.runtime import crypto_auth
from contracts.identity import normalize_actor_identity

REGISTERED_RUNTIME_IDENTITIES = {
    "codex-cli": "codex",
}


def test_registered_runtime_session_crypto_registry_intersection(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    """Every ratified runtime must normalize to an actor with an Ed25519 key."""
    private_key = Ed25519PrivateKey.generate()
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    (tmp_path / "codex_public.pem").write_bytes(public_key_pem)
    monkeypatch.setattr(crypto_auth, "_AAA_KEYS", tmp_path)
    monkeypatch.setattr(crypto_auth, "_AFORGE_KEYS", tmp_path / "missing-aforge")
    monkeypatch.setattr(crypto_auth, "_AGENT_REGISTRY", tmp_path / "missing-registry.json")
    monkeypatch.setattr(crypto_auth, "_DID_REGISTRY_CANDIDATES", ())

    for runtime_id, expected_actor in REGISTERED_RUNTIME_IDENTITIES.items():
        normalized = normalize_actor_identity(runtime_id)["normalized"]

        assert normalized == expected_actor
        assert crypto_auth.is_registered_actor(str(normalized)), (
            f"{runtime_id}: session actor {normalized!r} has no crypto registry entry"
        )
