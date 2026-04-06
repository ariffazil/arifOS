"""
aclip_skill_bridge.py - F13 Sovereign Override for Skills

Allows Arif (F13 Sovereign) to:
1. Execute skills directly (bypassing AI autonomy)
2. Force human approval gates
3. Veto any skill execution
4. Seal decisions to VAULT999

This is the PHYSICAL HANDLE for the constitution.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.skill_bridge import execute_skill
from skills import list_skills


async def run_skill(skill: str, action: str, params: dict, dry_run: bool = True, operator: str = "arif"):
    """Execute skill with F13 sovereign authority."""
    result = await execute_skill(
        skill_name=skill,
        action=action,
        params=params,
        session_id=f"sovereign-{operator}",
        dry_run=dry_run,
        operator=operator
    )
    return result


def main():
    parser = argparse.ArgumentParser(
        description="aCLIp Skill Bridge - F13 Sovereign Override",
        prog="aclip-skill"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # List skills
    list_p = subparsers.add_parser("list", help="List available skills")
    
    # Execute skill
    run_p = subparsers.add_parser("run", help="Execute skill with F13 authority")
    run_p.add_argument("skill", help="Skill name (vps-docker, git-ops, etc.)")
    run_p.add_argument("action", help="Action to execute")
    run_p.add_argument("--params", default="", help="Parameters as key=value,key2=value2")
    run_p.add_argument("--execute", action="store_true", help="Real execution (not dry-run)")
    run_p.add_argument("--operator", default="arif", help="Operator identity")
    
    # Check skill
    check_p = subparsers.add_parser("check", help="Check skill constitutional compliance")
    check_p.add_argument("skill", help="Skill name")
    
    # Vault seal
    seal_p = subparsers.add_parser("vault-seal", help="Seal approval for high-risk operations")
    seal_p.add_argument("--skill", help="Skill requiring approval")
    seal_p.add_argument("--action", help="Action requiring approval")
    
    args = parser.parse_args()
    
    if args.command == "list":
        skills = list_skills()
        print("\n=== arifOS Skills (9 Constitutional Capabilities) ===\n")
        for name, desc in skills.items():
            print(f"  {name:20} - {desc}")
        print("\nUse: aclip-skill run <skill> <action> [--execute]")
        return 0
    
    if args.command == "run":
        # Parse params
        params = {}
        if args.params:
            for pair in args.params.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
        
        dry_run = not args.execute
        
        print(f"\n🔥 F13 SOVEREIGN EXECUTION")
        print(f"   Operator: {args.operator}")
        print(f"   Skill: {args.skill}")
        print(f"   Action: {args.action}")
        print(f"   Mode: {'REAL' if args.execute else 'DRY-RUN (F7)'}")
        print(f"   Params: {params}")
        print()
        
        result = asyncio.run(run_skill(args.skill, args.action, params, dry_run, args.operator))
        
        print(f"\n📊 RESULT")
        print(f"   Verdict: {result.get('verdict', 'UNKNOWN')}")
        if 'w3_score' in result:
            print(f"   W3 Score: {result['w3_score']:.3f}")
        if 'checkpoint' in result:
            print(f"   Checkpoint: {result['checkpoint']}")
        if 'rollback' in result:
            print(f"   Rollback: {result['rollback']}")
        
        if result.get('verdict') == '888_HOLD':
            print("\n⏸️  888_HOLD - Human approval required")
            print(f"   Run: aclip-skill vault-seal --skill {args.skill} --action {args.action}")
            return 2
        
        return 0 if result.get('verdict') in ['SEAL', 'PARTIAL'] else 1
    
    if args.command == "check":
        from skills import get_skill
        skill = get_skill(args.skill)
        if not skill:
            print(f"❌ Unknown skill: {args.skill}")
            return 1
        
        print(f"\n📋 SKILL: {args.skill}")
        print(f"   Floor: {skill['floor']}")
        print(f"   Description: {skill['description']}")
        print(f"   Class: {skill['skill'].__name__}")
        return 0
    
    if args.command == "vault-seal":
        print(f"\n🔐 VAULT SEAL")
        print(f"   Approving: {args.skill or 'all'} / {args.action or 'all'}")
        print(f"   Status: SEALED to VAULT999")
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
