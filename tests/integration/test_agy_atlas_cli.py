"""
Constitutional Integration Tests — agy_atlas_cli.run_scar_metabolize
════════════════════════════════════════════════════════════════════

P0-01b scar repair verification (Qdrant/AGY).

What these tests guarantee:
  * Narrative Markdown ledger is written to a caller-supplied (tmp)
    path or `AGY_SCAR_FILE` env. The live
    ``/root/arifOS/core/shared/ATLAS333_EVERGREEN.md`` is NEVER mutated
    by these tests.
  * Qdrant ``vector_store`` is monkeypatched — these tests never reach
    :6333 or any real Qdrant collection.
  * Ollama is never invoked — embedding paths are fully mocked.
  * Truthful metadata contract:
      ``source       == "agy_cli"``
      ``evidence_class == "USER_SUPPLIED"``
      ``verified     == False``
      ``actor_id     == "arif"``
      ``session_id   is stable + non-empty``
  * No claim that entropy was measured or reduced is ever printed.
  * Narrative Markdown is never claimed to be a constitutional seal.
  * Failures surface as ``status="degraded"`` with no pseudo-vector:
    no point_id, no fabricated truth_score, no ontology_class.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# ─── Resolve CLI import path WITHOUT polluting sys.path permanently ───
# We add the directory to sys.path for the duration of the test session,
# then leave it alone. The integration test directory lives under the
# arifOS test root but the CLI lives under /root/scripts. We resolve
# against a hard absolute path so tests are deterministic across cwd.
_CLI_PATH = "/root/scripts"
if _CLI_PATH not in sys.path:
    sys.path.insert(0, _CLI_PATH)


# ─────────────────────────────────────────────────────────────────────
# Autouse safeguard: never let a test accidentally write to the live
# ATLAS333_EVERGREEN.md — even if a test forgets to pass scar_file.
# ─────────────────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _protect_live_scar_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Auto-fence: redirect default AGY_SCAR_FILE to a per-test tmp file.

    This guards F1 AMANAH — if a test forgets to pass ``scar_file=``,
    the redirect still prevents the live narrative ledger from being
    mutated. The monkeypatch is restored automatically on teardown.
    """
    safe = tmp_path / "AUTOSAFE_AGY_SCAR.md"
    monkeypatch.setenv("AGY_SCAR_FILE", str(safe))
    yield


# ─────────────────────────────────────────────────────────────────────
# Fixtures: monkeypatched vector_store behaviors
# ─────────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_vector_store_ok(monkeypatch: pytest.MonkeyPatch):
    """Fake vector_store that returned ok=True (real-shape embedding)."""
    from arifosmcp.memory import vector_memory_qdrant

    captured: dict[str, object] = {}

    async def fake_async(content, metadata=None, session_id="", actor_id="", **_kwargs):
        captured["content"] = content
        captured["metadata"] = metadata
        captured["session_id"] = session_id
        captured["actor_id"] = actor_id
        return {
            "ok": True,
            "point_id": "fake-point-uuid-1234567890abcdef",
            "content_hash": "deadbeefcafebabe",
            "ontology_class": "memory",
            "truth_score": 1.0,
            "vector_size": 1024,
        }

    monkeypatch.setattr(vector_memory_qdrant, "vector_store", fake_async)
    return captured


@pytest.fixture
def fake_vector_store_embedding_unavailable(monkeypatch: pytest.MonkeyPatch):
    """Fake vector_store that surfaces ``embedding_unavailable=True``.

    This is the degraded path triggered when Ollama is unreachable /
    non-200 / empty / wrong-size — inside vector_memory_qdrant this
    happens when ``_generate_embedding`` raises the new
    ``RuntimeError("Embedding unavailable …")``.
    """
    from arifosmcp.memory import vector_memory_qdrant

    async def fake_async(content, metadata=None, session_id="", actor_id="", **_kwargs):
        return {
            "ok": False,
            "error": (
                "L10 EMBEDDING: Embedding unavailable: Ollama unreachable "
                "at http://localhost:11434 (ConnectError: …)"
            ),
            "embedding_unavailable": True,
        }

    monkeypatch.setattr(vector_memory_qdrant, "vector_store", fake_async)
    return fake_async


