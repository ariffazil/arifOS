"""E20 Truth Metabolism — the judge gate must not mistake "no data" for "all clear".

F13 SAH 2026-10-01 authorized wiring `truth_metabolism_for_judge()` into arif_judge
pre-verdict. Before any binding wiring, the module's aggregate had to be measured.

What the code actually did (read, not inferred):
  `check_claim()` returns ``state="UNKNOWN"`` for any claim absent from the store
  (:205-217), and `truth_metabolism_for_judge()` raises only ``has_expired`` /
  ``has_stale`` — an UNKNOWN claim sets neither, so the aggregate returned
  ``recommendation="PROCEED"``.
  The store path is /tmp/truth_metabolism.json, which does not exist on this host,
  and NOTHING in the estate writes it (the only file naming that path is this module
  itself). Therefore every claim was UNKNOWN, and the gate would have returned
  PROCEED for 100% of verdicts, permanently — while an evidence bundle reading
  "truth_metabolism: PROCEED" reports temporal verification as having happened.

That contradicts the module's own rule: `ClaimStatus.can_support_seal` is True only
for FRESH claims (:95-97), and the class docstring says expired claims cannot support
SEAL without re-verification. Absence of evidence is not freshness.

These tests pin the corrected lattice:
  EXPIRED → HOLD      (dispositive: reality's answer aged out)
  STALE   → SABAR     (re-probe before sealing)
  UNKNOWN → NOT_CHECKED  (no producer / no registration — must never read as PROCEED)
  FRESH   → PROCEED
Severity order: HOLD > SABAR > NOT_CHECKED > PROCEED.

Also pins testability: the judge hook previously hard-instantiated `TruthMetabolism()`
against the module default path, so no test could isolate it (same defect class as the
inline events path in chron_attention_debt, fixed separately the same day).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from arifosmcp.runtime.truth_metabolism import (  # noqa: E402
    DEFAULT_TTL_SECONDS,
    STALE_THRESHOLD,
    TruthMetabolism,
    truth_metabolism_for_judge,
)


def _store(tmp_path: Path) -> Path:
    return tmp_path / "truth_metabolism.json"


def _rec(tmp_path: Path, claim_ids: list[str]) -> str:
    return truth_metabolism_for_judge(claim_ids, store_path=str(_store(tmp_path)))[
        "truth_metabolism"
    ]["recommendation"]


def test_t1_no_data_is_not_all_clear(tmp_path):
    """The defect that made this gate theatre: an unpopulated store must NOT PROCEED."""
    assert not _store(tmp_path).exists()
    rec = _rec(tmp_path, ["organs_alive"])
    assert rec == "NOT_CHECKED", (
        f"unregistered claim returned {rec!r} — absence of a producer read as "
        "temporal verification having passed"
    )


def test_t2_fresh_claim_proceeds(tmp_path):
    tm = TruthMetabolism(store_path=str(_store(tmp_path)))
    tm.register_claim("organs_alive", value=True, ttl_seconds=DEFAULT_TTL_SECONDS, source="probe")
    assert _rec(tmp_path, ["organs_alive"]) == "PROCEED"


def test_t3_expired_claim_holds(tmp_path):
    tm = TruthMetabolism(store_path=str(_store(tmp_path)))
    tm.register_claim("organs_alive", value=True, ttl_seconds=60)
    # force age past TTL without sleeping
    raw = json.loads(_store(tmp_path).read_text())
    raw["organs_alive"]["registered_epoch"] = time.time() - 120
    _store(tmp_path).write_text(json.dumps(raw))
    assert _rec(tmp_path, ["organs_alive"]) == "HOLD"


def test_t4_stale_claim_is_sabar(tmp_path):
    tm = TruthMetabolism(store_path=str(_store(tmp_path)))
    ttl = 100
    tm.register_claim("organs_alive", value=True, ttl_seconds=ttl)
    raw = json.loads(_store(tmp_path).read_text())
    raw["organs_alive"]["registered_epoch"] = time.time() - (ttl * (STALE_THRESHOLD + 0.05))
    _store(tmp_path).write_text(json.dumps(raw))
    assert _rec(tmp_path, ["organs_alive"]) == "SABAR"


def test_t5_expiry_and_unknown_mix_is_dispositive(tmp_path):
    """A real expiry outranks an unregistered sibling: HOLD, not NOT_CHECKED."""
    tm = TruthMetabolism(store_path=str(_store(tmp_path)))
    tm.register_claim("dead_claim", value=False, ttl_seconds=1)
    tm.register_claim("live_claim", value=True, ttl_seconds=DEFAULT_TTL_SECONDS)
    raw = json.loads(_store(tmp_path).read_text())
    raw["dead_claim"]["registered_epoch"] = time.time() - 500
    _store(tmp_path).write_text(json.dumps(raw))
    res = truth_metabolism_for_judge(
        ["dead_claim", "live_claim", "never_registered"],
        store_path=str(_store(tmp_path)),
    )["truth_metabolism"]
    assert res["recommendation"] == "HOLD"
    assert res["has_expired"] is True
    assert res["has_unknown"] is True


def test_t6_stale_outranks_unknown(tmp_path):
    tm = TruthMetabolism(store_path=str(_store(tmp_path)))
    ttl = 100
    tm.register_claim("aging_claim", value=True, ttl_seconds=ttl)
    raw = json.loads(_store(tmp_path).read_text())
    raw["aging_claim"]["registered_epoch"] = time.time() - (ttl * (STALE_THRESHOLD + 0.05))
    _store(tmp_path).write_text(json.dumps(raw))
    res = truth_metabolism_for_judge(
        ["aging_claim", "never_registered"], store_path=str(_store(tmp_path))
    )["truth_metabolism"]
    assert res["recommendation"] == "SABAR"
    assert res["has_unknown"] is True


def test_t7_empty_claim_list_is_not_checked(tmp_path):
    """Asking the gate about nothing must not look like a pass either."""
    assert _rec(tmp_path, []) == "NOT_CHECKED"


def test_t8_surface_carries_its_own_derivation_instant(tmp_path):
    """Ratified Temporal Derivation Law: every derived temporal surface carries
    as_of (instant of derivation) and whether a store was present at all."""
    res = truth_metabolism_for_judge(["x"], store_path=str(_store(tmp_path)))["truth_metabolism"]
    assert res.get("as_of"), "derived temporal surface must stamp its derivation instant"
    assert res.get("store_present") is False
