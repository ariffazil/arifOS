import base64
import json
import os
import subprocess
from pathlib import Path

# Placeholder Ed25519 key generation / loading
# In production, load a secure private key from a protected location
PRIVATE_KEY_PATH = Path(
    os.getenv("ARIFOS_PRIVATE_KEY", "C:/Users/User/arifOS/keys/ed25519_private.key")
)


def load_private_key():
    if not PRIVATE_KEY_PATH.is_file():
        raise FileNotFoundError(f"Private key not found at {PRIVATE_KEY_PATH}")
    return PRIVATE_KEY_PATH.read_bytes()


def sign_message(message: bytes, private_key: bytes) -> str:
    try:
        import ed25519
    except ImportError:
        raise RuntimeError("ed25519 library not installed. Install via 'pip install ed25519'.")
    signing_key = ed25519.SigningKey(private_key)
    signature = signing_key.sign(message)
    # Return base64‑encoded signature for storage
    return base64.b64encode(signature).decode("utf-8")


def get_last_commit_hash() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def record_signature(commit_hash: str, signature: str):
    vault_path = Path("C:/Users/User/arifOS/VAULT999/commits.log")
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "commit": commit_hash,
        "signature": signature,
    }
    with vault_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    private_key = load_private_key()
    commit_hash = get_last_commit_hash()
    signature = sign_message(commit_hash.encode("utf-8"), private_key)
    record_signature(commit_hash, signature)
    print(f"[git_sign_commit] Signed commit {commit_hash}")


if __name__ == "__main__":
    main()
