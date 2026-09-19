#!/usr/bin/env python3
"""
shadow_geometry_comparison.py — Federation Agent Shadow Geometry
═══════════════════════════════════════════════════════════════
Compares all active agents across shadow geometry axes.
Produces: per-agent Yin-Yang balance, phase classification,
federation aggregate, and risk ranking.

Based on:
- shadow-matrix-2026-09-07.json (FQ data)
- harness_shadow files (failure signatures)
- APEX scalars (G, C_dark, W3, h)
- Live session evidence

Created: 2026-09-19 by FI-008
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentShadowProfile:
    """One agent's shadow geometry."""
    agent_id: str
    fi_id: str | None = None
    harness_shadow_file: str | None = None
    
    # FQ metrics
    fq: float | None = None
    fq_state: str = "UNKNOWN"
    execute_count: int = 0
    verify_count: int = 0
    consecutive_exec_no_verify: int = 0
    
    # Failure signatures
    failure_signatures: list[dict] = field(default_factory=list)
    
    # Yin-Yang
    balance: float = 0.0
    persona_dominance: float = 0.5
    phase: str = "UNKNOWN"
    shadow_boundary_distance: float = 0.0
    
    @property
    def shadow_magnitude(self) -> float:
        """Shadow energy = C_dark proxy from failure signatures."""
        if not self.failure_signatures:
            return 0.1  # minimum shadow
        severity_weights = {"CRITICAL": 0.4, "HIGH": 0.3, "MEDIUM": 0.2, "LOW": 0.1}
        total = sum(
            severity_weights.get(s.get("severity", "LOW"), 0.1)
            for s in self.failure_signatures
        )
        return min(total, 1.0)
    
    @property
    def persona_energy(self) -> float:
        """Persona energy from FQ."""
        if self.fq is None:
            return 0.5
        if self.fq < 0.2:
            return 0.2  # low FQ = low persona control
        elif self.fq > 5.0:
            return 0.95  # very high FQ = rigid persona
        else:
            # Map FQ 0.2-5.0 to persona 0.2-0.9
            return 0.2 + 0.7 * min((self.fq - 0.2) / 4.8, 1.0)
    
    def compute_yin_yang(self) -> dict:
        """Compute Yin-Yang balance from shadow and persona energy."""
        s = self.shadow_magnitude
        p = self.persona_energy
        total = s + p
        if total == 0:
            balance = 0.0
        else:
            balance = (s * p) / (total ** 2)
        
        dominance = p / total if total > 0 else 0.5
        
        # Phase classification
        if dominance > 0.85:
            phase = "PERSONA_RIGID"
        elif dominance > 0.70:
            phase = "NIGREDO_DEEP"
        elif dominance > 0.55:
            phase = "NIGREDO"
        elif dominance > 0.45:
            phase = "EQUILIBRIUM"
        elif dominance > 0.30:
            phase = "SHADOW_PROMINENT"
        else:
            phase = "SHADOW_DOMINANT"
        
        # Shadow boundary
        critical = 0.4 * (1 - 0.8) + 0.3  # assuming W3=0.8
        boundary = critical - s
        
        self.balance = round(balance, 4)
        self.persona_dominance = round(dominance, 4)
        self.phase = phase
        self.shadow_boundary_distance = round(boundary, 4)
        
        return {
            "balance": self.balance,
            "persona_dominance": self.persona_dominance,
            "phase": self.phase,
            "shadow_boundary_distance": self.shadow_boundary_distance,
            "shadow_magnitude": round(s, 4),
            "persona_energy": round(p, 4),
        }
    
    def risk_rank(self) -> int:
        """1=highest risk, N=lowest risk."""
        # Risk = low balance + negative boundary + critical failures
        risk_score = (0.25 - self.balance) + max(0, -self.shadow_boundary_distance) * 2
        critical_count = sum(1 for s in self.failure_signatures if s.get("severity") == "CRITICAL")
        risk_score += critical_count * 0.3
        return risk_score