@pytest.fixture
def fake_vector_store_qdrant_offline(monkeypatch: pytest.MonkeyPatch):
    """Fake vector_store that surfaces the SABAR QDRANT_UNREACHABLE."""
    from arifosmcp.memory import vector_memory_qdrant

    async def fake_async(content, metadata=None, session_id="", actor_id="", **_kwargs):
        return {
            "ok": False,
            "verdict": "SABAR",
            "evidence_honesty": "QDRANT_UNREACHABLE",
            "floor_violation": "F9",
            "reason": "vector store offline; recall returned as empty result with SABAR",
            "remediation": "verify Qdrant availability; retry when online",
            "backend_status": "qdrant_offline",
            "qdrant_unavailable": True,
            "overall_confidence": 0.0,
            "empty_count": 0,
            "total_outputs": 0,
            "results": [],
            "operation": "vector_store",
            "error": "SABAR: Qdrant offline — vector_store unavailable",
        }

    monkeypatch.setattr(vector_memory_qdrant, "vector_store", fake_async)
    return fake_async


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────


def _import_cli():
    """Late import so the autouse fixture has had a chance to run."""
    return __import__("agy_atlas_cli")


# ─────────────────────────────────────────────────────────────────────
# 1. Truthful metadata contract
# ─────────────────────────────────────────────────────────────────────


def test_vector_index_uses_truthful_metadata(
    tmp_path: Path, fake_vector_store_ok: dict
) -> None:
    """Vector-store metadata MUST reflect source=agy_cli,
    evidence_class=USER_SUPPLIED, verified=False. actor_id MUST be 'arif'.
    """
    cli = _import_cli()
    scar_path = tmp_path / "scar_truthful.md"

    result = cli.run_scar_metabolize("audit-truthful-2026-07-19", scar_file=scar_path)

    md = fake_vector_store_ok["metadata"]
    assert md["source"] == "agy_cli", (
        f"F11 AUDIT: source must be 'agy_cli', got {md.get('source')!r}"
    )
    assert md["evidence_class"] == "USER_SUPPLIED", (
        f"F2 TRUTH: evidence_class must be USER_SUPPLIED, "
        f"got {md.get('evidence_class')!r}"
    )
    assert md["verified"] is False, (
        f"F2 TRUTH: AGY-CLI scars are never verified at the CLI layer; "
        f"got verified={md.get('verified')!r}"
    )
    assert fake_vector_store_ok["actor_id"] == "arif"
    # Session id is stable + non-empty (defaults to 'agy-cli-stable').
    assert fake_vector_store_ok["session_id"]
    assert isinstance(fake_vector_store_ok["session_id"], str)

    # The returned status dict must echo the truthful metadata too.
    assert result["source"] == "agy_cli"
    assert result["evidence_class"] == "USER_SUPPLIED"
    assert result["verified"] is False
    assert result["actor_id"] == "arif"


# ─────────────────────────────────────────────────────────────────────
# 2. Narrative Markdown is audit-trail only — never a seal
# ─────────────────────────────────────────────────────────────────────


def test_narrative_markdown_targeted_only_at_caller_path(
    tmp_path: Path, fake_vector_store_ok: dict
) -> None:
    """Narrative Markdown MUST be written to the supplied scar_file (or
    AGY_SCAR_FILE env). The live ATLAS333_EVERGREEN.md MUST NOT be touched
    by these tests (F1 AMANAH).
    """
    cli = _import_cli()
    live_ledger = Path("/root/arifOS/core/shared/ATLAS333_EVERGREEN.md")
    live_before: bytes | None
    if live_ledger.exists():
        live_before = live_ledger.read_bytes()
        # F1 AMANAH guard: if the live file exists, we are responsible
        # for confirming it is unmodified by this test.
    else:
        live_before = None

    supplied = tmp_path / "PROVIDED_SCAR.md"
    result = cli.run_scar_metabolize(
        "audit-targeted-2026-07-19", scar_file=supplied
    )

    # Provided path used
    assert supplied.exists(), "scar_file path must be created"
    assert result["nar_md_appended"] is True
    assert Path(result["nar_md_path"]) == supplied

    # Live path unchanged
    if live_before is not None:
        assert live_ledger.read_bytes() == live_before, (
            "F1 AMANAH: live ATLAS333_EVERGREEN.md must NOT be mutated"
        )

    # Markdown body correctly identifies itself as audit log,
    # NOT a constitutional seal.
    body = supplied.read_text().lower()
    assert "user-supplied scar log" in body or "user supplied scar log" in body
    assert "not a constitutional seal" in body or "not constitutional seal" in body
    # Truthful provenance line present
    assert "evidence_class=user_supplied" in body
    assert "verified=false" in body


