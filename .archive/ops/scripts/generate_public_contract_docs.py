from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "arifosmcp" / "sites" / "docs" / "docs" / "public-contract.md"
REGISTRY_PATH = ROOT / "arifosmcp" / "runtime" / "public_registry.py"


def _load_registry_module():
    spec = spec_from_file_location("arifosmcp_runtime_public_registry", REGISTRY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load public registry from {REGISTRY_PATH}")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    registry = _load_registry_module()
    DOC_PATH.write_text(registry.build_public_contract_markdown(), encoding="utf-8")
    print(f"Wrote {DOC_PATH}")


if __name__ == "__main__":
    main()
