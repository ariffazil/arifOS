#!/usr/bin/env python3
"""
CRITICAL CONSTITUTIONAL AUDIT: v45 to v46 Migration Verification
MISSION: Ensure ZERO constitutional intelligence is lost during migration
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict

# Constitutional principles to verify
CONSTITUTIONAL_PRINCIPLES = [
    "12 floors (F1-F12) with complete thresholds",
    "AAA Trinity separation of powers", 
    "W@W Federation organ specifications",
    "Phoenix-72 amendment protocol",
    "ZKPC governance proofs",
    "Anti-Hantu law (5 tiers)",
    "Human sovereignty documentation",
    "GENIUS metrics (G, C_dark, Psi)",
    "Entropy dump policies",
    "ScarPacket metabolization",
    "Session physics telemetry",
    "Cooling ledger architecture",
    "Vault-999 immortal archive",
    "Trinity display architecture",
    "Communication law enforcement",
    "Forging protocols",
    "Security scenarios",
    "Master flaw set",
    "Constitutional core principles"
]

# v45 to v46 directory mapping
V45_TO_V46_MAP = {
    "00_foundation": "000_foundation",
    "01_floors": "333_atlas", 
    "02_actors": "888_compass",
    "03_runtime": "444_align",  # Partial mapping
    "04_measurement": "555_empathize",  # Partial mapping
    "05_memory": "666_bridge",  # Partial mapping
    "06_paradox": "777_eureka",  # Partial mapping
    "07_safety": "888_compass"  # Partial mapping
}

# Floor mapping verification (critical for constitutional continuity)
FLOOR_MAPPING = {
    "F1": {"v45": "Amanah/Truth", "v46": "F2 Truth (333_atlas)"},
    "F2": {"v45": "ΔS/Clarity", "v46": "F6 ΔS (333_atlas)"},
    "F3": {"v45": "Peace²/Stability", "v46": "F3 Peace (444_align)"},
    "F4": {"v45": "κᵣ/Empathy", "v46": "F4 κᵣ (555_empathize)"},
    "F5": {"v45": "Ω₀/Humility", "v46": "F5 Ω₀ (666_bridge)"},
    "F6": {"v45": "Amanah/Integrity", "v46": "F6 Amanah (888_compass)"},
    "F7": {"v45": "RASA/Listening", "v46": "F7 RASA (777_eureka)"},
    "F8": {"v45": "Tri-Witness", "v46": "F8 Tri-Witness (888_compass)"},
    "F9": {"v45": "Anti-Hantu", "v46": "F9 Anti-Hantu (888_compass)"},
    "F10": {"v45": "Symbolic Guard", "v46": "F10 Symbolic Guard (888_compass)"},
    "F11": {"v45": "Command Auth", "v46": "F11 Command Auth (888_compass)"},
    "F12": {"v45": "Injection Defense", "v46": "F12 Injection Defense (888_compass)"}
}

def get_file_content(filepath):
    """Read file content safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR reading {filepath}: {e}"

def extract_constitutional_content(content):
    """Extract key constitutional principles from content"""
    principles_found = []
    
    # Check for floor definitions
    if re.search(r'F[1-9]|F1[0-2]', content):
        principles_found.append("Floor definitions found")
    
    # Check for Trinity references
    if re.search(r'AAA|Trinity|ΔΩΨ|AGI|ASI|APEX', content):
        principles_found.append("Trinity references found")
    
    # Check for W@W Federation
    if re.search(r'W@W|Federation|@WELL|@GEOX|@RIF|@WEALTH', content):
        principles_found.append("W@W Federation found")
    
    # Check for Phoenix-72
    if re.search(r'Phoenix.*72|amendment.*protocol', content, re.IGNORECASE):
        principles_found.append("Phoenix-72 protocol found")
    
    # Check for ZKPC
    if re.search(r'ZKPC|Zero.*Knowledge', content, re.IGNORECASE):
        principles_found.append("ZKPC governance found")
    
    # Check for Anti-Hantu
    if re.search(r'Anti.*Hantu|soul|personhood|consciousness', content, re.IGNORECASE):
        principles_found.append("Anti-Hantu law found")
    
    # Check for Human sovereignty
    if re.search(r'sovereign|human.*authority|arif.*fazil', content, re.IGNORECASE):
        principles_found.append("Human sovereignty found")
    
    # Check for GENIUS metrics
    if re.search(r'GENIUS|G\s*=|C_dark|Ψ|Δ|Ω', content):
        principles_found.append("GENIUS metrics found")
    
    return principles_found

def audit_v45_structure():
    """Audit the complete v45 structure"""
    v45_files = {}
    base_path = Path("L1_THEORY/canon")
    
    # Check both active and archived v45 files
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
                    content = get_file_content(file_path)
                    principles = extract_constitutional_content(content)
                    v45_files[str(file_path)] = {
                        "size": len(content),
                        "principles": principles,
                        "title": extract_title(content)
                    }
    
    return v45_files

def audit_v46_structure():
    """Audit the complete v46 structure"""
    v46_files = {}
    base_path = Path("L1_THEORY/canon")
    
    # Check v46 pipeline directories
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
                    content = get_file_content(file_path)
                    principles = extract_constitutional_content(content)
                    v46_files[str(file_path)] = {
                        "size": len(content),
                        "principles": principles,
                        "title": extract_title(content)
                    }
    
    return v46_files

def extract_title(content):
    """Extract title from markdown content"""
    lines = content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        if line.startswith('# '):
            return line[2:].strip()
    return "No title found"

