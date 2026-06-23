#!/usr/bin/env python3
"""
L0 Reality Scanner for arifOS federation docs vs live code.
Generates a simple chaos report without new MCP tools.
Respects the 7-tool public facade.

Run: python scripts/check_reality.py > reality_report.json
"""

import re
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_7 = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_judge",
    "arif_act",
    "arif_seal",
]


def find_docs_claims():
    claims = []
    for md in ROOT.rglob("*.md"):
        if any(x in str(md) for x in ["archive", "backup", ".git"]):
            continue
        text = md.read_text(errors="ignore")
        for m in re.finditer(r"(\d+)\s*(tools|canonical tools|public tools|MCP tools)", text, re.I):
            num = int(m.group(1))
            if num not in (7, 13, 15, 16, 50, 77):
                continue
            claims.append(
                {
                    "file": str(md.relative_to(ROOT)),
                    "claim": m.group(0),
                    "number": num,
                    "context": text[max(0, m.start() - 30) : m.end() + 30].replace("\n", " "),
                }
            )
    return claims


def get_live_code_state():
    try:
        import sys

        sys.path.insert(0, str(ROOT))
        from arifosmcp.runtime.public_surface import CANONICAL_7, public_tool_names_for_mode

        return {
            "public_7_declared": len(CANONICAL_7),
            "public_names": list(CANONICAL_7),
            "mode_default": len(public_tool_names_for_mode(None)),
        }
    except Exception as e:
        return {"error": str(e)}


def main():
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "mode": "L0_scanner_only",
        "public_facade_expected": 7,
        "docs_claims": find_docs_claims(),
        "live_code": get_live_code_state(),
        "drift_summary": [],
    }
    for claim in report["docs_claims"]:
        if claim["number"] != 7:
            report["drift_summary"].append(
                {
                    "file": claim["file"],
                    "issue": f"Claims {claim['number']} tools, expected 7 public",
                    "severity": "HIGH" if claim["number"] > 7 else "MEDIUM",
                    "evidence": claim,
                }
            )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
