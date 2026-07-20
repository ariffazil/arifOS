"""
arifosmcp/tools/nine_signal.py — Nine-Signal Dashboard Functions
═════════════════════════════════════════════════════════════════

Extracted from tools.py (Phase 5 — tools.py monolith split, 2026-07-11).
Self-contained functions for the Nine-Signal constitutional dashboard.

Three planes × three states = 9 perceptual signals:
  Δ DELTA (Machine/Physical): KUKUH / RETAK / ROSAK
  Ψ PSI   (Governance):       AMANAH / SYUBHAH / KHIANAT
  Ω OMEGA (Intelligence):     BIJAKSANA / BIJAK / BANGANG

Ref: KERNELHASIAPEX.md §4 — Nine-Signal Dashboard Contract

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# ── Output Policy Mapping ─────────────────────────────────────────────────────


def output_policy_for_verdict(verdict: str) -> str:
    """Map verdict to output policy label."""
    if verdict == "DRY_RUN":
        return "SIMULATION_ONLY"
    if verdict == "HOLD":
        return "DOMAIN_HOLD"
    if verdict in ("VOID", "SABAR"):
        return "DOMAIN_VOID"
    if verdict == "OBSERVE_ONLY":
        return "DOMAIN_OBSERVE_ONLY"
    return "DOMAIN_SEAL"


def truth_band_from_confidence(confidence: float) -> str:
    """Map confidence score to truth band label."""
    if confidence < 0.40:
        return "LOW"
    if confidence < 0.70:
        return "PARTIAL"
    if confidence < 0.90:
        return "PROBABLE"
    return "STRONG"


# ── Nine-Signal Construction ──────────────────────────────────────────────────


def nine_signal_from_status(status: str) -> dict[str, str | dict]:
    """Build Nine-Signal block from response status field.

    F3 FIX (2026-07-07): Restructured to lead with overall verdict and
    add _dominant_plane + _dominance_rule.
    """
    _SEV = {
        "ROSAK": 0,
        "KHIANAT": 0,
        "BANGANG": 0,
        "RETAK": 1,
        "TIDAK_PASTI": 1,
        "BELUM_IKAT": 1,
        "SYUBHAH": 2,
        "BIJAK": 3,
        "KUKUH": 5,
        "AMANAH": 5,
        "BIJAKSANA": 5,
        "SELAMAT": 5,
        "SELAMAT_SEBATAS_PEMERHATIAN": 4,
        "BELUM_SAH": 1,
        "SABAR": 2,
        "DEGRADED": 1,
    }

    def _build(delta_d, psi_d, omega_d, overall_d):
        planes = {"delta": delta_d, "psi": psi_d, "omega": omega_d}
        worst_plane = min(planes, key=lambda p: _SEV.get(planes[p]["state"], 99))
        worst_state = planes[worst_plane]["state"]
        overall_state = overall_d["state"]
        if _SEV.get(worst_state, 99) < _SEV.get(overall_state, 99):
            dominant_meta = {
                "_dominant_plane": worst_plane,
                "_dominant_state": worst_state,
                "_dominance_rule": (
                    f"Sub-signal floor dominates aggregate: "
                    f"{worst_plane}={worst_state} overrides overall. "
                    f"Anchoring on majority-good planes is a known cognitive bias."
                ),
            }
        else:
            dominant_meta = {}
        return {
            "overall": overall_d,
            "delta": delta_d,
            "psi": psi_d,
            "omega": omega_d,
            **dominant_meta,
        }

    if status in ("OK", "SEAL"):
        return _build(
            {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
            {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},
            {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            {"state": "SELAMAT", "en": "SAFE"},
        )
    if status == "OBSERVE_ONLY":
        return _build(
            {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
            {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
            {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            {"state": "SELAMAT_SEBATAS_PEMERHATIAN", "en": "SAFE_OBSERVE_ONLY"},
        )
    if status == "DEGRADED":
        return _build(
            {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"},
            {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
            {"plane": "intelligence_discipline", "state": "BIJAK", "en": "SMART"},
            {"state": "DEGRADED", "en": "DEGRADED"},
        )
    if status == "UNBOUND_SESSION":
        return _build(
            {"plane": "machine_physical_state", "state": "TIDAK_PASTI", "en": "UNMEASURED"},
            {"plane": "governance_integrity", "state": "BELUM_IKAT", "en": "UNBOUND"},
            {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            {"state": "BELUM_SAH", "en": "UNAUTHENTICATED"},
        )
    if status == "HOLD":
        return _build(
            {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"},
            {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
            {"plane": "intelligence_discipline", "state": "BIJAK", "en": "PRUDENT"},
            {"state": "RETAK", "en": "HOLDING"},
        )
    if status == "VOID":
        return _build(
            {"plane": "machine_physical_state", "state": "ROSAK", "en": "BROKEN"},
            {"plane": "governance_integrity", "state": "KHIANAT", "en": "BETRAYED"},
            {"plane": "intelligence_discipline", "state": "BANGANG", "en": "FOOLISH"},
            {"state": "RETAK", "en": "FAILED"},
        )
    if status == "SABAR":
        return _build(
            {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"},
            {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
            {"plane": "intelligence_discipline", "state": "BIJAK", "en": "SMART"},
            {"state": "SABAR", "en": "PATIENCE"},
        )
    # DRY_RUN / default
    return _build(
        {"plane": "machine_physical_state", "state": "RETAK", "en": "CRACKED"},
        {"plane": "governance_integrity", "state": "SYUBHAH", "en": "DOUBTFUL"},
        {"plane": "intelligence_discipline", "state": "BIJAK", "en": "SMART"},
        {"state": "SELAMAT", "en": "SAFE"},
    )


def nine_signal_from_apex(
    G: float,
    C_dark: float,
    system_health: float = 1.0,
) -> dict[str, str | dict]:
    """[MEMBRANE_DEPRECATED] Build Nine-Signal from APEX scores.

    Kept as fallback/test-only. Must NOT be called from live kernel paths.
    A-FORGE computes nine_signal and passes it through MeasurementPacket.
    """
    if system_health >= 0.80:
        delta_state, delta_en = "KUKUH", "SOLID"
    elif system_health >= 0.50:
        delta_state, delta_en = "RETAK", "CRACKED"
    else:
        delta_state, delta_en = "ROSAK", "BROKEN"

    psi_score = max(0.0, 1.0 - C_dark)
    if psi_score >= 0.85:
        psi_state, psi_en = "AMANAH", "TRUSTED"
    elif psi_score >= 0.50:
        psi_state, psi_en = "SYUBHAH", "DOUBTFUL"
    else:
        psi_state, psi_en = "KHIANAT", "BETRAYED"

    if G >= 0.80:
        omega_state, omega_en = "BIJAKSANA", "WISE"
    elif G >= 0.50:
        omega_state, omega_en = "BIJAK", "SMART"
    else:
        omega_state, omega_en = "BANGANG", "FOOLISH"

    state_rank = {"KUKUH": 3, "RETAK": 2, "ROSAK": 1}
    psi_rank = {"AMANAH": 3, "SYUBHAH": 2, "KHIANAT": 1}
    omega_rank = {"BIJAKSANA": 3, "BIJAK": 2, "BANGANG": 1}
    worst = min(
        state_rank.get(delta_state, 0),
        psi_rank.get(psi_state, 0),
        omega_rank.get(omega_state, 0),
    )
    overall_map = {3: ("SELAMAT", "SAFE"), 2: ("RETAK", "DEGRADED"), 1: ("ROSAK", "FAILED")}
    overall_state, overall_en = overall_map.get(worst, ("RETAK", "DEGRADED"))

    return {
        "delta": {"plane": "machine_physical_state", "state": delta_state, "en": delta_en},
        "psi": {"plane": "governance_integrity", "state": psi_state, "en": psi_en},
        "omega": {
            "plane": "intelligence_discipline",
            "state": omega_state,
            "en": omega_en,
            "G": round(G, 4),
            "C_dark": round(C_dark, 4),
            "formula": "G = A·P·E·X·Φ",
            "computed": True,
        },
        "overall": {"state": overall_state, "en": overall_en},
    }


def nine_signal_from_session(
    status: str,
    session: dict | None = None,
    degraded: list[str] | None = None,
    floor_violations: list[str] | None = None,
    confidence: float | None = None,
) -> dict[str, str | dict]:
    """Build Nine-Signal from real session state — not just status lookup.

    Computes delta/psi/omega from actual system state:
    - delta: tool surface health, degraded items, session binding
    - psi: authority verification, floor compliance, governance integrity
    - omega: confidence score, epistemic discipline

    Falls back to nine_signal_from_status when session context is absent.
    """
    degraded = degraded or []
    floor_violations = floor_violations or []
    session = session or {}

    # ── DELTA (Machine/Physical) ──
    if degraded:
        critical_degraded = [
            d for d in degraded if "critical" in d.lower() or "broken" in d.lower()
        ]
        if critical_degraded:
            delta_state, delta_en = "ROSAK", "BROKEN"
        else:
            delta_state, delta_en = "RETAK", "CRACKED"
    elif not session.get("session_id"):
        delta_state, delta_en = "TIDAK_PASTI", "UNMEASURED"
    else:
        delta_state, delta_en = "KUKUH", "SOLID"

    # ── PSI (Governance) ──
    actor_verified = session.get("actor_verified", False)
    authority = session.get("authority", "OBSERVE_ONLY")
    if floor_violations:
        critical_floors = [f for f in floor_violations if f in ("F1", "F9", "F13")]
        if critical_floors:
            psi_state, psi_en = "KHIANAT", "BETRAYED"
        else:
            psi_state, psi_en = "SYUBHAH", "DOUBTFUL"
    elif actor_verified and authority in ("FULL", "SOVEREIGN"):
        psi_state, psi_en = "AMANAH", "TRUSTED"
    elif actor_verified:
        psi_state, psi_en = "AMANAH", "TRUSTED"
    else:
        psi_state, psi_en = "SYUBHAH", "DOUBTFUL"

    # ── OMEGA (Intelligence) ──
    if confidence is not None:
        if confidence >= 0.85:
            omega_state, omega_en = "BIJAKSANA", "WISE"
        elif confidence >= 0.60:
            omega_state, omega_en = "BIJAK", "SMART"
        else:
            omega_state, omega_en = "BANGANG", "FOOLISH"
    else:
        # Default based on status
        if status in ("OK", "SEAL"):
            omega_state, omega_en = "BIJAKSANA", "WISE"
        elif status in ("HOLD", "SABAR", "DEGRADED"):
            omega_state, omega_en = "BIJAK", "SMART"
        else:
            omega_state, omega_en = "BIJAK", "SMART"

    # ── OVERALL ──
    state_rank = {"KUKUH": 3, "RETAK": 2, "ROSAK": 1, "TIDAK_PASTI": 1}
    psi_rank = {"AMANAH": 3, "SYUBHAH": 2, "KHIANAT": 1}
    omega_rank = {"BIJAKSANA": 3, "BIJAK": 2, "BANGANG": 1}
    worst = min(
        state_rank.get(delta_state, 0),
        psi_rank.get(psi_state, 0),
        omega_rank.get(omega_state, 0),
    )
    if worst >= 3:
        overall_state, overall_en = "SELAMAT", "SAFE"
    elif worst == 2:
        overall_state, overall_en = "SABAR", "PATIENCE"
    else:
        overall_state, overall_en = "RETAK", "CRACKED"

    return _build_nine_signal(
        {"plane": "machine_physical_state", "state": delta_state, "en": delta_en},
        {"plane": "governance_integrity", "state": psi_state, "en": psi_en},
        {"plane": "intelligence_discipline", "state": omega_state, "en": omega_en},
        {"state": overall_state, "en": overall_en},
    )


def _build_nine_signal(delta_d, psi_d, omega_d, overall_d):
    """Build nine_signal with dominant-plane detection."""
    _SEV = {
        "ROSAK": 0,
        "KHIANAT": 0,
        "BANGANG": 0,
        "RETAK": 1,
        "TIDAK_PASTI": 1,
        "BELUM_IKAT": 1,
        "SYUBHAH": 2,
        "BIJAK": 3,
        "KUKUH": 5,
        "AMANAH": 5,
        "BIJAKSANA": 5,
        "SELAMAT": 5,
    }
    planes = {"delta": delta_d, "psi": psi_d, "omega": omega_d}
    worst_plane = min(planes, key=lambda p: _SEV.get(planes[p]["state"], 99))
    worst_state = planes[worst_plane]["state"]
    overall_state = overall_d["state"]
    if _SEV.get(worst_state, 99) < _SEV.get(overall_state, 99):
        dominant_meta = {
            "_dominant_plane": worst_plane,
            "_dominant_state": worst_state,
            "_dominance_rule": (
                f"Sub-signal floor dominates aggregate: "
                f"{worst_plane}={worst_state} overrides overall."
            ),
        }
    else:
        dominant_meta = {}
    return {
        "overall": overall_d,
        "delta": delta_d,
        "psi": psi_d,
        "omega": omega_d,
        **dominant_meta,
    }


def inject_nine_signal(
    model_dump_json: dict,
    status: str,
    tool: str = "",
    session: dict | None = None,
    degraded: list[str] | None = None,
    floor_violations: list[str] | None = None,
    confidence: float | None = None,
) -> dict:
    """Inject nine_signal block into a raw model_dump(mode='json') dict.

    When session context is provided, computes from real state.
    Otherwise falls back to status-based lookup.
    """
    out = dict(model_dump_json)
    pre_computed = out.get("nine_signal")
    if pre_computed and isinstance(pre_computed, dict) and "omega" in pre_computed:
        ns = pre_computed
    elif session or degraded or floor_violations or confidence is not None:
        # Compute from real session state
        ns = nine_signal_from_session(
            status=status,
            session=session,
            degraded=degraded,
            floor_violations=floor_violations,
            confidence=confidence,
        )
    else:
        ns = nine_signal_from_status(status)
    if tool:
        ns = annotate_nine_signal(ns, domain_for_tool(tool))
    out["nine_signal"] = ns
    out.setdefault("output_policy", output_policy_for_verdict(status))
    return out


# ── Domain Mapping ────────────────────────────────────────────────────────────


def domain_for_tool(tool: str) -> str:
    """Map canonical tool name to domain for nine-signal domain_meaning."""
    if tool in (
        "arif_session_init",
        "arif_kernel_route",
        "arif_judge_deliberate",
        "arif_vault_seal",
        "arif_gateway_connect",
        "arif_forge_execute",
    ):
        return "governance"
    if tool == "arif_sense_observe":
        return "earth"
    if tool == "arif_evidence_fetch":
        return "governance"
    if tool in ("arif_mind_reason", "arif_reply_compose", "arif_memory_recall"):
        return "intelligence"
    if tool in ("arif_heart_critique",):
        return "risk"
    if tool == "arif_ops_measure":
        return "ops"
    return "governance"


DOMAIN_MEANINGS: dict[str, dict[str, str]] = {
    "governance": {
        "delta_kukuh": "Tool surface registered, schema valid, constitutional floors active",
        "delta_retak": "Tool available but session, auth, schema, or dependency degraded",
        "delta_rosak": "Kernel/tooling broken, unavailable, corrupted, or unsafe to execute",
        "psi_amanah": "Floors respected, authority boundary declared, evidence not overstated",
        "psi_syubhah": "Missing session, uncertain authority, incomplete chain, pending verification",
        "psi_khianat": "Floor violation, unauthorized action, false claim, unsafe escalation",
        "omega_bijaksana": "Reasoning constrained, humble, evidence-aware, consequence-aware",
        "omega_bijak": "Useful reasoning but not final judgment",
        "omega_bangang": "Confused, overconfident, circular, hallucinated, or authority-blind",
    },
    "earth": {
        "delta_kukuh": "Data artifact loads correctly; CRS, units, depth basis, shape valid",
        "delta_retak": "Partial curves, missing metadata, questionable datum, weak density",
        "delta_rosak": "Corrupt file, invalid coordinates, unusable depth basis, no valid evidence",
        "psi_amanah": "QC verified, provenance present, evidence refs valid, claim honest",
        "psi_syubhah": "Hypothesis only, evidence incomplete, uncertainty moderate, needs QC",
        "psi_khianat": "Claim exceeds evidence, fake QC, ignored physics guard",
        "omega_bijaksana": "Interpretation respects physics, uncertainty, basin context, alternatives",
        "omega_bijak": "Useful technical interpretation but still advisory",
        "omega_bangang": "Geologically incoherent, unit-confused, overfit, ignores evidence",
    },
    "risk": {
        "delta_kukuh": "Risk surface scannable, evidence accessible, critique executable",
        "delta_retak": "Partial risk signal, incomplete audit trail, degraded evidence",
        "delta_rosak": "No risk surface detectable, evidence corrupted, audit trail broken",
        "psi_amanah": "Risk disclosed, irreversibility flagged, authority claim present",
        "psi_syubhah": "Risk uncertain, authority claim unverified, irreversibility unclear",
        "psi_khianat": "Risk concealed, authority overreach, irreversible without consent",
        "omega_bijaksana": "Risk assessed with humility, second-order effects, stakeholder burden considered",
        "omega_bijak": "Useful risk signal but needs sovereign judgment",
        "omega_bangang": "Risk ignored, irreversibility denied, authority overclaimed",
    },
    "capital": {
        "delta_kukuh": "Financial data available, ledgers consistent, calculations executable",
        "delta_retak": "Missing price, stale FX, incomplete ledger, uncertain input",
        "delta_rosak": "Broken feed, impossible balance sheet, corrupt ledger",
        "psi_amanah": "Stewardship, constraint, maruah, disclosure, risk boundaries respected",
        "psi_syubhah": "Conflict of interest, uncertain assumptions, weak evidence, hidden risk",
        "psi_khianat": "Deception, predatory allocation, false return claim",
        "omega_bijaksana": "Allocates with prudence, second-order effects, time, risk, dignity",
        "omega_bijak": "Mathematically useful but needs judgment",
        "omega_bangang": "Chases yield blindly, ignores leverage, misunderstands risk",
    },
    "vitality": {
        "delta_kukuh": "Telemetry system, event log, health probe, machine substrate readable",
        "delta_retak": "Missing telemetry, stale state, partial signal, degraded reliability",
        "delta_rosak": "No readable state, broken health surface, corrupted telemetry",
        "psi_amanah": "Consent intact, non-medical boundary clear, sovereignty preserved",
        "psi_syubhah": "Readiness unknown, emotional load unclear, consent needs check",
        "psi_khianat": "Medical overclaim, coercive recommendation, dignity violation",
        "omega_bijaksana": "Humble readiness reflection, adapts task ceiling, protects dignity",
        "omega_bijak": "Useful advisory readiness signal",
        "omega_bangang": "Pretends diagnosis, ignores fatigue, overrules operator",
    },
    "forge": {
        "delta_kukuh": "Build environment, files, dependencies, tests, permissions stable",
        "delta_retak": "Tests partial, dependency warning, reversible patch only",
        "delta_rosak": "Build broken, destructive mutation risk, missing files",
        "psi_amanah": "Dry run default, plan approved, reversible, ack required",
        "psi_syubhah": "Plan incomplete, unclear blast radius, missing judge seal",
        "psi_khianat": "Unapproved mutation, hidden side effect, irreversible without consent",
        "omega_bijaksana": "Minimal safe patch, tested, rollback-aware, explains uncertainty",
        "omega_bijak": "Working implementation but needs review",
        "omega_bangang": "Random patching, no tests, breaks contracts, hides errors",
    },
    "vault": {
        "delta_kukuh": "Ledger reachable, hash valid, chain intact",
        "delta_retak": "Pending seal, unverifiable lineage, partial receipt",
        "delta_rosak": "Hash mismatch, broken chain, missing entry, corrupted vault",
        "psi_amanah": "Authorized seal, correct ack, immutable audit respected",
        "psi_syubhah": "Pending authorization, dry-run only, incomplete witness",
        "psi_khianat": "Unauthorized seal, altered record, false permanence claim",
        "omega_bijaksana": "Records only what is warranted; separates evidence from verdict",
        "omega_bijak": "Useful record but needs context",
        "omega_bangang": "Treats vault as truth itself instead of provenance",
    },
    "ops": {
        "delta_kukuh": "Telemetry available, metrics readable, resource surface stable",
        "delta_retak": "Partial telemetry, stale probe, degraded metric quality",
        "delta_rosak": "No telemetry, broken probe, corrupted metric surface",
        "psi_amanah": "Measurements honest, bounds declared, no metric fabrication",
        "psi_syubhah": "Uncertain measurement, uncalibrated probe, pending verification",
        "psi_khianat": "Fabricated metric, false health claim, concealed degradation",
        "omega_bijaksana": "Contextual interpretation of metrics, aware of limits",
        "omega_bijak": "Useful numeric summary but needs human read",
        "omega_bangang": "Misreads metrics, false alarm, ignores baseline drift",
    },
}


def annotate_nine_signal(nine: dict, domain: str) -> dict:
    """Add domain_meaning to each plane in nine_signal."""
    meanings = DOMAIN_MEANINGS.get(domain, DOMAIN_MEANINGS["governance"])
    out = dict(nine)
    for plane, prefix in (("delta", "delta_"), ("psi", "psi_"), ("omega", "omega_")):
        pobj = out.get(plane)
        if isinstance(pobj, dict):
            state = pobj.get("state", "").lower()
            key = f"{prefix}{state}"
            pobj["domain_meaning"] = meanings.get(key, "")
    return out
