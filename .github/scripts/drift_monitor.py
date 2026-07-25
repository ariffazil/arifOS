#!/usr/bin/env python3
"""
arifOS Drift Monitor — Canonical Surface Auditor (F1–F13 · CANON_APEX_V2)

Reads the 13 sealed canon files + FLOOR_TABLE.json as the single source of truth.
Snapshots live surfaces (GitHub, PyPI, MCP, kernel health) and detects drift.
Writes drift events to Supabase. Alerts on VOID-severity mismatches.

Usage:
    python drift_monitor.py [--dry-run] [--supabase-write] [--alert]
"""

import json, os, sys, re, hashlib, argparse
from datetime import datetime, timezone
from typing import Any
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # type: ignore

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None  # type: ignore

# ── Config ────────────────────────────────────────────────────────────────
CANON_DIR = Path(os.environ.get("CANON_DIR", "docs/canon/CANON_APEX_V2"))
FLOOR_TABLE_PATH = Path(os.environ.get("FLOOR_TABLE_PATH", "GENESIS/FLOOR_TABLE.json"))
SPEC_VERSION = os.environ.get("CANON_SPEC_VERSION", "v2026.07.APEX")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# ── Surface URLs ──────────────────────────────────────────────────────────
SURFACES = {
    "github_readme": "https://raw.githubusercontent.com/ariffazil/arifOS/main/README.md",
    "pypi_json": "https://pypi.org/project/arifos/json",
    "mcp_tools": "https://mcp.arif-fazil.com/mcp",
    "kernel_health": "http://127.0.0.1:8088/health",
    "docs_version": "https://arifos.arif-fazil.com/version",
    "docs_constitution": "https://arifos.arif-fazil.com/constitution.json",
}

# ── Canon floor types for validation ──────────────────────────────────────
EXPECTED_FLOORS = {
    "F1": "AMANAH",
    "F2": "TRUTH",
    "F3": "TRI-WITNESS",
    "F4": "CLARITY",
    "F5": "PEACE²",
    "F6": "EMPATHY",
    "F7": "HUMILITY",
    "F8": "GENIUS",
    "F9": "ANTI-HANTU",
    "F10": "ONTOLOGY",
    "F11": "AUDITABILITY",
    "F12": "RESILIENCE",
    "F13": "SOVEREIGN",
}
EXPECTED_TOOL_COUNT = 8  # Zen-8 canonical kernel verbs
EXPECTED_ORGANS = 7  # arifOS, A-FORGE, AAA, GEOX, WEALTH, WELL, HERMES
EXPECTED_PORTS = {8088, 7071, 3001, 8081, 18082, 18083}


# ═══════════════════════════════════════════════════════════════════════════
# 1. CANON PARSER — read the 13 sealed files + FLOOR_TABLE.json
# ═══════════════════════════════════════════════════════════════════════════


def parse_canon_frontmatter(filepath: Path) -> dict[str, str]:
    """Extract YAML-style frontmatter from a canon markdown file."""
    meta = {}
    if not filepath.exists():
        return meta
    text = filepath.read_text()
    in_front = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped == "---":
            if not in_front:
                in_front = True
            else:
                break
        elif in_front and ":" in stripped:
            key, _, val = stripped.partition(":")
            meta[key.strip()] = val.strip()
    return meta


def load_canon_index() -> dict[str, Any]:
    """Load all 13 canon files and build the truth table."""
    canon_files = sorted(CANON_DIR.glob("*.md"))
    index: dict[str, Any] = {
        "spec_version": SPEC_VERSION,
        "bundle": "CANON_APEX_V2",
        "file_count": len(canon_files),
        "files": [],
        "floor_names": {},
        "tool_names": [],
    }
    for fp in canon_files:
        meta = parse_canon_frontmatter(fp)
        index["files"].append(
            {
                "filename": fp.name,
                "canon_id": meta.get("canon_id", ""),
                "version": meta.get("version", ""),
                "status": meta.get("status", ""),
                "sha256": hashlib.sha256(fp.read_bytes()).hexdigest()[:16] + "...",
            }
        )
    return index


def load_floor_table() -> dict[str, Any]:
    """Load FLOOR_TABLE.json as the canonical floor definition."""
    if FLOOR_TABLE_PATH.exists():
        return json.loads(FLOOR_TABLE_PATH.read_text())
    return {"floors": []}


