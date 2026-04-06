from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SPEC_DIR = ROOT / "spec"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    from arifosmcp.runtime.public_registry import build_mcp_manifest, build_server_json

    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    write_json(SPEC_DIR / "server.json", build_server_json())
    write_json(SPEC_DIR / "mcp-manifest.json", build_mcp_manifest())


if __name__ == "__main__":
    main()
