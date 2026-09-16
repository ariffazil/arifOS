#!/usr/bin/env python3
"""compute_capability_hash.py — G0.6: semantic capability hash.

    CapabilityHash = SHA256( JCS( [ CapabilitySpec_1 .. n ] ) )

Every public capability is normalized to a semantic record (RFC 8785 JCS),
hashed, and the ordered projection hashed into one value. The hash is
witnessed in static/.well-known/capability_hash.json and bound into the
peer contract. CI (--check) fails when capability MEANING drifts without a
deliberate regeneration — capability drift becomes a witnessed boundary,
not an observability event.

Deliberate design choices:
- Description prose is EXCLUDED from the record: wording churn without
  semantic change must not flip an authority boundary.
- Schemas are hashed over their JCS-normalized parse — formatting-only
  edits do not change the hash, content edits always do.
- Stage/risk/floors/modes come from tools_sot.yaml (generated from
  constitutional_map.py — the capability SOT).

The enforcement seam (G3): a verdict minted under CapabilityHash C_n must
not authorize mutations after the hash becomes C_n+1 without explicit
compatibility review — Verdict(C_n, A) ↛ Authorization(C_n+1, A).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import rfc8785
import yaml

from arifosmcp.core.axis_map import VERB_AXES

REPO = Path(__file__).resolve().parent.parent
TOOLS_SOT = REPO / "tools_sot.yaml"
SCHEMA_DIR = REPO / "arifosmcp" / "schema" / "registry" / "tools"
STATE_PATH = REPO / "static" / ".well-known" / "capability_hash.json"
PEER_PATH = REPO / "static" / ".well-known" / "peer-contract.json"

KIND = "tool"
PUBLIC = True


def _sha(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _schema_path(name_short: str) -> Path | None:
    for cand in (f"arifos.{name_short}.schema.json", f"arifos.{name_short}.json"):
        p = SCHEMA_DIR / cand
        if p.exists():
            return p
    return None


def _schema_hash(path: Path) -> str:
    return _sha(rfc8785.dumps(json.loads(path.read_text())))


def build_records() -> list[dict]:
    sot = yaml.safe_load(TOOLS_SOT.read_text())
    tools = sot.get("tools") if isinstance(sot, dict) else sot
    records = []
    for t in tools:
        short = t["name"].replace("arif_", "")
        sp = _schema_path(short)
        axes = VERB_AXES[t["name"]]
        rec = {
            "canonical_name": t["name"],
            "kind": KIND,
            "public": PUBLIC,
            "metabolic_stage": axes["metabolic_stage"],
            "governance_tier": axes["governance_tier"],
            "stage": str(t.get("stage", "")),
            "risk_tier": str(t.get("risk_tier", "")),
            "floors": sorted(str(f) for f in (t.get("floors") or [])),
            "modes": sorted(str(m) for m in (t.get("modes") or [])),
            "schema_sha256": _schema_hash(sp) if sp else None,
        }
        records.append(rec)
    records.sort(key=lambda r: r["canonical_name"])
    return records


def capability_hash(records: list[dict]) -> str:
    return _sha(rfc8785.dumps(records))


def build_state(records: list[dict], chash: str) -> dict:
    return {
        "capability_hash": chash,
        "algorithm": "RFC8785-JCS + SHA256 over sorted semantic records",
        "record_count": len(records),
        "records": [
            {"name": r["canonical_name"], "record_sha256": _sha(rfc8785.dumps(r))}
            for r in records
        ],
        "excluded_by_design": [
            "description (prose churn without semantic change)",
        ],
        "enforcement_seam": (
            "Verdict(C_n, A) does NOT authorize under C_n+1 — G3 binds this "
            "hash into verdicts/receipts; until then this file is the witness."
        ),
    }


def write_outputs(records: list[dict], chash: str) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    state = build_state(records, chash)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    peer = json.loads(PEER_PATH.read_text())
    card = dict(peer.get("capability_card") or {})
    card["semantic_capability_hash"] = chash
    card["capability_hash_algorithm"] = state["algorithm"]
    peer["capability_card"] = card
    PEER_PATH.write_text(json.dumps(peer, indent=2, sort_keys=False, ensure_ascii=False) + "\n")


def check() -> int:
    drift = []
    records = build_records()
    chash = capability_hash(records)
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    if state.get("capability_hash") != chash:
        drift.append(str(STATE_PATH))
    peer = json.loads(PEER_PATH.read_text()) if PEER_PATH.exists() else {}
    if (peer.get("capability_card") or {}).get("semantic_capability_hash") != chash:
        drift.append(str(PEER_PATH))
    if drift:
        print("CAPABILITY DRIFT (regenerate: scripts/compute_capability_hash.py):")
        for d in drift:
            print(f"  {d}")
        print(f"  expected: {chash}")
        return 1
    print(f"capability hash coherent: {chash} ({len(records)} records)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--print", action="store_true", help="print hash only")
    args = ap.parse_args()

    records = build_records()
    if len(records) != 8:
        print(f"FATAL: expected 8 canonical records, got {len(records)}")
        return 2
    chash = capability_hash(records)

    if args.print:
        print(chash)
        return 0
    if args.check:
        return check()
    write_outputs(records, chash)
    print(f"wrote {STATE_PATH}")
    print(f"bound into {PEER_PATH}")
    print(f"capability_hash: {chash}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
