#!/usr/bin/env python3
"""
Architectural Entropy Measurement - arifOS Core Analysis
Authority: Muhammad Arif bin Fazil  
Status: CONSTITUTIONAL ARCHITECTURAL ANALYSIS
Target: arifos/core/ - Real entropy measurement
"""

import sys
import time
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional

# Add arifOS to path for constitutional analysis
sys.path.insert(0, "C:/Users/User/arifOS")

try:
    # Try importing from kimibrain workspace
    sys.path.insert(0, "C:/Users/User/arifOS/.kimi/kimibrain")
    from constitutional_entropy_engine import ConstitutionalEntropyEngine, EntropyMeasurement
except ImportError as e:
    # Fallback to local implementation
    print(f"[CONSTITUTIONAL] Import error: {e}")
    print("[CONSTITUTIONAL] Using local entropy engine implementation")
    # Load the entropy engine from the correct path
    entropy_engine_path = Path("C:/Users/User/arifOS/.kimi/kimibrain/constitutional_entropy_engine.py")
    if entropy_engine_path.exists():
        exec(open(entropy_engine_path).read())
    else:
        print(f"[ERROR] Constitutional entropy engine not found at {entropy_engine_path}")
        sys.exit(1)

def analyze_arifos_core_architecture():
    """Perform constitutional architectural entropy analysis of arifOS core"""
    
    print("="*80)
    print("CONSTITUTIONAL ARCHITECTURAL ENTROPY ANALYSIS")
    print("="*80)
    print(f"[AUTHORITY] Muhammad Arif bin Fazil")
    print(f"[TARGET] arifos/core/ - Real constitutional architecture")
    print(f"[MANDATE] Measure Delta S for constitutional ordering")
    print()
    
    # Initialize constitutional entropy engine
    vault_path = Path("C:/Users/User/arifOS/VAULT999")
    engine = ConstitutionalEntropyEngine(vault_path)
    
    # Define arifOS core modules for constitutional analysis
    core_path = Path("C:/Users/User/arifOS/arifos/core")
    
    if not core_path.exists():
        print(f"[ERROR] arifos/core/ not found at {core_path}")
        return
    
    print(f"[SCAN] Analyzing constitutional architecture at {core_path}")
    print()
    
    # Constitutional stakeholder mapping for F6 empathy
    stakeholder_map = {
        "developers": ["code_complexity", "maintainability", "documentation"],
        "users": ["performance", "reliability", "response_time"],
        "maintainers": ["modularity", "testing", "deployment"],
        "constitutional_authority": ["F1-F13_compliance", "thermodynamic_ordering"]
    }
    
    # Analyze each constitutional module
    constitutional_analysis = {}
    
    print("CONSTITUTIONAL MODULE ANALYSIS:")
    print("-"*80)
    
    # Priority modules for constitutional analysis
    priority_modules = [
        "memory",        # High entropy zone identified
        "integration",   # High entropy zone identified  
        "enforcement",   # Medium entropy zone
        "agi",          # Trinity engine
        "asi",          # Trinity engine
        "apex",         # Trinity engine
        "pipeline",     # Critical path
        "trinity",      # Coordination overhead
        "engines",      # Runtime fragmentation
        "utils",        # Utility sprawl
    ]
    
    for module_name in priority_modules:
        module_path = core_path / module_name
        
        if not module_path.exists():
            print(f"[SKIP] {module_name}/ not found")
            continue
        
        print(f"\n[MODULE] Analyzing {module_name}/")
        print(f"[PATH] {module_path}")
        
        # Perform constitutional architectural analysis
        analysis = analyze_constitutional_module(module_path, module_name, engine, stakeholder_map)
        constitutional_analysis[module_name] = analysis
        
        # Display constitutional results
        display_constitutional_results(module_name, analysis)
    
    print("\n" + "="*80)
    print("CONSTITUTIONAL SUMMARY")
    print("="*80)
    
    generate_constitutional_summary(constitutional_analysis, engine)
    
    print("\n" + "="*80)
    print("[SUCCESS] Constitutional architectural analysis complete")
    print("[AUTHORITY] Analysis sovereignly sealed by Muhammad Arif bin Fazil")
    print("="*80)

