#!/usr/bin/env python3
"""
Federation Null-Space Boundary Applicator
═══════════════════════════════════════════════════════════════
FORGED 2026-07-22 — Constitutional Amendment F2/F4
DITEMPA BUKAN DIBERI

Generates the [EPISTEMIC_BOUNDARY] system prompt injection for each
arifOS federation organ. Each organ's MCP server or system prompt loader
should include the generated injection in its system prompt.

Usage:
  python3 /root/arifOS/arifosmcp/runtime/null_space_boundary.py GEOX
  python3 /root/arifOS/arifosmcp/runtime/null_space_boundary.py --all
"""

import sys

from arifosmcp.runtime.null_space_boundary import (
    ORGAN_REGISTRY,
    generate_null_space_injection,
)

if __name__ == "__main__":
    if "--all" in sys.argv or len(sys.argv) == 1:
        for name in sorted(ORGAN_REGISTRY):
            print(f"\n{'=' * 70}")
            print(f"  {name} — NULL-SPACE BOUNDARY INJECTION")
            print(f"{'=' * 70}")
            print(generate_null_space_injection(name))
    else:
        name = sys.argv[1].upper()
        if name not in ORGAN_REGISTRY:
            print(f"Unknown organ: {name}. Registered: {sorted(ORGAN_REGISTRY)}")
            sys.exit(1)
        print(generate_null_space_injection(name))
