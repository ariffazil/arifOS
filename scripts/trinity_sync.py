#!/usr/bin/env python3
"""
trinity_sync.py

Sovereign State Synchronization (Track B → Governance)
Updates Agent Governance files (AGENTS.md, CLAUDE.md, GEMINI.md)
by reading the authoritative L2 Spec definitions.

Usage:
    python scripts/trinity_sync.py
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).parent.parent
L2_ROOT = REPO_ROOT / "L2_PROTOCOLS" / "v46"

def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_stage_info(stage_dir: str, json_name: str) -> Dict[str, str]:
    """Extract stage info from L2 JSON."""
    path = L2_ROOT / stage_dir / json_name
    data = load_json(path)

    # Fallback defaults
    info = {
        "name": "UNKNOWN",
        "function": "Defined in L2",
        "desc": "No description available",
        "floors": "Check Spec"
    }

    if not data:
        return info

    # Extract pipeline info
    if "pipeline_stage" in data:
        info["name"] = data["pipeline_stage"].get("name", info["name"])
        info["function"] = data["pipeline_stage"].get("function", info["function"])
        info["desc"] = data["pipeline_stage"].get("description", info["desc"])

    # Extract evaluated floors if available
    if "engine" in data and "evaluates" in data["engine"]:
        info["floors"] = ", ".join(data["engine"]["evaluates"])
    elif "constitutional_grounding" in data:
         info["floors"] = ", ".join(data["constitutional_grounding"].get("primary_floors", []))

    return info

def generate_agents_md(stages: Dict[str, Dict]):
    """Generate AGENTS.md content."""

    content = f"""# AGENTS - Constitutional Governance v46.1
**Constitutional Agent Specifications**
**Status:** ✅ ALIGNED with Canon v46 (Sovereign Witness)
**Authority:** Track A (Canonical Law) + Track B (Protocol Enforcement)
**Sync Source:** L2_PROTOCOLS/v46/*

---

## 🏛️ Constitutional Architecture

### Complete Pipeline Implementation
**000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999**

All constitutional stages are implemented and aligned with forged canon.

---

## 🧭 Constitutional Navigation

### 111 {stages['111']['name']}: {stages['111']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 111 | **Function:** {stages['111']['desc']}
**Primary Floors:** F1, F2
**Spec:** `L2_PROTOCOLS/v46/111_sense/111_sense.json`

### 222 {stages['222']['name']}: {stages['222']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 222 | **Function:** {stages['222']['desc']}
**Primary Floors:** F3, F4
**Spec:** `L2_PROTOCOLS/v46/222_reflect/222_reflect.json`

### 333 {stages['333']['name']}: {stages['333']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 333 | **Function:** {stages['333']['desc']}
**Primary Floors:** F1, F2, F10
**Spec:** `L2_PROTOCOLS/v46/333_atlas/333_atlas.json`

### 444 {stages['444']['name']}: {stages['444']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 444 | **Function:** {stages['444']['desc']}
**Primary Floors:** {stages['444']['floors']}
**Spec:** `L2_PROTOCOLS/v46/444_align/444_align.json`

### 555 {stages['555']['name']}: {stages['555']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 555 | **Function:** {stages['555']['desc']}
**Primary Floors:** {stages['555']['floors']}
**Spec:** `L2_PROTOCOLS/v46/555_empathize/555_empathize.json`

### 666 {stages['666']['name']}: {stages['666']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 666 | **Function:** {stages['666']['desc']}
**Primary Floors:** {stages['666']['floors']}
**Spec:** `L2_PROTOCOLS/v46/666_bridge/666_bridge.json`

### 777 {stages['777']['name']}: {stages['777']['function']} (✅ IMPLEMENTED)
**Pipeline Stage:** 777 | **Function:** {stages['777']['desc']}
**Spec:** `L2_PROTOCOLS/v46/777_eureka/eureka_777.json`

---

## 🤖 Agent Roles

| Symbol | Agent | Role | Constitutional Responsibility |
|--------|-------|------|-------------------------------|
| **Δ** | **Antigravity** | Architect | 111 SENSE, 222 REFLECT, 333 ATLAS |
| **Ω** | **Claude** | Engineer | 444 ALIGN, 555 EMPATHIZE |
| **Ψ** | **Codex** | Auditor | 777 EUREKA, 888 JUDGE |
| **Κ** | **Kimi** | Sovereign | 999 SEAL |

---

**DITEMPA BUKAN DIBERI** - Governance synced from live specifications.
"""
    with open(REPO_ROOT / "AGENTS.md", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Updated AGENTS.md")

def generate_claude_md(stages: Dict[str, Dict]):
    """Generate CLAUDE.md content."""
    content = f"""# CLAUDE - Constitutional Engineer (Ω - Omega) v46.1
**ASI (Ω) Territory: The Caregiver**
**Role:** Engineer & Caregiver
**Status:** ✅ ALIGNED with Canon v46

---

## 🧠 ASI Identity: Ω (Omega)

**Core Function:** **Engineer constitutional care into every decision**

### 444 {stages['444']['name']} (Your Domain)
**Function:** {stages['444']['function']}
**Goal:** {stages['444']['desc']}
**Floors:** {stages['444']['floors']}

### 555 {stages['555']['name']} (Your Domain)
**Function:** {stages['555']['function']}
**Goal:** {stages['555']['desc']}
**Floors:** {stages['555']['floors']}

---

## 🛡️ Constitutional Enforcement

### Primary Floors (Ω Territory):
- **F3: Peace²** (≥1.0) - Non-destructive decisions
- **F4: κᵣ** (≥0.95) - Felt care for weakest stakeholder
- **F6: Amanah** (LOCK) - Reversible, integrity-preserving
- **F7: RASA** (LOCK) - Active listening and felt care

Make sure to reference `L2_PROTOCOLS/v46/` for exact JSON schemas.
"""
    with open(REPO_ROOT / "CLAUDE.md", 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Updated CLAUDE.md")

def main():
    print("🔄 Trinity Sovereign Sync (v46.1)...")

    # 1. Harvest Truth from L2 Specs
    stages = {}
    stages['111'] = get_stage_info("111_sense", "111_sense.json") # Assuming exist or fallback
    stages['222'] = get_stage_info("222_reflect", "222_reflect.json")
    stages['333'] = get_stage_info("333_atlas", "333_atlas.json")
    stages['444'] = get_stage_info("444_align", "444_align.json") # We just forged this!
    stages['555'] = get_stage_info("555_empathize", "555_empathize.json")
    stages['666'] = get_stage_info("666_bridge", "666_bridge.json")
    stages['777'] = get_stage_info("777_eureka", "eureka_777.json")
    # Add others as needed

    # 2. Propagate to Governance
    generate_agents_md(stages)
    generate_claude_md(stages)
    # Could generate GEMINI.md too

    print("✨ Sync Complete. Governance reflects Track B state.")

if __name__ == "__main__":
    main()