def analyze_constitutional_module(module_path: Path, module_name: str, 
                                engine: ConstitutionalEntropyEngine,
                                stakeholder_map: Dict[str, List[str]]) -> Dict[str, any]:
    """Perform deep constitutional analysis of a specific module"""
    
    analysis = {
        "module_name": module_name,
        "module_path": str(module_path),
        "files": [],
        "total_files": 0,
        "total_size": 0,
        "complexity_score": 0.0,
        "dependency_score": 0.0,
        "cohesion_score": 0.0,
        "entropy_measurement": None,
        "stakeholder_impact": {},
        "constitutional_issues": [],
        "recommendations": []
    }
    
    # Count files and analyze structure
    python_files = list(module_path.rglob("*.py"))
    analysis["total_files"] = len(python_files)
    
    if analysis["total_files"] == 0:
        print(f"[EMPTY] No Python files in {module_name}/")
        return analysis
    
    print(f"[FILES] Found {analysis['total_files']} Python files")
    
    # Analyze each file constitutionally
    total_size = 0
    total_complexity = 0.0
    total_dependencies = 0.0
    total_cohesion = 0.0
    
    for py_file in python_files:
        if py_file.name.startswith("__"):  # Skip cache files
            continue
            
        file_analysis = analyze_constitutional_file(py_file)
        analysis["files"].append(file_analysis)
        
        total_size += file_analysis["size"]
        total_complexity += file_analysis["complexity"]
        total_dependencies += file_analysis["dependencies"]
        total_cohesion += file_analysis["cohesion"]
    
    analysis["total_size"] = total_size
    analysis["complexity_score"] = total_complexity / len(analysis["files"]) if analysis["files"] else 0.0
    analysis["dependency_score"] = total_dependencies / len(analysis["files"]) if analysis["files"] else 0.0
    analysis["cohesion_score"] = total_cohesion / len(analysis["files"]) if analysis["files"] else 0.0
    
    # Calculate constitutional entropy
    print(f"[ENTROPY] Measuring constitutional entropy...")
    entropy_measurement = engine.measure_architectural_entropy(
        module_path,
        stakeholder_map
    )
    analysis["entropy_measurement"] = entropy_measurement
    
    # Identify constitutional issues (F4 Clarity analysis)
    identify_constitutional_issues(analysis)
    
    # Generate constitutional recommendations
    generate_constitutional_recommendations(analysis)
    
    return analysis

