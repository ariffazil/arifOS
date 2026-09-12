"""GOV-02 (F13 2026-09-12): verifier consumes seal_chain_annotations.jsonl.

A link-family divergence whose position AND hash pair match an annotation is
classified EXPLAINED — recorded and visible — instead of blocking verification.
Precision by construction: wrong hash pair, wrong line, or a non-link gap
class never matches.
"""

import json

from arifosmcp.runtime.canonical_vault_chain import (
    ANNOTATIONS_FILENAME,
    CHAIN_FILENAME,
    GapClass,
    load_chain_annotations,
    verify_chain,
)

EPOCH = "F004-CANONICAL-2026-07-17"


def _hash(n: int) -> str:
    return f"sha256:{'ab' * 31}{n:02x}"


def _append_entry(vault, seq: int, prev: str, this: str) -> None:
    entry = {
        "epoch_id": EPOCH,
        "receipt_id": f"rcpt-test-{seq:04d}",
        "sequence": seq,
        "prev_hash": prev,
        "this_hash": this,
        "timestamp": f"2026-09-12T00:00:{seq:02d}Z",
        "actor_id": "test-annotation",
    }
    with open(vault / CHAIN_FILENAME, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def _write_annotation(vault, record: dict) -> None:
    with open(vault / ANNOTATIONS_FILENAME, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _build_chain(vault) -> tuple[str, str]:
    """3 canonical entries; entry 3's prev_hash deliberately diverges."""
    h1, h2, h3 = _hash(1), _hash(2), _hash(3)
    tampered = _hash(99)
    _append_entry(vault, 1, "genesis", h1)
    _append_entry(vault, 2, h1, h2)
    _append_entry(vault, 3, tampered, h3)  # prev != h2 → CHAIN_BREAK at line 3
    return h2, tampered


def test_no_annotation_chain_break_blocks(tmp_path):
    _build_chain(tmp_path)
    r = verify_chain(tmp_path)
    assert not r.verified
    assert any(g.gap_class == GapClass.CHAIN_BREAK for g in r.gaps)
    assert r.explained_gaps == []
    assert r.annotations_loaded == 0


def test_matching_annotation_explains_gap(tmp_path):
    expected_prev, recorded_prev = _build_chain(tmp_path)
    _write_annotation(
        tmp_path,
        {
            "schema": "arifos.chain-annotation/v1",
            "annotation_id": "ANN-TEST-001",
            "annotation_class": "NORMALIZATION_RETROACTIVE_DIVERGENCE",
            "position": {"line_no": 3, "sequence": 3, "receipt_id": "rcpt-test-0003"},
            "recorded_prev_hash": recorded_prev,
            "expected_prev_under_current_hash": expected_prev,
        },
    )
    r = verify_chain(tmp_path)
    assert r.annotations_loaded == 1
    assert len(r.explained_gaps) == 1
    eg = r.explained_gaps[0]
    assert eg.explained_by == "ANN-TEST-001"
    assert eg.gap_class == GapClass.CHAIN_BREAK
    # The explained divergence no longer blocks verification.
    assert not any(g.gap_class == GapClass.CHAIN_BREAK for g in r.gaps)
    assert r.verified, "chain with only an explained divergence must verify"
    d = r.to_dict()
    assert d["gaps_explained"] == 1
    assert d["explained_gaps"][0]["explained_by"] == "ANN-TEST-001"


def test_wrong_hash_pair_never_matches(tmp_path):
    expected_prev, recorded_prev = _build_chain(tmp_path)
    _write_annotation(
        tmp_path,
        {
            "schema": "arifos.chain-annotation/v1",
            "annotation_id": "ANN-WRONG-HASH",
            "annotation_class": "NORMALIZATION_RETROACTIVE_DIVERGENCE",
            "position": {"line_no": 3},
            "recorded_prev_hash": recorded_prev,
            "expected_prev_under_current_hash": _hash(77),  # wrong expected
        },
    )
    r = verify_chain(tmp_path)
    assert r.annotations_loaded == 1
    assert r.explained_gaps == []
    assert any(g.gap_class == GapClass.CHAIN_BREAK for g in r.gaps)
    assert not r.verified


def test_wrong_line_never_matches(tmp_path):
    expected_prev, recorded_prev = _build_chain(tmp_path)
    _write_annotation(
        tmp_path,
        {
            "schema": "arifos.chain-annotation/v1",
            "annotation_id": "ANN-WRONG-LINE",
            "annotation_class": "NORMALIZATION_RETROACTIVE_DIVERGENCE",
            "position": {"line_no": 2},
            "recorded_prev_hash": recorded_prev,
            "expected_prev_under_current_hash": expected_prev,
        },
    )
    r = verify_chain(tmp_path)
    assert r.explained_gaps == []
    assert any(g.gap_class == GapClass.CHAIN_BREAK for g in r.gaps)


def test_load_annotations_absent_file(tmp_path):
    assert load_chain_annotations(tmp_path) == []


def test_load_annotations_tolerates_bad_lines(tmp_path):
    with open(tmp_path / ANNOTATIONS_FILENAME, "w", encoding="utf-8") as fh:
        fh.write("not-json\n")
        fh.write(json.dumps({"annotation_id": "ANN-OK"}) + "\n")
    anns = load_chain_annotations(tmp_path)
    assert len(anns) == 1
    assert anns[0]["annotation_id"] == "ANN-OK"
