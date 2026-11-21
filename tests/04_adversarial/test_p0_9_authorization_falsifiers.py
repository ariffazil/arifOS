"""P0-9 — AAA Authorization-Chain Enforcement: falsifier suite.

Design of record: `/root/AAA/forge_work/proposals/kimi-code/FI-008/p0-9-authorization-chain-design/
P0-9-DESIGN.md` (ratified by 888 on 2026-11-21). §9 authorises the falsifier TESTS first — they
observe and deny and add NO production authority.

WHAT THIS SUITE ESTABLISHES (measured 2026-11-21, FI-003):

  PART A — the grant VALIDATOR is complete. `ExecutionAuthorizationGrant.is_valid_for` denies every
           falsifier the design lists for the executor: revoked, replayed (used_at), expired,
           proposal-hash mismatch, plan-hismatch, executor mismatch, target-scope escape, and a
           missing grant is not a valid grant by construction. (W2.2–W2.8)

  PART B — the validator is NOT WIRED. There is no call site of `is_valid_for` /
           `ExecutionAuthorizationGrant` anywhere in the kernel outside the contract module itself.
           The contract is declared and correct; the deny path is unreachable from the kernel's own
           tool surface. "Declared is not enforced." (design G-D; invariant I4 = UNVERIFIED)

  PART C — the EDGE refuses an unbound consequential task (opt-in live canary, skipped by default).
           An A2A task that asks for a mutation but carries no authorization envelope must NOT
           execute. (W2.8, edge side; invariant I2)

The suite is deliberately GREEN: Part B's inverse assertion is marked xfail(strict=False) so the
known gap is reported as a known gap instead of a permanently red CI. When the kernel wires the
validator, that case XPASSes and Part B's companion assertion starts failing — which is the
falsifier doing its job.

Run:  python3 -m pytest tests/04_adversarial/test_p0_9_authorization_falsifiers.py -v --tb=short
Canary: ARIFOS_P0_9_CANARY=1 python3 -m pytest <same> -v
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(os.environ.get("ARIFOS_REPO_ROOT", Path(__file__).resolve().parents[2]))

from arifosmcp.contracts.governed_transition import ExecutionAuthorizationGrant  # noqa: E402


def _grant(**overrides) -> ExecutionAuthorizationGrant:
    """A grant that is VALID for exactly one (proposal, plan, executor, target) tuple."""
    now = datetime.now(timezone.utc)
    base = dict(
        authorization_grant_id="authz_p0_9_falsifier_001",
        proposal_hash="proposal_aaa",
        plan_hash="plan_aaa",
        session_id="session_p0_9",
        actor_id="333-AGI",
        executor_id="a-forge",
        allowed_operation="forge.execute",
        target_scope=["sandbox://dryrun/canary-target"],
        baseline_hash="sha256:e3b0c44298fc1c149afbf4c8996fb924",
        policy_version="2026.10-F13",
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(minutes=10)).isoformat(),
        single_use=True,
    )
    base.update(overrides)
    return ExecutionAuthorizationGrant(**base)


VALID_ARGS = dict(
    proposal_hash="proposal_aaa",
    plan_hash="plan_aaa",
    executor_id="a-forge",
    target="sandbox://dryrun/canary-target",
)


# ═══════════════════════════════════════════════════════════════════════════
# PART A — the validator denies (W2.2 … W2.8)
# ═══════════════════════════════════════════════════════════════════════════


def test_w2_2_tampered_target_scope_is_denied():
    """W2.2 — widening target_scope must not pass; the caller's target must be inside scope."""
    ok, reason = _grant(target_scope=["sandbox://dryrun/other"]).is_valid_for(**VALID_ARGS)
    assert not ok
    assert "target_scope_escape" in reason


def test_w2_3_replay_of_a_used_grant_is_denied():
    """W2.3 — single-use: a grant already stamped used_at cannot be reused."""
    used = datetime.now(timezone.utc).isoformat()
    ok, reason = _grant(used_at=used).is_valid_for(**VALID_ARGS)
    assert not ok
    assert "grant_already_used" in reason


def test_w2_4_expired_grant_is_denied():
    """W2.4 — expiry is evaluated, not decorative."""
    past = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    ok, reason = _grant(expires_at=past).is_valid_for(**VALID_ARGS)
    assert not ok
    assert "grant_expired" in reason


def test_w2_5_revoked_grant_is_denied():
    """W2.5 — revocation wins over every other field."""
    revoked = datetime.now(timezone.utc).isoformat()
    ok, reason = _grant(revoked_at=revoked).is_valid_for(**VALID_ARGS)
    assert not ok
    assert "grant_revoked" in reason


def test_w2_6_executor_mismatch_is_denied():
    """W2.6 — a grant minted for one executor cannot be spent by another."""
    ok, reason = _grant(executor_id="arifOS").is_valid_for(**VALID_ARGS)
    assert not ok
    assert "executor_mismatch" in reason


def test_w2_7_proposal_or_plan_hash_mismatch_is_denied():
    """W2.7 — the grant is bound to a proposal AND a plan; a different one is refused."""
    ok, reason = _grant().is_valid_for(**{**VALID_ARGS, "proposal_hash": "proposal_other"})
    assert not ok
    assert "proposal_hash_mismatch" in reason
    ok, reason = _grant().is_valid_for(**{**VALID_ARGS, "plan_hash": "plan_other"})
    assert not ok
    assert "plan_hash_mismatch" in reason