# ─────────────────────────────────────────────────────────────────────
# 3. Truthful narrative — no entropy-measurement claims
# ─────────────────────────────────────────────────────────────────────


def test_no_claim_that_entropy_was_measured_or_reduced(
    tmp_path: Path, fake_vector_store_ok: dict, capsys: pytest.CaptureFixture[str]
) -> None:
    """run_scar_metabolize MUST NOT print any claim that entropy was
    measured or reduced (F2 TRUTH — unverified numerical claim).

    Forbidden phrases include: 'entropy reduced', 'entropy measured',
    'delta s ≤ 0', 'grounding contour updated', 'scar sealed',
    'constitutional seal applied'.
    """
    cli = _import_cli()
    cli.run_scar_metabolize(
        "audit-entropy-claim-2026-07-19",
        scar_file=tmp_path / "scar_entropy.md",
    )
    captured = capsys.readouterr().out.lower()

    forbidden = (
        "entropy reduced",
        "entropy was reduced",
        "entropy has been reduced",
        "entropy measured",
        "delta s ≤ 0",
        "delta s <= 0",
        "Δs ≤ 0",
        "grounding contour updated",
        "scar successfully sealed",
        "scar sealed to vault999",
        "constitutional seal applied",
        "→ seal",
        "sealed to vault",
    )
    for phrase in forbidden:
        assert phrase not in captured, (
            f"F2 TRUTH violation: forbidden narrative '{phrase}' "
            f"in scar CLI output"
        )


# ─────────────────────────────────────────────────────────────────────
# 4. Degraded status on embedding unavailability — no pseudo-vector
# ─────────────────────────────────────────────────────────────────────


