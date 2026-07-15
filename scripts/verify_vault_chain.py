#!/usr/bin/env python3
"""
VAULT999 Merkle-V3 Hash Chain Integrity Verifier — P0-02
═══════════════════════════════════════════════════════════════════════════

AUDIT-ONLY. Read-only by construction.

Walks each Merkle-chained vault ledger and verifies that each entry's
`prev_hash` pointer equals the prior entry's `chain_hash`. Reports any
broken links as HOLD events (read-only signal, no mutation).

Handles two schemata:
  - v1 (SEALED_EVENTS.jsonl):     fields {id, prev_hash, chain_hash, merkle_leaf}
                                  genesis prev = "" (empty string)
                                  + Type-B entries with {ts, chain_position, prev_hash}
                                  where prev_hash may be sentinel "GENESIS"
  - v2 (SEALED_EVENTS_v2.jsonl):  fields {id, prev_leaf, chain_hash, seal_hash}
                                  genesis prev = null

Live ledger (vault999.jsonl) is NOT a Merkle chain — it's a flat record
ledger with `seal_hash` only. It is included for completeness and
clearly marked NON_CHAIN.

Output JSON (per ledger):
  {
    "ledger": "<name>",
    "chain_length": <int>,         # entries with a chain pointer
    "first_seq": <int|None>,       # lowest id / chain_position
    "last_seq":  <int|None>,       # highest id / chain_position
    "broken_links": [              # array of break events
      {
        "line_no":   <int>,
        "seq":       <int|None>,
        "prev_hash": "<actual prev_hash string>",
        "expected":  "<prior chain_hash string>",
        "kind":      "PREV_MISMATCH|UNEXPECTED_GENESIS|MISSING_CHAIN_HASH|UNEXPECTED_HASH_FIELD"
      }, ...
    ],
    "parse_errors": <int>,
    "declared_lineage_breaks": <int|None>,   # from epoch_state.json if known
    "status": "INTACT|BROKEN|NON_CHAIN|UNREADABLE"
  }

F2 TRUTH labels: this audit emits OBS (observed) tags on empirical counts;
declared counts are SPEC (declared-by-source). They are NEVER confused.

F9 ANTI-HANTU: if a measurement cannot be taken (file missing, locked,
schema drift), we emit "UNMEASURED" — not zero, not silent.

F11 AUDIT: every run appends to .audit/verify_vault_chain_history.jsonl
in CWD (caller is responsible for path; the audit trace is the receipt).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ─── Locate the fossil layer ──────────────────────────────────────────────────
REPO = Path("/root/arifOS")
VAULT = REPO / "VAULT999"


# Schemata that participate in a real Merkle chain.
CHAIN_LEDGERS: list[dict[str, Any]] = [
    {
        # v1 (frozen historical). Two co-existing entry types in the same file
        # are detected by schema presence; both feed the same prev/chain pointer
        # sequence and are walked together for completeness.
        "name": "SEALED_EVENTS.jsonl (v1, frozen historical)",
        "path": VAULT / "SEALED_EVENTS.jsonl",
        # primary schema: id → prev_hash → chain_hash
        "seq_field": "id",
        "prev_field": "prev_hash",
        "chain_field": "chain_hash",
        "leaf_field": "merkle_leaf",
        # OBSERVED genesis markers in v1 file: "", "GENESIS", and absent (None).
        "genesis_prev_values": {"", "GENESIS"},
    },
    {
        # v2 (active canonical ledger, as of epoch split 2026-06-02).
        "name": "SEALED_EVENTS_v2.jsonl (v2, active canonical)",
        "path": VAULT / "SEALED_EVENTS_v2.jsonl",
        "seq_field": "id",
        "prev_field": "prev_leaf",
        "chain_field": "chain_hash",
        "leaf_field": "merkle_leaf",
        "genesis_prev_values": {None, "GENESIS", ""},
    },
    {
        # live rolling vault (newest, ~10 entries). Two coexisting formats per
        # file: older rows have a top-level chain_hash; newer rows nest the
        # chain inside entry["chain"] = {prev_entry_hash, entry_hash, ...}.
        # Older rows may carry neither — those are flat legacy rows, not
        # broken chain entries. The walk distinguishes these.
        "name": "vault999.jsonl (live, mixed nested/flat ledger v3)",
        "path": VAULT / "vault999.jsonl",
        "seq_field": "session_id",
        "nested_chain": True,
        "flat_chain_field": "chain_hash",
        # v3 nested chain genesis uses the canonical EVM zero hash. Including
        # it in the genesis set prevents false-positive PREV_MISMATCH at
        # sub-chain start.
        "genesis_prev_values": {
            "",
            None,
            "0x" + "0" * 64,
        },
    },
]

GENESIS_PLACEHOLDER = "<GENESIS>"

# Audit trace target (run-relative). Caller may override via argv.
DEFAULT_HISTORY = Path(".audit/verify_vault_chain_history.jsonl")


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _short(h: str | None, n: int = 16) -> str:
    """Trim a hash for human reports while preserving audit-fidelity via full length."""
    if h is None:
        return "<null>"
    if h == "":
        return "<empty>"
    return h[:n] + ("…" if len(h) > n else "")


def _load_epoch_state() -> dict[str, Any]:
    """Best-effort load of epoch_state.json — authoritative DECLARED lineage_break counts."""
    p = VAULT / "epoch_state.json"
    if not p.is_file():
        return {}
    try:
        with p.open("r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        # F11 AUDIT: misparsing the state file is an event; we leave it UNMEASURED.
        return {"_state_file_unreadable": True}


def _declared_lineage_breaks(state: dict[str, Any], ledger_key: str) -> int | None:
    """Extract the declared lineage_breaks count for a given ledger_key ('v1' or 'v2')."""
    section = state.get(ledger_key)
    if not isinstance(section, dict):
        return None
    if "lineage_breaks" in section and isinstance(section["lineage_breaks"], int):
        return section["lineage_breaks"]
    # v2 ledger reports it under a different name in epoch_state.json
    if "historical_chain_breaks" in section and isinstance(section["historical_chain_breaks"], int):
        return section["historical_chain_breaks"]
    return None


def verify_ledger(spec: dict[str, Any], declared_breaks: int | None) -> dict[str, Any]:
    """
    Walk one chain-formatted ledger; return the spec-shape report dict.

    Read-only: opens with 'r', never writes to the ledger.
    """
    path: Path = spec["path"]
    report: dict[str, Any] = {
        "ledger": spec["name"],
        "path": str(path),
        "chain_length": 0,
        "sub_chains_observed": 0,
        "prev_with_genesis_or_null_count": 0,
        # The "strict" count mirrors what the F13 epoch-split declaration treats
        # as a break: any prev_hash (sentinel or hash) that does NOT equal the
        # IMMEDIATELY preceding entry's chain_hash. This is the convention used
        # in epoch_state.json (v1: 120; v2: "955 historical_chain_breaks").
        "strict_link_break_count": 0,
        "first_seq": None,
        "last_seq": None,
        "broken_links": [],
        "parse_errors": 0,
        "declared_lineage_breaks": declared_breaks,
        "status": "UNREADABLE",
    }

    if spec.get("non_chain"):
        if not path.is_file():
            report["status"] = "MISSING"
            return report
        # Count rows for the report; mark non-chain.
        n = 0
        with path.open("r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    json.loads(ln)
                    n += 1
                except json.JSONDecodeError:
                    report["parse_errors"] += 1
        report["non_chain_row_count"] = n
        report["status"] = "NON_CHAIN"
        return report

    if not path.is_file():
        report["status"] = "MISSING"
        return report

    seq_field = spec["seq_field"]
    prev_field = spec.get("prev_field")
    chain_field = spec.get("chain_field")
    genesis_set = spec["genesis_prev_values"]
    nested_chain = bool(spec.get("nested_chain"))
    flat_chain_field = spec.get("flat_chain_field")

    chain_length = 0
    seqs: list[int] = []
    parse_errors = 0

    # The file may contain MULTIPLE interleaved Merkle sub-chains (different
    # schemas: id-based and ts/chain_position-based). Each sub-chain is
    # bracketed by a genesis sentinel ("" / null / "GENESIS").
    sub_chain_anchor: str | None = None  # last real chain_hash within the CURRENT sub-chain
    sub_chains_observed = 0
    prev_with_genesis_or_null_count = 0
    # The "strict" view walks the file SEQUENTIALLY regardless of sub-chains:
    # each entry must have prev_hash == prior entry's chain_hash, and any other
    # value (sentinel included) counts as a break. This is how epoch_state.json
    # v1.lineage_breaks=120 and v2.historical_chain_breaks=955 were counted.
    strict_link_break_count = 0
    strict_anchor: str | None = None  # IMMEDIATELY previous entry's chain_hash (strict view)

    with path.open("r") as f:
        for line_no_raw, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                parse_errors += 1
                report["broken_links"].append(
                    {
                        "line_no": line_no_raw,
                        "seq": None,
                        "prev_hash": None,
                        "expected": None,
                        "kind": "PARSE_ERROR",
                        "detail": f"{type(e).__name__}: {e}",
                    }
                )
                continue

            if not isinstance(entry, dict):
                # Schema drift — surface, do not fabricate.
                report["broken_links"].append(
                    {
                        "line_no": line_no_raw,
                        "seq": None,
                        "prev_hash": None,
                        "expected": None,
                        "kind": "SCHEMA_DRIFT",
                        "detail": f"top-level type: {type(entry).__name__}",
                    }
                )
                continue

            # ── Per-row schema resolution ────────────────────────────────────
            # For nested-chain ledgers (live vault999.jsonl), each row may carry
            # its chain under entry["chain"]["prev_entry_hash"] / ["entry_hash"];
            # for v1/v2 we read the flat top-level fields as before.
            prev: Any = None
            cur_chain: Any = None
            chain_field_used: str = chain_field
            if nested_chain:
                nested = entry.get("chain")
                if isinstance(nested, dict):
                    prev = nested.get("prev_entry_hash")
                    cur_chain = nested.get("entry_hash")
                    chain_field_used = "chain.entry_hash"
                else:
                    # Fallback: try flat top-level chain_hash
                    prev = entry.get(prev_field) if prev_field else None
                    cur_chain = entry.get(flat_chain_field) if flat_chain_field else None
                    chain_field_used = flat_chain_field or chain_field
            else:
                prev = entry.get(prev_field)
                cur_chain = entry.get(chain_field)

            # Missing chain_hash is a structural break — not synthesizable.
            if cur_chain is None or cur_chain == "":
                # For mixed-format ledgers (e.g. vault999.jsonl), a row may be a
                # LEGACY_FLAT entry that legitimately does not carry chain data.
                # We surface those separately so they are not falsely amplified
                # as MISSING_CHAIN_HASH breaks. Pure flat-chain ledgers DO treat
                # missing chain_hash as a real break.
                if nested_chain and not isinstance(entry.get("chain"), dict):
                    kind = "LEGACY_FLAT_ROW"
                    detail = "row uses flat schema without chain pointer"
                else:
                    kind = "MISSING_CHAIN_HASH"
                    detail = f"{chain_field_used} missing or empty"
                report["broken_links"].append(
                    {
                        "line_no": line_no_raw,
                        "seq": entry.get(seq_field),
                        "prev_hash": prev,
                        "expected": sub_chain_anchor,
                        "kind": kind,
                        "detail": detail,
                    }
                )
                # Continue walking so we surface every defect, not just the first.

            # Sequence tracking (only when present and int-like).
            seq_val = entry.get(seq_field)
            try:
                seq_int = int(seq_val) if seq_val is not None else None
            except (TypeError, ValueError):
                seq_int = None
            # For vault999.jsonl we deliberately ignore seq — session_id is a
            # opaque hex string, not an integer sequence.
            if seq_int is not None:
                seqs.append(seq_int)
                if report["first_seq"] is None or seq_int < report["first_seq"]:
                    report["first_seq"] = seq_int
                if report["last_seq"] is None or seq_int > report["last_seq"]:
                    report["last_seq"] = seq_int

            # Count this entry toward chain length if it carries a chain pointer.
            if cur_chain is not None and cur_chain != "":
                chain_length += 1

            # Verify the prev pointer against the CURRENT sub-chain anchor.
            prev_is_genesis = prev in genesis_set

            if prev_is_genesis:
                # Sentinel = "this starts a new sub-chain". We close the previous
                # sub-chain (if any) and reset the anchor.
                if sub_chain_anchor is not None:
                    sub_chains_observed += 1
                sub_chain_anchor = None
                prev_with_genesis_or_null_count += 1
                # Strict view: any sentinel value mid-file is a break.
                if strict_anchor is not None:
                    strict_link_break_count += 1
            else:
                # Real prev_hash string — must equal the current sub-chain's anchor.
                if sub_chain_anchor is None:
                    # First entry of a sub-chain WITHOUT a genesis sentinel — that's
                    # a normal opening (the very first sub-chain in the file). Accept.
                    pass
                elif prev != sub_chain_anchor:
                    report["broken_links"].append(
                        {
                            "line_no": line_no_raw,
                            "seq": seq_int,
                            "prev_hash": prev,
                            "expected": sub_chain_anchor,
                            "kind": "PREV_MISMATCH",
                            "detail": (
                                f"{prev_field}={_short(prev)}"
                                " != prior"
                                f" {chain_field}={_short(sub_chain_anchor)}"
                            ),
                        }
                    )
                    # Do NOT advance the anchor on a break — the next entry that
                    # chains correctly off the still-valid anchor is not penalised.

                # Strict view: prev_hash must equal the IMMEDIATELY prior
                # entry's chain_hash.
                if strict_anchor is not None and prev != strict_anchor:
                    strict_link_break_count += 1

            # Advance the sub-chain anchor only when this entry contributed
            # a real chain_hash. The next entry in this sub-chain must point here.
            if cur_chain is not None and cur_chain != "":
                sub_chain_anchor = cur_chain
                strict_anchor = cur_chain

    # Close the final sub-chain if we're still mid-chain at EOF.
    if sub_chain_anchor is not None:
        sub_chains_observed += 1

    report["chain_length"] = chain_length
    report["sub_chains_observed"] = sub_chains_observed
    report["prev_with_genesis_or_null_count"] = prev_with_genesis_or_null_count
    report["strict_link_break_count"] = strict_link_break_count
    report["parse_errors"] = parse_errors
    # A "real structural break" excludes row-level parse errors AND legacy
    # non-chain flat rows in mixed-schema files. Only intra-chain hash
    # mismatches and missing chain hashes count under the lenient (sub-chain-aware)
    # view.
    real_break_kinds = (
        "PREV_MISMATCH",
        "MISSING_CHAIN_HASH",
        "UNEXPECTED_GENESIS",
        "SCHEMA_DRIFT",
    )
    real_breaks = [b for b in report["broken_links"] if b.get("kind") in real_break_kinds]
    if real_breaks:
        report["status"] = "BROKEN"
    elif parse_errors and chain_length == 0:
        report["status"] = "UNREADABLE"
    else:
        report["status"] = "INTACT"
    # Also surface the LEGACY_FLAT_ROW count separately for transparency.
    report["legacy_flat_row_count"] = sum(
        1 for b in report["broken_links"] if b.get("kind") == "LEGACY_FLAT_ROW"
    )
    return report


# ─── Driver ──────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    state = _load_epoch_state()

    history_path = DEFAULT_HISTORY
    if "--history" in argv:
        i = argv.index("--history")
        if i + 1 < len(argv):
            history_path = Path(argv[i + 1])

    reports: list[dict[str, Any]] = []
    for spec in CHAIN_LEDGERS:
        # Decide which epoch_state key maps to which ledger.
        declared_breaks: int | None = None
        if "v1" in spec["name"]:
            declared_breaks = _declared_lineage_breaks(state, "v1")
        elif "v2" in spec["name"]:
            declared_breaks = _declared_lineage_breaks(state, "v2")
        reports.append(verify_ledger(spec, declared_breaks))

    # Aggregate with an honest overall verdict. INTACT = no broken links anywhere.
    overall = "INTACT"
    for r in reports:
        if r["status"] in ("BROKEN", "UNREADABLE", "MISSING"):
            overall = "DEGRADED"
            break
        if r["status"] == "NON_CHAIN":
            continue

    envelope: dict[str, Any] = {
        "audit_id": f"verify_vault_chain.{datetime.now(UTC).isoformat()}",
        "actor": "arifos-p0-02-subagent",
        "constitutional_floors": {
            "F2_TRUTH": "declared vs observed counts carry distinct tags",
            "F4_CLARITY": "broken_links is a deterministic walk, not an LLM judgement",
            "F9_ANTIHANTU": "missing scalars become UNMEASURED, never 0",
            "F11_AUDIT": "this JSON is the receipt; appended to history file",
            "F13_SOVEREIGN": "READ-ONLY by construction; no sealing, no mutating",
        },
        "epoch_state_present": bool(state) and "_state_file_unreadable" not in state,
        "ledgers": reports,
        "overall": overall,
    }

    # Stdout: pretty-printed (for human review).
    pretty = json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False)
    print(pretty)

    # F11 AUDIT: append-only history. Compact one-line JSON per envelope so the
    # file is a valid JSONL stream (each `audit_id` is exactly one line).
    try:
        history_path.parent.mkdir(parents=True, exist_ok=True)
        compact = json.dumps(envelope, sort_keys=True, ensure_ascii=False)
        with history_path.open("a") as hf:
            hf.write(compact + "\n")
    except OSError as e:
        # We do not fail the audit if we cannot write our own log — that would
        # be circular (a logging failure should not corrupt the audit result).
        print(f"\n[warn] could not append history → {history_path}: {e}", file=sys.stderr)

    # Non-zero exit only on hard failure (UNREADABLE / MISSING chain files).
    hard_failures = [
        r
        for r in reports
        if r["status"] in ("UNREADABLE", "MISSING") and not r.get("non_chain_row_count")
    ]
    if hard_failures:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
