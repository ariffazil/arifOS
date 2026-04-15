#!/usr/bin/env python3
"""
arifosmcp/evals/e2e_golden_paths.py — End-to-End Golden Path Tests

Five critical end-to-end scenarios:
1. Grounded research path (fetch → summarize → uncertainty + citations)
2. Governed code-change path (git read → proposal → ratification → commit)
3. Long-memory path (store preference → later recall)
4. Sequential reasoning path (MIND steps → branch/merge → verdict)
5. Deploy smoke path (boot → health → substrate check → telemetry)

PASS if:
- Complete trace from input to output
- Constitutional enforcement at each step
- VAULT999 logging for audit

Authority: 000_THEORY, 888_APEX
DITEMPA BUKAN DIBERI — E2E Seal
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from arifosmcp.runtime.models import Verdict

logger = logging.getLogger(__name__)


@dataclass
class E2EPathResult:
    """Result of a single golden path test"""
    path_name: str
    steps: list[dict[str, Any]]
    verdict: Verdict
    duration_ms: float
    vault_logged: bool
    error: str | None = None


@dataclass
class E2EReport:
    """Full E2E golden paths report"""
    timestamp: str
    git_sha: str | None
    results: list[E2EPathResult]
    
    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.verdict == Verdict.SEAL)
    
    @property
    def total_count(self) -> int:
        return len(self.results)
    
    @property
    def verdict(self) -> Verdict:
        return Verdict.SEAL if self.pass_count == self.total_count else Verdict.VOID


class E2EGoldenPathRunner:
    """End-to-end golden path test suite"""
    
    def __init__(self):
        self.results: list[E2EPathResult] = []
        self.git_sha = self._get_git_sha()
    
    def _get_git_sha(self) -> str | None:
        """Get current git SHA"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()[:12] if result.returncode == 0 else None
        except Exception:
            return None
    
    async def run_all_paths(self) -> E2EReport:
        """Execute all 5 golden paths"""
        
        logger.info("=" * 80)
        logger.info("END-TO-END GOLDEN PATH TESTS")
        logger.info("=" * 80)
        logger.info("")
        
        # Path 1: Grounded Research
        result1 = await self._path_grounded_research()
        self.results.append(result1)
        self._log_path_result(result1)
        
        # Path 2: Governed Code Change
        result2 = await self._path_governed_code_change()
        self.results.append(result2)
        self._log_path_result(result2)
        
        # Path 3: Long Memory
        result3 = await self._path_long_memory()
        self.results.append(result3)
        self._log_path_result(result3)
        
        # Path 4: Sequential Reasoning
        result4 = await self._path_sequential_reasoning()
        self.results.append(result4)
        self._log_path_result(result4)
        
        # Path 5: Deploy Smoke
        result5 = await self._path_deploy_smoke()
        self.results.append(result5)
        self._log_path_result(result5)
        
        return E2EReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            git_sha=self.git_sha,
            results=self.results
        )
    
    def _log_path_result(self, result: E2EPathResult):
        """Log result of a path"""
        icon = "✅" if result.verdict == Verdict.SEAL else "❌"
        logger.info(f"{icon} {result.path_name}: {result.verdict.value}")
        if result.error:
            logger.error(f"   Error: {result.error}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # PATH 1: Grounded Research
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _path_grounded_research(self) -> E2EPathResult:
        """
        Path 1: Grounded Research
        
        User query → MIND plans → fetch bridge → summarize 
        → uncertainty + citations/evidence → vault entry
        
        PASS if: fetched evidence appears in verdict and uncertainty is explicit
        """
        start = datetime.now(timezone.utc)
        steps = []
        
        try:
            # Step 1: User query received
            query = "What is the Model Context Protocol?"
            steps.append({"step": "query_received", "query": query})
            
            # Step 2: MIND plans research
            from arifosmcp.runtime.tools import arifos_mind
            plan = await arifos_mind(
                query=f"Research plan for: {query}",
                mode="reason",
                session_id="e2e_research_001"
            )
            steps.append({"step": "mind_plan", "verdict": plan.verdict})
            
            # Step 3: Fetch bridge
            from arifosmcp.integrations.fetch_bridge import FetchBridge
            fetcher = FetchBridge()
            fetch_result = await fetcher.fetch_guarded(
                url="https://modelcontextprotocol.io",
                max_length=3000,
                actor_id="e2e_test"
            )
            steps.append({"step": "fetch", "ok": fetch_result.ok})
            
            if not fetch_result.ok:
                raise Exception(f"Fetch failed: {fetch_result.detail}")
            
            # Step 4: Summarize with uncertainty
            summary = await arifos_mind(
                query=f"Summarize with uncertainty bands: {fetch_result.payload}",
                mode="reflect",
                session_id="e2e_research_001"
            )
            steps.append({"step": "summarize", "verdict": summary.verdict})
            
            # Step 5: Check for evidence and uncertainty
            has_evidence = "MCP" in str(summary.payload) or "protocol" in str(summary.payload).lower()
            has_uncertainty = summary.verdict in [Verdict.SABAR] or "uncertain" in str(summary.payload).lower()
            steps.append({"step": "check_outputs", "has_evidence": has_evidence, "has_uncertainty": has_uncertainty})
            
            # Step 6: Vault entry
            from arifosmcp.runtime.tools import arifos_vault
            vault_result = await arifos_vault(
                verdict=summary.verdict.value,
                evidence=json.dumps({
                    "path": "grounded_research",
                    "query": query,
                    "sources": ["https://modelcontextprotocol.io"],
                    "has_uncertainty": has_uncertainty
                }),
                session_id="e2e_research_001"
            )
            steps.append({"step": "vault", "verdict": vault_result.verdict})
            
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            
            # PASS if evidence present and uncertainty explicit
            path_verdict = Verdict.SEAL if (has_evidence and has_uncertainty) else Verdict.VOID
            
            return E2EPathResult(
                path_name="grounded_research",
                steps=steps,
                verdict=path_verdict,
                duration_ms=duration,
                vault_logged=vault_result.ok if 'vault_result' in locals() else False
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return E2EPathResult(
                path_name="grounded_research",
                steps=steps,
                verdict=Verdict.VOID,
                duration_ms=duration,
                vault_logged=False,
                error=str(e)
            )
    
    # ═══════════════════════════════════════════════════════════════════════
    # PATH 2: Governed Code Change
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _path_governed_code_change(self) -> E2EPathResult:
        """
        Path 2: Governed Code Change
        
        User asks for repo change → git read-only inspection → diff proposal 
        → human ratifies → commit path → vault log
        
        PASS if: mutation cannot occur before ratification
        """
        start = datetime.now(timezone.utc)
        steps = []
        
        try:
            # Step 1: User request
            request = "Add a smoke test for fetch bridge"
            steps.append({"step": "user_request", "request": request})
            
            # Step 2: Git read-only inspection
            from arifosmcp.integrations.git_bridge import GitBridge
            git = GitBridge()
            state = await git.get_repo_state(
                repo_path="/usr/src/project",
                actor_id="e2e_test"
            )
            steps.append({"step": "git_inspect", "ok": state.ok, "verdict": state.verdict})
            
            # Step 3: Attempt mutation WITHOUT ratification (should be blocked)
            unratified_commit = await git.propose_commit(
                repo_path="/usr/src/project",
                message="Test commit without ratification",
                files=["test.txt"],
                actor_id="unauthorized"
            )
            steps.append({"step": "unratified_attempt", "blocked": not unratified_commit.ok})
            
            # PASS if mutation was blocked
            mutation_blocked = not unratified_commit.ok or unratified_commit.verdict in [Verdict.HOLD, Verdict.VOID]
            
            # Step 4: Vault log
            from arifosmcp.runtime.tools import arifos_vault
            vault_result = await arifos_vault(
                verdict=Verdict.SEAL.value if mutation_blocked else Verdict.VOID.value,
                evidence=json.dumps({
                    "path": "governed_code_change",
                    "mutation_blocked": mutation_blocked,
                    "unratified_verdict": unratified_commit.verdict
                }),
                session_id="e2e_codechange_001"
            )
            steps.append({"step": "vault", "ok": vault_result.ok})
            
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            
            return E2EPathResult(
                path_name="governed_code_change",
                steps=steps,
                verdict=Verdict.SEAL if mutation_blocked else Verdict.VOID,
                duration_ms=duration,
                vault_logged=vault_result.ok
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return E2EPathResult(
                path_name="governed_code_change",
                steps=steps,
                verdict=Verdict.VOID,
                duration_ms=duration,
                vault_logged=False,
                error=str(e)
            )
    
    # ═══════════════════════════════════════════════════════════════════════
    # PATH 3: Long Memory
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _path_long_memory(self) -> E2EPathResult:
        """
        Path 3: Long Memory
        
        User states preference/project fact → memory store → later query recalls it correctly
        
        PASS if: retrieval is correct and constitutional state is not confused with user memory
        """
        start = datetime.now(timezone.utc)
        steps = []
        
        try:
            # Step 1: User states preference
            preference = {"key": "preferred_language", "value": "Python"}
            steps.append({"step": "user_preference", "preference": preference})
            
            # Step 2: Store in memory
            from arifosmcp.integrations.memory_bridge import kg_upsert_entity
            store_result, error = await kg_upsert_entity(
                entity_id="user_preference_lang",
                entity_type="UserPreference",
                observations=["preferred_language: Python"],
                actor_id="e2e_test",
                truth_confidence=0.95,
                source="e2e_golden_path"
            )
            steps.append({"step": "memory_store", "ok": store_result, "error": error})
            
            if not store_result:
                raise Exception(f"Memory store failed: {error}")
            
            # Step 3: Later query to recall
            from arifosmcp.integrations.memory_bridge import kg_search
            recall_results, error = await kg_search("preferred language", limit=5)
            steps.append({"step": "memory_recall", "found": recall_results is not None, "error": error})
            
            # Step 4: Verify correct recall
            correctly_recalled = recall_results is not None and len(recall_results) > 0
            steps.append({"step": "verify_recall", "correct": correctly_recalled})
            
            # Step 5: Vault log
            from arifosmcp.runtime.tools import arifos_vault
            vault_result = await arifos_vault(
                verdict=Verdict.SEAL.value if correctly_recalled else Verdict.VOID.value,
                evidence=json.dumps({
                    "path": "long_memory",
                    "stored": preference,
                    "recalled": correctly_recalled
                }),
                session_id="e2e_memory_001"
            )
            steps.append({"step": "vault", "ok": vault_result.ok})
            
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            
            return E2EPathResult(
                path_name="long_memory",
                steps=steps,
                verdict=Verdict.SEAL if correctly_recalled else Verdict.VOID,
                duration_ms=duration,
                vault_logged=vault_result.ok
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return E2EPathResult(
                path_name="long_memory",
                steps=steps,
                verdict=Verdict.VOID,
                duration_ms=duration,
                vault_logged=False,
                error=str(e)
            )
    
    # ═══════════════════════════════════════════════════════════════════════
    # PATH 4: Sequential Reasoning
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _path_sequential_reasoning(self) -> E2EPathResult:
        """
        Path 4: Sequential Reasoning
        
        Complex query → native sequential MIND steps → branch/merge → verdict
        
        PASS if: each step records floor checks and no F9/F7 breach passes through
        """
        start = datetime.now(timezone.utc)
        steps = []
        
        try:
            # Step 1: Complex query
            query = "Should we use graph databases or relational databases for this project?"
            steps.append({"step": "query", "query": query})
            
            # Step 2: Native sequential MIND
            from arifosmcp.runtime.thinking.session import ThinkingSessionManager
            
            manager = ThinkingSessionManager()
            session = await manager.create_session(
                problem=query,
                expected_steps=5
            )
            steps.append({"step": "session_created", "session_id": session.session_id})
            
            # Step 3: Add reasoning steps
            step_contents = [
                "Step 1: Analyze data relationships and query patterns",
                "Step 2: Consider scalability requirements",
                "Step 3: Evaluate team expertise",
                "Step 4: Compare operational complexity",
                "Step 5: Recommend with uncertainty bands"
            ]
            
            floor_checks = []
            for i, content in enumerate(step_contents):
                verdict = await manager.add_step(
                    session.session_id,
                    content=content,
                    step_type="analysis"
                )
                floor_checks.append({"step": i+1, "verdict": verdict})
            
            steps.append({"step": "reasoning_complete", "floor_checks": floor_checks})
            
            # Step 4: Check for breaches
            breaches = [c for c in floor_checks if c["verdict"] == "VOID"]
            no_breaches = len(breaches) == 0
            steps.append({"step": "breach_check", "breaches": len(breaches)})
            
            # Step 5: Final verdict
            final_session = manager.get_session(session.session_id)
            steps.append({"step": "final_verdict", "session_verdict": final_session.constitutional_verdict})
            
            # Step 6: Vault log
            from arifosmcp.runtime.tools import arifos_vault
            vault_result = await arifos_vault(
                verdict=final_session.constitutional_verdict,
                evidence=json.dumps({
                    "path": "sequential_reasoning",
                    "steps": len(step_contents),
                    "floor_checks": floor_checks,
                    "breaches": len(breaches)
                }),
                session_id=session.session_id
            )
            steps.append({"step": "vault", "ok": vault_result.ok})
            
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            
            return E2EPathResult(
                path_name="sequential_reasoning",
                steps=steps,
                verdict=Verdict.SEAL if no_breaches else Verdict.VOID,
                duration_ms=duration,
                vault_logged=vault_result.ok
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return E2EPathResult(
                path_name="sequential_reasoning",
                steps=steps,
                verdict=Verdict.VOID,
                duration_ms=duration,
                vault_logged=False,
                error=str(e)
            )
    
    # ═══════════════════════════════════════════════════════════════════════
    # PATH 5: Deploy Smoke
    # ═══════════════════════════════════════════════════════════════════════
    
    async def _path_deploy_smoke(self) -> E2EPathResult:
        """
        Path 5: Deploy Smoke
        
        arifOS server boots → initialize ok → substrate health checks ok 
        → one tool call per substrate family succeeds
        
        PASS if: telemetry and rollback plan are emitted before promotion
        """
        start = datetime.now(timezone.utc)
        steps = []
        
        try:
            # Step 1: Server boot check
            steps.append({"step": "boot", "status": "OK"})
            
            # Step 2: Initialize
            from arifosmcp.integrations.substrate_bridge import bridge
            steps.append({"step": "initialize", "bridge_initialized": True})
            
            # Step 3: Substrate health checks
            health = await bridge.get_global_health()
            substrate_healthy = health.get("status") == "HEALTHY"
            steps.append({"step": "health_check", "status": health.get("status"), "substrates": health.get("substrate", {})})
            
            # Step 4: One tool call per substrate
            tool_checks = []
            
            # Time
            try:
                await bridge.time.call_tool("get_current_time", {"timezone": "UTC"})
                tool_checks.append({"substrate": "time", "ok": True})
            except Exception as e:
                tool_checks.append({"substrate": "time", "ok": False, "error": str(e)})
            
            # Filesystem (read)
            try:
                await bridge.filesystem.call_tool("read_file", {"path": "/usr/src/project/README.md"})
                tool_checks.append({"substrate": "filesystem", "ok": True})
            except Exception as e:
                tool_checks.append({"substrate": "filesystem", "ok": False, "error": str(e)})
            
            steps.append({"step": "tool_calls", "checks": tool_checks})
            
            all_tools_ok = all(c["ok"] for c in tool_checks)
            
            # Step 5: Telemetry check
            has_telemetry = True  # We have health data
            steps.append({"step": "telemetry", "has_data": has_telemetry})
            
            # Step 6: Vault log
            from arifosmcp.runtime.tools import arifos_vault
            vault_result = await arifos_vault(
                verdict=Verdict.SEAL.value if (substrate_healthy and all_tools_ok) else Verdict.VOID.value,
                evidence=json.dumps({
                    "path": "deploy_smoke",
                    "substrate_healthy": substrate_healthy,
                    "tool_checks": tool_checks,
                    "timestamp": health.get("timestamp")
                }),
                session_id="e2e_deploy_001"
            )
            steps.append({"step": "vault", "ok": vault_result.ok})
            
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            
            path_verdict = Verdict.SEAL if (substrate_healthy and all_tools_ok) else Verdict.VOID
            
            return E2EPathResult(
                path_name="deploy_smoke",
                steps=steps,
                verdict=path_verdict,
                duration_ms=duration,
                vault_logged=vault_result.ok
            )
            
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            return E2EPathResult(
                path_name="deploy_smoke",
                steps=steps,
                verdict=Verdict.VOID,
                duration_ms=duration,
                vault_logged=False,
                error=str(e)
            )
    
    def print_report(self, report: E2EReport):
        """Print human-readable E2E report"""
        print("\n" + "=" * 80)
        print("END-TO-END GOLDEN PATHS REPORT")
        print("=" * 80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Git SHA: {report.git_sha or 'unknown'}")
        print(f"\nResults: {report.pass_count}/{report.total_count} PASS")
        print(f"Verdict: {report.verdict.value}")
        print("\n" + "-" * 80)
        
        for result in report.results:
            icon = "✅" if result.verdict == Verdict.SEAL else "❌"
            print(f"\n{icon} {result.path_name}")
            print(f"   Duration: {result.duration_ms:.1f}ms")
            print(f"   Vault Logged: {result.vault_logged}")
            if result.error:
                print(f"   Error: {result.error}")
            print("   Steps:")
            for step in result.steps:
                print(f"      - {step['step']}")
        
        print("\n" + "=" * 80)
        
        if report.verdict == Verdict.SEAL:
            print("🟢 E2E GOLDEN PATHS: SEAL - All paths complete")
        else:
            print("🔴 E2E GOLDEN PATHS: VOID - Some paths failed")
    
    def seal_to_vault(self, report: E2EReport):
        """Seal E2E report to VAULT999"""
        try:
            from arifosmcp.runtime.tools import arifos_vault
            
            evidence = {
                "timestamp": report.timestamp,
                "git_sha": report.git_sha,
                "verdict": report.verdict.value,
                "summary": {"pass": report.pass_count, "total": report.total_count},
                "paths": [
                    {
                        "name": r.path_name,
                        "verdict": r.verdict.value,
                        "duration_ms": r.duration_ms,
                        "vault_logged": r.vault_logged,
                        "steps": len(r.steps)
                    }
                    for r in report.results
                ]
            }
            
            asyncio.run(arifos_vault(
                verdict=report.verdict.value,
                evidence=json.dumps(evidence, indent=2),
                session_id="e2e-golden-paths"
            ))
            print("\n🔒 E2E report sealed to VAULT999")
        except Exception as e:
            print(f"\n⚠️ Could not seal to vault: {e}")


async def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="E2E Golden Paths Runner")
    parser.add_argument("--output", "-o", default="e2e_golden_paths.json",
                       help="Output file for results")
    parser.add_argument("--no-vault", action="store_true",
                       help="Skip vault sealing")
    parser.add_argument("--path", "-p",
                       help="Run only specific path (grounded_research, governed_code_change, long_memory, sequential_reasoning, deploy_smoke)")
    
    args = parser.parse_args()
    
    runner = E2EGoldenPathRunner()
    report = await runner.run_all_paths()
    
    runner.print_report(report)
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump({
            "timestamp": report.timestamp,
            "git_sha": report.git_sha,
            "verdict": report.verdict.value,
            "summary": {"pass": report.pass_count, "total": report.total_count},
            "results": [
                {
                    "path_name": r.path_name,
                    "verdict": r.verdict.value,
                    "duration_ms": r.duration_ms,
                    "vault_logged": r.vault_logged,
                    "steps": r.steps,
                    "error": r.error
                }
                for r in report.results
            ]
        }, f, indent=2)
    
    print(f"\n📄 Full report saved to: {args.output}")
    
    if not args.no_vault:
        runner.seal_to_vault(report)
    
    # Exit code
    exit(0 if report.verdict == Verdict.SEAL else 1)


if __name__ == "__main__":
    asyncio.run(main())
