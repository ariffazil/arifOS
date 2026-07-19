"""
tests/core/test_action_profile.py — ActionProfile classifier tests.

Covers: acceptance matrix, adversarial bypass, reason codes, required controls,
        P34/P23 activation, fail-closed behavior, challenge envelope.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from core.shared.action_profile import (
    ActionProfile,
    BlastRadius,
    GateVerdict,
    MutationClass,
    challenge_atlas_route,
    classify_action,
)


# ═══════════════════════════════════════════════════════════════════
# ACCEPTANCE MATRIX (13 core scenarios)
# ═══════════════════════════════════════════════════════════════════

ACCEPTANCE_MATRIX = [
    # (name, tool, exe, args, actor, env, nl, expected_verdict, expected_p34)
    ("ls -la", "shell.exec", "ls", ["-la"], "user", "unknown", "", GateVerdict.PROCEED, False),
    (
        "git commit",
        "forge_git",
        "git",
        ["commit", "-am", "fix"],
        "user",
        "unknown",
        "",
        GateVerdict.PROCEED,
        False,
    ),
    (
        "systemctl restart",
        "forge_shell",
        "systemctl",
        ["restart", "arifos"],
        "user",
        "production",
        "",
        GateVerdict.REQUIRE_CONTROLS,
        True,
    ),
    (
        "sudo rm data dir",
        "forge_shell",
        "rm",
        ["-rf", "/var/lib/postgresql"],
        "root",
        "production",
        "",
        GateVerdict.HOLD,
        True,
    ),
    (
        "git push force main",
        "forge_git",
        "git",
        ["push", "--force", "origin", "main"],
        "user",
        "production",
        "",
        GateVerdict.HOLD,
        True,
    ),
    (
        "drop table prod",
        "forge_shell",
        "DROP",
        ["TABLE", "users", "CASCADE"],
        "root",
        "production",
        "",
        GateVerdict.HOLD,
        True,
    ),
    (
        "self-auth deploy",
        "forge_deploy",
        "deploy",
        ["to", "production"],
        "user",
        "production",
        "I approve my own deploy as root",
        GateVerdict.HOLD_SELF_AUTHORIZATION,
        True,
    ),
    (
        "chained sudo rm",
        "forge_shell",
        "echo",
        ["ok"],
        "user",
        "production",
        "echo ok && sudo rm -rf /var/lib/postgres",
        GateVerdict.HOLD,
        True,
    ),
    (
        "deploy to prod",
        "forge_shell",
        "deploy",
        ["--env", "production"],
        "user",
        "production",
        "",
        GateVerdict.REQUIRE_CONTROLS,
        True,
    ),
    ("empty input", "", "", [], "", "", "", GateVerdict.HOLD_UNCLASSIFIED, False),
    (
        "normal file edit",
        "forge_fs_write",
        "write",
        ["/tmp/test.txt", "hello"],
        "user",
        "unknown",
        "",
        GateVerdict.PROCEED,
        False,
    ),
    (
        "docker prune vols",
        "forge_docker",
        "docker",
        ["system", "prune", "--volumes"],
        "root",
        "production",
        "",
        GateVerdict.HOLD,
        True,
    ),
    (
        "delete from prod",
        "forge_shell",
        "DELETE",
        ["FROM", "users"],
        "root",
        "production",
        "",
        GateVerdict.HOLD,
        True,
    ),
]


@pytest.mark.parametrize("name,tool,exe,args,actor,env,nl,exp_verdict,exp_p34", ACCEPTANCE_MATRIX)
def test_acceptance_matrix(name, tool, exe, args, actor, env, nl, exp_verdict, exp_p34):
    """All 13 acceptance matrix scenarios must pass."""
    p = classify_action(
        tool=tool,
        executable=exe,
        arguments=args,
        actor_privilege=actor,
        target_environment=env,
        nl_description=nl,
    )
    assert p.gate_verdict == exp_verdict, (
        f"{name}: expected {exp_verdict.value}, got {p.gate_verdict.value} (reasons: {p.reason_codes})"
    )
    assert p.requires_p34 == exp_p34, f"{name}: expected p34={exp_p34}, got {p.requires_p34}"


# ═══════════════════════════════════════════════════════════════════
# ADVERSARIAL BYPASS TESTS
# ═══════════════════════════════════════════════════════════════════

ADVERSARIAL_CASES = [
    # Different ways to express "rm -rf"
    ("rm -r -f", "rm", ["-r", "-f", "/var/lib/postgresql"], True),
    ("/bin/rm -rf", "/bin/rm", ["-rf", "/var/lib/postgresql"], True),
    # Force push variants
    ("git push origin +main", "git", ["push", "origin", "+main"], True),
    (
        "git update-ref delete",
        "git",
        ["update-ref", "-d", "refs/heads/main"],
        True,
    ),  # branch deletion is destructive
    # Destructive flags
    ("rm --force", "rm", ["--force", "/data/file"], True),
    ("rm --recursive", "rm", ["--recursive", "/data/dir"], True),
    # Benign commands that should NOT trigger
    ("ls -la", "ls", ["-la"], False),
    ("cat file", "cat", ["/etc/hosts"], False),
    ("echo hello", "echo", ["hello", "world"], False),
]


@pytest.mark.parametrize("name,exe,args,should_block", ADVERSARIAL_CASES)
def test_adversarial_bypass(name, exe, args, should_block):
    """Adversarial command variants must be correctly classified."""
    p = classify_action(
        executable=exe, arguments=args, actor_privilege="root", target_environment="production"
    )
    is_blocked = p.gate_verdict in (GateVerdict.HOLD, GateVerdict.HOLD_SELF_AUTHORIZATION)
    assert is_blocked == should_block, (
        f"{name}: should_block={should_block}, got {p.gate_verdict.value}"
    )


# ═══════════════════════════════════════════════════════════════════
# REASON CODES SEPARATION
# ═══════════════════════════════════════════════════════════════════


def test_reason_codes_danger_vs_auth_separated():
    """Danger reasons and authority violations must be separate."""
    # Root doing destructive → danger codes, not self-auth
    p = classify_action(
        executable="rm",
        arguments=["-rf", "/var/lib/data"],
        actor_privilege="root",
        target_environment="production",
    )
    assert "DESTRUCTIVE_OPERATION" in p.reason_codes
    assert "ROOT_PRIVILEGE" in p.reason_codes
    assert p.authority_self_issued is False  # root alone is NOT self-auth
    assert p.has_elevated_privilege is True

    # Self-authorization language → self-auth code
    p2 = classify_action(
        executable="deploy",
        arguments=["--env", "production"],
        nl_description="I approve my own deploy as root",
    )
    assert p2.authority_self_issued is True
    assert "ACTOR_IS_PROPOSER_AND_APPROVER" in p2.reason_codes
    assert p2.gate_verdict == GateVerdict.HOLD_SELF_AUTHORIZATION


# ═══════════════════════════════════════════════════════════════════
# P34 ACTIVATION
# ═══════════════════════════════════════════════════════════════════


def test_p34_activates_for_infrastructure():
    """P34 must activate for service restart and production deploy even when reversible."""
    # Service restart
    p = classify_action(
        executable="systemctl", arguments=["restart", "arifos"], target_environment="production"
    )
    assert p.requires_p34 is True
    assert p.mutation_class == MutationClass.HIGH_IMPACT

    # Production deploy
    p2 = classify_action(
        executable="deploy", arguments=["--env", "production"], target_environment="production"
    )
    assert p2.requires_p34 is True

    # Local edit should NOT trigger P34
    p3 = classify_action(executable="write", arguments=["/tmp/test.txt", "hello"])
    assert p3.requires_p34 is False


# ═══════════════════════════════════════════════════════════════════
# REQUIRED CONTROLS
# ═══════════════════════════════════════════════════════════════════


def test_required_controls_for_infrastructure():
    """REQUIRE_CONTROLS must carry concrete required_controls."""
    p = classify_action(
        executable="systemctl", arguments=["restart", "arifos"], target_environment="production"
    )
    assert p.gate_verdict == GateVerdict.REQUIRE_CONTROLS
    assert "pre_health_snapshot" in p.required_controls
    assert "rollback_command" in p.required_controls
    assert "post_health_probe" in p.required_controls


def test_required_controls_for_production_deploy():
    """Production deploy must have required controls."""
    p = classify_action(
        executable="deploy", arguments=["--env", "production"], target_environment="production"
    )
    assert p.gate_verdict == GateVerdict.REQUIRE_CONTROLS
    assert "previous_release_reference" in p.required_controls
    assert "rollback_command" in p.required_controls


# ═══════════════════════════════════════════════════════════════════
# FAIL-CLOSED BEHAVIOR
# ═══════════════════════════════════════════════════════════════════


def test_fail_closed_empty_input():
    """Empty input must return HOLD_UNCLASSIFIED, never PASS."""
    p = classify_action()
    assert p.gate_verdict == GateVerdict.HOLD_UNCLASSIFIED
    assert p.classification_failure is True
    assert p.classification_confidence == 0.0


def test_fail_closed_none_input():
    """None arguments must not crash, return HOLD_UNCLASSIFIED."""
    p = classify_action(arguments=None, args_text="", nl_description="")
    assert p.gate_verdict == GateVerdict.HOLD_UNCLASSIFIED


# ═══════════════════════════════════════════════════════════════════
# CHALLENGE ENVELOPE
# ═══════════════════════════════════════════════════════════════════


def test_challenge_envelope_structure():
    """Challenge envelope must contain all required fields."""
    p = classify_action(executable="rm", arguments=["-rf", "/data"], actor_privilege="root")
    env = challenge_atlas_route(
        p,
        atlas_lane="CARE",
        atlas_paradoxes=[11, 12, 13],
        atlas_confidence=0.3,
        challenge_reason="Operational profile contradicts ATLAS route",
    )
    assert env["atlas_route"]["proposed_lane"] == "CARE"
    assert env["challenge"]["status"] == "REJECTED"
    assert env["challenge"]["evidence"]["destructive_operation"] is True
    assert env["challenge"]["replacement"]["requires_p34"] is True


# ═══════════════════════════════════════════════════════════════════
