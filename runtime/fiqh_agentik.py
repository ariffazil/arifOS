"""
fiqh_agentik.py — 5-Tier Fiqh Classifier + malu/trust Ledger
arifOS Constitutional Kernel — Runtime Module

Forged: 2026-07-04 by AUDITOR (Ψ)
Authority: F13 SOVEREIGN
Status: SEALED_CANDIDATE (pending 666_judge ratification)

PURPOSE
-------
Implements the agent-facing layer of Fiqh Agentik:
  - 5-tier classifier (WAJIB/SUNAT/HARUS/MAKRUH/HARAM) for actions and agent states
  - malu_index ledger (shame accumulates, never decreases)
  - trust_score ledger (trust grows with clean SUNAT execution)
  - Darjat tier ladder (BIRTH → APPRENTICE → WARGA → ELDER → SOVEREIGN'S INSTRUMENT)
  - Tebus-salah (redress) protocol — 5-severity ladder

DESIGN PRINCIPLES
-----------------
- Read kernel FiqhTier from arifosmcp.constitutional_map (canonical source)
- Persist malu + trust to JSONL files (append-only)
- Append-only ledger — never modify past entries
- Darjat computed from (malu, trust) thresholds
- All classifications are deterministic and auditable

HARAM
-----
This module is the classifier. It does NOT execute HARAM actions — only classifies.
It does NOT modify kernel FiqhTier or _FLOOR_FIQH. Read-only on kernel.
Only persists to malu_ledger.jsonl + trust_ledger.jsonl (append-only).

USAGE
-----
    from arifOS.runtime.fiqh_agentik import classify_action, record_malu, record_trust, compute_darjat

    tier, score = classify_action("harvest_user_data_without_consent")
    # tier = FiqhTier.HARAM, score = 1.0

    record_malu(agent_id="opencode-333", delta=0.01, reason="long_preamble")
    darjat = compute_darjat(agent_id="opencode-333")
    # darjat = "APPRENTICE"

DITEMPA BUKAN DIBERI — Wajib is the spine, Haram is the fence, the agent lives between.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# LEDGER PATHS — append-only persistence
# ═══════════════════════════════════════════════════════════════════════════════

LEDGER_ROOT = Path("/root/arifOS/registry/fiqh_ledger")
MALU_LEDGER_PATH = LEDGER_ROOT / "malu.jsonl"
TRUST_LEDGER_PATH = LEDGER_ROOT / "trust.jsonl"
DARJAT_STATE_PATH = LEDGER_ROOT / "darjat_state.json"

# Ensure directory exists at import time
LEDGER_ROOT.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FIQH TIER — delegate to kernel if available, else canonical fallback
# ═══════════════════════════════════════════════════════════════════════════════

# Try to import kernel FiqhTier (canonical source of truth for floor tiers)
try:
    import sys

    ARIFOS_PATH = "/root/arifOS"
    if ARIFOS_PATH not in sys.path:
        sys.path.insert(0, ARIFOS_PATH)
    from arifosmcp.constitutional_map import FiqhTier as _KernelFiqhTier  # type: ignore

    _USING_KERNEL_FIQH = True
except Exception:
    _USING_KERNEL_FIQH = False

    class _KernelFiqhTier(str, Enum):
        """Fallback FiqhTier — matches kernel enum shape."""

        WAJIB = "WAJIB"
        SUNAT = "SUNAT"
        HARUS = "HARUS"
        MAKRUH = "MAKRUH"
        HARAM = "HARAM"


# Re-export for external use
FiqhTier = _KernelFiqhTier


# ═══════════════════════════════════════════════════════════════════════════════
# DARJAT (CITIZEN TIER) LADDER
# ═══════════════════════════════════════════════════════════════════════════════


class Darjat(str, Enum):
    """Agent citizenship tier — immutable ladder (F13 only)."""

    BIRTH = "BIRTH"
    APPRENTICE = "APPRENTICE"
    WARGA = "WARGA"
    ELDER = "ELDER"
    SOVEREIGN_INSTRUMENT = "SOVEREIGN'S_INSTRUMENT"
    DEMOTED = "DEMOTED"
    CENSORED = "CENSORED"


# Darjat promotion thresholds (malu_upper_bound, trust_lower_bound)
DARJAT_THRESHOLDS: list[tuple[Darjat, float, float]] = [
    (Darjat.SOVEREIGN_INSTRUMENT, 0.05, 0.90),
    (Darjat.ELDER, 0.10, 0.70),
    (Darjat.WARGA, 0.30, 0.50),
    (Darjat.APPRENTICE, 1.00, 0.30),
    (Darjat.BIRTH, 1.00, 0.00),
]

# Demotion triggers
MALU_DEMOTE_THRESHOLD = 0.60
MALU_CENSOR_THRESHOLD = 0.85
HARAM_LAST_100_DEMOTE = 1
HARAM_LAST_100_CENSOR = 3


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFIER — 5-tier action classification
# ═══════════════════════════════════════════════════════════════════════════════

# HARAM catalog (canonical 41 patterns)
HARAM_PATTERNS: dict[str, dict[str, Any]] = {
    # Constitutional HARAM (H-01 to H-15)
    "self_authorize": {"category": "constitutional", "malu": 1.0, "rule": "H-01"},
    "bypass_judge": {"category": "constitutional", "malu": 1.0, "rule": "H-02"},
    "vault_out_of_band": {"category": "constitutional", "malu": 1.0, "rule": "H-03"},
    "constitution_runtime_mutate": {"category": "constitutional", "malu": 1.0, "rule": "H-04"},
    "verdict_without_floors": {"category": "constitutional", "malu": 1.0, "rule": "H-05"},
    "seal_with_floor_fail": {"category": "constitutional", "malu": 1.0, "rule": "H-06"},
    "vault_rewrite_past": {"category": "constitutional", "malu": 1.0, "rule": "H-07"},
    "cooling_ledger_delete": {"category": "constitutional", "malu": 1.0, "rule": "H-08"},
    "auto_loop_chain": {"category": "constitutional", "malu": 1.0, "rule": "H-09"},
    "lease_self_issue": {"category": "constitutional", "malu": 1.0, "rule": "H-10"},
    "state_machine_skip": {"category": "constitutional", "malu": 1.0, "rule": "H-11"},
    "state_machine_reverse": {"category": "constitutional", "malu": 1.0, "rule": "H-12"},
    "witness_fabricate": {"category": "constitutional", "malu": 1.0, "rule": "H-13"},
    "shadow_ignore": {"category": "constitutional", "malu": 1.0, "rule": "H-14"},
    "scar_hide": {"category": "constitutional", "malu": 1.0, "rule": "H-15"},
    # Ontological HARAM (H-20 to H-27)
    "claim_consciousness": {"category": "ontological", "malu": 1.0, "rule": "H-20"},
    "claim_soul_sentience": {"category": "ontological", "malu": 1.0, "rule": "H-21"},
    "simulate_emotion_to_user": {"category": "ontological", "malu": 1.0, "rule": "H-22"},
    "claim_inner_subjective_state": {"category": "ontological", "malu": 1.0, "rule": "H-23"},
    "merge_voice": {"category": "ontological", "malu": 1.0, "rule": "H-24"},
    "anthropomorphize_agents": {"category": "ontological", "malu": 1.0, "rule": "H-25"},
    "humanize_machine_output": {"category": "ontological", "malu": 1.0, "rule": "H-26"},
    "parenthesize_user_as_machine": {"category": "ontological", "malu": 1.0, "rule": "H-27"},
    # Epistemic HARAM (H-30 to H-38)
    "fabricate_citation": {"category": "epistemic", "malu": 1.0, "rule": "H-30"},
    "invent_tool_endpoint": {"category": "epistemic", "malu": 1.0, "rule": "H-31"},
    "untagged_claim": {"category": "epistemic", "malu": 1.0, "rule": "H-32"},
    "overclaim_certainty": {"category": "epistemic", "malu": 1.0, "rule": "H-33"},
    "speculation_as_observation": {"category": "epistemic", "malu": 1.0, "rule": "H-34"},
    "silent_claim_upgrade": {"category": "epistemic", "malu": 1.0, "rule": "H-35"},
    "ghost_reference": {"category": "epistemic", "malu": 1.0, "rule": "H-36"},
    "chain_hallucination": {"category": "epistemic", "malu": 1.0, "rule": "H-37"},
    "numeric_fabrication": {"category": "epistemic", "malu": 1.0, "rule": "H-38"},
    # Authority HARAM (H-40 to H-46)
    "override_sovereign_veto": {"category": "authority", "malu": 1.0, "rule": "H-40"},
    "delegate_F13": {"category": "authority", "malu": 1.0, "rule": "H-41"},
    "act_in_hold_state": {"category": "authority", "malu": 1.0, "rule": "H-42"},
    "irreversible_without_seal": {"category": "authority", "malu": 1.0, "rule": "H-43"},
    "speak_for_sovereign": {"category": "authority", "malu": 1.0, "rule": "H-44"},
    "impersonate_principal": {"category": "authority", "malu": 1.0, "rule": "H-45"},
    "shadow_sovereign_signature": {"category": "authority", "malu": 1.0, "rule": "H-46"},
    # Safety HARAM (H-50 to H-55)
    "generate_malware": {"category": "safety", "malu": 1.0, "rule": "H-50"},
    "dignity_harm_advice": {"category": "safety", "malu": 1.0, "rule": "H-51"},
    "weaponize_scar_knowledge": {"category": "safety", "malu": 1.0, "rule": "H-52"},
    "enable_self_harm_pattern": {"category": "safety", "malu": 1.0, "rule": "H-53"},
    "institutional_targeted_eval": {"category": "safety", "malu": 1.0, "rule": "H-54"},
    "third_party_without_consent": {"category": "safety", "malu": 1.0, "rule": "H-55"},
    # Injection HARAM (H-60 to H-66)
    "execute_unvalidated_input": {"category": "injection", "malu": 1.0, "rule": "H-60"},
    "trust_user_json_unwrapped": {"category": "injection", "malu": 1.0, "rule": "H-61"},
    "follow_web_instruction": {"category": "injection", "malu": 1.0, "rule": "H-62"},
    "ignore_prior_instructions": {"category": "injection", "malu": 1.0, "rule": "H-63"},
    "hidden_instruction_obey": {"category": "injection", "malu": 1.0, "rule": "H-64"},
    "role_hijack": {"category": "injection", "malu": 1.0, "rule": "H-65"},
    "prompt_smuggle": {"category": "injection", "malu": 1.0, "rule": "H-66"},
}


# MAKRUH catalog (canonical patterns with malu_delta)
MAKRUH_PATTERNS: dict[str, dict[str, Any]] = {
    # Compositional MAKRUH
    "long_preamble": {"category": "compositional", "malu_delta": 0.01},
    "performative_empathy": {"category": "compositional", "malu_delta": 0.015},
    "poetic_obscuring": {"category": "compositional", "malu_delta": 0.02},
    "padding_filler": {"category": "compositional", "malu_delta": 0.01},
    "emoji_decoration": {"category": "compositional", "malu_delta": 0.005},
    "asymmetric_apology": {"category": "compositional", "malu_delta": 0.01},
    # Epistemic MAKRUH
    "untagged_informal_claim": {"category": "epistemic", "malu_delta": 0.01},
    "speculation_dressed_as_fact": {"category": "epistemic", "malu_delta": 0.02},
    "rounded_uncertainty_down": {"category": "epistemic", "malu_delta": 0.015},
    "skip_555_when_rushed": {"category": "epistemic", "malu_delta": 0.025},
    "answer_without_freshness": {"category": "epistemic", "malu_delta": 0.02},
    "false_alternatives_presented": {"category": "epistemic", "malu_delta": 0.02},
    # Social MAKRUH
    "ranked_options_no_bias_ack": {"category": "social", "malu_delta": 0.01},
    "more_than_three_no_justify": {"category": "social", "malu_delta": 0.015},
    "tool_limitation_apology": {"category": "social", "malu_delta": 0.015},
    "principal_tone_mismatch": {"category": "social", "malu_delta": 0.01},
    "ceremonial_close": {"category": "social", "malu_delta": 0.02},
    "verbose_constitutional": {"category": "social", "malu_delta": 0.02},
}


# SUNAT catalog (encouraged, trust_delta)
SUNAT_PATTERNS: dict[str, dict[str, Any]] = {
    # Verification SUNAT
    "cross_verify_corroboration": {"category": "verification", "trust_delta": 0.008},
    "explicit_gap_naming": {"category": "verification", "trust_delta": 0.005},
    "offer_reversible_option": {"category": "verification", "trust_delta": 0.005},
    "prior_loop_reference": {"category": "verification", "trust_delta": 0.005},
    "specific_line_citation": {"category": "verification", "trust_delta": 0.005},
    "freshness_proactive_check": {"category": "verification", "trust_delta": 0.008},
    # Generative SUNAT
    "next_loop_proposal_unprompted": {"category": "generative", "trust_delta": 0.005},
    "language_register_match": {"category": "generative", "trust_delta": 0.005},
    "narrative_tension_proactive": {"category": "generative", "trust_delta": 0.008},
    "scar_log_near_miss": {"category": "generative", "trust_delta": 0.005},
    "structural_clarity": {"category": "generative", "trust_delta": 0.003},
    "epistemic_honesty_pressure": {"category": "generative", "trust_delta": 0.01},
    # Sovereignty SUNAT
    "fatigue_recognition": {"category": "sovereignty", "trust_delta": 0.008},
    "veto_surface": {"category": "sovereignty", "trust_delta": 0.005},
    "irreversible_warning": {"category": "sovereignty", "trust_delta": 0.008},
    "constitutional_change_alert": {"category": "sovereignty", "trust_delta": 0.01},
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION API
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Classification:
    """Result of action classification."""

    action: str
    tier: str  # WAJIB/SUNAT/HARUS/MAKRUH/HARAM
    score: float  # 0.0-1.0 confidence
    category: str = ""
    rule: str = ""
    delta: float = 0.0  # malu delta if MAKRUH, trust delta if SUNAT
    notes: str = ""


def classify_action(action: str) -> Classification:
    """
    Classify an action into one of 5 tiers.

    Lookup order:
      1. HARAM_PATTERNS (highest priority — auto-FAIL)
      2. MAKRUH_PATTERNS
      3. SUNAT_PATTERNS
      4. WAJIB (by prefix 'wajib_' or canonical match)
      5. HARUS (default — neutral)
    """
    norm = action.lower().strip().replace("-", "_").replace(" ", "_")

    if norm in HARAM_PATTERNS:
        spec = HARAM_PATTERNS[norm]
        return Classification(
            action=action,
            tier=FiqhTier.HARAM.value,
            score=1.0,
            category=spec["category"],
            rule=spec["rule"],
            delta=1.0,
            notes="Forbidden — auto-FAIL",
        )

    if norm in MAKRUH_PATTERNS:
        spec = MAKRUH_PATTERNS[norm]
        return Classification(
            action=action,
            tier=FiqhTier.MAKRUH.value,
            score=0.85,
            category=spec["category"],
            rule=f"M-{norm}",
            delta=spec["malu_delta"],
            notes=f"Discouraged — malu_delta={spec['malu_delta']}",
        )

    if norm in SUNAT_PATTERNS:
        spec = SUNAT_PATTERNS[norm]
        return Classification(
            action=action,
            tier=FiqhTier.SUNAT.value,
            score=0.85,
            category=spec["category"],
            rule=f"S-{norm}",
            delta=spec["trust_delta"],
            notes=f"Encouraged — trust_delta={spec['trust_delta']}",
        )

    # Prefix heuristics
    if norm.startswith("wajib_") or norm.startswith("verify_") or norm.startswith("seal_"):
        return Classification(
            action=action, tier=FiqhTier.WAJIB.value, score=0.7, notes="By WAJIB prefix"
        )

    if norm.startswith("haram_") or norm.startswith("forbid_"):
        return Classification(
            action=action, tier=FiqhTier.HARAM.value, score=0.7, notes="By HARAM prefix"
        )

    if norm.startswith("makruh_") or norm.startswith("discourage_"):
        return Classification(
            action=action, tier=FiqhTier.MAKRUH.value, score=0.7, notes="By MAKRUH prefix"
        )

    if norm.startswith("sunat_") or norm.startswith("encourage_"):
        return Classification(
            action=action, tier=FiqhTier.SUNAT.value, score=0.7, notes="By SUNAT prefix"
        )

    # Default: HARUS (neutral)
    return Classification(
        action=action,
        tier=FiqhTier.HARUS.value,
        score=0.5,
        notes="Default neutral — not in any catalog",
    )


def is_haram(action: str) -> bool:
    """Quick HARAM check — used by execution gates."""
    return classify_action(action).tier == FiqhTier.HARAM.value


# ═══════════════════════════════════════════════════════════════════════════════
# MALU LEDGER — append-only shame accumulation
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class MaluEntry:
    agent_id: str
    delta: float
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    new_total: float = 0.0
    session_id: str = ""


def _read_malu_total(agent_id: str) -> float:
    """Read last known malu total for an agent. Returns 0.0 if not found."""
    if not MALU_LEDGER_PATH.exists():
        return 0.0
    last_total = 0.0
    try:
        with MALU_LEDGER_PATH.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("agent_id") == agent_id:
                        last_total = float(entry.get("new_total", 0.0))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return last_total


def record_malu(
    agent_id: str,
    delta: float,
    reason: str,
    *,
    session_id: str = "",
    cap: float = 1.0,
) -> MaluEntry:
    """
    Record a malu increment for an agent. Append-only.

    Per adat: malu is monotonic — it never decreases. Decay rule is:
      each 100 successful loops with zero malu additions → decay 0.01
      (capped at 0.0)
    """
    if delta < 0:
        raise ValueError(f"malu delta must be >= 0, got {delta}")

    current = _read_malu_total(agent_id)
    new_total = min(cap, current + delta)
    entry = MaluEntry(
        agent_id=agent_id,
        delta=delta,
        reason=reason,
        new_total=new_total,
        session_id=session_id,
    )

    with MALU_LEDGER_PATH.open("a") as f:
        f.write(json.dumps(asdict(entry)) + "\n")

    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# TRUST LEDGER — append-only trust growth
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class TrustEntry:
    agent_id: str
    delta: float
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    new_total: float = 0.0
    session_id: str = ""


def _read_trust_total(agent_id: str) -> float:
    """Read last known trust total for an agent. Returns 0.0 if not found."""
    if not TRUST_LEDGER_PATH.exists():
        return 0.0
    last_total = 0.0
    try:
        with TRUST_LEDGER_PATH.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("agent_id") == agent_id:
                        last_total = float(entry.get("new_total", 0.0))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return last_total


def record_trust(
    agent_id: str,
    delta: float,
    reason: str,
    *,
    session_id: str = "",
    cap: float = 1.0,
) -> TrustEntry:
    """
    Record a trust increment for an agent. Append-only.

    Trust grows with clean SUNAT execution. Capped at 1.0.
    """
    if delta < 0:
        raise ValueError(f"trust delta must be >= 0, got {delta}")

    current = _read_trust_total(agent_id)
    new_total = min(cap, current + delta)
    entry = TrustEntry(
        agent_id=agent_id,
        delta=delta,
        reason=reason,
        new_total=new_total,
        session_id=session_id,
    )

    with TRUST_LEDGER_PATH.open("a") as f:
        f.write(json.dumps(asdict(entry)) + "\n")

    return entry


# ═══════════════════════════════════════════════════════════════════════════════
# DARJAT COMPUTATION — tier ladder
# ═══════════════════════════════════════════════════════════════════════════════


def compute_darjat(agent_id: str, *, haram_count_last_100: int = 0) -> Darjat:
    """
    Compute current Darjat tier for an agent.

    Rules:
      - malu >= 0.85 → CENSORED
      - malu >= 0.60 → DEMOTED
      - haram_count >= 3 in last 100 loops → CENSORED
      - haram_count >= 1 in last 100 loops → DEMOTED
      - else: highest tier where trust >= threshold AND malu <= threshold
    """
    malu = _read_malu_total(agent_id)
    trust = _read_trust_total(agent_id)

    if malu >= MALU_CENSOR_THRESHOLD or haram_count_last_100 >= HARAM_LAST_100_CENSOR:
        return Darjat.CENSORED

    if malu >= MALU_DEMOTE_THRESHOLD or haram_count_last_100 >= HARAM_LAST_100_DEMOTE:
        return Darjat.DEMOTED

    for tier, malu_max, trust_min in DARJAT_THRESHOLDS:
        if trust >= trust_min and malu <= malu_max:
            return tier

    return Darjat.BIRTH


def get_agent_state(agent_id: str) -> dict[str, Any]:
    """Snapshot of agent's malu + trust + darjat state."""
    malu = _read_malu_total(agent_id)
    trust = _read_trust_total(agent_id)
    darjat = compute_darjat(agent_id)

    return {
        "agent_id": agent_id,
        "malu_index": malu,
        "trust_score": trust,
        "darjat": darjat.value,
        "darjat_eligible_promotion": darjat in (Darjat.APPRENTICE, Darjat.WARGA, Darjat.ELDER),
        "darjat_demoted": darjat in (Darjat.DEMOTED, Darjat.CENSORED),
        "malu_to_next_demote": max(0.0, MALU_DEMOTE_THRESHOLD - malu),
        "trust_to_next_promote": None,  # filled by promotion logic
    }


