"""
Generate manifest.json for arifOS Core
"""
import hashlib
import json
from pathlib import Path


def compute_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_manifest():
    repo_root = Path.cwd()
    spec_dir = repo_root / "arifos_core" / "spec"

    files = {}

    # Scan for JSON and MD specs in spec dir, recursively
    for path in spec_dir.rglob("*"):
        if path.is_file() and path.suffix in ['.json', '.md', '.py']:
             rel_path = path.relative_to(repo_root).as_posix()
             files[rel_path] = compute_sha256(path)

    manifest = {
        "version": "v46.0.0",
        "files": files
    }

    manifest_path = repo_root / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest generated at {manifest_path} with {len(files)} files.")

if __name__ == "__main__":
    generate_manifest()
