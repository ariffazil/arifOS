"""Tests for the durable EvidenceStore (Epoch 2 / Item 3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def test_append_returns_canonical_ref():
    """append returns an arifos://evidence/{id} ref derived from the content hash."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    ref = store.append({"type": "geox", "sample_id": "s-1"})
    assert ref.ref.startswith("arifos://evidence/")
    assert len(ref.ref.split("/")[-1]) == 16


def test_append_is_idempotent():
    """Appending the same evidence twice returns the same ref and does not duplicate."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    evidence = {"type": "geox", "sample_id": "s-1", "value": 42}
    r1 = store.append(evidence)
    r2 = store.append(evidence)
    assert r1.ref == r2.ref
    # The store holds one record, not two.
    assert store.all_refs() == (r1.ref,)


def test_get_returns_appended_evidence():
    """get retrieves the original evidence dict by ref."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    evidence = {"type": "wealth", "metric": "npv", "value": 1.5e6}
    ref = store.append(evidence)
    retrieved = store.get(ref.ref)
    assert retrieved == evidence


def test_get_returns_none_for_unknown_ref():
    """get returns None when the ref is not in the store."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    result = store.get("arifos://evidence/0000000000000000")
    assert result is None


def test_has_checks_membership():
    """has() returns True iff the ref is in the store."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    ref = store.append({"type": "well", "metric": "vitality"})
    assert store.has(ref.ref)
    assert not store.has("arifos://evidence/0000000000000000")


def test_all_refs_returns_in_append_order():
    """all_refs returns refs in the order they were appended."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    r1 = store.append({"id": 1, "type": "obs"})
    r2 = store.append({"id": 2, "type": "obs"})
    r3 = store.append({"id": 3, "type": "obs"})
    assert store.all_refs() == (r1.ref, r2.ref, r3.ref)


def test_content_hash_is_canonical_hash():
    """The content_hash matches a sha256 of the canonical JSON form."""
    from arifosmcp.runtime.evidence_store import _canonical_hash

    evidence = {"b": 2, "a": 1}  # deliberately unsorted
    h = _canonical_hash(evidence)
    # Canonical form sorts keys.
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    import hashlib
    expected = "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert h == expected


def test_different_evidence_produces_different_refs():
    """Different evidence always produces different refs."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    r1 = store.append({"x": 1})
    r2 = store.append({"x": 2})
    assert r1.ref != r2.ref


def test_evidence_record_is_durable_across_instances(tmp_path: Path):
    """Re-opening the store on the same path returns the same records."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    path = tmp_path / "evidence.jsonl"
    s1 = EvidenceStore(path=path)
    s1.append({"k": "v1"})
    s1.append({"k": "v2"})
    # A fresh instance reads the same file.
    s2 = EvidenceStore(path=path)
    assert len(s2.all_refs()) == 2


def test_append_writes_to_disk(tmp_path: Path):
    """The file on disk grows when records are appended."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path=path)
    if path.exists():
        path.unlink()
    assert path.exists() is False
    store.append({"a": 1})
    assert path.exists()
    assert path.stat().st_size > 0


def test_record_shape_matches_audit_spec(tmp_path: Path):
    """A stored record has ref, evidence, appended_at, content_hash fields."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    path = tmp_path / "evidence.jsonl"
    store = EvidenceStore(path=path)
    ref = store.append({"k": "v"})

    # Read the raw line from disk.
    with open(path, "r") as f:
        line = f.readline().strip()
    record = json.loads(line)
    assert record["ref"] == ref.ref
    assert record["evidence"] == {"k": "v"}
    assert "appended_at" in record
    assert record["content_hash"].startswith("sha256:")
    assert record["content_hash"] == ref.content_hash


def test_content_hash_idempotence():
    """Two appends of equivalent dicts (different key order) get the same ref."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    r1 = store.append({"a": 1, "b": 2})
    r2 = store.append({"b": 2, "a": 1})  # different insertion order
    assert r1.ref == r2.ref


def test_evidence_store_rejects_non_dict():
    """append requires a dict — non-dict evidence is rejected."""
    from arifosmcp.runtime.evidence_store import EvidenceStore

    store = EvidenceStore(path=Path("/tmp/test-evidence.jsonl"))
    store.path.unlink(missing_ok=True)
    raised = False
    try:
        store.append("not a dict")  # type: ignore[arg-type]
    except TypeError:
        raised = True
    assert raised


def test_ref_id_is_first_16_hex_of_sha256():
    """The ref id is the first 16 hex chars of the content hash."""
    from arifosmcp.runtime.evidence_store import EvidenceStore, _canonical_hash, _make_ref

    evidence = {"x": 1}
    content_hash = _canonical_hash(evidence)
    expected_id = content_hash.split(":", 1)[1][:16]
    assert _make_ref(content_hash) == f"arifos://evidence/{expected_id}"