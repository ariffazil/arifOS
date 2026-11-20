"""Guard against OUT_OF_BAND_APPEND ordering (seq 43 defect).

An envelope whose operation_id is a prefix of its own receipt_hash can only
have been assembled with the digest computed BEFORE operation_id was set.
Such a row can never reproduce its stored hash. The canonical envelope type
must refuse to construct it.

This closes the in-repo assembly path. The raw file-append path is a separate
concern (OS/process isolation) — named here so the guard is not overclaimed.
"""

import pytest

from arifosmcp.runtime.canonical_vault_chain import ReceiptEnvelope


def _valid_env(**kwargs):
    base = dict(
        receipt_id="rcpt-test",
        sequence=1,
        previous_hash="sha256:0",
        receipt_hash="sha256:" + "a" * 64,
        timestamp="2026-10-24T00:00:00Z",
        actor_id="test",
        actor_verification={"actor_verified": False, "method": "unsigned"},
        session_id="s",
        trace_id="t",
        operation_id="op-test",
        tool_name="test",
        input_hash="sha256:" + "b" * 64,
        authority_state="OBSERVE_ONLY",
        decision_reference="",
        result_hash="sha256:" + "c" * 64,
        reversibility="REVERSIBLE",
        software_release="",
        signature="",
    )
    base.update(kwargs)
    return base


def test_out_of_band_append_refused():
    """operation_id copied from the digest is refused at construction."""
    digest = "sha256:2569f83d9812596de26bb44f53a8ebc6d7229a7791fbe305965cf6171d2a4ab9"
    with pytest.raises(ValueError, match="OUT_OF_BAND_APPEND"):
        ReceiptEnvelope(**_valid_env(operation_id="2569f83d9812596d", receipt_hash=digest))


def test_valid_envelope_still_constructs():
    """Normal envelopes construct without raising."""
    env = ReceiptEnvelope(**_valid_env())
    assert env.seq == 1
    assert env.this_hash == env.receipt_hash


def test_writer_fenced_blocks_rogue_actor(tmp_path):
    """Rogue/unlisted actors (e.g. aaa-gateway) are blocked from constitutional seal_chain."""
    from arifosmcp.runtime.canonical_vault_chain import append_receipt
    with pytest.raises(ValueError, match="WRITER_FENCED"):
        append_receipt(actor_id="aaa-gateway", vault_dir=tmp_path)


def test_epoch_reset_forbidden_on_nonempty_chain(tmp_path):
    """Non-empty chain refuses force_sequence=1 or force_prev_hash=sha256:0."""
    from arifosmcp.runtime.canonical_vault_chain import append_receipt, GENESIS_PREV_HASH
    (tmp_path / "seal_chain.jsonl").write_text('{"seq":1}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="EPOCH_RESET_FORBIDDEN"):
        append_receipt(
            actor_id="hermes",
            vault_dir=tmp_path,
            force_prev_hash=GENESIS_PREV_HASH,
        )
    with pytest.raises(ValueError, match="EPOCH_RESET_FORBIDDEN"):
        append_receipt(
            actor_id="hermes",
            vault_dir=tmp_path,
            force_sequence=1,
        )