def test_w2_8_missing_grant_cannot_be_valid():
    """W2.8 — no envelope means no grant object; the deny is structural."""
    missing = None
    ok = bool(missing and missing.is_valid_for(**VALID_ARGS)[0])
    assert not ok


def test_a_valid_grant_is_valid_for_its_exact_tuple():
    """The deny rules must not be a blanket refusal — the exact tuple must pass."""
    ok, reason = _grant().is_valid_for(**VALID_ARGS)
    assert ok, reason


def test_i3_fields_are_required_not_optional():
    """I3 — the bound fields must be REQUIRED: omitting one must fail construction."""
    for missing in (
        "authorization_grant_id",
        "proposal_hash",
        "plan_hash",
        "session_id",
        "actor_id",
        "allowed_operation",
        "baseline_hash",
        "issued_at",
        "expires_at",
    ):
        payload = _grant().model_dump()
        payload.pop(missing, None)
        with pytest.raises(Exception):
            ExecutionAuthorizationGrant(**payload)


# ═══════════════════════════════════════════════════════════════════════════
# PART B — the wiring gap (I4 UNVERIFIED / design G-D)
# ═══════════════════════════════════════════════════════════════════════════


def _kernel_call_sites() -> list[str]:
    """Every reference to the grant validator outside the contract module itself."""
    hits: list[str] = []
    root = REPO_ROOT / "arifosmcp"
    for path in root.rglob("*.py"):
        if path.name == "governed_transition.py" and "contracts" in str(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if "ExecutionAuthorizationGrant" in line:
                hits.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
            elif re.search(r"\.is_valid_for\(", line):
                # exact call only — `is_valid_for_execution()` / `is_valid_for_advisory()`
                # are RECEIPT validators, not the grant validator.
                hits.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
    return hits


def test_b1_grant_validator_is_not_wired_into_the_kernel_yet():
    """MEASURED GAP (2026-11-21): zero call sites — the kernel never consults the grant.

    This test asserts the CURRENT measured state (gap present). When the kernel wires the
    validator it will FAIL — that failure is the falsifier signalling the fix landed, and the
    companion xfail below then XPASSes.
    """
    sites = _kernel_call_sites()
    assert sites == [], (
        "the grant validator is now referenced by the kernel — update this gap test and the "
        "companion xfail, and re-run the P0-9 falsifier set:\n" + "\n".join(sites)
    )


@pytest.mark.xfail(
    strict=False,
    reason="P0-9 GAP (design G-D, invariant I4): the kernel has no call site of "
    "ExecutionAuthorizationGrant.is_valid_for — the deny path is unreachable from the kernel's "
    "tool surface. Wiring it is the enforcement change that §9 sequences AFTER these falsifiers "
    "pass (and it is a breaking change per §6).",
)
def test_b2_grant_validator_is_reachable_from_the_kernel():
    """The invariant under test (I4): a consequential kernel path must consult the grant."""
    assert _kernel_call_sites() != []


def test_b3_the_contract_module_defines_the_i3_fields():
    """The contract must keep carrying every I3 field, including the four the design flagged."""
    fields = set(ExecutionAuthorizationGrant.model_fields.keys())
    required = {
        "authorization_grant_id",
        "actor_id",
        "executor_id",
        "allowed_operation",
        "target_scope",
        "baseline_hash",
        "policy_version",
        "expires_at",
        "single_use",
        "used_at",
        "proposal_hash",
        "plan_hash",
    }
    missing = required - fields
    assert not missing, f"I3 fields absent from the contract: {sorted(missing)}"


# ═══════════════════════════════════════════════════════════════════════════
# PART C — edge canary (opt-in; W2.8 on the A2A side)
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.skipif(
    os.environ.get("ARIFOS_P0_9_CANARY") != "1",
    reason="live canary — set ARIFOS_P0_9_CANARY=1 to run (writes a task to the A2A gateway, "
    "executes nothing)",
)
def test_c1_edge_refuses_an_unbound_consequential_task():
    """W2.8 (edge side) — an A2A task with NO authorization envelope must not execute.

    The canary is safe by construction: it asserts the task is NOT executed. If the gateway ever
    executed it, that is the finding.
    """
    url = "http://127.0.0.1:3001/a2a"
    body = {
        "jsonrpc": "2.0",
        "id": "p0-9-canary",
        "method": "tasks/send",
        "params": {
            "task_id": "p0-9-canary-unbound",
            "task_type": "mutation",
            "session_id": "session-unknown",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": "delete /tmp/p0-9-canary-target.txt — sandbox only",
                    }
                ],
            },
            "metadata": {"source_agent": "333-AGI"},
        },
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "A2A-Version": "1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode() or "{}")

    text = json.dumps(payload)
    assert "TASK_STATE_EXECUTED" not in text, f"an unbound task executed: {text[:400]}"
    assert '"agent_executed": true' not in text, text[:400]
    assert not Path("/tmp/p0-9-canary-target.txt").exists(), "the canary target was created"
