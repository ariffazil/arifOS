#!/usr/bin/env python3
"""deployment_boundary_closure.py — ARIFOS::DEPLOYMENT_BOUNDARY_CLOSURE::v1
AUTHORITY: ARIF · MODE: OBSERVE_ONLY · NO mutation/deploy/restart/delete/seal.

Deterministic, re-runnable evidence collector. Emits 5 machine-verifiable outputs:
  1. import-origin-report.json
  2. execution-roots-report.json
  3. package-origin-report.json
  4. runtime-attestation-gap-report.json
  5. release-closure-plan.md
Plus automatic findings (ONE_ORIGIN_RULE_VIOLATION / IMPORT_SHADOW_RISK /
EDITABLE_INSTALL_DRIFT / PACKAGE_MULTIPLICITY) and a final verdict.
"""

from __future__ import annotations
import json, os, re, subprocess, datetime, hashlib

ROOT = "/root/arifOS"
HEALTH = "http://127.0.0.1:8088/health"
PID = 2610307
SP = "/opt/arifos/venv/lib/python3.13/site-packages"
CANONICAL = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_forge",
    "arif_seal",
]
TS = datetime.datetime.now(datetime.timezone.utc).isoformat()


def fetch_health():
    out = subprocess.run(["curl", "-sf", HEALTH], capture_output=True, text=True, timeout=20)
    return json.loads(out.stdout) if out.returncode == 0 else None


def read_proc_env(pid):
    try:
        raw = open(f"/proc/{pid}/environ", "rb").read()
        env = {}
        for kv in raw.split(b"\0"):
            if b"=" in kv:
                k, v = kv.split(b"=", 1)
                env[k.decode()] = v.decode()
        return env
    except Exception as e:
        return {"_error": str(e)}


