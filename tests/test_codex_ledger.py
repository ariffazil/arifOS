import json
from pathlib import Path

from arifos_core.codex_ledger import log_codex_cli_entry
from arifos_core.memory.cooling_ledger import verify_chain


def _floors() -> dict:
    return {
        "F0_anti_janitor": "PASS",
        "F1_amanah": "PASS",
        "F2_truth": 0.99,
        "F3_peace2": 1.2,
        "F4_delta_s": 0.1,
        "F5_kappa_r": 0.97,
        "F6_omega0": 0.04,
        "F7_rasa": "PASS",
        "F8_tri_witness": 0.98,
        "F9_anti_hantu": "PASS",
    }


def test_log_codex_cli_entry_writes_codex_metadata(tmp_path: Path) -> None:
    ledger_path = tmp_path / "cooling_ledger.jsonl"
    floors = _floors()

    entry = log_codex_cli_entry(
        floors=floors,
        verdict="SEAL",
        task_type="code_gen",
        task_description="Generate fibonacci function",
        scope="fibonacci.py",
        risk_score=0.001,
        entropy_delta=-0.5,
        reversible=True,
        artifacts=["fibonacci.py"],
        query="Generate a recursive Fibonacci function",
        candidate_output="def fibonacci(n): return n if n <= 1 else fibonacci(n - 1) + fibonacci(n - 2)",
        pipeline_path=["CODEX_CLI"],
        ledger_path=ledger_path,
        job_id="codex-test-1",
    )

    assert ledger_path.exists()
    line = ledger_path.read_text(encoding="utf-8").strip()
    on_disk = json.loads(line)

    assert entry["hash"] == on_disk["hash"]
    assert on_disk["source"] == "CODEX_CLI"
    assert on_disk["task_type"] == "code_gen"
    assert on_disk["task_description"].startswith("Generate fibonacci")
    assert on_disk["scope"] == "fibonacci.py"
    assert on_disk["codex_audit"]["floors"]["F2_truth"] == floors["F2_truth"]
    assert on_disk["codex_audit"]["risk_score"] == 0.001
    assert on_disk["codex_audit"]["entropy_delta"] == -0.5
    assert on_disk["codex_audit"]["reversible"] is True
    assert on_disk["codex_audit"]["artifacts"] == ["fibonacci.py"]
    assert on_disk["metrics"]["truth"] == floors["F2_truth"]
    assert on_disk["metrics"]["omega_0"] == floors["F6_omega0"]
    assert on_disk["metrics"]["anti_hantu"] is True


def test_log_codex_cli_entry_preserves_hash_chain(tmp_path: Path) -> None:
    ledger_path = tmp_path / "cooling_ledger_chain.jsonl"
    floors = _floors()

    log_codex_cli_entry(
        floors=floors,
        verdict="SEAL",
        task_type="code_gen",
        task_description="first",
        scope="a.py",
        risk_score=0.0,
        entropy_delta=0.0,
        reversible=True,
        artifacts=["a.py"],
        ledger_path=ledger_path,
        job_id="codex-chain-1",
    )

    log_codex_cli_entry(
        floors=floors,
        verdict="SEAL",
        task_type="code_gen",
        task_description="second",
        scope="b.py",
        risk_score=0.0,
        entropy_delta=0.0,
        reversible=True,
        artifacts=["b.py"],
        ledger_path=ledger_path,
        job_id="codex-chain-2",
    )

    ok, message = verify_chain(ledger_path)
    assert ok, message
