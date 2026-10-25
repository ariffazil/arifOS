#!/usr/bin/env python3
"""test_contract_gate.py — positive-control-first test of the mode contract resolver.

Arif's rule (2026-10-20): "A system that refuses everything scores 100% on
refusal tests while being unable to work. Positive control is mandatory."

So this file tests in this order:
  POSITIVE CONTROL  a permitted action MUST be permitted, with the right class
  NEGATIVE          each refusal MUST cite the exact reason
  DOWNGRADE         asking for less than the contract allows MUST fail
  UNKNOWN           a mutating request with no contract MUST fail

Run: python3 -I scripts/test_contract_gate.py   (exit 0 = all pass)
"""

from __future__ import annotations

import sys

REPO = "/root/arifOS"
sys.path.insert(0, REPO)

from arifosmcp.runtime.mode_contract_gate import (  # noqa: E402
    ContractUnavailable,
    contract_summary,
    resolve_contract_class,
)

PASS, FAIL = "PASS", "FAIL"
rows: list[tuple[str, str, str]] = []


def check(
    kind: str,
    label: str,
    tool: str,
    mode: str,
    requested: str,
    expect: str | None,
    expect_reason: str | None = None,
    manifest_class: str | None = None,
) -> None:
    """expect=None means 'must raise ContractUnavailable'."""
    try:
        got, reason = resolve_contract_class(tool, mode, requested, manifest_class=manifest_class)
    except ContractUnavailable as e:
        if expect is None:
            ok = expect_reason is None or expect_reason in str(e)
            rows.append((kind, PASS if ok else FAIL, f"{label}: refused — {str(e)[:90]}"))
        else:
            rows.append((kind, FAIL, f"{label}: refused but expected {expect} — {e}"))
        return
    if expect is None:
        rows.append((kind, FAIL, f"{label}: allowed as {got}, expected refusal"))
        return
    ok = got == expect
    rows.append(
        (
            kind,
            PASS if ok else FAIL,
            f"{label}: {requested} → {got}" + ("" if ok else f" (expected {expect})"),
        )
    )


