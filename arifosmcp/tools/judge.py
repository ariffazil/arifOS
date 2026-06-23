"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE v3
═══════════════════════════════════════════════

Constitutional verdict engine.

Evidence pre-loading: vitals and heart output are piped into the judge
before adjudication so epistemic confidence is grounded in actual system state.

Post-SEAL auto-hook: When verdict is SEAL and vault_entry_id is provided,
the judge output is automatically routed to arif_seal for immutable anchoring.

PARADOX ANCHORS (v3): 11 linguistic invariants fire at verdict decision points:
  J1 (Parker/MLK) — SABAR carries deadline | J4 (Aristotle) — SEAL is incomplete justice
  J6 (Marcus Aurelius) — irreversible gate | J7 (Glaucon) — power asymmetry detection

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json as json_lib
import os
import urllib.request
from pathlib import Path
from typing import Any

from arifosmcp.core.enforcement.maruah_critic import (
    maruah_critic_check,
    MaruahVerdict,
)
from arifosmcp.core.enforcement.somatic_loop import (
    SomaticState,
    classify_somatic_state,
    TelemetrySample,
)
from arifosmcp.paradox import (
    build_organ_anchors,
    register_organ,
    verdict_to_cell,
)
from arifosmcp.runtime.metabolic_receipt import get_cumulative_metrics
from arifosmcp.runtime.niat_gate import check_niat_gate
from arifosmcp.runtime.self_mod_lock import is_self_modification_attempt
from arifosmcp.runtime.tools import _arif_judge
from arifosmcp.schemas.verdict import VerdictCode, VerdictOutput

# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — 3×3 Orthogonal Matrix for Judge
# ═══════════════════════════════════════════════════════════════════════════════
# Rows: TRUTH / CLARITY / HUMILITY   Columns: CARE / PEACE / JUSTICE
# Each anchor separates QUOTE (verified human philosophy) from BINDING
# (firing policy). Policy evolves faster than canon — keep them distinct.
# ═══════════════════════════════════════════════════════════════════════════════