def sha_file(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError:
        return None


def grep(pattern, base, kinds=(".py",)):
    hits = []
    for dp, dn, fn in os.walk(base):
        dn[:] = [
            d for d in dn if d not in {".venv", "build", "node_modules", "__pycache__", ".git"}
        ]
        for f in fn:
            if not f.endswith(kinds):
                continue
            p = os.path.join(dp, f)
            try:
                text = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if re.search(pattern, line):
                    hits.append(f"{os.path.relpath(p, base)}:{i}:{line.strip()[:120]}")
    return hits


# ── A. Runtime import identity ──────────────────────────────────────────────
def section_a(h):
    rip = h.get("runtime_import_path", "")
    if rip.startswith("/opt/arifos/current/venv"):
        cls = "WHEEL_ORIGIN"
    elif rip.startswith("/opt/arifos/app"):
        cls = "REPO_COPY_ORIGIN"
    elif rip.startswith("/root/arifOS") or "editable" in rip:
        cls = "DEV_ORIGIN"
    else:
        cls = "UNKNOWN"
    return {
        "captured_at": TS,
        "service_pid": h.get("software_release", {}).get("service_pid"),
        "runtime_import_path": rip,
        "runtime_path": h.get("runtime_path"),
        "deployment_source": h.get("deployment_source"),
        "deployment_marker": h.get("deployment_marker"),
        "deployment_marker_exists": h.get("deployment_marker_exists"),
        "build_commit": h.get("build_commit"),
        "live_commit": h.get("live_commit"),
        "runtime_matches_build": h.get("runtime_matches_build"),
        "registry_truth": h.get("registry_truth"),
        "active_sot": h.get("active_sot"),
        "runtime_drift": h.get("runtime_drift"),
        "deployment_drift_status": h.get("deployment_drift_status"),
        "expected_origin_prefix": "/opt/arifos/current/venv/",
        "classification": cls,
    }


# ── B. Resolver surface ─────────────────────────────────────────────────────
def section_b(env):
    pth_files, dist_infos, editable = [], [], []
    if os.path.isdir(SP):
        for f in os.listdir(SP):
            if f.endswith(".dist-info"):
                dist_infos.append(f)
            if f.endswith(".pth") or f.endswith(".egg-link") or f.startswith("__editable__"):
                pth_files.append(os.path.join(SP, f))
    for p in pth_files:
        try:
            c = open(p, encoding="utf-8", errors="ignore").read()
            editable.append({"path": p, "content": c[:200]})
        except OSError:
            pass
    return {
        "PYTHONPATH": env.get("PYTHONPATH"),
        "PYTHONNOUSERSITE": env.get("PYTHONNOUSERSITE"),
        "PWD": env.get("PWD"),
        "site_packages": SP,
        "pth_files": pth_files,
        "dist_info_generations": dist_infos,
        "editable_registrations": editable,
        "physical_packages": [
            d for d in ("arifos", "arifosmcp") if os.path.isdir(os.path.join(SP, d))
        ],
        "package_shadowing": bool(
            env.get("PYTHONPATH") and env.get("PYTHONPATH").startswith("/opt/arifos/app")
        ),
        "editable_drift": bool(editable),
        "package_multiplicity": len([d for d in dist_infos if d.startswith("arifos-")]),
    }


# ── C. Execution roots ──────────────────────────────────────────────────────
def classify_root(ex):
    if (
        ex.startswith("/opt/arifos/venv/bin")
        and "/opt/arifos/app" not in ex
        and "python -c" not in ex
    ):
        return "AUTHORIZED_RELEASE_ROOT"
    if "/opt/arifos/app" in ex:
        return "REPO_COPY_ROOT"
    if "/root/arifOS" in ex or "/root/AAA" in ex or "/root/scripts" in ex or "/root/.hermes" in ex:
        return "DEVELOPMENT_ROOT"
    return "UNKNOWN_ROOT"


def section_c():
    roots = []
    # systemd
    try:
        out = subprocess.run(
            ["grep", "-rhE", "ExecStart", "/etc/systemd/system/"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        for line in out.stdout.splitlines():
            line = line.strip()
            if re.search(r"arifos|arifosmcp|/root/arifOS|/root/AAA|/root/scripts", line):
                roots.append(
                    {"source": "systemd", "command": line[:300], "class": classify_root(line)}
                )
    except Exception:
        pass
    # cron
    try:
        out = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=15)
        for line in out.stdout.splitlines():
            line = line.strip()
            if (
                line
                and not line.startswith("#")
                and re.search(r"arifos|/root/arifOS|/root/AAA|/root/scripts", line)
            ):
                roots.append(
                    {"source": "cron", "command": line[:300], "class": classify_root(line)}
                )
    except Exception:
        pass
    # console_scripts from pyproject
    try:
        pt = open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
        for m in re.finditer(r"^(\S+)\s*=\s*\"([^\"]+)\"", pt, re.M):
            name, target = m.group(1), m.group(2)
            if "arifos" in name or "arifos" in target:
                roots.append(
                    {
                        "source": "console_script",
                        "command": f"{name} = {target}",
                        "class": "AUTHORIZED_RELEASE_ROOT",
                    }
                )
    except Exception:
        pass
    from collections import Counter

    return {"roots": roots, "class_counts": dict(Counter(r["class"] for r in roots))}


# ── D. Runtime closure test (8 canonical tools x 6 links, best-effort) ──────
def section_d():
    reg = {}
    try:
        d = json.load(open(os.path.join(ROOT, "arifosmcp/abi/capability_registry.json")))
        for c in d.get("capabilities", []):
            t = (c.get("provider") or {}).get("tool")
            if t:
                reg[t] = c
    except Exception:
        pass
    tools_py = open(
        os.path.join(ROOT, "arifosmcp/runtime/tools.py"), encoding="utf-8", errors="ignore"
    ).read()
    gate = open(
        os.path.join(ROOT, "arifosmcp/runtime/pre_execution_gate.py"),
        encoding="utf-8",
        errors="ignore",
    ).read()
    sot = open(os.path.join(ROOT, "tools_sot.yaml"), encoding="utf-8", errors="ignore").read()
    rows = []
    for t in CANONICAL:
        c = reg.get(t, {})
        rows.append(
            {
                "tool": t,
                "registry": "VERIFIED" if t in reg else "NOT_VERIFIED",
                "schema": "VERIFIED"
                if (c.get("input_schema_ref") and c.get("output_schema_ref"))
                else "NOT_VERIFIED",
                "handler": "VERIFIED" if t in tools_py else "NOT_VERIFIED",
                "authorization": "VERIFIED" if t in gate else "NOT_VERIFIED",
                "telemetry": "NOT_VERIFIED",  # requires arifFlow receipt cross-check (not in this pass)
                "documentation": "VERIFIED" if t in sot else "NOT_VERIFIED",
            }
        )
    return {"closure_rows": rows, "all_verified": all(r["registry"] == "VERIFIED" for r in rows)}


# ── E. Attestation gap ──────────────────────────────────────────────────────
def section_e():
    rip_hits = grep(r"runtime_import_path", os.path.join(ROOT, "arifosmcp"))
    drift_hits = grep(
        r"runtime_matches_build|deployment_drift", os.path.join(ROOT, "arifosmcp/runtime")
    )
    linked = any("runtime_import_path" in h and "drift" in h.lower() for h in rip_hits + drift_hits)
    gap = not linked
    return {
        "runtime_import_path_source_hits": rip_hits[:10],
        "drift_logic_source_hits": drift_hits[:10],
        "att_gap_runtime_origin": gap,
        "finding": "ATT_GAP_RUNTIME_ORIGIN" if gap else "attestation-links-runtime-origin",
    }


# ── main ────────────────────────────────────────────────────────────────────
def main():
    h = fetch_health()
    if h is None:
        print("FAIL: could not fetch /health")
        return 1
    env = read_proc_env(PID)
    a, b, c, d, e = section_a(h), section_b(env), section_c(), section_d(), section_e()

    findings = []
    if a["runtime_import_path"].startswith("/opt/arifos/app/"):
        findings.append(
            {
                "id": "ONE_ORIGIN_RULE_VIOLATION",
                "severity": "CRITICAL",
                "evidence": a["runtime_import_path"],
            }
        )
    if env.get("PYTHONPATH", "").startswith("/opt/arifos/app"):
        findings.append(
            {
                "id": "IMPORT_SHADOW_RISK",
                "severity": "CRITICAL",
                "evidence": f"PYTHONPATH={env.get('PYTHONPATH')}",
            }
        )
    if b["editable_drift"]:
        findings.append(
            {
                "id": "EDITABLE_INSTALL_DRIFT",
                "severity": "HIGH",
                "evidence": b["editable_registrations"][:3],
            }
        )
    if b["package_multiplicity"] >= 2:
        findings.append(
            {
                "id": "PACKAGE_MULTIPLICITY",
                "severity": "HIGH",
                "evidence": b["dist_info_generations"],
            }
        )

    verdict = "HOLD"
    report = {
        "reference": "ARIFOS::DEPLOYMENT_BOUNDARY_CLOSURE::v1",
        "mode": "OBSERVE_ONLY",
        "generated_at": TS,
        "service_pid": PID,
        "import_origin": a,
        "resolver_surface": b,
        "execution_roots": c,
        "closure_test": d,
        "attestation_gap": e,
        "findings": findings,
        "verdict": verdict,
    }

    # 1
    json.dump(
        {
            "generated_at": TS,
            "pid": PID,
            **a,
            "findings": [f for f in findings if "ORIGIN" in f["id"] or "SHADOW" in f["id"]],
        },
        open(os.path.join(ROOT, "import-origin-report.json"), "w"),
        indent=2,
        sort_keys=True,
    )
    # 2
    json.dump(
        {"generated_at": TS, **c},
        open(os.path.join(ROOT, "execution-roots-report.json"), "w"),
        indent=2,
        sort_keys=True,
    )
    # 3
    json.dump(
        {"generated_at": TS, **b},
        open(os.path.join(ROOT, "package-origin-report.json"), "w"),
        indent=2,
        sort_keys=True,
    )
    # 4
    json.dump(
        {
            "generated_at": TS,
            **e,
            "runtime_import_path": a["runtime_import_path"],
            "drift_fields_present": a["runtime_drift"] is not None
            or a["deployment_drift_status"] is not None,
        },
        open(os.path.join(ROOT, "runtime-attestation-gap-report.json"), "w"),
        indent=2,
        sort_keys=True,
    )
    # 5
    with open(os.path.join(ROOT, "release-closure-plan.md"), "w") as fh:
        fh.write(render_plan(report))

    print(json.dumps(report, indent=2))
    return 0


def render_plan(r):
    a, f = r["import_origin"], r["findings"]
    return (
        f"""# release-closure-plan.md — ARIFOS::DEPLOYMENT_BOUNDARY_CLOSURE::v1

Generated: {r["generated_at"]} · Mode: OBSERVE_ONLY (no mutation executed)

## Verdict: {r["verdict"]}

## Proven defect
- `runtime_import_path = {a["runtime_import_path"]}` (classification: {a["classification"]})
- Expected: `/opt/arifos/current/venv/...`

## Findings
"""
        + "\n".join(f"- [{x['severity']}] {x['id']}" for x in f)
        + """

## Remediation (F13-gated — NOT executed)
1. `ExecStart` drops `PYTHONPATH=/opt/arifos/app` + `PWD=/opt/arifos/app`; run console script from isolated release venv.
2. Gate `drift`/`runtime_matches_build` on `runtime_import_path.startswith(/opt/arifos/current/venv/)`.
3. Remove editable `.pth` + superseded dist-info; one `arifos` package, one origin.
4. `ProtectHome=yes` as final proof `/root/arifOS` + repo-copy are unreachable.
5. Build clean wheel (exclude archive/00_legacy/experiments/tooling/scripts/tests/*.bak/*.pre-forged*).
6. Staged release → `/opt/arifos/releases/<id>` → `current` symlink → atomic activation → post-start attestation.

## Success condition: plan only. No mutation, restart, deployment, activation, or seal.
"""
    )


if __name__ == "__main__":
    raise SystemExit(main())
