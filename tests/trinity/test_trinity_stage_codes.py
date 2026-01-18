import pytest
from arifos.protocol.codes import StageCode

TRINITY = {
    'VAULT': {StageCode.INIT_000, StageCode.VAULT_999},
    'AGI': {StageCode.SENSE_111, StageCode.THINK_222, StageCode.ATLAS_333},
    'ASI': {StageCode.ALIGN_444, StageCode.EMPATHY_555, StageCode.BRIDGE_666},
    'APEX': {StageCode.EUREKA_777, StageCode.JUDGE_888, StageCode.PROOF_889},
}

def test_trinity_stage_codes_complete():
    expected = {
        StageCode.INIT_000,
        StageCode.SENSE_111,
        StageCode.THINK_222,
        StageCode.ATLAS_333,
        StageCode.ALIGN_444,
        StageCode.EMPATHY_555,
        StageCode.BRIDGE_666,
        StageCode.EUREKA_777,
        StageCode.JUDGE_888,
        StageCode.PROOF_889,
        StageCode.VAULT_999,
    }
    assert set(StageCode) == expected


def test_trinity_stage_distribution():
    # Ensure each stage is assigned to exactly one engine bucket
    buckets = {}
    for engine, stages in TRINITY.items():
        for s in stages:
            assert s not in buckets, f"Stage {s} assigned to multiple engines"
            buckets[s] = engine
    assert len(buckets) == 10  # all except INIT? Wait includes INIT and VAULT
    assert buckets[StageCode.INIT_000] == 'VAULT'
    assert buckets[StageCode.VAULT_999] == 'VAULT'
    assert buckets[StageCode.SENSE_111] == 'AGI'
    assert buckets[StageCode.THINK_222] == 'AGI'
    assert buckets[StageCode.ATLAS_333] == 'AGI'
    assert buckets[StageCode.ALIGN_444] == 'ASI'
    assert buckets[StageCode.EMPATHY_555] == 'ASI'
    assert buckets[StageCode.BRIDGE_666] == 'ASI'
    assert buckets[StageCode.EUREKA_777] == 'APEX'
    assert buckets[StageCode.JUDGE_888] == 'APEX'
    assert buckets[StageCode.PROOF_889] == 'APEX'
