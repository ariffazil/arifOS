"""F6 witness CLI — the human-confirm half of the F6 lane.

Hermetic: ARIFOS_HUMAN_WITNESS redirects the ledger; evaluate_all is exercised
read-only against live (absent) production ledgers, which is exactly the
UNMEASURED path. The tool must never fabricate a witness: no statement, no row.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "f6_witness_review.py"


def _run(env_extra: dict, *args: str) -> subprocess.CompletedProcess:
    import os

    env = dict(os.environ)
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CLI), *args], capture_output=True, text=True, env=env
    )


def test_render_writes_nothing(tmp_path: Path):
    witness = tmp_path / "human_witness.jsonl"
    p = _run({"ARIFOS_HUMAN_WITNESS": str(witness)})
    assert p.returncode == 0, p.stderr
    assert "machine proposes" in p.stdout
    assert "report sha256:" in p.stdout
    assert not witness.exists()  # render is read-only


def test_confirm_without_statement_is_refused(tmp_path: Path):
    witness = tmp_path / "human_witness.jsonl"
    p = _run({"ARIFOS_HUMAN_WITNESS": str(witness)}, "--confirm")
    assert p.returncode == 2
    assert "REFUSED" in p.stderr
    assert not witness.exists()  # no statement, no row — never fabricated


def test_confirm_records_verbatim_human_statement(tmp_path: Path):
    witness = tmp_path / "human_witness.jsonl"
    words = "Saya dah baca enam meter ini; M1 fail unsigned commits ialah keadaan sebenar."
    p = _run(
        {"ARIFOS_HUMAN_WITNESS": str(witness)},
        "--confirm",
        "--statement",
        words,
        "--actor",
        "arif",
    )
    assert p.returncode == 0, p.stderr
    assert "WITNESS_RECORDED" in p.stdout
    rows = [json.loads(l) for l in witness.read_text().splitlines() if l.strip()]
    assert len(rows) == 1
    row = rows[0]
    assert row["statement"] == words  # verbatim, not paraphrased
    assert row["actor_class"] == "HUMAN"
    assert row["event"] == "f6_meter_review"
    assert len(row["report_sha256"]) == 64
    assert row["at"]


def test_recorded_row_flips_witness_axis_to_reviewed(tmp_path: Path):
    """The row shape must be what meters._witness_status actually reads."""
    sys.path.insert(0, str(ROOT))
    from arifosmcp.runtime.f6.meters import _witness_status

    witness = tmp_path / "human_witness.jsonl"
    p = _run(
        {"ARIFOS_HUMAN_WITNESS": str(witness)},
        "--confirm",
        "--statement",
        "reviewed",
    )
    assert p.returncode == 0, p.stderr
    status, reason = _witness_status(witness)
    assert status == "REVIEWED", reason
