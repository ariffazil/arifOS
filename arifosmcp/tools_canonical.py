"""
arifosmcp/tools_canonical.py — 13-Tool Canonical Implementation

Consolidates 33 P/T/V/E/M tools into 5 canonical engines.
Preserves all capability — zero capability loss.

Axis mapping:
  Constitutional Primordials (11): arifosmcp/runtime/tools.py — UNCHANGED
  Computation Engine 1: T_* physics/math → arifos_compute_physics
  Computation Engine 2: V_* + T_irr + T_growth → arifos_compute_finance
  Computation Engine 3: V_civ + M_game + M_cross → arifos_compute_civilization
  Oracle Bio: P_well_* + E_well_* → arifos_oracle_bio
  Oracle World: P_geox_* + P_wealth_* → arifos_oracle_world

EXTENSION HOOKS PATTERN (from wiki/pages/RECURSIVE_IMPROVEMENT_LOG.md):
  Before deployment: wire F9_TAQWA and F11_AUDIT into the tool dispatch layer.
  class Extension:
      async def before_execution(self, **kwargs):  # F9 TAQWA constitutional check
          pass
      async def after_execution(self, result, **kwargs):  # F11 AUDIT → VAULT999
          pass
  Maps cleanly to: before_execution → F9_TAQWA check; after_execution → F11_AUDIT logging.

DELTA BUNDLE SPEC (from wiki/pages/RECURSIVE_IMPROVEMENT_LOG.md):
  arif_mind_reason output must include: facts, scars, floor_scores, entropy, omega_0.
  See: tools/mind_reason.py _build_delta_bundle()

QUANTUM SABAR PROTOCOL (from wiki/pages/RECURSIVE_IMPROVEMENT_LOG.md):
  Byzantine continuity when W1/W3 unreachable. partition_mode: ONLINE | PURGATORY | DEAD.
  See: tools/sense_observe.py

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import math
import random
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL COMPUTE ENGINE 1 — PHYSICS
# ═══════════════════════════════════════════════════════════════════════════════


def arifos_compute_physics(
    mode: str,
    /,
    session_id: str | None = None,
    # petrophysics
    well_id: str | None = None,
    computation: str | None = None,
    params: dict[str, Any] | None = None,
    # stratigraphy
    wells: list[str] | None = None,
    section_id: str | None = None,
    # geometry
    horizons: list[dict[str, Any]] | None = None,
    # monte_carlo
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    iterations: int = 1000,
    # entropy_audit
    cashflows: list[float] | None = None,
    # growth_runway
    burn_rate: float | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Physics-grounded computation engine.
    Modes: petrophysics | stratigraphy_correlate | geometry_build |
           monte_carlo | entropy_audit | growth_runway
    """
    if mode == "petrophysics":
        phi = (params or {}).get("porosity", 0.0)
        sw = (params or {}).get("water_saturation", 1.0)
        h = (params or {}).get("thickness", 0.0)
        area = (params or {}).get("area", 0.0)
        bf = (params or {}).get("formation_volume_factor", 1.0)
        if computation == "porosity":
            value, unit = phi, "fraction"
        elif computation == "saturation":
            value, unit = sw, "fraction"
        elif computation == "volume":
            value = area * h * phi * (1 - sw) / bf if bf > 0 else 0
            unit = "bbl"
        else:
            value, unit = 0.0, "fraction"
        return {
            "agent": "T",
            "domain": "physics",
            "action": "petrophysics_compute",
            "canonical": "arifos_compute_physics[petrophysics]",
            "result": {
                "well_id": well_id,
                "computation": computation,
                "value": round(value, 4),
                "unit": unit,
            },
        }

    if mode == "stratigraphy_correlate":
        return {
            "agent": "T",
            "domain": "physics",
            "action": "stratigraphy_correlate",
            "canonical": "arifos_compute_physics[stratigraphy_correlate]",
            "result": {"wells": wells, "section_id": section_id, "correlation_map": {}},
        }

    if mode == "geometry_build":
        return {
            "agent": "T",
            "domain": "physics",
            "action": "geometry_build",
            "canonical": "arifos_compute_physics[geometry_build]",
            "result": {"horizons": horizons, "geometries": {}},
        }

    if mode == "monte_carlo":
        if not outcomes or not probabilities or len(outcomes) != len(probabilities):
            return {
                "agent": "T",
                "domain": "math",
                "action": "monte_carlo",
                "canonical": "arifos_compute_physics[monte_carlo]",
                "error": "outcomes and probabilities must be non-empty and matching",
            }
        results = []
        for _ in range(iterations):
            r = random.random()
            cumulative = 0.0
            for outcome, prob in zip(outcomes, probabilities, strict=False):
                cumulative += prob
                if r <= cumulative:
                    results.append(outcome)
                    break
        if not results:
            results = [sum(o * p for o, p in zip(outcomes, probabilities, strict=False))]
        mean_val = sum(results) / len(results)
        variance_val = sum((x - mean_val) ** 2 for x in results) / len(results)
        sorted_res = sorted(results)
        p10 = sorted_res[int(len(sorted_res) * 0.10)]
        p50 = sorted_res[int(len(sorted_res) * 0.50)]
        p90 = sorted_res[int(len(sorted_res) * 0.90)]
        return {
            "agent": "T",
            "domain": "math",
            "action": "monte_carlo",
            "canonical": "arifos_compute_physics[monte_carlo]",
            "result": {
                "iterations": iterations,
                "mean": round(mean_val, 4),
                "std_dev": round(math.sqrt(variance_val), 4),
                "distribution": {"p10": round(p10, 4), "p50": round(p50, 4), "p90": round(p90, 4)},
                "confidence_intervals": {"90": [round(p10, 4), round(p90, 4)]},
            },
        }

    if mode == "entropy_audit":
        if not cashflows:
            return {
                "agent": "T",
                "domain": "math",
                "action": "entropy_audit",
                "canonical": "arifos_compute_physics[entropy_audit]",
                "result": {"entropy_score": 0.0, "multiple_IRRs": False},
            }
        prev = 0
        changes = 0
        for cf in cashflows:
            if abs(cf) < 1e-9:
                continue
            sign = 1 if cf > 0 else -1
            if prev != 0 and sign != prev:
                changes += 1
            prev = sign
        signs = [1 if cf >= 0 else -1 for cf in cashflows]
        pos = sum(1 for s in signs if s > 0)
        neg = sum(1 for s in signs if s < 0)
        n = len(signs)
        p_pos = pos / n if n > 0 else 0.5
        p_neg = neg / n if n > 0 else 0.5
        entropy = 0.0
        if p_pos > 0:
            entropy -= p_pos * math.log2(p_pos)
        if p_neg > 0:
            entropy -= p_neg * math.log2(p_neg)
        norm_entropy = entropy / math.log2(2) if math.log2(2) > 0 else 0
        return {
            "agent": "T",
            "domain": "math",
            "action": "entropy_audit",
            "canonical": "arifos_compute_physics[entropy_audit]",
            "result": {"entropy_score": round(norm_entropy, 4), "multiple_IRRs": changes > 1},
        }

    if mode == "growth_runway":
        if not cashflows or len(cashflows) < 2:
            return {
                "agent": "T",
                "domain": "math",
                "action": "growth_runway_compute",
                "canonical": "arifos_compute_physics[growth_runway]",
                "result": {"cagr": 0.0, "runway_months": 0},
            }
        first, last = cashflows[0], cashflows[-1]
        n = len(cashflows) - 1
        cagr = (abs(last) / abs(first)) ** (1.0 / n) - 1 if first != 0 and n > 0 else 0.0
        runway_months = first / burn_rate if burn_rate and burn_rate > 0 and first > 0 else 0
        return {
            "agent": "T",
            "domain": "math",
            "action": "growth_runway_compute",
            "canonical": "arifos_compute_physics[growth_runway]",
            "result": {"cagr": round(cagr, 4), "runway_months": round(runway_months, 1)},
        }

    return {"error": f"Unknown mode: {mode}"}


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL COMPUTE ENGINE 2 — FINANCE
# ═══════════════════════════════════════════════════════════════════════════════


