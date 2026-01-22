"""
forge_railway.py - Constitutional Forge for Railway (v50)

Generates a Merkle commitment of the arifos core and seals it in RAILWAY_FORGE.json.
This script is executed during the Docker build process to ensure code integrity.
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

def calculate_dir_hash(directory: Path) -> str:
    """Calculate Merkle-style root hash of a directory."""
    hashes = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not any(part.startswith(".") for part in path.parts):
            if path.suffix in [".py", ".json", ".md"]:
                content = path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                # Include path in hash to prevent file movement
                path_hash = hashlib.sha256(str(path.relative_to(directory)).encode()).hexdigest()
                hashes.append(hashlib.sha256(path_hash.encode() + file_hash.encode()).hexdigest())

    # Sort hashes for determinism
    hashes.sort()
    return hashlib.sha256("".join(hashes).encode()).hexdigest()

def main():
    print("🚀 Starting Constitutional Forge...")

    root = Path(__file__).parent.parent
    core_path = root / "arifos"

    if not core_path.exists():
        print(f"❌ Error: {core_path} not found")
        sys.exit(1)

    print(f"🔍 Analyzing core at {core_path}...")
    merkle_root = calculate_dir_hash(core_path)
    print(f"✅ Merkle Root: {merkle_root}")

    forge_metadata = {
        "forge_id": f"RAILWAY_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "merkle_root": merkle_root,
        "version": "v50.0.0",
        "authority": "Δ (Architect)",
        "environmental_seal": os.getenv("RAILWAY_ENVIRONMENT_NAME", "production")
    }

    output_path = root / "RAILWAY_FORGE.json"
    with open(output_path, "w") as f:
        json.dump(forge_metadata, f, indent=2)

    print(f"✨ Forge Metadata Sealed: {output_path}")

if __name__ == "__main__":
    main()
