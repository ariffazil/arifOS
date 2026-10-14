"""C1-shape tests for the kernel path engine (arifosmcp.tools.planner).

SPEC of record: F13 chat 2026-10-14. C1 acceptance: "Init, kemudian minta 3
laluan di bawah OBSERVE_ONLY. Mesti keluar 3, bukan kosong." This suite pins
the engine half of C1 (the think-dispatch half lands when mode wiring ships).
"""

from __future__ import annotations

import json

from arifosmcp.tools.planner import (
    OUTPUT_BUDGET_BYTES,
    compact_within_budget,
    generate_paths,
)


def _write_cf(path, entries):
    path.write_text(json.dumps({"schema": "arifos.carry_forward.v3", "entries": entries}))


def _write_chron(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows))


def _run(tmp_path, *, with_sources=True):
    cf = tmp_path / "cf.json"
    chron = tmp_path / "predictions.jsonl"
    if with_sources:
        _write_cf(
            cf,
            [
                {"id": "e-1", "kind": "decision", "content": "closed thing"},
                {"id": "e-2", "kind": "open_loop", "content": "CONTESTED - budget sentinel"},
                {"id": "e-3", "kind": "open_loop", "content": "membrane probe next"},
            ],
        )
        _write_chron(
            chron,
            [
                {
                    "prediction_id": "pred-a",
                    "claim": "BNM holds OPR",
                    "confidence": "0.8",
                    "verify_at": "2026-10-16T23:59:59+00:00",
                },
                {
                    "prediction_id": "pred-b",
                    "claim": "older, already past",
                    "confidence": "0.6",
                    "verify_at": "2026-10-01T00:00:00+00:00",
                },
            ],
        )
    else:
        _write_cf(cf, [])
        _write_chron(chron, [])
    return generate_paths(
        "test intent",
        cf_path=str(cf),
        chron_path=str(chron),
        fq_url="http://127.0.0.1:1/health",  # unreachable on purpose → None
        now=1759000000.0,
    )


def test_exactly_three_paths_with_required_fields(tmp_path):
    pg = _run(tmp_path)
    assert len(pg.candidates) == 3, "C1: must return exactly 3 paths, never empty"
    for c in pg.candidates:
        assert c.steps, f"{c.id}: steps non-empty"
        assert c.reversibility in ("read_only", "reversible", "ext_reversible", "irreversible")
        assert c.blast_radius in ("self", "session", "organ", "federation", "external")
        assert 0.0 <= c.expected_uncertainty_reduction <= 1.0
        assert c.falsifier, f"{c.id}: falsifier mandatory (what kills this path)"


def test_output_within_2kb_budget(tmp_path):
    pg = _run(tmp_path)
    compact = compact_within_budget(pg)
    size = len(json.dumps(compact, separators=(",", ":"), default=str).encode("utf-8"))
    assert size <= OUTPUT_BUDGET_BYTES, f"compact output {size}B > {OUTPUT_BUDGET_BYTES}B budget"


def test_advisory_and_unsealable_stamps(tmp_path):
    pg = _run(tmp_path)
    assert "ADVISORY_ONLY" in pg.advisory
    assert pg.unsealable is True, "engine output must never feed arif_seal directly"
    assert pg.verdict is None, "only arif_judge collapse may set a verdict"


def test_deterministic_same_inputs_same_graph(tmp_path):
    a = _run(tmp_path)
    b = _run(tmp_path)
    assert a.model_dump() == b.model_dump()


def test_graceful_when_sources_missing(tmp_path):
    pg = _run(tmp_path, with_sources=False)
    assert len(pg.candidates) == 3, "engine degrades honestly, never returns empty"
    resolve = next(c for c in pg.candidates if c.id == "path_resolve")
    assert "data_gap" in resolve.uncertainty_note or resolve.expected_uncertainty_reduction == 0.0


def test_verdict_field_is_canonical_enum_or_none(tmp_path):
    pg = _run(tmp_path)
    # engine never sets it; if ever set, only canonical lattice tokens
    assert pg.verdict is None
