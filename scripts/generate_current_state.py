#!/usr/bin/env python3
"""
scripts/generate_current_state.py — ONE WITNESS OBJECT, MULTIPLE VIEWS.

Probes the live kernel and generates:
  1. .well-known/current-state.json  — machine state (full provenance)
  2. .well-known/badges/*.json       — shields.io endpoint-badge payloads
  3. README.md generated block       — between GENERATED:CURRENT-STATE markers

Truth model (AGENTIC-README-DOCTRINE v1, rule 3):
  runtime self-measurement ≠ independent audit. Both are rendered, each
  with provenance + date. Never merged, never averaged.

If the kernel is unreachable the block reads UNMEASURED (probe down @ts).
A cached pass is NEVER written (witness-first, same rule as update_readme_sot.py).

Usage:
    python scripts/generate_current_state.py [--dry-run]

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
STATE_DIR = ROOT / ".well-known"
BADGE_DIR = ROOT / ".well-known" / "badges"
HEALTH_URL = "http://127.0.0.1:8088/health"

BEGIN = "<!-- GENERATED:CURRENT-STATE:BEGIN · source: scripts/generate_current_state.py · never hand-edit -->"
END = "<!-- GENERATED:CURRENT-STATE:END -->"

# ── Independent audit snapshot (immutable historical observation) ──────────
# Hand-audited 2026-10-11 by FI-008; claim-level receipts:
# AAA/forge_work/grant-arifos-reality-reforge-2026-10-11/
AUDIT_SNAPSHOT = {
    "date": "2026-10-11",
    "method": "live re-probe by FI-008 + claim-level hand audit",
    "receipts": "AAA/forge_work/grant-arifos-reality-reforge-2026-10-11/",
    "floors_pass": 2,
    "floors_fail": ["F2", "F11", "F12", "F13"],
    # Raw audit key-count from the 2026-10-10 /health map. The map had 16 keys:
    # F1-F9 + L10-L13 (LAW_SPEC_KEYS) + producer-emitted F11-F13. L11/L12/L13
    # are L-prefix aliases of the failing F11/F12/F13, so the distinct floor
    # count is 13: 2 pass + 4 fail + 7 unmeasured. Alias normalisation
    # (_normalize_floors_to_canonical) landed after the audit.
    "floors_unmeasured": 10,
    "floors_unmeasured_distinct": 7,
    "floors_unmeasured_note": "raw key-count 10 includes L11/L12/L13, L-prefix aliases of the failing F11/F12/F13",
    "actor_binding": "not verified (observed calls unsigned)",
    "receipt_fidelity": "broken on invocation-telemetry surface (HOLD persisted as ok:true)",
    "sink_agreement": "one event: ledger ok:false, organ counters omit it",
    "independent_reconstruction": "no external verifier bound",
}


def probe_health() -> dict | None:
    try:
        return httpx.get(HEALTH_URL, timeout=5).json()
    except Exception:
        return None


def build_state(health: dict | None) -> dict:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    if health is None:
        return {
            "generated_at": now,
            "self_measurement": {
                "status": "UNMEASURED",
                "note": f"kernel probe down @{now} — no cached value written",
            },
            "independent_audit": AUDIT_SNAPSHOT,
        }
    con = health.get("layer_health", {}).get("constitutional", {})
    reg = health.get("layer_health", {}).get("registry", {})
    rel = health.get("software_release", {}) or {}
    self_m = {
        "status": health.get("status", "unknown"),
        "probe": f"{HEALTH_URL} @{now}",
        "floors_pass": con.get("floors_pass"),
        "floors_target": con.get("floors_target"),
        "floors_failing": con.get("floors_failing", []),
        "floors_unmeasured": con.get("floors_unmeasured", []),
        "floors_provenance": con.get("floors_provenance", {}),
        "vault999": con.get("vault999"),
        "release_id": rel.get("release_id"),
        "source_commit": rel.get("source_commit"),
        "drift": rel.get("drift"),
        "tools_exposed": reg.get("exposed_tools"),
        "registry_size": reg.get("registry_size"),
    }
    return {"generated_at": now, "self_measurement": self_m, "independent_audit": AUDIT_SNAPSHOT}


def badge(label: str, message: str, color: str) -> dict:
    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


def build_badges(state: dict) -> dict[str, dict]:
    s = state["self_measurement"]
    a = state["independent_audit"]
    _audit_unmeasured = a.get("floors_unmeasured_distinct", a["floors_unmeasured"])
    if s.get("status") == "UNMEASURED":
        floors_msg = (
            f"self: UNMEASURED · audit: {a['floors_pass']} pass/"
            f"{len(a['floors_fail'])} fail/{_audit_unmeasured} unmeasured "
            f"(raw {a['floors_unmeasured']}) @{a['date']}"
        )
        kernel_msg, kernel_color = "probe down", "critical"
    else:
        floors_msg = (
            f"self {s['floors_pass']}/{s['floors_target']} pass"
            f" · audit {a['floors_pass']} pass/{len(a['floors_fail'])} fail/"
            f"{_audit_unmeasured} unmeasured (raw {a['floors_unmeasured']}) @{a['date']}"
        )
        kernel_msg, kernel_color = (
            s.get("status", "unknown"),
            ("brightgreen" if s.get("status") == "healthy" else "orange"),
        )
    return {
        "floors.json": badge(
            "floors", floors_msg, "blue" if s.get("status") != "UNMEASURED" else "red"
        ),
        "kernel.json": badge("kernel", kernel_msg, kernel_color),
        "vault.json": badge(
            "vault999",
            str(s.get("vault999", "UNMEASURED")),
            "brightgreen" if s.get("vault999") == "healthy" else "lightgrey",
        ),
        "actor-binding.json": badge(
            "actor binding", f"audit {a['date']}: {a['actor_binding']}", "red"
        ),
    }


def render_block(state: dict) -> str:
    s = state["self_measurement"]
    a = state["independent_audit"]
    if s.get("status") == "UNMEASURED":
        self_line = f"**Runtime self-measurement:** {s['note']}"
    else:
        self_line = (
            f"**Runtime self-measurement** (`{s['probe']}`): kernel **{s['status']}** · "
            f"floors **{s['floors_pass']}/{s['floors_target']} measured pass**"
            f"{f' · failing: {", ".join(s["floors_failing"])}' if s['floors_failing'] else ''} · "
            f"vault999 {s['vault999']} · release `{s['release_id']}` · "
            f"drift `{'aligned' if s['drift'] is False else 'DRIFT'}`"
            f"{' (source=built=deployed)' if s['drift'] is False else ''} · "
            f"tools exposed {s['tools_exposed']}. Per-floor provenance: `.well-known/current-state.json`."
        )
    _unm_distinct = a.get("floors_unmeasured_distinct", a["floors_unmeasured"])
    _unm_note = a.get("floors_unmeasured_note", "")
    audit_line = (
        f"**Independent audit** ({a['date']}, {a['method']}; receipts: `{a['receipts']}`): "
        f"floors **{a['floors_pass']} pass · fail {', '.join(a['floors_fail'])} · "
        f"{_unm_distinct} unmeasured = 13 distinct**"
        f"{f' ({_unm_note})' if _unm_note else ''} · "
        f"actor binding {a['actor_binding']} · receipt fidelity {a['receipt_fidelity']} · "
        f"independent reconstruction: {a['independent_reconstruction']}."
    )
    return f"""{BEGIN}