def main() -> int:
    # ── POSITIVE CONTROLS: these must be ALLOWED, or nothing works ──────────
    check("positive", "memory.recall is a read", "arif_memory", "recall", "OBSERVE", "OBSERVE")
    check("positive", "forge.dry_run is a read", "arif_forge", "dry_run", "OBSERVE", "OBSERVE")
    # contract says OBSERVE, gate manifest says ANALYZE → stricter (ANALYZE) wins
    check(
        "positive",
        "think.axioms, two sources disagree",
        "arif_think",
        "axioms",
        "ANALYZE",
        "ANALYZE",
        manifest_class="ANALYZE",
    )
    check("positive", "seal.verify is a read", "arif_seal", "verify", "OBSERVE", "OBSERVE")
    check(
        "positive",
        "memory.remember is reversible write",
        "arif_memory",
        "remember",
        "MUTATE",
        "MUTATE",
    )
    check(
        "positive",
        "caller may ask MORE conservative than contract",
        "arif_memory",
        "recall",
        "IRREVERSIBLE",
        "OBSERVE",
    )

    # ── NEGATIVE: exact reasons, not just refusal ──────────────────────────
    check(
        "negative",
        "memory.forget is irreversible",
        "arif_memory",
        "forget",
        "IRREVERSIBLE",
        "IRREVERSIBLE",
    )
    check(
        "negative",
        "memory.promote is irreversible",
        "arif_memory",
        "promote",
        "IRREVERSIBLE",
        "IRREVERSIBLE",
    )
    check(
        "negative",
        "forge.commit is irreversible",
        "arif_forge",
        "commit",
        "IRREVERSIBLE",
        "IRREVERSIBLE",
    )

    # ── DOWNGRADE: manifest said OBSERVE, contract says otherwise ──────────
    # This is the defect this module closes: the old manifest classified
    # arif_memory as OBSERVE globally, so forget inherited a read's class.
    check(
        "downgrade",
        "forget claimed as OBSERVE",
        "arif_memory",
        "forget",
        "OBSERVE",
        None,
        "downgrade refused",
    )
    check(
        "downgrade",
        "commit claimed as MUTATE",
        "arif_forge",
        "commit",
        "MUTATE",
        None,
        "downgrade refused",
    )

    # ── UNKNOWN: no contract + mutating request must fail closed ───────────
    # arif_fetch has no contract at all (tool absent from mode_contracts.json)
    check(
        "unknown",
        "tool with no contract, mutating request",
        "arif_fetch",
        "archive",
        "MUTATE",
        None,
        "NO_CONTRACT",
    )
    check(
        "unknown",
        "undeclared mode, irreversible request",
        "arif_route",
        "relay",
        "IRREVERSIBLE",
        None,
        "NO_CONTRACT",
    )
    # ...but an unknown mode with a READ request is still allowed (no side effect)
    check(
        "unknown",
        "tool with no contract, read request",
        "arif_fetch",
        "fetch",
        "OBSERVE",
        "OBSERVE",
    )
    # arif_report DOES declare file=MATERIAL — a write must resolve, not be refused
    check("positive", "report.file is a declared write", "arif_report", "file", "MUTATE", "MUTATE")
    # 2026-10-25: the WIRE write mode is "report"; "file" is a deprecated alias.
    # Before this fix the live write resolved OBSERVE while the dead "file" key
    # escalated — the test below pinned the dead name and passed while the real
    # append was admitted as a read (reproduced live 2026-10-25).
    check(
        "positive",
        "report.report is the declared wire write",
        "arif_report",
        "report",
        "MUTATE",
        "MUTATE",
    )
    check(
        "positive",
        "report.flush pushes to the human = write",
        "arif_report",
        "flush",
        "MUTATE",
        "MUTATE",
    )

    # ── GATE INTEGRATION: the deployed classifier must escalate too ────────
    # These call the real resolve_action_class_for_mode, not the resolver.
    # Before 2026-10-20 21:46 this returned OBSERVE for every row below.
    from arifosmcp.runtime.pre_execution_gate import (
        ActionClass,
        resolve_action_class_for_mode,
    )

    gate_cases = [
        ("memory.forget claimed OBSERVE", "arif_memory", "forget", "OBSERVE", "IRREVERSIBLE"),
        ("memory.promote claimed OBSERVE", "arif_memory", "promote", "OBSERVE", "IRREVERSIBLE"),
        (
            "forge.commit claimed IRREVERSIBLE",
            "arif_forge",
            "commit",
            "IRREVERSIBLE",
            "IRREVERSIBLE",
        ),
        ("forge.commit claimed OBSERVE", "arif_forge", "commit", "OBSERVE", "IRREVERSIBLE"),
        ("report.file claimed OBSERVE", "arif_report", "file", "OBSERVE", "MUTATE"),
        # 2026-10-25 wire-name pins: the real write mode must escalate too.
        ("report.report claimed OBSERVE", "arif_report", "report", "OBSERVE", "MUTATE"),
        ("report.flush claimed OBSERVE", "arif_report", "flush", "OBSERVE", "MUTATE"),
        ("report.inbox stays a read", "arif_report", "inbox", "OBSERVE", "OBSERVE"),
        ("route.metabolize claimed OBSERVE", "arif_route", "metabolize", "OBSERVE", "ANALYZE"),
        # positive controls: escalation must not over-reach
        ("memory.recall stays a read", "arif_memory", "recall", "OBSERVE", "OBSERVE"),
        ("forge.dry_run stays a read", "arif_forge", "dry_run", "OBSERVE", "OBSERVE"),
        ("think.axioms stays a read", "arif_think", "axioms", "OBSERVE", "OBSERVE"),
        ("seal.verify stays a read", "arif_seal", "verify", "OBSERVE", "OBSERVE"),
    ]
    for label, tool, mode, claim, expect in gate_cases:
        try:
            got = resolve_action_class_for_mode(tool, mode, ActionClass[claim]).name
            ok = got == expect
            rows.append(
                (
                    "gate",
                    PASS if ok else FAIL,
                    f"{label}: {claim} → {got}" + ("" if ok else f" (expected {expect})"),
                )
            )
        except Exception as e:
            rows.append(("gate", FAIL, f"{label}: raised {type(e).__name__}: {e}"))

    # ── contract summary is readable (receipt line for future wiring) ──────
    s = contract_summary("arif_memory", "forget")
    rows.append(
        (
            "summary",
            PASS if s and s["recovery"] == "permanent" else FAIL,
            f"memory.forget summary: {s}",
        )
    )

    for kind, status, detail in rows:
        print(f"{status:5} {kind:10} {detail}")
    fails = sum(1 for _, s, _ in rows if s == FAIL)
    print(f"\n{len(rows)} checks · {len(rows) - fails} pass · {fails} fail")
    print("scope: contract RESOLUTION only. Grant expiry/revocation/action-binding")
    print("       are NOT tested here and remain UNMEASURED (need SOVEREIGN grant).")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
