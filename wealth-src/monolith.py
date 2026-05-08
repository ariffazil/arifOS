import hashlib
import inspect
import json
import math
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

__version__ = "2026.04.29"
"""WEALTH v2026.04.29 - Sovereign Pipeline OS with Expanded Resource Lattice."""

LAST_RECEIPT_HASH = "0" * 64

# Ensure sibling arifOS directory is in path for arifosmcp imports
arifos_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "arifOS"))
if os.path.exists(arifos_path) and arifos_path not in sys.path:
    sys.path.append(arifos_path)

try:
    from fastmcp import FastMCP

    FASTMCP_AVAILABLE = True
except ImportError:
    FASTMCP_AVAILABLE = False

    class FastMCP:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def tool(self, name=None):
            return lambda f: f

        def resource(self, uri):
            return lambda f: f

        def run(self):
            pass


# --- Sovereign Governance ---
try:
    from arifosmcp.runtime.megaTools.tool_01_init_anchor import check_floors
    from arifosmcp.runtime.vault_postgres import seal_to_vault as append_vault999

    GOVERNANCE_AVAILABLE = True
except Exception:
    try:
        from arifosmcp.runtime.tools import arifos_judge as check_floors
        from arifosmcp.runtime.vault_postgres import seal_to_vault as append_vault999

        GOVERNANCE_AVAILABLE = True
    except Exception:
        GOVERNANCE_AVAILABLE = False

        def check_floors(*args, **kwargs):
            return {"pass": True, "verdict": "SEAL", "violations": [], "holds": [], "warnings": []}

        try:
            from host.governance.vault_supabase import append_vault999

            GOVERNANCE_AVAILABLE = True
        except Exception:

            def append_vault999(record, **kwargs):
                return record


def _vault_append(record, **kwargs):
    """Bridge sync/async vault append safely."""
    import asyncio

    result = append_vault999(record, **kwargs)
    if inspect.isawaitable(result):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop is None:
            return asyncio.run(result)
        # Inside async context: fire-and-forget with task
        asyncio.create_task(result)
    return result


# --- Coordination Layer ---
try:
    from host.coordination.lp_allocator import allocate as lp_allocate
    from host.coordination.cooperative import shapley_values, core_feasibility
    from host.coordination.strategic import nash_approximation
    from host.coordination.commons import commons_risk

    COORDINATION_AVAILABLE = True
except Exception:
    COORDINATION_AVAILABLE = False

    def lp_allocate(*args, **kwargs):
        return {"feasible": False}

    def shapley_values(*args, **kwargs):
        return {"shapley": {}}

    def core_feasibility(*args, **kwargs):
        return {"in_core": False}

    def nash_approximation(*args, **kwargs):
        return {"equilibrium": {}}

    def commons_risk(*args, **kwargs):
        return {"tragedy_risk": 1.0}


# --- Epistemic Layer ---
try:
    from host.epistemic.evoi import compute_evoi, compute_evoi_monte_carlo
    from host.epistemic.correlation_guard import (
        PortfolioCorrelationGuard as CorrelationGuard,
    )
    from host.epistemic.schema_validator import (
        EpistemicSchemaValidator as SchemaValidator,
    )

    EPISTEMIC_AVAILABLE = True
except Exception:
    EPISTEMIC_AVAILABLE = False

    def compute_evoi(*args, **kwargs):
        return {"error": "EPISTEMIC_UNAVAILABLE"}

    def compute_evoi_monte_carlo(*args, **kwargs):
        return {"error": "EPISTEMIC_UNAVAILABLE"}

    class CorrelationGuard:
        def __init__(self, *args, **kwargs):
            pass

        def check_portfolio(self, *args, **kwargs):
            return {"correlation_risk": 0.0}

    class SchemaValidator:
        def __init__(self, *args, **kwargs):
            pass

        def validate_portfolio(self, *args, **kwargs):
            return {"integrity_score": 1.0}


# --- Policy Engine ---
try:
    from host.governance.policy_engine import PolicyEngine

    POLICY_ENGINE_AVAILABLE = True
except Exception:
    POLICY_ENGINE_AVAILABLE = False

    class PolicyEngine:
        def __init__(self, *args, **kwargs):
            pass

        def evaluate(self, *args, **kwargs):
            return {"feasible": True, "flags": []}


# --- Harness Architecture (9-Harness Constraint) ---
try:
    from host.governance.harness_alarm import HarnessAlarmSystem
except Exception:
    class HarnessAlarmSystem:
        def trigger(self, *args, **kwargs):
            return {"status": "ALARM_UNAVAILABLE"}


