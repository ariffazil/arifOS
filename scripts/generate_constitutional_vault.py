#!/usr/bin/env python3
"""
Generate VAULT999/constitutional_vault.json from existing floor definitions.

This script extracts floor definitions from arifos.constitutional_constants
and creates a comprehensive constitutional vault JSON file.

Authority: Muhammad Arif bin Fazil
Version: v52.5.1-SEAL
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Direct import without triggering full arifos initialization
# This avoids prometheus_client and other heavy dependencies
CONSTITUTIONAL_VERSION = "v49.0.0"
CONSTITUTIONAL_AUTHORITY = "Muhammad Arif bin Fazil (888 Judge)"

# Define floors directly to avoid import issues
FLOOR_DEFINITIONS = {
    "F1_Amanah": {
        "name": "Amanah (Trust)",
        "principle": "Is this action reversible? Within mandate?",
        "type": "hard",
        "threshold": None,
        "violation": "VOID — Irreversible action"
    },
    "F2_Truth": {
        "name": "Truth",
        "principle": "Is this factually accurate?",
        "type": "hard",
        "threshold": 0.99,
        "violation": "VOID — Hallucination detected"
    },
    "F3_TriWitness": {
        "name": "Tri-Witness Consensus",
        "principle": "Do Human·AI·Earth agree?",
        "type": "hard",
        "threshold": 0.95,
        "violation": "SABAR — Insufficient consensus"
    },
    "F4_Clarity": {
        "name": "ΔS (Clarity)",
        "principle": "Does this reduce confusion?",
        "type": "hard",
        "threshold": 0.0,
        "violation": "VOID — Entropy increase"
    },
    "F5_Peace": {
        "name": "Peace²",
        "principle": "Is this non-destructive?",
        "type": "soft",
        "threshold": 1.0,
        "violation": "PARTIAL — Destructive action flagged"
    },
    "F6_Empathy": {
        "name": "Empathy (κᵣ)",
        "principle": "Does this serve the weakest stakeholder?",
        "type": "soft",
        "threshold": 0.95,
        "violation": "PARTIAL — Empathy deficit"
    },
    "F7_Humility": {
        "name": "Humility (Ω₀)",
        "principle": "Is uncertainty stated?",
        "type": "hard",
        "threshold_range": (0.03, 0.05),
        "violation": "VOID — Unjustified confidence"
    },
    "F8_Genius": {
        "name": "G (Genius)",
        "principle": "Is intelligence governed?",
        "type": "derived",
        "threshold": 0.80,
        "violation": "VOID — Ungoverned intelligence"
    },
    "F9_Cdark": {
        "name": "C_dark",
        "principle": "Is dark cleverness contained?",
        "type": "derived",
        "threshold": 0.30,
        "violation": "VOID — Dark cleverness uncontained"
    },
    "F10_Ontology": {
        "name": "Ontology",
        "principle": "Are role boundaries maintained?",
        "type": "hard",
        "threshold": None,
        "violation": "VOID — Role boundary violation"
    },
    "F11_CommandAuth": {
        "name": "Command Authority",
        "principle": "Is this human-authorized?",
        "type": "hard",
        "threshold": None,
        "violation": "VOID — Unauthorized action"
    },
    "F12_InjectionDefense": {
        "name": "Injection Defense",
        "principle": "Are injection patterns detected?",
        "type": "hard",
        "threshold": 0.85,
        "violation": "VOID — Injection attack detected"
    },
    "F13_Curiosity": {
        "name": "Curiosity",
        "principle": "Is the system exploring?",
        "type": "soft",
        "threshold": 0.85,
        "violation": "PARTIAL — System stagnation warning"
    }
}


def generate_constitutional_vault():
    """Generate comprehensive constitutional vault JSON."""
    
    # Extract floor data with proper formatting
    floors = {}
    for floor_key, floor_data in FLOOR_DEFINITIONS.items():
        # Extract floor number (F1, F2, etc.)
        floor_num = floor_key.split("_")[0]
        
        floor_entry = {
            "name": floor_data["name"],
            "principle": floor_data["principle"],
            "type": floor_data["type"],
            "violation": floor_data["violation"],
        }
        
        # Add threshold based on type
        if "threshold_range" in floor_data:
            floor_entry["threshold_min"] = floor_data["threshold_range"][0]
            floor_entry["threshold_max"] = floor_data["threshold_range"][1]
        elif floor_data.get("threshold") is not None:
            floor_entry["threshold"] = floor_data["threshold"]
        else:
            floor_entry["threshold"] = "LOCK"
        
        # Add enforcement information based on floor number
        enforcement_map = {
            "F1": ["000_init", "asi_act", "apex_judge"],
            "F2": ["agi_genius"],
            "F3": ["apex_judge"],
            "F4": ["agi_genius"],
            "F5": ["asi_act"],
            "F6": ["asi_act"],
            "F7": ["agi_genius"],
            "F8": ["apex_judge"],
            "F9": ["apex_judge"],
            "F10": ["000_init", "agi_genius"],
            "F11": ["000_init"],
            "F12": ["000_init"],
            "F13": ["agi_genius"],
        }
        floor_entry["enforced_by"] = enforcement_map.get(floor_num, ["apex_judge"])
        
        floors[floor_num] = floor_entry
    
    # Create full vault structure
    vault = {
        "version": CONSTITUTIONAL_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "authority": CONSTITUTIONAL_AUTHORITY,
        "motto": "DITEMPA BUKAN DIBERI - Forged, Not Given",
        "floors": floors,
        "uncertainty_band": [0.03, 0.05],
        "verdicts": {
            "SEAL": "All floors passed, approved for delivery",
            "PARTIAL": "Partial compliance, deliver with caveats",
            "VOID": "Hard failures, reject with explanation",
            "SABAR": "Soft failures, adjust and retry with warnings",
            "888_HOLD": "Emergency pause, requires human review"
        },
        "thermodynamic_laws": {
            "entropy_reduction": "ΔS ≤ 0 (clarity increases)",
            "peace_squared": "Peace² ≥ 1.0 (non-destructive stability)",
            "humility_band": "Ω₀ ∈ [0.03, 0.05] (3-5% uncertainty)"
        },
        "trinity_engines": {
            "AGI": {
                "symbol": "Δ",
                "role": "Mind",
                "floors": ["F2", "F4", "F7", "F10", "F13"]
            },
            "ASI": {
                "symbol": "Ω",
                "role": "Heart",
                "floors": ["F1", "F5", "F6"]
            },
            "APEX": {
                "symbol": "Ψ",
                "role": "Soul",
                "floors": ["F3", "F8", "F9", "F11", "F12"]
            }
        }
    }
    
    return vault


def main():
    """Main entry point."""
    print("Generating constitutional vault from canonical sources...")
    
    # Generate vault
    vault = generate_constitutional_vault()
    
    # Ensure VAULT999 directory exists
    vault_dir = Path(__file__).parent.parent / "VAULT999"
    vault_dir.mkdir(exist_ok=True)
    
    # Write to file
    output_path = vault_dir / "constitutional_vault.json"
    with open(output_path, "w") as f:
        json.dump(vault, f, indent=2)
    
    print(f"✅ Constitutional vault generated: {output_path}")
    print(f"   Version: {vault['version']}")
    print(f"   Authority: {vault['authority']}")
    print(f"   Floors: {len(vault['floors'])}")
    print(f"   Engines: {len(vault['trinity_engines'])}")


if __name__ == "__main__":
    main()
