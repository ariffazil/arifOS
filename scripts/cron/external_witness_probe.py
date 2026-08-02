#!/usr/bin/env python3
"""external_witness_probe — F3 TRI-WITNESS
Probes external surfaces for W³ witness channel health.
Forged 2026-08-02 by 333-AGI — anti-behavioral-sink remediation
"""
import json, urllib.request, time, sys
SURFACES = {
    "arifos": "https://arifos.arif-fazil.com/health",
    "geox": "https://geox.arif-fazil.com/health",
    "wealth": "https://wealth.arif-fazil.com/health",
    "well": "https://well.arif-fazil.com/health",
    "vault": "https://arif-fazil.com/999/verify",
}
results = {}
for name, url in SURFACES.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "arifOS-witness-probe/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            results[name] = {"status": resp.status, "healthy": data.get("status") in ("healthy", "ok", "green"), "ts": time.time()}
    except Exception as e:
        results[name] = {"status": 0, "healthy": False, "error": str(e), "ts": time.time()}

healthy = sum(1 for r in results.values() if r["healthy"])
print(f"WITNESS: {healthy}/{len(SURFACES)} surfaces healthy")
for name, r in results.items():
    print(f"  {name}: {'✅' if r['healthy'] else '❌'} ({r['status']})")
sys.exit(0 if healthy >= 3 else 1)