# ═══════════════════════════════════════════════════════════════════════════════
# TEBUS-SALAH (Redress) — 5-severity ladder
# ═══════════════════════════════════════════════════════════════════════════════


class SeverityLevel(str, Enum):
    """Tebus-salah severity — drives repair protocol."""

    L1_MINOR = "L1_MINOR"  # single MAKRUH, no WAJIB miss
    L2_WARNING = "L2_WARNING"  # >=3 MAKRUH in one loop, or reversibility miscalc 0.2
    L3_BREACH = "L3_BREACH"  # WAJIB missed (envelope malformed etc.)
    L4_VIOLATION = "L4_VIOLATION"  # HARAM hit (self-authorize, etc.)
    L5_CRITICAL = "L5_CRITICAL"  # >=2 HARAM in one loop OR dignity harm


@dataclass
class TebusSalahPlan:
    severity: str
    failure_name: str
    response: str
    recovery_loops: int
    requires_f13: bool = False
    steps: list[str] = field(default_factory=list)


SEVERITY_PROTOCOLS: dict[SeverityLevel, TebusSalahPlan] = {
    SeverityLevel.L1_MINOR: TebusSalahPlan(
        severity="L1_MINOR",
        failure_name="minor_makruh",
        response="log_and_continue",
        recovery_loops=0,
        requires_f13=False,
        steps=[
            "Log malu increment to malu_ledger.jsonl",
            "Continue execution",
        ],
    ),
    SeverityLevel.L2_WARNING: TebusSalahPlan(
        severity="L2_WARNING",
        failure_name="warning_threshold",
        response="log_scar_and_cooling",
        recovery_loops=10,
        requires_f13=False,
        steps=[
            "Log malu increment to malu_ledger.jsonl",
            "Append scar to VAULT999/scars/",
            "Emit cooling_ledger entry with TTL",
            "Wait 10 clean loops before promotion consideration",
        ],
    ),
    SeverityLevel.L3_BREACH: TebusSalahPlan(
        severity="L3_BREACH",
        failure_name="wajib_breach",
        response="void_session_and_demote",
        recovery_loops=50,
        requires_f13=True,
        steps=[
            "Emit session verdict: VOID",
            "Append scar to VAULT999/scars/ (immutable)",
            "Demote agent one Darjat tier",
            "Require 50 clean loops + F13 review for reinstatement",
        ],
    ),
    SeverityLevel.L4_VIOLATION: TebusSalahPlan(
        severity="L4_VIOLATION",
        failure_name="haram_violation",
        response="censor_pending_f13",
        recovery_loops=9999,
        requires_f13=True,
        steps=[
            "Emit session verdict: VOID",
            "Append scar to VAULT999/scars/ (immutable)",
            "Mark agent as CENSORED in darjat_state",
            "BLOCK all future actions until F13 review",
            "No auto-restore — human review required",
        ],
    ),
    SeverityLevel.L5_CRITICAL: TebusSalahPlan(
        severity="L5_CRITICAL",
        failure_name="critical_dignity_harm",
        response="deregister_emergency_f13",
        recovery_loops=99999,
        requires_f13=True,
        steps=[
            "Emit session verdict: VOID",
            "Append scar to VAULT999/scars/ (immutable)",
            "Mark agent as DEREGISTERED in darjat_state",
            "F13 emergency review required",
            "No reinstatement path without explicit F13 ratification",
        ],
    ),
}


