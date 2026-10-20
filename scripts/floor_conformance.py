#!/usr/bin/env python3
"""floor_conformance.py — do all arifOS surfaces agree on F1–F13?

WHY (failure class, observed 2026-10-20 by claude-code-kvm8):
  The same 13 floors carried different names on different surfaces in one
  running kernel. An agent reading arifos://doctrine and an agent reading
  arifos://floors were obeying different laws, and arif_think(mode=axioms)
  emitted a third set. A resource that says "single source of truth" while
  five consumers hardcode their own copy does not enforce anything.

WHAT THIS IS
  The missing enforcement point. Read-only. It reads the declared canon
  (GENESIS/FLOOR_TABLE.json — its own `consumers_must_sync_to` names itself
  or 000_KERNEL_CANON.md) and mechanically extracts the floor name from every
  consumer surface. Divergence is reported, never silently resolved: the
  checker does not decide which name is right (that is an F13 call).

OUTPUT
  Human table + JSON. Exit 1 if any surface diverges or is unreadable.

USAGE
  python3 floor_conformance.py [--json] [--quiet] [--no-live]
"""
from __future__ import annotations

import ast
import json
import re
import sys
import urllib.request

REPO = "/root/arifOS"
CANON = f"{REPO}/GENESIS/FLOOR_TABLE.json"
MCP = "http://127.0.0.1:8088/mcp"


# ── extractors ───────────────────────────────────────────────────────
def _from_py_dict(path: str, var: str) -> dict[str, str]:
    """Parse a module-level dict literal of the form {"F1": "...", ...}."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    for node in ast.walk(tree):
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target.id]
        if var in targets:
            if isinstance(node.value, ast.Dict):
                out = {}
                for k, v in zip(node.value.keys, node.value.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        out[str(k.value)] = str(v.value)
                return out
    raise LookupError(f"{var} not found in {path}")


def _from_prose(path: str) -> dict[str, str]:
    """Parse lines like 'F06 MARUAH   : Dignity-first...'."""
    out = {}
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\s*F(\d{1,2})\s+([A-Z][A-Z0-9_²⇄·\- ]{1,28}?)\s*(?::|—|\|)", line)
        if m:
            out[f"F{int(m.group(1))}"] = m.group(2).strip()
    return out


def _law_enum(path: str) -> dict[str, str]:
    """Parse class Law members. Multi-line values (L03) must not be missed — use AST."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = {}
    for cls in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "Law"]:
        for node in cls.body:
            target = None
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                t = node.targets[0]
                target = t.id if isinstance(t, ast.Name) else None
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target = node.target.id
            if not target:
                continue
            m = re.match(r"^L(\d{2})_([A-Z]+)$", target)
            if m:
                out[f"F{int(m.group(1))}"] = m.group(2)
    return out


def _live_floors_resource() -> dict[str, str]:
    """Read arifos://floors over MCP (JSON-RPC resources/read)."""
    body = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "resources/read",
        "params": {"uri": "arifos://floors"},
    }).encode()
    req = urllib.request.Request(MCP, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })
    raw = urllib.request.urlopen(req, timeout=20).read().decode()
    if "data: " in raw:
        raw = raw.split("data: ", 1)[-1]
    text = json.loads(raw)["result"]["contents"][0]["text"]
    out = {}
    for m in re.finditer(r"^\|\s*\*\*F(\d{1,2})\*\*\s*\|\s*([^|]+?)\s*\|", text, re.M):
        out[f"F{int(m.group(1))}"] = m.group(2).strip()
    return out


