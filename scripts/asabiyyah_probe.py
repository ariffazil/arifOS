#!/usr/bin/env python3
"""asabiyyah_probe.py — arifOS kernel organ reading for the federation cycle instrument.

WHAT THIS IS
────────────
The kernel measures its OWN substrate and emits one reading conforming to
/root/AAA/schemas/asabiyyah-reading.schema.json. The kernel does not measure
other organs, and does not federate: it drops its reading and the aggregator
(`arifosmcp/runtime/asabiyyah.py:aggregate()`) sums counts and re-derives ratios.

The three signals (Ibn Khaldun, al-Muqaddimah 1377 · Usman Awang, Melayu 1992):

  CER  ceremony / exercise   → Luxury: doctrine production outruns capability
  ASD  executors / holders   → Kafes:  doctrine inherited, execution thinned
  ENC  gated / total paths   → Kerkoporta: a mutation path bypasses the gate

DESIGN LAW
──────────
* OBSERVE ONLY. This probe never judges, never mutates the repo, never remediates.
* Every number traces to a file / SQLite table / directory walk on disk. The exact
  rule that produced it is recorded in the metric's `source` and in `evidence`.
  A number with no source is a STORY; the kernel refuses to federate stories.
* `evidence` carries RAW ADDITIVE INTEGER COUNTS, never pre-divided ratios.
* Honest NOT_APPLICABLE beats an invented number. A labelled proxy is honest; an
  unlabelled one is a lie.
* Standard library only. The shared instrument is LOADED, never vendored:
  `importlib.util.spec_from_file_location` on the runtime module keeps the heavy
  `arifosmcp/__init__.py` out of the process.
* The only write is this organ's own reading to /var/lib/arifos/asabiyyah/arifOS.json.

Usage:
    python3 /root/arifOS/scripts/asabiyyah_probe.py            # emit + drop
    python3 /root/arifOS/scripts/asabiyyah_probe.py --no-write # emit only
    python3 /root/arifOS/scripts/asabiyyah_probe.py --window-days 30

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import socket
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Sequence

# ─────────────────────────────────────────────────────────────────────────
# anchors — every path below is checked for existence at runtime
# ─────────────────────────────────────────────────────────────────────────

REPO = Path("/root/arifOS")
MODULE_PATH = REPO / "arifosmcp" / "runtime" / "asabiyyah.py"
SCHEMA_PATH = Path("/root/AAA/schemas/asabiyyah-reading.schema.json")
DROP_DIR = Path("/var/lib/arifos/asabiyyah")
DROP_FILE = DROP_DIR / "arifOS.json"

ABI_CAPABILITY_REGISTRY = REPO / "arifosmcp" / "abi" / "capability_registry.json"
AGENT_REGISTRY = REPO / "arifos" / "identity" / "agent_registry.json"
RECEIPT_DB = Path("/var/lib/arifos/apex_metrics.db")
MODEL_REGISTRY = REPO / "arifosmcp" / "abi" / "model_registry.json"

DEFAULT_WINDOW_DAYS = 30

# CER — the walk rule, declared in one place. `live doctrine` = markdown that is
# not vendored, not built, not archived.
CER_EXCLUDE_DIRS = frozenset(
    {"build", "dist", ".venv", "node_modules", ".git", ".ruff_cache", "site-packages"}
)
CER_ARCHIVE_DIRS = frozenset({"archive", "_retired", "00_legacy_materials", "arifOS_park", ".archive"})

# ENC — an invocation of the authority reference monitor. Import-only mentions do
# NOT count: a module that imports the gate and never calls it is not a gate.
GATE_CALL_RE = re.compile(r"\b(pre_execution_gate|quick_gate)\s*\(")

# ENC — modules that admit a mutation. Each is tested, not assumed.
ENFORCEMENT_CANDIDATES: tuple[str, ...] = (
    "arifosmcp/runtime/kernel_router.py",
    "arifosmcp/runtime/tools.py",
    "arifosmcp/runtime/shell_forge.py",
    "arifosmcp/runtime/rest_routes/rest_routes.py",
    "arifosmcp/runtime/agentic_bridge.py",
    "arifosmcp/runtime/agent_loop.py",
    "arifosmcp/runtime/memory_gate.py",
    "arifosmcp/runtime/session_policy.py",
    "arifosmcp/runtime/art_registry.py",
    "arifosmcp/runtime/kernel_freeze.py",
    "arifosmcp/runtime/release_attestation.py",
)

# ENC — a module is only counted as a write primitive if it names protected state
# AND contains a write operation. File-level, therefore conservative: it will name a
# file that only mentions VAULT999 in prose. Such false positives are kept, not
# filtered, because an over-wide postern list is the honest failure direction.
WRITE_OP_RE = re.compile(r"write_text|\.write\(|open\([^)]*[\"'](?:a|w)")

# The one false positive that is a measurement error rather than a postern: this probe
# names VAULT999 only in prose and writes only its own reading (DROP_FILE). Excluding it
# is correctness, not leniency — recorded here and named in the metric's `source`.
SELF_EXCLUDE = frozenset({Path(__file__).name})

# ASD — synthetic/diagnostic actor ids. A load generator wearing a seat's name is
# not evidence that the seat still works. Declared, not tuned.
SYNTHETIC_ACTOR_RE = re.compile(
    r"(^|[-_/])(anon|anonymous|test|tests|probe|bench|selftest|e2e|fake|dummy|sample"
    r"|canary|demo|stress|stub|mock)([-_/0-9]|$)",
    re.IGNORECASE,
)


def log(msg: str) -> None:
    """Diagnostics go to stderr; stdout carries the reading and nothing else."""
    print(msg, file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────
# load the shared instrument (never vendor a copy)
# ─────────────────────────────────────────────────────────────────────────


def load_asabiyyah():
    if not MODULE_PATH.is_file():
        raise SystemExit(f"FATAL: instrument not found at {MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("asabiyyah", str(MODULE_PATH))
    if spec is None or spec.loader is None:
        raise SystemExit(f"FATAL: cannot build import spec for {MODULE_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["asabiyyah"] = mod
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────
# CER — ceremony artifacts vs exercised capabilities
# ─────────────────────────────────────────────────────────────────────────


def count_markdown(root: Path, exclude: frozenset[str]) -> int:
    """Live .md count. Rule: os.walk, prune excluded dir names anywhere in the
    tree, count every file ending '.md'. Symlinked dirs are not followed."""
    total = 0
    for _dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        total += sum(1 for f in filenames if f.endswith(".md"))
    return total


def abi_capabilities() -> list[dict[str, Any]]:
    """The kernel's own declarative capability manifest."""
    data = json.loads(ABI_CAPABILITY_REGISTRY.read_text())
    caps = data.get("capabilities") or []
    if not isinstance(caps, list):
        raise SystemExit("FATAL: abi/capability_registry.json has no capabilities list")
    return [c for c in caps if isinstance(c, dict)]