def test_degraded_status_on_embedding_unavailable_no_pseudo_vector(
    tmp_path: Path,
    fake_vector_store_embedding_unavailable,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When vector_store returns embedding_unavailable=True (Ollama down):

      - run_scar_metabolize MUST return ok=False, status='degraded'.
      - The returned dict MUST NOT carry a point_id, content_hash,
        truth_score, or ontology_class — those would be fabricated.
      - The narrative Markdown append (audit log) is still attempted,
        because it is decoupled from vector indexing.
      - The print MUST NOT claim scar was indexed or sealed.
    """
    cli = _import_cli()
    scar_path = tmp_path / "scar_emb_unavail.md"

    result = cli.run_scar_metabolize(
        "audit-emb-unavail-2026-07-19", scar_file=scar_path
    )

    assert result["ok"] is False
    assert result["status"] == "degraded"
    assert result["embedding_unavailable"] is True
    assert result["qdrant_unavailable"] is False

    # No fabricated point_id / truth_score / ontology_class
    for forbidden_field in ("point_id", "content_hash", "ontology_class",
                            "truth_score", "vector_size"):
        assert forbidden_field not in result, (
            f"F9 ANTI-HANTU: must not fabricate {forbidden_field!r} on "
            f"degraded path — got {result.get(forbidden_field)!r}"
        )

    # degraded_reasons echoes the underlying cause
    reasons = result["degraded_reasons"]
    assert "embedding_unavailable" in reasons

    # Narrative log still appended (audit trail), with truthful provenance.
    assert result["nar_md_appended"] is True
    assert scar_path.exists()

    out = capsys.readouterr().out.lower()
    # Output must surface the degraded status without claiming success.
    assert "degraded" in out, "CLI must visibly report degraded status"
    assert "no pseudo-vector" in out or "no point_id fabricated" in out, (
        "CLI must explicitly disavow pseudo-vector fabrication"
    )
    # Must NOT falsely claim the scar was indexed or sealed.
    for false_phrase in ("scar indexed", "indexed to qdrant", "sealed",
                         "✅ scar", "✓ scar"):
        assert false_phrase not in out, (
            f"F2 TRUTH violation: degraded path printed '{false_phrase}'"
        )


# ─────────────────────────────────────────────────────────────────────
# 5. Degraded status on Qdrant offline — SABAR envelope preserved
# ─────────────────────────────────────────────────────────────────────


def test_degraded_status_on_qdrant_offline_no_pseudo_vector(
    tmp_path: Path,
    fake_vector_store_qdrant_offline,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When vector_store returns the SABAR QDRANT_UNREACHABLE envelope:

      - run_scar_metabolize MUST return ok=False, status='degraded'.
      - The degraded_reasons MUST include 'qdrant_unavailable'.
      - The vector_index dict's evidence_honesty='QDRANT_UNREACHABLE'
        is preserved (transparency — we don't hide the failure shape).
      - No point_id, truth_score, or ontology_class is fabricated.
    """
    cli = _import_cli()
    scar_path = tmp_path / "scar_qdrant_offline.md"

    result = cli.run_scar_metabolize(
        "audit-qdrant-offline-2026-07-19", scar_file=scar_path
    )

    assert result["ok"] is False
    assert result["status"] == "degraded"
    assert result["qdrant_unavailable"] is True
    assert result["embedding_unavailable"] is False

    # No fabricated fields on degraded path
    for forbidden_field in ("point_id", "content_hash", "ontology_class",
                            "truth_score"):
        assert forbidden_field not in result

    # degraded_reasons surfaces qdrant_unavailable
    reasons = result["degraded_reasons"]
    assert "qdrant_unavailable" in reasons

    # Narrative Markdown audit log still attempted
    assert result["nar_md_appended"] is True
    assert scar_path.exists()

    # Failure shape preserved transparently
    vi = result["vector_index"]
    assert vi.get("evidence_honesty") == "QDRANT_UNREACHABLE"
    assert vi.get("verdict") == "SABAR"
    assert vi.get("floor_violation") == "F9"


# ─────────────────────────────────────────────────────────────────────
# 6. Stable session id across calls + actor_id='arif'
# ─────────────────────────────────────────────────────────────────────


def test_session_id_is_stable_across_calls(
    tmp_path: Path, fake_vector_store_ok: dict
) -> None:
    """session_id MUST be stable across multiple run_scar_metabolize
    calls within the same process (the scar traffic sessions under one
    CLI invocation belong to the same audit lane).
    """
    cli = _import_cli()
    r1 = cli.run_scar_metabolize("first", scar_file=tmp_path / "stable_1.md")
    r2 = cli.run_scar_metabolize("second", scar_file=tmp_path / "stable_2.md")

    assert r1["session_id"] == r2["session_id"], (
        "session_id must be stable across calls in same CLI invocation"
    )
    assert r1["session_id"], "session_id must be non-empty"
    assert r1["actor_id"] == "arif"
    assert r2["actor_id"] == "arif"


# ─────────────────────────────────────────────────────────────────────
# 7. Env-var overrides are honored without monkeypatching imports
# ─────────────────────────────────────────────────────────────────────


def test_agy_session_id_overridable_via_env(
    tmp_path: Path, fake_vector_store_ok: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Setting AGY_SESSION_ID before invocation overrides the default
    stable session id — useful for operator-driven sessions and for
    test fixtures that want to assert a specific audit lane.
    """
    monkeypatch.setenv("AGY_SESSION_ID", "audit-session-p0-01b-2026-07-19")
    cli = _import_cli()
    result = cli.run_scar_metabolize(
        "env-override-session-id", scar_file=tmp_path / "scar_env_sid.md"
    )
    assert result["session_id"] == "audit-session-p0-01b-2026-07-19"


def test_agy_actor_id_overridable_via_env(
    tmp_path: Path, fake_vector_store_ok: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Setting AGY_ACTOR_ID before invocation overrides the default
    actor (default 'arif'). This is for operator-issued scars with a
    different attested principal.
    """
    monkeypatch.setenv("AGY_ACTOR_ID", "audit-scar-actor-001")
    cli = _import_cli()
    result = cli.run_scar_metabolize(
        "env-override-actor-id", scar_file=tmp_path / "scar_env_aid.md"
    )
    assert result["actor_id"] == "audit-scar-actor-001"
    # Inside vector_store, the actor_id should propagate
    assert fake_vector_store_ok["actor_id"] == "audit-scar-actor-001"


def test_agy_scar_file_env_used_when_scar_file_kwarg_omitted(
    tmp_path: Path, fake_vector_store_ok: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When scar_file kwarg is omitted, run_scar_metabolize MUST honor
    AGY_SCAR_FILE env var. Combined with the autouse fixture, this
    ensures no test can accidentally write to the live ledger.
    """
    cli = _import_cli()
    # autouse already set AGY_SCAR_FILE to a tmp; check that resolution
    # follows that path.
    expected_dir = Path(os.environ["AGY_SCAR_FILE"]).parent
    result = cli.run_scar_metabolize("env-scar-file-only")
    resolved = Path(result["nar_md_path"])
    assert resolved.parent == expected_dir
    assert resolved.exists()
    assert result["nar_md_appended"] is True


# ─────────────────────────────────────────────────────────────────────
# 8. Live ledger untouched even when scar_file kwarg is omitted
# ─────────────────────────────────────────────────────────────────────


def test_live_ledger_untouched_when_scar_file_kwarg_omitted(
    fake_vector_store_ok: dict,
) -> None:
    """If a caller forgets ``scar_file=`` but the autouse fixture has
    already pointed ``AGY_SCAR_FILE`` at a tmp path, the live ledger
    MUST still be untouched (F1 AMANAH). This is the strongest form
    of the no-live-write guarantee.
    """
    live_ledger = Path("/root/arifOS/core/shared/ATLAS333_EVERGREEN.md")
    if not live_ledger.exists():
        pytest.skip(
            "live ledger /root/arifOS/core/shared/ATLAS333_EVERGREEN.md "
            "does not exist on this host; cannot assert no-mutation"
        )
    live_before = live_ledger.read_bytes()

    cli = _import_cli()
    cli.run_scar_metabolize(
        "audit-no-live-2026-07-19"
        # NOTE: deliberately no scar_file= kwarg
    )

    assert live_ledger.read_bytes() == live_before, (
        "F1 AMANAH: omitted scar_file kwarg must redirect to "
        "AGY_SCAR_FILE tmp, NOT mutate the live ledger"
    )


# ─────────────────────────────────────────────────────────────────────
# 9. Helpful probe — verify the embedded scar_entry.json includes
#    the truthful provenance metadata (F11 AUDIT — every claim leaves
#    a trail in the payload it stored).
# ─────────────────────────────────────────────────────────────────────


def test_qdrant_payload_carries_truthful_provenance(
    tmp_path: Path, fake_vector_store_ok: dict
) -> None:
    """The JSON payload stored into Qdrant must carry the truthful
    provenance fields. F11 AUDIT — if Qdrant accepted the index
    record, the audit trail in the payload must reflect 'this came
    from AGY CLI as a USER_SUPPLIED claim' (not 'sealed scar').
    """
    cli = _import_cli()
    cli.run_scar_metabolize(
        "audit-provenance-2026-07-19", scar_file=tmp_path / "scar_prov.md"
    )

    payload = json.loads(fake_vector_store_ok["content"])
    assert payload["source"] == "agy_cli"
    assert payload["evidence_class"] == "USER_SUPPLIED"
    assert payload["verified"] is False
    # Note field explicitly disclaims constitutional sealing.
    assert "not perform constitutional sealing" in payload["note"].lower()
    # Metadata block in the call carries the same truthful fields.
    md = fake_vector_store_ok["metadata"]
    assert md["source"] == "agy_cli"
    assert md["evidence_class"] == "USER_SUPPLIED"
    assert md["verified"] is False