def arifos_compute_finance(
    mode: str,
    /,
    session_id: str | None = None,
    # NPV / PI
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    terminal_value: float = 0,
    # IRR / MIRR
    finance_rate: float = 0,
    reinvest_rate: float = 0,
    # EMV
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    # DSCR
    ebitda: float | None = None,
    debt_service: float | None = None,
    # Allocation
    candidates: list[dict[str, Any]] | None = None,
    constraints: dict[str, Any] | None = None,
    # Personal decision
    alternatives: list[dict[str, Any]] | None = None,
    # Budget optimize
    tasks: list[dict[str, Any]] | None = None,
    resources: dict[str, Any] | None = None,
    # Civilization
    current_state: dict[str, Any] | None = None,
    # Verification / Δm
    novelty: float = 0.5,
    proxy_distance: float = 0.5,
    verifier_scarcity: float = 0.5,
    latency_to_ground_truth: float = 0.5,
    model_opacity: float = 0.5,
    provenance_score: float = 0.5,
    reversibility_score: float = 0.5,
    executable_scope: float = 1.0,
    verifiable_scope: float = 1.0,
    liability_owner: str | None = None,
    junior_loop_status: str = "SAFE",
    human_capacity_score: float = 0.8,
    anti_hantu_fail: bool = False,
    sovereign_veto: bool = False,
    floors_passed: bool = True,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Financial + verification governance engine.
    Modes: npv | irr | mirr | emv | dscr | payback | profitability_index |
           allocation_rank | personal_decision_rank | budget_optimize |
           civilization_sustainability | wealth_audit_entropy | wealth_score_kernel |
           wealth_decision_packet | wealth_junior_loop | wealth_liability_route
    """
    # ── NPV ──────────────────────────────────────────────────────────────────
    if mode == "npv":
        from core.organs._5_wealth import calculate_npv as _calc_npv

        result = _calc_npv(initial_investment or 0, cash_flows or [], discount_rate, terminal_value)
        npv_val = result.get("npv", 0.0)
        return {
            "agent": "V",
            "domain": "economic",
            "action": "npv_evaluate",
            "canonical": "arifos_compute_finance[npv]",
            "result": {
                "npv": npv_val,
                "discount_rate": discount_rate,
                "initial_investment": initial_investment,
                "terminal_value": terminal_value,
                "criterion": "accept" if npv_val > 0 else "reject" if npv_val < 0 else "marginal",
                "flags": result.get("flags", []),
            },
        }

    # ── IRR ─────────────────────────────────────────────────────────────────
    if mode == "irr":
        from core.organs._5_wealth import calculate_irr as _calc_irr

        irr_result = _calc_irr(initial_investment or 0, cash_flows or [])
        irr_val = irr_result.get("irr")
        mirr_val = None
        if irr_val is not None and cash_flows and len(cash_flows) > 0:
            n = len(cash_flows)
            positive_total = sum(cf for cf in cash_flows if cf > 0)
            negative_total = abs(sum(cf for cf in cash_flows if cf < 0))
            if positive_total > 0 and negative_total > 0:
                f_rate = finance_rate if finance_rate else 0
                r_rate = reinvest_rate if reinvest_rate else irr_val
                mirr_num = positive_total * pow(1 + r_rate, n)
                mirr_den = abs(initial_investment or 0) * pow(1 + f_rate, n)
                if mirr_den > 0:
                    mirr_val = pow(mirr_num / mirr_den, 1.0 / n) - 1
        return {
            "agent": "T",
            "domain": "math",
            "action": "irr_compute",
            "canonical": "arifos_compute_finance[irr]",
            "result": {
                "irr": irr_val,
                "mirr": round(mirr_val, 6) if mirr_val is not None else None,
                "flags": irr_result.get("flags", []),
            },
        }

    # ── EMV ─────────────────────────────────────────────────────────────────
    if mode == "emv":
        if not outcomes or not probabilities or len(outcomes) != len(probabilities):
            return {"error": "outcomes and probabilities must have same length"}
        emv = sum(o * p for o, p in zip(outcomes, probabilities, strict=False))
        prob_sum = sum(probabilities)
        flags = [] if abs(prob_sum - 1.0) < 0.001 else ["PROBABILITY_MASS_INVALID"]
        return {
            "agent": "V",
            "domain": "economic",
            "action": "emv_evaluate",
            "canonical": "arifos_compute_finance[emv]",
            "result": {
                "emv": round(emv, 6),
                "distribution": {"outcomes": outcomes, "probabilities": probabilities},
                "prob_sum": round(prob_sum, 6),
                "flags": flags,
            },
        }

    # ── DSCR ─────────────────────────────────────────────────────────────────
    if mode == "dscr":
        from core.organs._5_wealth import calculate_dscr as _calc_dscr

        result = _calc_dscr(ebitda or 0, debt_service or 0)
        dscr_val = result.get("dscr")
        if dscr_val is None:
            return {
                "agent": "V",
                "domain": "economic",
                "action": "dscr_evaluate",
                "error": "debt_service cannot be zero",
            }
        return {
            "agent": "V",
            "domain": "economic",
            "action": "dscr_evaluate",
            "canonical": "arifos_compute_finance[dscr]",
            "result": {
                "dscr": dscr_val,
                "ebitda": ebitda,
                "debt_service": debt_service,
                "criterion": "adequate" if dscr_val >= 1.25 else "inadequate",
                "flags": result.get("flags", []),
            },
        }

    # ── PAYBACK ──────────────────────────────────────────────────────────────
    if mode == "payback":
        cumulative = 0.0
        periods = 0
        cumulative_series = []
        for i, cf in enumerate(cash_flows or []):
            cumulative += cf
            cumulative_series.append(cumulative)
            if cumulative >= (initial_investment or 0):
                periods = i + 1
                break
        disc_cumulative = 0.0
        disc_periods = None
        for i, cf in enumerate(cash_flows or []):
            disc_cumulative += cf / pow(1 + discount_rate, i) if discount_rate else cf
            if disc_cumulative >= (initial_investment or 0):
                disc_periods = i + 1
                break
        return {
            "agent": "V",
            "domain": "economic",
            "action": "payback_evaluate",
            "canonical": "arifos_compute_finance[payback]",
            "result": {
                "simple_payback_period": periods,
                "discounted_payback_period": disc_periods,
                "unit": "years",
                "cumulative_cash_flows": cumulative_series,
            },
        }

    # ── PROFITABILITY INDEX ─────────────────────────────────────────────────
    if mode == "profitability_index":
        from core.organs._5_wealth import calculate_npv as _calc_npv

        npv_result = _calc_npv(
            initial_investment or 0, cash_flows or [], discount_rate, terminal_value
        )
        npv_future = npv_result.get("npv", 0.0) if "npv_result" else 0.0
        pv_total = abs(initial_investment or 0) + npv_future
        pi = pv_total / abs(initial_investment or 0) if initial_investment else None
        return {
            "agent": "V",
            "domain": "economic",
            "action": "profitability_index",
            "canonical": "arifos_compute_finance[profitability_index]",
            "result": {
                "pi": round(pi, 6) if pi is not None else None,
                "npv": npv_future,
                "criterion": "accept" if pi and pi > 1 else "reject" if pi else "undefined",
            },
        }

    # ── ALLOCATION RANK ─────────────────────────────────────────────────────
    if mode == "allocation_rank":
        if not candidates:
            return {
                "agent": "V",
                "domain": "allocation",
                "action": "allocation_rank",
                "canonical": "arifos_compute_finance[allocation_rank]",
                "result": {"ranked": [], "constraints_satisfied": True},
            }
        scored = [(c.get("score", 0), c) for c in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [{"rank": i + 1, "candidate": c, "score": s} for i, (s, c) in enumerate(scored)]
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "allocation_rank",
            "canonical": "arifos_compute_finance[allocation_rank]",
            "result": {"ranked": ranked, "constraints_satisfied": True},
        }

    # ── PERSONAL DECISION RANK ───────────────────────────────────────────────
    if mode == "personal_decision_rank":
        if not alternatives:
            return {
                "agent": "V",
                "domain": "personal",
                "action": "personal_decision_rank",
                "canonical": "arifos_compute_finance[personal_decision_rank]",
                "result": {"ranked": []},
            }
        scored = [(a.get("score", 0), a) for a in alternatives]
        scored.sort(key=lambda x: x[0], reverse=True)
        ranked = [{"rank": i + 1, "alternative": a, "score": s} for i, (s, a) in enumerate(scored)]
        return {
            "agent": "V",
            "domain": "personal",
            "action": "personal_decision_rank",
            "canonical": "arifos_compute_finance[personal_decision_rank]",
            "result": {"ranked": ranked},
        }

    # ── BUDGET OPTIMIZE ─────────────────────────────────────────────────────
    if mode == "budget_optimize":
        if not tasks:
            return {
                "agent": "V",
                "domain": "allocation",
                "action": "agent_budget_optimize",
                "canonical": "arifos_compute_finance[budget_optimize]",
                "result": {"optimal_sequence": []},
            }
        budget = (resources or {}).get("budget", 0)
        scored = []
        for t in tasks:
            value = t.get("value", 0)
            cost = t.get("cost", 0)
            vp = value / cost if cost > 0 else 0
            scored.append((vp, value, t))
        scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
        selected = []
        spent = 0.0
        for _vp, _val, t in scored:
            c = t.get("cost", 0)
            if spent + c <= budget:
                selected.append(t)
                spent += c
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "agent_budget_optimize",
            "canonical": "arifos_compute_finance[budget_optimize]",
            "result": {"optimal_sequence": selected, "total_cost": spent, "budget": budget},
        }

    # ── CIVILIZATION SUSTAINABILITY ─────────────────────────────────────────
    if mode == "civilization_sustainability":
        cs = current_state or {}
        return {
            "agent": "V",
            "domain": "civilization",
            "action": "civilization_sustainability",
            "canonical": "arifos_compute_finance[civilization_sustainability]",
            "result": {
                "sustainability_index": round(cs.get("sustainability_index", 0.0), 4),
                "trajectory": cs.get("trajectory", "unknown"),
                "flags": cs.get("flags", []),
            },
        }

    # ── WEALTH AUDIT ENTROPY / Δm ───────────────────────────────────────────
    if mode == "wealth_audit_entropy":
        from skills.wealth.verify import wealth_measure_delta_m

        result = wealth_measure_delta_m(
            cashflows=cash_flows,
            novelty=novelty,
            proxy_distance=proxy_distance,
            verifier_scarcity=verifier_scarcity,
            latency_to_ground_truth=latency_to_ground_truth,
            model_opacity=model_opacity,
            provenance_score=provenance_score,
            reversibility_score=reversibility_score,
            executable_scope=executable_scope,
            verifiable_scope=verifiable_scope,
        )
        return {
            "agent": "V",
            "domain": "verification",
            "action": "wealth_audit_entropy",
            "canonical": "arifos_compute_finance[wealth_audit_entropy]",
            "result": result.to_dict(),
        }

    # ── WEALTH SCORE KERNEL ─────────────────────────────────────────────────
    if mode == "wealth_score_kernel":
        from skills.wealth.score_kernel import wealth_score_kernel

        # Derive svs from verifiable_scope / executable_scope
        safe_exec = max(executable_scope, 1e-9)
        svs = verifiable_scope / safe_exec
        delta_m = max(0.0, executable_scope - verifiable_scope)
        # Determine entropy band
        if delta_m >= 0.75 or svs < 0.25:
            band = "EXTREME"
        elif delta_m >= 0.50 or svs < 0.50:
            band = "HIGH"
        elif delta_m >= 0.25 or svs < 0.75:
            band = "MEDIUM"
        else:
            band = "LOW"
        result = wealth_score_kernel(
            reward_score=initial_investment,
            risk_score=discount_rate,
            npv_estimate=None,
            emv_estimate=None,
            verifiability_score=svs,
            delta_m=delta_m,
            entropy_band=band,
            floors_passed=floors_passed,
            liability_owner_present=(liability_owner is not None),
            liability_score=0.8 if liability_owner else 0.0,
            reversibility_score=reversibility_score,
            junior_loop_status=junior_loop_status,
            human_capacity_score=human_capacity_score,
            anti_hantu_fail=anti_hantu_fail,
            sovereign_veto=sovereign_veto,
        )
        return {
            "agent": "V",
            "domain": "verification",
            "action": "wealth_score_kernel",
            "canonical": "arifos_compute_finance[wealth_score_kernel]",
            "result": result.to_dict(),
        }

    # ── WEALTH JUNIOR LOOP ─────────────────────────────────────────────────
    if mode == "wealth_junior_loop":
        from skills.wealth.verify import wealth_assess_junior_loop

        result = wealth_assess_junior_loop(
            domain=(alternatives[0].get("domain") if alternatives else "unknown"),
            junior_task_share_removed=min(1.0, novelty),
            synthetic_training_available=(provenance_score > 0.5),
            current_senior_capacity=human_capacity_score,
        )
        return {
            "agent": "V",
            "domain": "verification",
            "action": "wealth_junior_loop",
            "canonical": "arifos_compute_finance[wealth_junior_loop]",
            "result": result.to_dict(),
        }

    # ── WEALTH LIABILITY ROUTE ───────────────────────────────────────────────
    if mode == "wealth_liability_route":
        from skills.wealth.verify import wealth_route_liability

        decision_id = alternatives[0].get("decision_id") if alternatives else "unknown"
        result = wealth_route_liability(
            decision_id=decision_id,
            liability_owner=liability_owner,
            owner_type="human" if liability_owner else None,
            max_loss_band=0.0,
            insurance_required=False,
            legal_review_required=False,
            deployment_class="LOW",
        )
        return {
            "agent": "V",
            "domain": "verification",
            "action": "wealth_liability_route",
            "canonical": "arifos_compute_finance[wealth_liability_route]",
            "result": result.to_dict(),
        }

    # ── WEALTH DECISION PACKET ───────────────────────────────────────────────
    if mode == "wealth_decision_packet":
        from skills.wealth.score_kernel import wealth_decision_packet

        title = (
            (alternatives[0].get("title") if alternatives else "Unnamed")
            if alternatives
            else "Unnamed"
        )
        safe_exec = max(executable_scope, 1e-9)
        svs = verifiable_scope / safe_exec
        delta_m = max(0.0, executable_scope - verifiable_scope)
        if delta_m >= 0.75 or svs < 0.25:
            band = "EXTREME"
        elif delta_m >= 0.50 or svs < 0.50:
            band = "HIGH"
        elif delta_m >= 0.25 or svs < 0.75:
            band = "MEDIUM"
        else:
            band = "LOW"
        result = wealth_decision_packet(
            title=title,
            domain=(
                (alternatives[0].get("domain") if alternatives else "trading")
                if alternatives
                else "trading"
            ),
            claims=(alternatives[0].get("claims", []) if alternatives else []),
            npv_estimate=None,
            emv_estimate=None,
            liability_owner=liability_owner,
            entropy_band=band,
            delta_m=delta_m,
            svs=svs,
            floors_passed=floors_passed,
            junior_loop_status=junior_loop_status,
            human_capacity_score=human_capacity_score,
            anti_hantu_fail=anti_hantu_fail,
            sovereign_veto=sovereign_veto,
        )
        return {
            "agent": "V",
            "domain": "verification",
            "action": "wealth_decision_packet",
            "canonical": "arifos_compute_finance[wealth_decision_packet]",
            "result": result,
        }

    return {"error": f"Unknown finance mode: {mode}"}


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL COMPUTE ENGINE 3 — CIVILIZATION
# ═══════════════════════════════════════════════════════════════════════════════


def arifos_compute_civilization(
    mode: str,
    /,
    session_id: str | None = None,
    # game_theory
    agents: list[dict[str, Any]] | None = None,
    payoff_matrix: dict[str, Any] | None = None,
    # cross_evidence
    scene_id: str | None = None,
    current_state: dict[str, Any] | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    Civilization-scale computation engine.
    Modes: sustainability_path | game_theory | cross_evidence_synthesize
    """
    if mode == "sustainability_path":
        cs = current_state or {}
        return {
            "agent": "V",
            "domain": "civilization",
            "action": "civilization_sustainability",
            "canonical": "arifos_compute_civilization[sustainability_path]",
            "result": {
                "sustainability_index": round(cs.get("sustainability_index", 0.0), 4),
                "trajectory": cs.get("trajectory", "unknown"),
                "path_years": cs.get("path_years", 10),
            },
        }

    if mode == "game_theory":
        if not agents or not payoff_matrix:
            return {
                "agent": "M",
                "domain": "meta",
                "action": "game_theory_solve",
                "canonical": "arifos_compute_civilization[game_theory]",
                "result": {"solution": None, "type": "unknown"},
            }
        # Shapley value approximation (simplified)
        n = len(agents)
        shapley = {}
        for agent in agents:
            aid = agent.get("id", "unknown")
            shapley[aid] = round(1.0 / n, 4)  # Equal contribution baseline
        return {
            "agent": "M",
            "domain": "meta",
            "action": "game_theory_solve",
            "canonical": "arifos_compute_civilization[game_theory]",
            "result": {
                "shapley_values": shapley,
                "n_agents": n,
                "solution_type": "shapley_approximation",
            },
        }

    if mode == "cross_evidence_synthesize":
        return {
            "agent": "M",
            "domain": "meta",
            "action": "cross_evidence_synthesize",
            "canonical": "arifos_compute_civilization[cross_evidence_synthesize]",
            "result": {"scene_id": scene_id, "synthesis": "pending", "evidence_count": 0},
        }

    return {"error": f"Unknown civilization mode: {mode}"}


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL ORACLE — BIO
# ═══════════════════════════════════════════════════════════════════════════════


def arifos_oracle_bio(
    mode: str,
    /,
    session_id: str | None = None,
    # snapshot_read / readiness_check / floor_scan
    ctx: Any | None = None,
    # log_update
    dimensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Biological telemetry oracle.
    Modes: snapshot_read | readiness_check | floor_scan | log_update
    """
    import datetime
    import json
    from pathlib import Path

    well_state = Path("/root/WELL/state.json")

    if mode == "snapshot_read":
        if not well_state.exists():
            return {"agent": "P", "action": "well_state_read", "error": "WELL state not found"}
        with open(well_state) as f:
            state = json.load(f)
        return {
            "agent": "P",
            "action": "well_state_read",
            "canonical": "arifos_oracle_bio[snapshot_read]",
            "result": {
                "well_score": state.get("well_score"),
                "metrics": state.get("metrics", {}),
                "floors_violated": state.get("floors_violated", []),
                "timestamp": state.get("timestamp"),
            },
        }

    if mode == "readiness_check":
        if not well_state.exists():
            return {"agent": "P", "action": "well_readiness_check", "error": "WELL state not found"}
        with open(well_state) as f:
            state = json.load(f)
        score = state.get("well_score", 0.5)
        readiness = "HIGH" if score >= 0.75 else "MODERATE" if score >= 0.5 else "LOW"
        return {
            "agent": "P",
            "action": "well_readiness_check",
            "canonical": "arifos_oracle_bio[readiness_check]",
            "result": {
                "readiness": readiness,
                "well_score": score,
                "verdict": (
                    "SEAL" if readiness == "HIGH" else "HOLD" if readiness == "LOW" else "PARTIAL"
                ),
            },
        }

    if mode == "floor_scan":
        if not well_state.exists():
            return {"agent": "P", "action": "well_floor_scan", "error": "WELL state not found"}
        with open(well_state) as f:
            state = json.load(f)
        return {
            "agent": "P",
            "action": "well_floor_scan",
            "canonical": "arifos_oracle_bio[floor_scan]",
            "result": {
                "floors": state.get("floors", {}),
                "floors_violated": state.get("floors_violated", []),
                "timestamp": state.get("timestamp"),
            },
        }

    if mode == "log_update":
        if not well_state.exists():
            return {"agent": "E", "action": "well_log", "error": "WELL state not found"}
        with open(well_state) as f:
            state = json.load(f)
        metrics = state.get("metrics", {})
        for key, value in (dimensions or {}).items():
            if key in ("sleep", "stress", "cognitive", "metabolic", "structural"):
                if isinstance(value, dict):
                    metrics[key] = {**metrics.get(key, {}), **value}
                else:
                    metrics[key] = value
            else:
                metrics[key] = value
        state["metrics"] = metrics
        state["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with open(well_state, "w") as f:
            json.dump(state, f, indent=2)
        return {
            "agent": "E",
            "action": "well_log",
            "canonical": "arifos_oracle_bio[log_update]",
            "result": {"updated_state": metrics},
        }

    return {"error": f"Unknown bio mode: {mode}"}


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL ORACLE — WORLD
# ═══════════════════════════════════════════════════════════════════════════════


async def arifos_oracle_world(
    mode: str,
    /,
    session_id: str | None = None,
    scene_type: str | None = None,
    path: str | None = None,
    query: str = "",
    domain: str | None = None,
    geography: str | None = None,
    source: str | None = None,
    series_id: str | None = None,
    vintage_date: str | None = None,
    ctx: Any | None = None,
) -> dict[str, Any]:
    """
    External world data oracle — bridges to GEOX (geoscience) and WEALTH (capital).
    Modes: geox_scene_load | geox_skills_query | macro_snapshot |
           series_fetch | series_vintage_fetch

    GEOX: https://geox.arif-fazil.com/mcp (public SSE, no auth needed)
    WEALTH: https://wealth.arif-fazil.com/mcp (session-based MCP StreamableHTTP)
    """
    import logging

    logger = logging.getLogger("arifosmcp.oracle_world")

    # ── GEOX modes ─────────────────────────────────────────────────────────────
    if mode == "geox_scene_load":
        try:
            from arifosmcp.runtime.geox_bridge import call_geox_tool

            result = await call_geox_tool(
                "geox_data_ingest_bundle",
                {"source_uri": path or "", "source_type": scene_type or "auto"},
            )
            return {
                "agent": "P",
                "action": "geox_scene_load",
                "canonical": "arifos_oracle_world[geox_scene_load]",
                "result": {
                    "scene_type": scene_type,
                    "path": path,
                    "scene_data": result,
                    "organ": "GEOX",
                    "status": "loaded",
                },
            }
        except Exception as e:
            logger.warning(f"geox_scene_load bridge failed: {e}")
            return {
                "agent": "P",
                "action": "geox_scene_load",
                "canonical": "arifos_oracle_world[geox_scene_load]",
                "result": {"scene_type": scene_type, "path": path, "scene_data": None},
                "error": str(e),
            }

    if mode == "geox_skills_query":
        try:
            from arifosmcp.runtime.geox_bridge import call_geox_tool

            result = await call_geox_tool("geox_list_skills", {"query": query, "domain": domain})
            skills = result if isinstance(result, list) else result.get("skills", [])
            return {
                "agent": "P",
                "action": "geox_skills_query",
                "canonical": "arifos_oracle_world[geox_skills_query]",
                "result": {"query": query, "domain": domain, "skills": skills},
            }
        except Exception as e:
            logger.warning(f"geox_skills_query bridge failed: {e}")
            return {
                "agent": "P",
                "action": "geox_skills_query",
                "canonical": "arifos_oracle_world[geox_skills_query]",
                "result": {"query": query, "domain": domain, "skills": []},
                "error": str(e),
            }

    # ── WEALTH modes ───────────────────────────────────────────────────────────
    if mode in ("macro_snapshot", "series_fetch", "series_vintage_fetch"):
        return {
            "agent": "P",
            "action": f"wealth_{mode}",
            "canonical": f"arifos_oracle_world[{mode}]",
            "result": {
                "mode": mode,
                "geography": geography,
                "source": source,
                "series_id": series_id,
                "vintage_date": vintage_date,
                "organ": "WEALTH",
                "status": "stub_pending_wealth_bridge_live",
            },
        }

    return {"error": f"Unknown world mode: {mode}"}


# ═══════════════════════════════════════════════════════════════════════════════
# ALIAS REGISTRY — Maps old tool names to canonical (mode, **kwargs)
# Used by mcp_tools.py shim layer
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_ALIAS_MAP: dict[str, tuple[str, str, dict]] = {
    # T_* → arifos_compute_physics
    "T_petrophysics_compute": ("arifos_compute_physics", "petrophysics", {}),
    "T_stratigraphy_correlate": ("arifos_compute_physics", "stratigraphy_correlate", {}),
    "T_geometry_build": ("arifos_compute_physics", "geometry_build", {}),
    "T_math_monte_carlo": ("arifos_compute_physics", "monte_carlo", {}),
    "T_math_entropy_audit": ("arifos_compute_physics", "entropy_audit", {}),
    "T_growth_runway_compute": ("arifos_compute_physics", "growth_runway", {}),
    # T_irr → arifos_compute_finance (IRR is finance)
    "T_math_irr_compute": ("arifos_compute_finance", "irr", {}),
    # V_* → arifos_compute_finance
    "V_npv_evaluate": ("arifos_compute_finance", "npv", {}),
    "V_emv_evaluate": ("arifos_compute_finance", "emv", {}),
    "V_dscr_evaluate": ("arifos_compute_finance", "dscr", {}),
    "V_profitability_index": ("arifos_compute_finance", "profitability_index", {}),
    "V_payback_evaluate": ("arifos_compute_finance", "payback", {}),
    "V_allocation_rank": ("arifos_compute_finance", "allocation_rank", {}),
    "V_personal_decision_rank": ("arifos_compute_finance", "personal_decision_rank", {}),
    "V_agent_budget_optimize": ("arifos_compute_finance", "budget_optimize", {}),
    "V_civilization_sustainability": ("arifos_compute_finance", "civilization_sustainability", {}),
    # V_civ also has a civilization route
    # M_* → arifos_compute_civilization
    "M_game_theory_solve": ("arifos_compute_civilization", "game_theory", {}),
    "M_cross_evidence_synthesize": ("arifos_compute_civilization", "cross_evidence_synthesize", {}),
    # P_well_* + E_well_* → arifos_oracle_bio
    "P_well_state_read": ("arifos_oracle_bio", "snapshot_read", {}),
    "P_well_readiness_check": ("arifos_oracle_bio", "readiness_check", {}),
    "P_well_floor_scan": ("arifos_oracle_bio", "floor_scan", {}),
    "E_well_log": ("arifos_oracle_bio", "log_update", {}),
    "E_well_anchor": ("arifos_oracle_bio", "log_update", {}),  # anchor uses same well state
    # P_geox_* + P_wealth_* → arifos_oracle_world
    "P_geox_scene_load": ("arifos_oracle_world", "geox_scene_load", {}),
    "P_geox_skills_query": ("arifos_oracle_world", "geox_skills_query", {}),
    "P_wealth_snapshot_fetch": ("arifos_oracle_world", "macro_snapshot", {}),
    "P_wealth_series_fetch": ("arifos_oracle_world", "series_fetch", {}),
    "P_wealth_vintage_fetch": ("arifos_oracle_world", "series_vintage_fetch", {}),
    # M_* meta → stays as-is (skill discovery, metabolic monitor don't fit canonical)
}


def resolve_alias(tool_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Route an old tool name to its canonical implementation."""
    import logging

    logger = logging.getLogger("arifos.canonical")
    if tool_name not in TOOL_ALIAS_MAP:
        return {"error": f"No canonical alias for: {tool_name}"}
    canonical_fn, mode, _ = TOOL_ALIAS_MAP[tool_name]
    fn = globals().get(canonical_fn)
    if fn is None:
        return {"error": f"Canonical function not found: {canonical_fn}"}
    logger.debug(f"ALIAS_RESOLVE: {tool_name} → {canonical_fn}[{mode}]")
    kwargs.pop("mode", None)
    return fn(mode, **kwargs)
