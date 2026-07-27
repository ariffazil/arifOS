"""
governance/test_probe_logging.py — Phase B: probe logging gate.

Verifies the Phase B repair on the two drift / capability probe units:
  1. /var/log/arifos-capability-probe.log exists and is non-empty.
  2. /var/log/auditor-drift-check.log exists and is non-empty.
  3. Each log has at least one "exit=… ts=…" envelope line (Phase B format).
  4. The systemd unit files include the tee+envelope wrapper.

Read-only.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PROBE_LOG = Path("/var/log/arifos-capability-probe.log")
AUDITOR_LOG = Path("/var/log/auditor-drift-check.log")
PROBE_UNIT = Path("/etc/systemd/system/arifos-capability-probe.service")
AUDITOR_UNIT = Path("/etc/systemd/system/auditor-drift-check.service")

ENVELOPE_RE = re.compile(r"^exit=\S+\s+ts=\S+", re.MULTILINE)


@pytest.mark.parametrize(
    "log_path,unit_path",
    [(PROBE_LOG, PROBE_UNIT), (AUDITOR_LOG, AUDITOR_UNIT)],
)
def test_log_exists_and_written(log_path: Path, unit_path: Path):
    assert log_path.exists(), f"{log_path} missing"
    text = log_path.read_text(encoding="utf-8", errors="replace")
    assert text.strip(), f"{log_path} empty — silent failure would be possible"


@pytest.mark.parametrize(
    "log_path,unit_path",
    [(PROBE_LOG, PROBE_UNIT), (AUDITOR_LOG, AUDITOR_UNIT)],
)
def test_log_contains_envelope(log_path: Path, unit_path: Path):
    text = log_path.read_text(encoding="utf-8", errors="replace")
    assert ENVELOPE_RE.search(text), (
        f"{log_path} missing exit=… ts=… envelope from Phase B"
    )


@pytest.mark.parametrize(
    "unit_path,expected",
    [
        (PROBE_UNIT, "tee -a /var/log/arifos-capability-probe.log"),
        (AUDITOR_UNIT, "tee -a /var/log/auditor-drift-check.log"),
    ],
)
def test_unit_wraps_with_tee(unit_path: Path, expected: str):
    text = unit_path.read_text(encoding="utf-8")
    assert expected in text, f"{unit_path} missing Phase B tee wrapper"


@pytest.mark.parametrize(
    "unit_path",
    [PROBE_UNIT, AUDITOR_UNIT],
)
def test_unit_uses_correct_date_format(unit_path: Path):
    """The Phase B envelope must produce an ISO-style ts line, not the literal
    string `/bin/bash` (regression marker for the broken `%%Y` escape)."""
    text = unit_path.read_text(encoding="utf-8")
    assert "+%Y-%m-%dT%H:%M:%SZ" in text, f"{unit_path} missing date format"
    assert "%%Y" not in text, f"{unit_path} still has broken double-percent escape"
