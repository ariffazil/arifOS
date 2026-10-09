#!/usr/bin/env python3
"""
shadow_geometry_comparison.py — Federation Agent Shadow Geometry
═══════════════════════════════════════════════════════════════
Compares all active agents across shadow geometry axes.
Produces: per-agent Yin-Yang balance, phase classification,
federation aggregate, and risk ranking.

Based on:
- LIVE arifFlow /health per-actor FQ (MEASURED at run time)
- harness_shadow files (failure signatures — DECLARED, static registry)
- APEX scalars (G, C_dark, W3, h)

Created: 2026-09-19 by FI-008
Rewired to live FQ: 2026-10-03 by FI-003 (F13 order "fix the shadow cron").
Before this change every FQ value below was a hardcoded literal copied from
shadow-matrix-2026-09-07.json, so the 6-hourly cron republished a frozen
2026-09-07 measurement as a current report. There are no stored FQ fallbacks:
if arifFlow is unreachable the report says UNKNOWN.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations
import json
import math
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Live measurement source ──────────────────────────────────────
ARIFLOW_HEALTH_URL = "http://127.0.0.1:7073/health"
ARIFLOW_TIMEOUT_S = 8  # timeout is a constitutional boundary, not a perf knob

# Registry actor_id → keys used by arifFlow's per_actor map. The two naming
# grammars coexist in the estate ("aforge" in the registry, "a-forge" in
# receipts); without this the lookup silently misses and reads as "no data".
ACTOR_ALIASES: dict[str, tuple[str, ...]] = {
    "claude-code": ("claude-code", "claude_code"),
    "kimi-code": ("kimi-code", "kimi_code"),
    "hermes-asi": ("hermes-asi", "hermes_asi"),
    "aforge": ("a-forge", "aforge", "A-FORGE"),
    "grok-build": ("grok-build", "grok_build"),
    "qwen-code": ("qwen-code", "qwen_code", "qwen-code/FI-003"),
    "well": ("well", "g-well"),
    "frame": ("frame",),
}


def fetch_live_fq() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Pull per-actor FQ from arifFlow. Fail-closed: never a stored fallback."""
    meta: dict[str, Any] = {
        "source": ARIFLOW_HEALTH_URL,
        "snapshot_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "UNAVAILABLE",
        "error": None,
        "live_actor_count": None,
        "federation_quotient": None,
    }
    try:
        with urllib.request.urlopen(ARIFLOW_HEALTH_URL, timeout=ARIFLOW_TIMEOUT_S) as r:
            data = json.loads(r.read().decode())
    except Exception as e:  # noqa: BLE001 — any failure must degrade to UNKNOWN
        meta["error"] = f"{type(e).__name__}: {e}"
        return None, meta

    fq = data.get("fq") or {}
    per_actor = fq.get("per_actor")
    if not isinstance(per_actor, dict) or not per_actor:
        meta["error"] = "response had no fq.per_actor map"
        return None, meta

    meta["status"] = "MEASURED"
    meta["live_actor_count"] = len(per_actor)
    meta["federation_quotient"] = fq.get("quotient")
    return per_actor, meta


def overlay_live_fq(
    profiles: list["AgentShadowProfile"], per_actor: dict[str, Any] | None
) -> None:
    """Attach measured FQ to each profile. No match and no source → UNKNOWN."""
    for p in profiles:
        if not per_actor:
            p.fq = None
            p.fq_state = "UNKNOWN"
            p.execute_count = None
            p.verify_count = None
            p.consecutive_exec_no_verify = None
            continue

        row = None
        for key in ACTOR_ALIASES.get(p.agent_id, (p.agent_id,)):
            if key in per_actor:
                row = per_actor[key]
                break

        if row is None:
            # Actor exists in the shadow registry but produced no receipts in the
            # live window. That is "not observed", NOT "balanced" and NOT 0.
            p.fq = None
            p.fq_state = "NOT_IN_LIVE_SOURCE"
            p.execute_count = None
            p.verify_count = None
            p.consecutive_exec_no_verify = None
            continue

        q = row.get("quotient")
        p.fq = float(q) if isinstance(q, (int, float)) else None
        p.fq_state = row.get("verdict") or "UNKNOWN"
        p.execute_count = row.get("execute")
        p.verify_count = row.get("verify")
        p.consecutive_exec_no_verify = row.get("consecutive_exec_no_verify")
        p.live_diagnosis = row.get("diagnosis")