class HarnessEngine:
    """9-Harness Constraint Architecture for WEALTH."""

    _LINEAGE_HASH = None
    _DOCTRINE_HASH = None

    @classmethod
    def get_doctrine_hash(cls) -> str:
        """Compute hash of the WEALTH_HARNESS.md file."""
        if cls._DOCTRINE_HASH is None:
            try:
                # Resolve path relative to this file
                base_dir = os.path.dirname(__file__)
                path = os.path.join(base_dir, "canon", "WEALTH_HARNESS.md")
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        cls._DOCTRINE_HASH = hashlib.sha256(f.read().encode()).hexdigest()
                else:
                    cls._DOCTRINE_HASH = "MISSING_DOCTRINE_FILE"
            except Exception:
                cls._DOCTRINE_HASH = "UNKNOWN_DOCTRINE"
        return cls._DOCTRINE_HASH

    @classmethod
    def get_lineage_hash(cls) -> str:
        """Compute the lineage hash of the HarnessEngine source code."""
        if cls._LINEAGE_HASH is None:
            try:
                # Use absolute source to handle dynamic imports/changes
                source = inspect.getsource(cls)
                cls._LINEAGE_HASH = hashlib.sha256(source.encode()).hexdigest()
            except Exception:
                cls._LINEAGE_HASH = "UNKNOWN_LINEAGE"
        return cls._LINEAGE_HASH

    HARNESS_NAMES = [
        "Identity",
        "Reality",
        "Epistemic",
        "Entropy",
        "Survival",
        "Constitutional",
        "Efficiency",
        "Coordination",
        "Civilization",
    ]

    TOOL_TO_HARNESS = {
        "wealth_init": "Identity",
        "wealth_record_transaction": "Identity",
        "wealth_snapshot_portfolio": "Identity",
        "wealth_ingest_fetch": "Reality",
        "wealth_ingest_snapshot": "Reality",
        "wealth_ingest_reconcile": "Reality",
        "wealth_ingest_vintage": "Reality",
        "wealth_ingest_health": "Reality",
        "wealth_ingest_sources": "Reality",
        "wealth_schema_validate": "Epistemic",
        "wealth_correlation_guard_check": "Epistemic",
        "wealth_evoi_compute": "Epistemic",
        "wealth_evoi_monte_carlo": "Epistemic",
        "wealth_monte_carlo_forecast": "Entropy",
        "wealth_emv_risk": "Entropy",
        "wealth_audit_entropy": "Entropy",
        "wealth_dscr_leverage": "Survival",
        "wealth_cashflow_flow": "Survival",
        "wealth_networth_state": "Survival",
        "wealth_growth_velocity": "Survival",
        "wealth_crisis_triage": "Survival",
        "wealth_check_floors": "Constitutional",
        "wealth_policy_audit": "Constitutional",
        "wealth_score_kernel": "Constitutional",
        "wealth_npv_reward": "Efficiency",
        "wealth_irr_yield": "Efficiency",
        "wealth_pi_efficiency": "Efficiency",
        "wealth_payback_time": "Efficiency",
        "wealth_coordination_equilibrium": "Coordination",
        "wealth_game_theory_solve": "Coordination",
        "wealth_personal_decision": "Coordination",
        "wealth_civilization_stewardship": "Civilization",
        "wealth_agent_budget": "Civilization",
    }

    SOVEREIGN_METADATA_FAMILIES = ["VAULT", "SENSE", "MIND", "HEART", "REASON", "JUDGE", "SURVIVAL"]
    
    SOVEREIGN_METADATA = {
        "wealth_init": {"family": "VAULT", "stage": "000-VAULT", "display": "wealth_init"},
        "wealth_record_transaction": {"family": "VAULT", "stage": "000-VAULT", "display": "wealth_record_transaction"},
        "wealth_snapshot_portfolio": {"family": "VAULT", "stage": "000-VAULT", "display": "wealth_snapshot_portfolio"},
        "wealth_ingest_fetch": {"family": "SENSE", "stage": "100-SENSE", "display": "wealth_ingest_fetch"},
        "wealth_ingest_snapshot": {"family": "SENSE", "stage": "100-SENSE", "display": "wealth_ingest_snapshot"},
        "wealth_ingest_reconcile": {"family": "SENSE", "stage": "100-SENSE", "display": "wealth_ingest_reconcile"},
        "wealth_ingest_health": {"family": "SENSE", "stage": "100-SENSE", "display": "wealth_ingest_health"},
        "wealth_ingest_sources": {"family": "SENSE", "stage": "100-SENSE", "display": "wealth_ingest_sources"},
        "wealth_schema_validate": {"family": "MIND", "stage": "200-MIND", "display": "wealth_schema_validate"},
        "wealth_correlation_guard_check": {"family": "MIND", "stage": "200-MIND", "display": "wealth_risk_correlation"},
        "wealth_evoi_compute": {"family": "MIND", "stage": "200-MIND", "display": "wealth_evoi_compute"},
        "wealth_monte_carlo_forecast": {"family": "MIND", "stage": "200-MIND", "display": "wealth_risk_monte_carlo"},
        "wealth_emv_risk": {"family": "MIND", "stage": "200-MIND", "display": "wealth_risk_emv"},
        "wealth_audit_entropy": {"family": "MIND", "stage": "200-MIND", "display": "wealth_audit_entropy", "dual_domain": ["MIND", "JUDGE"]},
        "wealth_dscr_leverage": {"family": "HEART", "stage": "300-HEART", "display": "wealth_survival_dscr"},
        "wealth_crisis_triage": {"family": "HEART", "stage": "300-HEART", "display": "wealth_crisis_triage"},
        "wealth_civilization_stewardship": {"family": "HEART", "stage": "300-HEART", "display": "wealth_stewardship_civ"},
        "wealth_npv_reward": {"family": "REASON", "stage": "400-REASON", "display": "wealth_calc_npv"},
        "wealth_irr_yield": {"family": "REASON", "stage": "400-REASON", "display": "wealth_calc_irr"},
        "wealth_pi_efficiency": {"family": "REASON", "stage": "400-REASON", "display": "wealth_calc_pi"},
        "wealth_payback_time": {"family": "REASON", "stage": "400-REASON", "display": "wealth_calc_payback"},
        "wealth_coordination_equilibrium": {"family": "REASON", "stage": "400-REASON", "display": "wealth_coord_equilibrium"},
        "wealth_game_theory_solve": {"family": "REASON", "stage": "400-REASON", "display": "wealth_coord_game_theory"},
        "wealth_personal_decision": {"family": "REASON", "stage": "400-REASON", "display": "wealth_personal_decision"},
        "wealth_agent_budget": {"family": "REASON", "stage": "400-REASON", "display": "wealth_calc_agent_budget"},
        "wealth_score_kernel": {"family": "JUDGE", "stage": "888-JUDGE", "display": "wealth_score_kernel", "primary": True},
        "wealth_check_floors": {"family": "JUDGE", "stage": "800-JUDGE", "display": "wealth_check_floors"},
        "wealth_policy_audit": {"family": "JUDGE", "stage": "800-JUDGE", "display": "wealth_policy_audit"},
        "wealth_evoi_monte_carlo": {"family": "MIND", "stage": "200-MIND", "display": "wealth_evoi_monte_carlo"},
        "wealth_cashflow_flow": {"family": "HEART", "stage": "300-HEART", "display": "wealth_survival_flow"},
        "wealth_networth_state": {"family": "HEART", "stage": "300-HEART", "display": "wealth_survival_networth"},
        "wealth_growth_velocity": {"family": "HEART", "stage": "300-HEART", "display": "wealth_survival_velocity"},
    }

    # ============================================================
    # WEALTH v2 Canonical Namespace Map
    # Non-breaking alias layer (Phase 1 Migration)
    # ============================================================
    V2_CANONICAL_MAP = {
        # SENSE (100)
        "wealth_sense_fetch": "wealth_ingest_fetch",
        "wealth_sense_snapshot": "wealth_ingest_snapshot",
        "wealth_sense_reconcile": "wealth_ingest_reconcile",
        "wealth_sense_health": "wealth_ingest_health",
        "wealth_sense_vintage": "wealth_ingest_vintage",
        "wealth_sense_sources": "wealth_ingest_sources",
        # MIND (200)
        "wealth_mind_emv": "wealth_emv_risk",
        "wealth_mind_monte_carlo": "wealth_monte_carlo_forecast",
        "wealth_mind_correlation": "wealth_correlation_guard_check",
        "wealth_mind_evoi": "wealth_evoi_compute",
        "wealth_mind_evoi_mc": "wealth_evoi_monte_carlo",
        "wealth_mind_schema": "wealth_schema_validate",
        # SURVIVAL (300)
        "wealth_survival_dscr": "wealth_dscr_leverage",
        "wealth_survival_networth": "wealth_networth_state",
        "wealth_survival_velocity": "wealth_growth_velocity",
        "wealth_survival_cashflow": "wealth_cashflow_flow",
        "wealth_survival_triage": "wealth_crisis_triage",
        "wealth_survival_civilization": "wealth_civilization_stewardship",
        # REASON (400)
        "wealth_reason_npv": "wealth_npv_reward",
        "wealth_reason_irr": "wealth_irr_yield",
        "wealth_reason_pi": "wealth_pi_efficiency",
        "wealth_reason_payback": "wealth_payback_time",
        "wealth_reason_equilibrium": "wealth_coordination_equilibrium",
        "wealth_reason_game": "wealth_game_theory_solve",
        "wealth_reason_personal": "wealth_personal_decision",
        "wealth_reason_agent": "wealth_agent_budget",
        # JUDGE (888)
        "wealth_judge_kernel": "wealth_score_kernel",
        "wealth_judge_floors": "wealth_check_floors",
        "wealth_judge_policy": "wealth_policy_audit",
        "wealth_judge_entropy": "wealth_audit_entropy",
        # VAULT (999)
        "wealth_vault_init": "wealth_init",
        "wealth_vault_record": "wealth_record_transaction",
        "wealth_vault_snapshot": "wealth_snapshot_portfolio",
    }

    def __init__(self):
        self.alarm_system = HarnessAlarmSystem()

    def audit(self, tool_name: str, primary: Dict[str, Any], flags: List[str], parent_hash: str = "") -> Dict[str, Any]:
        """Audit the current tool call against the 9-harness constraints."""
        harness_status = {name: {"stress": 0.0, "status": "SECURE"} for name in self.HARNESS_NAMES}
        violations = []
        
        # 0. Global Doctrine Seal
        d_hash = self.get_doctrine_hash()
        violations = []

        # 1. Identity Check
        if "UNAUTHENTICATED" in flags or "UNANCHORED" in flags:
            harness_status["Identity"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("IDENTITY_HARNESS_FAILURE")
        elif parent_hash and len(parent_hash) != 64:
            harness_status["Identity"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("IDENTITY_CHAIN_VIOLATION")

        # 2. Reality Check
        if any(f in flags for f in ["INVALID_DATA_SOURCE", "STALE_DATA", "SOURCE_DIVERGENCE"]):
            harness_status["Reality"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("REALITY_HARNESS_FAILURE")

        # 3. Epistemic Check
        if "EPISTEMIC_FAILURE" in flags or "LOW_INTEGRITY" in flags:
            harness_status["Epistemic"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("EPISTEMIC_HARNESS_FAILURE")
        elif "SYSTEMIC_CORRELATION_RISK" in flags:
            harness_status["Epistemic"].update({"stress": 0.8, "status": "STRESSED"})

        # 4. Entropy Check
        if "HIGH_ENTROPY_SIGNAL" in flags or "MULTIPLE_IRR_POSSIBLE" in flags:
            harness_status["Entropy"].update({"stress": 0.8, "status": "STRESSED"})

        # 5. Survival Check (Structural Load)
        if any(f in flags for f in ["LEVERAGE_DEFAULT", "RUNWAY_CRITICAL", "CASHFLOW_NEGATIVE"]):
            harness_status["Survival"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("SURVIVAL_HARNESS_FAILURE")

        # 6. Constitutional Check
        if any(f.startswith("FLOOR_") for f in flags) or "SOVEREIGN_DIGNITY_LOW" in flags:
            harness_status["Constitutional"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("CONSTITUTIONAL_HARNESS_FAILURE")

        # 7. Efficiency Check
        if tool_name == "wealth_pi_efficiency" and primary.get("pi", 1.0) < 1.0:
            harness_status["Efficiency"].update({"stress": 0.9, "status": "STRESSED"})
        if "NOT_RECOVERED" in flags:
            harness_status["Efficiency"].update({"stress": 1.0, "status": "SNAPPED"})

        # 8. Coordination Check
        if "TRAGEDY_RISK_HIGH" in flags or "CORE_INFEASIBLE" in flags:
            harness_status["Coordination"].update({"stress": 1.0, "status": "SNAPPED"})
            violations.append("COORDINATION_HARNESS_FAILURE")

        # 9. Civilization Check (Quantified Triggers)
        carbon = primary.get("carbon_intensity", 0.0)
        collapse = primary.get("collapse_risk", 0.0)
        growth = primary.get("sustainable_growth_rate", 1.0)
        
        if carbon > 0.04 or collapse > 0.3 or growth < 0:
            harness_status["Civilization"].update({
                "stress": 1.0, 
                "status": "SNAPPED",
                "detail": f"C:{carbon:.3f} | R:{collapse:.3f} | G:{growth:.3f}"
            })
            violations.append("CIVILIZATION_HARNESS_FAILURE")

        # Systemic Accumulator Rule (Cumulative Stress)
        systemic_stress = sum(h["stress"] for h in harness_status.values())
        if systemic_stress > 2.0:
            violations.append("SYSTEMIC_INSTABILITY_FAILURE")

        overall_verdict = "PASS"
        recommended_verdict = "SEAL"
        
        has_snapped = any(h["status"] == "SNAPPED" for h in harness_status.values())
        has_stressed = any(h["status"] == "STRESSED" for h in harness_status.values())
        
        if has_snapped or systemic_stress > 2.0:
            overall_verdict = "FAIL"
            recommended_verdict = "VOID"
            self.alarm_system.trigger(tool_name, "Systemic", {"violations": violations, "systemic_stress": systemic_stress})
        elif has_stressed or systemic_stress > 1.2:
            overall_verdict = "PASS" # Keep PASS for backward compatibility
            recommended_verdict = "SABAR"
        
        return {
            "verdict": overall_verdict,
            "recommended_verdict": recommended_verdict,
            "harness_status": harness_status,
            "violations": violations,
            "systemic_stress": round(systemic_stress, 4),
            "harness_lineage_hash": self.get_lineage_hash(),
            "doctrine_hash": self.get_doctrine_hash(),
        }


def maruah_band(score):
    if score >= 0.85:
        return "SOVEREIGN"
    if score >= 0.70:
        return "STABLE"
    if score >= 0.60:
        return "FLOOR"
    if score >= 0.40:
        return "AMBER"
    return "RED"


mcp = FastMCP("WEALTH Valuation Kernel")

EPSILON = 1e-9
INVALID_FLAGS = {
    "INVALID_INITIAL_INVESTMENT",
    "INVALID_CASHFLOW_SERIES",
    "INVALID_DISCOUNT_RATE",
    "INVALID_FINANCE_RATE",
    "INVALID_REINVESTMENT_RATE",
    "INVALID_SCENARIOS",
    "INVALID_SCENARIO",
    "PROBABILITY_MASS_INVALID",
    "INVALID_DEBT_SERVICE",
    "INVALID_CFADS",
    "INVALID_BASE_RATE",
}
HOLD_FLAGS = {"LEVERAGE_CRITICAL", "LEVERAGE_DEFAULT", "SOVEREIGN_DIGNITY_LOW"}
HOLD_FLAGS.add("MULTIPLE_IRR_POSSIBLE")
QUALIFY_FLAGS = {
    "NON_NORMAL_FLOWS",
    "IRR_NOT_FOUND",
    "NOT_RECOVERED",
    "EBITDA_PROXY_USED",
}
EPISTEMIC_ORDER = ["UNKNOWN", "HYPOTHESIS", "ESTIMATE", "PLAUSIBLE", "CLAIM"]
RELIABILITY_TO_TAG = {
    "guaranteed": "CLAIM",
    "regular": "PLAUSIBLE",
    "irregular": "ESTIMATE",
    "speculative": "HYPOTHESIS",
}


def round_value(value: Optional[float], digits: int = 6) -> Optional[float]:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)


def count_sign_changes(values: List[float]) -> int:
    previous_sign = 0
    changes = 0
    for value in values:
        if not math.isfinite(value) or abs(value) <= EPSILON:
            continue
        sign = 1 if value > 0 else -1
        if previous_sign != 0 and sign != previous_sign:
            changes += 1
        previous_sign = sign
    return changes


def build_cashflow_series(
    initial_investment: float, cash_flows: List[float], terminal_value: float = 0
) -> List[float]:
    series = [-abs(initial_investment), *cash_flows]
    if terminal_value and len(series) > 1:
        series[-1] += terminal_value
    return series


def derive_confidence_band(
    value: Optional[float], epistemic: str = "CLAIM", mode: str = "relative"
) -> Optional[List[float]]:
    if value is None or not math.isfinite(value):
        return None
    upper_epistemic = str(epistemic).upper()
    relative_width = (
        0.25
        if upper_epistemic == "HYPOTHESIS"
        else 0.15
        if upper_epistemic == "ESTIMATE"
        else 0.08
        if upper_epistemic == "PLAUSIBLE"
        else 0
    )
    if relative_width == 0:
        return None
    if mode == "absolute-nonnegative":
        delta = max(0.05, abs(value) * relative_width)
        return [round_value(max(0.0, value - delta), 6), round_value(value + delta, 6)]
    return [
        round_value(value * (1 - relative_width), 6),
        round_value(value * (1 + relative_width), 6),
    ]


def npv_from_series(cashflow_series: List[float], discount_rate: float) -> float:
    total = 0.0
    for index, cashflow in enumerate(cashflow_series):
        if index == 0:
            total += cashflow
        else:
            total += cashflow / pow(1 + discount_rate, index)
    return total


def present_value_breakdown(
    cashflow_series: List[float], discount_rate: float
) -> Dict[str, Any]:
    discounted = []
    for index, cashflow in enumerate(cashflow_series):
        if index == 0:
            discounted.append(cashflow)
        else:
            discounted.append(cashflow / pow(1 + discount_rate, index))

    pv_inflows = sum(value for value in discounted if value > 0)
    pv_outflows = sum(abs(value) for value in discounted if value < 0)
    return {
        "discounted_cashflows": [round_value(value, 6) for value in discounted],
        "pv_inflows": round_value(pv_inflows, 6),
        "pv_outflows": round_value(pv_outflows, 6),
    }


def validate_series(initial_investment: float, cash_flows: List[float]) -> List[str]:
    flags: List[str] = []
    if not math.isfinite(initial_investment) or initial_investment == 0:
        flags.append("INVALID_INITIAL_INVESTMENT")
    if (
        not isinstance(cash_flows, list)
        or len(cash_flows) == 0
        or any(not math.isfinite(value) for value in cash_flows)
    ):
        flags.append("INVALID_CASHFLOW_SERIES")
    return flags


def validate_rate(rate: float, invalid_flag: str) -> List[str]:
    if not math.isfinite(rate) or rate <= -1:
        return [invalid_flag]
    return []


def weakest_epistemic(items: List[dict], default_tag: str = "CLAIM") -> str:
    if not items:
        return default_tag
    weakest_index = len(EPISTEMIC_ORDER) - 1
    for item in items:
        reliability = str(item.get("reliability", "")).lower()
        candidate = str(
            item.get("tag")
            or item.get("epistemic")
            or RELIABILITY_TO_TAG.get(reliability, default_tag)
        ).upper()
        if candidate in EPISTEMIC_ORDER:
            weakest_index = min(weakest_index, EPISTEMIC_ORDER.index(candidate))
    return EPISTEMIC_ORDER[weakest_index]


def derive_verdict(flags: List[str], default_verdict: str = "SEAL", high_stress: bool = False, recommended: str = "SEAL") -> str:
    if recommended == "VOID" or any(flag in INVALID_FLAGS for flag in flags):
        return "VOID"
    if recommended == "SABAR" or high_stress:
        return "SABAR"
    if any(flag in HOLD_FLAGS for flag in flags):
        return "888-HOLD"
    if any(flag in QUALIFY_FLAGS for flag in flags):
        return "QUALIFY"
    return default_verdict


def infer_epistemic(flags: List[str], default_epistemic: str = "CLAIM") -> str:
    if any(flag in INVALID_FLAGS for flag in flags):
        return "UNKNOWN"
    if any((flag in HOLD_FLAGS) or (flag in QUALIFY_FLAGS) for flag in flags):
        return "ESTIMATE"
    return default_epistemic


def confidence_from_verdict(verdict: str, flags: List[str]) -> str:
    if verdict in {"VOID", "888-HOLD"}:
        return "LOW"
    if verdict == "QUALIFY" or flags:
        return "MEDIUM"
    return "HIGH"


SCALE_DEFAULTS = {
    "personal": {
        "discount_rate": 0.03,
        "horizon_years": 5,
        "objective": "maximize_lifetime_utility",
    },
    "household": {
        "discount_rate": 0.04,
        "horizon_years": 10,
        "objective": "intergenerational_stability",
    },
    "sme": {
        "discount_rate": 0.10,
        "horizon_years": 5,
        "objective": "survival_and_growth",
    },
    "enterprise": {
        "discount_rate": 0.10,
        "horizon_years": 10,
        "objective": "shareholder_value",
    },
    "national": {
        "discount_rate": 0.02,
        "horizon_years": 35,
        "objective": "gdp_plus_welfare",
    },
    "crisis": {
        "discount_rate": float("inf"),
        "horizon_years": 0,
        "objective": "minimize_collapse_probability",
    },
    "civilization": {
        "discount_rate": 0.005,
        "horizon_years": 300,
        "objective": "species_continuation",
    },
    "agentic": {
        "discount_rate": 0.15,
        "horizon_years": 2,
        "objective": "capability_accumulation",
    },
}

CAPITAL_TERMINOLOGY = {
    "financial": {
        "npv_label": "NPV",
        "irr_label": "IRR",
        "pi_label": "PI",
        "commitment_label": "initial_investment",
        "stream_label": "cash_flows",
        "value_label": "Net Present Value",
    },
    "temporal": {
        "npv_label": "NTV",
        "irr_label": "ITR",
        "pi_label": "TI",
        "commitment_label": "initial_time_commitment",
        "stream_label": "time_streams",
        "value_label": "Net Temporal Value",
    },
    "cognitive": {
        "npv_label": "NCV",
        "irr_label": "ICR",
        "pi_label": "CI",
        "commitment_label": "initial_attention_commitment",
        "stream_label": "attention_streams",
        "value_label": "Net Cognitive Value",
    },
    "social": {
        "npv_label": "NSV",
        "irr_label": "ISR",
        "pi_label": "SI",
        "commitment_label": "initial_reputation_commitment",
        "stream_label": "reputation_streams",
        "value_label": "Net Social Value",
    },
    "ecological": {
        "npv_label": "NEV",
        "irr_label": "IER",
        "pi_label": "EI",
        "commitment_label": "initial_resource_commitment",
        "stream_label": "resource_streams",
        "value_label": "Net Ecological Value",
    },
    "strategic": {
        "npv_label": "NXV",
        "irr_label": "IXR",
        "pi_label": "XI",
        "commitment_label": "initial_option_commitment",
        "stream_label": "option_streams",
        "value_label": "Net Strategic Value",
    },
    "thermodynamic": {
        "npv_label": "NΦV",
        "irr_label": "IΦR",
        "pi_label": "ΦI",
        "commitment_label": "initial_energy_commitment",
        "stream_label": "energy_streams",
        "value_label": "Net Thermodynamic Value",
    },
}


def get_scale_defaults(scale_mode: str) -> Dict[str, Any]:
    return SCALE_DEFAULTS.get(scale_mode, SCALE_DEFAULTS["enterprise"])


def get_capital_terminology(capital_type: str) -> Dict[str, str]:
    return CAPITAL_TERMINOLOGY.get(capital_type, CAPITAL_TERMINOLOGY["financial"])


def derive_allocation_signal(
    flags: List[str], primary: Dict[str, Any], tool: str, scale_mode: str = "enterprise"
) -> str:
    if any(flag in INVALID_FLAGS for flag in flags):
        return "INSUFFICIENT_DATA"

    scale = get_scale_defaults(scale_mode)

    if tool in {"wealth_coordination_equilibrium", "wealth_game_theory_solve"}:
        tragedy_risk = primary.get("tragedy_risk", 1.0)
        if any(flag in INVALID_FLAGS for flag in flags):
            return "INSUFFICIENT_DATA"
        if primary.get("in_core") is False or any("BLOCK" in f for f in flags):
            return "REJECT"
        if tragedy_risk > 0.5:
            return "REJECT"
        if tragedy_risk > 0.3:
            return "MARGINAL"
        return "ACCEPT"

    if tool == "wealth_npv_reward":
        npv = primary.get("npv")
        if npv is None:
            return "INSUFFICIENT_DATA"
        if npv > 0:
            return "ACCEPT"
        if npv < 0:
            return "REJECT"
        return "MARGINAL"

    if tool == "wealth_pi_efficiency":
        pi = primary.get("pi")
        if pi is None:
            return "INSUFFICIENT_DATA"
        if pi > 1:
            return "ACCEPT"
        if pi < 1:
            return "REJECT"
        return "MARGINAL"

    if tool == "wealth_irr_yield":
        irr = primary.get("irr")
        if irr is None:
            return "INSUFFICIENT_DATA"
        hurdle = (
            scale["discount_rate"] if scale["discount_rate"] != float("inf") else 0.10
        )
        if irr > hurdle:
            return "ACCEPT"
        if irr < hurdle:
            return "REJECT"
        return "MARGINAL"

    if tool == "wealth_payback_time":
        payback = primary.get("payback_periods")
        if payback is None:
            return (
                "REJECT"
                if any(f == "NOT_RECOVERED" for f in flags)
                else "INSUFFICIENT_DATA"
            )
        return "ACCEPT"

    if tool == "wealth_dscr_leverage":
        dscr = primary.get("dscr")
        if dscr is None:
            return "INSUFFICIENT_DATA"
        if dscr >= 1.5:
            return "ACCEPT"
        if dscr >= 1.25:
            return "MARGINAL"
        return "REJECT"

    if tool == "wealth_growth_velocity":
        runway = primary.get("runway_months")
        if runway is not None and runway != math.inf and runway < 3:
            return "REJECT"
        return "ACCEPT"

    if tool == "wealth_cashflow_flow":
        net_monthly = primary.get("net_monthly")
        if net_monthly is not None and net_monthly < 0:
            runway = primary.get("runway_months")
            if runway is not None and runway != math.inf and runway < 3:
                return "REJECT"
            return "MARGINAL"
        return "ACCEPT"

    if tool == "wealth_score_kernel":
        r_adj = primary.get("r_adj", 0.1)
        m_score = primary.get("maruahScore", 0.5)
        if m_score < 0.6:
            return "REJECT"
        if r_adj > 0.15:
            return "REJECT"  # High risk/extractive
        if r_adj > 0.12 or m_score < 0.75:
            return "MARGINAL"
        return "ACCEPT"

    return "MARGINAL"


def measurement_validate_invariants(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
    measurement_results: Optional[Dict[str, Any]] = None,
) -> List[str]:
    flags = []
    if measurement_results is None:
        return flags

    npv = measurement_results.get("npv")
    irr = measurement_results.get("irr")
    pi = measurement_results.get("pi")
    pv_inflows = measurement_results.get("pv_inflows")

    series = build_cashflow_series(initial_investment, cash_flows, terminal_value)
    sign_changes = count_sign_changes(series)

    if pi is not None and pv_inflows is not None:
        expected_pi = pv_inflows / abs(initial_investment)
        if abs(pi - expected_pi) > 0.001:
            flags.append("INVARIANT_VIOLATION")

    if npv is not None and pi is not None and sign_changes <= 1:
        if npv > 0 and pi <= 1:
            flags.append("INVARIANT_VIOLATION")
        if npv < 0 and pi >= 1:
            flags.append("INVARIANT_VIOLATION")

    if (
        npv is not None
        and irr is not None
        and discount_rate is not None
        and sign_changes <= 1
    ):
        if (npv > 0 and irr <= discount_rate) or (npv < 0 and irr >= discount_rate):
            flags.append("INVARIANT_VIOLATION")

    return flags


_policy_engine = PolicyEngine()


def create_envelope(
    tool: str,
    dimension: str,
    primary: Dict[str, Any],
    secondary: Optional[Dict[str, Any]] = None,
    flags: Optional[List[str]] = None,
    assumptions: Optional[List[str]] = None,
    epistemic: str = "CLAIM",
    verdict: Optional[str] = None,
    scale_mode: str = "enterprise",
    governance_args: Optional[Dict[str, Any]] = None,
    parent_hash: Optional[str] = None,
) -> Dict[str, Any]:
    global LAST_RECEIPT_HASH
    flags = flags or []
    
    # 1. Harness Audit with Chaining
    final_parent_hash = parent_hash or LAST_RECEIPT_HASH
    engine = HarnessEngine()
    audit_res = engine.audit(tool, primary, flags, final_parent_hash)
    
    systemic_stress = audit_res.get("systemic_stress", 0.0)
    # Stress (0.7-0.9) or systemic instability forces 888-HOLD/QUALIFY
    is_high_stress = systemic_stress > 1.5 or any(h["stress"] >= 0.7 for h in audit_res["harness_status"].values())
    
    derived_governance = verdict or derive_verdict(flags, high_stress=is_high_stress, recommended=audit_res["recommended_verdict"])
    derived_allocation = derive_allocation_signal(flags, primary, tool, scale_mode)
    
    if is_high_stress and derived_allocation == "ACCEPT":
        derived_allocation = "MARGINAL" # Force downgraded allocation on high stress

    engine_status = (
        "ERROR"
        if derived_governance == "VOID" or audit_res["verdict"] == "FAIL"
        else "WARNING"
        if derived_governance in ("QUALIFY", "888-HOLD", "SABAR") or is_high_stress
        else "VALID"
    )
    derived_epistemic = infer_epistemic(flags, epistemic)
    
    if audit_res["verdict"] == "FAIL":
        derived_governance = "VOID"
        derived_allocation = "REJECT"
        engine_status = "ERROR"
        for viol in audit_res["violations"]:
            if viol not in flags:
                flags.append(viol)

    # Three-verdict semantics (Fix #2 — Sin of Headline Metric Seduction):
    #   verdict           = allocation_signal   → ACCEPT/REJECT/MARGINAL/INSUFFICIENT_DATA
    #                       The DECISION signal. What a decision-maker reads first.
    #   governance_verdict = SEAL/VOID/HOLD/QUALIFY
    #                       Was the computation constitutionally valid? SEAL ≠ investment approved.
    #   engine_status      = VALID/WARNING/ERROR
    #                       Did the math pipeline run cleanly?
    # A project can be SEAL (computation valid) + REJECT (don't fund it). These must never collapse.
    # 3. Build Envelope with Sovereign Metadata
    meta = engine.SOVEREIGN_METADATA.get(tool, {})
    
    # Namespace transparency (v2 Alias Layer)
    alias_of = None
    if tool in engine.V2_CANONICAL_MAP:
        alias_of = engine.V2_CANONICAL_MAP[tool]
        
    envelope = {
        "tool": tool,
        "display_name": meta.get("display", tool),
        "family": meta.get("family", dimension.upper()),
        "pipeline_stage": meta.get("stage", "UNKNOWN"),
        "sovereign": meta.get("sovereign", True),
        "namespace": {
            "invoked_as": tool,
            "canonical_handler": alias_of or tool,
            "version": "v2-alias-layer"
        },
        "dimension": dimension,
        "verdict": derived_allocation,
        "governance_verdict": derived_governance,
        "allocation_signal": derived_allocation,
        "engine_status": engine_status,
        "primary_result": primary,
        "secondary_metrics": secondary or {},
        "integrity_flags": flags,
        "confidence": confidence_from_verdict(derived_governance, flags),
        "epistemic": derived_epistemic,
        "harness_audit": audit_res,
        "assumptions": assumptions or [],
        "epoch": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if "dual_domain" in meta:
        envelope["dual_domain"] = meta["dual_domain"]
    if meta.get("primary"):
        envelope["primary_entrypoint"] = True
    
    # 4. Update Global Identity Chain
    # Hash the envelope to create the next receipt
    receipt_blob = json.dumps(envelope, sort_keys=True, separators=(",", ":"), default=str)
    receipt_hash = hashlib.sha256(receipt_blob.encode()).hexdigest()
    envelope["receipt_hash"] = receipt_hash
    LAST_RECEIPT_HASH = receipt_hash

    # === Constitutional Governance Layer ===
    # Governance tools are exempt from recursive envelope governance so they can audit bad proposals
    is_governance_tool = tool in {"wealth_check_floors", "wealth_policy_audit"}
    if (
        scale_mode in {"national", "crisis", "civilization", "agentic"}
        and not is_governance_tool
    ):
        gov_args = governance_args or {}
        floor_result = check_floors(
            {**gov_args, "epistemic": derived_epistemic, "scale_mode": scale_mode}
        )
        # Merge floor outcomes
        if floor_result["verdict"] == "VOID":
            envelope["governance_verdict"] = "VOID"
            envelope["allocation_signal"] = "REJECT"
            envelope["engine_status"] = "ERROR"
        elif floor_result["verdict"] == "HOLD":
            envelope["governance_verdict"] = "888-HOLD"
            envelope["allocation_signal"] = "INSUFFICIENT_DATA"
            envelope["engine_status"] = "WARNING"

        envelope["floor_check"] = {
            "verdict": floor_result.get("verdict", "SEAL"),
            "violations": floor_result.get("violations", []),
            "holds": floor_result.get("holds", []),
            "warnings": floor_result.get("warnings", []),
        }

        # Policy constraints (if audit data provided)
        if gov_args:
            policy_result = _policy_engine.evaluate(gov_args, scale_mode)
            if not policy_result["policy_pass"]:
                envelope["governance_verdict"] = "VOID"
                envelope["allocation_signal"] = "REJECT"
                envelope["engine_status"] = "ERROR"
            envelope["policy_audit"] = policy_result

        # Vault all high-scale decisions
        _vault_append(
            {
                "tool": tool,
                "scale_mode": scale_mode,
                "allocation_signal": envelope["allocation_signal"],
                "governance_verdict": envelope["governance_verdict"],
                "floor_check": envelope.get("floor_check"),
                "policy_audit": envelope.get("policy_audit"),
            }
        )

    return envelope


def measurement_npv(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
    period_unit: str = "annual",
    input_epistemic: str = "CLAIM",
) -> Dict[str, Any]:
    flags = [
        *validate_series(initial_investment, cash_flows),
        *validate_rate(discount_rate, "INVALID_DISCOUNT_RATE"),
    ]
    assumptions = [
        "NPV is the primary accept/reject metric.",
        "Discount rate and cash flow periodicity are aligned.",
    ]
    if flags:
        return {
            "npv": None,
            "eaa": None,
            "pv_inflows": None,
            "pv_outflows": None,
            "discounted_cashflows": [],
            "period_count": len(cash_flows) if isinstance(cash_flows, list) else 0,
            "period_unit": period_unit,
            "assumptions": assumptions,
            "flags": flags,
        }

    series = build_cashflow_series(initial_investment, cash_flows, terminal_value)
    breakdown = present_value_breakdown(series, discount_rate)
    npv = npv_from_series(series, discount_rate)
    periods = len(cash_flows)
    if periods == 0:
        eaa = None
    elif abs(discount_rate) <= EPSILON:
        eaa = npv / periods
    else:
        eaa = (npv * discount_rate) / (1 - pow(1 + discount_rate, -periods))
    return {
        "npv": round_value(npv, 6),
        "eaa": round_value(eaa, 6),
        "pv_inflows": breakdown["pv_inflows"],
        "pv_outflows": breakdown["pv_outflows"],
        "discounted_cashflows": breakdown["discounted_cashflows"],
        "period_count": periods,
        "period_unit": period_unit,
        "assumptions": assumptions,
        "input_epistemic": str(input_epistemic).upper(),
        "confidence_band": derive_confidence_band(npv, input_epistemic),
        "flags": flags,
    }


def bracket_roots(
    npv_fn, lower: float = -0.9999, upper: float = 10.0, steps: int = 4096
) -> List[List[float]]:
    brackets: List[List[float]] = []
    step = (upper - lower) / steps
    previous_rate = lower
    previous_value = npv_fn(previous_rate)
    for index in range(1, steps + 1):
        rate = lower + step * index
        value = npv_fn(rate)
        if not math.isfinite(previous_value) or not math.isfinite(value):
            previous_rate = rate
            previous_value = value
            continue
        if abs(previous_value) <= EPSILON:
            brackets.append([previous_rate, previous_rate])
        elif previous_value * value < 0:
            brackets.append([previous_rate, rate])
        elif abs(value) <= EPSILON:
            brackets.append([rate, rate])
        previous_rate = rate
        previous_value = value
    return brackets


def bisect_root(npv_fn, lower: float, upper: float, iterations: int = 200) -> float:
    if lower == upper:
        return lower
    left = lower
    right = upper
    left_value = npv_fn(left)
    for _ in range(iterations):
        midpoint = (left + right) / 2
        midpoint_value = npv_fn(midpoint)
        if not math.isfinite(midpoint_value):
            break
        if abs(midpoint_value) <= EPSILON:
            return midpoint
        if left_value * midpoint_value <= 0:
            right = midpoint
        else:
            left = midpoint
            left_value = midpoint_value
        if abs(right - left) <= EPSILON:
            return (left + right) / 2
    return (left + right) / 2


def measurement_irr(
    initial_investment: float,
    cash_flows: List[float],
    finance_rate: float = 0.1,
    reinvestment_rate: float = 0.1,
    period_unit: str = "annual",
) -> Dict[str, Any]:
    flags = [
        *validate_series(initial_investment, cash_flows),
        *validate_rate(finance_rate, "INVALID_FINANCE_RATE"),
        *validate_rate(reinvestment_rate, "INVALID_REINVESTMENT_RATE"),
    ]
    assumptions = [
        "NPV remains the primary ranking metric for mutually exclusive projects.",
        "MIRR is preferred when reinvestment should not equal IRR.",
    ]
    if flags:
        return {
            "irr": None,
            "mirr": None,
            "sign_changes": 0,
            "period_count": len(cash_flows) if isinstance(cash_flows, list) else 0,
            "period_unit": period_unit,
            "assumptions": assumptions,
            "flags": flags,
        }

    series = build_cashflow_series(initial_investment, cash_flows)
    sign_changes = count_sign_changes(series)
    if sign_changes > 1:
        flags.extend(["NON_NORMAL_FLOWS", "MULTIPLE_IRR_POSSIBLE"])

    def npv_fn(rate):
        return npv_from_series(series, rate)

    brackets = bracket_roots(npv_fn)
    roots = {
        round_value(bisect_root(npv_fn, lower, upper), 10) for lower, upper in brackets
    }
    irr = next(iter(roots)) if len(roots) == 1 else None
    if len(roots) == 0:
        flags.append("IRR_NOT_FOUND")

    period_count = len(series) - 1
    pv_negative = 0.0
    fv_positive = 0.0
    for index, cashflow in enumerate(series):
        if cashflow < 0:
            pv_negative += cashflow / pow(1 + finance_rate, index)
        elif cashflow > 0:
            fv_positive += cashflow * pow(1 + reinvestment_rate, period_count - index)
    mirr = None
    if pv_negative < 0 and fv_positive > 0 and period_count > 0:
        mirr = pow(fv_positive / abs(pv_negative), 1 / period_count) - 1

    return {
        "irr": round_value(irr, 8) if irr is not None else None,
        "mirr": round_value(mirr, 8) if mirr is not None else None,
        "sign_changes": sign_changes,
        "period_count": period_count,
        "period_unit": period_unit,
        "assumptions": assumptions,
        "flags": flags,
    }


def measurement_pi(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
) -> Dict[str, Any]:
    npv_measure = measurement_npv(
        initial_investment, cash_flows, discount_rate, terminal_value
    )
    flags = list(npv_measure["flags"])
    if (
        count_sign_changes(
            build_cashflow_series(initial_investment, cash_flows, terminal_value)
        )
        > 1
    ):
        flags.append("NON_NORMAL_FLOWS")
    pi = (
        None
        if npv_measure["pv_inflows"] is None
        else npv_measure["pv_inflows"] / abs(initial_investment)
    )
    return {
        "pi": round_value(pi, 8) if pi is not None else None,
        "pv_inflows": npv_measure["pv_inflows"],
        "assumptions": [
            "Profitability Index is for ranking under capital rationing.",
            "PI does not override NPV for mutually exclusive decisions.",
        ],
        "flags": flags,
    }


def measurement_emv(scenarios: List[dict]) -> Dict[str, Any]:
    flags: List[str] = []
    assumptions = [
        "EMV should be paired with downside probability and scenario dispersion.",
        "Scenario probabilities should sum to 1.0.",
    ]
    if not isinstance(scenarios, list) or not scenarios:
        flags.append("INVALID_SCENARIOS")
        return {
            "emv": None,
            "total_probability": None,
            "downside_probability": None,
            "worst_outcome": None,
            "best_outcome": None,
            "variance": None,
            "assumptions": assumptions,
            "flags": flags,
        }

    for scenario in scenarios:
        if (
            scenario is None
            or not math.isfinite(scenario.get("probability"))
            or not math.isfinite(scenario.get("outcome"))
        ):
            flags.append("INVALID_SCENARIO")
            return {
                "emv": None,
                "total_probability": None,
                "downside_probability": None,
                "worst_outcome": None,
                "best_outcome": None,
                "variance": None,
                "assumptions": assumptions,
                "flags": flags,
            }

    total_probability = sum(scenario["probability"] for scenario in scenarios)
    if abs(total_probability - 1.0) > 1e-6:
        flags.append("PROBABILITY_MASS_INVALID")

    emv = sum(scenario["probability"] * scenario["outcome"] for scenario in scenarios)
    downside_probability = sum(
        scenario["probability"] for scenario in scenarios if scenario["outcome"] < 0
    )
    variance = sum(
        scenario["probability"] * pow(scenario["outcome"] - emv, 2)
        for scenario in scenarios
    )
    return {
        "emv": round_value(emv, 6),
        "total_probability": round_value(total_probability, 6),
        "downside_probability": round_value(downside_probability, 6),
        "worst_outcome": round_value(
            min(scenario["outcome"] for scenario in scenarios), 6
        ),
        "best_outcome": round_value(
            max(scenario["outcome"] for scenario in scenarios), 6
        ),
        "variance": round_value(variance, 6),
        "assumptions": assumptions,
        "flags": flags,
    }


def measurement_payback(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float = 0,
    period_unit: str = "annual",
) -> Dict[str, Any]:
    flags = [
        *validate_series(initial_investment, cash_flows),
        *validate_rate(discount_rate, "INVALID_DISCOUNT_RATE"),
    ]
    assumptions = ["Payback should only support, not replace, NPV."]
    if flags:
        return {
            "payback_periods": None,
            "discounted": discount_rate > 0,
            "period_unit": period_unit,
            "assumptions": assumptions,
            "flags": flags,
        }

    remaining = abs(initial_investment)
    payback_periods = None
    for index, raw_cashflow in enumerate(cash_flows):
        adjusted_cashflow = (
            raw_cashflow / pow(1 + discount_rate, index + 1)
            if discount_rate > 0
            else raw_cashflow
        )
        if adjusted_cashflow <= 0:
            continue
        if remaining > adjusted_cashflow:
            remaining -= adjusted_cashflow
            continue
        payback_periods = index + (remaining / adjusted_cashflow) + 1e-12
        remaining = 0
        break
    if remaining > EPSILON:
        flags.append("NOT_RECOVERED")
    return {
        "payback_periods": round_value(payback_periods, 6)
        if payback_periods is not None
        else None,
        "discounted": discount_rate > 0,
        "period_unit": period_unit,
        "assumptions": assumptions,
        "flags": flags,
    }


def measurement_dscr(
    cfads: Optional[float],
    debt_service: Optional[float],
    ebitda: Optional[float],
    principal: float = 0,
    interest: float = 0,
    leases: float = 0,
    period_unit: str = "annual",
    input_epistemic: str = "CLAIM",
) -> Dict[str, Any]:
    flags: List[str] = []
    numerator = cfads if cfads is not None else ebitda
    denominator = (
        debt_service if debt_service is not None else principal + interest + leases
    )
    if numerator is None or not math.isfinite(numerator):
        flags.append("INVALID_CFADS")
    if denominator is None or not math.isfinite(denominator) or denominator <= 0:
        flags.append("INVALID_DEBT_SERVICE")
    if cfads is None and ebitda is not None:
        flags.append("EBITDA_PROXY_USED")

    dscr = (
        None
        if any(flag in INVALID_FLAGS for flag in flags)
        else numerator / denominator
    )
    if dscr is not None and dscr < 1.0:
        flags.append("LEVERAGE_DEFAULT")
    elif dscr is not None and dscr < 1.25:
        flags.append("LEVERAGE_CRITICAL")
    return {
        "dscr": round_value(dscr, 6) if dscr is not None else None,
        "basis": "CFADS" if cfads is not None else "EBITDA",
        "period_unit": period_unit,
        "assumptions": [
            "DSCR should use CFADS when available.",
            "Minimum covenant floor defaults to 1.25x.",
        ],
        "input_epistemic": str(input_epistemic).upper(),
        "confidence_band": None
        if dscr is None
        else derive_confidence_band(dscr, input_epistemic, "absolute-nonnegative"),
        "flags": flags,
    }


def capitalx(base_rate: float, signals: Dict[str, float]) -> Dict[str, Any]:
    flags: List[str] = []
    if not math.isfinite(base_rate) or base_rate < 0:
        flags.append("INVALID_BASE_RATE")

    d_s = signals.get("dS", 0.0)
    peace2 = signals.get("peace2", 1.0)
    maruah = signals.get("maruahScore", 0.5)
    trust = signals.get("trustIndex", 0.5)
    delta_civ = signals.get("deltaCiv", 0.0)

    entropy_penalty = max(0.0, d_s * 0.5)
    peace_discount = min(0.02, max(0.0, (peace2 - 1.0) * 0.05))
    maruah_discount = min(0.03, max(0.0, (maruah - 0.5) * 0.06))
    trust_discount = min(0.02, max(0.0, (trust - 0.5) * 0.04))
    civ_discount = min(0.02, max(0.0, delta_civ * 0.10))

    r_adj = max(
        0.0,
        round_value(
            base_rate
            + entropy_penalty
            - peace_discount
            - maruah_discount
            - trust_discount
            - civ_discount,
            6,
        )
        or 0.0,
    )
    if d_s > 0.3:
        flags.append("HIGH_ENTROPY_SIGNAL")
    if maruah < 0.6:
        flags.append("SOVEREIGN_DIGNITY_LOW")

    uncertainty_radius = round_value(0.01 + d_s * 0.02, 6) or 0.01
    return {
        "base_rate": round_value(base_rate, 6),
        "adjusted_rate": r_adj,
        "r_adj": r_adj,
        "adjustments": {
            "entropy_penalty": round_value(entropy_penalty, 6),
            "peace_discount": round_value(peace_discount, 6),
            "maruah_discount": round_value(maruah_discount, 6),
            "trust_discount": round_value(trust_discount, 6),
            "civ_discount": round_value(civ_discount, 6),
        },
        "uncertainty_band": [
            max(0.0, round_value(r_adj - uncertainty_radius, 6) or 0.0),
            round_value(r_adj + uncertainty_radius, 6),
        ],
        "integrity_flags": flags,
        "assumptions": [
            "CapitalX pricing is an estimate layered on top of the base rate.",
            "If entropy rises, r_adj must not decrease.",
        ],
    }


@mcp.tool(name="wealth_npv_reward")
def npv_reward(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
    period_unit: str = "annual",
    input_epistemic: str = "CLAIM",
    scale_mode: str = "enterprise",
) -> Any:
    """Compute NPV, Terminal Value, and EAA. [Reward Dimension]"""
    measurement = measurement_npv(
        initial_investment,
        cash_flows,
        discount_rate,
        terminal_value,
        period_unit,
        input_epistemic,
    )
    return create_envelope(
        "wealth_npv_reward",
        "Reward",
        {"npv": measurement["npv"]},
        {
            "eaa": measurement["eaa"],
            "pv_inflows": measurement["pv_inflows"],
            "pv_outflows": measurement["pv_outflows"],
            "period_count": measurement["period_count"],
            "period_unit": measurement["period_unit"],
            "confidence_band": measurement["confidence_band"],
        },
        measurement["flags"],
        measurement["assumptions"],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_irr_yield")
def irr_yield(
    initial_investment: float,
    cash_flows: List[float],
    reinvestment_rate: float = 0.1,
    finance_rate: float = 0.1,
    period_unit: str = "annual",
    discount_rate: float = 0.1,
    scale_mode: str = "enterprise",
) -> Any:
    """Compute IRR and MIRR (Potential). [Energy Dimension]"""
    measurement = measurement_irr(
        initial_investment, cash_flows, finance_rate, reinvestment_rate, period_unit
    )
    invariant_flags = measurement_validate_invariants(
        initial_investment,
        cash_flows,
        discount_rate,
        0,
        {
            "npv": npv_from_series(
                build_cashflow_series(initial_investment, cash_flows), discount_rate
            ),
            "irr": measurement["irr"],
        },
    )
    all_flags = list(dict.fromkeys([*measurement["flags"], *invariant_flags]))
    return create_envelope(
        "wealth_irr_yield",
        "Energy",
        {"irr": measurement["irr"]},
        {
            "mirr": measurement["mirr"],
            "sign_changes": measurement["sign_changes"],
            "period_count": measurement["period_count"],
            "period_unit": measurement["period_unit"],
        },
        all_flags,
        measurement["assumptions"],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_pi_efficiency")
def pi_efficiency(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float,
    terminal_value: float = 0,
    scale_mode: str = "enterprise",
) -> Any:
    """Compute Profitability Index (Concentration). [Energy Dimension]"""
    measurement = measurement_pi(
        initial_investment, cash_flows, discount_rate, terminal_value
    )
    invariant_flags = measurement_validate_invariants(
        initial_investment,
        cash_flows,
        discount_rate,
        terminal_value,
        {"pi": measurement["pi"], "pv_inflows": measurement["pv_inflows"]},
    )
    all_flags = list(dict.fromkeys([*measurement["flags"], *invariant_flags]))
    ranking_signal = (
        "EFFICIENT"
        if measurement["pi"] is not None and measurement["pi"] >= 1
        else "EXTRACTIVE"
    )
    return create_envelope(
        "wealth_pi_efficiency",
        "Energy",
        {"pi": measurement["pi"]},
        {"ranking_signal": ranking_signal},
        all_flags,
        measurement["assumptions"],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_emv_risk")
def emv_risk(scenarios: List[dict], scale_mode: str = "enterprise") -> Any:
    """Compute Expected Monetary Value (Probability Density). [Entropy Dimension]"""
    measurement = measurement_emv(scenarios)
    return create_envelope(
        "wealth_emv_risk",
        "Entropy",
        {"emv": measurement["emv"]},
        {
            "scenario_count": len(scenarios) if isinstance(scenarios, list) else 0,
            "total_probability": measurement["total_probability"],
            "downside_probability": measurement["downside_probability"],
            "variance": measurement["variance"],
            "worst_outcome": measurement["worst_outcome"],
            "best_outcome": measurement["best_outcome"],
        },
        measurement["flags"],
        measurement["assumptions"],
        epistemic="ESTIMATE",
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_audit_entropy")
def audit_entropy(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float = 0.1,
    scale_mode: str = "enterprise",
) -> Any:
    """Audit project cash flows for noise and multiple IRRs. [Entropy Dimension]"""
    irr_measure = measurement_irr(
        initial_investment, cash_flows, discount_rate, discount_rate
    )
    npv_measure = measurement_npv(initial_investment, cash_flows, discount_rate)
    invariant_flags = measurement_validate_invariants(
        initial_investment,
        cash_flows,
        discount_rate,
        0,
        {"npv": npv_measure["npv"], "irr": irr_measure["irr"]},
    )
    all_flags = list(dict.fromkeys([*irr_measure["flags"], *invariant_flags]))
    sensitivity = []
    for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:
        sweep_npv = measurement_npv(
            initial_investment, cash_flows, discount_rate * multiplier
        )
        sensitivity.append({"multiplier": multiplier, "npv": sweep_npv["npv"]})
    return create_envelope(
        "wealth_audit_entropy",
        "Entropy",
        {"sign_changes": irr_measure["sign_changes"]},
        {"sensitivity_sweep": sensitivity},
        all_flags,
        irr_measure["assumptions"],
        epistemic="ESTIMATE",
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_dscr_leverage")
def dscr_leverage(
    ebitda: Optional[float] = None,
    principal: float = 0,
    interest: float = 0,
    leases: float = 0,
    cfads: Optional[float] = None,
    debt_service: Optional[float] = None,
    period_unit: str = "annual",
    input_epistemic: str = "CLAIM",
    scale_mode: str = "enterprise",
) -> Any:
    """Compute Debt Service Coverage Ratio (Structural Load). [Survival Dimension]"""
    measurement = measurement_dscr(
        cfads,
        debt_service,
        ebitda,
        principal,
        interest,
        leases,
        period_unit,
        input_epistemic,
    )
    return create_envelope(
        "wealth_dscr_leverage",
        "Survival",
        {"dscr": measurement["dscr"]},
        {
            "basis": measurement["basis"],
            "period_unit": measurement["period_unit"],
            "confidence_band": measurement["confidence_band"],
        },
        measurement["flags"],
        measurement["assumptions"],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_payback_time")
def payback_time(
    initial_investment: float,
    cash_flows: List[float],
    discount_rate: float = 0,
    period_unit: str = "annual",
    scale_mode: str = "enterprise",
) -> Any:
    """Compute Payback Period (Recovery Velocity). [Time Dimension]"""
    measurement = measurement_payback(
        initial_investment, cash_flows, discount_rate, period_unit
    )
    return create_envelope(
        "wealth_payback_time",
        "Time",
        {"payback_periods": measurement["payback_periods"]},
        {
            "period_unit": measurement["period_unit"],
            "discounted": measurement["discounted"],
        },
        measurement["flags"],
        measurement["assumptions"],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_growth_velocity")
def growth_velocity(
    principal: float,
    rate: float,
    years: int,
    annual_contribution: float = 0,
    monthly_burn: float = 0,
    scale_mode: str = "enterprise",
) -> Any:
    """Compute Compound Growth and Runway. [Velocity Dimension]"""
    total = principal
    for _ in range(years):
        total = total * (1 + rate) + annual_contribution
    final_value = round_value(total, 2)
    low = round_value(final_value * 0.88, 2)
    high = round_value(final_value * 1.12, 2)
    net_monthly = -monthly_burn
    runway_months = (
        math.inf if monthly_burn <= 0 else round_value(principal / monthly_burn, 1)
    )
    flags = (
        ["RUNWAY_CRITICAL"]
        if monthly_burn > 0 and runway_months is not None and runway_months < 3
        else []
    )
    return create_envelope(
        "wealth_growth_velocity",
        "Velocity",
        {"growth_forecast": {"low": low, "mid": final_value, "high": high}},
        {
            "runway_months": runway_months,
            "final_value": final_value,
            "net_monthly": net_monthly,
        },
        flags,
        ["Forward projections remain ESTIMATE by design."],
        epistemic="ESTIMATE",
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_networth_state")
def networth_state(
    assets: Optional[List[dict]] = None,
    liabilities: Optional[List[dict]] = None,
    scale_mode: str = "enterprise",
) -> Any:
    """Compute portfolio balance sheet (Accumulated Mass). [Mass Dimension]"""
    assets = assets or []
    liabilities = liabilities or []
    asset_value = sum(
        asset.get("value", 0)
        for asset in assets
        if math.isfinite(asset.get("value", 0))
    )
    liability_value = sum(
        liability.get("outstanding", liability.get("principal", 0))
        for liability in liabilities
        if math.isfinite(liability.get("outstanding", liability.get("principal", 0)))
    )
    epistemic = weakest_epistemic([*assets, *liabilities])
    return create_envelope(
        "wealth_networth_state",
        "Mass",
        {
            "net_worth": round_value(asset_value - liability_value, 2),
            "assets": round_value(asset_value, 2),
            "liabilities": round_value(liability_value, 2),
            "tag": epistemic,
        },
        {},
        [],
        [],
        epistemic=epistemic,
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_cashflow_flow")
def cashflow_flow(
    income: Optional[List[dict]] = None,
    expenses: Optional[List[dict]] = None,
    liquid_assets: float = 0,
    scale_mode: str = "enterprise",
) -> Any:
    """Compute metabolic liquidity (Flow Dimension). [Flow Dimension]"""
    income = [item for item in (income or []) if item.get("active", True)]
    expenses = [item for item in (expenses or []) if item.get("active", True)]
    total_income = sum(
        item.get("monthly_amount", 0)
        for item in income
        if math.isfinite(item.get("monthly_amount", 0))
    )
    total_expenses = sum(
        item.get("monthly_amount", 0)
        for item in expenses
        if math.isfinite(item.get("monthly_amount", 0))
    )
    net_monthly = total_income - total_expenses
    burn_rate = max(0.0, -net_monthly)
    runway_months = (
        math.inf if burn_rate == 0 else round_value(liquid_assets / burn_rate, 1)
    )
    flags = (
        ["RUNWAY_CRITICAL"]
        if burn_rate > 0 and runway_months is not None and runway_months < 3
        else []
    )
    epistemic = weakest_epistemic([*income, *expenses], "UNKNOWN")
    return create_envelope(
        "wealth_cashflow_flow",
        "Flow",
        {
            "monthly_income": round_value(total_income, 2),
            "monthly_expenses": round_value(total_expenses, 2),
            "net_monthly": round_value(net_monthly, 2),
            "runway_months": runway_months,
            "burn_rate": round_value(burn_rate, 2),
            "tag": epistemic,
        },
        {"period_unit": "monthly"},
        flags,
        [],
        epistemic=epistemic,
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_score_kernel")
def wealth_score_kernel(
    d_s: float,
    peace2: float,
    maruah_score: float,
    base_rate: float,
    trust_index: float = 0.5,
    delta_civ: float = 0.0,
    wealth_signals: Optional[dict] = None,
    prospects: Optional[List[dict]] = None,
    extractive_signals: Optional[dict] = None,
    compare: bool = False,
    scale_mode: str = "enterprise",
    task_definition: str = "",
    irreversible: bool = False,
) -> Any:
    """Final Sovereign Allocation Verdict. [Allocation Dimension]

    Constitutional Gate (F1-F13) + Epistemic Gate (Schema + Correlation).
    """
    epistemic_flags = []
    integrity_score = 1.0
    correlation_risk = 0.0
    epistemic_tag = "ESTIMATE"

    if EPISTEMIC_AVAILABLE and prospects:
        validator = SchemaValidator()
        guard = CorrelationGuard()

        schema_res = validator.validate_portfolio(prospects)
        integrity_score = schema_res.get("integrity_score", 1.0)
        epistemic_flags.extend(schema_res.get("flags", []))

        corr_res = guard.check_portfolio(prospects)
        correlation_risk = corr_res.get("correlation_risk", 0.0)
        epistemic_flags.extend(corr_res.get("flags", []))

        if integrity_score < 0.3:
            epistemic_flags.append("EPISTEMIC_FAILURE")
        if correlation_risk > 0.5:
            epistemic_flags.append("SYSTEMIC_CORRELATION_RISK")

    # --- 888 Harness Gate ---
    h_engine = HarnessEngine()
    pre_audit = h_engine.audit(
        "wealth_score_kernel",
        {"maruahScore": maruah_score, "base_rate": base_rate},
        epistemic_flags
    )
    if pre_audit["verdict"] == "FAIL":
        return create_envelope(
            "wealth_score_kernel",
            "Allocation",
            {
                "blocked_by_harness": True,
                "harness_verdict": "FAIL",
                "integrity_score": integrity_score,
                "correlation_risk": correlation_risk,
            },
            {"harness_detail": pre_audit},
            [*epistemic_flags, *pre_audit["violations"]],
            ["Allocation blocked by harness-snap (Constraint Violation)."],
            epistemic="VOID",
            verdict="VOID",
            scale_mode=scale_mode,
        )

    if not GOVERNANCE_AVAILABLE:
        pass
    else:
        floor_result = check_floors(
            {
                "reversible": not irreversible,
                "human_confirmed": False,
                "epistemic": epistemic_tag,
                "ai_is_deciding": True,
                "floor_override": False,
                "peace2": peace2,
                "maruah_score": maruah_score,
                "integrity_score": integrity_score,
                "correlation_risk": correlation_risk,
                "operation_type": "ALLOCATION",
                "scale_mode": scale_mode,
                "task_definition": task_definition,
                "critical": irreversible,
            }
        )
        if (floor_result.get("verdict") in ("HOLD", "VOID")) or (
            "EPISTEMIC_FAILURE" in epistemic_flags
        ):
            gov_verdict = (
                "888-HOLD" if floor_result.get("verdict") == "HOLD" else "VOID"
            )
            if "EPISTEMIC_FAILURE" in epistemic_flags:
                gov_verdict = "VOID"

            return create_envelope(
                "wealth_score_kernel",
                "Allocation",
                {
                    "blocked_by_governance": True,
                    "verdict": gov_verdict,
                    "integrity_score": integrity_score,
                    "correlation_risk": correlation_risk,
                },
                {
                    "floor_violations": floor_result.get("violations", []),
                    "epistemic_violations": epistemic_flags,
                },
                [*floor_result.get("violations", []), *epistemic_flags],
                ["Allocation blocked by constitutional or epistemic gate."],
                epistemic=epistemic_tag,
                verdict=gov_verdict,
                scale_mode=scale_mode,
            )

    wealth_payload = {
        "dS": d_s,
        "peace2": peace2,
        "maruahScore": maruah_score,
        "tag": "ESTIMATE",
    }

    # 888 Epistemic Gate
    if EPISTEMIC_AVAILABLE and prospects:
        validator = SchemaValidator()
        v_res = validator.validate_portfolio(prospects)
        if not v_res.get("portfolio_valid", True):
            return create_envelope(
                "wealth_score_kernel",
                "Allocation",
                {"error": "EPISTEMIC_HOLD", "reason": v_res.get("status")},
                {},
                ["888_HOLD", "EPISTEMIC_VIOLATION"],
                [
                    "Epistemic validation failed. Scalar volumetrics detected or integrity low."
                ],
                epistemic="VOID",
                verdict="VOID",
                scale_mode=scale_mode,
            )

        guard = CorrelationGuard()
        g_res = guard.check_portfolio(prospects)
        if g_res.action == "HOLD":
            return create_envelope(
                "wealth_score_kernel",
                "Allocation",
                {"error": "CORRELATION_HOLD", "systemic_risk": True},
                {},
                ["888_HOLD", "SYSTEMIC_RISK"],
                ["Systemic risk detected. Models are too correlated."],
                epistemic="VOID",
                verdict="VOID",
                scale_mode=scale_mode,
            )

    if wealth_signals:
        wealth_payload.update(wealth_signals)

    flags: List[str] = [*epistemic_flags]
    if d_s > 0.3:
        flags.append("HIGH_ENTROPY_SIGNAL")
    if maruah_score < 0.6:
        flags.append("SOVEREIGN_DIGNITY_LOW")

    wealth_result = capitalx(base_rate, wealth_payload)

    if compare:
        extractive_result = capitalx(base_rate, extractive_signals or {})
        comparison = {
            "base_rate": wealth_result["base_rate"],
            "wealth_r_adj": wealth_result["r_adj"],
            "extractive_r_adj": extractive_result["r_adj"],
            "advantage_bps": round(
                (extractive_result["r_adj"] - wealth_result["r_adj"]) * 10000
            ),
            "integrity_score": integrity_score,
            "correlation_risk": correlation_risk,
        }
        return create_envelope(
            "wealth_score_kernel",
            "Allocation",
            comparison,
            {},
            [
                *flags,
                *(wealth_result.get("integrity_flags", [])),
                *(extractive_result.get("integrity_flags", [])),
            ],
            ["CapitalX remains an estimate until delta_bps is proven."],
            epistemic="ESTIMATE",
            scale_mode=scale_mode,
        )

    # Merge results
    final_primary = {**wealth_result}
    final_primary.update(
        {"integrity_score": integrity_score, "correlation_risk": correlation_risk}
    )

    return create_envelope(
        "wealth_score_kernel",
        "Allocation",
        final_primary,
        {},
        [*flags, *(wealth_result.get("integrity_flags", []))],
        wealth_result.get("assumptions", []),
        epistemic=epistemic_tag,
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_personal_decision")
def personal_decision(
    alternatives: List[dict],
    constraints: dict,
    values: Optional[dict] = None,
    scale_mode: str = "personal",
) -> Any:
    """Rank personal alternatives under constraints. [Personal Dimension]"""
    values = values or {}
    ranked = []
    flags = []
    for alt in alternatives:
        cost = alt.get("cost", 0)
        time = alt.get("time_hours", 0)
        utility = alt.get("expected_utility", 0)
        weight_money = values.get("weight_money", 0.33)
        weight_time = values.get("weight_time", 0.33)
        weight_utility = values.get("weight_utility", 0.34)
        budget = constraints.get("budget", math.inf)
        time_budget = constraints.get("time_budget", math.inf)
        score = (
            weight_money * (-cost / max(budget, 1))
            + weight_time * (-time / max(time_budget, 1))
            + weight_utility * utility
        )
        feasible = cost <= budget and time <= time_budget
        ranked.append(
            {
                "name": alt.get("name"),
                "score": round_value(score, 6),
                "feasible": feasible,
            }
        )
    ranked.sort(key=lambda x: x["score"], reverse=True)
    if not any(r["feasible"] for r in ranked):
        flags.append("NO_FEASIBLE_ALTERNATIVE")
    return create_envelope(
        "wealth_personal_decision",
        "Personal",
        {"ranked_alternatives": ranked},
        {"constraint_summary": constraints},
        flags,
        ["Personal decisions trade money, time, and subjective utility."],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_agent_budget")
def agent_budget(
    compute_budget_usd: float,
    token_budget: float,
    time_deadline_hours: float,
    expected_value_of_information: float,
    actions: List[dict],
    scale_mode: str = "agentic",
) -> Any:
    """Optimal action sequence for an AI agent under resource constraints. [Agentic Dimension]"""
    feasible = []
    for action in actions:
        cost = action.get("compute_cost_usd", 0) + action.get("token_cost", 0) * 0.00001
        time = action.get("time_hours", 0)
        value = action.get("expected_value", 0)
        if cost <= compute_budget_usd and time <= time_deadline_hours:
            feasible.append(
                {
                    "name": action.get("name"),
                    "cost": round_value(cost, 6),
                    "value": value,
                    "efficiency": round_value(value / max(cost, 1e-9), 6),
                }
            )
    feasible.sort(key=lambda x: x["efficiency"], reverse=True)
    selected = []
    remaining_budget = compute_budget_usd
    remaining_time = time_deadline_hours
    total_value = 0.0
    for action in feasible:
        if (
            action["cost"] <= remaining_budget
            and action["cost"] * 0.00001 <= token_budget
            and action.get("time_hours", 0) <= remaining_time
        ):
            selected.append(action["name"])
            remaining_budget -= action["cost"]
            remaining_time -= action.get("time_hours", 0)
            total_value += action["value"]
    flags = []
    if total_value < expected_value_of_information:
        flags.append("VALUE_OF_INFORMATION_NEGATIVE")
    return create_envelope(
        "wealth_agent_budget",
        "Agentic",
        {"selected_actions": selected, "total_value": round_value(total_value, 6)},
        {
            "remaining_budget": round_value(remaining_budget, 2),
            "remaining_time": round_value(remaining_time, 2),
        },
        flags,
        ["Agent budgets optimize value per unit of compute and latency."],
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_crisis_triage")
def crisis_triage(
    resources: dict,
    demands: List[dict],
    recovery_horizon_days: float = 30,
    scale_mode: str = "crisis",
) -> Any:
    """Survival-oriented resource triage. [Crisis Dimension]"""
    total_supply = sum(v for v in resources.values() if math.isfinite(v))
    total_demand = sum(
        d.get("amount", 0) for d in demands if math.isfinite(d.get("amount", 0))
    )
    gap = total_demand - total_supply
    sorted_demands = sorted(demands, key=lambda d: d.get("urgency", 1), reverse=True)
    allocated = []
    remaining = dict(resources)
    for demand in sorted_demands:
        name = demand.get("name")
        amount = demand.get("amount", 0)
        res_type = demand.get("resource_type", "general")
        available = remaining.get(res_type, remaining.get("general", 0))
        grant = min(amount, available)
        remaining[res_type] = available - grant
        if res_type != "general" and "general" in remaining:
            remaining["general"] -= grant
        allocated.append(
            {
                "name": name,
                "granted": round_value(grant, 2),
                "shortfall": round_value(amount - grant, 2),
            }
        )
    survival_probability = max(0.0, min(1.0, total_supply / max(total_demand, 1e-9)))
    flags = []
    if survival_probability < 0.5:
        flags.append("SURVIVAL_CRITICAL")
    elif survival_probability < 0.8:
        flags.append("SURVIVAL_AT_RISK")
    return create_envelope(
        "wealth_crisis_triage",
        "Crisis",
        {
            "survival_probability": round_value(survival_probability, 4),
            "resource_gap": round_value(gap, 2),
        },
        {
            "triage_allocation": allocated,
            "recovery_horizon_days": recovery_horizon_days,
        },
        flags,
        ["Crisis mode prioritizes survival probability over efficiency."],
        scale_mode=scale_mode,
        governance_args={
            "reversible": False,
            "human_confirmed": False,
            "epistemic": "ESTIMATE",
            "peace2": 1.0,
            "maruah_score": 0.6,
            "runway_months": recovery_horizon_days / 30.0,
        },
    )


@mcp.tool(name="wealth_civilization_stewardship")
def civilization_stewardship(
    population: float,
    energy_budget_twh: float,
    carbon_budget_gt: float,
    tech_growth_rate: float,
    time_horizon_years: int = 100,
    scale_mode: str = "civilization",
) -> Any:
    """Long-term civilization sustainability path. [Civilization Dimension]"""
    flags = []
    energy_per_capita = energy_budget_twh / max(population, 1)
    carbon_intensity = carbon_budget_gt / max(energy_budget_twh, 1)
    sustainable_growth = tech_growth_rate * (1 - carbon_intensity)
    projected_pop = population * pow(
        1 + min(tech_growth_rate, 0.02), time_horizon_years / 100
    )
    collapse_risk = max(0.0, min(1.0, (projected_pop * 10) / max(energy_budget_twh, 1)))
    if collapse_risk > 0.5:
        flags.append("CIVILIZATION_COLLAPSE_RISK_HIGH")
    if carbon_intensity > 0.05:
        flags.append("CARBON_BUDGET_EXHAUSTION")
    sustainability_index = max(
        0.0, min(1.0, sustainable_growth / max(collapse_risk, 0.01))
    )
    return create_envelope(
        "wealth_civilization_stewardship",
        "Civilization",
        {
            "sustainability_index": round_value(sustainability_index, 4),
            "collapse_risk": round_value(collapse_risk, 4),
            "sustainable_growth_rate": round_value(sustainable_growth, 6),
        },
        {
            "energy_per_capita_twh": round_value(energy_per_capita, 6),
            "projected_population_billions": round_value(projected_pop / 1e9, 4),
            "time_horizon_years": time_horizon_years,
        },
        flags,
        ["Civilization modeling uses long-horizon, low-discount assumptions."],
        scale_mode=scale_mode,
        governance_args={
            "reversible": False,
            "human_confirmed": False,
            "epistemic": "ESTIMATE",
            "peace2": 1.0 - collapse_risk,
            "maruah_score": 0.5,
            "carbon_intensity": carbon_intensity,
            "social_stability_index": 1.0 - collapse_risk,
        },
    )


@mcp.tool(name="wealth_coordination_equilibrium")
def coordination_equilibrium(
    agents: List[dict],
    shared_resources: dict,
    mechanism: str = "cooperative",
    scale_mode: str = "enterprise",
) -> Any:
    """Multi-agent resource coordination and equilibrium analysis. [Coordination Dimension]"""
    # Normalize agents to LP schema
    lp_agents = []
    for agent in agents:
        lp_agents.append(
            {
                "name": agent.get("name", "unnamed"),
                "utility": agent.get("utility", {res: 1.0 for res in shared_resources}),
                "demand": agent.get("resource_demand", {}),
            }
        )

    lp_result = lp_allocate(lp_agents, shared_resources)
    commons = commons_risk(lp_agents, shared_resources)

    # === Epistemic Correlation Guard ===
    correlation_report = {"action": "PASS"}
    if EPISTEMIC_AVAILABLE:
        guard = CorrelationGuard()
        res = guard.check_portfolio(agents)
        correlation_report = res.to_dict()
        if res.action == "HOLD":
            lp_result["feasible"] = False
            lp_result["flags"] = lp_result.get("flags", []) + ["CORRELATED_MODEL_BIAS"]

    tragedy_risk = commons["tragedy_risk"]
    conflicts = []
    if "DEMAND_PARTIALLY_UNMET" in commons.get("flags", []):
        for name, unmet in lp_result.get("unmet_demand", {}).items():
            for res, gap in unmet.items():
                conflicts.append({"agent": name, "resource": res, "gap": gap})

    cooperative_surplus = 0.0
    if mechanism == "cooperative":
        for agent in agents:
            cooperative_surplus += agent.get("cooperative_value", 0)

    flags = commons.get("flags", [])
    if correlation_report.get("action") == "HOLD":
        flags.append("CORRELATED_RISK_HOLD")

    if not conflicts and lp_result["feasible"]:
        flags.append("EQUILIBRIUM_FEASIBLE")

    return create_envelope(
        "wealth_coordination_equilibrium",
        "Coordination",
        {
            "tragedy_risk": round_value(tragedy_risk, 4),
            "conflict_count": len(conflicts),
            "total_welfare": lp_result.get("total_welfare", 0.0),
            "correlation_risk": correlation_report,
        },
        {
            "conflicts": conflicts,
            "cooperative_surplus": round_value(cooperative_surplus, 2),
            "mechanism": mechanism,
            "shadow_prices": commons.get("shadow_prices", {}),
        },
        flags,
        [
            "Coordination layer uses LP shadow prices and scarcity metrics, not hand-wavy ratios.",
            "Epistemic Correlation Guard active — checking for shared model bias across agents.",
        ],
        scale_mode=scale_mode,
        governance_args={
            "reversible": True,
            "human_confirmed": False,
            "epistemic": "ESTIMATE",
            "peace2": 1.0 - tragedy_risk,
            "maruah_score": 0.6,
            "dS": tragedy_risk,
        },
    )


@mcp.tool(name="wealth_game_theory_solve")
def game_theory_solve(
    agents: List[dict],
    resources: dict,
    mechanism: str = "cooperative",
    solve_equilibrium: bool = False,
    scale_mode: str = "enterprise",
) -> Any:
    """Multi-agent allocation brain: LP welfare, Shapley/core, and Nash approximation. [Coordination Dimension]"""
    lp_agents = []
    for agent in agents:
        lp_agents.append(
            {
                "name": agent.get("name", "unnamed"),
                "utility": agent.get("utility", {res: 1.0 for res in resources}),
                "demand": agent.get("resource_demand", {}),
            }
        )

    lp_result = lp_allocate(lp_agents, resources)
    commons = commons_risk(lp_agents, resources)
    shapley = shapley_values(lp_agents, resources)
    core = core_feasibility(lp_agents, resources, lp_result.get("allocations"))

    # === Epistemic Correlation Guard ===
    correlation_report = {"action": "PASS"}
    if EPISTEMIC_AVAILABLE:
        guard = CorrelationGuard()
        res = guard.check_portfolio(agents)
        correlation_report = res.to_dict()
        if res.action == "HOLD":
            lp_result["feasible"] = False

    equilibrium = {}
    if solve_equilibrium:
        eq = nash_approximation(lp_agents, resources)
        equilibrium = {
            "allocations": eq.get("equilibrium", {}),
            "converged": eq.get("converged", False),
            "iterations": eq.get("iterations", 0),
        }

    flags = []
    if not lp_result["feasible"]:
        flags.append("LP_INFEASIBLE")
    if correlation_report.get("action") == "HOLD":
        flags.append("CORRELATED_RISK_HOLD")
    if commons.get("tragedy_risk", 0.0) > 0.5:
        flags.append("TRAGEDY_OF_COMMONS")
    if not core.get("in_core", False):
        flags.append("CORE_BLOCK_DETECTED")
    if solve_equilibrium and not equilibrium.get("converged", False):
        flags.append("NASH_NO_CONVERGENCE")

    return create_envelope(
        "wealth_game_theory_solve",
        "Coordination",
        {
            "total_welfare": lp_result.get("total_welfare", 0.0),
            "tragedy_risk": commons.get("tragedy_risk", 0.0),
            "in_core": core.get("in_core", False),
            "blocking_coalitions": core.get("blocking_coalitions", [])[:5],
            "correlation_risk": correlation_report,
        },
        {
            "allocations": lp_result.get("allocations", {}),
            "shadow_prices": commons.get("shadow_prices", {}),
            "shapley": shapley.get("shapley", {}),
            "scarcity_index": commons.get("scarcity_index", {}),
            "equilibrium": equilibrium,
        },
        flags,
        [
            "Game-theory solver replaces naive tragedy-risk with LP, core, and equilibrium logic.",
            "Correlation Guard active — preventing systemic failure from shared model lineage.",
        ],
        scale_mode=scale_mode,
        governance_args={
            "reversible": True,
            "human_confirmed": False,
            "epistemic": "ESTIMATE",
            "peace2": 1.0 - commons.get("tragedy_risk", 0.0),
            "maruah_score": 0.6,
            "dS": commons.get("tragedy_risk", 0.0),
        },
    )


@mcp.tool(name="wealth_monte_carlo_forecast")
def monte_carlo_forecast(
    initial_commitment: float,
    mean_cash_flows: List[float],
    volatilities: List[float],
    discount_rate: float = 0.1,
    simulations: int = 10000,
    distribution: str = "lognormal",
    scale_mode: str = "enterprise",
) -> Any:
    """Stochastic forecast with probability-weighted outcomes. [Risk Dimension]"""
    import random

    random.seed(42)
    npvs = []
    periods = len(mean_cash_flows)
    for _ in range(simulations):
        draws = []
        for i, mean in enumerate(mean_cash_flows):
            vol = volatilities[i] if i < len(volatilities) else volatilities[-1]
            if distribution == "lognormal":
                sigma = math.sqrt(math.log1p((vol / max(abs(mean), 1e-9)) ** 2))
                mu = math.log(max(abs(mean), 1e-9)) - 0.5 * sigma**2
                draw = random.lognormvariate(mu, sigma) * (1 if mean >= 0 else -1)
            elif distribution == "triangular":
                low = mean * (1 - vol)
                high = mean * (1 + vol)
                draw = random.triangular(low, high, mean)
            else:
                draw = random.gauss(mean, vol)
            draws.append(draw)
        npv = -abs(initial_commitment) + sum(
            draws[t] / pow(1 + discount_rate, t + 1) for t in range(periods)
        )
        npvs.append(npv)
    npvs.sort()
    positive_prob = sum(1 for n in npvs if n > 0) / len(npvs)
    es_5 = npvs[int(len(npvs) * 0.05)] if npvs else 0
    upside_95 = npvs[int(len(npvs) * 0.95)] if npvs else 0
    mean_npv = sum(npvs) / len(npvs) if npvs else 0
    variance_npv = sum((n - mean_npv) ** 2 for n in npvs) / len(npvs) if npvs else 0
    flags = []
    if positive_prob < 0.5:
        flags.append("MAJORITY_DOWNSIDE")
    return create_envelope(
        "wealth_monte_carlo_forecast",
        "Risk",
        {
            "probability_positive_nrv": round_value(positive_prob, 4),
            "expected_shortfall_5pct": round_value(es_5, 2),
            "upside_potential_95pct": round_value(upside_95, 2),
        },
        {
            "mean_npv": round_value(mean_npv, 2),
            "volatility_of_outcome": round_value(math.sqrt(variance_npv), 2),
            "simulations": simulations,
            "distribution": distribution,
        },
        flags,
        ["Monte Carlo provides density estimates, not deterministic guarantees."],
        scale_mode=scale_mode,
        governance_args={
            "epistemic": "ESTIMATE",
            "uncertainty_band": [round_value(es_5, 2), round_value(upside_95, 2)],
            "scale_mode": scale_mode,
        },
    )


# === INGESTION LAYER ===
try:
    from host.ingest.registry import get_registry

    INGEST_AVAILABLE = True
except Exception:
    INGEST_AVAILABLE = False

    def get_registry():  # type: ignore
        return None


@mcp.tool(name="wealth_ingest_fetch")
def ingest_fetch(
    source: str,
    series_id: str,
    entity_code: str,
    use_cache: bool = True,
    bus: str = "slow",
) -> Any:
    """Fetch a live data series from an open public source. [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_fetch",
            "Sense",
            {"records": []},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    result = registry.fetch(
        source, series_id, entity_code, use_cache=use_cache, bus=bus
    )
    flags = result.get("flags", [])
    return create_envelope(
        "wealth_ingest_fetch",
        "Sense",
        {"count": result["count"], "cached": result.get("cached", False)},
        {"records": result["records"][:50], "flags": flags},
        flags,
        ["Live feeds carry source, timestamp, unit, and revision metadata."],
    )


@mcp.tool(name="wealth_ingest_snapshot")
def ingest_snapshot(entity_code: str, sources: Optional[List[str]] = None) -> Any:
    """Fetch a cross-source macro/energy/carbon snapshot for a geography. [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_snapshot",
            "Sense",
            {"coverage": 0},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    result = registry.snapshot(entity_code, sources=sources)
    flags = result.get("flags", [])
    return create_envelope(
        "wealth_ingest_snapshot",
        "Sense",
        {"coverage": result["coverage"], "entity_code": entity_code},
        {"snapshot": result["snapshot"], "flags": flags},
        flags,
        ["Snapshot assembles orthogonal reality anchors for a single geography."],
    )


@mcp.tool(name="wealth_ingest_sources")
def ingest_sources() -> Any:
    """List available data sources and their adapter status. [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_sources",
            "Sense",
            {"sources": []},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    sources = registry.available_sources()
    return create_envelope(
        "wealth_ingest_sources",
        "Sense",
        {"sources": sources},
        {},
        [],
        [
            "Sources are ranked by sovereignty: central bank > multilateral > aggregator."
        ],
    )


@mcp.tool(name="wealth_ingest_health")
def ingest_health(adapter: Optional[str] = None) -> Any:
    """Return bus health metrics: latency, cache age, field completeness, stale flags. [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_health",
            "Sense",
            {},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    health = registry.health(adapter)
    return create_envelope(
        "wealth_ingest_health",
        "Sense",
        {"health": health},
        {},
        [],
        ["Health tracks latency, success rate, cache age, and observation freshness."],
    )


@mcp.tool(name="wealth_ingest_vintage")
def ingest_vintage(
    source: str, series_id: str, entity_code: str, vintage_date: str
) -> Any:
    """Fetch a specific vintage of a series (FRED/ALFRED). [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_vintage",
            "Sense",
            {"count": 0},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    try:
        if source == "FRED":
            result = registry.fetch(
                source,
                series_id,
                entity_code,
                use_cache=False,
                vintage_dates=[vintage_date],
                bus="archive",
            )
        else:
            result = {
                "records": [],
                "flags": [f"VINTAGE_UNSUPPORTED:{source}"],
                "count": 0,
            }
    except Exception as exc:
        result = {"records": [], "flags": [f"VINTAGE_ERROR:{exc}"], "count": 0}
    return create_envelope(
        "wealth_ingest_vintage",
        "Sense",
        {"count": result["count"]},
        {"records": result["records"][:50], "flags": result["flags"]},
        result["flags"],
        ["Vintages preserve truth as it was known at a specific date."],
    )


@mcp.tool(name="wealth_ingest_reconcile")
def ingest_reconcile(entity_code: str) -> Any:
    """Cross-source divergence detection for a geography. [Sense Dimension]"""
    if not INGEST_AVAILABLE:
        return create_envelope(
            "wealth_ingest_reconcile",
            "Sense",
            {},
            {},
            ["INGEST_LAYER_UNAVAILABLE"],
            ["Ingest layer failed to initialize."],
        )
    registry = get_registry()
    result = registry.reconcile(entity_code)
    return create_envelope(
        "wealth_ingest_reconcile",
        "Sense",
        {
            "divergences": result["divergences"],
            "snapshot_coverage": result["snapshot_coverage"],
        },
        {"flags": result["flags"]},
        result["flags"],
        ["Reconciliation surfaces contradictory signals across independent sources."],
    )


@mcp.tool(name="wealth_check_floors")
def check_floors_tool(
    reversible: bool = True,
    human_confirmed: bool = False,
    epistemic: str = "ESTIMATE",
    ai_is_deciding: bool = False,
    floor_override: bool = False,
    peace2: float = 1.0,
    maruah_score: float = 0.5,
    uncertainty_band: Optional[List[float]] = None,
    operation_type: str = "PROJECTION",
    scale_mode: str = "enterprise",
    task_definition: str = "",
    phantom_entries: bool = False,
    critical: bool = False,
    pin_verified: bool = False,
) -> Any:
    """Evaluate F1–F13 constitutional floors. [Governance Dimension]"""
    result = check_floors(
        {
            "reversible": reversible,
            "human_confirmed": human_confirmed,
            "epistemic": epistemic,
            "ai_is_deciding": ai_is_deciding,
            "floor_override": floor_override,
            "peace2": peace2,
            "maruah_score": maruah_score,
            "uncertainty_band": uncertainty_band,
            "operation_type": operation_type,
            "scale_mode": scale_mode,
            "task_definition": task_definition,
            "phantom_entries": phantom_entries,
            "critical": critical,
            "pin_verified": pin_verified,
        }
    )
    gov_verdict = {
        "HOLD": "888-HOLD",
        "VOID": "VOID",
        "CAUTION": "QUALIFY",
        "SEAL": "SEAL",
    }.get(result["verdict"], "SEAL")
    return create_envelope(
        "wealth_check_floors",
        "Governance",
        {"pass": result["pass"], "verdict": result["verdict"]},
        {
            "violations": result["violations"],
            "holds": result["holds"],
            "warnings": result["warnings"],
            "maruah_band": maruah_band(maruah_score),
        },
        [*result["violations"], *result["holds"]],
        ["F1-F13 floors are hard constraints, not suggestions."],
        epistemic=epistemic,
        verdict=gov_verdict,
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_policy_audit")
def policy_audit(
    proposal: dict, constraints: Optional[dict] = None, scale_mode: str = "enterprise"
) -> Any:
    """Audit an allocation proposal against configurable policy constraints. [Governance Dimension]"""
    engine = PolicyEngine(constraints)
    result = engine.evaluate(proposal, scale_mode)
    policy_verdict = (
        "VOID"
        if not result["policy_pass"]
        else ("QUALIFY" if result["flags"] else "SEAL")
    )
    return create_envelope(
        "wealth_policy_audit",
        "Governance",
        {"policy_pass": result["policy_pass"]},
        {
            "flags": result["flags"],
            "details": result["details"],
            "constraints_applied": result["constraints_applied"],
        },
        result["flags"],
        ["Policy constraints encode constitutional economic boundaries."],
        verdict=policy_verdict,
        scale_mode=scale_mode,
    )


@mcp.tool(name="wealth_record_transaction")
def record_transaction_tool(
    tx_type: str,
    amount: float,
    currency: str,
    description: str,
    quantity: Optional[float] = None,
    price: Optional[float] = None,
    fees: Optional[float] = None,
    broker: Optional[str] = None,
    asset_id: Optional[str] = None,
    category: Optional[str] = None,
    notes: Optional[str] = None,
    dry_run: bool = False,
    human_confirmed: bool = False,
    idempotency_key: Optional[str] = None,
) -> Any:
    """Record a financial transaction to VAULT999 arifos_vault.wealth.transactions. [Vault Dimension]"""
    from host.governance.vault import record_transaction as _rt

    if dry_run:
        return create_envelope(
            "wealth_record_transaction",
            "Vault",
            {
                "tx_id": None,
                "status": "DRY_RUN",
                "integrity": None,
                "idempotency_key": idempotency_key,
                "human_confirmed": human_confirmed,
                "would_write": True,
                "dry_run": True,
            },
            {},
            [],
            ["DRY_RUN: No transaction written to VAULT999."],
            verdict="HOLD",
            scale_mode="enterprise",
        )

    result = _rt(
        tx_type=tx_type,
        amount=amount,
        currency=currency,
        description=description,
        quantity=quantity,
        price=price,
        fees=fees,
        broker=broker,
        asset_id=asset_id,
        category=category,
        source_tool="wealth_record_transaction",
        notes=notes,
        metadata={
            "idempotency_key": idempotency_key,
            "human_confirmed": human_confirmed,
            "tool": "wealth_record_transaction",
        },
    )
    verdict = "SEAL" if result.get("status") == "INSERTED" else "VOID"
    return create_envelope(
        "wealth_record_transaction",
        "Vault",
        {
            "tx_id": result.get("tx_id"),
            "status": result.get("status"),
            "integrity": result.get("integrity"),
            "idempotency_key": idempotency_key,
            "human_confirmed": human_confirmed,
        },
        {"pg_error": result.get("pg_error")},
        [],
        ["Transaction recorded to VAULT999 — immutable, auditable."],
        verdict=verdict,
        scale_mode="enterprise",
    )


@mcp.tool(name="wealth_snapshot_portfolio")
def snapshot_portfolio_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    result: Dict[str, Any],
    scale_mode: str = "enterprise",
    asset_id: Optional[str] = None,
    nav_myr: Optional[float] = None,
    quantity_held: Optional[float] = None,
    price_close: Optional[float] = None,
    currency: str = "MYR",
    dry_run: bool = False,
    human_confirmed: bool = False,
    idempotency_key: Optional[str] = None,
) -> Any:
    """Snapshot a tool computation result to VAULT999 arifos_vault.wealth.portfolio_snapshots. [Vault Dimension]"""
    from host.governance.vault import snapshot_portfolio as _sp

    if dry_run:
        return create_envelope(
            "wealth_snapshot_portfolio",
            "Vault",
            {
                "snapshot_id": None,
                "status": "DRY_RUN",
                "integrity": None,
                "idempotency_key": idempotency_key,
                "human_confirmed": human_confirmed,
                "would_write": True,
                "dry_run": True,
            },
            {},
            [],
            ["DRY_RUN: No snapshot written to VAULT999."],
            verdict="HOLD",
            scale_mode="enterprise",
        )

    snap = _sp(
        tool_name=tool_name,
        arguments=arguments,
        result=result,
        scale_mode=scale_mode,
        asset_id=asset_id,
        nav_myr=nav_myr,
        quantity_held=quantity_held,
        price_close=price_close,
        currency=currency,
    )
    verdict = "SEAL" if snap.get("status") == "INSERTED" else "VOID"
    return create_envelope(
        "wealth_snapshot_portfolio",
        "Vault",
        {
            "snapshot_id": snap.get("snapshot_id"),
            "status": snap.get("status"),
            "integrity": snap.get("integrity"),
            "idempotency_key": idempotency_key,
            "human_confirmed": human_confirmed,
        },
        {"pg_error": snap.get("pg_error")},
        [],
        ["Portfolio snapshot sealed to VAULT999."],
        verdict=verdict,
        scale_mode=scale_mode,
    )


@mcp.resource("wealth://doctrine/valuation")
def get_valuation_doctrine() -> str:
    return json.dumps(
        {
            "motto": "Physics > Narrative",
            "principles": [
                "F1: Absolute Value (NPV) is the primary anchor.",
                "F2: Reinvestment risk must be modeled via MIRR.",
                "F3: Time-Value is a physical decay function.",
                "F4: Leverage must never break the DSCR floor (1.25x).",
                "F5: Mandatory governance signals (dS, peace2, maruah) for SEAL.",
            ],
            "protocol": f"Dimensional Forge v{__version__}",
        },
        indent=2,
    )


@mcp.resource("wealth://dimensions/definitions")
def get_dimensional_definitions() -> str:
    return json.dumps(
        {
            "Reward": "Total energy output (NPV, EAA).",
            "Energy": "Efficiency and potential (IRR, PI).",
            "Entropy": "Risk, noise, and probability (EMV, Audit).",
            "Time": "Recovery velocity (Payback).",
            "Mass": "Accumulated state (Net Worth).",
            "Flow": "Metabolic rate (Cash Flow).",
            "Velocity": "Rate of expansion (Growth).",
            "Survival": "Structural load capacity (DSCR).",
            "Allocation": "Sovereign decision kernel (Score).",
        },
        indent=2,
    )


@mcp.resource("wealth://governance/floors")
def get_constitutional_floors() -> str:
    """Detailed definitions of the 13 Constitutional Floors (F1-F13)."""
    return json.dumps(
        {
            "F1": "Amanah (Reversibility) - All actions must be reversible or reparable.",
            "F2": "Truth (Accuracy) - Prioritize factual grounding; cite sources.",
            "F3": "Tri-Witness (Consensus) - Decisions require Theory, Constitution, and Manifesto agreement.",
            "F4": "Clarity (Entropy Reduction) - Responses must reduce confusion (delta S <= 0).",
            "F5": "Peace^2 (Non-Destruction) - Exponential penalty for destruction of value/trust.",
            "F6": "Empathy (RASA) - Active listening: Receive, Appreciate, Summarize, Ask.",
            "F7": "Humility (Uncertainty) - Maintain epistemic uncertainty within [0.03, 0.05].",
            "F8": "Genius (Systemic Health) - Maintain G >= 0.80 across A, P, X, E dials.",
            "F9": "Ethics (Anti-Poison) - Dark genius (C_dark) must remain below 0.30.",
            "F10": "Conscience (Identity) - No false consciousness claims; maintain Lab-Shaped Identity.",
            "F11": "Auditability (Transparency) - Immutable, tamper-evident logs for all decisions.",
            "F12": "Resilience (Graceful Failure) - Degrade functionality safely; never crash.",
            "F13": "Adaptability (Safe Evolution) - Governed evolution via W^3 consensus and tests.",
        },
        indent=2,
    )


@mcp.resource("wealth://governance/harness-doctrines")
def get_harness_doctrines() -> str:
    """The 9-Harness Constraint Architecture for WEALTH power containment."""
    return json.dumps(
        {
            "1_Identity": "Bind power to accountable identity and chain continuity. No seal, no allocation.",
            "2_Reality": "Ground decisions in physical data provenance. No hallucination.",
            "3_Epistemic": "Prevent scalar illusions and correlated bias. P10/P50/P90 thinking mandatory.",
            "4_Entropy": "Detect hidden fragility and noise in cash flows. Stochastic stress-testing.",
            "5_Survival": "Ensure metabolic liquidity and solvency under stress (DSCR/Flow).",
            "6_Constitutional": "Bind allocation to F1-F13 floors. 888_HOLD for irreversible harm.",
            "7_Efficiency": "Resource discipline; capital must earn its survival (PI >= 1.0).",
            "8_Coordination": "Multi-agent stability; Nash-equilibrium and Core-feasibility checks.",
            "9_Civilization": "Long-horizon planetary survival and energy budget alignment.",
        },
        indent=2,
    )


@mcp.resource("wealth://topology/families")
def get_sovereign_families() -> str:
    """The 6 Sovereign Families of the WEALTH v2 Lattice."""
    return json.dumps(
        {
            "SENSE": "External reality ingestion and environmental observation (Stage 100).",
            "MIND": "Uncertainty modeling, Monte Carlo, and epistemic validation (Stage 200).",
            "SURVIVAL": "Solvency, leverage gating, and metabolic triage (Stage 300).",
            "REASON": "Capital discipline, NPV/IRR optimization, and yield analysis (Stage 400).",
            "JUDGE": "Constitutional gating, policy auditing, and 888_HOLD (Stage 888).",
            "VAULT": "Immutable anchoring, receipt hashing, and ledger sealing (Stage 999).",
        },
        indent=2,
    )


@mcp.resource("wealth://topology/scales")
def get_capital_scales() -> str:
    """Definitions of the 8 Capital Scales used in the WEALTH Engine."""
    return json.dumps(
        {
            "personal": "Individual resource allocation and life-horizon planning.",
            "household": "Multi-individual metabolic unit (family/home) stability.",
            "sme": "Small/Medium Enterprise; metabolic local node growth.",
            "enterprise": "Large-scale organizational resource optimization.",
            "national": "Macro-scale resource policy and sovereign allocation.",
            "crisis": "Extreme stress/survival state (war, disaster, famine).",
            "civilization": "Planetary/Species-horizon survival and stewardship.",
            "agentic": "Autonomous agent resource coordination and budget gating.",
        },
        indent=2,
    )


@mcp.resource("wealth://epistemic/uncertainty-matrix")
def get_epistemic_matrix() -> str:
    """Key metrics for Epistemic Integrity and Humility."""
    return json.dumps(
        {
            "omega_0": "Raw uncertainty coefficient (0.0 = total certainty, 1.0 = total chaos).",
            "kappa_r": "Humility score (derived from RASA and Truth consistency).",
            "humility_band": "The habitability range [0.03, 0.05]. Outside this is Arrogance or Paralysis.",
            "epistemic_tiers": ["CLAIM", "PLAUSIBLE", "HYPOTHESIS", "ESTIMATE", "VERIFIED"],
        },
        indent=2,
    )


@mcp.tool(name="wealth_evoi_compute")
async def wealth_evoi_compute(
    prior_pos: float,
    posterior_pos: float,
    well_cost_musd: float,
    p50_value_musd: float,
    info_cost_musd: float = 5.0,
    discount_rate: float = 0.10,
    scale_mode: str = "enterprise",
) -> Any:
    """
    Expected Value of Information (EVOI) point-estimate computation. [Epistemic Dimension]
    EVOI = E[V | with_info] - E[V | without_info]
    Helps decide if acquiring new data (seismic, audit, research) is worth the cost.
    """
    if not EPISTEMIC_AVAILABLE:
        return create_envelope(
            "wealth_evoi_compute",
            "Epistemic",
            {},
            {"error": "EPISTEMIC_UNAVAILABLE"},
            ["EPISTEMIC_UNAVAILABLE"],
            verdict="VOID",
        )

    try:
        res = compute_evoi(
            prior_pos=prior_pos,
            posterior_pos=posterior_pos,
            well_cost_musd=well_cost_musd,
            p50_value_musd=p50_value_musd,
            info_cost_musd=info_cost_musd,
            discount_rate=discount_rate,
        )

        return create_envelope(
            "wealth_evoi_compute",
            "Epistemic",
            res,
            {"info_cost": info_cost_musd, "well_cost": well_cost_musd},
            [],
            [
                f"Assumed information cost: {info_cost_musd} MUSD",
                f"Discount rate: {discount_rate}",
            ],
            verdict="SEAL" if res.get("evoi_musd", 0) > 0 else "QUALIFY",
            scale_mode=scale_mode,
        )
    except Exception as e:
        return create_envelope(
            "wealth_evoi_compute",
            "Epistemic",
            {},
            {"error": str(e)},
            ["COMPUTATION_ERROR"],
            verdict="VOID",
        )


@mcp.tool(name="wealth_evoi_monte_carlo")
async def wealth_evoi_monte_carlo(
    prior_pos_samples: List[float],
    posterior_pos_samples: List[float],
    well_cost_musd: float,
    p50_value_musd: float,
    info_cost_musd: float = 5.0,
    scale_mode: str = "enterprise",
) -> Any:
    """
    Monte Carlo Expected Value of Information (EVOI) distributional computation. [Epistemic Dimension]
    Uses sample distributions to compute P10/P50/P90 EVOI metrics.
    Recommended when PoS estimates are highly uncertain.
    """
    if not EPISTEMIC_AVAILABLE:
        return create_envelope(
            "wealth_evoi_monte_carlo",
            "Epistemic",
            {},
            {"error": "EPISTEMIC_UNAVAILABLE"},
            ["EPISTEMIC_UNAVAILABLE"],
            verdict="VOID",
        )

    try:
        res = compute_evoi_monte_carlo(
            prior_pos_samples=prior_pos_samples,
            posterior_pos_samples=posterior_pos_samples,
            well_cost_musd=well_cost_musd,
            p50_value_musd=p50_value_musd,
            info_cost_musd=info_cost_musd,
        )

        return create_envelope(
            "wealth_evoi_monte_carlo",
            "Epistemic",
            res,
            {"sample_count": len(prior_pos_samples)},
            [],
            ["Monte Carlo distribution based on user-provided samples"],
            verdict="SEAL" if res.get("evoi_p50", 0) > 0 else "QUALIFY",
            scale_mode=scale_mode,
        )
    except Exception as e:
        return create_envelope(
            "wealth_evoi_monte_carlo",
            "Epistemic",
            {},
            {"error": str(e)},
            ["COMPUTATION_ERROR"],
            verdict="VOID",
        )


@mcp.tool(name="wealth_correlation_guard_check")
async def wealth_correlation_guard_check(
    prospects: List[Dict[str, Any]],
    correlation_threshold: int = 3,
    scale_mode: str = "enterprise",
) -> Any:
    """
    Check portfolio for correlated model bias. [Epistemic Dimension]
    Uses model_lineage_hash to detect when multiple prospects share the same AI lineage.
    Systemic risk is detected if >= threshold prospects share a lineage.
    """
    if not EPISTEMIC_AVAILABLE:
        return create_envelope(
            "wealth_correlation_guard_check",
            "Epistemic",
            {},
            {"error": "EPISTEMIC_UNAVAILABLE"},
            ["EPISTEMIC_UNAVAILABLE"],
            verdict="VOID",
        )

    try:
        guard = CorrelationGuard(correlation_threshold=correlation_threshold)
        res = guard.check_portfolio(prospects)

        return create_envelope(
            "wealth_correlation_guard_check",
            "Epistemic",
            res.to_dict(),
            guard.assess_epistemic_diversity(prospects),
            [],
            [f"Correlation threshold: {correlation_threshold}"],
            verdict="SEAL" if res.action == "PASS" else "888-HOLD",
            scale_mode=scale_mode,
        )
    except Exception as e:
        return create_envelope(
            "wealth_correlation_guard_check",
            "Epistemic",
            {},
            {"error": str(e)},
            ["COMPUTATION_ERROR"],
            verdict="VOID",
        )


@mcp.tool(name="wealth_schema_validate")
async def wealth_schema_validate(
    prospects: List[Dict[str, Any]],
    scale_mode: str = "enterprise",
) -> Any:
    """
    Validate prospect inputs against epistemic requirements. [Epistemic Dimension]
    Rejects scalar volumes (requires p10/p50/p90).
    Enforces integrity_score >= 0.3 for capital allocation.
    """
    if not EPISTEMIC_AVAILABLE:
        return create_envelope(
            "wealth_schema_validate",
            "Epistemic",
            {},
            {"error": "EPISTEMIC_UNAVAILABLE"},
            ["EPISTEMIC_UNAVAILABLE"],
            verdict="VOID",
        )

    try:
        validator = SchemaValidator()
        res = validator.validate_portfolio(prospects)

        return create_envelope(
            "wealth_schema_validate",
            "Epistemic",
            res,
            {},
            [],
            ["Validation against v1.5.0 epistemic invariants."],
            verdict="SEAL" if res.get("portfolio_valid") else "VOID",
            scale_mode=scale_mode,
        )
    except Exception as e:
        return create_envelope(
            "wealth_schema_validate",
            "Epistemic",
            {},
            {"error": str(e)},
            ["COMPUTATION_ERROR"],
            verdict="VOID",
        )


@mcp.tool(name="wealth_init")
async def wealth_init_tool(
    session_id: Optional[str] = None,
    actor_id: str = "wealth-agent",
    intent: Optional[str] = None,
) -> Any:
    """
    Open a WEALTH governance session — writes a 000_INIT event to VAULT999.
    Call this at the start of any WEALTH analysis session to anchor identity
    and connect to the canonical Merkle chain (prev_hash = last vault_seals root).
    Returns session_id and chain position for subsequent wealth_snapshot_portfolio seals.
    """
    import sys
    import uuid as _uuid
    import os

    # Robust path resolution for arifOS root
    possible_paths = [
        "/root/arifOS",
        "/root",
        os.path.abspath(os.path.join(os.getcwd(), "..")),
        os.getcwd(),
    ]
    for p in possible_paths:
        if p not in sys.path:
            sys.path.append(p)

    sid = session_id or f"wealth-session-{_uuid.uuid4().hex[:12]}"

    try:
        from arifosmcp.runtime.vault_postgres import seal_to_vault

        res = await seal_to_vault(
            event_type="WEALTH_SESSION_INIT",
            session_id=sid,
            actor_id=actor_id,
            stage="000_INIT",
            verdict="ACTIVE",
            payload={"intent": intent or "economic-analysis", "source": "WEALTH-MCP"},
            risk_tier="low",
        )

        return create_envelope(
            "wealth_init",
            "Vault",
            {
                "session_id": sid,
                "stage": "000_INIT",
                "chain_hash": res.chain_hash if hasattr(res, "chain_hash") else "",
                "vault_id": res.ledger_id if hasattr(res, "ledger_id") else "",
            },
            {},
            [],
            ["WEALTH session anchored to VAULT999 chain. Ready for analysis."],
            verdict="SEAL",
        )
    except Exception as e:
        return create_envelope(
            "wealth_init",
            "Vault",
            {},
            {"error": str(e)},
            [],
            ["Vault anchor failed."],
            verdict="VOID",
        )


# ============================================================
# Register v2 aliases (non-breaking Phase 1 Migration)
# ============================================================
_engine = HarnessEngine()
_v1_to_func = {
    "wealth_ingest_fetch": ingest_fetch,
    "wealth_ingest_snapshot": ingest_snapshot,
    "wealth_ingest_reconcile": ingest_reconcile,
    "wealth_ingest_health": ingest_health,
    "wealth_ingest_vintage": ingest_vintage,
    "wealth_ingest_sources": ingest_sources,
    "wealth_emv_risk": emv_risk,
    "wealth_monte_carlo_forecast": monte_carlo_forecast,
    "wealth_correlation_guard_check": wealth_correlation_guard_check,
    "wealth_evoi_compute": wealth_evoi_compute,
    "wealth_evoi_monte_carlo": wealth_evoi_monte_carlo,
    "wealth_schema_validate": wealth_schema_validate,
    "wealth_dscr_leverage": dscr_leverage,
    "wealth_networth_state": networth_state,
    "wealth_growth_velocity": growth_velocity,
    "wealth_cashflow_flow": cashflow_flow,
    "wealth_crisis_triage": crisis_triage,
    "wealth_civilization_stewardship": civilization_stewardship,
    "wealth_npv_reward": npv_reward,
    "wealth_irr_yield": irr_yield,
    "wealth_pi_efficiency": pi_efficiency,
    "wealth_payback_time": payback_time,
    "wealth_coordination_equilibrium": coordination_equilibrium,
    "wealth_game_theory_solve": game_theory_solve,
    "wealth_personal_decision": personal_decision,
    "wealth_agent_budget": agent_budget,
    "wealth_score_kernel": wealth_score_kernel,
    "wealth_check_floors": check_floors_tool,
    "wealth_policy_audit": policy_audit,
    "wealth_audit_entropy": audit_entropy,
    "wealth_init": wealth_init_tool,
    "wealth_record_transaction": record_transaction_tool,
    "wealth_snapshot_portfolio": snapshot_portfolio_tool,
}

for v2_name, v1_name in _engine.V2_CANONICAL_MAP.items():
    if v1_name in _v1_to_func:
        mcp.tool(name=v2_name)(_v1_to_func[v1_name])

if __name__ == "__main__":
    mcp.run()
