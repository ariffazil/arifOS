#!/usr/bin/env python3
"""f6_witness_review.py — the human-witness lane for F6 MARUAH meters.

WHY (F6 spec §5d + F6_MARUAH_CANON.md):
  The F6 producer requires witness == REVIEWED (a human reviewed the meter
  report within 7 days). Silence is never a pass: an empty or stale
  /var/lib/arifos/human_witness.jsonl keeps F6 honestly UNMEASURED. This CLI
  is the SANCTIONED PATH for that human act — it renders the current meter
  report for review and, ONLY on explicit human confirmation with the
  human's own statement, appends a witness row.

CONTRACT
  render (default)   : print the six meters + report sha256 + witness status.
                       Writes NOTHING. This is the machine-proposes half.
  --confirm          : append a witness row. REQUIRES --statement "<the
                       human's own words>" (non-empty). Refuses without it.
                       The statement is recorded verbatim — the tool never
                       composes, completes, or paraphrases it. A witness row
                       is a human act receipt; the machine only carries it.

  No pipeline, cron, or agent may invoke --confirm on a human's behalf:
  fabricating a witness row is exactly the ceremony-masquerading-as-gate
  failure class F6 exists to prevent.

SCHEMA v2 (2026-11-21):
  Measured defect this revision closes: v1 wrote `at/event/actor_class/
  report_sha256/statement/tool` and NEVER wrote the one key F3's human leg
  reads (`human_witness`), while a hand-written machine probe did carry it.
  Six authentic human acts were therefore invisible to F3 and a probe was
  counted. Evidence: HUMAN-WITNESS-LEDGER-REMEDIATION-20261121.md.

  v2 separates the act from the boolean:
    act_type     authorization | acceptance | rejection | deferral | statement
    decision     derived from act_type — never inferred from free text
    subject_*    the object the act is about (required except for `statement`)
    outcome_*    the witnessed outcome (required for `acceptance`)
    auth_*       how the human was authenticated (recorded, never assumed)
    test         explicit; a test row may never be written to the production
                 ledger and can never qualify
  `human_witness` is now DERIVED from a qualification predicate:

      not test
      and act_type in (authorization, acceptance)
      and authenticated (method + evidence reference present)
      and subject_id + subject_hash present
      and (act_type != acceptance or outcome_witness_hash present)

  A record is never called a human witness merely because it contains
  human-originated text. Missing bindings fail closed: the tool refuses to
  write rather than emit an ambiguous boolean.

TEST SEAM: ARIFOS_HUMAN_WITNESS overrides the ledger path (tests only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

WITNESS_PATH = Path("/var/lib/arifos/human_witness.jsonl")

SCHEMA_VERSION = "human_witness.v2"

ACT_TYPES = ("authorization", "acceptance", "rejection", "deferral", "statement")
POSITIVE_ACT_TYPES = ("authorization", "acceptance")
DECISION_BY_ACT = {
    "authorization": "AUTHORIZE",
    "acceptance": "ACCEPT",
    "rejection": "REJECT",
    "deferral": "DEFER",
    "statement": "NOTE",
}

AUTHENTICATED_METHODS = ("authenticated_signed", "authenticated_session")
DEFAULT_AUTH_METHOD = "unauthenticated_local_cli"
AUTH_METHODS = (DEFAULT_AUTH_METHOD,) + AUTHENTICATED_METHODS


class WitnessBindingError(ValueError):
    """Raised when a row cannot be written with truthful bindings."""


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_report() -> dict:
    """Evaluate the six meters (read-only) and fingerprint the report."""
    from arifosmcp.runtime.f6.meters import evaluate_all

    report = evaluate_all()
    canonical = json.dumps(report, sort_keys=True, default=str)
    return {
        "report": report,
        "report_sha256": hashlib.sha256(canonical.encode()).hexdigest(),
    }


def _qualification_blocker(
    *,
    act_type: str,
    test: bool,
    authenticated: bool,
    subject_id: str | None,
    subject_hash: str | None,
    outcome_witness_hash: str | None,
) -> str | None:
    """Return the reason this row cannot qualify, or None when it qualifies."""
    if test:
        return "TEST_RECORD"
    if act_type not in POSITIVE_ACT_TYPES:
        return "NON_POSITIVE_ACT"
    if not authenticated:
        return "ACTOR_AUTHENTICATION_UNVERIFIED"
    if not subject_id or not subject_hash:
        return "SUBJECT_UNBOUND"
    if act_type == "acceptance" and not outcome_witness_hash:
        return "OUTCOME_UNBOUND"
    return None


def _append_guard(
    *, qualifies: bool, target: Path, allow_nonqualifying: bool
) -> str | None:
    """Refuse to append a non-qualifying row to the PRODUCTION witness ledger.

    A row that cannot qualify still enters ``probe_human_witness``'s
    denominator (it counts every non-empty line), so writing one would move
    F3 without adding a witness. A "warning + write" is not enough: the write
    itself is the pollution. Scratch/derived ledgers are unaffected, and an
    explicit ``--allow-nonqualifying`` override exists for deliberate
    operator use (not authorised for production in this deployment).
    """
    if target == WITNESS_PATH and not qualifies and not allow_nonqualifying:
        return (
            "NON_QUALIFYING_ROW_ON_PRODUCTION_LEDGER — this row cannot qualify, "
            "and every line in the production ledger is counted in F3's "
            "denominator. Nothing was written."
        )
    return None


def build_witness_row(
    *,
    act_type: str,
    statement: str,
    actor: str,
    subject_id: str | None = None,
    subject_hash: str | None = None,
    subject_type: str = "f6_meter_report",
    scope: str | None = None,
    auth_method: str = DEFAULT_AUTH_METHOD,
    auth_evidence: str | None = None,
    outcome_witness_id: str | None = None,
    outcome_witness_hash: str | None = None,
    expires_at: str | None = None,
    supersedes: str | None = None,
    test: bool = False,
    recorded_by: str = "f6_witness_review.py",
    report: dict | None = None,
    report_sha256: str | None = None,
    now: str | None = None,
) -> dict:
    """Build one v2 witness row. Pure: no I/O, no ledger write.

    Raises WitnessBindingError when a mandatory binding for the act type is
    absent. The caller must not fall back to writing an ambiguous record.
    """
    statement = (statement or "").strip()
    if not statement:
        raise WitnessBindingError("STATEMENT_REQUIRED")
    if act_type not in ACT_TYPES:
        raise WitnessBindingError(f"UNKNOWN_ACT_TYPE: {act_type!r}")
    if auth_method not in AUTH_METHODS:
        raise WitnessBindingError(f"UNKNOWN_AUTH_METHOD: {auth_method!r}")

    # Conditional required bindings: not every field is mandatory for every act.
    if act_type != "statement" and not (subject_id and subject_hash):
        raise WitnessBindingError(
            f"SUBJECT_BINDING_REQUIRED for act_type={act_type!r} "
            "(need subject_id + subject_hash)"
        )
    if act_type == "acceptance" and not outcome_witness_hash:
        raise WitnessBindingError(
            "OUTCOME_BINDING_REQUIRED for act_type='acceptance' "
            "(need outcome_witness_hash — the act must bind to a witnessed outcome)"
        )

    authenticated = auth_method in AUTHENTICATED_METHODS and bool(auth_evidence)
    blocker = _qualification_blocker(
        act_type=act_type,
        test=bool(test),
        authenticated=authenticated,
        subject_id=subject_id,
        subject_hash=subject_hash,
        outcome_witness_hash=outcome_witness_hash,
    )
    qualifies = blocker is None
    at = now or _now_iso()
    rid_seed = f"{at}|{actor}|{act_type}|{subject_hash or ''}|{statement}"
    stamp = at.replace("-", "").replace(":", "").replace("+0000", "Z")
    record_id = f"hw2-{stamp}-{_sha256_text(rid_seed)[:8]}"

    provenance = {
        "qualification": "QUALIFIED" if qualifies else f"NOT_QUALIFIED:{blocker}",
        "object_binding": "subject_hash" if subject_hash else "NONE",
        "outcome_binding": "outcome_witness_hash" if outcome_witness_hash else "NONE",
        "auth": {
            "method": auth_method,
            "evidence_present": bool(auth_evidence),
            "authenticated": authenticated,
        },
        "statement_source": "human_verbatim",
        "tool_version": "f6_witness_review.py/v2",
    }

    row: dict = {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "recorded_at": at,
        "effective_at": at,
        # Compatibility keys: meters._witness_status reads `at`; the F6 report
        # renderer and legacy readers read event/actor_class/report_sha256.
        "at": at,
        "event": "f6_meter_review",
        "actor_id": actor,
        "actor_class": "HUMAN",
        "actor_authentication": {
            "method": auth_method,
            "evidence": auth_evidence,
            "authenticated": authenticated,
        },
        "act_type": act_type,
        "subject_type": subject_type,
        "subject_id": subject_id,
        "subject_hash": subject_hash,
        "scope": scope,
        "outcome_witness_id": outcome_witness_id,
        "outcome_witness_hash": outcome_witness_hash,
        "decision": DECISION_BY_ACT[act_type],
        "statement": statement,
        "recorded_by": recorded_by,
        "recording_method": "f6_witness_review.py --confirm (v2)",
        "provenance": provenance,
        "test": bool(test),
        "expires_at": expires_at,
        "supersedes": supersedes,
        "tool": "scripts/f6_witness_review.py",
        "human_witness": qualifies,
    }
    if report is not None:
        row["meters"] = {
            str(m.get("meter_id")): {
                "result": m.get("result"),
                "measurement": m.get("measurement"),
            }
            for m in report.get("meters", [])
        }
        row["f6_overall_at_review"] = report.get("f6_overall")
    if report_sha256:
        row["report_sha256"] = report_sha256

    row["source_record_hash"] = _sha256_text(
        json.dumps(row, sort_keys=True, default=str)
    )
    return row


def append_witness_row(row: dict, witness_path: Path | None = None) -> Path:
    """Append one row as a single JSONL line. Returns the path written."""
    target = witness_path or Path(
        __import__("os").environ.get("ARIFOS_HUMAN_WITNESS", str(WITNESS_PATH))
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return target


def confirm(
    statement: str,
    actor: str = "arif",
    *,
    act_type: str = "statement",
    subject_id: str | None = None,
    subject_hash: str | None = None,
    subject_type: str = "f6_meter_report",
    scope: str | None = None,
    auth_method: str = DEFAULT_AUTH_METHOD,
    auth_evidence: str | None = None,
    outcome_witness_id: str | None = None,
    outcome_witness_hash: str | None = None,
    expires_at: str | None = None,
    supersedes: str | None = None,
    test: bool = False,
    allow_nonqualifying: bool = False,
) -> int:
    statement = (statement or "").strip()
    if not statement:
        print(
            "REFUSED: --confirm requires --statement with the human's own words. "
            "An empty or machine-composed statement is not a witness act.",
            file=sys.stderr,
        )
        return 2

    import os

    target = Path(os.environ.get("ARIFOS_HUMAN_WITNESS", str(WITNESS_PATH)))
    if test and target == WITNESS_PATH:
        print(
            "REFUSED: --test may not append to the production witness ledger. "
            "Set ARIFOS_HUMAN_WITNESS to a scratch path for test rows.",
            file=sys.stderr,
        )
        return 2

    # Phase 2 guard: decide eligibility BEFORE any report work or file open.
    # A non-qualifying row would still be counted in F3's denominator.
    _authenticated = auth_method in AUTHENTICATED_METHODS and bool(auth_evidence)
    _blocker = _qualification_blocker(
        act_type=act_type,
        test=bool(test),
        authenticated=_authenticated,
        subject_id=subject_id,
        subject_hash=subject_hash,
        outcome_witness_hash=outcome_witness_hash,
    )
    _refusal = _append_guard(
        qualifies=_blocker is None,
        target=target,
        allow_nonqualifying=allow_nonqualifying,
    )
    if _refusal:
        print(f"REFUSED: {_refusal}", file=sys.stderr)
        print(
            "  To record a qualifying act: --act-type authorization|acceptance "
            "--subject-id <id> --subject-hash <sha256> "
            "--auth-method authenticated_session --auth-evidence <ref> "
            "(acceptance also needs --bind-report-as-outcome).",
            file=sys.stderr,
        )
        return 2

    bundle = build_report()
    report = bundle["report"]
    try:
        row = build_witness_row(
            act_type=act_type,
            statement=statement,
            actor=actor,
            subject_id=subject_id,
            subject_hash=subject_hash,
            subject_type=subject_type,
            scope=scope,
            auth_method=auth_method,
            auth_evidence=auth_evidence,
            outcome_witness_id=outcome_witness_id,
            outcome_witness_hash=outcome_witness_hash,
            expires_at=expires_at,
            supersedes=supersedes,
            test=test,
            report=report,
            report_sha256=bundle["report_sha256"],
        )
    except WitnessBindingError as exc:
        print(
            f"REFUSED: {exc}. A row with missing bindings would be an ambiguous "
            "record; nothing was written.",
            file=sys.stderr,
        )
        return 2

    if allow_nonqualifying and not row["human_witness"]:
        # Explicit operator override: make the deviation visible on the row.
        row["provenance"]["non_qualifying_override"] = True

    target = append_witness_row(row)
    print(f"WITNESS_RECORDED {target} at={row['recorded_at']} actor={actor}")
    print(f"report_sha256={row['report_sha256']}")
    print(
        f"act_type={row['act_type']} decision={row['decision']} "
        f"qualifies={row['human_witness']} "
        f"({row['provenance']['qualification']})"
    )
    if not row["human_witness"]:
        print(
            "NOTE: this row is recorded as evidence but does NOT qualify as a "
            "positive human witness. Bind subject/outcome and authenticate the "
            "actor to qualify."
        )
    return 0


def render() -> int:
    bundle = build_report()
    report = bundle["report"]
    print("F6 MARUAH — six system-behavior meters (machine proposes; human confirms)")
    print(f"report sha256: {bundle['report_sha256']}")
    print(f"generated_at : {report.get('generated_at')}")
    print(f"f6_overall   : {report.get('f6_overall')}  floor: {report.get('f6_floor_status')}")
    print(f"witness      : {report.get('witness_states')}")
    print("-" * 78)
    for m in report.get("meters", []):
        print(
            f"{m.get('meter_id'):<28} result={m.get('result'):<14} "
            f"measurement={m.get('measurement'):<11} witness={m.get('witness')}"
        )
        reason = str(m.get("result_reason") or "")
        if reason:
            print(f"    reason: {reason[:160]}")
    print("-" * 78)
    print("To witness: a HUMAN runs this tool, reads the report above, and then:")
    print(
        "  f6_witness_review.py --confirm --act-type acceptance "
        "--statement '<your own words>' --bind-report-as-outcome "
        "[--auth-method authenticated_session --auth-evidence <ref>]"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--confirm", action="store_true", help="record a human witness act")
    ap.add_argument(
        "--statement", default="", help="the human's own words (required with --confirm)"
    )
    ap.add_argument("--actor", default="arif", help="human actor id (default: arif)")
    ap.add_argument(
        "--act-type",
        default="statement",
        choices=list(ACT_TYPES),
        help="what the human is doing (default: statement — never qualifies alone)",
    )
    ap.add_argument("--subject-id", default=None, help="ID of the object the act is about")
    ap.add_argument("--subject-hash", default=None, help="sha256 of that object")
    ap.add_argument("--subject-type", default="f6_meter_report")
    ap.add_argument("--scope", default=None)
    ap.add_argument(
        "--bind-report-as-outcome",
        action="store_true",
        help="for act_type=acceptance: bind the rendered meter report as the outcome witness",
    )
    ap.add_argument(
        "--auth-method",
        default=DEFAULT_AUTH_METHOD,
        choices=list(AUTH_METHODS),
        help="how the human was authenticated (default: none — row does not qualify)",
    )
    ap.add_argument("--auth-evidence", default=None, help="reference to the auth proof")
    ap.add_argument(
        "--expires-at", default=None, help="explicit expiry (ISO); omitted = none declared"
    )
    ap.add_argument("--supersedes", default=None, help="record_id this row supersedes")
    ap.add_argument("--test", action="store_true", help="explicit test row (never qualifies)")
    ap.add_argument(
        "--allow-nonqualifying",
        action="store_true",
        help="operator override: permit a non-qualifying row on the PRODUCTION ledger "
        "(not authorised for production in this deployment; the row is stamped)",
    )
    a = ap.parse_args(argv)
    if not a.confirm:
        return render()

    subject_id = a.subject_id
    subject_hash = a.subject_hash
    outcome_id = None
    outcome_hash = None
    if a.act_type == "acceptance" and a.bind_report_as_outcome:
        bundle = build_report()
        subject_hash = subject_hash or bundle["report_sha256"]
        subject_id = subject_id or f"f6_meter_report:{bundle['report_sha256'][:8]}"
        outcome_id = f"f6_meter_report:{bundle['report_sha256'][:8]}"
        outcome_hash = bundle["report_sha256"]
    return confirm(
        a.statement,
        a.actor,
        act_type=a.act_type,
        subject_id=subject_id,
        subject_hash=subject_hash,
        subject_type=a.subject_type,
        scope=a.scope,
        auth_method=a.auth_method,
        auth_evidence=a.auth_evidence,
        outcome_witness_id=outcome_id,
        outcome_witness_hash=outcome_hash,
        expires_at=a.expires_at,
        supersedes=a.supersedes,
        test=a.test,
        allow_nonqualifying=a.allow_nonqualifying,
    )


if __name__ == "__main__":
    raise SystemExit(main())
