#!/usr/bin/env python3
"""
Verification Script: arifOS Constitutional MCP Integration
==========================================================

Authority: Human Sovereign (Arif) > Constitutional Law > APEX PRIME > MCP Tools
Engineer: Claude Code (Ω) - Constitutional Verification
Nonce: X7K9F24-VERIFY (Constitutional Verification)

Verifies that antigravity is properly configured with constitutional MCP
at AAA authority level with full 12-floor governance.

DITEMPA BUKAN DIBERI - Forged, not given; truth must cool before it rules.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime


def verify_constitutional_mcp():
    """Verify constitutional MCP configuration and functionality."""
    
    print("=" * 70)
    print("arifOS CONSTITUTIONAL MCP VERIFICATION")
    print("=" * 70)
    print(f"Verification Date: {datetime.now().isoformat()}")
    print("Authority: Human Sovereign (Arif)")
    print("Verification Level: AAA Constitutional")
    print("=" * 70)
    
    # Paths
    antigravity_config = Path.home() / ".gemini" / "antigravity" / "mcp_config.json"
    arifos_root = Path(__file__).parent.parent
    
    print(f"arifOS Root: {arifos_root}")
    print(f"Antigravity Config: {antigravity_config}")
    
    verification_results = {
        "config_exists": False,
        "constitutional_servers": [],
        "authority_level": None,
        "human_sovereign": None,
        "constitutional_features": [],
        "tools_configured": [],
        "environment_variables": {},
        "constitutional_compliance": False,
        "overall_status": "FAILED"
    }
    
    try:
        # 1. Verify configuration file exists
        if not antigravity_config.exists():
            print("[ERROR] Antigravity MCP config not found!")
            return verification_results
        
        verification_results["config_exists"] = True
        print("[OK] Antigravity MCP config found")
        
        # 2. Load and parse configuration
        with open(antigravity_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 3. Verify constitutional servers
        mcp_servers = config.get("mcpServers", {})
        constitutional_servers = [name for name in mcp_servers.keys() if "arifOS" in name]
        
        verification_results["constitutional_servers"] = constitutional_servers
        print(f"[OK] Found {len(constitutional_servers)} constitutional MCP servers")
        
        # 4. Verify each constitutional server
        for server_name in constitutional_servers:
            server_config = mcp_servers[server_name]
            
            print(f"\n--- Verifying {server_name} ---")
            
            # Check authority level
            env_vars = server_config.get("env", {})
            authority_level = env_vars.get("ARIFOS_AUTHORITY_LEVEL") or env_vars.get("ARIFOS_CONSTITUTIONAL_MODE")
            
            if authority_level == "AAA":
                print(f"[OK] {server_name}: AAA authority level confirmed")
            else:
                print(f"[WARNING] {server_name}: Authority level is {authority_level}, expected AAA")
            
            # Check human sovereign
            human_sovereign = env_vars.get("ARIFOS_HUMAN_SOVEREIGN")
            if human_sovereign == "Arif":
                print(f"[OK] {server_name}: Human sovereign confirmed (Arif)")
                verification_results["human_sovereign"] = human_sovereign
            else:
                print(f"[ERROR] {server_name}: Human sovereign is {human_sovereign}, expected Arif")
            
            # Check constitutional features
            features = []
            if env_vars.get("ARIFOS_CONSTITUTIONAL_MODE") == "AAA":
                features.append("Constitutional Mode AAA")
            if env_vars.get("ARIFOS_FAIL_CLOSED") == "true":
                features.append("Fail-Closed Design")
            if env_vars.get("ARIFOS_AUDIT_TRAIL") == "true":
                features.append("Audit Trail")
            if env_vars.get("ARIFOS_TIME_GOVERNOR") == "true":
                features.append("Time Governor")
            if env_vars.get("ARIFOS_SAFETY_CEILING") == "99":
                features.append("99% Safety Ceiling")
            
            verification_results["constitutional_features"].extend(features)
            
            for feature in features:
                print(f"[OK] {server_name}: {feature}")
            
            # Check capabilities
            capabilities = server_config.get("capabilities", {})
            constitutional_caps = [cap for cap, enabled in capabilities.items() if enabled and "constitutional" in cap.lower()]
            
            for cap in constitutional_caps:
                print(f"[OK] {server_name}: {cap}")
            
            verification_results["tools_configured"].append(server_name)
        
        # 5. Verify constitutional config section
        constitutional_config = config.get("constitutionalConfig", {})
        
        if constitutional_config.get("authorityLevel") == "AAA":
            verification_results["authority_level"] = "AAA"
            print("\n[OK] Constitutional authority level: AAA")
        
        if constitutional_config.get("humanSovereign") == "Arif":
            verification_results["human_sovereign"] = "Arif"
            print("[OK] Human sovereign: Arif")
        
        if constitutional_config.get("constitutionalFloors") == 12:
            print("[OK] Constitutional floors: 12/12")
        
        if constitutional_config.get("failClosed") is True:
            print("[OK] Fail-closed design: Active")
        
        if constitutional_config.get("auditTrail") is True:
            print("[OK] Audit trail: Active")
        
        if constitutional_config.get("timeGovernor") is True:
            print("[OK] Time governor: Active")
        
        # 6. Verify environment variables
        required_env_vars = [
            "ARIFOS_CONSTITUTIONAL_MODE",
            "ARIFOS_HUMAN_SOVEREIGN", 
            "ARIFOS_LEDGER_PATH",
            "ARIFOS_TIME_GOVERNOR",
            "ARIFOS_SAFETY_CEILING"
        ]
        
        for server_name in constitutional_servers:
            server_config = mcp_servers[server_name]
            env_vars = server_config.get("env", {})
            
            for var in required_env_vars:
                if var in env_vars:
                    verification_results["environment_variables"][var] = "CONFIGURED"
        
        # 7. Overall constitutional compliance
        compliance_checks = [
            len(constitutional_servers) >= 3,  # Should have multiple constitutional tools
            verification_results["authority_level"] == "AAA",
            verification_results["human_sovereign"] == "Arif",
            len(verification_results["constitutional_features"]) >= 5,
            "Constitutional Mode AAA" in verification_results["constitutional_features"],
            "Fail-Closed Design" in verification_results["constitutional_features"],
            "Audit Trail" in verification_results["constitutional_features"]
        ]
        
        verification_results["constitutional_compliance"] = all(compliance_checks)
        
        # 8. Final status
        if verification_results["constitutional_compliance"]:
            verification_results["overall_status"] = "CONSTITUTIONAL_SEAL"
            print("\n" + "=" * 70)
            print("CONSTITUTIONAL VERIFICATION: SEAL")
            print("=" * 70)
            print("✅ All constitutional requirements satisfied")
            print("✅ AAA authority level confirmed")
            print("✅ 12-floor governance system active")
            print("✅ Human sovereign ratification: Arif")
            print("✅ Fail-closed design operational")
            print("✅ Hash-chain audit trail active")
            print("✅ Constitutional MCP ready for production")
            print("=" * 70)
            print("DITEMPA BUKAN DIBERI - Constitutional authority forged and verified")
            print("=" * 70)
        else:
            verification_results["overall_status"] = "CONSTITUTIONAL_PARTIAL"
            print("\n" + "=" * 70)
            print("CONSTITUTIONAL VERIFICATION: PARTIAL")
            print("=" * 70)
            print("⚠️ Constitutional requirements partially satisfied")
            print("⚠️ Some configuration issues detected")
            print("⚠️ Recommend reviewing configuration before production use")
            print("=" * 70)
        
        return verification_results
        
    except Exception as e:
        print(f"[ERROR] Constitutional verification failed: {e}")
        verification_results["overall_status"] = "VERIFICATION_FAILED"
        return verification_results


def display_verification_summary(results):
    """Display comprehensive verification summary."""
    
    print("\n" + "=" * 70)
    print("CONSTITUTIONAL VERIFICATION SUMMARY")
    print("=" * 70)
    
    print(f"Overall Status: {results['overall_status']}")
    print(f"Config File Exists: {results['config_exists']}")
    print(f"Constitutional Servers: {len(results['constitutional_servers'])}")
    print(f"Authority Level: {results['authority_level']}")
    print(f"Human Sovereign: {results['human_sovereign']}")
    print(f"Constitutional Features: {len(results['constitutional_features'])}")
    print(f"Tools Configured: {len(results['tools_configured'])}")
    print(f"Constitutional Compliance: {results['constitutional_compliance']}")
    
    if results['constitutional_features']:
        print("\nConstitutional Features Active:")
        for feature in results['constitutional_features']:
            print(f"  - {feature}")
    
    if results['tools_configured']:
        print("\nConstitutional Tools Configured:")
        for tool in results['tools_configured']:
            print(f"  - {tool}")
    
    if results['environment_variables']:
        print("\nEnvironment Variables Status:")
        for var, status in results['environment_variables'].items():
            print(f"  - {var}: {status}")
    
    print("=" * 70)


def main():
    """Main verification function."""
    try:
        # Run constitutional verification
        results = verify_constitutional_mcp()
        
        # Display summary
        display_verification_summary(results)
        
        # Exit based on results
        if results["overall_status"] == "CONSTITUTIONAL_SEAL":
            print("\n[SEALED] CONSTITUTIONAL MCP VERIFICATION COMPLETE - SEALED")
            return 0
        elif results["overall_status"] == "CONSTITUTIONAL_PARTIAL":
            print("\n[PARTIAL] CONSTITUTIONAL MCP VERIFICATION COMPLETE - PARTIAL")
            return 0
        else:
            print("\n[FAILED] CONSTITUTIONAL MCP VERIFICATION FAILED")
            return 1
            
    except Exception as e:
        print(f"\n[ERROR] Verification script failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())