#!/usr/bin/env python3
"""gen_surface_evidence.py — Step 1 deterministic evidence capture (A1/A2, read-only).

Produces surface-evidence.json: the pre-mutation witness for the surface-drift fix.
Verifies stated facts at source level BEFORE any live-file regeneration.
Read-only. Deterministic. Re-runnable.
"""

from __future__ import annotations
import json, hashlib, os, sys, datetime

ROOT = "/root/arifOS"
SOT = os.path.join(ROOT, "kernel-sot.yaml")
ABI = os.path.join(ROOT, "arifosmcp/abi/capability_registry.json")
AAA_ABI = "/root/AAA/arifos_kernel/abi/capability_registry.json"
OUT = os.path.join(ROOT, "surface-evidence.json")

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


def sha(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError as e:
        return f"ERR:{e}"


def read_lines(path, start, end):
    try:
        lines = open(path, encoding="utf-8", errors="ignore").read().splitlines()
        return {f"{start}-{end}": lines[start - 1 : end]}
    except Exception as e:
        return {"error": str(e)}


ev = {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}

# ── 1. SOT YAML parse + structural validation ─────────────────────────────────
try:
    import yaml

    with open(SOT) as fh:
        sot = yaml.safe_load(fh)
    caps = sot.get("capabilities", {})
    aliases = sot.get("aliases", {})
    dep = aliases.get("deprecated", {})
    tombs = aliases.get("tombstones", [])
    internal_ex = aliases.get("internal", {}).get("examples", [])

    canon_keys = sorted(caps.keys())
    ev["sot_parse"] = {"ok": True}
    ev["sot_capabilities"] = {
        "count": len(canon_keys),
        "keys": canon_keys,
        "is_exactly_canonical": canon_keys == sorted(CANONICAL),
    }
    ev["sot_aliases"] = {
        "deprecated_count": len(dep),
        "missing_targets": [a for a, t in dep.items() if t not in caps],
        "tombstones": tombs,
        "tombstone_overlap_canonical": [t for t in tombs if t in caps],
        "internal_examples": internal_ex,
        "internal_overlap_canonical": [i for i in internal_ex if i in caps],
    }
    ev["sot_visibility_field"] = {k: ("visibility" in v) for k, v in caps.items()}
except Exception as e:
    ev["sot_parse"] = {"ok": False, "error": str(e)}

# ── 2. capability_registry.json: hash + provider.tool bindings ────────────────
try:
    d = json.load(open(ABI))
    caps_list = d.get("capabilities", [])
    tools = [(c.get("provider") or {}).get("tool") for c in caps_list]
    unique = sorted(set(t for t in tools if t))
    canon = [t for t in unique if t in CANONICAL]
    nounverb = [t for t in unique if t not in CANONICAL and t.startswith("arif_")]
    other = [t for t in unique if not t.startswith("arif_")]
    ev["abi_registry"] = {
        "path": ABI,
        "sha256": sha(ABI),
        "abi_version": d.get("abi_version"),
        "capability_count": len(caps_list),
        "unique_provider_tools": len(unique),
        "provider_tools": unique,
        "canonical_bindings": canon,
        "nounverb_bindings": nounverb,
        "non_arif_bindings": other,
        "drift_count": len(nounverb),
    }
except Exception as e:
    ev["abi_registry"] = {"error": str(e)}

arifos_sha = sha(ABI)
aaa_sha = sha(AAA_ABI)
ev["aaa_abi_registry"] = {
    "path": AAA_ABI,
    "sha256": aaa_sha,
    "byte_equal_to_arifos": (aaa_sha == arifos_sha),
}

# ── 3. cited line verification ────────────────────────────────────────────────
ev["cited_lines"] = {
    "kernel_abi.py:167": read_lines(os.path.join(ROOT, "arifosmcp/abi/kernel_abi.py"), 165, 170),
    "rest_routes.py:6646": read_lines(
        os.path.join(ROOT, "arifosmcp/runtime/rest_routes/rest_routes.py"), 6644, 6655
    ),
    "pre_execution_gate.py:783": read_lines(
        os.path.join(ROOT, "arifosmcp/runtime/pre_execution_gate.py"), 781, 796
    ),
    "tools.py:1154": read_lines(os.path.join(ROOT, "arifosmcp/runtime/tools.py"), 1150, 1170),
    "interceptor.py:298": read_lines(
        os.path.join(ROOT, "arifosmcp/kernel/interceptor.py"), 296, 302
    ),
}

# ── 4. handler path existence (SOT handler fields) ────────────────────────────
handlers = {
    "tool_01_init_anchor.py": "arifosmcp/runtime/megaTools/tool_01_init_anchor.py",
    "tool_13_arif_memory.py": "arifosmcp/runtime/megaTools/tool_13_arif_memory.py",
    "tools.py": "arifosmcp/runtime/tools.py",
    "router.py": "arifosmcp/router.py",
}
ev["handlers_exist"] = {k: os.path.exists(os.path.join(ROOT, p)) for k, p in handlers.items()}

with open(OUT, "w") as fh:
    json.dump(ev, fh, indent=2, sort_keys=True)

print(json.dumps(ev, indent=2))
