"""
tests/test_reindex_prl.py — Non-destructive reindex script counters
════════════════════════════════════════════════════════════════════

Validates the dry-run / apply contract for ``scripts/reindex_prl.py``:

  1. **Dry-run never touches Ollama or Qdrant.**  The embedder and the
     Qdrant client are mocked; both must see zero post/upsert calls.
  2. **Dry-run counter ``written`` is renamed to ``would_write_candidates``**
     in the JSON report, with ``written=0`` so an operator cannot mistake
     a forward-looking count for an actual write.
  3. **Dry-run does NOT label valid candidates as ``skipped_fail_open``**
     — that bucket stays at 0 in dry-run mode.  (Regression test for the
     defect reported by parent verification.)
  4. **Apply mode** calls the embedder + Qdrant; embedder fail-opens go
     to ``embedder_fail_open``, never to ``skipped_fail_open``.

The script is invoked through ``main(argv)`` so the test exercises the
real CLI surface, not just internal helpers.

DITEMPA BUKAN DIBEI — Forged, Not Given.
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


SCRIPT = "/root/arifOS/scripts/reindex_prl.py"


def _write_vault(tmp_path: Path) -> Path:
    """Seed a tiny vault with 3 valid seal entries + 1 missing-id line."""
    p = tmp_path / "seal_chain.jsonl"
    p.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "entry_id": "seal-1",
                        "seq": 1,
                        "sha256_hash": "a" * 64,
                        "payload": json.dumps({"action": "deploy"}),
                        "verdict": "SEAL",
                        "blast_radius": "L2_SYSTEM",
                        "session_id": "sess-1",
                        "actor_id": "arifos",
                        "timestamp": "2026-07-22T00:00:00Z",
                    }
                ),
                json.dumps(
                    {
                        "entry_id": "seal-2",
                        "seq": 2,
                        "sha256_hash": "b" * 64,
                        "payload": json.dumps({"action": "migrate"}),
                        "verdict": "SEAL",
                        "blast_radius": "L2_SYSTEM",
                        "session_id": "sess-2",
                        "actor_id": "arifos",
                        "timestamp": "2026-07-22T00:01:00Z",
                    }
                ),
                json.dumps(
                    {
                        "entry_id": "seal-3",
                        "seq": 3,
                        "sha256_hash": "c" * 64,
                        "payload": json.dumps({"action": "rotate key"}),
                        "verdict": "HOLD",
                        "blast_radius": "L1_LOCAL",
                        "session_id": "sess-3",
                        "actor_id": "arifos",
                        "timestamp": "2026-07-22T00:02:00Z",
                    }
                ),
                # No entry_id, no seq, no sha — must be skipped_bad_id.
                json.dumps({"payload": {"action": "missing-id"}}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


def _import_script():
    """Import reindex_prl as a module without executing main()."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("reindex_prl", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["reindex_prl"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def _reindex_module():
    return _import_script()


