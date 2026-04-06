#!/usr/bin/env python3
"""
aCLIp — arifOS Constitutional Layer Interface (CLI)
Exactly 9 commands for constitutional GitOps, agent governance, and code analysis.

The 9 Commands:
    1. aclip worktree add <agent> <feature>   Create F1 sandbox
    2. aclip worktree rm <branch>              Collapse → VOID
    3. aclip worktree list                     Show all worktrees
    4. aclip agent run [--stage]               Execute with F7 dry_run
    5. aclip f3 eval [--enforce]               Tri-Witness evaluation
    6. aclip graph build [--output]            CodeGraph dependency analysis
    7. aclip graph view [--worktree]           View code structure summary
    8. aclip ingest local [path]               GitIngest local worktree
    9. aclip ingest remote <github-url>        GitIngest remote repo

Tools Integrated:
    - Git worktrees (F1 sandboxes)
    - CodeGraph (dependency analysis)
    - GitIngest (LLM context generation)
    - arifOS F3 evaluation (Tri-Witness)

Exit codes:
    0 = Success (verdict executed)
    1 = Config error
    2 = Enforce violated (--enforce with low W₃)
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Constants
ARIFOS_ROOT = Path(__file__).parent.parent
TOOLCHAIN = ARIFOS_ROOT / "scripts" / "constitutional-gitops"
TEMPLATES = ARIFOS_ROOT / "templates"
VERSION = "2026.03.24"


def run_tool(script_name: str, args: list) -> int:
    """Execute a toolchain script"""
    script_path = TOOLCHAIN / script_name
    if not script_path.exists():
        print(f"❌ Error: {script_name} not found")
        return 1
    
    # On Windows, we must explicitly call python for .py files
    cmd = [str(script_path)] + args
    if script_path.suffix == ".py":
        cmd = [sys.executable] + cmd
        
    result = subprocess.run(cmd)
    return result.returncode


# ═══════════════════════════════════════════════════════════════════
# COMMAND 1-3: worktree (add, rm, list)
# ═══════════════════════════════════════════════════════════════════

def cmd_worktree_add(args):
    """1. aclip worktree add <agent> <feature> — Create F1 sandbox"""
    return run_tool("arifos-worktree-add.sh", [args.agent, args.feature])


def cmd_worktree_rm(args):
    """2. aclip worktree rm <branch> — Collapse universe → VOID"""
    return run_tool("arifos-worktree-remove.sh", [args.branch])


def cmd_worktree_list(args):
    """3. aclip worktree list — Show all constitutional worktrees"""
    result = subprocess.run(["git", "worktree", "list"])
    return result.returncode


# ═══════════════════════════════════════════════════════════════════
# COMMAND 4: agent run
# ═══════════════════════════════════════════════════════════════════

def cmd_agent_run(args):
    """4. aclip agent run [--stage] — Execute with F7 dry_run"""
    stage = args.stage or "dev"
    return run_tool("arifos-agent-run.sh", [stage])


# ═══════════════════════════════════════════════════════════════════
# COMMAND 5: f3 eval
# ═══════════════════════════════════════════════════════════════════

def cmd_f3_eval(args):
    """5. aclip f3 eval [--enforce] — Compute Tri-Witness (F3)"""
    cmd_args = []
    if args.worktree:
        cmd_args.extend(["--worktree", args.worktree])
    if args.mode:
        cmd_args.extend(["--mode", args.mode])
    if args.json:
        cmd_args.append("--json")
    if args.enforce:
        cmd_args.append("--enforce")
    if args.update_manifest:
        cmd_args.append("--update-manifest")
    return run_tool("arifos_f3_eval.py", cmd_args)


# ═══════════════════════════════════════════════════════════════════
# COMMAND 6-7: graph (CodeGraph integration)
# ═══════════════════════════════════════════════════════════════════

def cmd_graph_build(args):
    """6. aclip graph build [--output] — CodeGraph dependency analysis"""
    try:
        from codegraph import CodeGraph
        
        path = args.path or "."
        output = args.output or "codegraph.json"
        
        print(f"🔥 Building CodeGraph for: {path}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Initialize CodeGraph
        cg = CodeGraph(root_path=path)
        
        # Build graph
        cg.build()
        
        # Export to JSON
        cg.export(output)
        
        print(f"✅ CodeGraph built: {output}")
        print(f"   Modules: {len(cg.modules)}")
        print(f"   Dependencies: {len(cg.edges)}")
        return 0
    except ImportError:
        print("❌ codegraph not installed. Run: pip install codegraph")
        print("   Or: pip install git+https://github.com/xnuinside/codegraph.git")
        return 1
    except Exception as e:
        print(f"❌ CodeGraph build failed: {e}")
        return 1


def cmd_graph_view(args):
    """7. aclip graph view [--worktree] — View code structure summary"""
    try:
        import json
        
        path = args.worktree or "."
        graph_file = Path(path) / "codegraph.json"
        
        if not graph_file.exists():
            print(f"⚠️  No codegraph.json found at {path}")
            print("   Run: aclip graph build [--output codegraph.json]")
            return 1
        
        with open(graph_file) as f:
            graph = json.load(f)
        
        print("🔥 CODEGRAPH STRUCTURE SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Show modules
        modules = graph.get("modules", [])
        print(f"\n📦 Modules ({len(modules)}):")
        for mod in modules[:10]:  # Show first 10
            print(f"   • {mod.get('name', 'unknown')}")
        if len(modules) > 10:
            print(f"   ... and {len(modules) - 10} more")
        
        # Show dependencies
        deps = graph.get("dependencies", [])
        print(f"\n🔗 Dependencies ({len(deps)}):")
        
        # Find hot spots (high fan-in)
        fan_in = {}
        for dep in deps:
            target = dep.get("target", "")
            fan_in[target] = fan_in.get(target, 0) + 1
        
        hot_spots = sorted(fan_in.items(), key=lambda x: x[1], reverse=True)[:5]
        if hot_spots:
            print("   Hot spots (high fan-in):")
            for mod, count in hot_spots:
                print(f"      {mod}: {count} references")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return 0
    except Exception as e:
        print(f"❌ Graph view failed: {e}")
        return 1


# ═══════════════════════════════════════════════════════════════════
# COMMAND 8-9: ingest (GitIngest)
# ═══════════════════════════════════════════════════════════════════

def cmd_ingest_local(args):
    """8. aclip ingest local [path] — GitIngest local worktree"""
    try:
        from gitingest import ingest
        
        path = args.path or "."
        print(f"🔥 Ingesting local worktree: {path}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        result = ingest(
            path_or_url=path,
            include_patterns=args.include,
            exclude_patterns=args.exclude,
            max_file_size=args.max_size * 1024 if args.max_size else None
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"✅ Ingested to: {args.output}")
        else:
            print(result)
        
        return 0
    except ImportError:
        print("❌ gitingest not installed. Run: pip install gitingest")
        return 1
    except Exception as e:
        print(f"❌ Ingest failed: {e}")
        return 1


def cmd_ingest_remote(args):
    """9. aclip ingest remote <github-url> — GitIngest remote repo"""
    try:
        from gitingest import ingest
        
        print(f"🔥 Ingesting remote repo: {args.url}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        result = ingest(
            path_or_url=args.url,
            include_patterns=args.include,
            exclude_patterns=args.exclude,
            max_file_size=args.max_size * 1024 if args.max_size else None
        )
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            print(f"✅ Ingested to: {args.output}")
        else:
            print(result)
        
        return 0
    except ImportError:
        print("❌ gitingest not installed. Run: pip install gitingest")
        return 1
    except Exception as e:
        print(f"❌ Ingest failed: {e}")
        return 1


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="aclip",
        description="aCLIp — arifOS Constitutional Layer Interface (9 Commands)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
The 9 Commands:
  1. worktree add <agent> <feature>    Create F1 sandbox (Git worktree)
  2. worktree rm <branch>              Collapse → VOID
  3. worktree list                     Show worktrees
  4. agent run [--stage]               Execute with F7
  5. f3 eval [--enforce]               Tri-Witness evaluation
  6. graph build [--output]            CodeGraph dependency analysis
  7. graph view [--worktree]           View code structure
  8. ingest local [path]               GitIngest local
  9. ingest remote <url>               GitIngest remote

Tools: Git worktrees + CodeGraph + GitIngest + arifOS F3
Constitutional Floors: F1-F13
Tri-Witness: W₃ = (H × A × E)^(1/3)
Exit codes: 0=success, 1=config-error, 2=enforce-violated

Ditempa bukan diberi.
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # ═══════════════════════════════════════════════════════════════
    # 1-3: worktree
    # ═══════════════════════════════════════════════════════════════
    worktree_parser = subparsers.add_parser("worktree", help="1-3. Manage F1 sandboxes")
    worktree_sub = worktree_parser.add_subparsers(dest="worktree_cmd")
    
    # 1. worktree add
    add_p = worktree_sub.add_parser("add", help="1. Create F1 sandbox")
    add_p.add_argument("agent", help="Agent name (claude, codex, etc.)")
    add_p.add_argument("feature", help="Feature slug")
    add_p.set_defaults(func=cmd_worktree_add)
    
    # 2. worktree rm
    rm_p = worktree_sub.add_parser("rm", help="2. Collapse → VOID")
    rm_p.add_argument("branch", help="Branch name (feature/xxx)")
    rm_p.set_defaults(func=cmd_worktree_rm)
    
    # 3. worktree list
    list_p = worktree_sub.add_parser("list", help="3. Show worktrees")
    list_p.set_defaults(func=cmd_worktree_list)
    
    # ═══════════════════════════════════════════════════════════════
    # 4: agent
    # ═══════════════════════════════════════════════════════════════
    agent_parser = subparsers.add_parser("agent", help="4. Run agent with F7")
    agent_parser.add_argument("--stage", default="dev", help="Stage (dev/prod)")
    agent_parser.set_defaults(func=cmd_agent_run)
    
    # ═══════════════════════════════════════════════════════════════
    # 5: f3
    # ═══════════════════════════════════════════════════════════════
    f3_parser = subparsers.add_parser("f3", help="5. Tri-Witness evaluation")
    f3_sub = f3_parser.add_subparsers(dest="f3_cmd")
    
    eval_p = f3_sub.add_parser("eval", help="Compute W₃ score")
    eval_p.add_argument("-w", "--worktree", default=".", help="Worktree path")
    eval_p.add_argument("-m", "--mode", choices=["pre-push", "pr-draft", "ci"],
                       default="pre-push", help="Mode")
    eval_p.add_argument("-j", "--json", action="store_true", help="JSON output")
    eval_p.add_argument("-e", "--enforce", action="store_true", help="Exit 2 if below threshold")
    eval_p.add_argument("-u", "--update-manifest", action="store_true", help="Update arifos.yml with evaluation results")
    eval_p.set_defaults(func=cmd_f3_eval)
    
    # ═══════════════════════════════════════════════════════════════
    # 6-7: graph (CodeGraph)
    # ═══════════════════════════════════════════════════════════════
    graph_parser = subparsers.add_parser("graph", help="6-7. CodeGraph analysis")
    graph_sub = graph_parser.add_subparsers(dest="graph_cmd")
    
    # 6. graph build
    build_p = graph_sub.add_parser("build", help="6. Build dependency graph")
    build_p.add_argument("path", nargs="?", default=".", help="Path to analyze")
    build_p.add_argument("-o", "--output", default="codegraph.json", help="Output file")
    build_p.set_defaults(func=cmd_graph_build)
    
    # 7. graph view
    view_p = graph_sub.add_parser("view", help="7. View code structure")
    view_p.add_argument("-w", "--worktree", default=".", help="Worktree path")
    view_p.set_defaults(func=cmd_graph_view)
    
    # ═══════════════════════════════════════════════════════════════
    # 8-9: ingest (GitIngest)
    # ═══════════════════════════════════════════════════════════════
    ingest_parser = subparsers.add_parser("ingest", help="8-9. GitIngest for LLMs")
    ingest_sub = ingest_parser.add_subparsers(dest="ingest_cmd")
    
    # 8. ingest local
    local_p = ingest_sub.add_parser("local", help="8. Ingest local worktree")
    local_p.add_argument("path", nargs="?", default=".", help="Path to ingest")
    local_p.add_argument("-i", "--include", action="append", help="Include patterns")
    local_p.add_argument("-e", "--exclude", action="append", help="Exclude patterns")
    local_p.add_argument("-s", "--max-size", type=int, help="Max file size (KB)")
    local_p.add_argument("-o", "--output", help="Output file")
    local_p.set_defaults(func=cmd_ingest_local)
    
    # 9. ingest remote
    remote_p = ingest_sub.add_parser("remote", help="9. Ingest remote repo")
    remote_p.add_argument("url", help="GitHub URL")
    remote_p.add_argument("-i", "--include", action="append", help="Include patterns")
    remote_p.add_argument("-e", "--exclude", action="append", help="Exclude patterns")
    remote_p.add_argument("-s", "--max-size", type=int, help="Max file size (KB)")
    remote_p.add_argument("-o", "--output", help="Output file")
    remote_p.set_defaults(func=cmd_ingest_remote)
    
    # Parse
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
