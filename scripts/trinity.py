#!/usr/bin/env python3
"""
trinity.py - Universal CLI for Trinity Governance System

Simple, memorable interface for git governance:
- trinity forge <branch>  - Analyze changes
- trinity qc <branch>     - Constitutional check
- trinity seal <branch> <reason> - Seal with approval

Works with ANY AI (ChatGPT, Claude, Gemini, etc.) - just tell them:
"Run: trinity forge my-work"
"""

import sys
import subprocess
from pathlib import Path


VERSION = "43.1.0"


def print_help():
    """Show usage information."""
    print("""
Trinity - Universal Git Governance System v{VERSION}

USAGE:
    trinity <command> [options]

COMMANDS:
    forge <branch>              Analyze git changes (entropy, risk, hot zones)
    qc <branch>                 Constitutional quality control (F1-F9 validation)
    seal <branch> <reason>      Seal changes with human authority
    
    help                        Show this help message
    version                     Show version

EXAMPLES:
    trinity forge my-feature
    trinity qc my-feature
    trinity seal my-feature "Feature complete and tested"

SHORTCUTS:
    You can also use: /gitforge, /gitQC, /gitseal (for AI assistants)

MORE INFO:
    See: L1_THEORY/canon/03_runtime/FORGING_PROTOCOL_v43.md
    GitHub: https://github.com/ariffazil/arifOS

Built for accessibility. Forged, not given.
""".format(VERSION=VERSION))


def get_repo_root():
    """Find repository root (where scripts/ directory is)."""
    # Start from current file location
    current = Path(__file__).parent.parent
    
    # If we're already in repo root, use it
    if (current / "scripts").exists():
        return current
    
    # Otherwise use current directory
    return Path.cwd()


def run_forge(branch, base="main"):
    """Execute /gitforge analysis."""
    repo_root = get_repo_root()
    script = repo_root / "scripts" / "git_forge.py"
    
    if not script.exists():
        print(f"❌ Error: Cannot find {script}")
        print(f"   Make sure you're running from arifOS repository root")
        return 1
    
    args = ["python", str(script), "--branch", branch]
    if base != "main":
        args.extend(["--base", base])
    
    result = subprocess.run(args, cwd=repo_root)
    return result.returncode


def run_qc(branch):
    """Execute /gitQC constitutional validation."""
    repo_root = get_repo_root()
    script = repo_root / "scripts" / "git_qc.py"
    
    if not script.exists():
        print(f"❌ Error: Cannot find {script}")
        print(f"   Make sure you're running from arifOS repository root")
        return 1
    
    args = ["python", str(script), "--branch", branch]
    
    result = subprocess.run(args, cwd=repo_root)
    return result.returncode


def run_seal(branch, reason, human="Unknown"):
    """Execute /gitseal with human authority."""
    repo_root = get_repo_root()
    script = repo_root / "scripts" / "git_seal.py"
    
    if not script.exists():
        print(f"❌ Error: Cannot find {script}")
        print(f"   Make sure you're running from arifOS repository root")
        return 1
    
    # Detect human from git config if not provided
    if human == "Unknown":
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                check=True
            )
            human = result.stdout.strip()
        except:
            human = "Unknown"
    
    args = [
        "python", str(script),
        "APPROVE",
        "--branch", branch,
        "--human", human,
        "--reason", reason
    ]
    
    result = subprocess.run(args, cwd=repo_root)
    return result.returncode


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("❌ Error: No command specified")
        print("   Run: trinity help")
        return 1
    
    command = sys.argv[1].lower()
    
    # Help and version
    if command in ["help", "-h", "--help"]:
        print_help()
        return 0
    
    if command in ["version", "-v", "--version"]:
        print(f"Trinity v{VERSION}")
        return 0
    
    # Forge command
    if command in ["forge", "gitforge", "/gitforge"]:
        if len(sys.argv) < 3:
            print("❌ Error: Missing branch name")
            print("   Usage: trinity forge <branch>")
            return 1
        
        branch = sys.argv[2]
        base = sys.argv[3] if len(sys.argv) > 3 else "main"
        return run_forge(branch, base)
    
    # QC command
    if command in ["qc", "gitqc", "/gitqc"]:
        if len(sys.argv) < 3:
            print("❌ Error: Missing branch name")
            print("   Usage: trinity qc <branch>")
            return 1
        
        branch = sys.argv[2]
        return run_qc(branch)
    
    # Seal command
    if command in ["seal", "gitseal", "/gitseal"]:
        if len(sys.argv) < 4:
            print("❌ Error: Missing branch or reason")
            print("   Usage: trinity seal <branch> <reason>")
            print('   Example: trinity seal my-work "Feature complete"')
            return 1
        
        branch = sys.argv[2]
        reason = " ".join(sys.argv[3:])  # Join all remaining args as reason
        
        return run_seal(branch, reason)
    
    # Unknown command
    print(f"❌ Error: Unknown command '{command}'")
    print("   Run: trinity help")
    return 1


if __name__ == "__main__":
    sys.exit(main())