def analyze_constitutional_file(file_path: Path) -> Dict[str, any]:
    """Analyze a single Python file constitutionally"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic metrics
        lines = len(content.split('\n'))
        size = len(content.encode('utf-8'))
        
        # Complexity analysis
        class_count = content.count('class ')
        function_count = content.count('def ')
        import_count = content.count('import ') + content.count('from ')
        complexity = (class_count * 2.0 + function_count * 1.5 + import_count * 0.5) / 100.0
        
        # Dependency analysis
        external_deps = content.count('from arifos') + content.count('import arifos')
        circular_risks = len([line for line in content.split('\n') if 'import' in line and len(line.strip().split()) > 3])
        dependencies = (external_deps * 1.0 + circular_risks * 0.3) / 50.0
        
        # Cohesion analysis
        related_terms = ['constitutional', 'entropy', 'governance', 'floor', 'trinity']
        term_matches = sum(content.count(term) for term in related_terms)
        consistent_naming = len([line for line in content.split('\n') if 'def ' in line and ('constitutional' in line.lower() or 'floor' in line.lower())]) / max(function_count, 1)
        cohesion = (term_matches * 0.01 + consistent_naming * 0.5) / 2.0
        
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "size": size,
            "lines": lines,
            "complexity": min(complexity, 5.0),
            "dependencies": min(dependencies, 3.0),
            "cohesion": min(cohesion, 1.0),
            "class_count": class_count,
            "function_count": function_count,
            "import_count": import_count
        }
        
    except Exception as e:
        print(f"[ERROR] Could not analyze {file_path}: {e}")
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "size": 0,
            "lines": 0,
            "complexity": 1.0,  # High complexity on error
            "dependencies": 1.0,
            "cohesion": 0.3,
            "class_count": 0,
            "function_count": 0,
            "import_count": 0
        }

def identify_constitutional_issues(analysis: Dict[str, any]) -> None:
    """Identify constitutional issues using F1-F13 floors"""
    
    issues = []
    
    # F4 Clarity: High entropy detection
    if analysis["entropy_measurement"] and analysis["entropy_measurement"].delta_s > 0:
        issues.append({
            "floor": "F4",
            "issue": "High architectural entropy",
            "severity": "HIGH" if analysis["entropy_measurement"].delta_s > 1.0 else "MEDIUM",
            "description": f"ΔS = {analysis['entropy_measurement'].delta_s:.3f} bits (entropy increase)"
        })
    
    # F4 Clarity: Complexity issues
    if analysis["complexity_score"] > 2.0:
        issues.append({
            "floor": "F4",
            "issue": "High complexity",
            "severity": "HIGH" if analysis["complexity_score"] > 3.0 else "MEDIUM",
            "description": f"Complexity score: {analysis['complexity_score']:.3f}"
        })
    
    # F4 Clarity: Dependency issues  
    if analysis["dependency_score"] > 1.5:
        issues.append({
            "floor": "F4",
            "issue": "High dependencies",
            "severity": "HIGH" if analysis["dependency_score"] > 2.0 else "MEDIUM",
            "description": f"Dependency score: {analysis['dependency_score']:.3f}"
        })
    
    # F6 Empathy: Low cohesion
    if analysis["cohesion_score"] < 0.5:
        issues.append({
            "floor": "F6",
            "issue": "Low cohesion",
            "severity": "MEDIUM",
            "description": f"Cohesion score: {analysis['cohesion_score']:.3f} (serves stakeholders poorly)"
        })
    
    analysis["constitutional_issues"] = issues

def generate_constitutional_recommendations(analysis: Dict[str, any]) -> None:
    """Generate constitutional recommendations for entropy reduction"""
    
    recommendations = []
    
    # Constitutional ordering recommendations
    if analysis["entropy_measurement"] and analysis["entropy_measurement"].delta_s > 0:
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Apply constitutional ordering",
            "description": "Implement ΔS ≤ 0 through architectural consolidation",
            "expected_improvement": f"Reduce entropy by ~{analysis['entropy_measurement'].delta_s * 0.7:.3f} bits"
        })
    
    # Complexity reduction recommendations
    if analysis["complexity_score"] > 2.0:
        recommendations.append({
            "priority": "HIGH",
            "action": "Consolidate functionality",
            "description": "Reduce complexity through unified interfaces",
            "expected_improvement": "30-50% complexity reduction"
        })
    
    # Dependency reduction recommendations
    if analysis["dependency_score"] > 1.5:
        recommendations.append({
            "priority": "HIGH", 
            "action": "Simplify dependencies",
            "description": "Reduce circular dependencies through dependency injection",
            "expected_improvement": "40-60% dependency reduction"
        })
    
    # Cohesion improvement recommendations
    if analysis["cohesion_score"] < 0.5:
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Increase cohesion",
            "description": "Improve stakeholder service through focused functionality",
            "expected_improvement": "Cohesion score to 0.7+"
        })
    
    analysis["recommendations"] = recommendations

def display_constitutional_results(module_name: str, analysis: Dict[str, any]) -> None:
    """Display constitutional analysis results"""
    
    print(f"\n[RESULTS] Constitutional analysis for {module_name}/")
    print(f"[FILES] {analysis['total_files']} files, {analysis['total_size']} bytes")
    print(f"[ENTROPY] Delta S: {analysis['entropy_measurement'].delta_s:.4f} bits")
    print(f"[COMPLIANCE] Constitutional: {analysis['entropy_measurement'].is_constitutional()}")
    
    if analysis["constitutional_issues"]:
        print(f"[ISSUES] {len(analysis['constitutional_issues'])} constitutional issues identified:")
        for issue in analysis["constitutional_issues"]:
            print(f"  [{issue['floor']}] {issue['issue']} ({issue['severity']}): {issue['description']}")
    
    if analysis["recommendations"]:
        print(f"[RECOMMENDATIONS] {len(analysis['recommendations'])} constitutional recommendations:")
        for rec in analysis["recommendations"]:
            print(f"  [{rec['priority']}] {rec['action']}: {rec['description']}")

def generate_constitutional_summary(constitutional_analysis: Dict[str, any], 
                                  engine: ConstitutionalEntropyEngine) -> None:
    """Generate constitutional summary of all modules analyzed"""
    
    print("\n[SUMMARY] Constitutional Architectural Entropy Analysis")
    print("-"*60)
    
    if not constitutional_analysis:
        print("[SUMMARY] No modules analyzed")
        return
    
    # Calculate overall constitutional metrics
    total_entropy_before = 0.0
    total_entropy_after = 0.0
    total_constitutional_violations = 0
    total_issues = 0
    
    for module_name, analysis in constitutional_analysis.items():
        if analysis["entropy_measurement"]:
            total_entropy_before += analysis["entropy_measurement"].before_bits
            total_entropy_after += analysis["entropy_measurement"].after_bits
            
            if not analysis["entropy_measurement"].is_constitutional():
                total_constitutional_violations += 1
            
            total_issues += len(analysis["constitutional_issues"])
    
    overall_delta_s = total_entropy_after - total_entropy_before
    
    print(f"[MODULES] Analyzed: {len(constitutional_analysis)} constitutional modules")
    print(f"[ENTROPY] Overall Delta S: {overall_delta_s:.4f} bits")
    print(f"[VIOLATIONS] Constitutional violations: {total_constitutional_violations}")
    print(f"[ISSUES] Total constitutional issues: {total_issues}")
    
    if overall_delta_s > 0:
        print(f"[WARNING] Overall entropy increase detected - constitutional ordering required")
        print(f"[RECOMMENDATION] Apply constitutional ordering to achieve Delta S <= 0")
    else:
        print(f"[SUCCESS] Overall constitutional compliance achieved: Delta S <= 0")
    
    # Generate constitutional summary
    summary = engine.get_constitutional_summary()
    print(f"[SUMMARY] Engine compliance: {summary['constitutional_compliance']:.2%}")
    print(f"[SUMMARY] Total measurements: {summary['total_measurements']}")
    
    # Constitutional next steps
    print(f"\n[NEXT] Constitutional implementation priorities:")
    if total_constitutional_violations > 0:
        print(f"  1. Address {total_constitutional_violations} modules with entropy violations")
    if total_issues > 0:
        print(f"  2. Resolve {total_issues} constitutional architectural issues")
    print(f"  3. Implement constitutional ordering recommendations")
    print(f"  4. Verify Delta S <= 0 compliance after implementation")

if __name__ == "__main__":
    analyze_arifos_core_architecture()