class TestDryRunCounterContract:
    def test_dry_run_does_not_call_ollama_or_qdrant(self, tmp_path, _reindex_module):
        """Dry-run must be hermetic — no embedder calls, no Qdrant writes."""
        vault = _write_vault(tmp_path)
        report_path = tmp_path / "report.json"

        # Mock the Qdrant client and the embedder batch function.
        qdrant_client = MagicMock()
        qdrant_client.get_collections.return_value.collections = []
        with (
            patch.object(_reindex_module, "_qdrant_client", return_value=qdrant_client),
            patch.object(
                _reindex_module, "embed_texts_batch", return_value=[[0.1] * 768] * 3
            ) as embed_mock,
        ):
            rc = _reindex_module.main(
                [
                    "--vault-path",
                    str(vault),
                    "--shadow",
                    "test_shadow",
                    "--qdrant-url",
                    "http://q.test",
                    "--json-report",
                    str(report_path),
                    "--stop-after",
                    "3",
                ]
            )

        assert rc == 0
        # No embedder calls — dry-run must NEVER hit Ollama.
        assert embed_mock.call_count == 0
        # No shadow writes — dry-run must NEVER hit Qdrant upsert/create.
        upsert_calls = [
            call for call in qdrant_client.method_calls if call[0] == "upsert"
        ]
        create_calls = [
            call for call in qdrant_client.method_calls if call[0] == "create_collection"
        ]
        delete_calls = [
            call for call in qdrant_client.method_calls if call[0] == "delete_collection"
        ]
        assert upsert_calls == []
        assert create_calls == []
        assert delete_calls == []

    def test_dry_run_does_not_label_candidates_as_embed_failures(
        self, tmp_path, _reindex_module
    ):
        """The defect fix: valid candidates must NOT be counted as
        ``skipped_fail_open`` in dry-run.  That bucket is reserved for
        actual embedder fail-opens during ``--apply``.
        """
        vault = _write_vault(tmp_path)
        report_path = tmp_path / "report.json"

        qdrant_client = MagicMock()
        qdrant_client.get_collections.return_value.collections = []
        with (
            patch.object(_reindex_module, "_qdrant_client", return_value=qdrant_client),
            patch.object(
                _reindex_module, "embed_texts_batch", return_value=[[0.1] * 768] * 3
            ),
        ):
            _reindex_module.main(
                [
                    "--vault-path",
                    str(vault),
                    "--shadow",
                    "test_shadow",
                    "--qdrant-url",
                    "http://q.test",
                    "--json-report",
                    str(report_path),
                ]
            )

        report = json.loads(report_path.read_text())
        # 3 valid candidates should be counted as ``would_write_candidates``.
        assert report["read"] == 4  # 3 valid + 1 missing-id
        assert report["would_write_candidates"] == 3
        assert report["written"] == 0  # explicitly zeroed for dry-run
        assert report["dry_run"] is True
        # The defect fix: this MUST be 0 in dry-run mode.
        assert report["skipped_fail_open"] == 0
        assert report["embedder_fail_open"] == 0
        assert report["skipped_bad_id"] == 1

    def test_dry_run_no_false_fail_open_log(
        self, tmp_path, _reindex_module, caplog
    ):
        """Dry-run must NOT log any 'embedder fail-open' warnings —
        those are reserved for actual embedder failures during apply."""
        vault = _write_vault(tmp_path)
        report_path = tmp_path / "report.json"

        qdrant_client = MagicMock()
        qdrant_client.get_collections.return_value.collections = []
        with (
            patch.object(_reindex_module, "_qdrant_client", return_value=qdrant_client),
            patch.object(
                _reindex_module, "embed_texts_batch", return_value=[[0.1] * 768] * 3
            ),
        ):
            with caplog.at_level("WARNING"):
                _reindex_module.main(
                    [
                        "--vault-path",
                        str(vault),
                        "--shadow",
                        "test_shadow",
                        "--qdrant-url",
                        "http://q.test",
                        "--json-report",
                        str(report_path),
                        "--stop-after",
                        "3",
                    ]
                )

        # No "fail-open" warning should have been emitted during dry-run.
        fail_open_warnings = [
            record.message for record in caplog.records
            if "fail-open" in str(record.message).lower()
            and "reindex" in str(record.message).lower()
        ]
        assert fail_open_warnings == []


class TestApplyCounterContract:
    def test_apply_records_embedder_fail_open_separately(self, tmp_path, _reindex_module):
        """Apply mode: a batch whose embedder fail-opens MUST land in
        ``embedder_fail_open``, NOT in ``skipped_fail_open``.
        """
        vault = _write_vault(tmp_path)
        report_path = tmp_path / "report.json"

        qdrant_client = MagicMock()
        qdrant_client.get_collections.return_value.collections = []
        # First call returns [None, None, None] (whole batch fail-opens).
        # Second call would be skipped because the batch is flushed in one go.
        with (
            patch.object(_reindex_module, "_qdrant_client", return_value=qdrant_client),
            patch.object(
                _reindex_module,
                "embed_texts_batch",
                return_value=[None, None, None],
            ),
        ):
            rc = _reindex_module.main(
                [
                    "--vault-path",
                    str(vault),
                    "--shadow",
                    "test_shadow",
                    "--qdrant-url",
                    "http://q.test",
                    "--json-report",
                    str(report_path),
                    "--apply",
                    "--stop-after",
                    "3",
                ]
            )

        assert rc == 0
        report = json.loads(report_path.read_text())
        assert report["read"] == 3
        assert report["written"] == 0
        assert report["embedder_fail_open"] == 3
        assert report["skipped_fail_open"] == 0  # NOT 3 — the bug fix.
        assert report["dry_run"] is False

    def test_apply_calls_embedder_and_qdrant(self, tmp_path, _reindex_module):
        vault = _write_vault(tmp_path)
        report_path = tmp_path / "report.json"

        qdrant_client = MagicMock()
        qdrant_client.get_collections.return_value.collections = []
        with (
            patch.object(_reindex_module, "_qdrant_client", return_value=qdrant_client),
            patch.object(
                _reindex_module,
                "embed_texts_batch",
                return_value=[[0.1] * 768] * 3,
            ) as embed_mock,
        ):
            rc = _reindex_module.main(
                [
                    "--vault-path",
                    str(vault),
                    "--shadow",
                    "test_shadow",
                    "--qdrant-url",
                    "http://q.test",
                    "--json-report",
                    str(report_path),
                    "--apply",
                    "--stop-after",
                    "3",
                ]
            )

        assert rc == 0
        assert embed_mock.call_count == 1  # one batch call for 3 texts
        # create_collection was called (shadow didn't exist).
        create_calls = [
            call for call in qdrant_client.method_calls if call[0] == "create_collection"
        ]
        assert len(create_calls) == 1
        upsert_calls = [
            call for call in qdrant_client.method_calls if call[0] == "upsert"
        ]
        assert len(upsert_calls) == 1
        report = json.loads(report_path.read_text())
        assert report["written"] == 3
        assert "would_write_candidates" not in report  # only in dry-run
