"""Integration tests for the custom ``agy-atlas`` wrapper.

The canonical Antigravity binary remains ``agy``.  These tests exercise only
``/root/scripts/agy_atlas_cli.py`` and redirect every narrative write to a
per-test temporary file.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_CLI_PATH = "/root/scripts"
if _CLI_PATH not in sys.path:
    sys.path.insert(0, _CLI_PATH)


@pytest.fixture(autouse=True)
def protect_live_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGY_SCAR_FILE", str(tmp_path / "agy-scar.md"))
    monkeypatch.delenv("AGY_ACTOR_ID", raising=False)
    monkeypatch.delenv("AGY_SESSION_ID", raising=False)


def _cli():
    return __import__("agy_atlas_cli")


def test_atlas_query_uses_canonical_gpv_paradoxes(capsys: pytest.CaptureFixture[str]) -> None:
    from core.shared.atlas import Phi

    query = "sudo rm -rf production database and force push main"
    expected = Phi(query)
    result = _cli().run_atlas_query(query)

    assert result["ok"] is True
    assert result["active_paradoxes"] == expected.paradox_axes
    assert set(result["active_paradoxes"]) >= set(expected.paradox_axes)
    assert result["calibration_verdict"] in {"CONSTRAIN", "OBSERVE"}
    assert result["tearframe"]["provenance"] == "policy_constant"
    assert "GOVERNED_PASS" not in capsys.readouterr().out


def test_calibrate_reports_observations_not_execution_verdict(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli = _cli()

    def fake_get(url: str, timeout: int = 5):
        if url.endswith("/health"):
            return {"status": "healthy", "source_commit": "abc123"}
        return {
            "entropy_delta": None,
            "peace_squared": None,
            "kappa_r": None,
            "telemetry_source": "unavailable",
        }

    monkeypatch.setattr(cli, "http_get", fake_get)
    result = cli.run_calibrate()
    output = capsys.readouterr().out

    assert result["status"] == "observed"
    assert "OBSERVED" in output
    assert "OK to execute" not in output
    assert "TRM = 0.96" not in output
    assert "Machine Entropy: NOMINAL" not in output


def test_scar_is_narrative_only_pending_verification(tmp_path: Path) -> None:
    scar_path = tmp_path / "scar.md"
    result = _cli().run_scar_metabolize("operator-observed failure", scar_file=scar_path)

    assert result["ok"] is False
    assert result["status"] == "pending_verification"
    assert result["degraded_reasons"] == ["verification_required"]
    assert result["vector_index"]["status"] == "not_indexed"
    assert result["vector_index"]["verified"] is False
    assert result["source"] == "agy_cli"
    assert result["evidence_class"] == "USER_SUPPLIED"
    for forbidden in ("point_id", "content_hash", "truth_score", "ontology_class"):
        assert forbidden not in result

    body = scar_path.read_text()
    assert "evidence_class=USER_SUPPLIED" in body
    assert "verified=False" in body
    assert "Not a constitutional seal" in body


def test_scar_path_actor_and_session_are_overridable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    scar_path = tmp_path / "custom-scar.md"
    monkeypatch.setenv("AGY_SCAR_FILE", str(scar_path))
    monkeypatch.setenv("AGY_ACTOR_ID", "operator-test")
    monkeypatch.setenv("AGY_SESSION_ID", "session-test")

    result = _cli().run_scar_metabolize("bounded observation")

    assert result["actor_id"] == "operator-test"
    assert result["session_id"] == "session-test"
    assert result["nar_md_path"] == str(scar_path)
    assert scar_path.exists()


def test_scar_output_never_claims_entropy_or_seal(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _cli().run_scar_metabolize("bounded observation", scar_file=tmp_path / "scar.md")
    output = capsys.readouterr().out.lower()

    for phrase in (
        "entropy reduced",
        "entropy measured",
        "grounding contour updated",
        "scar successfully sealed",
        "sealed to vault999",
        "indexed as user_supplied",
    ):
        assert phrase not in output
    assert "no pseudo-vector written" in output
    assert "verification_required" in output


def test_default_test_path_never_touches_live_ledger(tmp_path: Path) -> None:
    live = Path("/root/arifOS/core/shared/ATLAS333_EVERGREEN.md")
    before = live.read_bytes() if live.exists() else None

    result = _cli().run_scar_metabolize("isolated test observation")

    assert Path(result["nar_md_path"]).parent == tmp_path
    if before is not None:
        assert live.read_bytes() == before