def receipted_tools(since_iso: str) -> set[str]:
    """Distinct tool names with at least one real invocation receipt in the window."""
    con = sqlite3.connect(f"file:{RECEIPT_DB}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT DISTINCT tool_name FROM tool_calls WHERE timestamp >= ?", (since_iso,)
        ).fetchall()
    finally:
        con.close()
    return {r[0] for r in rows if r[0]}


def exercised_capability_count(since_iso: str) -> tuple[int, int, int, set[str]]:
    """Exercised = ABI capability whose bound tool has a receipt in the window.

    Matrix anchored to the kernel's declarative manifest, closed by the kernel's own
    receipt ledger. Returns (exercised, declared_total, receipts_in_window, names).
    """
    caps = abi_capabilities()
    seen = receipted_tools(since_iso)
    names: set[str] = set()
    for cap in caps:
        tool = (cap.get("provider") or {}).get("tool")
        if tool and tool in seen:
            names.add(str(cap.get("capability_id") or tool))
    return len(names), len(caps), len(seen), names


# ─────────────────────────────────────────────────────────────────────────
# ASD — doctrine holders vs executors
# ─────────────────────────────────────────────────────────────────────────


def registry_seats() -> dict[str, dict[str, Any]]:
    """Registered seats in the kernel's own identity registry."""
    data = json.loads(AGENT_REGISTRY.read_text())
    agents = data.get("agents") or {}
    seats: dict[str, dict[str, Any]] = {}
    for name, rec in agents.items():
        if not isinstance(rec, dict):
            continue
        fi = str(rec.get("fi_id") or "").lower()
        toks = {t for t in re.split(r"[^a-z0-9]+", str(rec.get("agent_id") or name).lower()) if t}
        seats[str(name)] = {"fi": fi, "tokens": toks}
    return seats


