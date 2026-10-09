#!/usr/bin/env python3
"""
vault999_auditor_export.py — Independent audit tool for VAULT999 ledgers.
Part of arifOS v1.0.0-SEALED freeze protocol (item #3, punch list).

DESIGN TRUTH (2026-08-31 forensic finding):
  - Kernel canonical spec exists (arifosmcp/runtime/canonical_vault_chain.py:
    receipt_hash = sha256("sha256:"+canonical_json(15 _HASH_FIELDS)))
  - Historical ledgers (SEALED_EVENTS*.jsonl) PREDATE this spec and carry
    hash fields whose algorithms are NOT kernel-verifiable.
  - Therefore this tool is honest about method boundaries:
      VERIFIED   = internal hashes recomputed against a documented spec
      ANCHORED   = file snapshot SHA256 + Merkle root over record hashes
                   (tamper-evidence for the artifact, NOT chain validation)
  - seal_chain.jsonl (canonical store) is verified by spec when it exists.

Zero dependencies beyond Python stdlib. An auditor re-runs `verify` mode
with the same ledger files + manifest and must get identical results.

Usage:
  export  [--vault DIR] [--out manifest.json]
  verify  --manifest manifest.json [--vault DIR]
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

CANON_SPEC = {
    "fields": ("sequence", "previous_hash", "timestamp", "actor_id",
               "session_id", "trace_id", "operation_id", "tool_name",
               "input_hash", "authority_state", "decision_reference",
               "result_hash", "reversibility", "software_release", "epoch_id"),
    "algorithm": ("receipt_hash = 'sha256:' + hex(sha256(json.dumps("
                  "{f: rec[f] for f in FIELDS}, sort_keys=True, "
                  "separators=(',',':'), default=str)))"),
    "source": "arifosmcp/runtime/canonical_vault_chain.py:158",
}

HISTORICAL_LEDGERS = ("SEALED_EVENTS.jsonl", "SEALED_EVENTS_v2.jsonl",
                      "arifflow_sealed.jsonl")
CANONICAL_LEDGERS = ("seal_chain.jsonl",)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def merkle_root(leaves: list[str]) -> str | None:
    """Standard binary Merkle root over hex leaf hashes (duplicate-last on odd)."""
    if not leaves:
        return None
    level = [l.removeprefix("sha256:") for l in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(
            bytes.fromhex(level[i]) + bytes.fromhex(level[i + 1])
        ).hexdigest() for i in range(0, len(level), 2)]
    return "sha256:" + level[0]


def parse_ledger(p: Path) -> tuple[list[dict], list[dict]]:
    good, bad = [], []
    with open(p, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            try:
                good.append(json.loads(s))
            except Exception as e:
                bad.append({"line": i, "error": str(e)[:120], "head": s[:100]})
    return good, bad


def leaf_of(rec: dict, raw_line_sha: str | None = None) -> str:
    """Leaf for Merkle snapshot: honor declared merkle_leaf, else hash raw line."""
    ml = rec.get("merkle_leaf")
    if isinstance(ml, str) and len(ml) >= 32:
        return ml.removeprefix("sha256:")
    if raw_line_sha:
        return raw_line_sha.removeprefix("sha256:")
    core = {k: v for k, v in rec.items()
            if k not in ("merkle_leaf", "chain_hash", "signature", "prev_hash")}
    return hashlib.sha256(json.dumps(
        core, sort_keys=True, separators=(",", ":"), default=str
    ).encode()).hexdigest()


def parse_ledger_with_raw(p: Path):
    good, bad = [], []
    with open(p, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            raw_sha = hashlib.sha256(s.encode()).hexdigest()
            try:
                rec = json.loads(s)
            except Exception as e:
                bad.append({"line": i, "error": str(e)[:120], "head": s[:100]})
                continue
            good.append((rec, raw_sha))
    return good, bad


def verify_canonical(records: list[dict]) -> dict:
    """Verify records against the kernel canonical spec (go-forward chain)."""
    checked = matched = 0
    for r in records:
        if not all(f in r for f in CANON_SPEC["fields"]) or "receipt_hash" not in r:
            continue
        checked += 1
        body = {k: r.get(k) for k in CANON_SPEC["fields"]}
        canon = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
        v = "sha256:" + hashlib.sha256(canon.encode()).hexdigest()
        if v.removeprefix("sha256:") == str(r["receipt_hash"]).removeprefix("sha256:"):
            matched += 1
    linked = sum(1 for a, b in zip(records, records[1:])
                 if b.get("previous_hash") and
                 str(a.get("receipt_hash", "")).removeprefix("sha256:") ==
                 str(b.get("previous_hash")).removeprefix("sha256:"))
    return {"checked": checked, "matched": matched, "linked_pairs": linked}


def build_manifest(vault: Path) -> dict:
    ledgers = []
    for name in (*HISTORICAL_LEDGERS, *CANONICAL_LEDGERS):
        p = vault / name
        if not p.exists():
            p2 = vault / "sealed" / name
            if not p2.exists():
                continue
            p = p2
        good, bad = parse_ledger_with_raw(p)
        recs = [g[0] for g in good]
        leaves = [leaf_of(r, raw) for r, raw in good]
        is_canonical = name in CANONICAL_LEDGERS
        entry = {
            "file": str(p), "records": len(recs),
            "bad_lines": bad,
            "file_sha256": sha256_file(p),
            "merkle_root_snapshot": merkle_root(leaves),
            "method": ("VERIFIED:canonical_spec" if is_canonical
                       else "ANCHORED:snapshot_only — internal chain fields "
                            "predate kernel canonical spec; see FINDINGS"),
            "canonical_check": verify_canonical(recs) if is_canonical else None,
        }
        ledgers.append(entry)
    return {
        "tool": "vault999_auditor_export",
        "version": "0.1.0",
        "exported_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "canonical_spec": CANON_SPEC,
        "method_boundaries": {
            "VERIFIED": "hash recomputed against documented kernel spec",
            "ANCHORED": "file SHA256 + Merkle snapshot root (tamper-evidence, "
                        "not internal-chain validation)",
        },
        "findings": [
            "Historical ledgers carry merkle_leaf/chain_hash fields whose "
            "algorithm is not documented in kernel source; they are anchored, "
            "not verified.",
            "Kernel canonical spec (receipt_hash over 15 fields) is the "
            "go-forward write path; seal_chain.jsonl not yet instantiated.",
        ],
        "ledgers": ledgers,
    }


def run_verify(vault: Path, manifest: dict) -> int:
    m = build_manifest(vault)
    fails = []
    if len(m["ledgers"]) != len(manifest["ledgers"]):
        fails.append("ledger count drift")
    for a, b in zip(m["ledgers"], manifest["ledgers"]):
        for k in ("file", "records", "file_sha256", "merkle_root_snapshot"):
            if a[k] != b[k]:
                fails.append(f"{a['file']}: {k} drift "
                             f"({b[k]} -> {a[k]})")
    print(json.dumps({"verdict": "PASS" if not fails else "FAIL",
                      "fails": fails}, indent=2))
    return 0 if not fails else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("export", "verify"))
    ap.add_argument("--vault", default="/root/VAULT999")
    ap.add_argument("--manifest", default="vault999_auditor_manifest.json")
    a = ap.parse_args()
    vault = Path(a.vault)
    if a.mode == "export":
        m = build_manifest(vault)
        Path(a.manifest).write_text(json.dumps(m, indent=2))
        print(json.dumps({l["file"].split("/")[-1]:
                          {"records": l["records"], "root": l["merkle_root_snapshot"][:23],
                           "bad": len(l["bad_lines"])} for l in m["ledgers"]}, indent=2))
        print(f"manifest -> {a.manifest}")
        return 0
    return run_verify(vault, json.loads(Path(a.manifest).read_text()))


if __name__ == "__main__":
    sys.exit(main())