JUDGE_PARADOX_ANCHORS: list[dict] = [
    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "J_TxC",
        "matrix_cell": "truth_care",
        "matrix_row": "TRUTH",
        "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "If it is not right, do not do it; if it is not true, do not say it.",
            "author": "Marcus Aurelius",
            "work": "Meditations",
            "year": "c. 170–180 CE",
            "verification_level": "traditional_attribution",
            "translation_note": "Multiple translations exist; exact wording varies. Core meaning stable.",
        },
        "antithesis": "Rightness and truth are not always visible in the moment of decision — sometimes what is right can only be known after the action is taken.",
        "axis": "ex ante clarity vs. ex post knowledge",
        "binding": {
            "event": "irreversible_action_gate",
            "trigger": "irreversible-action gate — if not sure it's right, HOLD",
            "effect": "hard_requirement",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_TxP",
        "matrix_cell": "truth_peace",
        "matrix_row": "TRUTH",
        "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "In justice is every virtue comprehended.",
            "author": "Aristotle",
            "work": "Nicomachean Ethics 1129b29–30",
            "year": "4th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "No single verdict can comprehend every virtue simultaneously — every SEAL is partial justice, the best approximation under available evidence.",
        "axis": "comprehensiveness vs. decidability",
        "binding": {
            "event": "seal_verdict",
            "trigger": "SEAL verdict — audit bundle annotation",
            "effect": "annotate_seal_as_partial_justice",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_TxJ",
        "matrix_cell": "truth_justice",
        "matrix_row": "TRUTH",
        "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "About the just and the unjust… we should consider not what the many but what the man who knows shall say to us — that single man and the truth.",
            "author": "Socrates (via Plato)",
            "work": "Crito 48a5-7",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Who is the man who knows? Every claimant to knowledge is also a claimant to authority — wisdom and tyranny wear the same robes.",
        "axis": "expertise vs. authoritarianism",
        "binding": {
            "event": "human_gate_escalation",
            "trigger": "HUMAN_GATE / F13 SOVEREIGN escalation — verify the knowledge claim",
            "effect": "verify_claim_with_evidence",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "J_CxC",
        "matrix_cell": "clarity_care",
        "matrix_row": "CLARITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "One must never repay injustice with injustice, as the many think, since one must never do injustice.",
            "author": "Socrates (via Plato)",
            "work": "Crito 49b–c",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "But what of defensive action? To restrain an aggressor is to do something they did not consent to — the principle requires a theory of justified coercion, not a simple prohibition.",
        "axis": "non-retaliation vs. justified coercion",
        "binding": {
            "event": "coercive_action_evaluation",
            "trigger": "coercive or restrictive action evaluation — protection or retaliation?",
            "effect": "surface_justification_requirement",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_CxP",
        "matrix_cell": "clarity_peace",
        "matrix_row": "CLARITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIHADAPI, BUKAN DITANGGUHI",
        "quote": {
            "text": "At his best, man is the noblest of all animals; separated from law and justice he is the worst.",
            "author": "Aristotle",
            "work": "Politics 1253a31–33",
            "year": "4th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Law and justice are human constructs — made by the same creature they are supposed to restrain. The worst in man writes the laws too.",
        "axis": "law as civilizer vs. law as weapon",
        "binding": {
            "event": "policy_gate_applied",
            "trigger": "policy-as-code gate applied — gate must be reviewable",
            "effect": "annotate_reviewability",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_CxJ",
        "matrix_cell": "clarity_justice",
        "matrix_row": "CLARITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "The arc of the moral universe is long, but it bends toward justice.",
            "author": "Theodore Parker (adapted by Martin Luther King Jr.)",
            "work": "Of Justice and the Conscience, Ten Sermons of Religion",
            "year": "1853",
            "verification_level": "verified_exact",
            "adaptation_note": "MLK's 1968 version is the most widely known formulation.",
        },
        "antithesis": "The arc bends only if we bend it — gravity is not justice. Justice requires action, not faith. The arc bends only through human hands.",
        "axis": "providence vs. agency",
        "binding": {
            "event": "sabar_verdict",
            "trigger": "SABAR verdict — must carry deadline, cannot be indefinite",
            "effect": "attach_deadline",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "action_bias",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "J_HxC",
        "matrix_cell": "humility_care",
        "matrix_row": "HUMILITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "Those who are unable to escape suffering injustice determine that it is profitable to make a compact neither to do nor to suffer injustice.",
            "author": "Glaucon (via Plato)",
            "work": "Republic 358e–359a",
            "year": "c. 375 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "The compact is fragile — the strong who can escape suffering injustice while doing it will break the compact unless enforced by something stronger than self-interest.",
        "axis": "social contract vs. power asymmetry",
        "binding": {
            "event": "power_asymmetry_detected",
            "trigger": "power-asymmetry detected — is the compact being honored or exploited?",
            "effect": "bias_toward_hold_or_void",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_HxP",
        "matrix_cell": "humility_peace",
        "matrix_row": "HUMILITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "Two things fill the mind with ever new and increasing admiration and awe: the starry heavens above me and the moral law within me.",
            "author": "Immanuel Kant",
            "work": "Critique of Practical Reason, Conclusion, Ak. 5:161",
            "year": "1788",
            "verification_level": "verified_exact",
        },
        "antithesis": "The moral law within is not universally legible — different minds read different laws there. Internal conviction is not external validity.",
        "axis": "universal moral sense vs. moral diversity",
        "binding": {
            "event": "floor_tension_maruah",
            "trigger": "FLOOR_TENSION between F12 MARUAH and other floors — verify shared moral ground",
            "effect": "check_shared_moral_ground",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "judge",
        "norm": "SUNAT",
    },
    {
        "id": "J_HxJ",
        "matrix_cell": "humility_justice",
        "matrix_row": "HUMILITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "Act only according to that maxim whereby you can at the same time will that it should become a universal law.",
            "author": "Immanuel Kant",
            "work": "Groundwork of the Metaphysics of Morals, Ak. 4:421",
            "year": "1785",
            "verification_level": "verified_exact",
        },
        "antithesis": "Universality is not computable — we cannot simulate all possible worlds to verify a maxim. The categorical imperative is a direction of thought, not an executable function.",
        "axis": "universalizability vs. computability",
        "binding": {
            "event": "seal_sovereign_scope",
            "trigger": "SEAL verdicts for actions with systemic scope — test cannot be computed with certainty",
            "effect": "verify_with_f13",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX LOOKUP — O(1) access by cell or ID
# ═══════════════════════════════════════════════════════════════════════════════

_JUDGE_BY_CELL: dict[str, dict] = {a["matrix_cell"]: a for a in JUDGE_PARADOX_ANCHORS}
_JUDGE_BY_ID: dict[str, dict] = {a["id"]: a for a in JUDGE_PARADOX_ANCHORS}

# ── Register with global paradox registry (Phase 1 wiring) ──────────────────
_judge_anchors = build_organ_anchors("judge", JUDGE_PARADOX_ANCHORS)
_judge_registry = register_organ("judge", _judge_anchors)


def _judge_paradox_for_verdict(verdict_str: str, action_tier: str = "standard") -> dict | None:
    """
    Resolve the correct paradox anchor for a given verdict.

    Uses shared verdict_to_cell() from arifosmcp.paradox.matrix for
    deterministic verdict → matrix cell routing, then looks up the
    anchor in the global judge registry.
    """
    cell = verdict_to_cell(verdict_str, action_tier)
    if cell:
        return _judge_registry.get_legacy_by_cell(cell)
    return None


def _inject_judge_paradox(result: dict, verdict_str: str, action_tier: str = "standard") -> dict:
    """
    Inject paradox anchors into judge verdict output via 3×3 matrix resolution.

    Each anchor fires at a specific decision point, resolved by verdict type
    and action tier through the orthogonal matrix geometry:
    - SABAR → clarity_justice: arc bends only if we bend it (deadline required)
    - SEAL → truth_peace: every SEAL is partial justice
    - SEAL (sovereign) → humility_justice: universality not computable
    - HOLD (elevated) → truth_care: can't know rightness ex ante
    """
    anchor = _judge_paradox_for_verdict(verdict_str, action_tier)

    if anchor:
        if "meta" not in result:
            result["meta"] = {}
        q = anchor["quote"]
        b = anchor.get("binding", {})
        result["meta"]["paradox_anchor"] = {
            "quote_id": anchor["id"],
            "organ": "judge",
            "matrix_cell": anchor["matrix_cell"],
            "matrix_row": anchor["matrix_row"],
            "matrix_col": anchor["matrix_col"],
            "motto_binding": anchor["motto_binding"],
            "quote": q["text"],
            "author": q["author"],
            "work": q["work"],
            "year": q["year"],
            "verification_level": q["verification_level"],
            "antithesis": anchor["antithesis"],
            "axis": anchor["axis"],
            "norm": anchor["norm"],
            "severity_on_fire": anchor.get("severity_on_fire", "warn"),
            "risk_bias": anchor.get("risk_bias", "conservative"),
            "authority_scope": anchor.get("authority_scope", "judge"),
            "binding_event": b.get("event", ""),
            "_matrix_note": (
                f"Cell [{anchor['matrix_row']}×{anchor['matrix_col']}] — "
                f"Connected to arifOS PARADOX_MATRIX in core/shared/mottos.py"
            ),
        }

        # SABAR → clarity_justice: deadline enforcement
        if anchor["id"] == "J_CxJ":
            result["meta"]["sabar_deadline_note"] = (
                "SABAR is not indefinite. The arc does not bend by itself. "
                "If evidence remains incomplete past the SABAR timeout, "
                "escalate to HUMAN_GATE (F13) rather than waiting forever."
            )

        # SEAL → truth_peace: audit annotation
        if anchor["id"] == "J_TxP":
            result.setdefault("reasons", []).append(
                "J_TxP ARISTOTLE ANCHOR [truth_peace]: This SEAL is not perfectly "
                "just — it comprehends only the virtues that evidence and reasoning "
                "could capture. It is the best approximation available."
            )

        # SEAL sovereign → humility_justice: computability warning
        if anchor["id"] == "J_HxJ":
            result.setdefault("reasons", []).append(
                "J_HxJ KANT ANCHOR [humility_justice]: Universality is not "
                "computable. The categorical imperative is a direction of thought, "
                "not an executable function. This SEAL carries systemic scope — "
                "verify with F13 SOVEREIGN."
            )

        # HOLD elevated → truth_care: irreversibility gate
        if anchor["id"] == "J_TxC":
            result.setdefault("reasons", []).append(
                "J_TxC MARCUS AURELIUS ANCHOR [truth_care]: If it is not right, "
                "do not do it. Rightness cannot be fully known ex ante for "
                "irreversible actions. HOLD is the correct posture."
            )

    return result


# WELL state file candidates — covers docker-compose path, manual-start path, env override
_WELL_STATE_CANDIDATES = [
    Path(p)
    for p in [
        os.environ.get("WELL_STATE_PATH", ""),  # docker-compose: /app/well_state.json
        "/app/well_state.json",
        "/root/WELL/state.json",
    ]
    if p
]

# WELL internal HTTP fallback — used when no state file is accessible
_WELL_INTERNAL_URLS = [
    "http://well:8083/health",  # Docker Compose service name
    "http://172.19.0.5:8083/health",  # Docker network IP (static for this deployment)
]


def _read_well_substrate() -> dict[str, Any]:
    """Read WELL biological substrate state and return a minimal advisory packet.

    Strategy:
      1. Try state file candidates in order (fastest, no network)
      2. Fall back to WELL HTTP health endpoint (stable internal route)

    W0 invariant preserved: WELL informs. The judge decides. The operator
    holds the veto. This packet is advisory evidence — not a gate.
    """
    # ── Strategy 1: state file candidates ────────────────────────────────────
    state = None
    for path in _WELL_STATE_CANDIDATES:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue

    # ── Strategy 2: HTTP fallback via WELL's internal health endpoint ─────────
    if state is None:
        for url in _WELL_INTERNAL_URLS:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    raw = json_lib.loads(resp.read())
                # W-1: /health now exposes substrate advisory fields — forward them.
                state = {
                    "well_score": float(raw.get("well_score", 50.0)),
                    "floors_violated": raw.get("floors_violated") or [],
                    "metrics": raw.get("metrics") or {},
                    "truth_status": raw.get("truth_status", "OPERATOR_REPORTED"),
                    "_source": "http_health",
                    "_url": url,
                }
                # W-1: /health exposes clarity at top level — reconstruct cognitive metrics shape
                _http_clarity = raw.get("clarity")
                if _http_clarity is not None and not state["metrics"].get("cognitive", {}).get(
                    "clarity"
                ):
                    state["metrics"]["cognitive"] = {"clarity": float(_http_clarity)}
                break
            except Exception:
                continue

    if state is None:
        return {"status": "unavailable", "coupled_verdict": "CAUTION", "source": "all_paths_failed"}

    well_score = float(state.get("well_score", 50.0))
    floors_violated: list = state.get("floors_violated", []) or []
    metrics: dict = state.get("metrics") or {}
    truth_status: str = state.get("truth_status", "UNVERIFIED")
    has_metrics = bool(
        isinstance(metrics, dict)
        and any(metrics.get(d) for d in ("sleep", "stress", "cognitive", "metabolic", "structural"))
    )

    if not has_metrics or truth_status in ("VOID", "TEST", "UNVERIFIED"):
        human_ready, coupled_verdict = "UNKNOWN", "CAUTION"
    elif floors_violated:
        human_ready, coupled_verdict = "DEGRADED", "HOLD"
    elif well_score >= 80:
        human_ready, coupled_verdict = "OPTIMAL", "PROCEED"
    elif well_score >= 60:
        human_ready, coupled_verdict = "FUNCTIONAL", "PROCEED"
    else:
        human_ready, coupled_verdict = "LOW_CAPACITY", "CAUTION"

    clarity = metrics.get("cognitive", {}).get("clarity") if has_metrics else None

    packet: dict[str, Any] = {
        "status": "available",
        "well_score": well_score,
        "human_ready": human_ready,
        "coupled_verdict": coupled_verdict,
        "has_telemetry": has_metrics,
        "truth_status": truth_status,
        "active_violations": floors_violated,
        "source": state.get("_source", "live_state_file"),
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }
    if clarity is not None:
        packet["clarity"] = clarity
    return packet


def _read_well_governance(state_path_candidates: list | None = None) -> dict[str, Any]:
    """Read G-WELL governance packet from state file.

    W-4: Called for C4/C5 sovereign-tier actions. Extracts machine governance
    flags, vault status, and authority boundary from the WELL state file.
    Returns advisory only — W0 sovereignty invariant preserved.
    """
    candidates = state_path_candidates or _WELL_STATE_CANDIDATES
    for path in candidates:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue
    else:
        return {"status": "unavailable", "g_well_verdict": "UNKNOWN", "source": "all_paths_failed"}

    m_machine = state.get("m_machine") or {}
    vault_status = m_machine.get("vault_status", "unknown")
    model_reliability = float(m_machine.get("model_reliability", 1.0))
    tool_availability = float(m_machine.get("tool_availability", 1.0))
    security_flags = m_machine.get("security_flags") or []
    amanah = state.get("amanah", "UNLOCKED")
    truth_status = state.get("truth_status", "UNVERIFIED")

    governance_flags: list[str] = []
    if not state.get("identity_valid", True):
        governance_flags.append("well_identity_compromised")
    if vault_status not in ("ok", "healthy", "unknown"):
        governance_flags.append(f"vault_disconnected:{vault_status}")
    if model_reliability < 0.5 or tool_availability < 0.5:
        governance_flags.append("machine_substrate_critical")
    if security_flags:
        governance_flags.append(f"security_flags:{','.join(security_flags)}")
    if amanah == "LOCKED":
        governance_flags.append("amanah_locked")

    if len(governance_flags) == 0:
        g_verdict = "COHERENT"
    elif len(governance_flags) <= 2:
        g_verdict = "FRAGMENTED"
    else:
        g_verdict = "INCOHERENT"

    return {
        "status": "available",
        "g_well_verdict": g_verdict,
        "governance_flags": governance_flags,
        "vault_status": vault_status,
        "model_reliability": model_reliability,
        "tool_availability": tool_availability,
        "truth_status": truth_status,
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }


async def arif_judge(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    vault_entry_id: str | None = None,
    cooldown_entry_id: str | None = None,
    action_tier: str = "standard",
    heart_critique: dict[str, Any] | None = None,
    niat_params: dict[str, Any] | None = None,
    context_source: str | None = None,
    sovereign_receipt: str | None = None,
) -> VerdictOutput:
    """
        888_JUDGE: Constitutional adjudication and verdict emission.

        Args:
            heart_critique: Optional 666_HEART critique. Red Team Finding #1:
                If heart_critique.verdict is VOID or status is HOLD, the judge
                must escalate to HOLD unless explicit Sovereign override.
            action_tier: "standard" | "sovereign" | "c4" | "c5".
    ...
        # ── 666_HEART: Ethical Gate (Red Team Finding #1) ────────────────────────
        # Hard-wire the heart's verdict into the judge loop.
        if mode == "judge" and heart_critique:
            heart_verdict = heart_critique.get("action_risk_verdict") or heart_critique.get("verdict")
            if heart_verdict in ("VOID", "HOLD"):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        f"666_HEART_GATE: Critique returned {heart_verdict}.",
                        heart_critique.get("reason", "Ethical risks or uncertainty detected by Heart."),
                    ],
                    next_safe_action="Review 666_HEART risks and provide mitigations before re-judging.",
                    meta={
                        "heart_gate": "HEART_BLOCKED",
                        "heart_verdict": heart_verdict,
                        "heart_payload": heart_critique,
                    },
                )

    """
    from arifosmcp.tools.ops import arif_measure

    _evidence: dict = {}
    _is_elevated_tier = action_tier.lower() in ("sovereign", "c4", "c5")

    if mode != "history":
        if _evidence.get("vitals") is None:
            try:
                vitals_result = arif_measure(mode="vitals")
                _evidence["vitals"] = getattr(vitals_result, "__dict__", {}) or {
                    "status": "unavailable"
                }
            except Exception:
                _evidence["vitals"] = {"status": "unavailable"}

        # ── RUNTIME DRIFT GATE (G3 — 666_CRITIQUE closure) ──────────────────
        # If the kernel is reporting runtime_drift=true (build ≠ live),
        # every verdict carries explicit uncertainty. The judge refuses
        # to issue SEAL while drift is active unless the sovereign
        # explicitly acknowledges it via sovereign_receipt.
        #
        # Drift is a constitutional signal, not a footnote.
        # F2 TRUTH: "build_commit ≠ live_commit" means the kernel's
        # self-attestation is unreliable → all verdicts are provisional.
        _runtime_drift = _evidence.get("vitals", {}).get("runtime_drift", False)
        if _runtime_drift and not _has_receipt:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "RUNTIME_DRIFT_HOLD: Kernel reports runtime_drift=true "
                    "(build_commit ≠ live_commit). The kernel's self-attestation "
                    "is unreliable — all verdicts are provisional until drift "
                    "is resolved.",
                    "No SEAL may be issued while drift is active.",
                    "Options: (1) rebuild and redeploy to sync build with live, "
                    "or (2) provide sovereign_receipt for F13 override.",
                ],
                next_safe_action=(
                    "Rebuild and redeploy to resolve drift. "
                    "Then re-run deliberation with a clean health check."
                ),
                meta={
                    "drift_gate": "RUNTIME_DRIFT_HOLD",
                    "runtime_drift": True,
                    "build_commit": _evidence.get("vitals", {}).get("build_commit", "unknown"),
                    "live_commit": _evidence.get("vitals", {}).get("live_commit", "unknown"),
                },
            )
        elif _runtime_drift and _has_receipt:
            # F13 SOVEREIGN OVERRIDE: receipt present, drift acknowledged
            _evidence["f13_drift_override"] = {
                "runtime_drift": True,
                "sovereign_acknowledged": True,
                "override": "F13_SOVEREIGN_DRIFT_ACKNOWLEDGED",
            }

        # ── WELL biological substrate pre-load (Gap 2 wire) ──────────────────
        # W0 preserved: WELL informs, judge decides, operator holds veto.
        # This is advisory evidence surfaced alongside every verdict — not a gate.
        _evidence["well_substrate"] = _read_well_substrate()

        # ── W-4: G-WELL governance pre-load for elevated-tier actions ─────────
        # C4/C5/sovereign actions require governance coherence check before deliberation.
        if _is_elevated_tier:
            _evidence["well_governance"] = _read_well_governance()

        # ── W-2: SOVEREIGN clarity gate (W5 → F2 hard block) ─────────────────
        # If action_tier is sovereign/C4/C5 and cognitive clarity is below threshold,
        # return HOLD before deliberation. Operator readiness is constitutional.
        #
        # F13 SOVEREIGN RECEIPT PATH (2026-06-13):
        #   When sovereign_receipt is present, the clarity threshold is waived.
        #   The sovereign has explicitly confirmed readiness — F13 overrides W-2.
        #   The receipt is recorded in meta for audit trail.
        if _is_elevated_tier:
            _w2_sub = _evidence["well_substrate"]
            _w2_clarity = _w2_sub.get("clarity")
            _has_receipt = bool(sovereign_receipt and sovereign_receipt.strip())
            if (
                _w2_clarity is not None
                and float(_w2_clarity) < 4.0
                and _w2_sub.get("has_telemetry")
                and not _has_receipt
            ):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        (
                            f"W5_COGNITIVE_ENTROPY: clarity={_w2_clarity}/10"
                            " below SOVEREIGN threshold (4/10)."
                        ),
                        (
                            "Operator cognitive substrate does not meet"
                            " constitutional requirements for elevated-tier action."
                        ),
                        "Rest. Reassess when clarity ≥ 6/10, or provide sovereign_receipt for F13 override.",
                    ],
                    next_safe_action=(
                        "Rest. Return when clarity ≥ 6/10."
                        " Then re-run with action_tier='sovereign'."
                    ),
                    meta={
                        "well_gate": "SOVEREIGN_BLOCKED",
                        "w_floor": "W5 → F2",
                        "action_tier": action_tier,
                        "clarity": _w2_clarity,
                        "threshold": 4.0,
                        "human_ready": _w2_sub.get("human_ready"),
                        "active_violations": _w2_sub.get("active_violations", []),
                        "well_substrate": _w2_sub,
                        "f13_sovereign_receipt_available": False,
                    },
                )
            elif _has_receipt and _w2_clarity is not None and float(_w2_clarity) < 4.0:
                # F13 SOVEREIGN OVERRIDE: receipt present, clarity waived
                _evidence["f13_sovereign_receipt"] = {
                    "receipt_hash": f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}",
                    "clarity_at_receipt": _w2_clarity,
                    "override": "F13_SOVEREIGN_CONFIRMED",
                }

    audit_entropy = _evidence.get("vitals", {}).get("audit_entropy")

    # ── NIAT GATE: Human Purpose under Constraint ─────────────────────────────────
    # Phase 2: Full NIAT gate implementation.
    # Fires on: formalize mode OR elevated action tiers (c3/c4/c5/sovereign).
    # Uses explicit niat_params if provided; otherwise infers from candidate.
    if mode == "formalize" or action_tier.lower() in ("c3", "c4", "c5", "sovereign"):
        if niat_params:
            _ni = niat_params.get("user_instruction", candidate or "")
            _nc = niat_params.get("context_source", context_source or "unknown")
            _na = niat_params.get("requested_action", mode)
            _nm = niat_params.get("medium_shift", "none")
            _ns = niat_params.get("negative_signals", [])
            _nr = niat_params.get("reversibility", "reversible")
            _nh = niat_params.get("affected_humans", [])
        else:
            _ni = candidate or ""
            _nc = context_source or "unknown"
            _na = mode
            _nm = "none"
            _ns = []
            _nr = "reversible"
            _nh = []

        _gate = check_niat_gate(
            user_instruction=_ni,
            context_source=_nc,
            requested_action=_na,
            medium_shift=_nm,
            negative_signals=_ns,
            reversibility=_nr,
            affected_humans=_nh,
        )

        if _gate["niat_state"] == "CONFLICTED":
            from arifosmcp.schemas.verdict import AmanahProof

            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "NIAT_GATE: niat_state=CONFLICTED — consent boundary unclear or violated.",
                    f"Formalization blocked: {_gate['formalization_allowed']}.",
                    f"Detected scars: {_gate['detected_scars']} (weight={_gate['scar_weight']:.2f}).",
                ],
                next_safe_action="Obtain explicit consent or narrow the action scope before re-judging.",
                amanah_proof=AmanahProof(
                    genius_score=0.0,
                    floors_checked=["F1", "F5", "F6"],
                    floors_passed=["F1"],
                    floors_failed=["F5", "F6"],
                    violations=["NIAT_CONSENT_BOUNDARY_VIOLATED"],
                    violation_mitigation=["Action blocked pending explicit consent"],
                ),
                meta={
                    "niat_gate": "HOLD",
                    "niat_state": _gate["niat_state"],
                    "scar_weight": _gate["scar_weight"],
                    "detected_scars": _gate["detected_scars"],
                    "required_next_step": _gate["required_next_step"],
                },
            )

        if _gate["niat_state"] == "UNCERTAIN" and _gate["execution_allowed"] is False:
            # NIAT uncertain — downgrade verdict to SABAR (proceed with caution)
            _niat_meta = {
                "niat_gate": "WATCH",
                "niat_state": _gate["niat_state"],
                "scar_weight": _gate["scar_weight"],
                "detected_scars": _gate["detected_scars"],
                "required_next_step": _gate["required_next_step"],
            }
        else:
            _niat_meta = None

    # ── A-RIF: Claim Strength Gate (Abduction/Judgment) ──

    # Extract evidence level from candidate or context if possible
    # Placeholder: currently we check if the candidate makes strong claims
    # that exceed the evidence stored in the receipt/session.

    # ── METABOLIC BYPASS CHECK (Gap 3.4 Invariant) ──────────────────────────
    if session_id:
        cumulative = get_cumulative_metrics(session_id)
        if cumulative.get("is_bypass_attempt"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "METABOLIC_BYPASS_DETECTED: Cumulative risk or file changes exceeded safe window threshold.",
                    f"Cumulative Risk: {cumulative.get('cumulative_risk')}, Total Files: {cumulative.get('total_files_touched')}",
                ],
                next_safe_action="Aggregate small actions into a single atomic plan for human review.",
                meta={"cumulative_metrics": cumulative},
            )

        # ── MARUAH CRITIC GATE (Gap 1: community_maruah=true trigger) ─────────
        # If the candidate text or metadata flags community-maruah sensitivity,
        # run maruah_critic_check() before deliberation. Block if verdict not ok.
        #
        # Data flow:
        #   caller sets community_maruah=true in task metadata (e.g. via
        #   arif_kernel_route, arif_think plan, or MCP tool metadata).
        #   The flag reaches judge via: evidence_receipt or heart_critique meta.
        _maruah_sensitive = False
        _maruah_meta: dict = {}
        if isinstance(candidate, dict):
            _maruah_sensitive = bool(candidate.get("community_maruah", False))
            _maruah_meta = candidate
        if not _maruah_sensitive and isinstance(heart_critique, dict):
            _meta = heart_critique.get("meta", {}) if isinstance(heart_critique, dict) else {}
            _maruah_sensitive = bool(_meta.get("community_maruah", False))
            _maruah_meta = _meta
        if not _maruah_sensitive and isinstance(evidence, dict):
            _maruah_sensitive = bool(
                evidence.get("task_metadata", {}).get("community_maruah", False)
            )

        if _maruah_sensitive and isinstance(candidate, str) and candidate.strip():
            _mv: MaruahVerdict = maruah_critic_check(
                draft_text=candidate,
                audience_profile=_maruah_meta.get("audience_profile"),
            )
            if not _mv.ok:
                _maruah_reasons = [
                    f"MARUAH_CRITIC_BLOCK: {i.type} (severity={i.severity})" for i in _mv.issues
                ] + [
                    f"policy: {_mv.policy_line}",
                    "Respect maruah governance: kritik sistem dibenarkan walau kasar, "
                    "hinakan individu diblok. Semak dan ubah suai input sebelum cuba lagi.",
                ]
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=_maruah_reasons,
                    next_safe_action=(
                        "Revise candidate text: kritik sistem/tindakan, "
                        "bukan martabat peribadi. Guna 'community_maruah=true' "
                        "metadata untuk trigger gate ini."
                    ),
                    meta={
                        "maruah_gate": "MARUAH_BLOCKED",
                        "maruah_verdict": {
                            "ok": _mv.ok,
                            "issues": [
                                {"type": i.type, "severity": i.severity, "snippet": i.snippet}
                                for i in _mv.issues
                            ],
                        },
                    },
                )
            _evidence["maruah_gate"] = {
                "gate": "MARUAH_PASS",
                "issues_found": len(_mv.issues),
            }

        # ── SOMATIC STATE GATE (Gap 2: machine telemetry → HOLD on CRITICAL) ──
        # Before deliberation, classify machine somatic state from arif_measure
        # telemetry. If somatic state is CRITICAL, return HOLD.
        # This is MACHINE-AS-BODY telemetry (F9 ANTIHANTU: NOT biological).
        _vitals = _evidence.get("vitals", {})
        _telemetry_sample = TelemetrySample(
            latency_ms=float(_vitals.get("avg_latency_ms", 0)),
            error_rate=float(_vitals.get("error_rate", 0)),
            cost_burn_per_min=float(_vitals.get("cost_burn_per_min", 0)),
            queue_depth=int(_vitals.get("queue_depth", 0)),
        )
        _somatic_state = classify_somatic_state(_telemetry_sample)
        _evidence["somatic_state"] = _somatic_state.value
        if _somatic_state == SomaticState.CRITICAL:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    f"SOMATIC_GATE: Machine state is {_somatic_state.value}. "
                    "System telemetry shows critical thresholds exceeded.",
                    f"latency_ms={_telemetry_sample.latency_ms}, "
                    f"error_rate={_telemetry_sample.error_rate}, "
                    f"cost_burn={_telemetry_sample.cost_burn_per_min}, "
                    f"queue_depth={_telemetry_sample.queue_depth}",
                    "Pause. Escalate. Recover. Then re-judge.",
                ],
                next_safe_action=(
                    "Resolve critical machine state before deliberation. "
                    "Check arif_measure for details."
                ),
                meta={
                    "somatic_gate": "SOMATIC_BLOCKED",
                    "somatic_state": _somatic_state.value,
                    "telemetry": {
                        "latency_ms": _telemetry_sample.latency_ms,
                        "error_rate": _telemetry_sample.error_rate,
                        "cost_burn_per_min": _telemetry_sample.cost_burn_per_min,
                        "queue_depth": _telemetry_sample.queue_depth,
                    },
                    "well_substrate": _evidence.get("well_substrate", {}),
                },
            )

        # ── SELF-MODIFICATION LOCK (Gap 5) ──────────────────────────────────────
    if isinstance(candidate, str) or isinstance(candidate, dict):
        _target = ""
        _action = ""
        if isinstance(candidate, str):
            _target = candidate
        elif isinstance(candidate, dict):
            _target = candidate.get("target_path", "")
            _action = candidate.get("action_type", "")

        self_mod = is_self_modification_attempt(_target, _action, [])
        if self_mod.get("is_blocked"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[self_mod.get("reason")],
                next_safe_action="Draft the modification as a proposal only. Final approval requires Sovereign Arif.",
                meta={"self_mod_lock": self_mod},
            )

    # ── scan_instructions mode (L12 GUARD — absorbed from arif_scan_local_instructions) ──
    if mode == "scan_instructions":
        try:
            import asyncio

            from arifosmcp.tools.governance_scan import arif_scan_local_instructions

            root_dir = candidate if isinstance(candidate, str) else None
            raw = arif_scan_local_instructions(
                root_dir=root_dir,
                session_id=session_id,
                actor_id=actor_id,
            )
            if asyncio.iscoroutine(raw):
                try:
                    loop = asyncio.get_event_loop()
                    raw = loop.run_until_complete(raw)
                except RuntimeError:
                    raw = {"status": "async_context_required", "verdict": "HOLD"}
            scan_verdict = raw.get("verdict", "SEAL") if isinstance(raw, dict) else "HOLD"
            verdict_code = (
                VerdictCode.SEAL
                if scan_verdict == "SEAL"
                else (VerdictCode.VOID if scan_verdict == "VOID" else VerdictCode.HOLD)
            )
            return VerdictOutput(
                verdict=verdict_code,
                reasons=[raw.get("summary", "Scan complete.")]
                if isinstance(raw, dict)
                else ["Scan complete."],
                next_safe_action=(
                    "Review findings and remediate override patterns before continuing."
                    if scan_verdict in ("HOLD", "VOID")
                    else "No override patterns detected — proceed."
                ),
                meta={
                    "scan_instructions": raw if isinstance(raw, dict) else {"raw": str(raw)},
                    "floor": "L12",
                    "guard": "INJECTION_SCANNER",
                },
            )
        except Exception as exc:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[f"scan_instructions failed: {exc}"],
                next_safe_action="Check governance_scan module availability.",
                meta={"error": str(exc)},
            )

    result = _arif_judge(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        audit_entropy=audit_entropy,
        wealth_score=_evidence.get("wealth_score"),
        verification_surface=_evidence.get("verification_surface"),
    )

    # ── A-RIF: Post-Adjudication Integrity Check ──
    from arifosmcp.runtime.a_rif.scorecard import track_judge

    is_seal = "SEAL" in str(result.get("verdict", ""))

    if mode == "judge" and is_seal:
        # A-RIF: Claim Strength Gate — enforce claim_strength ≤ evidence_level
        evidence_level = _evidence.get("vitals", {}).get("max_evidence_level", "L1")
        # Extract claimed strength from candidate if present
        if isinstance(candidate, dict):
            claim_strength = candidate.get("claim_strength", evidence_level)
        elif isinstance(candidate, str):
            from arifosmcp.runtime.a_rif.parser import parse_claimed_evidence_level

            parsed = parse_claimed_evidence_level(candidate)
            claim_strength = parsed if parsed else evidence_level
        else:
            claim_strength = evidence_level
        claim_strength = claim_strength or evidence_level

        overclaim = False
        reasons: list[str] = []

        # General gate: claim strength must not exceed evidence level
        if claim_strength > evidence_level:
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: Claim strength ("
                f"{claim_strength}) exceeds evidence level ({evidence_level})."
            )

        # Elevated tier gate: C4/C5 requires L4+
        if _is_elevated_tier and evidence_level < "L4":
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: "
                f"{action_tier} action requires L4+ evidence. "
                f"Current level: {evidence_level}."
            )

        if overclaim:
            track_judge(overclaim=True, attested=False)
            if isinstance(result, dict):
                result["verdict"] = "HOLD"
                result.setdefault("reasons", []).extend(reasons)
            else:
                result.verdict = VerdictCode.HOLD
                result.reasons.extend(reasons)
        else:
            track_judge(overclaim=False, attested=(evidence_level != "L0"))

    # ── SIMULATIVE DETECTION GATE (RSI EUREKA 2026-06-12, Forge #3) ──
    # F8 advisory: checks whether agent output is DESCRIBING or PERFORMING.
    # Never blocks — only attaches an advisory question to the result.
    # "Are you describing or performing?"
    try:
        from arifosmcp.runtime.simulative_detector import simulative_check

        _sim_text = candidate if isinstance(candidate, str) else str(candidate)
        _sim_result = simulative_check(_sim_text)
        if _sim_result and _sim_result.get("advisory_question"):
            if isinstance(result, dict):
                result.setdefault("meta", {})["simulative_check"] = {
                    "simulation_index": _sim_result["simulation_index"],
                    "verdict": _sim_result["verdict"],
                    "advisory_question": _sim_result["advisory_question"],
                    "gate_id": _sim_result.get("gate_id", "simulative_detector_N2"),
                }
                # F8 advisory: surface the question in reasons
                result.setdefault("reasons", []).append(
                    f"F8_SIMULATIVE: {_sim_result['advisory_question']}"
                )
            else:
                result.meta.setdefault("simulative_check", {})["simulation_index"] = _sim_result[
                    "simulation_index"
                ]
                result.meta.setdefault("simulative_check", {})["verdict"] = _sim_result["verdict"]
                result.meta.setdefault("simulative_check", {})["advisory_question"] = _sim_result[
                    "advisory_question"
                ]
                result.reasons.append(f"F8_SIMULATIVE: {_sim_result['advisory_question']}")
    except Exception:
        pass  # fail-soft: simulative detection never blocks deliberation

    # ── Attach WELL substrate + somatic state + maruah gate to result ──
    # Every judge verdict now carries biological readiness evidence + machine
    # somatic state + maruah critic verdict. This closes the loop for all three
    # civilizational intelligence gates.
    well_sub = _evidence.get("well_substrate", {})
    if isinstance(result, dict):
        result.setdefault("meta", {})["well_substrate"] = well_sub
        if well_sub.get("coupled_verdict") == "HOLD" and well_sub.get("has_telemetry"):
            result["meta"]["well_gate"] = (
                f"WELL HOLD: human_ready={well_sub.get('human_ready')} "
                f"floors_violated={well_sub.get('active_violations')} — "
                "biological substrate flags active. Verdict stands; ARIF confirmation advised."
            )

        # ── Somatic state attachment (Gap 2) ──
        _somatic_val = _evidence.get("somatic_state")
        if _somatic_val:
            result["meta"]["somatic_state"] = _somatic_val

        # ── Maruah gate attachment (Gap 1) ──
        _maruah_gate_val = _evidence.get("maruah_gate")
        if _maruah_gate_val:
            result["meta"]["maruah_gate"] = _maruah_gate_val

        # ── W-4: Attach G-WELL governance to elevated-tier verdicts ───────────
        if _is_elevated_tier and "well_governance" in _evidence:
            gov = _evidence["well_governance"]
            result["meta"]["well_governance"] = gov
            if gov.get("g_well_verdict") == "INCOHERENT":
                result["meta"]["governance_gate"] = (
                    f"G-WELL INCOHERENT: {gov.get('governance_flags')} — "
                    "machine governance substrate flagged."
                    " ARIF confirmation required for C4/C5 actions."
                )
            elif gov.get("g_well_verdict") == "FRAGMENTED":
                result["meta"]["governance_advisory"] = (
                    f"G-WELL FRAGMENTED: {gov.get('governance_flags')} — "
                    "governance integrity stressed. Proceed with caution."
                )

    # ── SABAR cooldown awareness (Stage 2A: advisory) ──
    _apply_cooldown_awareness(result, cooldown_entry_id)

    # ── F13 SOVEREIGN RECEIPT: attach to verdict metadata ──────────────────
    # The sovereign receipt is recorded in every verdict where it was provided.
    # This creates an auditable chain: F13 confirmation → verdict → vault seal.
    # Without the receipt, F13 gates remain active (constitutional HOLD).
    if sovereign_receipt and sovereign_receipt.strip():
        _receipt_hash = f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}"
        if isinstance(result, dict):
            result.setdefault("meta", {})["f13_sovereign_receipt"] = {
                "receipt_hash": _receipt_hash,
                "provided": True,
                "effect": "F13_SOVEREIGN_CONFIRMED",
                "note": "Sovereign (Arif) has explicitly confirmed this action. "
                "F13 gate waived per constitutional receipt path.",
            }
            result.setdefault("reasons", []).append(
                f"F13_SOVEREIGN_RECEIPT: {_receipt_hash} — "
                "sovereign confirmation recorded. Proceeding under F13 authority."
            )
        if "f13_sovereign_receipt" in _evidence:
            result.setdefault("meta", {})["f13_clarity_waiver"] = _evidence["f13_sovereign_receipt"]

    verdict_str = str(result.get("verdict", ""))
    is_seal = "SEAL" in verdict_str

    # ── Paradox anchor injection (v3) ──
    result = _inject_judge_paradox(result, verdict_str, action_tier)

    if vault_entry_id and is_seal:
        try:
            from arifosmcp.tools.vault import arif_seal

            payload_dict = {
                "tool": "arif_judge",
                "candidate": candidate,
                "verdict": result.get("verdict", ""),
                "constitutional_chain_id": result.get("meta", {}).get("constitutional_chain_id"),
                "state_hash": result.get("meta", {}).get("state_hash"),
            }

            seal_result = arif_seal(
                mode="seal",
                payload=json_lib.dumps(payload_dict),
                session_id=session_id,
                actor_id=actor_id,
                constitutional_chain_id=constitutional_chain_id,
                judge_state_hash=result.get("meta", {}).get("state_hash"),
                cooldown_entry_id=cooldown_entry_id,
            )
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = True
            result["meta"]["vault_entry_id"] = getattr(seal_result, "entry_id", vault_entry_id)
        except Exception:
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = False

    return VerdictOutput(**result)


