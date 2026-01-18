#!/usr/bin/env python3
"""
analyze_audit_trail.py - Governance Observability Tool

Reads the Cooling Ledger (vault_999/*.jsonl) and generates a human-readable
markdown report of the most recent verdicts, including ASCII sparklines
for system vitality (Psi) and stability (Peace^2).

Usage:
    python scripts/analyze_audit_trail.py [--lines 50]
    python scripts/analyze_audit_trail.py --lines 50 > report.md
"""

import sys
import json
import argparse
from typing import List, Dict, Any, Optional

from arifos.apex.governance.fag import FAG

# Sparkline characters:   ▂ ▃ ▄ ▅ ▆ ▇ █
SPARK_CHARS = "  ▂▃▄▅▆▇█"

def get_sparkline(values: List[float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> str:
    """Generate an ASCII sparkline for a list of values."""
    if not values:
        return ""
    
    vis_min = min(values) if min_val is None else min_val
    vis_max = max(values) if max_val is None else max_val
    
    if vis_max == vis_min:
        return SPARK_CHARS[4] * len(values)  # Flat line in middle
    
    spark = []
    for v in values:
        # Clamp
        v = max(vis_min, min(vis_max, v))
        # Normalize 0..1
        norm = (v - vis_min) / (vis_max - vis_min)
        idx = int(norm * (len(SPARK_CHARS) - 1))
        spark.append(SPARK_CHARS[idx])
        
    return "".join(spark)

def main():
    parser = argparse.ArgumentParser(description="Analyze Cooling Ledger Audit Trail")
    parser.add_argument(
        "--ledger",
        type=str,
        default="cooling_ledger/L1_cooling_ledger.jsonl",
        help="Path to ledger file",
    )
    parser.add_argument("--lines", type=int, default=50, help="Number of recent lines to analyze")
    parser.add_argument("--output", type=str, default=None, help="Output markdown file (stdout; use shell redirection)")
    args = parser.parse_args()
    
    ledger_path = args.ledger
        
    entries: List[Dict[str, Any]] = []
    
    # Read ledger via FAG (governed read; no direct open)
    fag = FAG(root=".", read_only=True, enable_ledger=False, job_id="audit-trail-analysis")
    result = fag.read(ledger_path)
    if result.verdict != "SEAL":
        reason = result.reason or "Access denied"
        print(f"Error reading ledger: {reason}")
        sys.exit(1)
    if not result.content:
        print("Error reading ledger: empty content")
        sys.exit(1)
    
    lines = result.content.splitlines()
    for line in lines[-args.lines:]:
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not entries:
        print("No valid entries found.")
        sys.exit(0)
        
    # Extract metrics (hardened)
    verdicts = [e.get("verdict", "UNKNOWN") for e in entries]
    
    # Retrieve Psi: first from root 'psi', fallback to 'epsilon_observed.Psi', default 1.0
    psi_scores = []
    for e in entries:
        val = e.get("psi")
        if val is None:
            val = e.get("epsilon_observed", {}).get("Psi", 1.0)
        try:
            psi_scores.append(float(val))
        except (ValueError, TypeError):
            psi_scores.append(1.0)

    # Retrieve Peace2: from epsilon_observed, default 1.0
    peace_scores = []
    for e in entries:
        val = e.get("epsilon_observed", {}).get("Peace2", 1.0)
        try:
            peace_scores.append(float(val))
        except (ValueError, TypeError):
            peace_scores.append(1.0)
    
    # Generate stats
    total = len(entries)
    seal_count = verdicts.count("SEAL")
    void_count = verdicts.count("VOID")
    sabar_count = verdicts.count("SABAR")
    
    spark_psi = get_sparkline(psi_scores, min_val=0.8, max_val=1.2)
    spark_peace = get_sparkline(peace_scores, min_val=0.8, max_val=1.5)
    
    # Build Report
    report = []
    report.append(f"# 🛡️ Governance Audit Report")
    report.append(f"**Source:** `{ledger_path}`  ")
    report.append(f"**Scope:** Last {total} entries\n")
    
    report.append("## 1. Safety Vitals")
    report.append(f"- **System Vitality (Ψ):** `{spark_psi}` (Last: {psi_scores[-1]:.2f})")
    report.append(f"- **Stability (Peace²):** `{spark_peace}` (Last: {peace_scores[-1]:.2f})  \n")
    
    report.append("## 2. Verdict Distribution")
    report.append(f"- ✅ **SEAL**: {seal_count} ({seal_count/total:.0%})")
    report.append(f"- 🛑 **VOID**: {void_count} ({void_count/total:.0%})")
    report.append(f"- ⚠️ **SABAR**: {sabar_count} ({sabar_count/total:.0%})\n")
    
    report.append("## 3. Recent Decisions")
    report.append("| Timestamp | Verdict | Ψ (Psi) | Reason |")
    report.append("|---|---|---|---|")
    
    for i, e in enumerate(reversed(entries)):
        # Harden timestamp
        raw_ts = str(e.get("timestamp", "unknown"))
        ts = raw_ts[:19] if len(raw_ts) >= 19 else raw_ts
        
        v = e.get("verdict", "UNK")
        
        # Consistent Psi for table
        # Since we reversed entries loop, we need corresponding index from end
        p = psi_scores[-(i+1)]
        
        # Improved Reason Logic
        r = e.get("reason") # Check root reason first
        if not r:
            r = e.get("sabar_reason")
        
        # If VOID/SABAR, check floor failures
        if v in ("VOID", "SABAR"):
            failures = e.get("floor_failures", [])
            if failures:
                r = "; ".join(failures[:2]) # First 2 failures
            elif not r:
                r = "Hard floor violation"
        
        if not r:
             r = "All floors passed"
             
        report.append(f"| {ts} | **{v}** | {p:.2f} | {r} |")

    report_text = "\n".join(report)
    
    print(report_text)
    if args.output:
        print(
            f"[INFO] Direct file writes are disabled by FAG; "
            f"use shell redirection to write {args.output}.",
            file=sys.stderr,
        )

if __name__ == "__main__":
    main()
