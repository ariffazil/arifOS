"""CLI entry for arifOS pipeline (v42.1).

Usage (PowerShell examples):
  # optional env for drift demo
  # $env:ARIFOS_FORCE_EPSILON_TOTAL = "0.02"

  python -m arifos_core.system.pipeline --query "test query" --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from arifos_core.runtime.bootstrap import ensure_bootstrap, get_bootstrap_payload
from arifos_core.system.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("arifos_core.system.__main__")


from arifos_core.memory.cooling_ledger import append_entry


def _write_ledger_entry(entry: dict) -> None:
    """Append entry to cooling ledger JSONL with hash chain integrity."""
    ledger_path = Path("vault_999/cooling_ledger.jsonl")
    append_entry(ledger_path, entry)


def main() -> int:
    parser = argparse.ArgumentParser(description="arifOS v42.1 pipeline CLI")
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

    # Instantiate pipeline with ledger sink
    pipeline = Pipeline(ledger_sink=_write_ledger_entry)

    logger.info("Running pipeline for query: %r", args.query)
    state = pipeline.run(args.query)

    # Emit verdict summary
    verdict = getattr(state, "verdict", None)
    if verdict is None:
        print("No verdict produced", file=sys.stderr)
        return 1

    payload = {
        "verdict": getattr(verdict, "value", str(verdict)),
        "c_budi": getattr(state, "c_budi", None),
        "epsilon_observed": getattr(state, "epsilon_observed", None),
        "eye_vector": getattr(state, "eye_vector", None),
    }
    payload.update(get_bootstrap_payload())
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