@dataclass
class AgentShadowProfile:
    """One agent's shadow geometry."""
    agent_id: str
    fi_id: str | None = None
    harness_shadow_file: str | None = None

    # FQ metrics — MEASURED. None means "not observed", never zero.
    fq: float | None = None
    fq_state: str = "UNKNOWN"
    execute_count: int | None = None
    verify_count: int | None = None
    consecutive_exec_no_verify: int | None = None
    live_diagnosis: str | None = None
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
    """Build profiles from the STATIC shadow registry only.

    Carries identity + declared failure signatures. Carries NO measurement:
    fq / fq_state / execute_count / verify_count are filled by
    overlay_live_fq() from arifFlow at run time. Filenames below are the real
    on-disk names in /root/AAA/registries/harnesses/ (hyphenated) — the previous
    underscored names resolved to nothing, which is why the shadow matrix's
    harness_shadow_file pointers were all broken.
    """
    H = "/root/AAA/registries/harnesses/"
    profiles = [
        AgentShadowProfile(
            agent_id="claude-code", fi_id="FI-002",
            harness_shadow_file=H + "claude-code_harness_shadow.yaml",
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
            harness_shadow_file=H + "kimi-code_harness_shadow.yaml",
            failure_signatures=[
                {"name": "organ_routing_excess", "severity": "MEDIUM"},
                {"name": "receipt_theater", "severity": "MEDIUM"},
                {"name": "subagent_delegation_escape", "severity": "HIGH"},
                {"name": "synthesis_as_substance", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="hermes-asi", fi_id="FI-003",
            harness_shadow_file=H + "hermes-asi_harness_shadow.yaml",
            failure_signatures=[
                {"name": "bridge_volume_overload", "severity": "HIGH"},
            ],
        ),
        AgentShadowProfile(
            agent_id="aforge", fi_id="FI-007",
            harness_shadow_file=H + "aforge_harness_shadow.yaml",
            failure_signatures=[
                {"name": "mutation_hunger", "severity": "MEDIUM"},
                {"name": "forge_evaluate_circularity", "severity": "HIGH"},
                {"name": "tool_surface_bloat", "severity": "MEDIUM"},
                {"name": "receipt_as_product", "severity": "LOW"},
            ],
        ),
        AgentShadowProfile(
            agent_id="grok-build", fi_id="FI-004",
            harness_shadow_file=H + "grok-build_harness_shadow.yaml",
            failure_signatures=[
                {"name": "verification_paralysis", "severity": "CRITICAL"},
            ],
        ),
        AgentShadowProfile(
            agent_id="qwen-code", fi_id="FI-003",
            harness_shadow_file=H + "qwen-code_harness_shadow.yaml",
            failure_signatures=[
                {"name": "execution_dominance", "severity": "MEDIUM"},
            ],
        ),
        AgentShadowProfile(
            agent_id="well",
            harness_shadow_file=H + "well_harness_shadow.yaml",
            failure_signatures=[
                {"name": "self_report_paradox", "severity": "HIGH"},
                {"name": "measurement_substitution", "severity": "MEDIUM"},
                {"name": "dignity_as_avoidance", "severity": "MEDIUM"},
                {"name": "floor_as_boundary", "severity": "LOW"},
            ],
        ),
        AgentShadowProfile(
            agent_id="frame",
            harness_shadow_file=H + "frame_harness_shadow.yaml",
            failure_signatures=[
                {"name": "behavioral_blindness", "severity": "HIGH"},
                {"name": "identical_score_problem", "severity": "MEDIUM"},
                {"name": "observer_inertia", "severity": "MEDIUM"},
                {"name": "baseline_staleness", "severity": "LOW"},
            ],
        ),
    ]

    for p in profiles:
        p.compute_yin_yang()

    return profiles

def _count_yaml_ids(path: Path, prefix: str) -> int | None:
    """Count registry entries by id prefix. None = source unreadable (never 0)."""
    try:
        return sum(1 for ln in path.read_text().splitlines() if prefix in ln and "id:" in ln)
    except OSError:
        return None


def _count_active_checks(path: Path) -> int | None:
    """Count actors whose mechanical_checks_active list is non-empty."""
    try:
        txt = path.read_text()
    except OSError:
        return None
    n = 0
    for ln in txt.splitlines():
        s = ln.strip()
        if s.startswith("mechanical_checks_active:") and s.split(":", 1)[1].strip() not in ("", "[]"):
            n += 1
    return n


def measure_inventory() -> dict[str, Any]:
    """Measure the registry inventory from disk instead of asserting it."""
    harness_dir = Path("/root/AAA/registries/harnesses")
    checks_yaml = Path("/root/AAA/registries/harness_shadow_mechanical_checks.yaml")
    checks_mod = Path("/root/arifOS/arifosmcp/tools/shadow_mechanical_checks.py")
    matrix = Path("/root/AAA/cockpit/shadow-matrix/enhanced-shadow-matrix-v2.yaml")

    try:
        harness_files = len(list(harness_dir.glob("*_harness_shadow.yaml")))
    except OSError:
        harness_files = None

    impl_fns = None
    try:
        impl_fns = sum(
            1 for ln in checks_mod.read_text().splitlines() if ln.startswith("def check_")
        )
    except OSError:
        pass

    return {
        "harness_shadow_files": harness_files,
        "mechanical_checks_defined": _count_yaml_ids(checks_yaml, "SHADOW-CHECK-"),
        "mechanical_check_fns_in_module": impl_fns,
        "mechanical_checks_active_on_actors": _count_active_checks(matrix),
    }


def generate_report(profiles: list[AgentShadowProfile], fq_meta: dict[str, Any]) -> str:
    """Generate human-readable shadow geometry report.

    Every number here is either MEASURED (live arifFlow / disk inventory) or
    explicitly labelled DECLARED (static registry assertion). No value is
    silently defaulted: an unavailable source renders as UNKNOWN, never 0.
    """
    # Sort by risk
    profiles.sort(key=lambda p: p.risk_rank(), reverse=True)

    inv = fq_meta.get("inventory", {})
    measured_n = sum(1 for p in profiles if p.fq is not None)

    lines = [
        "# Federation Agent Shadow Geometry Report",
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} by shadow_geometry_comparison.py",
        "",
        "## Provenance",
        f"- FQ source: {fq_meta.get('source')}",
        f"- FQ snapshot: {fq_meta.get('snapshot_at')}",
        f"- FQ status: {fq_meta.get('status')}",
        f"- Actors measured: {measured_n}/{len(profiles)}"
        f" (live source reports {fq_meta.get('live_actor_count')} actors total)",
        f"- Federation FQ scalar: {fq_meta.get('federation_quotient')}",
        f"- Failure signatures: DECLARED — static registry "
        f"(/root/AAA/registries/harnesses/*_harness_shadow.yaml), not measured",
        "",
        "| Rank | Agent | FQ | State | Exec | Verify | Balance | Phase | Boundary | Critical |",
        "|------|-------|-----|-------|------|--------|---------|-------|----------|----------|",
    ]

    for i, p in enumerate(profiles, 1):
        crit = sum(1 for s in p.failure_signatures if s.get("severity") == "CRITICAL")
        fq = f"{p.fq:.3f}" if isinstance(p.fq, (int, float)) else "UNKNOWN"
        ex = p.execute_count if p.execute_count is not None else "—"
        ve = p.verify_count if p.verify_count is not None else "—"
        lines.append(
            f"| {i} | {p.agent_id} | {fq} | {p.fq_state} | {ex} | {ve} | "
            f"{p.balance:.3f} | {p.phase} | {p.shadow_boundary_distance:+.3f} | {crit} |"
        )

    # Aggregate
    balances = [p.balance for p in profiles]
    avg_balance = sum(balances) / len(balances) if balances else 0
    # The table is sorted by risk_rank(), NOT by balance — the previous footer
    # labelled profiles[0]/profiles[-1] as worst/best *balance*, which the table
    # itself contradicted. Compute each superlative from its own axis.
    worst_bal = min(profiles, key=lambda p: p.balance)
    best_bal = max(profiles, key=lambda p: p.balance)

    hf = inv.get("harness_shadow_files")
    mcd = inv.get("mechanical_checks_defined")
    mfn = inv.get("mechanical_check_fns_in_module")
    mact = inv.get("mechanical_checks_active_on_actors")

    lines.extend([
        "",
        "## Federation Aggregate",
        f"- Average Yin-Yang balance: {avg_balance:.3f} / 0.250 max ({avg_balance/0.25*100:.1f}%) — DECLARED inputs",
        f"- Highest risk rank: {profiles[0].agent_id} (risk={profiles[0].risk_rank():.3f})",
        f"- Lowest risk rank: {profiles[-1].agent_id} (risk={profiles[-1].risk_rank():.3f})",
        f"- Worst balance: {worst_bal.agent_id} ({worst_bal.balance:.3f})",
        f"- Best balance: {best_bal.agent_id} ({best_bal.balance:.3f})",
        f"- Agents in CRITICAL: {sum(1 for p in profiles if any(s.get('severity')=='CRITICAL' for s in p.failure_signatures))}",
        f"- Agents in BURNING/STUCK: {sum(1 for p in profiles if p.fq_state in ('BURNING','STUCK'))}",
        f"- Agents with no live FQ: {len(profiles) - measured_n}",
        "",
        "## Inventory (MEASURED from disk)",
        f"- Harness shadow files present: {hf if hf is not None else 'UNKNOWN'}",
        f"- Mechanical checks defined in YAML: {mcd if mcd is not None else 'UNKNOWN'}",
        f"- check_* functions in shadow_mechanical_checks.py: {mfn if mfn is not None else 'UNKNOWN'}",
        f"- Mechanical checks ACTIVE on an actor: {mact if mact is not None else 'UNKNOWN'}"
        + ("  <-- defined and coded but wired to nothing" if mact == 0 else ""),
    ])

    if fq_meta.get("status") != "MEASURED":
        lines.extend([
            "",
            f"## ⚠ FQ UNAVAILABLE — {fq_meta.get('error')}",
            "## All FQ columns above are UNKNOWN by design. This report refuses to",
            "## substitute a stored or hardcoded value for a missing measurement",
            "## (fail-closed: 0 = confirmed absence, UNKNOWN = cannot determine).",
        ])

    return "\n".join(lines)


if __name__ == "__main__":
    per_actor, fq_meta = fetch_live_fq()
    fq_meta["inventory"] = measure_inventory()
    profiles = build_profiles()
    overlay_live_fq(profiles, per_actor)
    print(generate_report(profiles, fq_meta))

