"""
Engineering Eureka Agent — CLI entry point.

Usage:
    python -m arifosmcp.agents.eureka bootstrap
    python -m arifosmcp.agents.eureka scan "OPA denied: floor F11 unbound"
    python -m arifosmcp.agents.eureka validate "F2: every claim needs evidence"
"""

from __future__ import annotations

import sys

from .agent import EngineeringEurekaAgent
from .validator import EngineeringClaim


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m arifosmcp.agents.eureka {bootstrap|scan|validate|substrate} [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    agent = EngineeringEurekaAgent()

    if cmd == "bootstrap":
        result = agent.bootstrap()
        print(result.notes)
        print("Available:", result.evidence[0] if result.evidence else "n/a")

    elif cmd == "scan":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        result = agent.scan_for_signals(text)
        print(f"Detected {len(result.signals)} signal(s):")
        for s in result.signals:
            print(f"  - {s.signal_type.value}: {s.title} (conf={s.confidence:.2f})")

    elif cmd == "validate":
        text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        claim = EngineeringClaim(
            claim=text,
            epistemic_label="DER",
            confidence=0.85,
            evidence=["CLI invocation"],
            witness_type="ai",
            witness_id="FORGE-000Ω",
            floor_compliance=["F2_TRUTH", "F11_AUDIT"],
        )
        result = agent.validate_claim(claim)
        print(result.notes)

    elif cmd == "substrate":
        agent.bootstrap()
        summary = agent.substrate_summary()
        print(
            f"Total: {summary['total']} | Available: {summary['available']} | Missing: {summary['missing']}"
        )
        if summary["missing_names"]:
            print("Missing:", ", ".join(summary["missing_names"]))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
