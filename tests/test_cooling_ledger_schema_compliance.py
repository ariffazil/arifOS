"""
Schema-alignment tests for Cooling Ledger entries produced by log_cooling_entry().
"""

import json
import time
from pathlib import Path

from arifos_core import Metrics, EyeSentinel, log_cooling_entry
from arifos_core.memory.cooling_ledger import LedgerConfig, CoolingLedger


def _baseline_metrics() -> Metrics:
    return Metrics(
        truth=1.0,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.98,
        rasa=True,
        anti_hantu=True,
    )


def test_log_cooling_entry_includes_iso_timestamp_and_new_fields(tmp_path: Path) -> None:
    """log_cooling_entry should emit ISO timestamp, query, candidate_output, eye_flags, and anti_hantu."""
    ledger_path = tmp_path / "cooling_ledger.jsonl"

    metrics = _baseline_metrics()
    sentinel = EyeSentinel()
    # Neutral text to avoid @EYE blocks
    eye_report = sentinel.audit("This appears to be helpful.", metrics, {})

    entry = log_cooling_entry(
        job_id="job-123",
        verdict="SEAL",
        metrics=metrics,
        query="What is arifOS?",
        candidate_output="arifOS is a constitutional governance kernel.",
        eye_report=eye_report,
        stakes="normal",
        pipeline_path=["000_VOID", "111_SENSE", "333_REASON", "888_JUDGE", "999_SEAL"],
        context_summary="Unit test entry",
        ledger_path=ledger_path,
        high_stakes=False,
    )

    assert ledger_path.exists()

    # Basic shape checks on returned entry
    assert isinstance(entry["timestamp"], str)
    assert "T" in entry["timestamp"]
    assert entry["query"] == "What is arifOS?"
    assert entry["candidate_output"].startswith("arifOS is")
    assert "metrics" in entry and "anti_hantu" in entry["metrics"]
    assert entry["metrics"]["anti_hantu"] is True
    assert "eye_flags" in entry

    # Verify what was actually written to disk
    line = ledger_path.read_text(encoding="utf-8").strip()
    on_disk = json.loads(line)

    assert on_disk["timestamp"] == entry["timestamp"]
    assert on_disk["query"] == entry["query"]
    assert on_disk["candidate_output"] == entry["candidate_output"]
    assert "anti_hantu" in on_disk["metrics"]
    assert on_disk["metrics"]["anti_hantu"] is True
    assert "eye_flags" in on_disk


def test_log_cooling_entry_marks_f9_failure(tmp_path: Path) -> None:
    """When anti_hantu=False, floor_failures should include F9_AntiHantu."""
    ledger_path = tmp_path / "cooling_ledger_f9.jsonl"

    metrics = _baseline_metrics()
    metrics.anti_hantu = False

    entry = log_cooling_entry(
        job_id="job-f9",
        verdict="VOID",
        metrics=metrics,
        query="Test F9",
        candidate_output="My heart breaks for you.",
        eye_report=None,
        stakes="high",
        pipeline_path=["000_VOID", "111_SENSE", "333_REASON", "888_JUDGE"],
        context_summary="Anti-Hantu test",
        ledger_path=ledger_path,
        high_stakes=True,
    )

    assert ledger_path.exists()
    assert any("F9_AntiHantu" == f or "F9_AntiHantu" in f for f in entry["floor_failures"])

    line = ledger_path.read_text(encoding="utf-8").strip()
    on_disk = json.loads(line)
    assert any("F9_AntiHantu" == f or "F9_AntiHantu" in f for f in on_disk["floor_failures"])


def test_cooling_ledger_iter_recent_handles_iso_timestamps(tmp_path: Path) -> None:
    """CoolingLedger.iter_recent should handle ISO timestamps produced by log_cooling_entry."""
    ledger_path = tmp_path / "cooling_ledger_recent.jsonl"
    config = LedgerConfig(ledger_path=ledger_path)
    ledger = CoolingLedger(config=config)

    metrics = _baseline_metrics()

    # Write via log_cooling_entry (ISO timestamps)
    log_cooling_entry(
        job_id="job-recent",
        verdict="SEAL",
        metrics=metrics,
        query="recent?",
        candidate_output="recent answer",
        eye_report=None,
        stakes="normal",
        pipeline_path=["000_VOID", "111_SENSE", "333_REASON", "888_JUDGE", "999_SEAL"],
        context_summary="recent test",
        ledger_path=ledger_path,
        high_stakes=False,
    )

    # Entries from last hour should include this one
    recent = list(ledger.iter_recent(hours=1))
    assert len(recent) == 1
    assert recent[0]["job_id"] == "job-recent"