def distinct_actors(since_iso: str) -> list[str]:
    con = sqlite3.connect(f"file:{RECEIPT_DB}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT DISTINCT actor_id FROM tool_calls WHERE timestamp >= ?", (since_iso,)
        ).fetchall()
    finally:
        con.close()
    return [r[0] for r in rows if r[0] is not None]


def seats_with_receipts(
    seats: dict[str, dict[str, Any]], actors: Sequence[str], *, exclude_synthetic: bool
) -> dict[str, list[str]]:
    """Match receipt actor ids to registered seats.

    Match rule (declared): an actor belongs to a seat if the seat's fi_id appears as
    a substring of the lowercased actor id, OR every token of the seat's agent_id
    appears as a token of the actor id. Actors matching SYNTHETIC_ACTOR_RE are
    excluded when exclude_synthetic — a bench harness is not a seat at work.
    """
    hits: dict[str, list[str]] = {}
    for actor in actors:
        if exclude_synthetic and SYNTHETIC_ACTOR_RE.search(actor):
            continue
        low = actor.lower()
        toks = {t for t in re.split(r"[^a-z0-9]+", low) if t}
        for name, seat in seats.items():
            fi: str = seat["fi"]
            seat_toks: set[str] = seat["tokens"]
            if (fi and fi in low) or (seat_toks and seat_toks <= toks):
                hits.setdefault(name, []).append(actor)
    return hits


# ─────────────────────────────────────────────────────────────────────────
# ENC — protected mutation paths
# ─────────────────────────────────────────────────────────────────────────


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def gated_admission_modules() -> list[str]:
    """Candidate admission modules that actually INVOKE the authority gate."""
    gated: list[str] = []
    for rel in ENFORCEMENT_CANDIDATES:
        path = REPO / rel
        if path.is_file() and GATE_CALL_RE.search(_read(path)):
            gated.append(rel)
    return gated


def ungated_vault_primitives() -> list[str]:
    """Vault/write primitives that touch protected state with no gate invocation.

    Complete mediation is the test, not intent: if the primitive that writes VAULT999
    can be imported and called without passing the reference monitor, the postern is
    open even when every polite caller uses the door.
    """
    out: list[str] = []
    for path in sorted((REPO / "arifosmcp" / "runtime").glob("vault*.py")):
        text = _read(path)
        if "VAULT999" in text and WRITE_OP_RE.search(text) and not GATE_CALL_RE.search(text):
            out.append(f"arifosmcp/runtime/{path.name}")
    extra = REPO / "arifosmcp" / "runtime" / "canonical_vault_chain.py"
    text = _read(extra)
    if extra.is_file() and "VAULT999" in text and WRITE_OP_RE.search(text) and not GATE_CALL_RE.search(text):
        out.append("arifosmcp/runtime/canonical_vault_chain.py")
    return out


def ungated_repo_scripts() -> list[str]:
    """Repo scripts that name VAULT999, write, and never call the gate.

    These are runnable by cron, by a human, or by any agent with a shell — outside
    every in-process gate in the package.
    """
    out: list[str] = []
    for path in sorted((REPO / "scripts").glob("*.py")):
        if path.name in SELF_EXCLUDE:
            continue
        text = _read(path)
        if "VAULT999" in text and WRITE_OP_RE.search(text) and not GATE_CALL_RE.search(text):
            out.append(f"scripts/{path.name}")
    return out


