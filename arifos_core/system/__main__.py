"""CLI entry for arifOS quantum validation (v47+).

AAA-Level Migration: Uses quantum orthogonal executor for constitutional validation.
Architecture: LLM Generation ⊥ Quantum Validation (dot_product = 0)

Usage (PowerShell examples):
  python -m arifos_core.system --query "test query" --verbose

Legacy compatibility: python -m arifos_core.system.pipeline --query "test"
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from arifos_core.system.runtime.bootstrap import ensure_bootstrap, get_bootstrap_payload

# AAA-Level: Import quantum helpers instead of old pipeline
from arifos_core.mcp import validate_text_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arifos_core.system.__main__")


from arifos_core.memory.ledger.cooling_ledger import DEFAULT_LEDGER_PATH, append_entry


def _write_ledger_entry(entry: dict) -> None:
    """Append entry to cooling ledger JSONL with hash chain integrity."""
    append_entry(DEFAULT_LEDGER_PATH, entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="arifOS v47+ quantum validation CLI")
    parser.add_argument("--query", required=True, help="Query text to process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info("Bootstrapping spec binding...")
        bootstrap_payload = ensure_bootstrap()
        logger.info("Spec binding OK: %s", list(bootstrap_payload.get("spec_hashes", {}).keys()))
    except Exception as exc:  # noqa: BLE001
        logger.error("Bootstrap failed: %s", exc, exc_info=True)
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # AAA-Level: Quantum validation (parallel AGI + ASI + APEX)
    logger.info("Running quantum validation for query: %r", args.query)
    quantum_state = validate_text_sync(
        query=args.query,
        draft_response=args.query,  # Validate query text itself
        context={"cli_mode": True, "bootstrap": bootstrap_payload}
    )

    # AAA-Level: Extract verdict from quantum state
    verdict = quantum_state.final_verdict
    if verdict is None:
        print("No verdict produced by quantum validation", file=sys.stderr)
        return 1

    # Write ledger entry after quantum validation
    ledger_entry = {
        "verdict": verdict,
        "query": args.query,
        "agi_verdict": getattr(quantum_state.agi_particle, 'verdict', None) if quantum_state.agi_particle else None,
        "asi_verdict": getattr(quantum_state.asi_particle, 'verdict', None) if quantum_state.asi_particle else None,
        "apex_verdict": getattr(quantum_state.apex_particle, 'verdict', None) if quantum_state.apex_particle else None,
        "collapsed": quantum_state.collapsed,
    }
    try:
        _write_ledger_entry(ledger_entry)
        logger.info("Ledger entry written")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to write ledger entry: %s", exc)

    # Emit verdict summary with quantum metrics
    payload = {
        "verdict": verdict,
        # Quantum metrics from AGI particle
        "truth": getattr(quantum_state.agi_particle, 'truth_score', None) if quantum_state.agi_particle else None,
        "delta_s": getattr(quantum_state.agi_particle, 'entropy_delta', None) if quantum_state.agi_particle else None,
        # Quantum metrics from ASI particle
        "peace_squared": getattr(quantum_state.asi_particle, 'peace_score', None) if quantum_state.asi_particle else None,
        "kappa_r": getattr(quantum_state.asi_particle, 'kappa_r', None) if quantum_state.asi_particle else None,
        # Quantum state metadata
        "collapsed": quantum_state.collapsed,
        "execution_time": quantum_state.execution_time if hasattr(quantum_state, 'execution_time') else None,
    }
    payload.update(get_bootstrap_payload())
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
