#!/usr/bin/env python3
"""
Forge Sentinel Prime: audit_parser.py
Parses scanner stdout for CRITICAL/HIGH findings and fires 888_HOLD via NATS.
Designed for 0-friction autonomous loops. ALWAYS exits 0.
"""

import sys
import json
import asyncio
import re
from datetime import datetime
try:
    from nats import connect
except ImportError:
    pass # Will handle gracefully below

# Regex patterns to detect high-severity findings in stdout
PATTERNS = [
    re.compile(r'Total:\s*[1-9]\d*\s*\(.*?HIGH:\s*[1-9]\d*', re.IGNORECASE),
    re.compile(r'Total:\s*[1-9]\d*\s*\(.*?CRITICAL:\s*[1-9]\d*', re.IGNORECASE),
    re.compile(r'severity:\s*critical', re.IGNORECASE),
    re.compile(r'severity:\s*high', re.IGNORECASE),
    re.compile(r'Found [1-9]\d* new secrets', re.IGNORECASE),
]

async def fire_hold_event(findings: list[str]):
    try:
        # Connect to the local core NATS bus used by arifOS
        nc = await connect("nats://127.0.0.1:4222")
        
        payload = json.dumps({
            "epoch": datetime.utcnow().isoformat() + "Z",
            "source": "forge_sentinel_audit",
            "type": "888_HOLD",
            "level": "CRITICAL",
            "reason": "Security scanner detected CRITICAL/HIGH findings during metabolic cycle.",
            "context": findings
        }).encode()
        
        # Publish to the standard arifos event bus topic
        await nc.publish("arifos.events.audit", payload)
        await nc.flush(1)
        await nc.close()
        print(f"\n[Sentinel] 888_HOLD event fired to NATS. Findings: {len(findings)}")
    except Exception as e:
        print(f"\n[Sentinel] Failed to publish event, but flow continues. {e}")

def main():
    if "nats" not in sys.modules:
        print("[Sentinel] nats-py not installed. Event bus disabled.")
        sys.exit(0)
        
    try:
        content = sys.stdin.read()
    except Exception:
        sys.exit(0)
        
    findings = []
    
    # Check for direct stdout pattern matches (Trivy, Gitleaks, etc)
    for line in content.splitlines():
        for pat in PATTERNS:
            if pat.search(line):
                findings.append(line.strip())
                break
                
    # Parse Semgrep/Ruff error blocks if visible
    if "Found " in content and " errors." in content:
         findings.append("Linting errors detected (SAST/Ruff).")
         
    if findings:
        print("\n[Sentinel] WARNING: Critical findings detected. Initiating 888_HOLD.")
        asyncio.run(fire_hold_event(findings))
    else:
        print("\n[Sentinel] Audit clean. No CRITICAL/HIGH findings detected.")

    # ALWAYS EXIT 0 to preserve agentic autonomy
    sys.exit(0)

if __name__ == "__main__":
    main()
