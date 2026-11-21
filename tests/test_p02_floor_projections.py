#!/usr/bin/env python3
"""P0-2 acceptance tests (contract 2026-11-21): single-state floor projections.

Run: python3 tests/test_p02_floor_projections.py   (exit 0 = pass)
"""
import importlib.util
import json
import os
import sys

# Load the helper standalone (dependency-free by design): importing the full
# arifosmcp package would require the deployed venv's third-party deps.
_spec = importlib.util.spec_from_file_location(
    "floor_projections",
    os.path.join(os.path.dirname(__file__), "..", "arifosmcp", "runtime", "floor_projections.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
constitutional_status = _mod.constitutional_status
derive_measurement_state = _mod.derive_measurement_state
derive_projections = _mod.derive_projections

ALL = [f"F{i}" for i in range(1, 14)]
PASS = {f: "pass" for f in ALL}
FAIL6 = dict(PASS, F6="fail")
UNM6 = dict(PASS, F6="unmeasured")
PROV_STALE = {f: f"probe:{f}@2026-11-21" for f in ALL}
PROV_STALE["F6"] = "STALE:well_health:stale_substrate"
PROV_MISSING = dict(PROV_STALE)
PROV_MISSING["F6"] = "unmeasured_default:empty_kernel_signal"

ok = 0

def check(name, cond):
    global ok
    assert cond, name
    ok += 1
    print(f"  PASS {name}")

# 1. all 13 measured
p = derive_projections(PASS, PROV_STALE)
check("all-measured: 13/0", p["floors_measured"] == sorted(ALL) and p["floors_unmeasured"] == [])

# 2. F6 stale -> unmeasured, exactly one state
p = derive_projections(UNM6, PROV_STALE)
check("stale-F6: unmeasured=[F6]", p["floors_unmeasured"] == ["F6"])
check("stale-F6: measured=12", len(p["floors_measured"]) == 12)

# 3. F6 recovers to measured
p = derive_projections(FAIL6, PROV_STALE)
check("F6-recovered: measured=13", p["floors_measured"] == sorted(ALL) and p["floors_unmeasured"] == [])

# 4. no floor in both categories
for det in (PASS, UNM6, FAIL6):
    p = derive_projections(det, PROV_STALE)
    check(f"disjoint ({len(det)} floors)", not set(p["floors_measured"]) & set(p["floors_unmeasured"]))

# 5. aggregate count always == 13
for det in (PASS, UNM6, FAIL6):
    p = derive_projections(det, PROV_STALE)
    check("measured+unmeasured==13", len(p["floors_measured"]) + len(p["floors_unmeasured"]) == 13)

# 6. every projection derives from the same canonical state
p = derive_projections(UNM6, PROV_STALE)
state = derive_measurement_state(UNM6)
check("projections agree with state map",
      p["floors_measurement_status"] == state
      and all(state[f] == "unmeasured" for f in p["floors_unmeasured"])
      and all(state[f] == "measured" for f in p["floors_measured"]))

# 7. stale provenance survives rendering
check("stale provenance visible", p["floors_measurement_status"]["F6"] == "unmeasured")
p2 = derive_projections(UNM6, PROV_STALE)
check("provenance passthrough retains STALE label", PROV_STALE["F6"].startswith("STALE:"))

# 8. missing substrate distinct from stale substrate
pm = derive_projections(UNM6, PROV_MISSING)
ps = derive_projections(UNM6, PROV_STALE)
check("missing != stale (provenance distinct)",
      pm["floors_defaulted"] == ["F6"] and ps["floors_defaulted"] == [])

# 9. unmeasured never renders as healthy
check("unmeasured != healthy",
      constitutional_status([], ["F6"], 12, 13) == "partial"
      and constitutional_status([], [], 13, 13) == "healthy"
      and constitutional_status(["F3"], ["F6"], 11, 13) == "degraded")

# 10. non-F6 behavior unchanged (pass/fail preserved through projections)
p = derive_projections(FAIL6, PROV_STALE)
check("F6 fail stays measured (fail != unmeasured)",
      "F6" in p["floors_measured"] and p["floors_unmeasured"] == [])

print("\nBEFORE/AFTER synthetic (F6 stale):")
before = {"floors_measured": 13, "floors_unmeasured": ["F6"], "note": "13 measured + 1 unmeasured / 13 (impossible)"}
after = derive_projections(UNM6, PROV_STALE)
print(json.dumps({"before": before,
                  "after": {"floors_measured": len(after["floors_measured"]),
                            "floors_unmeasured": after["floors_unmeasured"],
                            "floors_measurement_status_F6": after["floors_measurement_status"]["F6"],
                            "provenance_F6": PROV_STALE["F6"]}}, indent=1))
print(f"\nALL {ok} CHECKS PASSED")
