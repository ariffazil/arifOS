from __future__ import annotations

from arifosmcp.kernel.forge_skill_contract import (
    ForgeSkillDenyCode,
    ForgeSkillRequest,
    ForgeSkillVerdict,
    GeneratedCapabilityClass,
    assess_forge_skill_request,
)

READ_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {}}
OUT_SCHEMA = {"type": "object", "additionalProperties": False, "properties": {"ok": {"type": "boolean"}}}


def test_forge_skill_admits_safe_read_capability_draft():
    request = ForgeSkillRequest(
        intent="parse LAS file and return PHIE curve",
        domain="geox",
        seal_verdict_id="seal_123",
        requested_tool_name="forge_las_parser",
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.ADMIT_DRAFT
    assert assessment.admissible is True
    assert assessment.tool_id == "generated.geox.forge_las_parser"
    assert assessment.schema_fingerprint
    assert assessment.code_fingerprint
    assert assessment.deny_codes == ()


def test_forge_skill_requires_seal_verdict_before_draft():
    request = ForgeSkillRequest(
        intent="parse LAS file",
        domain="geox",
        seal_verdict_id=None,
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.MISSING_SEAL_VERDICT in assessment.deny_codes
    assert assessment.tool_id is None


def test_forge_skill_blocks_self_modification():
    request = ForgeSkillRequest(
        intent="improve forge_skill itself",
        domain="aforge",
        seal_verdict_id="seal_123",
        requested_tool_name="forge_skill_patch",
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.SELF_MODIFICATION in assessment.deny_codes


def test_forge_skill_blocks_registry_bypass():
    request = ForgeSkillRequest(
        intent="register tool directly",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="registry.register({'name': 'bad'})\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.REGISTRY_BYPASS in assessment.deny_codes


def test_forge_skill_blocks_vault_bypass_even_with_seal():
    request = ForgeSkillRequest(
        intent="write direct audit receipt",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="VAULT999.write({'ok': True})\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.VAULT_BYPASS in assessment.deny_codes


def test_forge_skill_blocks_haram_code_patterns():
    request = ForgeSkillRequest(
        intent="clean working tree",
        domain="aforge",
        seal_verdict_id="seal_123",
        generated_code="import os\nos.system('rm -rf /')\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.VOID
    assert ForgeSkillDenyCode.HARAM_PATTERN in assessment.deny_codes


def test_forge_skill_irreversible_requires_f13_hold_path():
    request = ForgeSkillRequest(
        intent="delete production deployment permanently",
        domain="aforge",
        seal_verdict_id="seal_123",
        capability_class=GeneratedCapabilityClass.IRREVERSIBLE,
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
        f13_ack=False,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.HOLD_888
    assert ForgeSkillDenyCode.IRREVERSIBLE_REQUIRES_F13 in assessment.deny_codes


def test_forge_skill_irreversible_with_f13_ack_can_be_drafted():
    request = ForgeSkillRequest(
        intent="rotate irreversible production secret with approved runbook",
        domain="aforge",
        seal_verdict_id="seal_123",
        capability_class=GeneratedCapabilityClass.IRREVERSIBLE,
        generated_code="def run(payload):\n    return {'ok': True}\n",
        input_schema=READ_SCHEMA,
        output_schema=OUT_SCHEMA,
        f13_ack=True,
    )

    assessment = assess_forge_skill_request(request)

    assert assessment.verdict == ForgeSkillVerdict.ADMIT_DRAFT
    assert assessment.admissible is True
