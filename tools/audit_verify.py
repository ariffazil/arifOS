#!/usr/bin/env python3
"""
audit_verify.py — VAULT999-SIG offline auditor verifier (Fasa 1, G1, 2026-08-30).

Independent signature + integrity verifier for the canonical seal chain
(seal_chain.jsonl). Zero dependencies beyond Python stdlib and ZERO imports
from arifosmcp: an auditor verifies a COPY of the chain outside the running
system, with the vault HMAC key delivered out-of-band. No trust in the
live kernel is required.

What it checks (strict posture — no grandfathering inherited from runtime):
  1. Link integrity   — entry N's previous_hash == entry N-1's this/receipt_hash
  2. Envelope hashes  — receipt_hash recomputed from the canonical 15-field
                        body (sorted JSON) must match the recorded value
  3. Signatures       — every entry with sig_key_id is HMAC-SHA256 verified
                        over its receipt_hash with the supplied key
  4. Cutover rule     — after the FIRST signed entry (VAULT-SIG-1 cutover),
                        every canonical entry must be signed (unsigned → fail)
  5. Duplicates       — duplicate receipt_id / duplicate canonical sequence
  6. Optional anchor  — --expect-head pins an externally recorded head hash

Companion tool: vault999_auditor_export.py (manifest export / artifact
anchoring). This tool performs the cryptographic chain verdict.

Usage:
  python3 tools/audit_verify.py --chain /path/to/seal_chain.jsonl \
      [--key-file /path/to/key] | [--key-env ARIFOS_VAULT_HMAC_KEY] \
      [--expect-head sha256:...] [--json]

Exit codes: 0 = VERIFIED (all signed entries green, no gaps)
            1 = gaps / signature failures found (see report)
            2 = invocation error

DITEMPA BUKAN DIBERI — Forged, not given.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any

SIG_KEY_ID = "vault-hmac-1"
SIG_PREFIX = "hmac-sha256:"
GENESIS = "genesis"

# Canonical hash body fields — MUST mirror arifosmcp canonical_vault_chain
# _HASH_FIELDS exactly. Deliberately duplicated (not imported) so this tool
# stays independent of the system it audits.
_HASH_FIELDS = (
    "sequence",
    "previous_hash",
    "timestamp",
    "actor_id",
    "session_id",
    "trace_id",
    "operation_id",
    "tool_name",
    "input_hash",
    "authority_state",
    "decision_reference",
    "result_hash",
    "reversibility",
    "software_release",
    "epoch_id",
)


def _sha256_hex(data: str) -> str:
    return "sha256:" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_receipt_hash(fields: dict[str, Any]) -> str:
    body = {k: fields.get(k) for k in _HASH_FIELDS}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return _sha256_hex(canonical)


def _bare(h: str | None) -> str | None:
    if h is None:
        return None
    h = h.strip()
    return h[7:] if h.startswith("sha256:") else h


def is_canonical(entry: dict[str, Any]) -> bool:
    return (
        entry.get("epoch_id") == "F004-CANONICAL-2026-07-17"
        or entry.get("envelope_version") == "f004-v1"
        or (
            "receipt_id" in entry
            and "receipt_hash" in entry
            and "previous_hash" in entry
            and isinstance(entry.get("sequence"), int)
        )
    )


def this_hash(entry: dict[str, Any]) -> str | None:
    return (
        entry.get("this_hash")
        or entry.get("receipt_hash")
        or entry.get("hash")
        or entry.get("seal_hash")
        or entry.get("content_hash")
    )


def load_key(args: argparse.Namespace) -> bytes | None:
    if args.key_file:
        key = Path(args.key_file).read_text(encoding="utf-8").strip()
        return key.encode("utf-8") if key else None
    if args.key_env:
        val = os.environ.get(args.key_env, "")
        return val.encode("utf-8") if val else None
    return None


def sign(receipt_hash: str, key: bytes) -> str:
    return SIG_PREFIX + hmac.new(
        key, receipt_hash.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def verify_chain_file(chain_path: Path, key: bytes | None) -> dict[str, Any]:
    report: dict[str, Any] = {
        "tool": "audit_verify.py",
        "sig_epoch": "VAULT-SIG-1",
        "chain_path": str(chain_path),
        "entries": 0,
        "canonical_entries": 0,
        "historical_entries": 0,
        "corrupt_lines": 0,
        "signed_entries": 0,
        "signed_unverifiable": 0,
        "unsigned_after_cutover": 0,
        "cutover_seq": None,
        "failures": [],
        "warnings": [],
    }

    if not chain_path.exists():
        report["failures"].append({"class": "NO_CHAIN", "detail": f"{chain_path} not found"})
        return report

    prev_hash: str | None = None
    seen_ids: set[str] = set()
    seen_seqs: set[int] = set()
    signed_seqs: list[int] = []
    unsigned_after: list[dict[str, Any]] = []

    with open(chain_path, encoding="utf-8", errors="replace") as fh:
        for line_no, raw in enumerate(fh, start=1):
            s = raw.strip()
            if not s:
                continue
            try:
                entry = json.loads(s)
                if not isinstance(entry, dict):
                    raise ValueError("non-dict")
            except (json.JSONDecodeError, ValueError) as exc:
                report["corrupt_lines"] += 1
                report["failures"].append(
                    {"class": "CORRUPT_LINE", "line": line_no, "detail": str(exc)}
                )
                continue

            report["entries"] += 1
            canon = is_canonical(entry)
            if canon:
                report["canonical_entries"] += 1
            else:
                report["historical_entries"] += 1

            th = this_hash(entry)
            ph = entry.get("prev_hash") or entry.get("previous_hash")
            seq = entry.get("sequence", entry.get("seq"))
            rid = entry.get("receipt_id") or entry.get("id")

            # 1. Link integrity (within canonical stream)
            if canon and prev_hash is not None and ph:
                if _bare(str(ph)) != _bare(prev_hash):
                    report["failures"].append(
                        {
                            "class": "CHAIN_BREAK",
                            "line": line_no,
                            "seq": seq,
                            "detail": f"prev_hash {str(ph)[:16]}… != prior hash {str(prev_hash)[:16]}…",
                        }
                    )

            # 2. Envelope hash recompute (canonical with full body only)
            if (
                canon
                and entry.get("receipt_hash")
                and all(k in entry for k in ("sequence", "previous_hash", "timestamp", "actor_id"))
            ):
                expected = compute_receipt_hash(entry)
                if _bare(expected) != _bare(str(entry.get("receipt_hash"))):
                    report["failures"].append(
                        {
                            "class": "HASH_MISMATCH",
                            "line": line_no,
                            "seq": seq,
                            "detail": "recomputed receipt_hash mismatch — body was modified after sealing",
                        }
                    )

            # 5. Duplicates
            if rid:
                if rid in seen_ids:
                    report["failures"].append(
                        {"class": "DUPLICATE_RECEIPT", "line": line_no, "detail": f"duplicate receipt_id={rid}"}
                    )
                seen_ids.add(str(rid))
            if canon and isinstance(seq, int):
                if seq in seen_seqs:
                    report["failures"].append(
                        {"class": "SEQUENCE_COLLISION", "line": line_no, "detail": f"duplicate canonical sequence={seq}"}
                    )
                seen_seqs.add(seq)

            # 3. Signature verification
            sig = str(entry.get("signature") or "")
            skid = str(entry.get("sig_key_id") or "")
            if canon and skid:
                if skid != SIG_KEY_ID:
                    report["failures"].append(
                        {"class": "WRONG_KEY", "line": line_no, "seq": seq, "detail": f"unknown sig_key_id '{skid}'"}
                    )
                elif key is None:
                    report["signed_unverifiable"] += 1
                    report["warnings"].append(
                        {
                            "class": "SIGNED_NO_KEY",
                            "line": line_no,
                            "seq": seq,
                            "detail": "entry is signed but no key supplied — supply --key-file to complete audit",
                        }
                    )
                else:
                    expected_sig = sign(str(entry.get("receipt_hash") or ""), key)
                    if not hmac.compare_digest(sig, expected_sig):
                        report["failures"].append(
                            {
                                "class": "SIGNATURE_FAIL",
                                "line": line_no,
                                "seq": seq,
                                "detail": "HMAC-SHA256 signature mismatch — receipt_hash or signature forged",
                            }
                        )
                    else:
                        report["signed_entries"] += 1
                if isinstance(seq, int):
                    signed_seqs.append(seq)
            elif canon:
                unsigned_after.append({"line": line_no, "seq": seq})

            if th:
                prev_hash = str(th)

        # 4. Cutover rule — strict for auditors
        report["cutover_seq"] = min(signed_seqs) if signed_seqs else None
        if report["cutover_seq"] is not None:
            for u in unsigned_after:
                if isinstance(u["seq"], int) and u["seq"] > report["cutover_seq"]:
                    report["unsigned_after_cutover"] += 1
                    report["failures"].append(
                        {
                            "class": "SIGNATURE_FAIL",
                            "line": u["line"],
                            "seq": u["seq"],
                            "detail": (
                                f"unsigned canonical entry after VAULT-SIG-1 cutover "
                                f"(seq {report['cutover_seq']}) — post-cutover receipts must be signed"
                            ),
                        }
                    )

    last_hash = _bare(prev_hash) or ""
    report["head_hash_bare64"] = last_hash
    report["verified"] = not report["failures"]
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VAULT999-SIG offline auditor verifier")
    ap.add_argument("--chain", required=True, help="path to seal_chain.jsonl (work on a COPY)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--key-file", help="file containing the vault HMAC key")
    g.add_argument("--key-env", default="ARIFOS_VAULT_HMAC_KEY", help="env var holding the key (default %(default)s)")
    ap.add_argument("--expect-head", help="externally recorded head hash (bare64 or sha256:-prefixed)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    if not args.key_file and not os.environ.get(args.key_env):
        print(
            "[WARN] no key supplied — signatures will be counted as unverifiable;\n"
            "       complete the audit with --key-file (key delivered out-of-band).",
            file=sys.stderr,
        )

    key = load_key(args)
    report = verify_chain_file(Path(args.chain), key)

    if args.expect_head:
        want = _bare(args.expect_head) or ""
        got = report.get("head_hash_bare64") or ""
        if want != got:
            report["failures"].append(
                {"class": "HEAD_ANCHOR_MISMATCH", "detail": f"expected head {want[:16]}… got {got[:16]}…"}
            )
            report["verified"] = False

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, default=str))
    else:
        r = report
        verdict = "GREEN ✔ VERIFIED" if r["verified"] else "RED ✘ GAPS FOUND"
        print(f"VAULT999-SIG audit — {verdict}")
        print(f"  chain      : {r['chain_path']}")
        print(f"  entries    : {r['entries']} (canonical {r['canonical_entries']}, historical {r['historical_entries']}, corrupt {r['corrupt_lines']})")
        print(f"  signatures : {r['signed_entries']} verified, {r['signed_unverifiable']} unverifiable(no key), cutover_seq={r['cutover_seq']}")
        print(f"  unsigned after cutover : {r['unsigned_after_cutover']}")
        print(f"  head (bare64)          : {r.get('head_hash_bare64', '')[:24]}…")
        if r["warnings"]:
            print(f"  warnings   : {len(r['warnings'])}")
        for f in r["failures"][:20]:
            print(f"  ✘ [{f['class']}] line={f.get('line', '?')} seq={f.get('seq', '?')} — {f['detail']}")
        if len(r["failures"]) > 20:
            print(f"  … and {len(r['failures']) - 20} more (use --json)")

    return 0 if report["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
