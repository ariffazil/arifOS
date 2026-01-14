#!/usr/bin/env python3
"""
CRITICAL CONSTITUTIONAL AUDIT: v45 to v46 Migration Verification
MISSION: Ensure ZERO constitutional intelligence is lost during migration
"""

import os
import re
from pathlib import Path

def get_file_content(filepath):
    """Read file content safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR reading {filepath}: {e}"

def audit_structure():
    """Audit both v45 and v46 structures"""
    base_path = Path("L1_THEORY/canon")
    
    # Find all v45 files
    v45_files = []
    v45_locations = [
        base_path / "archive" / "v45",
        base_path / "00_foundation",
        base_path / "01_floors", 
        base_path / "02_actors",
        base_path / "03_runtime",
        base_path / "04_measurement",
        base_path / "05_memory",
        base_path / "06_paradox",
        base_path / "07_safety"
    ]
    
    for location in v45_locations:
        if location.exists():
            for file_path in location.rglob("*v45*"):
                if file_path.is_file():
                    v45_files.append(str(file_path))
    
    # Find all v46 files
    v46_files = []
    v46_locations = [
        base_path / "000_foundation",
        base_path / "111_sense",
        base_path / "222_reflect", 
        base_path / "333_atlas",
        base_path / "444_align",
        base_path / "555_empathize",
        base_path / "666_bridge",
        base_path / "777_eureka",
        base_path / "888_compass",
        base_path / "999_vault"
    ]
    
    for location in v46_locations:
        if location.exists():
            for file_path in location.rglob("*v46*"):
                if file_path.is_file():
                    v46_files.append(str(file_path))
    
    return v45_files, v46_files

def analyze_floor_content():
    """Analyze floor content for constitutional continuity"""
    base_path = Path("L1_THEORY/canon")
    
    # Check v45 floors file
    v45_floors_file = base_path / "01_floors" / "010_CONSTITUTIONAL_FLOORS_F1F9_v45.md"
    v45_content = ""
    if v45_floors_file.exists():
        v45_content = get_file_content(v45_floors_file)
    
    # Check v46 floor files
    v46_floor_files = {
        "F2": base_path / "333_atlas" / "340_TRUTH_F1_v46.md",
        "F6": base_path / "333_atlas" / "350_CLARITY_F2_v46.md",
        "F3": base_path / "444_align" / "420_PEACE_F3_v46.md",
        "F4": base_path / "555_empathize" / "520_EMPATHY_F4_v46.md",
        "F5": base_path / "666_bridge" / "610_HUMILITY_F5_v46.md",
        "F6_Amanah": base_path / "888_compass" / "830_AMANAH_F6_v46.md",
        "F7": base_path / "777_eureka" / "760_RASA_F7_v46.md",
        "F8": base_path / "888_compass" / "840_TRI_WITNESS_F8_v46.md",
        "F9": base_path / "888_compass" / "850_ANTI_HANTU_F9_v46.md",
        "F10": base_path / "888_compass" / "860_SYMBOLIC_GUARD_F10_v46.md",
        "F11": base_path / "888_compass" / "870_COMMAND_AUTH_F11_v46.md",
        "F12": base_path / "888_compass" / "880_INJECTION_DEFENSE_F12_v46.md"
    }
    
    v46_floor_content = {}
    for floor, file_path in v46_floor_files.items():
        if file_path.exists():
            v46_floor_content[floor] = get_file_content(file_path)
        else:
            v46_floor_content[floor] = f"FILE NOT FOUND: {file_path}"
    
    return v45_content, v46_floor_content

def check_critical_principles():
    """Check for critical constitutional principles"""
    base_path = Path("L1_THEORY/canon")
    
    critical_files = {
        "v45_core": base_path / "000_CONSTITUTIONAL_CORE_v45.md",
        "v46_core": base_path / "000_foundation" / "000_CONSTITUTIONAL_CORE_v46.md",
        "v45_master_index": base_path / "_INDEX" / "00_MASTER_INDEX_v45.md",
        "v46_master_index": base_path / "000_MASTER_INDEX_v46.md"
    }
    
    results = {}
    for key, file_path in critical_files.items():
        if file_path.exists():
            content = get_file_content(file_path)
            results[key] = {
                "exists": True,
                "size": len(content),
                "has_floors": bool(re.search(r'F[1-9]|F1[0-2]', content)),
                "has_trinity": bool(re.search(r'AAA|Trinity|ΔΩΨ', content)),
                "has_pipeline": bool(re.search(r'000.*999|pipeline', content, re.IGNORECASE))
            }
        else:
            results[key] = {
                "exists": False,
                "error": f"File not found: {file_path}"
            }
    
    return results

def main():
    """Main audit execution"""
    print("CONSTITUTIONAL AUDIT: v45 to v46 Migration Verification")
    print("=" * 60)
    print()
    
    # Phase 1: File inventory
    print("PHASE 1: File Inventory")
    v45_files, v46_files = audit_structure()
    print(f"v45 files found: {len(v45_files)}")
    print(f"v46 files found: {len(v46_files)}")
    print()
    
    # Phase 2: Critical files check
    print("PHASE 2: Critical Constitutional Files")
    critical_results = check_critical_principles()
    
    for key, result in critical_results.items():
        print(f"{key}:")
        if result["exists"]:
            print(f"  - Size: {result['size']} bytes")
            print(f"  - Has floors: {result['has_floors']}")
            print(f"  - Has Trinity: {result['has_trinity']}")
            print(f"  - Has pipeline: {result['has_pipeline']}")
        else:
            print(f"  - ERROR: {result['error']}")
        print()
    
    # Phase 3: Floor analysis
    print("PHASE 3: Constitutional Floor Analysis")
    v45_floors, v46_floors = analyze_floor_content()
    
    print("v45 Floors Content Summary:")
    if v45_floors:
        floor_matches = re.findall(r'F[1-9]|F1[0-2]', v45_floors)
        print(f"  - Found floors: {set(floor_matches)}")
        print(f"  - Content length: {len(v45_floors)} bytes")
    else:
        print("  - NO V45 FLOORS FILE FOUND")
    
    print("\nv46 Floors Content Summary:")
    for floor, content in v46_floors.items():
        if "FILE NOT FOUND" in content:
            print(f"  - {floor}: MISSING")
        else:
            print(f"  - {floor}: Present ({len(content)} bytes)")
    
    # Phase 4: Gap analysis
    print("\nPHASE 4: Gap Analysis")
    missing_floors = []
    for floor in ["F2", "F6", "F3", "F4", "F5", "F6_Amanah", "F7", "F8", "F9", "F10", "F11", "F12"]:
        if floor not in v46_floors or "FILE NOT FOUND" in v46_floors[floor]:
            missing_floors.append(floor)
    
    if missing_floors:
        print(f"MISSING v46 FLOORS: {missing_floors}")
    else:
        print("All v46 floor files present")
    
    # Phase 5: Constitutional continuity assessment
    print("\nPHASE 5: Constitutional Continuity Assessment")
    
    continuity_issues = []
    
    # Check core files
    if not critical_results["v46_core"]["exists"]:
        continuity_issues.append("v46 constitutional core missing")
    
    if not critical_results["v46_master_index"]["exists"]:
        continuity_issues.append("v46 master index missing")
    
    # Check floor continuity
    if not v45_floors:
        continuity_issues.append("v45 floors reference missing - cannot verify continuity")
    
    if missing_floors:
        continuity_issues.append(f"v46 floor files missing: {missing_floors}")
    
    if continuity_issues:
        print("CONSTITUTIONAL CONTINUITY ISSUES DETECTED:")
        for issue in continuity_issues:
            print(f"  - {issue}")
        print("\nRECOMMENDATION: Immediate review required before v46.1")
    else:
        print("Basic constitutional continuity maintained")
    
    print("\n" + "=" * 60)
    print("AUDIT COMPLETE - Manual review of floor numbering recommended")
    print("=" * 60)

if __name__ == "__main__":
    main()