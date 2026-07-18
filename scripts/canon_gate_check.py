#!/usr/bin/env python3
"""Canon gate: no tool surface drift. Count ABI, capability, policy, surface — all must equal 8.
Exit 0 = pass, exit 1 = fail."""
import json, subprocess, sys
from pathlib import Path

ABI_DIR = Path("/opt/arifos/app/arifosmcp/abi")
EXPECTED = 8
EXCLUDED = {"arif_vault_verify"}

# 1. capability_registry.json
with open(ABI_DIR / "capability_registry.json") as f:
    cr = json.load(f)
cr_ids = [c["capability_id"] for c in cr["capabilities"]]
cr_ok = len(cr_ids) == EXPECTED and "vault.verify" not in cr_ids

# 2. policy_registry.json — public_agent profile
with open(ABI_DIR / "policy_registry.json") as f:
    pr = json.load(f)
pa_caps = pr["profiles"]["public_agent"]["capabilities"]
pa_ok = len(pa_caps) == EXPECTED and "vault.verify" not in pa_caps

# 3. Live tools/list (if server is up)
try:
    import httpx
    r = httpx.post("http://localhost:8088/mcp", json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/list"
    }, headers={"Content-Type": "application/json", "Accept": "application/json"}, timeout=3.0)
    tools = r.json().get("result", {}).get("tools", [])
    tool_names = [t["name"] for t in tools]
    surface_ok = len(tool_names) == EXPECTED and not EXCLUDED.intersection(tool_names)
except Exception:
    tool_names = []
    surface_ok = False

# Report
print(f"capability_registry: {len(cr_ids)} {'✅' if cr_ok else '❌'}")
print(f"policy_public_agent: {len(pa_caps)} {'✅' if pa_ok else '❌'}")
print(f"tools/list:          {len(tool_names)} {'✅' if surface_ok else '❌'}")

if cr_ok and pa_ok and surface_ok:
    print(f"\n✅ CANON GATE PASS: all three = {EXPECTED}")
    sys.exit(0)
else:
    print(f"\n❌ CANON GATE FAIL")
    sys.exit(1)
