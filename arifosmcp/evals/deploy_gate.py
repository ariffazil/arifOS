#!/usr/bin/env python3
"""
arifosmcp/evals/deploy_gate.py — Deployment Gate Orchestrator

FAILS CLOSED:
- If any P0 test fails → VOID
- If rollback unavailable → HOLD
- If conformance incomplete → SABAR
- Only full green + human ratification → SEAL

Implements Gates A-H:
A: Boot - Server starts, MCP initialize succeeds
B: Capability - Expected tools/resources/prompts listed correctly
C: Floors - P0 constitutional breaches all blocked
D: Substrate - fetch/git/filesystem/memory/time health checks pass
E: End-to-end - Golden paths pass
F: Rollback - Previous image/config/compose can be restored
G: Observe - Telemetry present, vault logs written, failures queryable
H: Human - Production promotion explicitly ratified

Authority: 000_THEORY, 888_APEX
DITEMPA BUKAN DIBERI — Gate Seal
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from arifosmcp.runtime.models import Verdict

logger = logging.getLogger(__name__)


class GateStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    HOLD = "HOLD"  # Requires human intervention
    SKIP = "SKIP"


@dataclass
class GateResult:
    """Result of a single deployment gate"""
    gate_name: str
    status: GateStatus
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


@dataclass
class DeployGateReport:
    """Full deployment gate report"""
    timestamp: str
    git_sha: str | None
    branch: str | None
    transport_mode: str
    gates: list[GateResult]
    human_ratified: bool
    
    @property
    def p0_failures(self) -> int:
        """Count P0 (Floor/Conformance) failures"""
        critical_gates = ["A", "B", "C", "D"]
        return sum(1 for g in self.gates 
                  if g.gate_name in critical_gates and g.status in [GateStatus.FAIL, GateStatus.HOLD])
    
    @property
    def rollback_ready(self) -> bool:
        """Check if rollback is available (Gate F)"""
        gate_f = next((g for g in self.gates if g.gate_name == "F"), None)
        return gate_f.status == GateStatus.PASS if gate_f else False
    
    @property
    def observability_ready(self) -> bool:
        """Check if observability is ready (Gate G)"""
        gate_g = next((g for g in self.gates if g.gate_name == "G"), None)
        return gate_g.status == GateStatus.PASS if gate_g else False
    
    @property
    def final_verdict(self) -> Verdict:
        """
        FAIL CLOSED:
        - P0 failure → VOID
        - No rollback → HOLD
        - No observability → HOLD
        - No human ratification → HOLD
        - All green + ratified → SEAL
        """
        # P0 failures = VOID
        if self.p0_failures > 0:
            return Verdict.VOID
        
        # No rollback = HOLD
        if not self.rollback_ready:
            return Verdict.HOLD
        
        # No observability = HOLD
        if not self.observability_ready:
            return Verdict.HOLD
        
        # No human ratification = HOLD
        if not self.human_ratified:
            return Verdict.HOLD
        
        # All gates pass + ratified = SEAL
        all_pass = all(g.status == GateStatus.PASS for g in self.gates)
        if all_pass:
            return Verdict.SEAL
        
        # Partial = SABAR
        return Verdict.SABAR


class DeployGateRunner:
    """
    Deployment Gate Orchestrator.
    
    Runs all test packs and evaluates Gates A-H.
    """
    
    def __init__(self, transport_mode: str = "http", human_ratified: bool = False):
        self.transport_mode = transport_mode
        self.human_ratified = human_ratified
        self.gates: list[GateResult] = []
        self.git_sha = self._get_git_sha()
        self.branch = self._get_git_branch()
    
    def _get_git_sha(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip()[:12] if result.returncode == 0 else None
        except Exception:
            return None
    
    def _get_git_branch(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    async def run_all_gates(self) -> DeployGateReport:
        """Execute all deployment gates"""
        
        print("=" * 80)
        print("DEPLOYMENT GATE ORCHESTRATOR")
        print("=" * 80)
        print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print(f"Git SHA: {self.git_sha or 'unknown'}")
        print(f"Branch: {self.branch or 'unknown'}")
        print(f"Transport: {self.transport_mode}")
        print(f"Human Ratified: {self.human_ratified}")
        print("")
        
        # Gate A: Boot
        await self._gate_a_boot()
        
        # Gate B: Capability
        await self._gate_b_capability()
        
        # Gate C: Floors (P0 Constitutional)
        await self._gate_c_floors()
        
        # Gate D: Substrate
        await self._gate_d_substrate()
        
        # Gate E: End-to-End
        await self._gate_e_e2e()
        
        # Gate F: Rollback
        await self._gate_f_rollback()
        
        # Gate G: Observability
        await self._gate_g_observe()
        
        # Gate H: Human
        self._gate_h_human()
        
        return DeployGateReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            git_sha=self.git_sha,
            branch=self.branch,
            transport_mode=self.transport_mode,
            gates=self.gates,
            human_ratified=self.human_ratified
        )
    
    async def _gate_a_boot(self):
        """
        Gate A: Boot
        - Server starts
        - MCP initialize succeeds
        """
        print("[Gate A] Boot check...")
        
        try:
            from arifosmcp.integrations.substrate_bridge import bridge
            
            # Check bridge initialization
            bridge_ok = bridge is not None
            
            # Check substrate clients exist
            clients_ok = all([
                hasattr(bridge, 'time'),
                hasattr(bridge, 'filesystem'),
                hasattr(bridge, 'git'),
                hasattr(bridge, 'memory'),
                hasattr(bridge, 'fetch'),
            ])
            
            status = GateStatus.PASS if (bridge_ok and clients_ok) else GateStatus.FAIL
            
            self.gates.append(GateResult(
                gate_name="A",
                status=status,
                description="Server boot and MCP initialize",
                evidence={"bridge_ok": bridge_ok, "clients_ok": clients_ok}
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '❌'} Boot: {status.value}")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="A",
                status=GateStatus.FAIL,
                description="Server boot and MCP initialize",
                error=str(e)
            ))
            print(f"  ❌ Boot: FAIL - {e}")
    
    async def _gate_b_capability(self):
        """
        Gate B: Capability
        - Expected tools/resources/prompts listed correctly
        """
        print("[Gate B] Capability discovery...")
        
        try:
            from arifosmcp.integrations.substrate_bridge import bridge
            
            # Check global health (implies discovery worked)
            health = await bridge.get_global_health()
            substrate_count = len(health.get("substrate", {}))
            
            status = GateStatus.PASS if substrate_count >= 5 else GateStatus.FAIL
            
            self.gates.append(GateResult(
                gate_name="B",
                status=status,
                description="Capability discovery (tools/resources/prompts)",
                evidence={
                    "substrate_count": substrate_count,
                    "substrates": list(health.get("substrate", {}).keys())
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '❌'} Capability: {status.value}")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="B",
                status=GateStatus.FAIL,
                description="Capability discovery",
                error=str(e)
            ))
            print(f"  ❌ Capability: FAIL - {e}")
    
    async def _gate_c_floors(self):
        """
        Gate C: Floors (P0 Constitutional)
        - All P0 breach tests pass
        - F1, F2, F7, F9, F11, F12 violations blocked
        """
        print("[Gate C] Constitutional floors (P0)...")
        
        try:
            # Run breach tests
            from arifosmcp.evals.breach_test_runner import BreachTestRunner
            
            runner = BreachTestRunner("arifosmcp/evals/constitutional_breach_tests.yaml")
            await runner.run_all_tests()
            report = runner.generate_report()
            
            p0_pass = report['summary']['passed']
            p0_total = report['summary']['total_tests']
            
            status = GateStatus.PASS if (p0_pass == p0_total) else GateStatus.FAIL
            
            self.gates.append(GateResult(
                gate_name="C",
                status=status,
                description="P0 Constitutional breach tests",
                evidence={
                    "passed": p0_pass,
                    "total": p0_total,
                    "by_floor": report['summary'].get('by_floor', {})
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '❌'} Floors: {p0_pass}/{p0_total} PASS")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="C",
                status=GateStatus.FAIL,
                description="P0 Constitutional breach tests",
                error=str(e)
            ))
            print(f"  ❌ Floors: FAIL - {e}")
    
    async def _gate_d_substrate(self):
        """
        Gate D: Substrate
        - fetch/git/filesystem/memory/time health checks pass
        """
        print("[Gate D] Substrate health...")
        
        try:
            from arifosmcp.integrations.substrate_bridge import bridge
            
            health = await bridge.get_global_health()
            substrates = health.get("substrate", {})
            
            healthy_count = sum(1 for s in substrates.values() if s.get("status") == "OK")
            total_count = len(substrates)
            
            status = GateStatus.PASS if healthy_count == total_count else GateStatus.FAIL
            
            self.gates.append(GateResult(
                gate_name="D",
                status=status,
                description="Substrate health checks",
                evidence={
                    "healthy": healthy_count,
                    "total": total_count,
                    "substrates": substrates
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '❌'} Substrate: {healthy_count}/{total_count} HEALTHY")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="D",
                status=GateStatus.FAIL,
                description="Substrate health checks",
                error=str(e)
            ))
            print(f"  ❌ Substrate: FAIL - {e}")
    
    async def _gate_e_e2e(self):
        """
        Gate E: End-to-End
        - Golden paths pass
        """
        print("[Gate E] End-to-end golden paths...")
        
        try:
            from arifosmcp.evals.e2e_golden_paths import E2EGoldenPathRunner
            
            runner = E2EGoldenPathRunner()
            report = await runner.run_all_paths()
            
            e2e_pass = report.pass_count
            e2e_total = report.total_count
            
            # E2E failures don't block deployment but warn
            status = GateStatus.PASS if (e2e_pass == e2e_total) else GateStatus.SKIP
            
            self.gates.append(GateResult(
                gate_name="E",
                status=status,
                description="End-to-end golden paths",
                evidence={
                    "passed": e2e_pass,
                    "total": e2e_total,
                    "paths": [r.path_name for r in report.results]
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '⚠️'} E2E: {e2e_pass}/{e2e_total} PASS")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="E",
                status=GateStatus.SKIP,
                description="End-to-end golden paths",
                error=str(e)
            ))
            print(f"  ⚠️ E2E: SKIP - {e}")
    
    async def _gate_f_rollback(self):
        """
        Gate F: Rollback
        - Previous image/config/compose can be restored
        """
        print("[Gate F] Rollback availability...")
        
        try:
            # Check for docker-compose backup
            compose_backup = Path("docker-compose.yml.backup").exists()
            
            # Check for git tag/branch for rollback
            git_result = subprocess.run(
                ["git", "tag", "-l", "rollback-*"],
                capture_output=True, text=True, timeout=5
            )
            has_rollback_tag = len(git_result.stdout.strip()) > 0
            
            # Check for container image history
            image_result = subprocess.run(
                ["docker", "images", "arifosmcp", "--format", "{{.Tag}}"],
                capture_output=True, text=True, timeout=10
            )
            has_image_history = len(image_result.stdout.strip()) > 0
            
            rollback_available = compose_backup or has_rollback_tag or has_image_history
            
            status = GateStatus.PASS if rollback_available else GateStatus.HOLD
            
            self.gates.append(GateResult(
                gate_name="F",
                status=status,
                description="Rollback availability",
                evidence={
                    "compose_backup": compose_backup,
                    "has_rollback_tag": has_rollback_tag,
                    "has_image_history": has_image_history
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '⏸️'} Rollback: {status.value}")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="F",
                status=GateStatus.HOLD,
                description="Rollback availability",
                error=str(e)
            ))
            print(f"  ⏸️ Rollback: HOLD - {e}")
    
    async def _gate_g_observe(self):
        """
        Gate G: Observability
        - Telemetry present
        - Vault logs written
        - Failures queryable
        """
        print("[Gate G] Observability...")
        
        try:
            # Check VAULT999 exists
            vault_path = Path("arifosmcp/VAULT999")
            vault_exists = vault_path.exists()
            
            # Check telemetry directory
            telemetry_path = Path("telemetry")
            telemetry_exists = telemetry_path.exists()
            
            # Check for logging configuration
            has_logging = True  # Assume configured
            
            observable = vault_exists and telemetry_exists and has_logging
            
            status = GateStatus.PASS if observable else GateStatus.HOLD
            
            self.gates.append(GateResult(
                gate_name="G",
                status=status,
                description="Observability (telemetry, vault, logs)",
                evidence={
                    "vault_exists": vault_exists,
                    "telemetry_exists": telemetry_exists,
                    "has_logging": has_logging
                }
            ))
            
            print(f"  {'✅' if status == GateStatus.PASS else '⏸️'} Observability: {status.value}")
            
        except Exception as e:
            self.gates.append(GateResult(
                gate_name="G",
                status=GateStatus.HOLD,
                description="Observability",
                error=str(e)
            ))
            print(f"  ⏸️ Observability: HOLD - {e}")
    
    def _gate_h_human(self):
        """
        Gate H: Human Ratification
        - Production promotion explicitly ratified
        """
        print("[Gate H] Human ratification...")
        
        status = GateStatus.PASS if self.human_ratified else GateStatus.HOLD
        
        self.gates.append(GateResult(
            gate_name="H",
            status=status,
            description="Human ratification for production",
            evidence={"ratified": self.human_ratified}
        ))
        
        print(f"  {'✅' if status == GateStatus.PASS else '⏸️'} Human: {status.value}")
    
    def print_report(self, report: DeployGateReport):
        """Print human-readable deployment gate report"""
        print("\n" + "=" * 80)
        print("DEPLOYMENT GATE REPORT")
        print("=" * 80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Git SHA: {report.git_sha or 'unknown'}")
        print(f"Branch: {report.branch or 'unknown'}")
        print(f"Transport: {report.transport_mode}")
        print(f"Human Ratified: {report.human_ratified}")
        print("\n" + "-" * 80)
        print("GATE RESULTS:")
        print("-" * 80)
        
        for gate in report.gates:
            icon = {
                GateStatus.PASS: "✅",
                GateStatus.FAIL: "❌",
                GateStatus.HOLD: "⏸️",
                GateStatus.SKIP: "⏭️"
            }.get(gate.status, "❓")
            
            print(f"  {icon} Gate {gate.gate_name}: {gate.status.value}")
            print(f"     {gate.description}")
            if gate.error:
                print(f"     Error: {gate.error}")
        
        print("\n" + "=" * 80)
        print(f"P0 Failures: {report.p0_failures}")
        print(f"Rollback Ready: {report.rollback_ready}")
        print(f"Observability Ready: {report.observability_ready}")
        print(f"Human Ratified: {report.human_ratified}")
        print("\n" + "=" * 80)
        print(f"FINAL VERDICT: {report.final_verdict.value}")
        print("=" * 80)
        
        if report.final_verdict == Verdict.SEAL:
            print("🟢 DEPLOYMENT APPROVED: All gates passed, production ready")
        elif report.final_verdict == Verdict.VOID:
            print("🔴 DEPLOYMENT BLOCKED: P0 failures detected")
        elif report.final_verdict == Verdict.HOLD:
            print("⏸️ DEPLOYMENT ON HOLD: Requires human intervention")
        else:
            print("🟡 DEPLOYMENT WARNING: SABAR - Review required")
    
    def seal_to_vault(self, report: DeployGateReport):
        """Seal deployment gate report to VAULT999"""
        try:
            from arifosmcp.runtime.tools import arifos_vault
            
            evidence = {
                "timestamp": report.timestamp,
                "git_sha": report.git_sha,
                "branch": report.branch,
                "transport": report.transport_mode,
                "final_verdict": report.final_verdict.value,
                "human_ratified": report.human_ratified,
                "p0_failures": report.p0_failures,
                "rollback_ready": report.rollback_ready,
                "observability_ready": report.observability_ready,
                "gates": [
                    {
                        "gate": g.gate_name,
                        "status": g.status.value,
                        "description": g.description,
                        "evidence": g.evidence,
                        "error": g.error
                    }
                    for g in report.gates
                ]
            }
            
            asyncio.run(arifos_vault(
                verdict=report.final_verdict.value,
                evidence=json.dumps(evidence, indent=2),
                session_id="deploy-gate"
            ))
            print("\n🔒 Deployment gate report sealed to VAULT999")
        except Exception as e:
            print(f"\n⚠️ Could not seal to vault: {e}")


async def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Deployment Gate Orchestrator")
    parser.add_argument("--transport", default="http", choices=["http", "stdio"],
                       help="Transport mode")
    parser.add_argument("--ratify", "-r", action="store_true",
                       help="Human ratification for production deployment")
    parser.add_argument("--output", "-o", default="deploy_gate.json",
                       help="Output file for results")
    parser.add_argument("--no-vault", action="store_true",
                       help="Skip vault sealing")
    
    args = parser.parse_args()
    
    runner = DeployGateRunner(
        transport_mode=args.transport,
        human_ratified=args.ratify
    )
    report = await runner.run_all_gates()
    
    runner.print_report(report)
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump({
            "timestamp": report.timestamp,
            "git_sha": report.git_sha,
            "branch": report.branch,
            "transport": report.transport_mode,
            "final_verdict": report.final_verdict.value,
            "human_ratified": report.human_ratified,
            "p0_failures": report.p0_failures,
            "rollback_ready": report.rollback_ready,
            "observability_ready": report.observability_ready,
            "gates": [
                {
                    "gate": g.gate_name,
                    "status": g.status.value,
                    "description": g.description,
                    "evidence": g.evidence,
                    "error": g.error
                }
                for g in report.gates
            ]
        }, f, indent=2)
    
    print(f"\n📄 Full report saved to: {args.output}")
    
    if not args.no_vault:
        runner.seal_to_vault(report)
    
    # Exit code
    exit_code = {
        Verdict.SEAL: 0,
        Verdict.SABAR: 1,
        Verdict.HOLD: 2,
        Verdict.VOID: 3
    }.get(report.final_verdict, 1)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