def _live_axioms() -> dict[str, str]:
    """Read arif_think(mode=axioms) — the cognitive surface agents act on."""
    args = {"mode": "axioms", "query": "F1-F13"}
    sid = _arg("--session")
    if sid:
        args["session_id"] = sid
    body = json.dumps({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "arif_think", "arguments": args},
    }).encode()
    req = urllib.request.Request(MCP, data=body, headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    })
    raw = urllib.request.urlopen(req, timeout=60).read().decode()
    if "data: " in raw:
        raw = raw.split("data: ", 1)[-1]
    payload = json.loads(json.loads(raw)["result"]["content"][0]["text"])

    def find_axioms(node):
        """Envelope nesting varies by auth path — search instead of assuming depth."""
        if isinstance(node, dict):
            if isinstance(node.get("axioms"), list):
                return node["axioms"]
            for v in node.values():
                got = find_axioms(v)
                if got:
                    return got
        elif isinstance(node, list):
            for v in node:
                got = find_axioms(v)
                if got:
                    return got
        return None

    axes = find_axioms(payload)
    if not axes:
        raise LookupError("no axioms list in arif_think payload")
    out = {}
    for a in axes:
        m = re.match(r"^L(\d{2})_([A-Z]+)$", str(a.get("id", "")))
        if m:
            out[f"F{int(m.group(1))}"] = m.group(2)
    return out


def _rendered_doctrine() -> dict[str, str]:
    """Read the RENDERED doctrine block, not its source text.

    Since 2026-10-20 the floor block is generated from
    arifosmcp.constitutional_canon, so parsing doctrine.py source would
    check the wrong thing — the renderer, not the output.
    """
    import importlib
    sys.path.insert(0, REPO)
    mod = importlib.import_module("arifosmcp.constitutional_canon")
    out = {}
    for m in re.finditer(r"^F(\d{1,2})\s+([A-Z][A-Z0-9_²⇄·\- ]{1,28}?)\s*(?::|—)",
                         mod.doctrine_block(), re.M):
        out[f"F{int(m.group(1))}"] = m.group(2).strip()
    return out or _from_prose(f"{REPO}/arifosmcp/resources/doctrine.py")


SURFACES = [
    ("resource:doctrine", _rendered_doctrine),
    ("resource:schema", lambda: _from_prose(f"{REPO}/arifosmcp/resources/schema.py")),
    ("resource:floor/{id}", lambda: _floors_template()),
    ("code:constitutional_map", lambda: _law_enum(f"{REPO}/arifosmcp/constitutional_map.py")),
    ("code:amendment_guard", lambda: _from_py_dict(f"{REPO}/arifosmcp/runtime/amendment_guard.py", "FLOOR_NAMES")),
    ("live:arifos://floors", _live_floors_resource),
    ("live:arif_think(axioms)", _live_axioms),
]


def _floors_template() -> dict[str, str]:
    """arifos://floor/{id} values are full paragraphs — keep only 'F6 MARUAH'.

    Read the EFFECTIVE dict, not the source literal: since 2026-10-20 the
    identity line is generated at import time from constitutional_canon and
    F10–F13 exist only as runtime aliases of the L-prefixed keys.
    """
    import importlib
    sys.path.insert(0, REPO)
    mod = importlib.import_module("arifosmcp.resources.floor_table")
    raw = {k: v for k, v in mod.FLOOR_TABLE.items() if isinstance(v, str)}
    raw.setdefault("__source__", "")
    out = {}
    for fid, text in raw.items():
        if not re.match(r"^(F|L)\d{1,2}$", str(fid)):
            continue
        m = re.match(r"^\s*(?:F|L)\d{1,2}\s+([A-Z][A-Z0-9_²⇄·\- ]{1,28}?)\s*(?:—|:)", text)
        if m:
            norm = f"F{int(fid[1:])}"
            out[norm] = m.group(1).strip()
    return out


# Sealed dual-registry bridges — GENESIS/000_KERNEL_CANON.md §3.4 (F13, 2026-07-24).
# Two names, both correct, chosen by the RENDERING layer. Flagging these as drift
# was a false positive in the first cut of this checker (corrected 2026-10-20).
SEALED_BRIDGES: dict[str, set[str]] = {
    "F6": {"MARUAH", "EMPATHY"},          # kernel layer / public layer
}

# Canonical confidence ceiling — GENESIS/000_KERNEL_CANON.md §3.2 (F13, 2026-07-23).
# Confidence cap = 1 − Ω₀ ∈ [0.95, 0.97]; operational ceiling 0.96.
# The 0.90 that used to sit in the doctrine page is the stale value §3.2 absorbed.
CONFIDENCE_HARD_MAX = 0.97
CONFIDENCE_OPERATIONAL = 0.96
OMEGA_BAND = (0.03, 0.05)