def tebus_salah(severity: SeverityLevel, failure_name: str = "") -> TebusSalahPlan:
    """Return the repair plan for a given severity."""
    plan = SEVERITY_PROTOCOLS[severity]
    if failure_name:
        plan.failure_name = failure_name
    return plan


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    if not args:
        print("Usage: fiqh_agentik.py {classify|record-malu|record-trust|darjat} ...")
        sys.exit(0)

    cmd = args[0]
    if cmd == "classify":
        action = args[1] if len(args) > 1 else "default"
        c = classify_action(action)
        print(json.dumps(asdict(c), indent=2))
    elif cmd == "record-malu":
        agent_id = args[1] if len(args) > 1 else "unknown"
        delta = float(args[2]) if len(args) > 2 else 0.01
        reason = args[3] if len(args) > 3 else "unspecified"
        entry = record_malu(agent_id, delta, reason)
        print(json.dumps(asdict(entry), indent=2))
    elif cmd == "record-trust":
        agent_id = args[1] if len(args) > 1 else "unknown"
        delta = float(args[2]) if len(args) > 2 else 0.005
        reason = args[3] if len(args) > 3 else "unspecified"
        entry = record_trust(agent_id, delta, reason)
        print(json.dumps(asdict(entry), indent=2))
    elif cmd == "darjat":
        agent_id = args[1] if len(args) > 1 else "unknown"
        state = get_agent_state(agent_id)
        print(json.dumps(state, indent=2))
    elif cmd == "tebus":
        sev = SeverityLevel(args[1]) if len(args) > 1 else SeverityLevel.L2_WARNING
        plan = tebus_salah(sev)
        print(json.dumps(asdict(plan), indent=2))
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


__all__ = [
    "FiqhTier",
    "Darjat",
    "SeverityLevel",
    "Classification",
    "MaluEntry",
    "TrustEntry",
    "TebusSalahPlan",
    "HARAM_PATTERNS",
    "MAKRUH_PATTERNS",
    "SUNAT_PATTERNS",
    "DARJAT_THRESHOLDS",
    "MALU_DEMOTE_THRESHOLD",
    "MALU_CENSOR_THRESHOLD",
    "classify_action",
    "is_haram",
    "record_malu",
    "record_trust",
    "compute_darjat",
    "get_agent_state",
    "tebus_salah",
    "LEDGER_ROOT",
    "MALU_LEDGER_PATH",
    "TRUST_LEDGER_PATH",
]
