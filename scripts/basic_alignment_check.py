#!/usr/bin/env python3
"""
basic_alignment_check.py

Basic Constitutional Alignment Check for 000-111-222-333
"""

import json
from pathlib import Path

def main():
    """Perform basic constitutional alignment check."""
    print("Basic Constitutional Alignment Check")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    pipeline_dir = project_root / "arifos_core" / "pipeline"
    
    # Check current pipeline stages
    orchestrator_file = pipeline_dir / "orchestrator.py"
    
    if orchestrator_file.exists():
        content = orchestrator_file.read_text(encoding='utf-8')
        
        # Extract current stages
        current_stages = []
        if "stage_000_hypervisor" in content:
            current_stages.append("000")
        if "stage_111" in content:
            current_stages.append("111")
        if "stage_222" in content:
            current_stages.append("222") 
        if "stage_333_reason" in content:
            current_stages.append("333")
        if "stage_555_feel" in content:
            current_stages.append("555")
        if "stage_888_witness" in content:
            current_stages.append("888")
        if "stage_999_seal" in content:
            current_stages.append("999")
        
        # Check for missing stages
        required_stages = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]
        missing_stages = [stage for stage in required_stages if stage not in current_stages]
        
        print(f"Current Pipeline Chain: {' -> '.join(current_stages)}")
        print(f"Required Chain: {' → '.join(required_stages)}")
        print(f"Missing Stages: {missing_stages}")
        
        # Constitutional analysis
        print("\nConstitutional Analysis:")
        
        violations = []
        if "111" not in current_stages:
            violations.append("F6 Amanah: Missing 111 SENSE measurement stage")
            violations.append("F8 Tri-Witness: No lineage traceability from 111")
            violations.append("F4 Empathy: No lane classification (CRISIS/FACTUAL/SOCIAL/CARE)")
            violations.append("F2 Clarity: No H_in entropy baseline for ΔS")
            violations.append("F1 Truth: No domain context (@WEALTH, @WELL, etc.)")
        
        if "222" not in current_stages:
            violations.append("F6 Amanah: Missing 222 REFLECT evaluation stage")
            violations.append("F8 Tri-Witness: No path evaluation audit trail")
            violations.append("Constitutional Process: No 4-path evaluation")
        
        for violation in violations:
            print(f"  CRITICAL: {violation}")
        
        # Overall status
        if missing_stages:
            print(f"\nOVERALL STATUS: VOID")
            print(f"Constitutional gap: {len(missing_stages)} missing stages")
            print(f"Required action: Implement missing constitutional stages")
            
            if "111" in missing_stages:
                print(f"\n111 SENSE Requirements:")
                print(f"  - Domain detection: 8 compass directions")
                print(f"  - Lane classification: 4 priority levels")
                print(f"  - Entropy calculation: Shannon H_in baseline")
                print(f"  - Subtext detection: psychological signals")
                print(f"  - Hypervisor scan: F10-F12 only")
                
            if "222" in missing_stages:
                print(f"\n222 REFLECT Requirements:")
                print(f"  - 4-path generation: direct/educational/refusal/escalation")
                print(f"  - Floor prediction: F1-F12 outcome forecasting")
                print(f"  - TAC analysis: Theory of Anomalous Contrast")
                print(f"  - Bearing selection: lane-weighted priority")
                print(f"  - Cryptographic lock: SHA-256 commitment")
        else:
            print(f"\nOVERALL STATUS: ALIGNED")
            print(f"All constitutional stages implemented")
        
        # Check current 333 implementation
        stage_333_file = pipeline_dir / "stage_333_reason.py"
        if stage_333_file.exists():
            content_333 = stage_333_file.read_text(encoding='utf-8')
            if "sensed_bundle_111" not in content_333 and "reflected_bundle_222" not in content_333:
                print(f"\nSTAGE 333 ARCHITECTURE ISSUE:")
                print(f"Current 333 mixes measurement+evaluation+commitment")
                print(f"Required: Pure commitment based on 222 bearing selection")
        
        return {
            "current_chain": current_stages,
            "missing_stages": missing_stages,
            "status": "VOID" if missing_stages else "ALIGNED",
            "violations": len(violations)
        }
    
    else:
        print(f"ERROR: Orchestrator file not found: {orchestrator_file}")
        return {"error": "Orchestrator file not found"}

if __name__ == "__main__":
    result = main()
    
    # Save results
    output_file = Path("basic_alignment_results.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Exit with appropriate code
    if result.get("status") == "VOID":
        print("\nCRITICAL: Constitutional alignment VOID - migration required")
        exit(1)
    else:
        print("\nSUCCESS: Constitutional alignment verified")
        exit(0)