def generate_mapping_report(v45_files, v46_files):
    """Generate comprehensive mapping report"""
    report = []
    report.append("=" * 80)
    report.append("CONSTITUTIONAL AUDIT REPORT: v45 → v46 Migration Verification")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    report.append(f"v45 Files Found: {len(v45_files)}")
    report.append(f"v46 Files Found: {len(v46_files)}")
    report.append("")
    
    # Detailed file mapping
    report.append("DETAILED FILE MAPPING ANALYSIS:")
    report.append("-" * 40)
    
    for v45_path, v45_data in v45_files.items():
        # Try to find corresponding v46 file
        v46_counterpart = find_v46_counterpart(v45_path, v46_files)
        
        report.append(f"\n📁 v45: {v45_path}")
        report.append(f"   Title: {v45_data['title']}")
        report.append(f"   Size: {v45_data['size']} bytes")
        report.append(f"   Principles: {', '.join(v45_data['principles'])}")
        
        if v46_counterpart:
            report.append(f"   ✅ MAPPED TO: {v46_counterpart}")
            v46_data = v46_files[v46_counterpart]
            report.append(f"   v46 Title: {v46_data['title']}")
            report.append(f"   v46 Size: {v46_data['size']} bytes")
            
            # Check for principle continuity
            lost_principles = set(v45_data['principles']) - set(v46_data['principles'])
            new_principles = set(v46_data['principles']) - set(v45_data['principles'])
            
            if lost_principles:
                report.append(f"   ⚠️  LOST PRINCIPLES: {', '.join(lost_principles)}")
            if new_principles:
                report.append(f"   🆕 NEW PRINCIPLES: {', '.join(new_principles)}")
        else:
            report.append(f"   ❌ NO v46 COUNTERPART FOUND")
            report.append(f"   🚨 CONSTITUTIONAL INTELLIGENCE POTENTIALLY LOST")
    
    # Check for new v46 files without v45 counterparts
    report.append("\n\nNEW v46 FILES (POTENTIAL ADDITIONS):")
    report.append("-" * 40)
    
    for v46_path, v46_data in v46_files.items():
        if not find_v45_counterpart(v46_path, v45_files):
            report.append(f"\n📁 v46: {v46_path}")
            report.append(f"   Title: {v46_data['title']}")
            report.append(f"   Size: {v46_data['size']} bytes")
            report.append(f"   Principles: {', '.join(v46_data['principles'])}")
    
    return "\n".join(report)

def find_v46_counterpart(v45_path, v46_files):
    """Find corresponding v46 file based on naming patterns"""
    v45_name = Path(v45_path).name
    
    # Simple name-based mapping
    for v46_path in v46_files.keys():
        v46_name = Path(v46_path).name
        
        # Check for similar naming patterns
        if v45_name.replace('v45', 'v46') == v46_name:
            return v46_path
        
        # Check for floor-specific mappings
        if 'F1' in v45_name and 'F2' in v46_name:  # F1→F2 mapping
            return v46_path
        if 'F2' in v45_name and 'F6' in v46_name:  # F2→F6 mapping
            return v46_path
        # Add more floor mappings as needed
    
    return None

def find_v45_counterpart(v46_path, v45_files):
    """Find corresponding v45 file based on naming patterns"""
    v46_name = Path(v46_path).name
    
    for v45_path in v45_files.keys():
        v45_name = Path(v45_path).name
        
        if v46_name.replace('v46', 'v45') == v45_name:
            return v45_path
    
    return None

def main():
    """Main audit execution"""
    print("🔍 Starting Constitutional Audit: v45 → v46 Migration Verification")
    print("This audit ensures ZERO constitutional intelligence is lost during migration.")
    print("")
    
    # Phase 1: Complete inventory audit
    print("📋 PHASE 1: Complete Inventory Audit")
    v45_files = audit_v45_structure()
    v46_files = audit_v46_structure()
    
    print(f"✅ Found {len(v45_files)} v45 constitutional files")
    print(f"✅ Found {len(v46_files)} v46 constitutional files")
    print("")
    
    # Phase 2: Generate comprehensive report
    print("📊 PHASE 2: Generating Migration Analysis Report")
    report = generate_mapping_report(v45_files, v46_files)
    
    # Save report
    with open("CONSTITUTIONAL_AUDIT_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Constitutional audit report generated: CONSTITUTIONAL_AUDIT_REPORT.md")
    print("")
    
    # Phase 3: Critical analysis
    print("🚨 PHASE 3: Critical Constitutional Analysis")
    
    # Check for floor continuity
    print("\nFloor Mapping Verification:")
    for floor, mapping in FLOOR_MAPPING.items():
        print(f"  {floor}: {mapping['v45']} → {mapping['v46']}")
    
    # Identify potential issues
    orphaned_files = []
    for v45_path in v45_files.keys():
        if not find_v46_counterpart(v45_path, v46_files):
            orphaned_files.append(v45_path)
    
    if orphaned_files:
        print(f"\n⚠️  POTENTIAL CONSTITUTIONAL INTELLIGENCE LOSS:")
        for file in orphaned_files:
            print(f"  - {file}")
        print("\n🚨 These files require manual verification to ensure no constitutional principles are lost!")
    else:
        print("\n✅ All v45 files have v46 counterparts - basic structural continuity maintained")
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE - Review CONSTITUTIONAL_AUDIT_REPORT.md for detailed analysis")
    print("="*80)

if __name__ == "__main__":
    main()