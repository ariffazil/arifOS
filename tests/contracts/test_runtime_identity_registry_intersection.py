"""Runtime identity registries must intersect before a session can bind."""

from arifosmcp.runtime.crypto_auth import is_registered_actor
from contracts.identity import normalize_actor_identity

REGISTERED_RUNTIME_IDENTITIES = {
    "codex-cli": "codex",
}


def test_registered_runtime_session_crypto_registry_intersection() -> None:
    """Every ratified runtime must normalize to an actor with an Ed25519 key."""
    for runtime_id, expected_actor in REGISTERED_RUNTIME_IDENTITIES.items():
        normalized = normalize_actor_identity(runtime_id)["normalized"]

        assert normalized == expected_actor
        assert is_registered_actor(str(normalized)), (
            f"{runtime_id}: session actor {normalized!r} has no crypto registry entry"
        )
