#!/usr/bin/env python3
"""
Constitutional Entropy Analysis for arifOS_core
Simple version with F6 Clarity enforcement
"""

import datetime
import re
from collections import defaultdict
from pathlib import Path


def check_relative_imports(file_path: str) -> float:
    """Penalty for relative imports (hidden entropy)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find relative imports (from .. or from ...)
            rel_imports = re.findall(r'^from \.\.+[\w\.]* import', content, re.MULTILINE)
            return len(rel_imports) * 0.5 # 0.5 penalty per relative import
    except:
        return 0.0

def analyze_constitutional_entropy():
    """Perform constitutional entropy analysis on arifos_core"""

    root_path = Path('arifos_core')
    file_count = 0
    total_lines = 0
    complexity_scores = []
    penalty_scores = [] # Track relative import penalties
    dependencies = defaultdict(set)
    circular_risks = []

    print("*** CONSTITUTIONAL ENTROPY ANALYSIS ***")
    print("Constitutional Authority: F6 Clarity (DS <= 0.0)")
    print(f"Analyzing: {root_path}")

    for py_file in root_path.rglob("*.py"):
        if py_file.is_file() and not any(part.startswith('.') for part in py_file.parts):
            file_count += 1

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    total_lines += lines

                    # Calculate complexity (F6 Clarity metric)
                    imports = len(re.findall(r'^import|^from.*import', content, re.MULTILINE))
                    classes = len(re.findall(r'^class\s+', content, re.MULTILINE))
                    functions = len(re.findall(r'^def\s+', content, re.MULTILINE))
                    constitutional_patterns = len(re.findall(r'constitutional|verdict|floor_|f[1-9]', content, re.IGNORECASE))

                    base_score = (lines * 0.001 + imports * 0.01 + classes * 0.02 + functions * 0.015)
                    constitutional_bonus = constitutional_patterns * 0.005
                    complexity = max(0.0, min(1.0, base_score - constitutional_bonus))
                    complexity_scores.append(complexity)

                    # Extract dependencies (F8 Tri-Witness metric)
                    file_deps = set()
                    file_deps.update(re.findall(r'^import\s+(\w+)', content, re.MULTILINE))
                    file_deps.update(re.findall(r'^from\s+([\.\w]+)\s+import', content, re.MULTILINE))
                    dependencies[str(py_file)] = file_deps

                    # Check for circular import risk (F9 Anti-Hantu metric)
                    circular_patterns = [
                        r'from \. import',
                        r'import.*\n.*import.*\n.*from.*import',
                        r'if __name__ == [\"\']__main__[\"\']\s*:.*import',
                    ]

                    has_circular_risk = any(re.search(pattern, content, re.MULTILINE | re.IGNORECASE) for pattern in circular_patterns)
                    if has_circular_risk:
                        circular_risks.append(str(py_file))

                    # New: Check for relative import penalty
                    penalty_scores.append(check_relative_imports(py_file))

            except Exception as e:
                print(f"Warning: Could not analyze {py_file}: {e}")

    # Calculate constitutional metrics
    avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0.0
    total_deps = sum(len(deps) for deps in dependencies.values())
    unique_deps = len(set().union(*dependencies.values())) if dependencies else 0
    dependency_entropy = total_deps / len(dependencies) if dependencies else 0.0
    circular_risk_score = len(circular_risks) / file_count if file_count > 0 else 0.0
    avg_penalty = sum(penalty_scores) / len(penalty_scores) if penalty_scores else 0.0 # New: Calculate average penalty

    # Constitutional clarity formula (F6 constitutional floor)
    # This calculation is now used as a component of h_output, not directly for delta_s
    constitutional_clarity = 1.0 - (avg_complexity * 0.4 + dependency_entropy * 0.4 + circular_risk_score * 0.2)
    constitutional_clarity = max(0.0, min(1.0, constitutional_clarity))

    # Thermodynamic Comparative Analysis
    # Baseline H (v46 unaligned state) = 5.500
    h_baseline = 5.500
    h_output = (avg_complexity + dependency_entropy + avg_penalty + (circular_risk_score * 0.5)) - (constitutional_clarity)
    delta_s = h_output - h_baseline

    print("\n=== ENTROPY METRICS ===")
    print(f"Files Analyzed: {file_count}")
    print(f"Total Lines: {total_lines}")
    print(f"Average Complexity: {avg_complexity:.3f}/1.000")
    print(f"Dependency Entropy: {dependency_entropy:.3f}/1.000")
    print(f"Relative Penalty: {avg_penalty:.3f}/1.000")
    print(f"Circular Import Risk: {circular_risk_score:.3f}/1.000")
    print(f"Constitutional Clarity: {constitutional_clarity:.3f}/1.000")
    print(f"Total H(output): {h_output:.3f}")
    print(f"Baseline H(input): {h_baseline:.3f}")
    print(f"Entropy Change (DS): {delta_s:.3f} (F6 floor: {'SEAL' if delta_s <= 0.0 else 'VOID'})")

    print("\n=== CONSTITUTIONAL VERDICT ===")
    if delta_s <= 0.0:
        verdict = "SEAL"
        reason = "Constitutional entropy analysis complete with DS <= 0.0"
        next_action = "Proceed with entropy reduction implementation"
    else:
        verdict = "VOID"
        reason = "F6 Clarity violation: DS > 0.0 indicates entropy increase"
        next_action = "Implement SABAR cooling before entropy reduction"

    print(f"Verdict: {verdict}")
    print(f"Reason: {reason}")
    print(f"Next Action: {next_action}")

    print("\n=== TOP CONSTITUTIONAL FILES ===")
    constitutional_files = []
    for py_file in root_path.rglob("*.py"):
        if py_file.is_file() and not any(part.startswith('.') for part in py_file.parts):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    constitutional_score = len(re.findall(r'constitutional|verdict|floor_|f[1-9]', content, re.IGNORECASE))
                    if constitutional_score > 0:
                        constitutional_files.append((str(py_file), constitutional_score))
            except:
                pass

    constitutional_files.sort(key=lambda x: x[1], reverse=True)
    for i, (file_path, score) in enumerate(constitutional_files[:10], 1):
        print(f"{i:2d}. {file_path} (constitutional score: {score})")

    print("\nDITEMPA BUKAN DIBERI - Constitutional entropy analyzed with F6 Clarity enforcement.")

    return {
        "file_count": file_count,
        "total_lines": total_lines,
        "avg_complexity": avg_complexity,
        "dependency_entropy": dependency_entropy,
        "circular_risk_score": circular_risk_score,
        "constitutional_clarity": constitutional_clarity,
        "delta_s": delta_s,
        "verdict": verdict,
        "reason": reason,
        "next_action": next_action
    }

if __name__ == "__main__":
    analyze_constitutional_entropy()
