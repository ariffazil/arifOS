#!/usr/bin/env python3
"""
simple_alignment_check.py

Simple Constitutional Alignment Check for 000-111-222-333

Quick analysis script to validate alignment gaps.
"""

import json
from pathlib import Path

def analyze_alignment():
    """Perform simple constitutional alignment analysis."""
    print("🔍 Simple Constitutional Alignment Check")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    pipeline_dir = project_root / "arifos_core" / "pipeline"
    
    # Check current pipeline stages
    orchestrator_file = pipeline_dir / "orchestrator.py"
    
    if orchestrator_file.exists():
        content = orchestrator_file.read_text()
        
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
        
        print(f"📊 Current Pipeline Chain: {' → '.join(current_stages)}")
        print(f"📋 Required Chain: {' → '.join(required_stages)}")
        print(f"❌ Missing Stages: {missing_stages}")
        
        # Constitutional analysis
        print("\n⚖️ Constitutional Analysis:")
        
        if "111" not in current_stages:
            print("  ❌ F6 Amanah VIOLATION: Missing 111 SENSE measurement stage")
            print("  ❌ F8 Tri-Witness VIOLATION: No lineage traceability from 111")
            print("  ❌ F4 Empathy VIOLATION: No lane classification (CRISIS/FACTUAL/SOCIAL/CARE)")
            print("  ❌ F2 Clarity VIOLATION: No H_in entropy baseline for ΔS")
            print("  ❌ F1 Truth VIOLATION: No domain context (@WEALTH, @WELL, etc.)")
        
        if "222" not in current_stages:
            print("  ❌ F6 Amanah VIOLATION: Missing 222 REFLECT evaluation stage")
            print("  ❌ F8 Tri-Witness VIOLATION: No path evaluation audit trail")
            print("  ❌ Constitutional Process: No 4-path evaluation (direct/educational/refusal/escalation)")
        
        # Overall status
        if missing_stages:
            print(f"\n🚨 OVERALL STATUS: ❌ VOID")
            print(f"   Constitutional gap: {len(missing_stages)} missing stages")
            print(f"   Required action: Implement missing constitutional stages")
            
            if "111" in missing_stages:
                print(f"\n📋 111 SENSE Requirements:")
                print(f"   • Domain detection: 8 compass directions")
                print(f"   • Lane classification: 4 priority levels")
                print(f"   • Entropy calculation: Shannon H_in baseline")
                print(f"   • Subtext detection: psychological signals")
                print(f"   • Hypervisor scan: F10-F12 only")
                
            if "222" in missing_stages:
                print(f"\n📋 222 REFLECT Requirements:")
                print(f"   • 4-path generation: direct/educational/refusal/escalation")
                print(f"   • Floor prediction: F1-F12 outcome forecasting")
                print(f"   • TAC analysis: Theory of Anomalous Contrast")
                print(f"   • Bearing selection: lane-weighted priority")
                print(f"   • Cryptographic lock: SHA-256 commitment")
        else:
            print(f"\n✅ OVERALL STATUS: ALIGNED")
            print(f"   All constitutional stages implemented")
        
        # Check current 333 implementation
        stage_333_file = pipeline_dir / "stage_333_reason.py"
        if stage_333_file.exists():
            content_333 = stage_333_file.read_text()
            if "sensed_bundle_111" not in content_333 and "reflected_bundle_222" not in content_333:
                print(f"\n⚠️  STAGE 333 ARCHITECTURE ISSUE:")
                print(f"   Current 333 mixes measurement+evaluation+commitment")
                print(f"   Required: Pure commitment based on 222 bearing selection")
        
        return {
            "current_chain": current_stages,
            "missing_stages": missing_stages,
            "status": "VOID" if missing_stages else "ALIGNED",
            "violations": len(missing_stages)
        }
    
    else:
        print(f"❌ Orchestrator file not found: {orchestrator_file}")
        return {"error": "Orchestrator file not found"}

if __name__ == "__main__":
    result = analyze_alignment()
    
    # Save results
    output_file = Path("alignment_check_results.json")
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    # Exit with appropriate code
    if result.get("status") == "VOID":
        print("\n💥 Constitutional alignment VOID - migration required")
        exit(1)
    else:
        print("\n✅ Constitutional alignment verified")
        exit(0)