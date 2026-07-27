"""
governance/test_ownership_lock.py — Phase A ownership-lock test.

Verifies the canonical ownership table in `/root/AGENTS.OWNERSHIP.md`
is consistent with `arifOS/arifosmcp/metadata/floor_status.json.ownership`.

Assertions:
  1. OWNERSHIP.md exists and is non-empty.
  2. floor_status.json has a top-level `ownership` block.
  3. Every F1-F13 row in floor_status.json has a matching row in OWNERSHIP.md.
  4. Every cron.d file under /etc/cron.d/ that begins with `arifos` is
     represented in either OWNERSHIP.md or the cron_duties table.
  5. Every playbook path in floor_status.json.ownership.rows ends with `.sh`
     OR starts with `/root/scripts/`.

The test is read-only and never mutates the federation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

OWNERSHIP_MD = Path("/root/AGENTS.OWNERSHIP.md")
FLOOR_STATUS = Path("/root/arifOS/arifosmcp/metadata/floor_status.json")
CRON_D = Path("/etc/cron.d")

FLOOR_IDS = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"]


def _read_ownership_md() -> str:
    assert OWNERSHIP_MD.exists(), "OWNERSHIP.md missing — Phase A addendum not applied"
    text = OWNERSHIP_MD.read_text(encoding="utf-8")
    assert len(text) > 200, "OWNERSHIP.md unexpectedly short"
    return text


def _read_floor_status() -> dict:
    return json.loads(FLOOR_STATUS.read_text(encoding="utf-8"))


def test_ownership_md_exists_and_seals():
    text = _read_ownership_md()
    assert "DITEMPA BUKAN DIBERI" in text
    assert "F13 SOVEREIGN" in text
    assert "Reversible" in text or "reversible" in text


def test_floor_status_has_ownership_block():
    status = _read_floor_status()
    assert "ownership" in status, "floor_status.json missing ownership block"
    block = status["ownership"]
    assert block.get("version"), "ownership.version missing"
    assert block.get("source") == "/root/AGENTS.OWNERSHIP.md"
    assert isinstance(block.get("rows"), list)
    assert isinstance(block.get("probes"), list)
    assert isinstance(block.get("cron_duties"), list)


@pytest.mark.parametrize("floor_id", FLOOR_IDS)
def test_floor_row_present_in_both(floor_id: str):
    status = _read_floor_status()
    md_text = _read_ownership_md()

    rows = status["ownership"]["rows"]
    matched = [r for r in rows if r.get("id") == floor_id]
    assert matched, f"{floor_id} missing from floor_status.json.ownership.rows"
    assert matched[0].get("playbook", "").startswith("/root/scripts/"), (
        f"{floor_id} playbook must live under /root/scripts/"
    )

    assert f"| {floor_id} " in md_text, f"{floor_id} missing from OWNERSHIP.md table"


def test_ownership_reversible_flag():
    status = _read_floor_status()
    assert status["ownership"].get("reversible") is True


def test_cron_duties_table_matches_etc_cron_d():
    status = _read_floor_status()
    cron_ids = {row["id"] for row in status["ownership"]["cron_duties"]}

    on_disk = set()
    if CRON_D.is_dir():
        for f in CRON_D.iterdir():
            if f.is_file() and not f.name.startswith("."):
                on_disk.add(f.name)

    arifos_duties = {d for d in on_disk if d.startswith("arifos-")}
    missing = arifos_duties - cron_ids
    assert not missing, f"arifos-* cron duties missing from ownership: {sorted(missing)}"


def test_no_irreversible_marker_in_addendum():
    text = _read_ownership_md()
    # Hard guard: this addendum must not declare any irreversible action.
    for forbidden in ("rm -rf /", "DROP TABLE", "git push --force"):
        assert forbidden not in text, f"OWNERSHIP.md accidentally encodes {forbidden!r}"


def test_ownership_md_cites_repair_federation_script():
    text = _read_ownership_md()
    assert "/root/scripts/repair-federation.sh" in text