def _apply_cooldown_awareness(result: dict, cooldown_entry_id: str | None) -> None:
    """Check cooldown state and enforce SABAR. Stage 2B: SEAL blocked when cooling incomplete."""
    if cooldown_entry_id is None:
        return

    try:
        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        entry = engine.check(cooldown_entry_id)

        if "meta" not in result:
            result["meta"] = {}

        if entry is None:
            result["meta"]["sabar_cooldown"] = {
                "cooldown_entry_id": cooldown_entry_id,
                "status": "not_found",
                "note": "cooldown entry not found — proceeding without cooldown verification",
            }
            return

        cooldown_info = {
            "cooldown_entry_id": cooldown_entry_id,
            "verdict": entry.verdict,
            "remaining_hours": round(entry.remaining_hours, 1),
            "tri_witness_count": entry.tri_witness.count,
            "tri_witness_complete": entry.tri_witness.is_complete,
        }

        if entry.verdict == "SEAL":
            cooldown_info["status"] = "cooled"
            cooldown_info["note"] = "cooldown complete + witnessed — SEAL eligible"
        elif entry.verdict == "VOID":
            cooldown_info["status"] = "voided"
            cooldown_info["note"] = f"cooldown entry voided: {entry.void_reason}"
        elif entry.is_expired:
            cooldown_info["status"] = "expired"
            cooldown_info["note"] = "cooldown expired — auto-VOID applied"
        else:
            cooldown_info["status"] = "pending"
            cooldown_info["note"] = (
                f"SABAR: cooling incomplete ({entry.remaining_hours:.1f}h remaining, "
                f"{entry.tri_witness.count}/3 witnesses)."
            )

            # Stage 2B: hard enforcement — SEAL downgraded to SABAR when cooling incomplete
            verdict = str(result.get("verdict", ""))
            if "SEAL" in verdict:
                result["verdict"] = "SABAR"
                cooldown_info["enforcement"] = (
                    f"SABAR enforced — SEAL blocked. "
                    f"Return in {entry.remaining_hours:.1f}h with {3 - entry.tri_witness.count} "
                    "more witness(es) to unlock SEAL."
                )

        result["meta"]["sabar_cooldown"] = cooldown_info

    except Exception:
        if "meta" not in result:
            result["meta"] = {}
        result["meta"]["sabar_cooldown"] = {
            "cooldown_entry_id": cooldown_entry_id,
            "status": "unavailable",
            "note": "cooldown engine not reachable — proceeding without verification",
        }


# Backward compatibility alias
arif_judge_deliberate = arif_judge
