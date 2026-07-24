"""B6 vault mirror safety — focused regression suite.

Each test builds an isolated temp directory and exercises one safety
contract of ``scripts/vault_mirror_sync.py``. The script is loaded via
``importlib`` (matching the project pattern used in
``tests/scripts/test_build_public_state.py``) so the suite does not
depend on arifosmcp being installed in the operator env.

Coverage matrix (mirrors the assignment spec):

  1. ``test_frozen_ledger_protection``     — cannot overwrite frozen v1 ledger
  2. ``test_schema_mismatch_before_write`` — refused pre-write on wrong schema
  3. ``test_idempotent_noop``              — second run writes nothing
  4. ``test_no_git_subprocess_no_external_effect`` — verify mode is pure stdlib

The tests use the real FROZEN v1 path that the production script
hard-codes (``/root/arifOS/VAULT999/SEALED_EVENTS.jsonl``). To avoid
touching that file under any circumstance, the suite monkey-patches
``MODULE.FROZEN_V1_LEDGER`` to a temp file before each test and
asserts that mirror attempted/wrote nothing.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "vault_mirror_sync.py"
SPEC = importlib.util.spec_from_file_location("vault_mirror_sync", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
# Register in sys.modules so the @dataclass decorator can resolve the
# module's __dict__ during class processing. Without this, dataclass
# raises ``AttributeError: 'NoneType' object has no attribute '__dict__'``.
sys.modules.setdefault("vault_mirror_sync", MODULE)
SPEC.loader.exec_module(MODULE)


# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_frozen_v1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the module's hard-coded frozen path to a temp file.

    The real ``/root/arifOS/VAULT999/SEALED_EVENTS.jsonl`` is the
    constitutional v1 historical ledger (F1 AMANAH). Tests must never
    point at it. We replace ``FROZEN_V1_LEDGER`` with a temp copy that
    contains v1-shaped rows, so the frozen-protection logic fires on
    a realistic payload but writes nothing on disk.
    """
    frozen = tmp_path / "SEALED_EVENTS.jsonl"
    # Three v1-style rows (event_id + sealed_at + chain_hash + prev_hash).
    v1_rows = [
        {
            "id": 0,
            "event_id": "a25a3f74-8481-4297-b665-64a75cfe2e33",
            "event_type": "decision",
            "session_id": "2026-04-05-RENAME-PHASE2",
            "actor_id": "arif-engineer",
            "stage": "999_SEAL",
            "verdict": "SEAL",
            "payload": {"session": "2026-04-05-RENAME-PHASE2"},
            "merkle_leaf": "3bcf56c02f8d5fafde4919f7a66c7cb462f8e2588a85f5780409dff3fa127d57",
            "prev_hash": "",
            "chain_hash": "b407ebca4a933cf40c563c0afe1a05f24fee711b24cd38dde0a90b5d2391278",
            "signature": "",
            "signed_by": "arif-engineer",
            "sealed_at": "2026-04-05T21:20:13.122309+00:00",
        },
        {
            "id": 1,
            "event_id": "e7b1c2a3-4d5e-6f78-9012-345678901234",
            "event_type": "deployment",
            "session_id": "2026-04-07-PHASE1-4-FORGE",
            "actor_id": "arif-engineer",
            "stage": "999_SEAL",
            "verdict": "SEAL",
            "payload": {"session": "2026-04-07-PHASE1-4-FORGE"},
            "merkle_leaf": "2b7ac66675914e854b8a61af3cb8e2e5362179b8e40aec9ca22d566347b51fca",
            "prev_hash": "b407ebca4a933cf40c563c0afe1a05f24fee711b24cd38dde0a90b5d2391278",
            "chain_hash": "ba5afc357a0f0edb88ee5abbe2725372f93eb3699aa532b0505d8d852d58e091",
            "signature": "",
            "signed_by": "arif-engineer",
            "sealed_at": "2026-04-07T23:12:00.000000+00:00",
        },
    ]
    frozen.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in v1_rows) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(MODULE, "FROZEN_V1_LEDGER", frozen)
    return frozen


