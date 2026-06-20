#!/usr/bin/env python3
"""validate_constitutional_reality.py — Validate the generated report against the schema.

Loads the schema module directly to avoid the heavy arifosmcp.schemas package init.
F2 TRUTH: confirms JSON shape matches declared contract.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "arifosmcp" / "schemas" / "constitutional_reality.py"
REPORT_PATH = ROOT / "CONSTITUTIONAL_REALITY_LATEST.json"


def load_schema_module():
    spec = importlib.util.spec_from_file_location("constitutional_reality_schema", SCHEMA_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load schema from {SCHEMA_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["constitutional_reality_schema"] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    report_path = Path(argv[0]) if argv else REPORT_PATH
    if not report_path.exists():
        print(f"ERROR: report not found at {report_path}", file=sys.stderr)
        return 1

    module = load_schema_module()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    report = module.ConstitutionalRealityReport.model_validate(data)

    print(f"OK: {report_path} validates against {SCHEMA_PATH.name}")
    print(f"  report_id: {report.report_id}")
    print(f"  overall_verdict: {report.overall_verdict}")
    print(f"  floors: {len(report.floors)}")
    print(f"  organs: {len(report.organs)}")
    print(f"  cross_checks: {len(report.cross_checks)}")
    print(f"  gaps: {len(report.gaps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
