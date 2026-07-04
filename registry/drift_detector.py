#!/usr/bin/env python3
"""Drift Detector for the 9 Canonical Registries."""
import os, json, hashlib, sys
from pathlib import Path
from datetime import datetime

REGISTRY_DIR = Path("/root/arifOS/registry")
REPORT_DIR = Path("/root/forge_work/2026-07-04")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk: break
            h.update(chunk)
    return h.hexdigest()

def check_yaml_exist():
    checks = []
    expected = ["01-constitution.yaml","02-identity.yaml","03-tools.yaml","04-scars.yaml",
                "05-models.yaml","06-philosophy.yaml","07-memory.yaml","08-vault.yaml","09-witness.yaml"]
    for f in expected:
        p = REGISTRY_DIR / f
        if p.exists():
            checks.append(("PASS", f"{f} ({p.stat().st_size} bytes)"))
        else:
            checks.append(("VOID", f"{f} MISSING"))
    return checks

def check_01():
    checks = []
    c = Path("/root/arifOS/static/constitution.json")
    if c.exists():
        with open(c) as f: d = json.load(f)
        floors = d.get("floors",[])
        if len(floors)==13: checks.append(("PASS",f"F1-F13: {len(floors)} floors"))
        else: checks.append(("DRIFT",f"Expected 13 floors, found {len(floors)}"))
    else: checks.append(("VOID","constitution.json MISSING"))
    k = Path("/root/VAULT999/kernel/ARIFOS_KERNEL.invariant.v1.0.yaml")
    checks.append(("PASS" if k.exists() else "DRIFT", "Kernel invariants"))
    return checks

def check_02():
    checks = []
    r = Path("/root/AAA/registries/AAA_AGENTS_REGISTRY.json")
    if r.exists():
        with open(r) as f: d = json.load(f)
        n = len(d.get("agents",[]))
        if n>=20: checks.append(("PASS",f"Agent registry: {n} agents"))
        else: checks.append(("DRIFT",f"Expected 20+ agents, found {n}"))
    else: checks.append(("VOID","AAA_AGENTS_REGISTRY.json MISSING"))
    s = Path("/root/arifOS/static/soul.json")
    checks.append(("PASS" if s.exists() else "DRIFT", "Sovereign soul.json"))
    return checks

def check_03():
    checks = []
    t = Path("/root/AAA/docs/TOOLREGISTRY.json")
    if t.exists():
        with open(t) as f: d = json.load(f)
        checks.append(("PASS",f"TOOLREGISTRY: {len(d.get('skills',[]))} skills"))
    else: checks.append(("VOID","TOOLREGISTRY.json MISSING"))
    return checks

def check_04():
    checks = []
    s = Path("/root/arifOS/static/scar.json")
    if s.exists():
        with open(s) as f: d = json.load(f)
        checks.append(("PASS",f"Scar definitions: {len(d)} types"))
    else: checks.append(("VOID","scar.json MISSING"))
    v = Path("/root/VAULT999/scars")
    checks.append(("PASS" if v.exists() else "DRIFT", f"VAULT999/scars: {len(list(v.iterdir())) if v.exists() else 0} batches"))
    c = Path("/root/arifOS/VAULT999/cooling")
    checks.append(("PASS" if c.exists() else "DRIFT", "Cooling ledger"))
    return checks

def check_05():
    checks = []
    m = Path("/root/arifOS/arifosmcp/config/model_registry.json")
    if m.exists():
        with open(m) as f: d = json.load(f)
        models = d.get("models",[])
        checks.append(("PASS",f"Model registry: {len(models)} models"))
        all_forbidden = all(m.get("forbidden") for m in models if isinstance(m,dict))
        checks.append(("PASS" if all_forbidden else "DRIFT", "Forbidden actions declared"))
    else: checks.append(("VOID","model_registry.json MISSING"))
    return checks

def check_06():
    checks = []
    u = Path("/root/arifOS/data/unified_quotes_registry.json")
    if u.exists():
        with open(u) as f: d = json.load(f)
        checks.append(("PASS",f"Unified quotes: {len(d.get('quotes',[]))} quotes, v{d.get('version','?')}"))
    else: checks.append(("VOID","unified_quotes_registry.json MISSING"))
    p = Path("/root/arifOS/data/philosophy_registry_v1.json")
    if p.exists():
        with open(p) as f: d = json.load(f)
        checks.append(("PASS",f"Philosophy v1: {len(d.get('quotes',[]))} quotes"))
    else: checks.append(("DRIFT","philosophy_registry_v1.json MISSING"))
    return checks