def declared_ungated_paths() -> list[str]:
    """Paths outside the package's mediation by construction.

    Each is witness-checked before it is named, so the list degrades honestly if the
    substrate changes.
    """
    out: list[str] = []
    if (REPO / ".git").is_dir():
        out.append(
            "git_commit (/root/arifOS/.git: no authority gate in .git/hooks — pre-commit "
            "hook is LSP lint only, and git commit --no-verify bypasses hooks entirely)"
        )
    if os.geteuid() == 0:
        out.append(
            "posix_direct_write (uid 0 shell/editor write to /root/arifOS and "
            "/var/lib/arifos: the gate is a Python function, there is no OS-level "
            "reference monitor — no fanotify/LSM rule — on these paths)"
        )
    return out


# ─────────────────────────────────────────────────────────────────────────
# GADAI — sovereign capacity signed away
# ─────────────────────────────────────────────────────────────────────────


def gadai_substrate() -> tuple[int, int, str]:
    """Does the kernel hold a ledger of its own rented capacity?

    substrate = models declared in abi/model_registry.json (the kernel's own record of
    inference capacity it depends on). Empty registry = no asset base on record, so the
    ratio is undefined. NOT_APPLICABLE is the honest answer; 0.0 would be a STORY.
    """
    if not MODEL_REGISTRY.is_file():
        return 0, 0, f"no asset base: {MODEL_REGISTRY} absent"
    data = json.loads(MODEL_REGISTRY.read_text())
    models = data.get("models")
    total = len(models) if isinstance(models, list) else 0
    if total <= 0:
        return 0, 0, (
            f"no asset base on record: {MODEL_REGISTRY} declares models=[] — the kernel "
            "keeps no ledger of capacity it rents, so gadai has no honest numerator"
        )
    # No relinquishment field exists in the registry; the kernel cannot measure the
    # share signed away. Emit NOT_APPLICABLE rather than invent the split.
    return 0, total, (
        f"{MODEL_REGISTRY} declares {total} model(s) but no relinquishment field — "
        "share signed away is not recorded, so gadai is NOT_APPLICABLE"
    )


# ─────────────────────────────────────────────────────────────────────────
# schema self-check (stdlib; the schema file is the contract)
# ─────────────────────────────────────────────────────────────────────────


def validate_reading(reading: dict[str, Any], schema_path: Path) -> list[str]:
    """Minimal validator for arifos.schemas.asabiyyah-reading v1.

    Checks structure, enums, metric shape and evidence integer-ness against the
    schema on disk. Not a general JSON-Schema engine — deliberately narrow, stdlib only.
    """
    errors: list[str] = []
    schema = json.loads(schema_path.read_text())

    allowed_top = set(schema.get("properties", {}))
    for key in schema.get("required", []):
        if key not in reading:
            errors.append(f"missing required key: {key}")
    for key in reading:
        if key not in allowed_top:
            errors.append(f"additional property not allowed: {key}")

    if reading.get("reading_version") != schema["properties"]["reading_version"]["const"]:
        errors.append("reading_version must be 1")
    organ_enum = schema["properties"]["organ"].get("enum", [])
    if organ_enum and reading.get("organ") not in organ_enum:
        errors.append(f"organ {reading.get('organ')!r} not in {organ_enum}")
    for key in ("host", "observed_at"):
        if not isinstance(reading.get(key), str) or not reading.get(key):
            errors.append(f"{key} must be a non-empty string")

    metric_def = schema["$defs"]["metric"]
    required_metric_keys = set(metric_def.get("required", []))
    allowed_metric_keys = set(metric_def.get("properties", {}))
    states = set(metric_def["properties"]["state"]["enum"])
    metric_names = set(schema["properties"]["metrics"].get("properties", {}))

    metrics = reading.get("metrics")
    if not isinstance(metrics, dict):
        errors.append("metrics must be an object")
    else:
        for name, metric in metrics.items():
            if name not in metric_names:
                errors.append(f"metric {name!r} not permitted by schema")
            if not isinstance(metric, dict):
                errors.append(f"metric {name!r} must be an object")
                continue
            missing = required_metric_keys - set(metric)
            if missing:
                errors.append(f"metric {name!r} missing {sorted(missing)}")
            extra = set(metric) - allowed_metric_keys
            if extra:
                errors.append(f"metric {name!r} has extra keys {sorted(extra)}")
            if metric.get("state") not in states:
                errors.append(f"metric {name!r} state {metric.get('state')!r} not in {sorted(states)}")
            value = metric.get("value")
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"metric {name!r} value must be number or null")
            if not (isinstance(metric.get("source"), str) and metric.get("source", "").strip()):
                errors.append(f"metric {name!r} source is empty — an unsourced number is a STORY")

    evidence = reading.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be an object")
    else:
        for key in (
            "ceremony_artifacts",
            "exercised_capabilities",
            "doctrine_holders",
            "executors",
            "gated_paths",
            "total_paths",
            "window_days",
        ):
            if key in evidence:
                val = evidence[key]
                if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                    errors.append(f"evidence.{key} must be a non-negative integer")
            elif key in ("ceremony_artifacts", "exercised_capabilities", "window_days"):
                errors.append(f"evidence.{key} is required by this organ's contract")
        if "window_days" in evidence and evidence["window_days"] < 1:
            errors.append("evidence.window_days must be >= 1")
        ungated = evidence.get("ungated")
        if ungated is not None and (
            not isinstance(ungated, list) or not all(isinstance(u, str) for u in ungated)
        ):
            errors.append("evidence.ungated must be a list of strings")
    return errors


