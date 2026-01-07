"""
Audit Task 2: F1-F9 Floor Implementation Verification
Purpose: Cross-check metrics.py against L1 canon and L2 specs
Estimated Time: 3 hours (automated pre-scan: 10 minutes)
"""

import re
from pathlib import Path


def audit_floor_implementation():
    """Audit F1-F9 implementation in metrics.py."""

    results = {
        "floors": {},
        "summary": {
            "implemented": 0,
            "aspirational": 0,
            "missing": 0
        }
    }

    # Read metrics.py
    metrics_path = Path("arifos_core/enforcement/metrics.py")
    if not metrics_path.exists():
        return {"error": "metrics.py not found"}

    with open(metrics_path, 'r', encoding='utf-8') as f:
        metrics_content = f.read()

    # Define floor audit patterns
    floors = {
        "F1_Amanah": {
            "function": "check_amanah",
            "threshold": "LOCK (boolean)",
            "expected_logic": ["reversible", "rollback", "destructive"]
        },
        "F2_Truth": {
            "function": "check_truth",
            "threshold": "0.99",
            "expected_logic": ["truth", "0.99", "evidence", "hallucination"]
        },
        "F3_TriWitness": {
            "function": "check_tri_witness",
            "threshold": "0.95",
            "expected_logic": ["tri_witness", "0.95", "consensus", "human", "ai", "earth"]
        },
        "F4_DeltaS": {
            "function": "check_delta_s",
            "threshold": "0.0",
            "expected_logic": ["delta_s", "zlib", "compress", "clarity"]
        },
        "F5_Peace_Squared": {
            "function": "check_peace_squared",
            "threshold": "1.0",
            "expected_logic": ["peace", "1.0", "stability", "entropy"]
        },
        "F6_Kappa_r": {
            "function": "compute_empathy_score",
            "threshold": "0.95",
            "expected_logic": ["empathy", "0.95", "kappa", "stakeholder"]
        },
        "F7_Omega_0": {
            "function": "check_omega_band",
            "threshold": "0.03-0.05",
            "expected_logic": ["omega", "0.03", "0.05", "humility", "uncertainty"]
        },
        "F8_Genius": {
            "function": "compute_genius_index",
            "threshold": "0.80",
            "expected_logic": ["genius", "0.80", "delta", "omega", "psi"]
        },
        "F9_C_dark": {
            "function": "compute_dark_cleverness",
            "threshold": "0.30",
            "expected_logic": ["dark", "0.30", "cleverness"]
        }
    }

    # Audit each floor
    for floor_name, floor_spec in floors.items():
        func_name = floor_spec["function"]

        # Check if function exists
        func_pattern = rf"def {func_name}\("
        func_match = re.search(func_pattern, metrics_content)

        if not func_match:
            results["floors"][floor_name] = {
                "status": "MISSING",
                "function": func_name,
                "found": False,
                "threshold_check": "N/A",
                "logic_check": []
            }
            results["summary"]["missing"] += 1
            continue

        # Extract function body (simple heuristic: until next def or end of file)
        func_start = func_match.start()
        next_def = re.search(r"\ndef ", metrics_content[func_start + 10:])
        if next_def:
            func_end = func_start + 10 + next_def.start()
        else:
            func_end = len(metrics_content)

        func_body = metrics_content[func_start:func_end]

        # Check threshold
        threshold_found = floor_spec["threshold"] in func_body

        # Check expected logic keywords
        logic_found = []
        for keyword in floor_spec["expected_logic"]:
            if keyword.lower() in func_body.lower():
                logic_found.append(keyword)

        # Classify status
        if threshold_found and len(logic_found) >= 2:
            status = "IMPLEMENTED"
            results["summary"]["implemented"] += 1
        elif len(logic_found) >= 1:
            status = "ASPIRATIONAL"
            results["summary"]["aspirational"] += 1
        else:
            status = "PLACEHOLDER"
            results["summary"]["aspirational"] += 1

        results["floors"][floor_name] = {
            "status": status,
            "function": func_name,
            "found": True,
            "threshold_check": threshold_found,
            "logic_keywords_found": logic_found,
            "logic_keywords_expected": floor_spec["expected_logic"]
        }

    return results

