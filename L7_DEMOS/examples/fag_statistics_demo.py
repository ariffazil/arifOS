"""
FAG Statistics and Audit Demo - v41.0.0

Demonstrates new FAG capabilities:
1. Access statistics tracking (count by pattern type)
2. Audit file logging for denied access

Run this demo:
    python examples/fag_statistics_demo.py
"""

from pathlib import Path
import tempfile
import json

from arifos_core.governance.fag import FAG


def demo_statistics():
    """Demonstrate access statistics tracking."""
    print("=" * 70)
    print("DEMO 1: Access Statistics Tracking")
    print("=" * 70)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test files
        (tmp_path / "public.txt").write_text("This is public data")
        (tmp_path / "README.md").write_text("# Documentation")
        (tmp_path / ".env").write_text("SECRET_KEY=abc123")
        (tmp_path / "app.exe").write_bytes(b"\x00\x01\x02")
        
        # Initialize FAG
        fag = FAG(root=str(tmp_path), enable_ledger=False)
        
        print("\n📁 Test Workspace Created:")
        print("  - public.txt (readable)")
        print("  - README.md (readable)")
        print("  - .env (forbidden - F9 C_dark)")
        print("  - app.exe (binary - F4 DeltaS)")
        
        print("\n🔍 Attempting Various File Access Operations...")
        
        # Successful reads
        result1 = fag.read("public.txt")
        print(f"\n  ✓ public.txt → {result1.verdict}")
        
        result2 = fag.read("README.md")
        print(f"  ✓ README.md → {result2.verdict}")
        
        # Denied reads
        result3 = fag.read(".env")
        print(f"  ✗ .env → {result3.verdict} ({result3.reason[:40]}...)")
        
        result4 = fag.read("app.exe")
        print(f"  ✗ app.exe → {result4.verdict} ({result4.reason[:40]}...)")
        
        result5 = fag.read("missing.txt")
        print(f"  ✗ missing.txt → {result5.verdict} ({result5.reason[:40]}...)")
        
        # Get statistics
        print("\n📊 Access Statistics:")
        stats = fag.get_access_statistics()
        
        print(f"\n  Total Attempts:    {stats['total_attempts']}")
        print(f"  ✓ Granted (SEAL):  {stats['total_granted']}")
        print(f"  ✗ Denied (VOID):   {stats['total_denied']}")
        print(f"  Success Rate:      {stats['success_rate']}%")
        
        print(f"\n  Denial Breakdown:")
        print(f"    F1 Amanah (jail/permission): {stats['f1_amanah_fail']}")
        print(f"    F2 Truth (not found):        {stats['f2_truth_fail']}")
        print(f"    F4 DeltaS (binary/encoding): {stats['f4_delta_s_fail']}")
        print(f"    F7 Omega0 (unexpected):      {stats['f7_omega0_alert']}")
        print(f"    F9 C_dark (forbidden):       {stats['f9_c_dark_fail']}")
        
        print("\n" + "=" * 70)


def demo_audit_file():
    """Demonstrate audit file logging."""
    print("\nDEMO 2: Audit File Logging")
    print("=" * 70)
    
    # Create temporary workspace
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        audit_path = tmp_path / "security_audit.jsonl"
        
        # Create test files
        (tmp_path / "public.txt").write_text("OK")
        (tmp_path / ".env").write_text("SECRET")
        (tmp_path / "id_rsa").write_text("PRIVATE_KEY")
        
        # Initialize FAG with audit logging
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            audit_file_path=str(audit_path),
            job_id="security-scan-001",
        )
        
        print("\n📝 Audit Logging Enabled:")
        print(f"  Audit File: {audit_path.name}")
        print(f"  Job ID: security-scan-001")
        
        print("\n🔐 Simulating Security-Sensitive Access Attempts...")
        
        # Mix of allowed and denied
        fag.read("public.txt")     # SEAL - not logged to audit
        fag.read(".env")           # VOID - logged to audit
        fag.read("id_rsa")         # VOID - logged to audit
        fag.read("missing.json")   # VOID - logged to audit
        
        print(f"\n  ✓ public.txt → SEAL (not logged to audit)")
        print(f"  ✗ .env → VOID (logged to audit)")
        print(f"  ✗ id_rsa → VOID (logged to audit)")
        print(f"  ✗ missing.json → VOID (logged to audit)")
        
        # Read audit file
        print(f"\n📋 Audit File Contents ({audit_path.name}):")
        print("  " + "-" * 66)
        
        with open(audit_path, "r") as f:
            for i, line in enumerate(f, 1):
                entry = json.loads(line)
                print(f"\n  Entry #{i}:")
                print(f"    Timestamp: {entry['timestamp']}")
                print(f"    Path: {entry['path']}")
                print(f"    Verdict: {entry['verdict']}")
                print(f"    Reason: {entry['reason'][:50]}...")
        
        print("\n  " + "-" * 66)
        print(f"\n  ℹ Note: Only VOID verdicts (denied access) are logged to audit file.")
        print(f"  ℹ SEAL verdicts (granted) are logged to Cooling Ledger only.")
        
        print("\n" + "=" * 70)


def demo_use_case_security_monitoring():
    """Demonstrate practical security monitoring use case."""
    print("\nDEMO 3: Practical Security Monitoring")
    print("=" * 70)
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Simulate a monitored codebase
        (tmp_path / "app.py").write_text("# Main app")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / ".env").write_text("SECRET")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        
        fag = FAG(
            root=str(tmp_path),
            enable_ledger=False,
            enable_audit_file=True,
            job_id="ai-agent-session",
        )
        
        print("\n🤖 AI Agent Reading Codebase...")
        print("  (FAG monitoring all file access)")
        
        # Simulate AI agent reading files
        fag.read("app.py")         # OK
        fag.read("config.json")    # OK
        fag.read(".env")           # BLOCKED
        fag.read(".git/config")    # BLOCKED
        
        # Get statistics
        stats = fag.get_access_statistics()
        
        print(f"\n🛡️ Security Monitor Report:")
        print(f"\n  Files Accessed: {stats['total_attempts']}")
        print(f"  ✓ Safe Access: {stats['total_granted']}")
        print(f"  🚨 Blocked (Sensitive): {stats['f9_c_dark_fail']}")
        
        if stats['f9_c_dark_fail'] > 0:
            print(f"\n  ⚠️ WARNING: AI agent attempted to access {stats['f9_c_dark_fail']} sensitive file(s)!")
            print(f"  ℹ Review audit file for details: fag_audit.jsonl")
        
        print("\n" + "=" * 70)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FAG v41.0.0 - Statistics & Audit Demo")
    print("arifOS Constitutional File Access Governance")
    print("=" * 70)
    
    demo_statistics()
    demo_audit_file()
    demo_use_case_security_monitoring()
    
    print("\n✅ Demo Complete!")
    print("\nKey Features:")
    print("  1. ✓ Access statistics by floor violation type")
    print("  2. ✓ Separate audit file for security events")
    print("  3. ✓ Real-time monitoring for AI agent file access")
    print("\nDITEMPA BUKAN DIBERI - Forged, not given\n")