def _finite(metric: Any) -> Any:
    """Guard the JSON contract: Infinity is not a JSON number.

    asabiyyah.ceremony_exercise_ratio returns float('inf') when nothing was exercised —
    an undefined ratio, correct for the classifier, unrepresentable in JSON. Emit null
    with state UNKNOWN and say so, rather than serialising a non-standard literal.
    """
    value = getattr(metric, "value", None)
    if isinstance(value, float) and not math.isfinite(value):
        metric.value = None
        metric.state = "UNKNOWN"
        note = "ratio undefined (0 exercised): module returned a non-finite value, emitted as null"
        metric.notes = f"{metric.notes}; {note}" if metric.notes else note
    return metric


# ─────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────


def build_reading(window_days: int):
    asb = load_asabiyyah()
    observed_at = os.environ.get("ASABIYYAH_OBSERVED_AT") or time.strftime("%Y-%m-%dT%H:%M:%S%z")
    since = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - window_days * 86400)
    )

    # — CER ───────────────────────────────────────────────────────────────
    ceremony = count_markdown(REPO, CER_EXCLUDE_DIRS)
    ceremony_excl_archive = count_markdown(REPO, CER_EXCLUDE_DIRS | CER_ARCHIVE_DIRS)
    exercised, abi_total, receipts_in_window, exercised_names = exercised_capability_count(since)
    cer_source = (
        f"ceremony_artifacts: os.walk({REPO}) pruning any dir named "
        f"{sorted(CER_EXCLUDE_DIRS)}, counting *.md ({ceremony} live; {ceremony_excl_archive} "
        f"with archive/_retired/legacy/park also pruned). exercised_capabilities: "
        f"capabilities declared in {ABI_CAPABILITY_REGISTRY} ({abi_total}) whose provider.tool "
        f"has >=1 row in {RECEIPT_DB} table tool_calls with timestamp >= {since} "
        f"({receipts_in_window} distinct tool names receipted; exercised: "
        f"{', '.join(sorted(exercised_names))})"
    )
    cer = asb.ceremony_exercise_ratio(ceremony, exercised, source=cer_source, observed_at=observed_at)

    # — ASD ───────────────────────────────────────────────────────────────
    seats = registry_seats()
    holders = len(seats)
    actors = distinct_actors(since)
    working = seats_with_receipts(seats, actors, exclude_synthetic=True)
    working_all = seats_with_receipts(seats, actors, exclude_synthetic=False)
    executors = len(working)
    asd_source = (
        f"doctrine_holders: len(agents) in {AGENT_REGISTRY} = {holders} registered seats "
        f"(fi_id + agent_id + declared capabilities). executors: distinct actor_id in "
        f"{RECEIPT_DB} tool_calls with timestamp >= {since} matched to a registered seat by "
        f"the declared rule (seat fi_id substring of lowercased actor, OR all agent_id tokens "
        f"present as actor tokens), excluding actor ids matching the synthetic/diagnostic "
        f"pattern {SYNTHETIC_ACTOR_RE.pattern!r}: {executors} seats receipted "
        f"({', '.join(sorted(working))})"
    )
    asd = asb.asabiyyah_depth(holders, executors, source=asd_source, observed_at=observed_at)

    # — ENC ───────────────────────────────────────────────────────────────
    gated = gated_admission_modules()
    ungated = ungated_vault_primitives() + ungated_repo_scripts() + declared_ungated_paths()
    total_paths = len(gated) + len(ungated)
    enc_source = (
        "path test = the module that admits the mutation invokes the authority gate "
        "(regex pre_execution_gate\\(|quick_gate\\(). File-local by construction: it proves "
        "a gate call site, not end-to-end coverage where a gated wrapper calls an ungated "
        "primitive. Enumeration rule: (a) declared in-package admission modules "
        f"{list(ENFORCEMENT_CANDIDATES)}; (b) every arifosmcp/runtime/vault*.py and "
        "canonical_vault_chain.py that names VAULT999 and contains a write operation; "
        f"(c) every {REPO}/scripts/*.py that names VAULT999 and contains a write operation, "
        f"minus this probe's own file {sorted(SELF_EXCLUDE)} (it writes only its own reading); "
        "(d) declared out-of-band paths (git commit, uid-0 direct write) witness-checked at "
        f"runtime. total_paths={total_paths}, gated={len(gated)}: {', '.join(gated)}"
    )
    enc = asb.enforcement_coverage(
        len(gated), total_paths, source=enc_source, observed_at=observed_at, ungated=ungated
    )

    # — GADAI ─────────────────────────────────────────────────────────────
    relinquished, total_value, gadai_reason = gadai_substrate()
    gadai = asb.kampung_gadai_risk(
        relinquished, total_value, source=gadai_reason, observed_at=observed_at
    )

    metrics = {
        "cer": _finite(cer),
        "asd": _finite(asd),
        "enc": _finite(enc),
        "gadai": _finite(gadai),
    }

    evidence: dict[str, Any] = {
        "ceremony_artifacts": ceremony,
        "exercised_capabilities": exercised,
        "doctrine_holders": holders,
        "executors": executors,
        "gated_paths": len(gated),
        "total_paths": total_paths,
        "ungated": ungated,
        "window_days": window_days,
        # context, not federated inputs — the kernel sums only the keys above
        "ceremony_artifacts_excl_archive": ceremony_excl_archive,
        "abi_capabilities_declared": abi_total,
        "receipted_tool_names_window": receipts_in_window,
        "distinct_receipters_window": len(actors),
        "seats_receipted_incl_synthetic": len(working_all),
        "gated_modules": gated,
        "window_start_utc": since,
    }

    reading = asb.SubstrateReading(
        organ="arifOS",
        host=socket.gethostname(),
        observed_at=observed_at,
        metrics=metrics,
        evidence=evidence,
    )
    return reading


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="arifOS kernel substrate reading (asabiyyah)")
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS)
    parser.add_argument("--out", default=str(DROP_FILE))
    parser.add_argument("--no-write", action="store_true", help="emit only; do not drop a reading")
    parser.add_argument("--no-validate", action="store_true")
    args = parser.parse_args(argv)

    if args.window_days < 1:
        raise SystemExit("FATAL: --window-days must be >= 1")

    reading = build_reading(args.window_days)
    payload = json.loads(reading.to_json())  # round-trip: the reading IS the contract

    if not args.no_validate:
        if not SCHEMA_PATH.is_file():
            raise SystemExit(f"FATAL: schema not found at {SCHEMA_PATH}")
        errors = validate_reading(payload, SCHEMA_PATH)
        if errors:
            for err in errors:
                log(f"SCHEMA INVALID: {err}")
            return 2

    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False)

    if not args.no_write:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(rendered + "\n")
        log(f"reading dropped: {args.out}")

    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