def check_07():
    checks = []
    m = Path("/root/arifOS/memory")
    checks.append(("PASS" if m.exists() else "VOID", f"arifOS memory: {len(list(m.glob('*.md')))} files" if m.exists() else "MISSING"))
    r = Path("/root/memory")
    checks.append(("PASS" if r.exists() else "DRIFT", f"Root memory: {len(list(r.glob('*.md')))} files" if r.exists() else "MISSING"))
    t = Path("/root/AAA/VAULT999/tree777/tree777_anchors.jsonl")
    checks.append(("PASS" if t.exists() else "DRIFT", "TREE777 anchors"))
    return checks

def check_08():
    checks = []
    v = Path("/root/VAULT999")
    if v.exists():
        subdirs = [d for d in v.iterdir() if d.is_dir()]
        checks.append(("PASS",f"VAULT999: {len(subdirs)} subdirs"))
    else: checks.append(("VOID","VAULT999 MISSING"))
    k = Path("/root/VAULT999/kernel/ARIFOS_KERNEL.invariant.v1.0.yaml")
    checks.append(("PASS" if k.exists() else "VOID", "Kernel invariants"))
    m = Path("/root/VAULT999/registry/999_master.log")
    checks.append(("PASS" if m.exists() else "DRIFT", "Master log"))
    return checks

def check_09():
    checks = []
    w = Path("/root/VAULT999/witness")
    if w.exists():
        checks.append(("PASS",f"Witness records: {len(list(w.iterdir()))} files"))
    else: checks.append(("VOID","VAULT999/witness/ MISSING"))
    p = Path("/root/arifOS/arifosmcp/runtime/witness_packet.py")
    checks.append(("PASS" if p.exists() else "DRIFT", "WitnessPacket code"))
    c = Path("/root/arifOS/arifosmcp/transport/conformance_spine.py")
    checks.append(("PASS" if c.exists() else "DRIFT", "Conformance spine"))
    return checks

def main():
    print("="*70)
    print("  9 CANONICAL REGISTRIES - DRIFT DETECTION REPORT")
    print(f"  Date: {datetime.utcnow().isoformat()}Z")
    print("="*70)
    print()
    all_checks = []
    print("CHECK 0: All 9 YAML files exist")
    print("-"*40)
    for s,m in check_yaml_exist():
        print(f"  [{'OK' if s=='PASS' else '!' if s=='DRIFT' else 'X'}] {m}")
        all_checks.append((s,m))
    print()
    for name,checker in [("01-CONSTITUTION",check_01),("02-IDENTITY",check_02),("03-TOOLS",check_03),
                         ("04-SCARS",check_04),("05-MODELS",check_05),("06-PHILOSOPHY",check_06),
                         ("07-MEMORY",check_07),("08-VAULT",check_08),("09-WITNESS",check_09)]:
        print(f"CHECK {name}")
        print("-"*40)
        for s,m in checker():
            print(f"  [{'OK' if s=='PASS' else '!' if s=='DRIFT' else 'X'}] {m}")
            all_checks.append((s,m))
        print()
    p = sum(1 for s,_ in all_checks if s=="PASS")
    d = sum(1 for s,_ in all_checks if s=="DRIFT")
    v = sum(1 for s,_ in all_checks if s=="VOID")
    t = len(all_checks)
    print("="*70)
    print(f"  SUMMARY: {p} PASS | {d} DRIFT | {v} VOID | {t} TOTAL")
    verdict = "VOID" if v>0 else ("DRIFT" if d>0 else "PASS")
    print(f"  VERDICT: {verdict}")
    print("="*70)
    REPORT_DIR.mkdir(parents=True,exist_ok=True)
    with open(REPORT_DIR/"drift-report.json","w") as f:
        json.dump({"timestamp":datetime.utcnow().isoformat()+"Z","pass":p,"drift":d,"void":v,"verdict":verdict,
                   "checks":[{"status":s,"message":m} for s,m in all_checks]},f,indent=2)
    print(f"\n  Report: {REPORT_DIR/'drift-report.json'}")
    return 1 if (v>0 or d>0) else 0

if __name__=="__main__":
    sys.exit(main())
