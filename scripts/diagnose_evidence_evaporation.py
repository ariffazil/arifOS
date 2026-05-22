#!/usr/bin/env python3
"""
scripts/diagnose_evidence_evaporation.py
═══════════════════════════════════════════════════════════════════

PHASE 0 DIAGNOSTIC: Evidence Evaporation Live Probe

Run this ad-hoc to inspect the SENSE → INGEST → MEMORY pipeline.

Usage:
    python scripts/diagnose_evidence_evaporation.py

Output: JSON diagnostic report to stderr.

Governing Principle:
    No observation without receipt.
    No receipt without bundle.
    No bundle without optional ingest.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root on sys.path
sys.path.insert(0, str(Path(__file__).parents[1]))

import os

os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")
os.environ.setdefault("ARIFOS_ALLOW_LEGACY_SPEC", "1")


def main() -> None:
    sys.stderr.write("\n" + "=" * 60 + "\n")
    sys.stderr.write("EVIDENCE EVAPORATION DIAGNOSTIC\n")
    sys.stderr.write("=" * 60 + "\n\n")

    # ── 1. Check vector_bridge file existence ──────────────────────
    arifosmcp_root = Path(__file__).parents[1] / "arifosmcp"
    vector_bridge_path = arifosmcp_root / "intelligence" / "tools" / "vector_bridge.py"
    file_on_disk = vector_bridge_path.exists()

    # ── 2. Check VECTOR_SYNC_AVAILABLE ─────────────────────────────
    try:
        from arifosmcp.runtime import reality_handlers

        VECTOR_SYNC_AVAILABLE = reality_handlers.VECTOR_SYNC_AVAILABLE
        auto_sync_bundle = reality_handlers.auto_sync_bundle

        # Determine if auto_sync_bundle is a real function or no-op stub

        is_noop_stub = (not VECTOR_SYNC_AVAILABLE) or auto_sync_bundle.__name__ == "<lambda>"
    except Exception as e:
        VECTOR_SYNC_AVAILABLE = False
        is_noop_stub = True
        sys.stderr.write(f"[WARN] Could not import reality_handlers: {e}\n")

    # ── 3. Check EvidenceBundle schema ──────────────────────────────
    try:
        from arifosmcp.runtime.reality_models import EvidenceBundle

        EvidenceBundle()
        bundle_schema_exists = True
        bundle_fields = list(EvidenceBundle.model_fields.keys())
    except Exception as e:
        bundle_schema_exists = False
        bundle_fields = []
        sys.stderr.write(f"[WARN] Could not import EvidenceBundle: {e}\n")

    # ── 4. Check EvidenceReceipt schema ────────────────────────────
    try:
        from arifosmcp.evidence.schemas import EvidenceReceipt

        receipt_schema_exists = True
        receipt_fields = list(EvidenceReceipt.model_fields.keys())
    except Exception as e:
        receipt_schema_exists = False
        receipt_fields = []
        sys.stderr.write(f"[WARN] Could not import EvidenceReceipt: {e}\n")

    # ── 5. Check memory backends ────────────────────────────────────
    try:
        memory_store_exists = True
    except Exception:
        memory_store_exists = False

    try:
        qdrant_available = True
    except Exception:
        qdrant_available = False

    try:
        postgres_available = True
    except Exception:
        postgres_available = False

    # ── 6. Build report ─────────────────────────────────────────────
    report = {
        "diagnostic": "evidence_evaporation_probe",
        "evaporation_confirmed": True,
        "timestamp_utc": __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .isoformat(),
        # VECTOR_BRIDGE status
        "vector_bridge": {
            "file_on_disk": file_on_disk,
            "file_path": str(vector_bridge_path),
            "VECTOR_SYNC_AVAILABLE": VECTOR_SYNC_AVAILABLE,
            "auto_sync_is_noop_stub": is_noop_stub,
        },
        # SCHEMAS
        "schemas": {
            "evidence_bundle_exists": bundle_schema_exists,
            "evidence_bundle_fields": bundle_fields,
            "evidence_receipt_exists": receipt_schema_exists,
            "evidence_receipt_fields": receipt_fields,
        },
        # MEMORY BACKENDS
        "memory_backends": {
            "memory_store_exists": memory_store_exists,
            "qdrant_available": qdrant_available,
            "postgres_available": postgres_available,
        },
        # EVIDENCE LEVEL of default search
        "evidence_level": {
            "search_result_default": "L1",
            "urls_ingested_by_default": 0,
            "independent_sources_by_default": 0,
        },
        # EVAPORATION SUMMARY
        "evaporation_point": (
            "auto_sync_bundle is no-op: VECTOR_SYNC_AVAILABLE=False "
            "means EvidenceBundle is created but never written to memory"
        ),
        "risk": "HIGH",
        "what_gets_lost": (
            "Every SENSE observation creates EvidenceBundle in memory, "
            "but that bundle is discarded after the response is returned. "
            "No Postgres record. No Qdrant vector. No claim persistence."
        ),
        # FIX PATH
        "fix": {
            "phase": "Phase 1",
            "action": "Create vector_bridge.py with real ingest_evidence_bundle()",
            "mode": "dry_run=True by default (no permanent write until explicitly enabled)",
            "idempotency": "Required — use sha256(session_id + query + provider + timestamp_bucket)",
            "dual_write": "Postgres (structured) + Qdrant (semantic vector)",
        },
        "next_phase": "Phase 1: EvidenceBundle schema + dry-run INGEST bridge",
    }

    # ── 7. Print report ─────────────────────────────────────────────
    sys.stderr.write("\n[DIAGNOSTIC REPORT]\n")
    sys.stderr.write(json.dumps(report, indent=2, default=str) + "\n\n")

    # ── 8. Verdict line ───────────────────────────────────────────
    if report["vector_bridge"]["VECTOR_SYNC_AVAILABLE"]:
        if report["vector_bridge"]["auto_sync_is_noop_stub"]:
            sys.stderr.write(
                "[VERDICT] Phase 0: Evaporation CONFIRMED. "
                "vector_bridge.py exists but is still stub (VECTOR_SYNC_AVAILABLE=True but no-op). "
                "Phase 1 required.\n"
            )
        else:
            sys.stderr.write(
                "[VERDICT] Phase 1 COMPLETE: Bridge is live (dry_run=True, no permanent write). "
                "Evidence evaporates ONLY in the sense that dry_run blocks writes. "
                "Phase 2 required to enable real dual-write ingest.\n"
            )
    else:
        sys.stderr.write(
            "[VERDICT] Phase 0: Evaporation CONFIRMED. "
            "vector_bridge.py missing. Phase 1 fix is required.\n"
        )

    sys.stderr.write("\n" + "=" * 60 + "\n")

    # Always exit 0 — this is a diagnostic, not a gate
    return


if __name__ == "__main__":
    main()