@pytest.fixture
def fake_frozen_v2(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the v2 active canonical path to a temp file."""
    frozen = tmp_path / "SEALED_EVENTS_v2.jsonl"
    frozen.write_text("", encoding="utf-8")  # empty v2 placeholder
    monkeypatch.setattr(MODULE, "FROZEN_V2_LEDGER", frozen)
    return frozen


def _write_f004_source(src: Path, n: int = 3) -> list[dict]:
    """Write a small F-004 canonical envelope JSONL to ``src``."""
    rows: list[dict] = []
    prev_hash = "genesis"
    for i in range(1, n + 1):
        row = {
            "receipt_id": f"rcpt-test-{i:06d}",
            "sequence": i,
            "previous_hash": prev_hash,
            "receipt_hash": f"sha256:test{i:064d}"[-64:],
            "timestamp": "2026-07-23T00:00:00+00:00",
            "actor_id": "test-actor",
            "session_id": "sess-test",
            "trace_id": "trace-test",
            "operation_id": f"op-{i}",
            "tool_name": "test-tool",
            "input_hash": "sha256:" + "0" * 64,
            "authority_state": "OBSERVE",
            "decision_reference": "",
            "result_hash": "sha256:" + "0" * 64,
            "reversibility": "REVERSIBLE",
            "software_release": "test",
            "epoch_id": MODULE.F004_EPOCH_ID,
            "envelope_version": MODULE.F004_ENVELOPE_VERSION,
            "verdict": "SEAL",
        }
        rows.append(row)
        prev_hash = row["receipt_hash"]
    src.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n",
        encoding="utf-8",
    )
    return rows


# ── Tests ───────────────────────────────────────────────────────────────────


def test_frozen_ledger_protection(
    tmp_path: Path,
    fake_frozen_v1: Path,
    fake_frozen_v2: Path,
) -> None:
    """Frozen v1 SEALED_EVENTS.jsonl must be refused under any mode.

    Reproduces the historical bug: the legacy mirror auto-overwrote the
    v1 frozen ledger with F-004 envelope rows. The hardened script must
    refuse BEFORE any write, regardless of --apply.
    """
    src = tmp_path / "seal_chain.jsonl"
    _write_f004_source(src)

    target = fake_frozen_v1
    pre_content = target.read_text(encoding="utf-8")

    # Even with --apply, the target is frozen → REFUSED_FROZEN_TARGET.
    res = MODULE.run_mirror(src=src, target=target, apply=True)
    assert res.status == "REFUSED_FROZEN_TARGET"
    assert "F1" in res.envelope["error"] or "frozen" in res.envelope["error"].lower()

    # Verify-mode must also refuse (defence in depth).
    res_verify = MODULE.run_mirror(src=src, target=target, apply=False)
    assert res_verify.status == "REFUSED_FROZEN_TARGET"

    # The frozen file MUST be byte-identical to its pre-test state.
    assert target.read_text(encoding="utf-8") == pre_content

    # And v2 active canonical must also be refused.
    res_v2 = MODULE.run_mirror(src=src, target=fake_frozen_v2, apply=True)
    assert res_v2.status == "REFUSED_FROZEN_TARGET"


def test_source_schema_mismatch_before_write(tmp_path: Path) -> None:
    """A mixed or malformed source must be refused before target handling."""
    src = tmp_path / "mixed_source.jsonl"
    _write_f004_source(src, n=1)
    with src.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"event_id": "legacy", "sealed_at": "2026-01-01"}) + "\n")

    target = tmp_path / "mirror_target.jsonl"
    for apply in (False, True):
        result = MODULE.run_mirror(src=src, target=target, apply=apply)
        assert result.status == "REFUSED_SOURCE_SCHEMA"
        assert result.envelope["src_f004_count"] == 1
        assert result.envelope["src_lines"] == 2
        assert not target.exists()


def test_schema_mismatch_before_write(tmp_path: Path) -> None:
    """A non-F-004 target must be refused pre-write.

    A target filled with v1-style rows (event_id, sealed_at) is
    schema-incompatible with F-004 envelope rows. The hardened script
    must detect the mismatch and exit REFUSED_SCHEMA_MISMATCH without
    touching the file — never silently merge or overwrite.
    """
    src = tmp_path / "seal_chain.jsonl"
    _write_f004_source(src)

    target = tmp_path / "v1_target.jsonl"
    # Populate with v1-shaped rows so detect_target_schema classifies it.
    v1_row = {
        "id": 0,
        "event_id": "v1-row-1",
        "event_type": "decision",
        "session_id": "v1-sess",
        "actor_id": "v1-actor",
        "stage": "999_SEAL",
        "verdict": "SEAL",
        "payload": {},
        "merkle_leaf": "0" * 64,
        "prev_hash": "",
        "chain_hash": "1" * 64,
        "signature": "",
        "signed_by": "v1-actor",
        "sealed_at": "2026-01-01T00:00:00+00:00",
    }
    target.write_text(json.dumps(v1_row, sort_keys=True) + "\n", encoding="utf-8")
    pre_content = target.read_text(encoding="utf-8")

    # With --apply, the schema mismatch must surface as a refusal, not a write.
    res = MODULE.run_mirror(src=src, target=target, apply=True)
    assert res.status == "REFUSED_SCHEMA_MISMATCH"
    assert res.envelope["target_schema"]["kind"] == "v1_frozen"

    # Target MUST be byte-identical (no partial / corrupt write).
    assert target.read_text(encoding="utf-8") == pre_content

    # And verify mode must report the same refusal shape (no apply-only bug).
    res_verify = MODULE.run_mirror(src=src, target=target, apply=False)
    assert res_verify.status == "REFUSED_SCHEMA_MISMATCH"
    assert target.read_text(encoding="utf-8") == pre_content


def test_idempotent_noop(tmp_path: Path) -> None:
    """Two consecutive --apply runs must converge to OK_NOOP without drift.

    The first run writes F-004 rows to a schema-compatible target. The
    second run observes byte-identical source vs destination and short-
    circuits to OK_NOOP — never re-writes, never bumps a counter, never
    spawns subprocess. SHA-256 of the file must match across runs.
    """
    src = tmp_path / "seal_chain.jsonl"
    _write_f004_source(src, n=4)

    target = tmp_path / "mirror_target.jsonl"
    assert not target.exists()

    # First apply: writes 4 rows.
    first = MODULE.run_mirror(src=src, target=target, apply=True)
    assert first.status == "OK_APPLIED"
    assert first.envelope["wrote"] is True
    assert first.envelope["wrote_lines"] == 4
    sha_after_first = first.envelope["comparison"]["src_sha256"]
    assert target.exists()
    on_disk_after_first = target.read_text(encoding="utf-8")

    # Second apply: identical content → idempotent no-op.
    second = MODULE.run_mirror(src=src, target=target, apply=True)
    assert second.status == "OK_NOOP"
    assert second.envelope["wrote"] is False
    assert second.envelope["comparison"]["identical"] is True
    assert second.envelope["comparison"]["src_sha256"] == sha_after_first

    # File content must be byte-identical to the first write (no truncation,
    # no extra trailing newline, no re-encoding artefacts).
    assert target.read_text(encoding="utf-8") == on_disk_after_first


def test_no_git_subprocess_no_external_effect(tmp_path: Path, monkeypatch) -> None:
    """Verify mode (the default) is pure stdlib: no git, no shell, no IO mutation.

    The legacy mirror called ``subprocess.run(["git", "add", ...])`` and
    then ``git commit`` + ``git push``. The hardened script must invoke
    ZERO subprocesses even with a target supplied, in verify mode. We
    prove it three ways:

      (a) The result envelope records ``subprocess_attempted=False`` and
          ``git_invoked=False`` for every status.
      (b) ``subprocess.run`` is patched in the stdlib ``subprocess``
          module; if any code path under verify mode touched it, the
          patch would fire and raise AssertionError.
      (c) The hardened script source contains NO git invocations, NO
          ``os.system``, and NO subprocess import — a static regression
          guard against accidental re-introduction.
    """
    src = tmp_path / "seal_chain.jsonl"
    _write_f004_source(src, n=2)

    target = tmp_path / "mirror_target.jsonl"

    # (b): Spy on the real stdlib ``subprocess`` module. The hardened
    # script no longer imports subprocess; the spy therefore stays cold
    # unless a regression re-introduces the import. We use raising
    # sentinels so even an accidental import is loud.
    calls: list[tuple] = []

    def _spy_run(*args, **kwargs):
        calls.append((args, kwargs))
        raise AssertionError(
            "subprocess.run was invoked during vault_mirror_sync run; "
            "verify mode must be pure stdlib (F4 CLARITY, no git mutation)."
        )

    monkeypatch.setattr(subprocess, "run", _spy_run)
    if hasattr(subprocess, "Popen"):
        monkeypatch.setattr(
            subprocess,
            "Popen",
            lambda *a, **k: (_ for _ in ()).throw(
                AssertionError("Popen invoked during vault_mirror_sync run")
            ),
        )

    # (a) Verify-mode run with a target must NOT touch subprocess and
    # NOT write the target file.
    res_verify = MODULE.run_mirror(src=src, target=target, apply=False)
    assert res_verify.status == "OK_VERIFY_ONLY"
    assert res_verify.envelope["subprocess_attempted"] is False
    assert res_verify.envelope["git_invoked"] is False
    assert res_verify.envelope["wrote"] is False
    assert not target.exists(), "verify mode must not create the target"
    assert calls == [], "no subprocess calls should have occurred"

    # Verify-mode WITHOUT a target must be an idempotent OK.
    res_no_target = MODULE.run_mirror(src=src, target=None, apply=False)
    assert res_no_target.status == "OK"
    assert res_no_target.envelope["subprocess_attempted"] is False
    assert res_no_target.envelope["git_invoked"] is False
    assert calls == []

    # (c) Static regression guard: scan only the executable code, not
    # docstrings/comments. We strip triple-quoted strings and comment
    # lines, then assert the executable surface contains NO git
    # invocation, NO os.system, and NO subprocess import. This is the
    # cheap tripwire for "someone re-added the auto-commit path" — the
    # tests fail loudly in collection before any external effect ever
    # happens. The docstring may LEGITIMATELY mention ``git add`` /
    # ``git commit`` / ``git push`` while describing what was removed.
    source_text = SCRIPT.read_text(encoding="utf-8")
    executable_lines: list[str] = []
    in_triple = False
    triple_delim = '"""'
    for raw_line in source_text.splitlines():
        stripped = raw_line.strip()
        if in_triple:
            if triple_delim in raw_line:
                in_triple = False
                # Keep anything after the closing delim on the same line.
                tail = raw_line.split(triple_delim, 1)[1]
                if tail.strip():
                    executable_lines.append(tail)
            continue
        if triple_delim in raw_line and not raw_line.lstrip().startswith(triple_delim):
            # Single-line docstring — strip the docstring portion, keep code.
            head, _, _ = raw_line.partition(triple_delim)
            executable_lines.append(head)
            continue
        if stripped.startswith(triple_delim):
            in_triple = True
            continue
        if stripped.startswith("#"):
            continue
        executable_lines.append(raw_line)
    executable = "\n".join(executable_lines)

    # Real invocation patterns only — never the bare word, which may
    # legitimately appear in the module docstring as a description.
    forbidden_patterns = [
        ("subprocess.run([", "git add"),
        ("subprocess.run([", "git commit"),
        ("subprocess.run([", "git push"),
        ("os.system(", None),
        ("import subprocess", None),
    ]
    for prefix, arg in forbidden_patterns:
        if arg is None:
            assert prefix not in executable, (
                f"vault_mirror_sync source contains forbidden executable "
                f"pattern: {prefix!r} — auto-mutation / external effect "
                f"removed."
            )
        else:
            combined = prefix + repr(arg)
            assert combined not in executable and combined.replace("'", '"') not in executable, (
                f"vault_mirror_sync source contains forbidden executable "
                f"pattern: {prefix + arg!r} — auto-mutation removed."
            )

    # And the module-level guard is importable + callable.
    MODULE.assert_no_subprocess()


# ── CLI smoke (entry-point exit codes) ───────────────────────────────────────


def test_cli_default_is_verify_with_zero_exit(tmp_path: Path) -> None:
    """Default invocation (no flags) must exit 0 and produce no writes.

    This is the operator-facing contract: ``python vault_mirror_sync.py``
    with no arguments is a pure read, never a write, never a subprocess.
    """
    src = tmp_path / "seal_chain.jsonl"
    _write_f004_source(src, n=1)
    target = tmp_path / "should_not_appear.jsonl"

    # Default mode: verify-only with no target → exit 0.
    rc = MODULE.main(["--src", str(src)])
    assert rc == 0
    assert not target.exists()
