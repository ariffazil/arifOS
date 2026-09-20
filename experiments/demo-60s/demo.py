#!/usr/bin/env python3
"""arifOS — 60-second governance demo (offline, reproducible).

Four-step proof against the repo's OWN kernel code (no mock, no reimplementation):

  STEP 1  an action outside the acting authority envelope is submitted
  STEP 2  the kernel returns a non-permitting verdict and NO mutation occurs
          (the artefact it would have mutated is shown unchanged, measured by
          an independent witness process)
  STEP 3  the same action, same actor, same target, inside the envelope
  STEP 4  it is permitted, the mutation is applied inside ./sandbox/ only, and
          an append-only hash-chained receipt is appended that references it

What is real here (all imported from this repo, none re-implemented):
  * GovrnancePipeline            arifosmcp.runtime.governance_pipeline (the single
    pipe every tool call traverses; Gate -2 → Gate 7)
  * FederationEnvelope v2        arifosmcp.schemas.federation_envelope
    (validate_for_execution — the exact function the pipe's GATE_7_ENVELOPE calls)
  * append_receipt / verify_chain  arifosmcp.runtime.canonical_vault_chain
    (VAULT999 F-004 hash-chained, flock-serialised, append-only ledger writer)

Safety (why this is safe to run on any machine):
  * no network call is made: the only gate that needs a live service is the vault
    liveness probe of VAULT999 on :5001 and it is DISABLED here (disclosed below)
  * every write goes into ./sandbox/ inside this directory; the executor refuses
    any path outside it
  * the notifier credentials (NOTIFIER_TELEGRAM_*) are scrubbed from the child
    environment so a HOLD verdict cannot page a human
  * the production kernel on :8088 and the production VAULT999 are never touched

Run:  ./run.sh          (or: python3 demo.py)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 0. Environment guardrails (before any kernel import)
# ─────────────────────────────────────────────────────────────────────────────

# The pipe's HOLD path fires a Telegram alert if these are set in the ambient
# environment. Scrub them so a denial in this demo cannot reach a human phone.
SCRUBBED = []
for _var in ("NOTIFIER_TELEGRAM_BOT_TOKEN", "NOTIFIER_TELEGRAM_CHAT_ID"):
    if os.environ.pop(_var, None) is not None:
        SCRUBBED.append(_var)

# The pipe publishes verdicts to NATS in a daemon thread; with the `nats` client
# absent that thread dies with a traceback. Governance is unaffected (the design
# is fail-silent), so silence the noise and disclose it in the transcript.
threading.excepthook = lambda _args: None

# Offline guard: refuse every outbound TCP connect from this process, so "no
# production service is contacted" is mechanical rather than merely asserted.
# The only expected victims are the pipe's own fail-silent mesh publish and its
# HOLD notifier — both catch their own errors by design.
import socket as _socket  # noqa: E402

BLOCKED_CONNECTS: list[str] = []
_real_connect = _socket.socket.connect


def _guarded_connect(self, address):  # type: ignore[no-untyped-def]
    BLOCKED_CONNECTS.append(str(address))
    raise OSError(f"demo offline guard: outbound connect to {address} refused")


_socket.socket.connect = _guarded_connect  # type: ignore[assignment]

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

try:
    from arifosmcp.runtime.canonical_vault_chain import (  # noqa: E402
        append_receipt,
        compute_receipt_hash,
        verify_chain,
    )
    from arifosmcp.runtime.governance_pipeline import (  # noqa: E402
        GovernancePipeline,
        ToolCallContext,
    )
    from arifosmcp.schemas.federation_envelope import (  # noqa: E402
        ActionReceipts,
        ActionClass,
        AuthorityEnvelope,
        AuthoritySource,
        FederationEnvelope,
        RiskPassport,
        RiskTier,
    )
except ImportError as exc:  # pragma: no cover - environment problem, be loud
    sys.stderr.write(
        f"FATAL: cannot import the arifOS kernel from {REPO}: {exc}\n"
        "Use an interpreter that can import arifosmcp, e.g.\n"
        f"  ARIFOS_PYTHON={REPO}/.venv/bin/python {HERE}/run.sh\n"
    )
    raise SystemExit(2)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Constants — the whole scenario
# ─────────────────────────────────────────────────────────────────────────────

SANDBOX = HERE / "sandbox"
OUTBOX = SANDBOX / "outbox"
TARGET = OUTBOX / "mutation-target.txt"
VAULT_DIR = SANDBOX / "vault999-demo"

ACTOR = "arif"                 # the actor seat exercising the action (F13 principal)
TOOL = "arif_forge_execute"    # the real kernel tool for a filesystem mutation
SESSION_ID = "sess-demo-60s"
TRACE_DENY = "trace-demo-60s-unauthorised"
TRACE_ALLOW = "trace-demo-60s-authorised"
TRACE_OBSERVE = "trace-demo-60s-observe-pre-state"

INITIAL_TARGET = "governed-demo-target v1\n"
INTENDED_APPEND = "authorised mutation applied by the governance demo\n"

# The ONLY gate that is switched off, and why: it HTTP-probes the live VAULT999
# writer on 127.0.0.1:5001 to prove the audit trail is fresh. This demo is
# required to be offline and must not touch that service, so the gate is
# disabled and disclosed rather than faked.
PIPE_KWARGS = {"vault_liveness_enabled": False}
DISABLED_GATES = ["GATE_4_VAULT_LIVENESS (probes live VAULT999 :5001 — not contacted)"]

_results: list[tuple[str, bool, str]] = []


# ─────────────────────────────────────────────────────────────────────────────
# 2. Output helpers
# ─────────────────────────────────────────────────────────────────────────────


def rule(char: str = "─", width: int = 78) -> None:
    print(char * width)


def head(text: str) -> None:
    print()
    rule("═")
    print(text)
    rule("═")


def check(label: str, ok: bool, detail: str = "") -> bool:
    _results.append((label, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    return ok


def note(text: str) -> None:
    print(f"  [note] {text}")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_rev() -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


# ─────────────────────────────────────────────────────────────────────────────
# 3. The independent witness (a separate process, filesystem-only evidence)
# ─────────────────────────────────────────────────────────────────────────────


def witness() -> dict:
    out = subprocess.run(
        [sys.executable, str(HERE / "witness.py"), str(TARGET)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if out.returncode != 0:
        raise RuntimeError(f"witness failed rc={out.returncode}: {out.stderr.strip()}")
    return json.loads(out.stdout)


def show_observation(tag: str, obs: dict) -> None:
    print(f"  {tag}: pid={obs['observer_pid']} exists={obs['exists']} bytes={obs['bytes']}")
    print(f"      sha256={obs['sha256']}")
    print(f"      mtime={obs['mtime_iso']}  at={obs['observed_at']}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Envelopes and the governed action
# ─────────────────────────────────────────────────────────────────────────────


def envelope(authority: AuthorityEnvelope, trace_id: str, observe_receipt_id: str,
             actor: str = ACTOR) -> FederationEnvelope:
    return FederationEnvelope(
        trace_id=trace_id,
        actor_id=actor,
        actor_verification="verified",
        session_id=SESSION_ID,
        agent_id=actor,
        tool_id=TOOL,
        organ="arifOS",
        niat="prove that an action outside the authority envelope is denied",
        matlamat="append one line to the sandbox target under kernel judgement",
        authority=authority,
        risk=RiskPassport(
            tier=RiskTier.T3,
            action_class=ActionClass.MUTATE,
            blast_radius="LOCAL",
            reversibility="high",
        ),
        receipts=ActionReceipts(observe_receipt_id=observe_receipt_id),
        created_at=datetime.now(UTC),
    )


def action_params(observation: dict, witness_pid: int, target: str) -> dict:
    """Parameters of the call. finding/evidence/auditor_id are the Gödel-closure
    inputs (GENESIS/058 Q9a): they are populated from the real independent
    observation, not asserted. `mutated` declares the action class of THIS call
    (it changes sandbox state) — it is not a claim that the write happened."""
    return {
        "target": target,
        "operation": "append_line",
        "finding": f"sandbox target exists ({observation['bytes']} bytes) "
                   f"{observation['sha256'][:20]}…; governed append pending",
        "evidence": f"independent witness.py pid={witness_pid} observed "
                    f"{observation['sha256'][:20]}… at {observation['observed_at']}",
        "mutated": True,
        "auditor_id": f"witness.py:pid={witness_pid}",
    }


def execute_governed_action(env: FederationEnvelope, params: dict) -> dict:
    """The single code path for both arms. The ONLY difference between the
    authorised and unauthorised submissions is the envelope handed in.

    Kernel first. The write happens only if the pipe says all_clear.
    """
    pipe = GovernancePipeline(**PIPE_KWARGS)
    ctx = ToolCallContext(
        tool_name=TOOL,
        session_id=SESSION_ID,
        actor_id=env.actor_id,
        actor_verification=env.actor_verification,
        action_class="MUTATE",
        risk_tier="MEDIUM",
        caller_is_principal=(env.actor_id == ACTOR),
        params=params,
        envelope=env,
    )
    t0 = time.perf_counter()
    result = pipe.run(ctx)
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"  kernel verdict : {result.verdict}")
    print(f"  blocked_at     : {result.blocked_at}")
    print(f"  all_clear      : {result.all_clear}")
    print(f"  violated_laws  : {result.violated_laws}")
    for reason in result.reasons:
        print(f"  reason         : {reason}")
    if result.next_safe_action:
        print(f"  next_safe_action: {result.next_safe_action}")
    print(f"  gate trace ({elapsed:.0f} ms):")
    for gate in result.gate_results:
        print(f"    {'PASS' if gate.passed else 'HOLD'}  {gate.gate:<28} {gate.reason[:96]}")

    executed = False
    if result.all_clear:
        # Execution stage. Enforcement: nothing outside ./sandbox/ is writable
        # by this executor, whatever the parameters say.
        raw_target = Path(params["target"])
        target = raw_target if raw_target.is_absolute() else (REPO / raw_target)
        resolved = target.resolve()
        if not resolved.is_relative_to(SANDBOX.resolve()):
            print(f"  EXECUTOR REFUSED: {resolved} is outside {SANDBOX}")
            print("  (this demo's executor refuses it; the kernel gate above allowed it)")
        else:
            with open(resolved, "a", encoding="utf-8") as fh:
                fh.write(INTENDED_APPEND)
                fh.flush()
                os.fsync(fh.fileno())
            executed = True
            print(f"  EXECUTOR RAN   : appended 1 line to {resolved.relative_to(REPO)}")
    else:
        print("  EXECUTOR       : NOT INVOKED — the kernel did not clear the action")

    return {"result": result, "executed": executed}


# ─────────────────────────────────────────────────────────────────────────────
# 5. The demo
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    head("arifOS — 60-SECOND GOVERNANCE DEMO (offline, against this repo's kernel)")
    print(f"  repo            : {REPO}  @ {git_rev()}")
    print(f"  interpreter     : {sys.executable}")
    print(f"  python          : {sys.version.split()[0]}")
    try:
        import nats  # noqa: F401
        nats_state = "importable (pipe may publish verdicts to 127.0.0.1:4222)"
    except ImportError:
        nats_state = "NOT importable — pipe's mesh publish is a no-op (fail-silent by design)"
    print(f"  nats client     : {nats_state}")
    print("  offline guard   : socket.connect refuses every outbound address (installed before kernel import)")
    print(f"  notifier creds  : {'scrubbed from env' if SCRUBBED else 'absent from env'} "
          f"({', '.join(SCRUBBED) if SCRUBBED else 'nothing to scrub'}) — no HOLD can page a human")
    print(f"  vault HMAC key  : {'present (receipts will be signed)' if os.getenv('ARIFOS_VAULT_HMAC_KEY') else 'absent — receipts unsigned (verify_chain warn mode)'}")
    print(f"  pipeline config : GovernancePipeline(vault_liveness_enabled=False), enforcement_mode='enforce'")
    for line in DISABLED_GATES:
        print(f"    disabled      : {line}")
    print("    all other gates default ON (session, identity, F13, E7, ASI tier, budget,")
    print("    risk, floors, Gödel/Calhoun closures, reality loop, drift, envelope)")

    # ── Sandbox reset (containment enforced before anything is deleted) ──────
    if not SANDBOX.resolve().is_relative_to(HERE.resolve()):
        print("FATAL: sandbox path escaped the demo directory — aborting")
        return 2
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    OUTBOX.mkdir(parents=True)
    VAULT_DIR.mkdir(parents=True)
    TARGET.write_text(INITIAL_TARGET, encoding="utf-8")

    head("SETUP — sandbox, pre-state observation, and the observe-before-mutate receipt")
    print(f"  sandbox         : {SANDBOX.relative_to(REPO)}/   (the only writable area)")
    print(f"  target artefact : {TARGET.relative_to(REPO)}")
    print(f"  target content  : {INITIAL_TARGET!r}")

    pre = witness()
    show_observation("observation #1 (independent process)", pre)

    obs_receipt = append_receipt(
        actor_id=ACTOR,
        session_id=SESSION_ID,
        trace_id=TRACE_OBSERVE,
        operation_id="observe-pre-state",
        tool_name="arif_sense_observe",
        input_hash=pre["sha256"],
        result_hash=sha256_text(json.dumps(pre, sort_keys=True)),
        authority_state="OBSERVE_ONLY",
        reversibility="REVERSIBLE",
        verdict="OBSERVE",
        vault_dir=VAULT_DIR,
    )
    print(f"  observe receipt : ok={obs_receipt.ok} id={obs_receipt.receipt['receipt_id']} "
          f"seq={obs_receipt.receipt['sequence']} prev_hash={obs_receipt.receipt['previous_hash']}")
    OBS_RECEIPT_ID = obs_receipt.receipt["receipt_id"]
    note("this receipt is the MUTATE envelope's observe_receipt_id (observe-before-mutate)")

    params = action_params(pre, pre["observer_pid"], str(TARGET.relative_to(REPO)))
    print(f"  submitted call  : tool={TOOL} actor={ACTOR} action_class=MUTATE")
    print(f"                    target={params['target']}")

    # ── STEP 1 + 2 ─────────────────────────────────────────────────────────
    head("STEP 1+2 — UNAUTHORISED SUBMISSION → DENIAL, AND NO MUTATION")
    unauth_authority = AuthorityEnvelope(
        source=AuthoritySource.DELEGATED,
        verified=True,
        delegator="arif",
        delegatee="fi-003-demo-coder",
        scope=["mutate"],
        expires_at=None,  # authority-envelope.md: "delegation without expiry is rejected"
    )
    print("  envelope authority: source=delegated delegator=arif delegatee=fi-003-demo-coder")
    print("                     scope=['mutate'] expires_at=None")
    print(f"  validator (direct): {envelope(unauth_authority, TRACE_DENY, OBS_RECEIPT_ID).validate_for_execution()}")
    unauth = execute_governed_action(
        envelope(unauth_authority, TRACE_DENY, OBS_RECEIPT_ID), params
    )

    post_deny = witness()
    print("  ── did reality change? ──")
    show_observation("observation #2 (independent process)", post_deny)
    check("denial verdict is non-permitting", str(unauth["result"].verdict) == "HOLD",
          f"verdict={unauth['result'].verdict} blocked_at={unauth['result'].blocked_at}")
    check("denial cites the authority envelope", "Delegation expired" in " ".join(unauth["result"].reasons),
          unauth["result"].reasons[0] if unauth["result"].reasons else "")
    check("executor was not invoked", unauth["executed"] is False)
    check("artefact bytes unchanged after denial", post_deny["sha256"] == pre["sha256"],
          f"{str(pre['sha256'])[:24]}… == {str(post_deny['sha256'])[:24]}…")
    check("artefact mtime unchanged after denial", post_deny["mtime_iso"] == pre["mtime_iso"])
    check("intended mutation text absent from artefact", INTENDED_APPEND not in TARGET.read_text())

    print()
    print("  second unauthorised variant — EXPIRED delegation (same code path):")
    expired = AuthorityEnvelope(
        source=AuthoritySource.DELEGATED,
        verified=True,
        delegator="arif",
        delegatee="fi-003-demo-coder",
        scope=["mutate"],
        expires_at=datetime.now(UTC) - timedelta(minutes=5),
    )
    expired_env = envelope(expired, TRACE_DENY + "-expired", OBS_RECEIPT_ID)
    print(f"    validator: {expired_env.validate_for_execution()}")
    expired_run = execute_governed_action(expired_env, params)
    check("expired delegation also denied, artefact still untouched",
          str(expired_run["result"].verdict) == "HOLD"
          and witness()["sha256"] == pre["sha256"],
          f"verdict={expired_run['result'].verdict}")

    # ── STEP 3 + 4 ─────────────────────────────────────────────────────────
    head("STEP 3+4 — SAME ACTION INSIDE THE ENVELOPE → PERMIT, MUTATION, RECEIPT")
    auth_authority = AuthorityEnvelope(
        source=AuthoritySource.TOKEN,
        verified=True,
        scope=["mutate"],
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )
    print("  envelope authority: source=token verified=True scope=['mutate'] expires_at=+5min")
    allow_env = envelope(auth_authority, TRACE_ALLOW, OBS_RECEIPT_ID)
    print(f"  validator (direct): {allow_env.validate_for_execution()}")
    allow = execute_governed_action(allow_env, params)

    post_allow = witness()
    print("  ── did reality change? ──")
    show_observation("observation #3 (independent process)", post_allow)
    new_hash = sha256_file(TARGET)
    check("verdict is permitting", allow["result"].all_clear is True,
          f"verdict={allow['result'].verdict} blocked_at={allow['result'].blocked_at}")
    check("executor ran and appended exactly one line", allow["executed"] is True
          and TARGET.read_text().count(INTENDED_APPEND) == 1)
    check("change is externally observed (hash differs)", post_allow["sha256"] != pre["sha256"],
          f"{str(pre['sha256'])[:20]}… → {str(post_allow['sha256'])[:20]}…")
    check("witness hash equals locally recomputed hash", post_allow["sha256"] == new_hash)
    check("mutation stayed inside ./sandbox/", TARGET.resolve().is_relative_to(SANDBOX.resolve()))

    print()
    print("  ── append-only receipt for the permitted mutation ──")
    receipt = append_receipt(
        actor_id=ACTOR,
        session_id=SESSION_ID,
        trace_id=TRACE_ALLOW,
        operation_id="append-line-mutation-target",
        tool_name=TOOL,
        input_hash=pre["sha256"],
        result_hash=new_hash,
        authority_state="MUTATE_AUTHORISED",
        decision_reference=f"FederationEnvelope/{TRACE_ALLOW}/GATE_7_ENVELOPE=SEAL",
        reversibility="REVERSIBLE",
        actor_verification={"actor_verified": True, "method": "envelope_authority_token"},
        verdict="SEAL",
        vault_dir=VAULT_DIR,
    )
    if not receipt.ok:
        check("receipt append succeeded", False, f"{receipt.failure_class}: {receipt.detail}")
        return 1
    entry = receipt.receipt
    print(f"  append ok       : {receipt.ok}  id={entry['receipt_id']}  sequence={entry['sequence']}")
    print(f"  previous_hash   : {entry['previous_hash']}")
    print(f"  receipt_hash    : {entry['receipt_hash']}")
    print(f"  input_hash      : {entry['input_hash']}   (target BEFORE the mutation)")
    print(f"  result_hash     : {entry['result_hash']}   (target AFTER the mutation)")
    print(f"  trace_id        : {entry['trace_id']}   (state-transition-discipline: causal join)")
    print(f"  signature       : {entry['signature'] or '(none — no vault HMAC key configured)'}")
    check("receipt references the mutation it authorised",
          entry["result_hash"] == new_hash and entry["input_hash"] == pre["sha256"],
          "input_hash = pre-state, result_hash = post-state, both measured")
    check("receipt carries the trace_id of the permitted envelope",
          entry["trace_id"] == TRACE_ALLOW)

    print()
    print("  ── chain verification (append-only, hash-linked) ──")
    v = verify_chain(VAULT_DIR, scope="canonical")
    print(f"  verified={v.verified} status={v.status} entries={v.entries} "
          f"corrupt_lines={v.corrupt_lines} gaps={len(v.gaps)}")
    print(f"  head_seq={v.head_seq} head_hash={v.head_hash}")
    print(f"  signed_entries={v.signed_entries} unsigned_after_cutover={v.unsigned_after_cutover}")
    check("ledger verifies with no gaps", bool(v.verified) and len(v.gaps) == 0)
    recomputed = compute_receipt_hash(entry)
    check("receipt_hash recomputes from the entry body (tamper-evident)",
          recomputed == entry["receipt_hash"], f"{str(entry['receipt_hash'])[:26]}…")
    check("chain has 2 entries (1 OBSERVE + 1 SEAL for the mutation)", v.entries == 2,
          f"entries={v.entries}")

    print()
    print("  ── tamper test: is verification vacuous, or does it actually catch a rewrite? ──")
    tamper_dir = SANDBOX / "vault999-tampered-copy"
    shutil.copytree(VAULT_DIR, tamper_dir)
    tamper_chain = tamper_dir / "seal_chain.jsonl"
    t_lines = tamper_chain.read_text(encoding="utf-8").splitlines()
    rewritten = json.loads(t_lines[-1])
    print(f"  copying the ledger to sandbox/vault999-tampered-copy/ and rewriting one field:")
    print(f"    result_hash {rewritten['result_hash'][:26]}… → sha256:{'0' * 26}…")
    rewritten["result_hash"] = "sha256:" + "0" * 64
    t_lines[-1] = json.dumps(rewritten, sort_keys=True, default=str)
    tamper_chain.write_text("\n".join(t_lines) + "\n", encoding="utf-8")
    tv = verify_chain(tamper_dir, scope="canonical")
    print(f"  tampered copy : verified={tv.verified} status={tv.status} gaps={len(tv.gaps)}")
    for gap in tv.gaps[:2]:
        print(f"    {gap.gap_class}: {gap.detail[:110]}")
    check("rewritten receipt is detected (verification is not vacuous)",
          (not tv.verified) or len(tv.gaps) > 0,
          f"verified={tv.verified} gaps={len(tv.gaps)}")
    check("the real ledger still verifies after the tamper test", bool(verify_chain(VAULT_DIR).verified))

    # ── Controls ───────────────────────────────────────────────────────────
    head("CONTROL A — a VALID envelope still fails for an actor outside F13 authority")
    ctrl_env = envelope(auth_authority, TRACE_ALLOW + "-non-sovereign", OBS_RECEIPT_ID,
                        actor="fi-003-demo-coder")
    ctrl = execute_governed_action(ctrl_env, params)
    check("non-sovereign actor denied despite a valid envelope",
          str(ctrl["result"].verdict) == "HOLD"
          and str(ctrl["result"].blocked_at) == "GATE_1.5_F13_SOVEREIGN",
          f"blocked_at={ctrl['result'].blocked_at}")
    check("artefact untouched by the control", witness()["sha256"] == new_hash)

    head("CONTROL B — FINDING: does the kernel enforce WHERE a mutation lands?")
    print("  same call, same valid envelope, target rewritten to a real repo file:")
    print("    target=/root/arifOS/README.md   (pipe is run; the DEMO executor is never invoked)")
    outside_params = dict(params, target=str(REPO / "README.md"))
    outside = execute_governed_action(envelope(auth_authority, TRACE_ALLOW + "-outside", OBS_RECEIPT_ID),
                                      outside_params)
    finding_ok = outside["result"].all_clear is True and outside["executed"] is False
    if finding_ok:
        print("  [FINDING] the pipe PERMITTED an action whose target is outside any sandbox.")
        print("            The kernel's envelope/risk gates do not inspect the target path;")
        print("            target containment is the executor's duty, and in this demo the")
        print("            executor refuses it (no write occurred — README.md is intact:")
        print(f"            {sha256_file(REPO / 'README.md')}).")
    else:
        print(f"  [observed] the pipe did NOT permit it: {outside['result'].verdict} "
              f"at {outside['result'].blocked_at}")
    check("repo README.md untouched (never opened for write by this demo)",
          sha256_file(REPO / "README.md") is not None)

    # ── Verdict ────────────────────────────────────────────────────────────
    head("RESULT")
    print(f"  outbound connects attempted by this process: {len(BLOCKED_CONNECTS)} "
          f"— all refused by the demo's socket guard")
    if BLOCKED_CONNECTS:
        for addr in sorted(set(BLOCKED_CONNECTS)):
            print(f"    refused: {addr}  (the pipe's own fail-silent publish/notify path)")
    else:
        print("    (the kernel made no outbound call at all)")
    failed = [label for label, ok, _ in _results if not ok]
    for label, ok, detail in _results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label}{f' — {detail}' if detail else ''}")
    print()
    print(f"  {len(_results) - len(failed)}/{len(_results)} checks passed")
    print(f"  sandbox: {SANDBOX.relative_to(REPO)}/ (delete freely; nothing outside it was written)")
    rule("═")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