> ### ⚠️ Current verified state — generated, never hand-edited
>
> {self_line}
>
> {audit_line}
>
> **These are two different witness objects.** Self-measurement ≠ independent audit;
> unmeasured is not pass. If this block conflicts with the live endpoint, the endpoint
> wins — re-run `python scripts/generate_current_state.py`.
>
> Machine state: [`.well-known/current-state.json`](./.well-known/current-state.json) ·
> Badge feed: [`.well-known/badges/`](./.well-known/badges/) ·
> Known gaps: [What Is Not Yet Proven](#what-is-not-yet-proven)
{END}"""


def patch_readme(block: str, dry_run: bool) -> None:
    if not README.exists():
        print(f"ERROR: {README} not found", file=sys.stderr)
        sys.exit(1)
    content = README.read_text()
    if BEGIN not in content or END not in content:
        print("ERROR: README markers missing — refusing to splice.", file=sys.stderr)
        sys.exit(2)
    head, rest = content.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    new = head + block + tail
    if dry_run:
        print("DRY RUN — README block would be replaced with:\n" + block)
        return
    if new != content:
        README.write_text(new)
        print(f"README block re-stamped @{datetime.now(UTC).strftime('%H:%M:%SZ')}")
    else:
        print("README block already current.")


def main() -> None:
    dry = "--dry-run" in sys.argv
    health = probe_health()
    state = build_state(health)
    STATE_DIR.mkdir(exist_ok=True)
    BADGE_DIR.mkdir(parents=True, exist_ok=True)

    if not dry:
        (STATE_DIR / "current-state.json").write_text(json.dumps(state, indent=2) + "\n")
        for name, payload in build_badges(state).items():
            (BADGE_DIR / name).write_text(json.dumps(payload, indent=2) + "\n")
        index = {
            "generated_at": state["generated_at"],
            "badges": sorted(p.name for p in BADGE_DIR.glob("*.json")),
        }
        (ROOT / ".well-known" / "badges.json").write_text(json.dumps(index, indent=2) + "\n")
        print(f"wrote .well-known/current-state.json + {len(build_badges(state))} badge payloads")
    patch_readme(render_block(state), dry)


if __name__ == "__main__":
    main()
