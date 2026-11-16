#!/usr/bin/env python3
"""live_state_probe.py — one-call wake-up truth table for AAA agents.

Born 2026-11-13: three writers (FI-008, 333-AGI, agy/FI-004) acted on stale
narratives about the same repo in one day — divergent branches, duplicate
releases, an amputated capability. This probe is the antidote:

RULE: run this BEFORE acting on any agent report about repo/release state.
A report that disagrees with this table is an opinion, not a fact.
This probe never gates and never argues — it prints reality, exits 0.
"""
import json, os, subprocess, sys, time, urllib.request

REPO = os.environ.get("ARIFOS_REPO", "/root/arifOS")
TOKEN = "/root/.config/mcp-publisher/token.json"

def row(label, value, state=""):
    icon = {"OK": "OK", "STALE": "~~", "DOWN": "XX"}.get(state, "--")
    print(f"[{icon:^2}] {label:<16} {value}")

def git(*args):
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True,
                          text=True, timeout=15).stdout.strip()

print(f"=== arifOS live state — {time.strftime('%Y-%m-%d %H:%M %Z')} ===")
head = git("rev-parse", "--short=9", "HEAD")
branch = git("branch", "--show-current")
st = git("status", "--porcelain")
row("git HEAD", f"{head} ({branch}) dirty_files={len(st.splitlines()) if st else 0}", "OK")

try:
    d = json.loads(urllib.request.urlopen("http://127.0.0.1:8088/health", timeout=8).read())
    sr = d.get("software_release", {}); cp = sr.get("content_parity", {}); gap = sr.get("repo_gap", {})
    ok = (not sr.get("drift")) and cp.get("state") == "MATCH"
    row("kernel", f"{sr.get('release_id')} drift={sr.get('drift')} parity={cp.get('state')}", "OK" if ok else "STALE")
    print(f"     repo_ahead_of_deployed={gap.get('repo_ahead_of_deployed')} (>0 = commit/deploy out of sync)")
except Exception as e:
    row("kernel :8088", f"unreachable ({type(e).__name__})", "DOWN")
    print("     pre-push guard GATE 1 will FAIL while kernel is down")

try:
    d = json.loads(urllib.request.urlopen("https://pypi.org/pypi/arifos/json", timeout=10).read())
    row("PyPI latest", d["info"]["version"], "OK")
except Exception as e:
    row("PyPI", f"unreachable ({type(e).__name__})", "DOWN")

try:
    d = json.loads(urllib.request.urlopen(
        "https://registry.modelcontextprotocol.io/v0/servers?search=arifos", timeout=10).read())
    best, ts = None, ""
    for srv in d.get("servers", []):
        s = srv.get("server", {})
        m = srv.get("_meta", {}).get("io.modelcontextprotocol.registry/official", {})
        u = m.get("updatedAt", "")
        if u > ts: ts, best = u, (s.get("version"), m.get("status"))
    if best: row("registry", f"v{best[0]} status={best[1]} updated={ts[:16]}", "OK")
    else: row("registry", "no listing found", "DOWN")
except Exception as e:
    row("registry", f"unreachable ({type(e).__name__})", "DOWN")

try:
    age_h = (time.time() - os.path.getmtime(TOKEN)) / 3600
    row("registry token", f"age {age_h:.1f}h", "OK" if age_h < 168 else "STALE (re-login before publishing)")
except OSError:
    row("registry token", "missing", "DOWN")

print("=== probe != gate: reality only. A report contradicting a line above loses. ===")
sys.exit(0)