def generate_audit_report(results):
    """Generate markdown audit report."""

    report = f"""# Floor Implementation Audit Report
**Date:** 2026-01-06
**Audit:** Task 2 - F1-F9 Floor Verification
**File Audited:** arifos_core/enforcement/metrics.py

---

## Executive Summary

- **Implemented:** {results['summary']['implemented']}/9 floors ({results['summary']['implemented']/9*100:.0f}%)
- **Aspirational:** {results['summary']['aspirational']}/9 floors ({results['summary']['aspirational']/9*100:.0f}%)
- **Missing:** {results['summary']['missing']}/9 floors ({results['summary']['missing']/9*100:.0f}%)

---

## Floor-by-Floor Analysis

| Floor | Function | Status | Threshold Check | Logic Keywords Found |
|-------|----------|--------|-----------------|---------------------|
"""

    for floor_name, floor_data in results["floors"].items():
        status_icon = {
            "IMPLEMENTED": "✅",
            "ASPIRATIONAL": "⚠️",
            "PLACEHOLDER": "🔶",
            "MISSING": "❌"
        }.get(floor_data["status"], "❓")

        threshold = "✓" if floor_data.get("threshold_check") else "✗"
        keywords = ", ".join(floor_data.get("logic_keywords_found", [])) or "None"

        report += f"| **{floor_name}** | `{floor_data['function']}()` | {status_icon} {floor_data['status']} | {threshold} | {keywords} |\n"

    report += """

---

## Detailed Findings

"""

    for floor_name, floor_data in results["floors"].items():
        report += f"""
### {floor_name}

- **Function:** `{floor_data['function']}()`
- **Status:** {floor_data['status']}
- **Found in metrics.py:** {'Yes' if floor_data['found'] else 'No'}
- **Threshold Check:** {'Pass' if floor_data.get('threshold_check') else 'Fail'}
- **Expected Logic:** {', '.join(floor_data.get('logic_keywords_expected', []))}
- **Found Logic:** {', '.join(floor_data.get('logic_keywords_found', [])) or 'None'}

"""

        if floor_data['status'] == "MISSING":
            report += "**⚠️ CRITICAL:** Function not found in metrics.py. Floor is not implemented.\n"
        elif floor_data['status'] == "PLACEHOLDER":
            report += "**⚠️ WARNING:** Function exists but lacks expected logic. Likely a placeholder.\n"
        elif floor_data['status'] == "ASPIRATIONAL":
            report += "**ℹ️ INFO:** Function partially implemented. Some logic present but threshold not enforced.\n"
        elif floor_data['status'] == "IMPLEMENTED":
            report += "**✅ VERIFIED:** Function appears to be fully implemented with threshold checks.\n"

    report += """

---

## Recommendations

1. **CRITICAL:** Implement missing floors (if any)
2. **HIGH:** Complete aspirational floors with proper threshold enforcement
3. **MEDIUM:** Verify implemented floors match L1 canon formulas exactly
4. **LOW:** Add inline comments linking to L1 canon sections

---

## Next Steps

1. Manual review of each function to verify formula correctness
2. Cross-check with L2_GOVERNANCE/core/constitutional_floors.yaml
3. Run test suite to verify floor enforcement
4. Update BINDING_MANIFEST with findings

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
"""

    return report

# Run audit
print("Running Floor Implementation Audit...")
results = audit_floor_implementation()

if "error" in results:
    print(f"ERROR: {results['error']}")
else:
    print(f"Implemented: {results['summary']['implemented']}/9")
    print(f"Aspirational: {results['summary']['aspirational']}/9")
    print(f"Missing: {results['summary']['missing']}/9")

    # Generate report
    report = generate_audit_report(results)

    # Save report
    with open("FLOOR_AUDIT_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\nReport saved to: FLOOR_AUDIT_REPORT.md")