def build_canonical_spec() -> dict[str, Any]:
    """Build the complete canonical spec from sealed files."""
    canon_index = load_canon_index()
    floor_table = load_floor_table()
    return {
        "spec_version": SPEC_VERSION,
        "canon_index": canon_index,
        "floor_table": floor_table,
        "expected": {
            "floor_count": 13,
            "tool_count": EXPECTED_TOOL_COUNT,
            "organ_count": EXPECTED_ORGANS,
            "ports": sorted(EXPECTED_PORTS),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. SURFACE SNAPSHOTTERS
# ═══════════════════════════════════════════════════════════════════════════


def snapshot_github() -> dict[str, Any]:
    """Scrape GitHub README for tool/floor claims."""
    snap = {"surface": "github", "source": SURFACES["github_readme"], "ok": False}
    if not requests:
        snap["error"] = "requests not installed"
        return snap
    try:
        r = requests.get(SURFACES["github_readme"], timeout=15)
        text = r.text
        # Parse floor mentions
        floor_mentions = []
        for fid, fname in EXPECTED_FLOORS.items():
            if fid in text or fname in text:
                floor_mentions.append(fid)
        # Parse tool mentions
        tool_pattern = re.findall(r"`(arif_\w+)`", text)
        snap["data"] = {
            "floors_mentioned": floor_mentions,
            "floor_count": len(floor_mentions),
            "tools_mentioned": list(set(tool_pattern)),
            "tool_count_in_text": len(set(tool_pattern)),
            "readme_bytes": len(text),
        }
        snap["ok"] = True
    except Exception as e:
        snap["error"] = str(e)
    return snap


def snapshot_pypi() -> dict[str, Any]:
    """Fetch PyPI package metadata."""
    snap = {"surface": "pypi", "source": SURFACES["pypi_json"], "ok": False}
    if not requests:
        snap["error"] = "requests not installed"
        return snap
    try:
        r = requests.get(SURFACES["pypi_json"], timeout=15)
        data = r.json()
        info = data.get("info", {})
        desc = info.get("description", "")
        # Count floor mentions in description
        floor_mentions = []
        for fid, fname in EXPECTED_FLOORS.items():
            if fid in desc or fname in desc:
                floor_mentions.append(fid)
        snap["data"] = {
            "version": info.get("version", ""),
            "summary": info.get("summary", ""),
            "floors_mentioned": floor_mentions,
            "floor_count_in_desc": len(floor_mentions),
        }
        snap["ok"] = True
    except Exception as e:
        snap["error"] = str(e)
    return snap


def snapshot_mcp() -> dict[str, Any]:
    """Query MCP gateway for tools/list."""
    snap = {"surface": "mcp", "source": SURFACES["mcp_tools"], "ok": False}
    if not requests:
        snap["error"] = "requests not installed"
        return snap
    try:
        r = requests.post(
            SURFACES["mcp_tools"],
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            timeout=15,
        )
        data = r.json()
        tools = data.get("result", {}).get("tools", [])
        tool_names = [t.get("name", "") for t in tools]
        arif_tools = [n for n in tool_names if n.startswith("arif_")]
        snap["data"] = {
            "total_tools": len(tools),
            "arif_tools": arif_tools,
            "arif_tool_count": len(arif_tools),
            "all_tool_names": tool_names,
        }
        snap["ok"] = True
    except Exception as e:
        snap["error"] = str(e)
    return snap


def snapshot_kernel_health() -> dict[str, Any]:
    """Probe kernel :8088/health for runtime state."""
    snap = {"surface": "kernel", "source": SURFACES["kernel_health"], "ok": False}
    if not requests:
        snap["error"] = "requests not installed"
        return snap
    try:
        r = requests.get(SURFACES["kernel_health"], timeout=10)
        data = r.json()
        thermo = data.get("thermodynamic", {})
        snap["data"] = {
            "verdict": thermo.get("verdict", "UNKNOWN"),
            "floors_active": data.get("floors_active", 0),
            "runtime_drift": data.get("runtime_drift", None),
            "tools_loaded": data.get("tools_loaded", 0),
            "vault999_health": data.get("vault999_health", "UNKNOWN"),
            "identity_hash": data.get("identity_hash", {}).get("b3_prefix", "UNKNOWN"),
        }
        snap["ok"] = True
    except Exception as e:
        snap["error"] = str(e)
    return snap


def snapshot_docs() -> dict[str, Any]:
    """Fetch constitution.json and version from docs surface."""
    snap = {"surface": "docs", "ok": False}
    results = {}
    if not requests:
        snap["error"] = "requests not installed"
        return snap
    try:
        r = requests.get(SURFACES["docs_constitution"], timeout=10)
        if r.ok:
            data = r.json()
            floors = data.get("floors", [])
            results["constitution_floors"] = len(floors)
            results["floor_names"] = [f.get("name", "") for f in floors]
    except Exception:
        pass
    try:
        r = requests.get(SURFACES["docs_version"], timeout=10)
        if r.ok:
            data = r.json()
            results["version"] = data.get("release_id", data.get("version", ""))
    except Exception:
        pass
    snap["data"] = results
    snap["ok"] = bool(results)
    return snap


# ═══════════════════════════════════════════════════════════════════════════
# 3. DRIFT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════


def detect_tool_drift(spec: dict, snap: dict) -> list[dict]:
    """Compare MCP tool count/names against canonical spec."""
    drifts = []
    surf = snap.get("data", {})
    if not surf:
        return drifts
    live_count = surf.get("arif_tool_count", surf.get("total_tools", 0))
    live_names = set(surf.get("arif_tools", surf.get("all_tool_names", [])))
    expected = spec["expected"]["tool_count"]

    if live_count != expected:
        drifts.append(
            {
                "dimension": "TOOLS",
                "severity": "HOLD" if abs(live_count - expected) <= 2 else "CAUTION",
                "description": f"MCP tool count mismatch: expected={expected}, live={live_count}",
                "diff": {
                    "expected": expected,
                    "live": live_count,
                    "live_names": sorted(live_names),
                },
            }
        )
    return drifts


def detect_floor_drift(spec: dict, snap: dict, surface: str) -> list[dict]:
    """Compare floor mentions against expected 13."""
    drifts = []
    surf = snap.get("data", {})
    count = surf.get(
        "floor_count",
        surf.get(
            "floor_count_in_desc", surf.get("floors_active", surf.get("constitution_floors", 0))
        ),
    )
    if count and count != 13:
        drifts.append(
            {
                "dimension": "FLOORS",
                "severity": "HOLD" if count >= 10 else "VOID",
                "description": f"{surface}: floor count mismatch: expected=13, live={count}",
                "diff": {"expected": 13, "live": count},
            }
        )
    return drifts


def detect_kernel_drift(spec: dict, snap: dict) -> list[dict]:
    """Detect kernel health anomalies."""
    drifts = []
    surf = snap.get("data", {})
    if not surf:
        return drifts
    verdict = surf.get("verdict", "")
    if verdict == "HOLD":
        drifts.append(
            {
                "dimension": "KERNEL",
                "severity": "HOLD",
                "description": f"Kernel verdict is HOLD — system in guarded state",
                "diff": {"verdict": verdict},
            }
        )
    if surf.get("runtime_drift") is True:
        drifts.append(
            {
                "dimension": "KERNEL",
                "severity": "VOID",
                "description": "Kernel reports runtime_drift=True — source/runtime mismatch",
                "diff": {"runtime_drift": True},
            }
        )
    if surf.get("floors_active", 13) != 13:
        drifts.append(
            {
                "dimension": "FLOORS",
                "severity": "VOID",
                "description": f"Kernel floors_active != 13: {surf.get('floors_active')}",
                "diff": {"expected": 13, "live": surf.get("floors_active")},
            }
        )
    return drifts


def detect_version_drift(spec: dict, snap: dict) -> list[dict]:
    """Check version alignment across surfaces."""
    drifts = []
    surf = snap.get("data", {})
    pypi_ver = surf.get("version", "")
    if pypi_ver and SPEC_VERSION not in pypi_ver:
        drifts.append(
            {
                "dimension": "VERSIONS",
                "severity": "CAUTION",
                "description": f"PyPI version ({pypi_ver}) may not align with spec ({SPEC_VERSION})",
                "diff": {"spec_version": SPEC_VERSION, "pypi_version": pypi_ver},
            }
        )
    return drifts


# ═══════════════════════════════════════════════════════════════════════════
# 4. MAIN
# ═══════════════════════════════════════════════════════════════════════════


def run_monitor(write_supabase: bool = False, alert: bool = False, dry_run: bool = False) -> dict:
    """Execute the full drift monitor cycle."""
    report = {
        "epoch": datetime.now(timezone.utc).isoformat(),
        "spec_version": SPEC_VERSION,
        "snapshots": [],
        "drifts": [],
    }

    # Build canonical spec from sealed files
    spec = build_canonical_spec()
    report["canon"] = {"files": spec["canon_index"]["file_count"], "version": SPEC_VERSION}

    # Snapshot all surfaces
    snapshots = [
        ("github", snapshot_github),
        ("pypi", snapshot_pypi),
        ("mcp", snapshot_mcp),
        ("kernel", snapshot_kernel_health),
        ("docs", snapshot_docs),
    ]

    supabase: Client | None = None
    if write_supabase and SUPABASE_URL and SUPABASE_KEY and create_client:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    for surf_name, snap_func in snapshots:
        if dry_run:
            print(f"[DRY-RUN] Snapshotting {surf_name}...")
        snap = snap_func()
        snap["surface"] = surf_name
        snap["observed_at"] = datetime.now(timezone.utc).isoformat()
        report["snapshots"].append(snap)

        # Detect drift per surface type
        drifts = []
        if surf_name == "mcp":
            drifts = detect_tool_drift(spec, snap)
        elif surf_name in ("github", "pypi", "docs"):
            drifts = detect_floor_drift(spec, snap, surf_name)
            if surf_name == "pypi":
                drifts += detect_version_drift(spec, snap)
        elif surf_name == "kernel":
            drifts = detect_kernel_drift(spec, snap)

        report["drifts"].extend(drifts)

        # Write to Supabase
        if supabase and drifts:
            for d in drifts:
                try:
                    supabase.table("drift_event").insert(
                        {
                            "dimension": d["dimension"],
                            "severity": d["severity"],
                            "description": d["description"],
                            "diff_json": d["diff"],
                            "detected_at": datetime.now(timezone.utc).isoformat(),
                        }
                    ).execute()
                except Exception as e:
                    if not dry_run:
                        print(f"[WARN] Supabase write failed: {e}")

        # Alert on VOID
        void_drifts = [d for d in drifts if d["severity"] == "VOID"]
        if void_drifts and alert:
            print(f"\n🚨 VOID DRIFT DETECTED ({surf_name}):")
            for d in void_drifts:
                print(f"  ▸ {d['dimension']}: {d['description']}")

    report["drift_count"] = len(report["drifts"])
    report["void_count"] = sum(1 for d in report["drifts"] if d["severity"] == "VOID")
    report["hold_count"] = sum(1 for d in report["drifts"] if d["severity"] == "HOLD")
    report["caution_count"] = sum(1 for d in report["drifts"] if d["severity"] == "CAUTION")

    return report


def main():
    parser = argparse.ArgumentParser(description="arifOS Drift Monitor")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing to Supabase")
    parser.add_argument(
        "--supabase-write", action="store_true", help="Write drift events to Supabase"
    )
    parser.add_argument("--alert", action="store_true", help="Print VOID alerts to stdout")
    parser.add_argument("--json", action="store_true", help="Output report as JSON")
    args = parser.parse_args()

    report = run_monitor(
        write_supabase=args.supabase_write,
        alert=args.alert,
        dry_run=args.dry_run,
    )

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(f"\n═══ arifOS Drift Monitor ═══ {SPEC_VERSION} ═══")
        print(f"  Canon files loaded: {report['canon']['files']}")
        print(f"  Snapshots taken:   {len(report['snapshots'])}")
        print(f"  Drifts detected:   {report['drift_count']}")
        print(f"    VOID:  {report['void_count']}")
        print(f"    HOLD:  {report['hold_count']}")
        print(f"    CAUTION: {report['caution_count']}")
        if report["drifts"]:
            print(f"\n  Drift details:")
            for d in report["drifts"]:
                flag = "🚨" if d["severity"] == "VOID" else "⚠️" if d["severity"] == "HOLD" else "ℹ️"
                print(f"  {flag} [{d['severity']}] {d['dimension']}: {d['description']}")
        verdict = (
            "VOID" if report["void_count"] > 0 else "HOLD" if report["hold_count"] > 0 else "SEAL"
        )
        print(f"\n  Monitor verdict: {verdict}")
        print(f"  DITEMPA BUKAN DIBERI\n")

    # Exit non-zero on VOID so CI can block
    if report["void_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