def normalise(name: str) -> str:
    """Hyphenation/separators are typography, not law: ANTI-HANTU == ANTIHANTU."""
    toks = [t for t in re.split(r"[^A-Z0-9]+", name.upper()) if t and t not in {"F", "THE"}]
    return "".join(toks)


def _arg(flag: str) -> str | None:
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return None


def check_confidence_cap() -> dict:
    """F7: is the confidence band (1 − Ω₀ ∈ [0.95, 0.97]) respected?

    The old check compared against 0.90 parsed from the doctrine page. That
    number is the STALE value GENESIS/000_KERNEL_CANON.md §3.2 absorbed —
    checking it would have been measuring against a retired rule (fixed
    2026-10-20 after reading the sealed canon instead of the resource).
    """
    args = {"mode": "axioms", "query": "F1-F13"}
    sid = _arg("--session")
    if sid:
        args["session_id"] = sid
    body = json.dumps({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                       "params": {"name": "arif_think", "arguments": args}}).encode()
    req = urllib.request.Request(MCP, data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    raw = urllib.request.urlopen(req, timeout=60).read().decode()
    if "data: " in raw:
        raw = raw.split("data: ", 1)[-1]
    payload = json.loads(json.loads(raw)["result"]["content"][0]["text"])

    def find_axioms(node):
        if isinstance(node, dict):
            if isinstance(node.get("axioms"), list):
                return node["axioms"]
            for v in node.values():
                got = find_axioms(v)
                if got:
                    return got
        elif isinstance(node, list):
            for v in node:
                got = find_axioms(v)
                if got:
                    return got
        return None

    axes = find_axioms(payload) or []
    if not axes:
        return {"status": "UNMEASURED",
                "detail": "no axioms emitted; pass --session for an attributed call"}
    confs = [(a.get("id"), a.get("confidence")) for a in axes
             if isinstance(a.get("confidence"), (int, float))]
    hard = CONFIDENCE_HARD_MAX
    over = [(i, c) for i, c in confs if c > hard]
    over_ops = [(i, c) for i, c in confs if c > CONFIDENCE_OPERATIONAL]
    high = max(confs, key=lambda x: x[1]) if confs else (None, None)
    return {
        "status": "VIOLATION" if over else "CONFORMANT",
        "rule": "F7 HUMILITY — GENESIS/000_KERNEL_CANON.md §3.2 (F13 2026-07-23)",
        "declared_band": {"omega_0": list(OMEGA_BAND),
                          "cap_range": [1 - OMEGA_BAND[1], 1 - OMEGA_BAND[0]],
                          "operational_ceiling": CONFIDENCE_OPERATIONAL},
        "stale_value_retired": 0.90,
        "axioms_emitted": len(axes),
        "max_emitted": {"axiom": high[0], "confidence": high[1]},
        "over_hard_max": [{"axiom": i, "confidence": c} for i, c in over],
        "over_operational": len(over_ops),
    }


def main() -> int:
    as_json = "--json" in sys.argv
    quiet = "--quiet" in sys.argv
    live = "--no-live" not in sys.argv
    surfaces = [s for s in SURFACES if live or not s[0].startswith("live:")]

    canon_doc = json.load(open(CANON, encoding="utf-8"))
    canon = {f["id"]: f["name"] for f in canon_doc["floors"]}

    extracted: dict[str, dict[str, str] | str] = {}
    for label, fn in surfaces:
        try:
            extracted[label] = fn()
        except Exception as e:  # unreadable is a finding, not a crash
            extracted[label] = f"UNREADABLE: {type(e).__name__}: {e}"

    findings = []
    for fid in sorted(canon, key=lambda x: int(x[1:])):
        ref = normalise(canon[fid])
        row = {"floor": fid, "canon": canon[fid], "surfaces": {}}
        for label, data in extracted.items():
            if isinstance(data, str):
                row["surfaces"][label] = {"name": None, "status": "UNREADABLE", "detail": data[:90]}
                continue
            got = data.get(fid)
            if got is None:
                status, detail = "MISSING", "floor absent from surface"
            elif fid in SEALED_BRIDGES and normalise(got) in {
                    normalise(x) for x in SEALED_BRIDGES[fid]}:
                status, detail = "BRIDGED", "sealed dual-registry (canon §3.4)"
            elif normalise(got) == ref:
                status, detail = "MATCH", ""
            elif ref in normalise(got):
                status, detail = "SUPERSET", "canon name contained in surface name"
            else:
                status, detail = "DRIFT", f"canon={canon[fid]}"
            row["surfaces"][label] = {"name": got, "status": status, "detail": detail}
            if status in {"DRIFT", "MISSING"}:
                findings.append((fid, label, canon[fid], got or status))

    unreadable = [label for label, v in extracted.items() if isinstance(v, str)]
    readable = len(extracted) - len(unreadable)
    # P2 (review 2026-10-20): an unreadable surface is NOT evidence of
    # conformance. If every probe fails we must never report CONFORMANT.
    if findings:
        verdict = "DRIFT"
    elif unreadable:
        verdict = "INCOMPLETE"
    else:
        verdict = "CONFORMANT"
    report = {
        "schema": "arifos.floor_conformance.v1",
        "checked_at": __import__("datetime").datetime.now(
            __import__("datetime").UTC).isoformat(),
        "canon": {"path": CANON, "version": canon_doc.get("version"),
                  "authority": canon_doc.get("authority"),
                  "consumers_must_sync_to": canon_doc.get("consumers_must_sync_to")},
        "surfaces_read": readable,
        "surfaces_total": len(surfaces),
        "surfaces_unreadable": unreadable,
        "verdict": verdict,
        "drift_count": len(findings),
        "findings": [{"floor": f, "surface": s, "canon": c, "surface_value": v}
                     for f, s, c, v in findings],
    }
    # per-floor matrix
    matrix = []
    for fid in sorted(canon, key=lambda x: int(x[1:])):
        ref = normalise(canon[fid])
        entry = {"floor": fid, "canon": canon[fid]}
        for label, data in extracted.items():
            if isinstance(data, str):
                entry[label] = "UNREADABLE"
                continue
            got = data.get(fid)
            if got is None:
                entry[label] = "ABSENT"
            elif fid in SEALED_BRIDGES and normalise(got) in {
                    normalise(x) for x in SEALED_BRIDGES[fid]}:
                entry[label] = "ok~"
            elif normalise(got) == ref:
                entry[label] = "ok"
            elif ref in normalise(got):
                entry[label] = "ok*"
            else:
                entry[label] = got
        matrix.append(entry)
    report["matrix"] = matrix
    report["rows"] = matrix

    capcheck = None
    if live:
        try:
            capcheck = check_confidence_cap()
        except Exception as e:  # never let the cap probe hide the naming result
            capcheck = {"status": "UNMEASURED", "detail": f"{type(e).__name__}: {e}"}
        report["confidence_cap"] = capcheck

    if as_json:
        print(json.dumps(report, indent=2))
    elif not quiet:
        print(f"CANON  {CANON}  v{canon_doc.get('version')}  ({canon_doc.get('authority')})")
        print(f"SURFACES READ  {readable}/{len(surfaces)}\n")
        heads = [s[0] for s in surfaces]
        w = max(len(h) for h in heads) + 2
        print(f"{'floor':6}{'canon':22}" + "".join(h.ljust(w) for h in heads))
        for row in matrix:
            line = f"{row['floor']:6}{row['canon']:22}"
            line += "".join(str(row[h]).ljust(w) for h in heads)
            print(line)
        print(f"\nVERDICT  {verdict}  ({len(findings)} drift)")
        for f, s, c, v in findings:
            print(f"  {f}  canon={c:16} {s:24} → {v}")
        if capcheck:
            print(f"\nF2 CONFIDENCE CAP  {capcheck.get('status')}  "
                  f"declared={capcheck.get('declared_cap')} "
                  f"max_emitted={capcheck.get('max_emitted')} "
                  f"over={len(capcheck.get('over_cap', []))}")
        print("\nok = exact token match · ok* = canon name is a subset (e.g. EMPATHY ⊂ EMPATHY ⇄ MARUAH)")
        print("Resolution of any drift is an F13 sovereign call. This script does not decide.")

    return 0 if verdict == "CONFORMANT" else 1


if __name__ == "__main__":
    raise SystemExit(main())
