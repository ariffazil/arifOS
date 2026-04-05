#!/usr/bin/env python3
"""
arifos_f3_eval.py — Refactored for exact Perplexity spec
Exit codes: 0=executed, 1=config error, 2=--enforce violated
"""

import argparse
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, Tuple, List


# Exit codes per spec
EXIT_SUCCESS = 0      # Command executed, verdict in payload
EXIT_CONFIG = 1       # Configuration error (no arifos.yml, parse failure)
EXIT_ENFORCE = 2      # --enforce violated (verdict VOID or below hold_min)


@dataclass
class WitnessScores:
    """F3 Tri-Witness scores"""
    ai: float = 0.0
    earth: float = 0.0
    human: float = 0.0
    
    def geometric_mean(self) -> float:
        """W₃ = (H × A × E)^(1/3)"""
        if self.ai <= 0 or self.earth <= 0 or self.human <= 0:
            return 0.0
        return (self.ai * self.earth * self.human) ** (1/3)


@dataclass
class VerdictResult:
    """888_JUDGE verdict"""
    verdict: str
    w3: float
    threshold: float
    scores: WitnessScores
    can_push: bool
    recommendation: str


class ArifosF3Eval:
    """F3 Tri-Witness evaluator"""
    
    THRESHOLDS = {
        "low": 0.850,
        "medium": 0.950,
        "high": 0.990,
        "critical": 1.000
    }
    
    HOLD_MIN = 0.700  # Minimum for HOLD (below is VOID)
    
    VERDICTS = ["SEAL", "PROVISIONAL", "SABAR", "HOLD", "HOLD_888", "VOID"]
    
    def __init__(self, worktree: Path):
        self.worktree = worktree
        self.manifest = self._load_manifest()
        
    def _load_manifest(self) -> Dict:
        """Load arifos.yml from worktree"""
        manifest_path = self.worktree / "arifos.yml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"F4: No arifos.yml in {self.worktree}")
        
        try:
            import yaml
            with open(manifest_path) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            return self._parse_yaml_fallback(manifest_path)
    
    def _parse_yaml_fallback(self, path: Path) -> Dict:
        """Simple YAML parser without PyYAML"""
        data = {"agent": {}, "constitutional": {}, "worktree": {}, "governance": {}}
        current_section = None
        
        with open(path) as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                    
                if stripped.endswith(':') and not '=' in stripped:
                    current_section = stripped[:-1].strip()
                    if current_section not in data:
                        data[current_section] = {}
                    continue
                
                if ':' in stripped:
                    key, val = stripped.split(':', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    
                    if current_section and current_section in data:
                        if ':' in val: # Handle nested line like 'key: val'
                             v_key, v_val = val.split(':', 1)
                             data[current_section][v_key.strip()] = v_val.strip().strip('"').strip("'")
                        else:
                             data[current_section][key] = val
                    else:
                        data[key] = val
        
        return data
    
    def _compute_ai_witness(self) -> float:
        """🤖 AI Witness: Agent self-check"""
        score = 0.0
        
        # Check for constitutional kernel usage
        if self._check_code_patterns([r"arifOS_kernel", r"init_anchor", r"apex_soul"]):
            score += 0.25
            
        # F1-F13 awareness
        floor_refs = len(self._grep_lines(r"F[1-9]|F1[0-3]"))
        if floor_refs > 5:
            score += 0.25
        elif floor_refs > 0:
            score += 0.15
            
        # Test coverage
        if list(self.worktree.glob("**/test*")):
            score += 0.20
            
        # Documentation
        if list(self.worktree.glob("**/*.md")):
            score += 0.17
            
        # Conventional commits
        if self._check_conventional_commits():
            score += 0.13
            
        return round(score, 2)
    
    def _compute_earth_witness(self) -> float:
        """🌍 Earth Witness: Local validation"""
        score = 0.0
        
        # Git cleanliness
        if self._git_clean():
            score += 0.25
        elif self._git_unstaged_count() < 5:
            score += 0.10
            
        # Syntax validation
        if self._validate_python_syntax():
            score += 0.25
            
        # Constitutional naming
        branch = self._git_branch()
        if branch and any(branch.startswith(p) for p in ["feature/", "hotfix/", "experiment/"]):
            score += 0.25
            
        # Recent activity
        if self._git_recent_commits(days=7):
            score += 0.25
            
        return round(score, 2)
    
    def _compute_human_witness(self) -> float:
        """👤 Human Witness: Review status"""
        # Priority 1: Check for PsiSeal in governance (Soul Witness)
        governance = self.manifest.get("governance", {})
        psi_seal = governance.get("psi_seal", {})
        if psi_seal:
            return float(psi_seal.get("tri_witness", {}).get("human", 0.0))

        # Priority 2: Check for legacy tri_witness
        tri_witness = governance.get("tri_witness", {})
        status = tri_witness.get("human", "pending")
        
        status_map = {
            "pending": 0.00,
            "partial": 0.50,
            "approved": 1.00,
            "rejected": 0.00
        }
        
        # Signed commit as human attestation
        if self._git_signed_commit():
            return 0.90
            
        return status_map.get(status, 0.00)
    
    def evaluate(self) -> VerdictResult:
        """Run F3 Tri-Witness evaluation"""
        # If we have a PsiSeal, the work is already evaluated by the APEX organ.
        governance = self.manifest.get("governance", {})
        psi_seal = governance.get("psi_seal", {})
        
        if psi_seal:
            tri_witness = psi_seal.get("tri_witness", {})
            ai = float(tri_witness.get("ai", 0.0))
            earth = float(tri_witness.get("earth", 0.0))
            human = float(tri_witness.get("human", 0.0))
        else:
            ai = self._compute_ai_witness()
            earth = self._compute_earth_witness()
            human = self._compute_human_witness()
        
        scores = WitnessScores(ai=ai, earth=earth, human=human)
        w3 = round(scores.geometric_mean(), 3)
        
        risk = self.manifest.get("constitutional", {}).get("max_risk_tier", "medium")
        threshold = self.THRESHOLDS.get(risk, 0.950)
        
        # Determine verdict
        if w3 >= threshold:
            verdict = "SEAL"
            can_push = True
            recommendation = "ready_to_merge"
        elif w3 >= threshold - 0.10:
            verdict = "PROVISIONAL"
            can_push = True
            recommendation = "proceed_with_reservations"
        elif w3 >= 0.800:
            verdict = "SABAR"
            can_push = False
            recommendation = "pause_for_context"
        elif w3 >= self.HOLD_MIN:
            verdict = "HOLD"
            can_push = False
            recommendation = "needs_work"
        else:
            verdict = "VOID"
            can_push = False
            recommendation = "reject_and_fix"
        
        # Override for medium+ risk without human approval
        if risk != "low" and human < 0.5:
            verdict = "HOLD_888"
            can_push = False
            recommendation = "f13_review_required"
        
        return VerdictResult(
            verdict=verdict,
            w3=w3,
            threshold=threshold,
            scores=scores,
            can_push=can_push,
            recommendation=recommendation
        )
    
    def print_report(self, result: VerdictResult, json_mode: bool = False):
        """Print evaluation report"""
        agent = self.manifest.get("agent", {}).get("name", "unknown")
        risk = self.manifest.get("constitutional", {}).get("max_risk_tier", "medium")
        branch = self.manifest.get("worktree", {}).get("branch", "unknown")
        
        if json_mode:
            output = {
                "worktree": str(self.worktree),
                "branch": branch,
                "agent": {
                    "name": agent,
                    "type": self.manifest.get("agent", {}).get("type", "unknown"),
                    "runtime": self.manifest.get("agent", {}).get("runtime", "unknown")
                },
                "witness": {
                    "human": {"raw_status": "pending", "score": result.scores.human},
                    "ai": {"score": result.scores.ai, "source": "heuristic"},
                    "earth": {"score": result.scores.earth, "source": "local_tests"}
                },
                "w3": result.w3,
                "thresholds": {
                    "f3_seal": result.threshold,
                    "hold_min": self.HOLD_MIN
                },
                "verdict": result.verdict,
                "can_push": result.can_push,
                "recommendation": result.recommendation
            }
            print(json.dumps(output, indent=2))
            return
        
        # Human-readable
        emoji = {"SEAL": "✅", "PROVISIONAL": "⚠️", "SABAR": "⏸️", 
                 "HOLD": "🛑", "HOLD_888": "🚨", "VOID": "❌"}.get(result.verdict, "⚖️")
        
        print("")
        print("🔥 F3 TRI-WITNESS EVALUATION")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📁 Worktree: {self.worktree}")
        print(f"🤖 Agent:    {agent}")
        print(f"⚠️  Risk:     {risk}")
        print("")
        print(f"🤖 AI:     {result.scores.ai}")
        print(f"🌍 Earth:  {result.scores.earth}")
        print(f"👤 Human:  {result.scores.human}")
        print("")
        print(f"   W₃ = {result.w3}")
        print(f"   Threshold: {result.threshold}")
        print("")
        print(f"   {emoji} VERDICT: {result.verdict}")
        print(f"   Can push: {result.can_push}")
        print(f"   {result.recommendation}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def update_manifest(self, result: VerdictResult):
        """Update arifos.yml with results"""
        try:
            import yaml
            path = self.worktree / "arifos.yml"
            with open(path) as f:
                data = yaml.safe_load(f)
            
            data.setdefault("governance", {}).setdefault("tri_witness", {})
            data["governance"]["tri_witness"]["ai"] = result.scores.ai
            data["governance"]["tri_witness"]["earth"] = result.scores.earth
            data["governance"]["tri_witness"]["human"] = result.scores.human
            data["governance"]["verdict"] = result.verdict
            data["governance"]["w3"] = result.w3
            
            # Record the evaluation session
            data["governance"]["last_eval"] = {
                "timestamp": self.manifest.get("governance", {}).get("last_eval", {}).get("timestamp", 0) + 1,
                "w3": result.w3,
                "threshold": result.threshold
            }
            
            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except:
            pass
    
    # Helper methods
    def _check_code_patterns(self, patterns: List[str]) -> bool:
        """Search for patterns in code (portable)"""
        try:
            for pattern in patterns:
                # Try git grep first as it's more portable and respects .gitignore
                result = subprocess.run(
                    ["git", "grep", "-E", pattern, "--", "*.py", "*.js"],
                    cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
                )
                if result.returncode == 0 and result.stdout:
                    return True
                
                # Fallback to grep -r if git grep fails
                result = subprocess.run(
                    ["grep", "-r", "-E", pattern, "--include=*.py", "--include=*.js"],
                    cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
                )
                if result.returncode == 0 and result.stdout:
                    return True
            return False
        except:
            return False
    
    def _grep_lines(self, pattern: str) -> List[str]:
        """Grep and return lines (portable)"""
        try:
            result = subprocess.run(
                ["git", "grep", "-E", pattern, "--", "*.py", "*.md"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout.strip().split('\n')
                
            result = subprocess.run(
                ["grep", "-r", "-E", pattern, "--include=*.py", "--include=*.md"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            return result.stdout.strip().split('\n') if result.stdout else []
        except:
            return []
    
    def _check_conventional_commits(self) -> bool:
        """Check for conventional commits"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            commits = result.stdout.lower()
            return any(p in commits for p in ["feat:", "fix:", "docs:", "refactor:", "test:"])
        except:
            return False
    
    def _git_clean(self) -> bool:
        """Check if git is clean"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def _git_unstaged_count(self) -> int:
        """Count unstaged files"""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            return len([l for l in result.stdout.split('\n') if l.strip()])
        except:
            return 0
    
    def _validate_python_syntax(self) -> bool:
        """Validate Python syntax"""
        py_files = list(self.worktree.glob("**/*.py"))[:5]
        for f in py_files:
            try:
                result = subprocess.run(
                    ["python", "-m", "py_compile", str(f)],
                    capture_output=True
                )
                if result.returncode != 0:
                    return False
            except:
                return False
        return True
    
    def _git_branch(self) -> Optional[str]:
        """Get current branch"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _git_recent_commits(self, days: int = 7) -> bool:
        """Check for recent commits"""
        try:
            result = subprocess.run(
                ["git", "log", f"--since={days} days ago", "--oneline"],
                cwd=self.worktree, capture_output=True, text=True, encoding="utf-8"
            )
            return len(result.stdout.strip()) > 0
        except:
            return False
    
    def _git_signed_commit(self) -> bool:
        """Check for signed commits"""
        try:
            result = subprocess.run(
                ["git", "log", "--show-signature", "-1"],
                cwd=self.worktree, capture_output=True, text=True
            )
            return "Good signature" in result.stdout
        except:
            return False


def main():
    parser = argparse.ArgumentParser(
        description="arifos f3-eval — F3 Tri-Witness evaluation"
    )
    parser.add_argument(
        "--worktree", "-w",
        type=Path,
        default=Path("."),
        help="Path to worktree containing arifos.yml (default: .)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["pre-push", "pr-draft", "ci"],
        default="pre-push",
        help="Evaluation mode (default: pre-push)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Emit JSON output only"
    )
    parser.add_argument(
        "--enforce", "-e",
        action="store_true",
        help="Exit 2 if verdict is VOID or below hold_min"
    )
    parser.add_argument(
        "--update-manifest", "-u",
        action="store_true",
        help="Update arifos.yml with evaluation results"
    )
    
    args = parser.parse_args()
    worktree = args.worktree.resolve()
    
    # Validate worktree exists
    if not worktree.exists():
        print(f"❌ Config error: worktree does not exist: {worktree}", file=sys.stderr)
        sys.exit(EXIT_CONFIG)
    
    # Validate manifest exists
    manifest_path = worktree / "arifos.yml"
    if not manifest_path.exists():
        print(f"❌ Config error (F4): No arifos.yml in {worktree}", file=sys.stderr)
        print("   This is not a constitutional worktree.", file=sys.stderr)
        sys.exit(EXIT_CONFIG)
    
    # Run evaluation
    try:
        evaluator = ArifosF3Eval(worktree)
        result = evaluator.evaluate()
        
        # Print report
        evaluator.print_report(result, json_mode=args.json)
        
        # Update manifest if requested
        if args.update_manifest:
            evaluator.update_manifest(result)
        
        # Determine exit code
        if args.enforce:
            if result.verdict == "VOID":
                print(f"\n❌ Enforce: verdict VOID — blocking", file=sys.stderr)
                sys.exit(EXIT_ENFORCE)
            elif result.w3 < evaluator.HOLD_MIN:
                print(f"\n❌ Enforce: W₃ {result.w3} < {evaluator.HOLD_MIN} — blocking", file=sys.stderr)
                sys.exit(EXIT_ENFORCE)
        
        # Normal success
        sys.exit(EXIT_SUCCESS)
        
    except FileNotFoundError as e:
        print(f"❌ Config error: {e}", file=sys.stderr)
        sys.exit(EXIT_CONFIG)
    except Exception as e:
        print(f"❌ Evaluation error: {e}", file=sys.stderr)
        sys.exit(EXIT_CONFIG)


if __name__ == "__main__":
    main()
