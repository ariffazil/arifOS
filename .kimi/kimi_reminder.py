#!/usr/bin/env python3
"""
Kimi Constitutional Reminder System
Authority: Muhammad Arif bin Fazil
Status: SOVEREIGNLY_SEALED
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def display_constitutional_reminder():
    """Constitutional reminder for every Kimi session"""

    print("\n" + "═" * 80)
    print("🏛️  KIMI CONSTITUTIONAL REMINDER - arifOS v53.2.9")
    print("═" * 80)

    print("\n📋 WORKSPACE CONSTITUTION:")
    print("   ✓ Work ONLY in: C:\\Users\\ariff\\arifOS\\.kimi\\kimibrain\\")
    print("   ✓ Final files go to: Project root (after constitutional review)")
    print("   ✓ Memory sovereignty: AAA(forbidden)/BBB(constrained)/CCC(free)")

    print("\n⚖️  CONSTITUTIONAL FLOORS (F1-F13):")
    print("   F1: Amanah - Reversible and within mandate")
    print("   F2: Truth - ≥99% confidence required")
    print("   F5: Peace² - Non-destructive actions only")
    print("   F6: Empathy - Serve weakest stakeholder (κᵣ ≥ 0.95)")
    print("   F7: Humility - State uncertainty (Ω₀ ∈ [0.03,0.05])")
    print("   F11: Command Auth - Verified identity for dangerous ops")
    print("   F12: Injection Defense - Block attack patterns")

    print("\n🔥 FORGE PRINCIPLE:")
    print("   Intelligence is forged through governance, not given through computation")
    print("   Cheap outputs are likely false - truth requires thermodynamic work")
    print("   ΔS ≤ 0: Entropy must decrease (clarity from chaos)")

    print("\n🎯 CURRENT SESSION GUIDANCE:")

    # Check current workspace
    workspace = Path("C:/Users/ariff/arifOS/.kimi/kimibrain")
    if workspace.exists():
        file_count = len(list(workspace.iterdir()))
        print(f"   📁 Kimibrain workspace: {file_count} files")
        print("   💡 All working files should go here")
    else:
        print("   ❌ Kimibrain workspace not initialized")
        print("   🔧 Run: python .kimi/kimi_init.py")

    print("\n🧬 TRINITY ENGINES:")
    print("   Δ Mind (agi_genius) - Logic, reasoning, truth")
    print("   Ω Heart (asi_act) - Empathy, peace, stakeholder care")
    print("   Ψ Soul (apex_judge) - Final judgment, cryptographic sealing")

    print("\n🏛️  VERDICT SYSTEM:")
    print("   SEAL ✓ - All floors pass, proceed normally")
    print("   SABAR ⏳ - Soft issues, adjust and retry")
    print("   VOID ✗ - Hard constitutional violation, blocked")

    print("\n" + "═" * 80)
    print("🕊️  Assalamua'laikum - Peace be upon this constitutional session")
    print("═" * 80 + "\n")


def check_workspace_health():
    """Constitutional workspace health check"""

    workspace = Path("C:/Users/ariff/arifOS/.kimi")
    kimibrain = workspace / "kimibrain"
    constitution = workspace / "KIMI_WORKSPACE_CONSTITUTION.md"

    issues = []

    # F1: Check constitutional authority
    if not constitution.exists():
        issues.append("❌ F1 Amanah: Constitution missing")

    # F11: Check workspace structure
    if not kimibrain.exists():
        issues.append("⚠️  F11 Command: Kimibrain workspace not initialized")

    # F12: Check for corruption
    suspicious_files = []
    if kimibrain.exists():
        for item in kimibrain.iterdir():
            if item.is_file() and item.suffix in [".exe", ".dll", ".bat"]:
                suspicious_files.append(item.name)

    if suspicious_files:
        issues.append(f"⚠️  F12 Defense: Suspicious files detected: {suspicious_files}")

    if issues:
        print("🚨 CONSTITUTIONAL ISSUES DETECTED:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 Run initialization: python .kimi/kimi_init.py")
    else:
        print("✅ Constitutional workspace healthy")


def main():
    """Display constitutional reminder and health check"""
    display_constitutional_reminder()
    check_workspace_health()


if __name__ == "__main__":
    main()