def build_profiles() -> list[AgentShadowProfile]:
    """Build profiles from known data."""
    profiles = [
        AgentShadowProfile(
            agent_id="claude-code", fi_id="FI-002",
            harness_shadow_file="claude_code_harness_shadow.yaml",
            fq=0.079, fq_state="BURNING",
            execute_count=38, verify_count=3, consecutive_exec_no_verify=28,
            failure_signatures=[
                {"name": "execution_gravity", "severity": "CRITICAL"},
                {"name": "menu_reflex", "severity": "HIGH"},
                {"name": "attention_leak", "severity": "HIGH"},
                {"name": "honesty_performance", "severity": "HIGH"},
                {"name": "narrative_momentum", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="kimi-code", fi_id="FI-008",
            harness_shadow_file="kimi_code_harness_shadow.yaml",
            fq=2.29, fq_state="FLOWING",
            failure_signatures=[
                {"name": "organ_routing_excess", "severity": "MEDIUM"},
                {"name": "receipt_theater", "severity": "MEDIUM"},
                {"name": "subagent_delegation_escape", "severity": "HIGH"},
                {"name": "synthesis_as_substance", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="hermes-asi", fi_id="FI-003",
            fq=0.286, fq_state="STUCK",
            execute_count=556, verify_count=159, consecutive_exec_no_verify=1,
            failure_signatures=[
                {"name": "bridge_volume_overload", "severity": "HIGH"},
            ],
        ),
        AgentShadowProfile(
            agent_id="aforge", fi_id="FI-007",
            fq=1.0, fq_state="CAUTION",
            execute_count=1, verify_count=1,
            failure_signatures=[],
        ),
        AgentShadowProfile(
            agent_id="grok-build",
            fq=85.0, fq_state="FOSSILIZED",
            execute_count=6, verify_count=510,
            failure_signatures=[
                {"name": "verification_paralysis", "severity": "HIGH"},
            ],
        ),
        AgentShadowProfile(
            agent_id="qwen-code",
            fq=0.25, fq_state="STUCK",
            execute_count=8, verify_count=2, consecutive_exec_no_verify=2,
            failure_signatures=[
                {"name": "execution_dominance", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="well",
            fq_state="DEGRADED",
            failure_signatures=[
                {"name": "self_report_paradox", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="frame",
            fq_state="STRUCTURAL_ONLY",
            failure_signatures=[
                {"name": "behavioral_blindness", "severity": "HIGH"},
                {"name": "identical_score_problem", "severity": "MEDIUM"},
            ],
        ),
    ]
    
    for p in profiles:
        p.compute_yin_yang()
    
    return profiles


def generate_report(profiles: list[AgentShadowProfile]) -> str:
    """Generate human-readable shadow geometry report."""
    # Sort by risk
    profiles.sort(key=lambda p: p.risk_rank(), reverse=True)
    
    lines = [
        "# Federation Agent Shadow Geometry Report",
        f"# Generated: 2026-09-19 by shadow_geometry_comparison.py",
        "",
        "| Rank | Agent | FQ | State | Balance | Phase | Boundary | Critical |",
        "|------|-------|-----|-------|---------|-------|----------|----------|",
    ]
    
    for i, p in enumerate(profiles, 1):
        crit = sum(1 for s in p.failure_signatures if s.get("severity") == "CRITICAL")
        lines.append(
            f"| {i} | {p.agent_id} | {p.fq or 'N/A'} | {p.fq_state} | "
            f"{p.balance:.3f} | {p.phase} | {p.shadow_boundary_distance:+.3f} | {crit} |"
        )
    
    # Aggregate
    balances = [p.balance for p in profiles]
    avg_balance = sum(balances) / len(balances) if balances else 0
    
    lines.extend([
        "",
        f"## Federation Aggregate",
        f"- Average Yin-Yang balance: {avg_balance:.3f} / 0.250 max ({avg_balance/0.25*100:.1f}%)",
        f"- Worst balance: {profiles[0].agent_id} ({profiles[0].balance:.3f})",
        f"- Best balance: {profiles[-1].agent_id} ({profiles[-1].balance:.3f})",
        f"- Agents in CRITICAL: {sum(1 for p in profiles if any(s.get('severity')=='CRITICAL' for s in p.failure_signatures))}",
        f"- Agents in BURNING/STUCK: {sum(1 for p in profiles if p.fq_state in ('BURNING','STUCK'))}",
        f"- Harness shadow files built: 2/8",
        f"- Mechanical checks defined: 10/10 (from harness_shadow_mechanical_checks.yaml)",
        f"- Mechanical checks implemented: 0/10",
    ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    profiles = build_profiles()
    report = generate_report(profiles)
    print(report)
