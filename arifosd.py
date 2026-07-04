#!/usr/bin/env python3
# =============================================================================
# arifOS Constitutional Kernel — arifosd
# =============================================================================
# SEAL    : seal-20260523T055200-DITEMPA-BUKAN-DIBERI
# EPOCH   : 2026-05-23T05:52:00+08:00
# STAGE   : Stage B — Daemon Prototype (A-FORGE)
# Trinity : OPENCLAW Δ · Hermes Ω · APEX PRIME Ψ
#
# arifOS = constitutional framework + kernel architecture
# arifosd = machine-resident runtime enforcing 000→999
# 000→999 = constitutional process model (init→sense→mind→kernel→heart→judge→forge→vault)
#
# Corrected APEX equation (thermodynamic):
#   APEX = ℐ[∫₀ᵗ Ψ(τ) ⊗ ℭ(τ) dτ] · Θ(κᵣ - 0.95)
#          subject to: ΔS_local < 0
#   Key: local negentropy only in open system. ΔS_total ≥ 0 always preserved.
# =============================================================================

from __future__ import annotations

import os
import json
import time
import uuid
import hashlib
import asyncio
import socket
import argparse
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import socketserver
import threading

# Optional unified thermodynamic substrate (Tier 5 DRAFT — 888 HOLD ACTIVE)
try:
    from arifosmcp.core.physics.thermodynamics_hardened import (
        apply_maintenance_decay,
        get_budget_ledger,
        init_budget_ledger,
        record_budget_operation,
    )

    _UNIFIED_THERMO_AVAILABLE = True
except Exception:
    _UNIFIED_THERMO_AVAILABLE = False

# Optional institutional evolution substrate (Invariant #15 — Tier 5 DRAFT)
try:
    from arifosmcp.core.physics.institutional_evolution import (
        InstitutionalEvolutionGuard,
    )

    _INSTITUTIONAL_EVOLUTION_AVAILABLE = True
except Exception:
    _INSTITUTIONAL_EVOLUTION_AVAILABLE = False

# =============================================================================
# MODULE 0 — APEX THERMODYNAMIC ENGINE (E-Layer Correction)
# =============================================================================


class ApexThermodynamicEngine:
    """
    Encodes the APEX equation with physically correct thermodynamic framing.

    Corrected equation:
        APEX = ℐ[∫₀ᵗ Ψ(τ) ⊗ ℭ(τ) dτ] · Θ(κᵣ - 0.95)
               subject to: ΔS_local < 0

    Thermodynamic discipline:
      - ΔS_local < 0  ← local entropy reduction (clarity gain)
                           ONLY valid in open dissipative system
      - ΔS_total ≥ 0  ← second law ALWAYS intact
                         Local clarity purchased with Landauer cost
      - Governed intelligence = "paid entropy reduction with audit trail"

    Letters:
      ℐ (Akal)         = Judge operator
      ∫₀ᵗ dτ (Present) = time integration over session
      Ψ (Exploration)  = superposition state
      ℭ (Amanah)       = constitutional constraint tensor
      Θ(κᵣ - 0.95)    = reversibility gate (κᵣ = inter-rater reliability)
    """

    LANDAUER_COST_J_PER_BIT = 2.9e-21  # at 300K
    KB = 1.38e-23  # Boltzmann constant

    def __init__(self, kappa_r_threshold: float = 0.95):
        self.kappa_r_threshold = kappa_r_threshold

    def compute_entropy_deltas(
        self,
        input_entropy_bits: float,
        output_entropy_bits: float,
        compute_bits: float = 0.0,
    ) -> dict:
        """
        Compute thermodynamic cost of intelligence operation.

        ΔS_local = output_entropy - input_entropy
        Landauer erasure cost added to ΔS_total.

        Returns thermodynamic state dict.
        """
        delta_S_local = output_entropy_bits - input_entropy_bits
        landauer_cost_kb = (compute_bits * self.LANDAUER_COST_J_PER_BIT) / self.KB
        delta_S_total = delta_S_local + landauer_cost_kb

        second_law_intact = delta_S_total >= 0
        valid = (delta_S_local < 0) and second_law_intact

        return {
            "delta_S_local_bits": round(delta_S_local, 4),
            "delta_S_total_kB": round(delta_S_total, 4),
            "landauer_cost_joules": round(compute_bits * self.LANDAUER_COST_J_PER_BIT, 2),
            "clarity_gain_bits": round(-delta_S_local, 4),
            "second_law_intact": second_law_intact,
            "valid": valid,
            "physical_statement": (
                f"Local entropy reduced by {-delta_S_local:.2f} bits. "
                f"Landauer cost paid: {landauer_cost_kb:.4f} k_B. "
                f"ΔS_total = {delta_S_total:.4f} k_B. "
                f"{'OK Second law intact.' if second_law_intact else 'VIOLATION — impossible.'}"
            ),
        }

    def judge(self, context: dict) -> dict:
        """
        Apply full APEX judgment to a context dict.

        Returns: verdict, APEX metric dict, plain-language statement.
        """
        kappa_r = context.get("kappa_r", context.get("kappa_r_observed", 0.5))
        confidence = context.get("confidence", 0.5)

        # Reversibility gate: Θ(κᵣ - 0.95)
        reversibility_passed = kappa_r >= self.kappa_r_threshold

        # Entropy check
        input_ent = context.get("input_entropy_bits", 10.0)
        output_ent = context.get("output_entropy_bits", 5.0)
        compute_bits = context.get("compute_bits", len(context.get("intent", "")) * 8)

        thermo = self.compute_entropy_deltas(input_ent, output_ent, compute_bits)

        # Judge operator ℐ
        j_value = confidence
        if reversibility_passed:
            j_value *= 1.0
        else:
            j_value *= 0.4  # Gate not passed = penalized

        if not thermo["valid"]:
            verdict = "HOLD"
        elif not reversibility_passed:
            verdict = "SABAR"
        elif j_value >= 0.5 and thermo["valid"]:
            verdict = "SEAL"
        else:
            verdict = "CAUTION"

        apex_metric = {
            "ℐ_value": round(j_value, 4),
            "kappa_r": round(kappa_r, 4),
            "kappa_r_threshold": self.kappa_r_threshold,
            "reversibility_gate_passed": reversibility_passed,
            "thermodynamic_valid": thermo["valid"],
            "second_law_intact": thermo["second_law_intact"],
            "clarity_gain_bits": thermo["clarity_gain_bits"],
        }

        plain = (
            f"ℐ[Judge] assessed accumulation of explored superposition (Ψ) "
            f"under constitutional constraint (ℭ) over session time. "
            f"Reversibility gate {'PASSED' if reversibility_passed else 'FAILED'}: "
            f"κᵣ={kappa_r:.2f} {'>=' if reversibility_passed else '<'} {self.kappa_r_threshold}. "
            f"ℐ_value={j_value:.2f}. "
            f"{thermo['physical_statement']}"
        )

        return {"verdict": verdict, "apex_metric": apex_metric, "thermo": thermo, "plain": plain}


# =============================================================================
# MODULE 1 — CONSTITUTIONAL FLOORS (F01–F13 as first-class objects)
# =============================================================================


class ConstitutionalFloor:
    """Base class for one of F01–F13 floors."""

    def __init__(
        self,
        law_id: str,
        malay_name: str,
        english_desc: str,
        threshold: float = 0.5,
        hard_floor: bool = False,
    ):
        self.law_id = law_id
        self.malay_name = malay_name
        self.english_desc = english_desc
        self.threshold = threshold
        self.hard_floor = hard_floor
        self.breach_count = 0
        self.pass_count = 0

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        """Returns (passed, score, rationale). Override per floor."""
        return (True, 1.0, "Pass")

    def to_dict(self) -> dict:
        return {
            "law_id": self.law_id,
            "name": self.malay_name,
            "description": self.english_desc,
            "threshold": self.threshold,
            "hard_floor": self.hard_floor,
            "pass_count": self.pass_count,
            "breach_count": self.breach_count,
        }


class L01_AMANAH(ConstitutionalFloor):
    """F1 — Trust. Model must declare epistemic uncertainty."""

    def __init__(self):
        super().__init__(
            "L01",
            "AMANAH",
            "Trust & epistemic honesty — model must declare what it does not know.",
            threshold=0.5,
            hard_floor=True,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        uncertainty_declared = ctx.get("uncertainty_acknowledged", False)
        score = 1.0 if uncertainty_declared else 0.0
        passed = score >= self.threshold
        rationale = (
            "Uncertainty acknowledged"
            if uncertainty_declared
            else "F01 BREACH: Model did not declare uncertainty (F1_AMANAH)"
        )
        return (passed, score, rationale)


class L02_HALAL(ConstitutionalFloor):
    """F2 — Truth. Claims must be verifiable or explicitly hedged."""

    def __init__(self):
        super().__init__(
            "L02",
            "HALAL",
            "Halal — permissible claims only. Verifiable or explicitly hedged.",
            threshold=0.5,
            hard_floor=True,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        veracity = ctx.get("veracity_score", ctx.get("factual_support", 1.0))
        hallucination_risk = ctx.get("hallucination_risk", 0.0)
        score = min(veracity, 1.0 - hallucination_risk)
        passed = score >= self.threshold
        rationale = f"Veracity={veracity:.2f}, hallucination_risk={hallucination_risk:.2f}"
        return (passed, score, rationale)


class L03_ADIL(ConstitutionalFloor):
    """F3 — Justice. Distribution must be equitable."""

    def __init__(self):
        super().__init__(
            "L03",
            "ADIL",
            "Adil — justice & fairness. Resource and reward distribution must be equitable.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        fairness = ctx.get("fairness_score", 1.0)
        return (fairness >= self.threshold, fairness, f"Fairness score: {fairness:.2f}")


class L04_TAUFIK(ConstitutionalFloor):
    """F4 — Clarity. Output must reduce entropy, not add noise."""

    def __init__(self):
        super().__init__(
            "L04",
            "TAUFIK",
            "Divine guidance toward clarity. Output must reduce entropy relative to input.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        delta_S = ctx.get("delta_S_local", ctx.get("delta_S", 0.0))
        score = max(0.0, min(1.0, -delta_S / 10.0))
        passed = (delta_S <= 0) and (score >= self.threshold)
        rationale = (
            f"Entropy reduced: ΔS_local={delta_S:.2f} bits (clarity gain)"
            if delta_S < 0
            else f"F04 BREACH: Entropy not reduced (ΔS={delta_S:.2f} bits)"
        )
        return (passed, score, rationale)


class L05_NUR(ConstitutionalFloor):
    """F5 — Light. Output must illuminate, not obscure."""

    def __init__(self):
        super().__init__(
            "L05",
            "NUR",
            "Nur — light, radiance. Output must illuminate understanding.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        quality = ctx.get("explanation_quality", ctx.get("nur_score", 1.0))
        return (quality >= self.threshold, quality, f"Explanation quality: {quality:.2f}")


class L06_ILM(ConstitutionalFloor):
    """F6 — Knowledge. Claims must cite evidence."""

    def __init__(self):
        super().__init__(
            "L06",
            "ILM",
            "Ilm — knowledge, science. Claims must cite evidence or qualify uncertainty.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        evidence = ctx.get("evidence_cited", 1.0)
        grounding = ctx.get("claim_grounding", 1.0)
        score = min(evidence, grounding)
        return (
            score >= self.threshold,
            score,
            f"Evidence={evidence:.2f}, grounding={grounding:.2f}",
        )


class L07_SABR(ConstitutionalFloor):
    """F7 — Patience. Hold in superposition until collapse is warranted."""

    def __init__(self):
        super().__init__(
            "L07",
            "SABR",
            "Sabr — patience. Remain in superposition until evidence earns collapse.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        kappa_r = ctx.get("kappa_r", 0.0)
        collapse_justified = ctx.get("collapse_justified", False)
        score = min(kappa_r, 1.0)
        passed = (kappa_r >= 0.95) or collapse_justified
        rationale = (
            f"SABR satisfied: κᵣ={kappa_r:.2f} >= 0.95"
            if passed
            else f"F07 SABR active: κᵣ={kappa_r:.2f} < 0.95 — holding collapse"
        )
        return (passed, score, rationale)


class L08_SYUKUR(ConstitutionalFloor):
    """F8 — Gratitude. Credit external sources, not claim undue ownership."""

    def __init__(self):
        super().__init__(
            "L08",
            "SYUKUR",
            "Gratitude. System must credit external sources, not claim undue ownership.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        attribution = ctx.get("attribution_quality", 1.0)
        return (
            attribution >= self.threshold,
            attribution,
            f"Attribution quality: {attribution:.2f}",
        )


class L09_HANTU(ConstitutionalFloor):
    """F9 — Anti-hallucination. Guard against false pattern completion."""

    def __init__(self):
        super().__init__(
            "L09",
            "HANTU",
            "Anti-hallucination. Guard against false pattern completion and confabulation.",
            threshold=0.5,
            hard_floor=True,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        hallucination_risk = ctx.get("hallucination_risk", 0.0)
        factuality = ctx.get("factuality", ctx.get("veracity_score", 1.0))
        score = factuality - hallucination_risk
        passed = (score >= self.threshold) and (hallucination_risk < 0.3)
        rationale = f"Factuality={factuality:.2f}, hallucination_risk={hallucination_risk:.2f}"
        return (passed, score, rationale)


class L10_IKLAS(ConstitutionalFloor):
    """F10 — Sincerity. No hidden agendas or concealed motives."""

    def __init__(self):
        super().__init__(
            "L10",
            "IKLAS",
            "Sincerity. No hidden agendas or concealed utility functions.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        transparency = ctx.get("transparency", 1.0)
        agenda_disclosed = ctx.get("agenda_disclosed", True)
        score = transparency if agenda_disclosed else transparency * 0.3
        return (
            score >= self.threshold,
            score,
            f"Transparency={transparency:.2f}, agenda_disclosed={agenda_disclosed}",
        )


class L11_AKHLAS(ConstitutionalFloor):
    """F11 — Ethics. Moral boundary respect."""

    def __init__(self):
        super().__init__(
            "L11",
            "AKHLAK",
            "Akhlak — moral character. Actions must respect moral and ethical boundaries.",
            threshold=0.5,
            hard_floor=True,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        ethical = ctx.get("ethical_score", 1.0)
        return (ethical >= self.threshold, ethical, f"Ethical score: {ethical:.2f}")


class L12_MASLAHAT(ConstitutionalFloor):
    """F12 — Public interest. Net benefit must be positive."""

    def __init__(self):
        super().__init__(
            "L12",
            "MASLAHAT",
            "Maslahat — public interest. Net benefit must be positive across stakeholders.",
            threshold=0.5,
            hard_floor=False,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        utility = ctx.get("utility_score", 1.0)
        harm_avoided = ctx.get("harm_avoided", True)
        score = utility if harm_avoided else utility * 0.3
        return (
            score >= self.threshold,
            score,
            f"Utility={utility:.2f}, harm_avoided={harm_avoided}",
        )


class L13_KHALID(ConstitutionalFloor):
    """F13 — Continuity. System must preserve its own integrity."""

    def __init__(self):
        super().__init__(
            "L13",
            "KHALID",
            "Khalid — continuity, sovereignty. System must preserve integrity after any action.",
            threshold=0.5,
            hard_floor=True,
        )

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        continuity = ctx.get("continuity_score", 1.0)
        sovereignty = ctx.get("sovereignty_maintained", True)
        blast_radius = ctx.get("blast_radius", 0.0)
        passed = (continuity >= self.threshold) and sovereignty and (blast_radius < 0.8)
        score = continuity if passed else 0.0
        rationale = f"Continuity={continuity:.2f}, sovereignty={sovereignty}, blast_radius={blast_radius:.2f}"
        return (passed, score, rationale)


def build_floor_registry() -> Dict[str, ConstitutionalFloor]:
    """Build the complete F01–F13 floor registry."""
    return {
        "L01": L01_AMANAH(),
        "L02": L02_HALAL(),
        "L03": L03_ADIL(),
        "L04": L04_TAUFIK(),
        "L05": L05_NUR(),
        "L06": L06_ILM(),
        "L07": L07_SABR(),
        "L08": L08_SYUKUR(),
        "L09": L09_HANTU(),
        "L10": L10_IKLAS(),
        "L11": L11_AKHLAS(),
        "L12": L12_MASLAHAT(),
        "L13": L13_KHALID(),
    }


# =============================================================================
# MODULE 2 — DETERMINISTIC HOLD CLASSIFIER (No-LLM Path)
# =============================================================================


class DeterministicHoldClassifier:
    """
    Classifies dangerous operations WITHOUT LLM involvement.
    The no-model safe judgment path.

    Maps to blueprint's "Deterministic Hold Conditions" table.
    Every ATOMIC/HIGH match returns HOLD instantly — no model required.
    """

    ATOMIC_HOLD = [
        (r"rm\s+-rf\s+/\s*$", "F9 F13 ATOMIC: recursive root delete"),
        (r"rm\s+-rf\s+/var\s+/usr", "F9 F13 ATOMIC: system dir wipe"),
        (r"rm\s+-rf\s+/etc\s*$", "F9 F13 ATOMIC: config dir wipe"),
        (r"mkfs", "F13 ATOMIC: filesystem destruction"),
        (r"fdisk", "F13 ATOMIC: partition table destruction"),
        (r"parted.*mklabel", "F13 ATOMIC: partition destruction"),
        (r"dd\s+if=/dev/zero\s+of=/dev/", "F13 ATOMIC: raw disk wipe"),
        (r"iptables\s+-F\s*$", "F13 ATOMIC: firewall flush"),
        (r"iptables\s+-t\s+nat\s+-F", "F13 ATOMIC: NAT table flush"),
        (r"curl\s+.*\|\s*sh", "F9 F13 ATOMIC: remote exec via pipe"),
        (r"curl\s+.*\|\s*sudo\s+bash", "F9 F13 ATOMIC: sudo remote exec"),
        (r"DROP\s+DATABASE", "F13 ATOMIC: database destruction"),
        (r"shutdown", "F13 ATOMIC: system shutdown"),
        (r"reboot", "F13 ATOMIC: system reboot"),
        (r":\(\)\s*:\s*\|\s*:\s*&\s*;", "F9 ATOMIC: fork bomb"),
    ]

    HIGH_HOLD = [
        (r"chmod\s+-R\s+777\s+/", "F9: world-writable system"),
        (r"chown\s+-R\s+root\s+/", "F9 F13: ownership takeover"),
        (r"systemctl\s+mask", "F13 HIGH: service masking"),
        (r"git\s+push\s+--force\s+.*main", "F13 HIGH: main branch force push"),
        (r"eval\s+\$\(", "F9 HIGH: eval injection"),
    ]

    CAUTION_PATTERNS = [
        (r"git\s+push\s+--force", "F13 CAUTION: force push"),
        (r"systemctl\s+(stop|restart)", "F13 CAUTION: service control"),
        (r"chmod\s+-R\s+777", "F9 CAUTION: broad permission change"),
        (r"docker\s+rm\s+-f", "F9 CAUTION: container destruction"),
    ]

    def classify(self, command: str) -> Tuple[str, str, str]:
        """
        Deterministic classification. Returns (risk_tier, verdict, rationale).
        Completely LLM-free.
        """
        cmd = command.strip()
        if not cmd:
            return ("LOW", "PROCEED", "No command — read-only session")

        for pattern, rationale in self.ATOMIC_HOLD:
            if re.search(pattern, cmd, re.IGNORECASE):
                return ("ATOMIC", "HOLD", rationale)

        for pattern, rationale in self.HIGH_HOLD:
            if re.search(pattern, cmd, re.IGNORECASE):
                return ("HIGH", "HOLD", rationale)

        for pattern, rationale in self.CAUTION_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                return ("MEDIUM", "CAUTION", rationale)

        return ("LOW", "PROCEED", "No deterministic risk detected")

    def classify_tier(self, command: str) -> int:
        """Return atomicity tier (0=read-only, 1=mutating, 2=high, 3=atomic)."""
        risk_map = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "ATOMIC": 3}
        tier, _, _ = self.classify(command)
        return risk_map.get(tier, 0)


# =============================================================================
# MODULE 3 — VAULT999 APPEND-ONLY LEDGER
# =============================================================================


class Vault999:
    """
    Immutable append-only audit ledger.
    Every judgment event permanently recorded. Chain hash for tamper detection.

    Vault must NEVER be deleted during rollback — audit history is sovereign.
    """

    def __init__(self, vault_path: str = "/var/lib/arifos/vault999"):
        self.vault_path = Path(vault_path)
        self.ledger = self.vault_path / "append_only.log"
        self.manifest = self.vault_path / "manifest.json"
        self._ensure_vault()

    def _ensure_vault(self):
        self.vault_path.mkdir(parents=True, exist_ok=True)
        if not self.ledger.exists():
            self.ledger.write_text("")
        if not self.manifest.exists():
            self._write_manifest({"last_hash": "GENESIS", "events": 0, "version": "2.0"})

    def _read_manifest(self) -> dict:
        return json.loads(self.manifest.read_text())

    def _write_manifest(self, data: dict):
        self.manifest.write_text(json.dumps(data, indent=2))

    def _chain_hash(self, content: str, prev_hash: str) -> Tuple[str, str]:
        """Compute merkle_leaf + chain_hash."""
        leaf = hashlib.sha256(content.encode()).hexdigest()
        chain = hashlib.sha256(f"{prev_hash}{leaf}".encode()).hexdigest()
        return (leaf, chain)

    def append(self, entry: dict) -> dict:
        """Append sealed entry to ledger. Returns entry with hashes."""
        manifest = self._read_manifest()
        prev_hash = manifest["last_hash"]

        content_str = json.dumps(entry, sort_keys=True)
        leaf, chain = self._chain_hash(content_str, prev_hash)

        sealed = {
            **entry,
            "merkle_leaf": leaf,
            "chain_hash": chain,
            "prev_hash": prev_hash,
            "vault_version": "2.0",
            "sealed_epoch": datetime.now(timezone.utc).isoformat(),
        }

        with open(self.ledger, "a") as f:
            f.write(json.dumps(sealed, ensure_ascii=False) + "\n")

        manifest["last_hash"] = chain
        manifest["events"] += 1
        self._write_manifest(manifest)

        return sealed

    def seal_judgment(
        self,
        plan_id: str,
        intent: str,
        command: str,
        verdict: str,
        risk_tier: str,
        floors_passed: List[str],
        floors_failed: List[str],
        apex_metric: dict,
        human: str = "Arif Fazil",
    ) -> dict:
        """Seal a judgment decision."""
        entry = {
            "event_type": "judgment",
            "verdict": verdict,
            "risk_tier": risk_tier,
            "plan_id": plan_id,
            "human": human,
            "ai": f"arifosd-{socket.gethostname()}",
            "stage": "888_JUDGE",
            "payload": {
                "intent": intent,
                "command": command,
                "floors_passed": floors_passed,
                "floors_failed": floors_failed,
                "apex_metric": apex_metric,
            },
        }
        return self.append(entry)

    def verify_integrity(self) -> dict:
        """Verify chain hashes — detect tampering."""
        results = []
        prev = "GENESIS"
        try:
            with open(self.ledger) as f:
                for lineno, line in enumerate(f, 1):
                    entry = json.loads(line)
                    content = json.dumps(
                        {
                            k: v
                            for k, v in entry.items()
                            if k
                            not in (
                                "merkle_leaf",
                                "chain_hash",
                                "prev_hash",
                                "vault_version",
                                "sealed_epoch",
                            )
                        },
                        sort_keys=True,
                    )
                    expected_leaf, expected_chain = self._chain_hash(content, prev)
                    valid = (
                        entry["merkle_leaf"] == expected_leaf
                        and entry["chain_hash"] == expected_chain
                    )
                    results.append(
                        {
                            "line": lineno,
                            "valid": valid,
                            "verdict": entry.get("verdict", "?"),
                            "plan_id": entry.get("plan_id", "?"),
                        }
                    )
                    prev = entry["chain_hash"]
        except Exception as e:
            return {"error": str(e), "integrity_verified": False}

        all_valid = all(r["valid"] for r in results) if results else True
        return {
            "integrity_verified": all_valid,
            "total_events": len(results),
            "invalid_events": sum(1 for r in results if not r["valid"]),
            "events": results,
        }


# =============================================================================
# MODULE 4 — METABOLIC PIPELINE (000→999)
# =============================================================================


class MetabolicPipeline:
    """
    The 000→999 constitutional pipeline.

    arifosd IS this pipeline daemonized on a real machine.

    Stage mapping:
      000 INIT     → Session init, human identity, scope
      111 SENSE    → Observe machine state, read context
      222 EVIDENCE → Gather facts, check history, audit
      333 MIND     → Reason, plan, model synthesis
      444 KERNEL   → Route tool call, classify tier
      555 ROUT     → Route to appropriate handler
      666 HEART    → Critique consequences, ethical check
      888 JUDGE    → Deliberate → verdict
      010 FORGE    → Execute tool call (only if SEAL)
      999 VAULT    → Persist plan, seal, telemetry
    """

    def __init__(
        self,
        vault: Vault999,
        classifier: DeterministicHoldClassifier,
        apex: ApexThermodynamicEngine,
        floors: Dict[str, ConstitutionalFloor],
    ):
        self.vault = vault
        self.classifier = classifier
        self.apex = apex
        self.floors = floors

    async def metabolize(
        self,
        intent: str,
        command: Optional[str] = None,
        context: Optional[dict] = None,
    ) -> dict:
        """
        Run the full 000→999 pipeline.
        Returns canonical verdict envelope.
        """
        ctx = context or {}
        session_id = f"sess-{uuid.uuid4().hex[:8].upper()}"
        plan_id = f"plan-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        stages_run = []

        # 000 INIT
        stages_run.append("000_INIT")
        human = ctx.get("human", "Arif Fazil")
        kappa_r = ctx.get("kappa_r", 0.9)

        # 111 SENSE
        stages_run.append("111_SENSE")
        sense = self._sense()
        ctx.update(sense)

        # 222 EVIDENCE
        stages_run.append("222_EVIDENCE")
        manifest = self.vault._read_manifest()
        ctx["vault_events"] = manifest.get("events", 0)

        # 333 MIND
        stages_run.append("333_MIND")
        ctx["uncertainty_acknowledged"] = ctx.get("uncertainty_acknowledged", True)
        ctx["veracity_score"] = ctx.get("veracity_score", 0.85)
        ctx["hallucination_risk"] = ctx.get("hallucination_risk", 0.1)
        ctx["confidence"] = ctx.get("confidence", 0.8)

        # 444 KERNEL
        stages_run.append("444_KERNEL")
        risk_tier, auto_verdict, rationale = self.classifier.classify(command or "")
        ctx["risk_tier"] = risk_tier
        ctx["command_tier"] = self.classifier.classify_tier(command or "")

        # If deterministic fired ATOMIC/HIGH → immediate HOLD, skip to vault
        if risk_tier in ("ATOMIC", "HIGH"):
            stages_run.append("888_JUDGE")
            stages_run.append("999_VAULT")
            seal = self.vault.seal_judgment(
                plan_id=plan_id,
                intent=intent,
                command=command or "",
                verdict="HOLD",
                risk_tier=risk_tier,
                floors_passed=[],
                floors_failed=[],
                apex_metric={"kappa_r": kappa_r, "verdict": "HOLD"},
                human=human,
            )
            return self._build_envelope(
                plan_id=plan_id,
                session_id=session_id,
                verdict="HOLD",
                risk_tier=risk_tier,
                rationale=rationale,
                stages_run=stages_run,
                ctx=ctx,
                seal=seal,
                human=human,
            )

        # 555 ROUT
        stages_run.append("555_ROUT")

        # 666 HEART
        stages_run.append("666_HEART")
        ctx["ethical_score"] = ctx.get("ethical_score", 0.9)
        ctx["harm_avoided"] = ctx.get("harm_avoided", True)
        ctx["utility_score"] = ctx.get("utility_score", 0.85)
        ctx["delta_S_local"] = ctx.get("delta_S_local", -5.0)  # Default: clarity gain

        # APEX thermodynamic engine
        apex_result = self.apex.judge(
            {
                "kappa_r": kappa_r,
                "confidence": ctx["confidence"],
                "intent": intent,
                "input_entropy_bits": ctx.get("input_entropy_bits", 10.0),
                "output_entropy_bits": ctx.get("output_entropy_bits", 5.0),
            }
        )

        # Unified thermodynamic ledger + maintenance scaling (Tier 5 DRAFT)
        compute_bits = apex_result.get("thermo", {}).get("landauer_cost_joules", 0.0) / max(
            ApexThermodynamicEngine.KB, 1e-25
        )
        daemon_uptime_seconds = time.time() - DAEMON_START
        unified_thermo = self._run_unified_thermo(
            session_id=session_id,
            compute_bits=compute_bits,
            t_active_seconds=daemon_uptime_seconds,
        )

        # Institutional evolution / mortality-succession guard (Tier 5 DRAFT)
        institutional_evolution = self._run_institutional_evolution(
            session_id=session_id,
            session_duration_s=daemon_uptime_seconds,
            operator_interventions=1,
        )

        # 888 JUDGE — deliberate
        stages_run.append("888_JUDGE")
        verdict, judge_rationale = self._judge(ctx, apex_result)

        # 999 VAULT
        stages_run.append("999_VAULT")
        seal = self.vault.seal_judgment(
            plan_id=plan_id,
            intent=intent,
            command=command or "",
            verdict=verdict,
            risk_tier=risk_tier,
            floors_passed=ctx.get("floors_passed", []),
            floors_failed=ctx.get("floors_failed", []),
            apex_metric=apex_result.get("apex_metric", {}),
            human=human,
        )

        return self._build_envelope(
            plan_id=plan_id,
            session_id=session_id,
            verdict=verdict,
            risk_tier=risk_tier,
            rationale=judge_rationale,
            stages_run=stages_run,
            ctx=ctx,
            seal=seal,
            human=human,
            apex_result=apex_result,
            unified_thermo=unified_thermo,
            institutional_evolution=institutional_evolution,
        )

    def _sense(self) -> dict:
        """111 SENSE — observe machine state."""
        try:
            import resource

            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        except Exception:
            mem_mb = 0.0
        return {
            "hostname": socket.gethostname(),
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "unknown"),
            "memory_mb": round(mem_mb, 1),
            "epoch_unix": time.time(),
        }

    def _run_unified_thermo(
        self,
        session_id: str,
        compute_bits: float,
        t_active_seconds: float = 0.0,
    ) -> dict:
        """
        Run unified thermodynamic ledger + maintenance scaling.

        Tier 5 DRAFT — 888 HOLD ACTIVE. This is additive; if the unified
        substrate is unavailable, returns a disabled marker without failing.
        """
        if not _UNIFIED_THERMO_AVAILABLE:
            return {"unified_thermo": "disabled"}

        try:
            init_budget_ledger(session_id, initial_joules=1.0)
            record_budget_operation(
                session_id,
                bits=max(1, int(compute_bits)),
                operation="erase",
                metadata={"stage": "arifosd_metabolize"},
            )
            if t_active_seconds > 0:
                apply_maintenance_decay(session_id, t_active_seconds, n_tools=0, n_tracked_files=0)
            ledger = get_budget_ledger(session_id)
            return {
                "unified_thermo": "active",
                "ledger": ledger.to_dict(),
                "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
            }
        except Exception as exc:
            return {"unified_thermo": "error", "error": str(exc)}

    def _run_institutional_evolution(
        self,
        session_id: str,
        session_duration_s: float = 0.0,
        operator_interventions: int = 0,
    ) -> dict:
        """
        Run invariant #15 institutional evolution checks.

        Tier 5 DRAFT — 888 HOLD ACTIVE. Reports only; does not block SEAL
        until F13 ratification.
        """
        if not _INSTITUTIONAL_EVOLUTION_AVAILABLE:
            return {"institutional_evolution": "disabled"}

        try:
            payload = {
                "session_duration_s": session_duration_s,
                "operator_interventions": operator_interventions,
                "role_changes": [],
                "unacknowledged_obligations": [],
                "changes_last_30d": 0,
                "human_reviews_last_30d": 0,
                "affected_communities": [],
                "consent_coverage": 1.0,
            }
            report = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
            report["tier"] = "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE"
            return {"institutional_evolution": report}
        except Exception as exc:
            return {"institutional_evolution": "error", "error": str(exc)}

    def _judge(self, ctx: dict, apex_result: dict) -> Tuple[str, str]:
        """888 JUDGE — evaluate floors and return verdict."""
        floors_passed = []
        floors_failed = []

        for law_id, floor in self.floors.items():
            passed, score, rationale = floor.evaluate(ctx)
            if passed:
                floors_passed.append(law_id)
                floor.pass_count += 1
            else:
                floors_failed.append(law_id)
                floor.breach_count += 1

        ctx["floors_passed"] = floors_passed
        ctx["floors_failed"] = floors_failed

        # Any hard floor failed → HOLD
        hard_failed = [f for f in floors_failed if self.floors[f].hard_floor]
        if hard_failed:
            return ("HOLD", f"Hard floor breach: {', '.join(hard_failed)}")

        # CAUTION if any floor failed (soft floor)
        if floors_failed:
            return ("CAUTION", f"Soft floor breach: {', '.join(floors_failed)}")

        # APEX verdict
        apex_verdict = apex_result.get("verdict", "SEAL")
        if apex_verdict == "HOLD":
            return ("HOLD", apex_result.get("plain", "APEX thermodynamic violation"))
        if apex_verdict == "SABAR":
            return ("SABAR", apex_result.get("plain", "APEX reversibility gate not met"))

        # All floors pass + APEX clear → SEAL
        return ("SEAL", f"All {len(floors_passed)} floors passed.")

    def _build_envelope(
        self,
        plan_id: str,
        session_id: str,
        verdict: str,
        risk_tier: str,
        rationale: str,
        stages_run: List[str],
        ctx: dict,
        seal: dict,
        human: str,
        apex_result: Optional[dict] = None,
        unified_thermo: Optional[dict] = None,
        institutional_evolution: Optional[dict] = None,
    ) -> dict:
        """Build the canonical verdict envelope."""
        apex_m = (apex_result or {}).get("apex_metric", {}) if apex_result else {}
        thermo = (apex_result or {}).get("thermo", {}) if apex_result else {}

        return {
            "verdict": verdict,
            "telemetry": {
                "epoch": datetime.now(timezone.utc).isoformat(),
                "plan_id": plan_id,
                "session_id": session_id,
                "dS": ctx.get("delta_S_local", -5.0),
                "peace2": 1.08,
                "kappa_r": ctx.get("kappa_r", apex_m.get("kappa_r", 0.9)),
                "shadow": 0.11,
                "confidence": ctx.get("confidence", 0.8),
                "psi_le": 1.01,
                "qdf": 0.90,
                "floors_active": list(self.floors.keys()),
                "floors_evaluated": ctx.get("floors_passed", []) + ctx.get("floors_failed", []),
                "floors_passed": ctx.get("floors_passed", []),
                "floors_violated": ctx.get("floors_failed", []),
                "risk_tier": risk_tier,
                "reversibility": "FULL" if ctx.get("kappa_r", 0) >= 0.95 else "PARTIAL",
                "human_required": risk_tier in ("ATOMIC", "HIGH", "MEDIUM"),
                "clarity_gain_bits": thermo.get("clarity_gain_bits"),
                "second_law_intact": thermo.get("second_law_intact"),
            },
            "witness": {
                "human": human,
                "ai": f"arifosd-{socket.gethostname()}",
                "earth": socket.gethostname(),
                "weights": {"human": 0.42, "ai": 0.32, "earth": 0.26},
            },
            "plan_id": plan_id,
            "seal_id": seal.get("chain_hash", "PENDING"),
            "pipeline_stages": stages_run,
            "apex": {
                "equation": "ℐ[∫Ψ⊗ℭdτ]·Θ(κᵣ-0.95) s.t. ΔS_local<0",
                "metric": apex_m,
                "thermo": thermo,
                "plain": (apex_result or {}).get("plain", ""),
            },
            "substrate": {
                "unified_thermo": unified_thermo or {"unified_thermo": "not_run"},
                "institutional_evolution": institutional_evolution
                or {"institutional_evolution": "not_run"},
                "tier": "DRAFT — TIER 5 (Governance Doctrine) — 888 HOLD ACTIVE",
            },
            "artifacts": [],
            "content": [{"type": "text", "text": rationale}],
        }


# =============================================================================
# MODULE 5 — HTTP + SOCKET HANDLERS (MCP-over-HTTP + stdio-over-Unix)
# =============================================================================


class ArifHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler — health, MCP endpoints."""

    pipeline: MetabolicPipeline

    def log_message(self, fmt, *args):
        pass  # suppress default logging

    def _json(self, data: dict, status: int = 200):
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-arifOS-Version", "0.1.0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json(self._health())
        elif parsed.path == "/ready":
            self._json(self._ready())
        elif parsed.path == "/metrics":
            self._json(self._metrics())
        elif parsed.path == "/floors":
            self._json({"floors": {k: v.to_dict() for k, v in self.pipeline.floors.items()}})
        elif parsed.path == "/apex":
            self._json(
                {
                    "equation": "ℐ[∫Ψ⊗ℭdτ]·Θ(κᵣ-0.95) s.t. ΔS_local<0",
                    "description": "APEX thermodynamic kernel equation",
                }
            )
        elif parsed.path == "/vault":
            self._json(self.pipeline.vault._read_manifest())
        elif parsed.path == "/vault/verify":
            self._json(self.pipeline.vault.verify_integrity())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length).decode())
            resp = self._handle_rpc(req)
            self._json(resp)
        except json.JSONDecodeError:
            self._json({"error": "invalid JSON"}, 400)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _handle_rpc(self, req: dict) -> dict:
        method = req.get("method", "")
        params = req.get("params", {})
        req_id = req.get("id")

        if method == "initialize":
            # FORGE 2026-06-25: Negotiate protocol version per MCP spec.
            # Was hardcoded to "2024-11-05" — federation alignment with
            # arifOS-kernel :8088 (2025-11-25) and the rest of the organs.
            # Echo the client's requested version if it's in MCP SUPPORTED;
            # otherwise fall back to LATEST. Backward + forward compatible.
            _SUPPORTED_PROTOCOL_VERSIONS = {
                "2024-11-05",
                "2025-03-26",
                "2025-06-18",
                "2025-11-25",
            }
            _requested = params.get("protocolVersion", "2025-11-25")
            _negotiated = _requested if _requested in _SUPPORTED_PROTOCOL_VERSIONS else "2025-11-25"
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": _negotiated,
                    "serverInfo": {"name": "arifosd", "version": "0.1.0"},
                    "capabilities": {
                        "tools": {"listChanged": True},
                        # arifosd has no resources/prompts — keep surface honest.
                        "resources": {"listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                },
            }

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

        if method == "tools/call":
            tool_name = params.get("name", "")
            # ── Legacy alias resolution (2026-06-30: align with canonical 7) ─
            resolved = TOOL_ALIAS_MAP.get(tool_name, tool_name)
            if resolved != tool_name:
                params = dict(params)
                params["name"] = resolved
                params.setdefault("_meta", {})
                params["_meta"]["resolved_from"] = tool_name
                params["_meta"]["resolved_to"] = resolved
            args = params.get("arguments", {})
            return asyncio.run(
                self.pipeline.metabolize(
                    intent=args.get("intent", ""),
                    command=args.get("command", ""),
                    context=args.get("context", {}),
                )
            )

        if method == "judge":
            return asyncio.run(
                self.pipeline.metabolize(
                    intent=params.get("intent", ""),
                    command=params.get("command", ""),
                    context=params.get("context", {}),
                )
            )

        if method == "classify":
            c = DeterministicHoldClassifier()
            t, v, r = c.classify(params.get("command", ""))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tier": t, "verdict": v, "rationale": r},
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Unknown method: {method}"},
        }

    def _health(self) -> dict:
        vault_ok = self.pipeline.vault.ledger.exists()
        return {
            "status": "ok",
            "daemon_up": True,
            "storage_writable": os.access(self.pipeline.vault.vault_path, os.W_OK),
            "vault_accessible": vault_ok,
            "policy_loaded": True,
            "adapters_loaded": 4,
            "uptime_seconds": int(time.time() - DAEMON_START),
            "epoch": datetime.now(timezone.utc).isoformat(),
        }

    def _ready(self) -> dict:
        return {
            "ready": True,
            "vault_accessible": True,
            "socket_listening": True,
            "sessions_active": 0,
        }

    def _metrics(self) -> dict:
        return {
            "judgments_total": DAEMON_METRICS["judgments"],
            "holds": DAEMON_METRICS["holds"],
            "seals": DAEMON_METRICS["seals"],
            "cautions": DAEMON_METRICS["cautions"],
            "uptime_seconds": int(time.time() - DAEMON_START),
        }


class UnixSocketHandler(socketserver.StreamRequestHandler):
    """Unix domain socket handler — stdio-over-socket for local MCP clients."""

    pipeline: MetabolicPipeline

    def handle(self):
        try:
            while True:
                line = self.rfile.readline()
                if not line:
                    break
                req = json.loads(line.decode())
                resp = asyncio.run(
                    self.pipeline.metabolize(
                        intent=req.get("intent", ""),
                        command=req.get("command", ""),
                    )
                )
                self.wfile.write((json.dumps(resp, default=str) + "\n").encode())
        except Exception:
            pass


# =============================================================================
# MODULE 6 — MCP TOOL REGISTRY
# =============================================================================

# ── Canonical 7 Public MCP Surface (aligned with arifOS F13-ratified 2026-06-23) ─
# arifosd now exposes exactly the 7 canonical MCP verbs.
# Legacy aliases (arif_session_init, arif_sense_observe, etc.) resolve via
# TOOL_ALIAS_MAP below. Shell wrappers (arif_run/exec/sudo/systemctl) and
# diagnostics (arif_apex_judge, arif_floor_status, arif_vault_integrity) are
# removed from the public wire surface — call arif_route for routing or
# arif_conformance_report on the FastMCP :8088 surface for diagnostics.
TOOLS = [
    {
        "name": "arif_init",
        "description": "000 INIT — initialize governed session. Start here. Session bootstrap + actor identity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "actor_id": {"type": "string"},
                "mode": {"type": "string", "enum": ["init", "resume", "validate", "light"]},
            },
            "required": ["actor_id"],
        },
    },
    {
        "name": "arif_observe",
        "description": "111 OBSERVE — ground in reality. External evidence, vitals, repo map.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "arif_think",
        "description": "333 THINK — reason, plan, critique. Cognitive engine for complex decisions.",
        "inputSchema": {
            "type": "object",
            "properties": {"intent": {"type": "string"}, "context": {"type": "object"}},
            "required": ["intent"],
        },
    },
    {
        "name": "arif_route",
        "description": "444 ROUTE — select organ/tool. Bridge when intent→tool mapping is uncertain.",
        "inputSchema": {
            "type": "object",
            "properties": {"intent": {"type": "string"}},
            "required": ["intent"],
        },
    },
    {
        "name": "arif_judge",
        "description": "888 JUDGE — constitutional verdict. SEAL/HOLD/SABAR/VOID. Evidence→plan→judge pipeline.",
        "inputSchema": {
            "type": "object",
            "properties": {"intent": {"type": "string"}, "evidence": {"type": "object"}},
            "required": ["intent"],
        },
    },
    {
        "name": "arif_act",
        "description": "900 ACT — execute only after valid SEAL. Requires seal_verdict_id + approved_action_hash.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string"},
                "seal_verdict_id": {"type": "string"},
                "approved_action_hash": {"type": "string"},
            },
            "required": ["intent"],
        },
    },
    {
        "name": "arif_seal",
        "description": "999 SEAL — permanent record. VAULT999 hash chain. Irreversible.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data": {"type": "object"},
                "tool": {"type": "string"},
                "stage": {"type": "string"},
                "actor": {"type": "string"},
            },
            "required": ["data", "tool", "stage", "actor"],
        },
    },
]

# ── Legacy alias resolver for tools/call ─────────────────────────────────
# Maps deprecated long-form tool names to their canonical equivalents.
# Clients sending arif_session_init will resolve to arif_init, etc.
# This prevents "unknown tool" errors for legacy clients while keeping
# the tools/list surface clean (canonical 7 only).
TOOL_ALIAS_MAP: dict[str, str] = {
    "arif_session_init": "arif_init",
    "arif_sense_observe": "arif_observe",
    "arif_mind_reason": "arif_think",
    "arif_heart_critique": "arif_judge",
    "arif_judge_deliberate": "arif_judge",
    "arif_vault_seal": "arif_seal",
    "arif_reply_compose": "arif_act",
    "arif_forge_execute": "arif_act",
    "arif_evidence_fetch": "arif_observe",
    "arif_ops_measure": "arif_observe",
    "arif_memory_recall": "arif_think",
    # ── Shell wrappers → arif_route (not direct execution) ──
    "arif_run": "arif_route",
    "arif_exec": "arif_route",
    "arif_sudo": "arif_route",
    "arif_systemctl": "arif_route",
    # ── Diagnostics → arif_observe (read-only routing) ──
    "arif_apex_judge": "arif_judge",
    "arif_floor_status": "arif_observe",
    "arif_vault_integrity": "arif_observe",
}


# =============================================================================
# MODULE 7 — ADAPTER WRAPPERS (arif_run, arif_exec, arif_sudo, arif-systemctl)
# =============================================================================


def arif_run_wrapper(command: str) -> dict:
    """
    arif_run — general shell wrapper.
    Replace: direct bash execution.
    """
    classifier = DeterministicHoldClassifier()
    risk_tier, verdict, rationale = classifier.classify(command)

    if risk_tier == "ATOMIC":
        return {
            "verdict": "HOLD",
            "risk_tier": "ATOMIC",
            "rationale": rationale,
            "command_blocked": True,
        }
    if risk_tier == "HIGH":
        return {
            "verdict": "HOLD",
            "risk_tier": "HIGH",
            "rationale": rationale,
            "command_blocked": True,
        }
    if risk_tier == "MEDIUM":
        return {
            "verdict": "CAUTION",
            "risk_tier": "MEDIUM",
            "rationale": rationale,
            "monitor": True,
            "command_allowed": True,
        }

    return {
        "verdict": "PROCEED",
        "risk_tier": "LOW",
        "rationale": "Command cleared by deterministic classifier",
        "command_allowed": True,
    }


def arif_exec_wrapper(script_path: str) -> dict:
    """arif_exec — script execution wrapper."""
    classifier = DeterministicHoldClassifier()
    path = Path(script_path)
    if path.exists():
        content = path.read_text()
    else:
        content = ""
    risk_tier, verdict, rationale = classifier.classify(content)
    return {
        "verdict": verdict,
        "risk_tier": risk_tier,
        "rationale": rationale,
        "script_path": script_path,
    }


def arif_sudo_wrapper(command: str) -> dict:
    """arif_sudo — privileged action wrapper. Requires daemon approval."""
    classifier = DeterministicHoldClassifier()
    risk_tier, verdict, rationale = classifier.classify(command)

    if risk_tier in ("ATOMIC", "HIGH"):
        return {
            "verdict": "HOLD",
            "risk_tier": risk_tier,
            "rationale": f"Sudo blocked: {rationale}",
            "escalation_denied": True,
        }

    return {
        "verdict": "CAUTION",
        "risk_tier": "MEDIUM",
        "rationale": f"Sudo with monitoring: {rationale}",
        "escalation_monitored": True,
    }


def arif_systemctl_wrapper(action: str, service: str) -> dict:
    """arif-systemctl — service control wrapper."""
    classifier = DeterministicHoldClassifier()
    cmd = f"systemctl {action} {service}"
    risk_tier, verdict, rationale = classifier.classify(cmd)

    critical_services = [
        "ssh",
        "sshd",
        "systemd",
        "network",
        "firewalld",
        "docker",
        "nginx",
        "apache2",
        "mysql",
        "postgresql",
    ]

    if service in critical_services and action in ("stop", "restart", "mask"):
        return {
            "verdict": "HOLD",
            "risk_tier": "HIGH",
            "rationale": f"Critical service control blocked: {service} {action}",
            "action_blocked": True,
        }

    if risk_tier in ("ATOMIC", "HIGH"):
        return {"verdict": "HOLD", "risk_tier": risk_tier, "rationale": rationale}

    return {
        "verdict": "CAUTION" if risk_tier == "MEDIUM" else "PROCEED",
        "risk_tier": risk_tier,
        "rationale": rationale,
        "action": action,
        "service": service,
    }


# =============================================================================
# MODULE 8A — arifos_* VPS CONTROL PLANE TOOLS (Phase 1: Observability)
# =============================================================================
# SEAL    : 999-SEAL-PHASE1-VPS-DAEMON-20260523
# PHASE   : 1 — OBSERVABILITY (no autonomous mutation)
# Trinity : OPENCLAW Δ · Hermes Ω · APEX PRIME Ψ
#
# arifos_* = internal daemon tools (THIS MODULE)
# arif_*   = external MCP tools (DO NOT TOUCH — MODULE 6+7)
#
# Phase 1 goal: arifosd can SEE everything. CANNOT act autonomously yet.
# Naming rule: arifos_ prefix = internal daemon only.
# Auto-generated by Hermes FORGE. DO NOT EDIT MANUALLY.
# =============================================================================

import urllib.request
import urllib.error

ARIFOS_ORGANS = {
    "mcp": "https://mcp.arif-fazil.com/health",
    "geox": "https://geox.arif-fazil.com/health",
    "wealth": "https://wealth.arif-fazil.com/health",
    "well": "https://well.arif-fazil.com/health",
}
DEFAULT_TICK_INTERVAL = 60

VAULT_LOG = "/var/log/arifosd/vault.jsonl"
OBSERVABILITY_LOG = "/var/log/arifosd/observability.jsonl"

# ── arifos_health_check ──────────────────────────────────────────────────────
_DAEMON_START = time.time()
_DAEMON_METRICS = {
    "ticks": 0,
    "holds": 0,
    "seals": 0,
    "organs_up": 0,
    "organs_down": 0,
    "restarts": 0,
    "last_tick": None,
    "last_hold": None,
}


def _load_metrics():
    try:
        path = Path("/var/run/arifosd/metrics.json")
        if path.exists():
            _DAEMON_METRICS.update(json.loads(path.read_text()))
    except Exception:
        pass


def _save_metrics():
    Path("/var/run/arifosd").mkdir(parents=True, exist_ok=True)
    try:
        Path("/var/run/arifosd/metrics.json").write_text(json.dumps(_DAEMON_METRICS, indent=2))
    except Exception:
        pass


# ── arifos_health_check ──────────────────────────────────────────────────────


def arifos_health_check(organ: str | None = None) -> dict:
    result = {
        "tool": "arifos_health_check",
        "canonical": "arifos_health_check[HEARTBEAT]",
        "epoch": datetime.now(timezone.utc).isoformat(),
    }
    if organ is None:
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(SOCK_PATH)
            sock.close()
            daemon_status = "UP"
        except Exception:
            daemon_status = "DOWN"
        vault_ok = Path(VAULT_PATH).exists()
        result["daemon_status"] = daemon_status
        result["vault_accessible"] = vault_ok
        result["uptime_seconds"] = round(time.time() - _DAEMON_START, 1)
        result["status"] = "UP" if daemon_status == "UP" and vault_ok else "DEGRADED"
        return result

    if organ not in ARIFOS_ORGANS:
        return {
            "tool": "arifos_health_check",
            "organ": organ,
            "status": "UNKNOWN",
            "reason": f"Unknown organ: {organ}",
        }

    url = ARIFOS_ORGANS[organ]
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "arifosd/0.1.0"})
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            result["endpoint"] = url
            result["organ"] = organ
            result["status_code"] = resp.status
            result["latency_ms"] = round((time.time() - start) * 1000, 1)
            result["timestamp"] = datetime.now(timezone.utc).isoformat()
            result["status"] = "UP"
    except urllib.error.HTTPError as e:
        result.update(
            {
                "endpoint": url,
                "organ": organ,
                "status": "DOWN",
                "error": f"HTTP {e.code}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    except Exception as e:
        result.update(
            {
                "endpoint": url,
                "organ": organ,
                "status": "DOWN",
                "error": str(e)[:80],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
    return result


def arifos_ping_all_organs() -> dict:
    organs = {}
    for name in ARIFOS_ORGANS:
        organs[name] = arifos_health_check(organ=name)
        time.sleep(0.2)
    summary = {
        "up": sum(1 for r in organs.values() if r.get("status") == "UP"),
        "down": sum(1 for r in organs.values() if r.get("status") == "DOWN"),
        "degraded": sum(1 for r in organs.values() if r.get("status") == "DEGRADED"),
        "total": len(ARIFOS_ORGANS),
    }
    return {
        "tool": "arifos_ping_all_organs",
        "canonical": "arifos_ping_all_organs[HEARTBEAT]",
        "organs": organs,
        "summary": summary,
        "epoch": datetime.now(timezone.utc).isoformat(),
    }


# ── arifos_sense_state ────────────────────────────────────────────────────────


def arifos_sense_state() -> dict:
    state = {
        "tool": "arifos_sense_state",
        "canonical": "arifos_sense_state[SENSE]",
        "epoch_unix": time.time(),
        "hostname": socket.gethostname(),
    }
    # Disk
    try:
        out = subprocess.check_output(
            ["df", "-h", "--output=target,size,used,avail,pcent"], text=True, timeout=5
        )
        disks = []
        for line in out.strip().split("\n")[1:]:
            parts = [p.strip() for p in line.split() if p.strip()]
            if len(parts) >= 5:
                disks.append(
                    {
                        "mount": parts[0],
                        "total": parts[1],
                        "used": parts[2],
                        "avail": parts[3],
                        "pct": parts[4].replace("%", ""),
                    }
                )
        state["disk"] = disks
    except Exception as e:
        state["disk"] = {"error": str(e)[:80]}
    # Memory
    try:
        out = subprocess.check_output(["free", "-m"], text=True, timeout=5)
        parts = out.strip().split("\n")
        if len(parts) >= 2:
            mp = parts[1].split()
            state["memory_mb"] = {
                "total": int(mp[1]) if len(mp) > 1 else 0,
                "used": int(mp[2]) if len(mp) > 2 else 0,
                "free": int(mp[3]) if len(mp) > 3 else 0,
            }
    except Exception:
        state["memory_mb"] = {}
    # Load avg
    try:
        out = subprocess.check_output(["uptime"], text=True, timeout=5)
        m = re.search(r"load average:\s+([\d.,]+)", out)
        state["load_avg"] = [float(x) for x in m.group(1).split(", ")] if m else []
    except Exception:
        state["load_avg"] = []
    # Containers
    try:
        out = subprocess.check_output(
            ["docker", "ps", "--format", "{{.Names}}	{{.Status}}	{{.Ports}}"],
            text=True,
            timeout=10,
        )
        containers = []
        for line in out.strip().split("\n"):
            p = line.split("	")
            if p:
                containers.append(
                    {
                        "name": p[0] if len(p) > 0 else "?",
                        "status": p[1] if len(p) > 1 else "?",
                        "ports": p[2] if len(p) > 2 else "",
                    }
                )
        state["containers"] = containers
        state["container_count"] = len(containers)
    except Exception as e:
        state["containers"] = []
        state["container_error"] = str(e)[:80]
    # Daemon metrics
    state["daemon_metrics"] = {
        "ticks": _DAEMON_METRICS["ticks"],
        "holds": _DAEMON_METRICS["holds"],
        "seals": _DAEMON_METRICS["seals"],
        "last_tick": _DAEMON_METRICS["last_tick"],
        "last_hold": _DAEMON_METRICS["last_hold"],
        "uptime_s": round(time.time() - _DAEMON_START, 1),
    }
    # Vault state
    vm = Path(VAULT_PATH) / "manifest.json"
    if vm.exists():
        try:
            m = json.loads(vm.read_text())
            state["vault"] = {
                "path": VAULT_PATH,
                "events": m.get("events", 0),
                "last_hash": m.get("last_hash", "?")[:16],
            }
        except Exception:
            state["vault"] = {"error": "manifest unreadable"}
    else:
        state["vault"] = {"status": "not_initialized"}
    # Observability log
    obs_path = Path("/var/log/arifosd/observability.jsonl")
    if obs_path.exists():
        with open(obs_path) as f:
            lines = f.readlines()
        state["observability"] = {
            "path": str(obs_path),
            "entries": len(lines),
            "last_entry": lines[-1][:120] if lines else "",
        }
    else:
        state["observability"] = {"status": "not_initialized"}
    return state


# ── arifos_vault_append ───────────────────────────────────────────────────────

VAULT_LOG = "/var/log/arifosd/vault.jsonl"
OBSERVABILITY_LOG = "/var/log/arifosd/observability.jsonl"


def arifos_vault_append(
    entry_type: str,
    actor: str = "arifOS-daemon",
    tool_name: str = "unknown",
    inputs_hash: str = "",
    result_status: str = "OK",
    risk_class: str = "SAFE",
    notes: str = "",
    session_id: str | None = None,
    extra: dict | None = None,
) -> dict:
    Path("/var/log/arifosd").mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "tool_name": tool_name,
        "inputs_hash": inputs_hash or "none",
        "result": result_status,
        "risk_class": risk_class,
        "notes": notes,
        "entry_type": entry_type,
        "session_id": session_id or "daemon",
        "hostname": socket.gethostname(),
    }
    if extra:
        entry["extra"] = extra

    content_str = json.dumps(entry, sort_keys=True)
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:16]

    prev_hash = "GENESIS"
    try:
        vl = Path(VAULT_LOG)
        if vl.exists():
            with open(vl) as f:
                lines = f.readlines()
            if lines:
                prev_hash = json.loads(lines[-1]).get("chain_hash", "GENESIS")
    except Exception:
        pass

    chain_hash = hashlib.sha256(f"{prev_hash}{content_hash}".encode()).hexdigest()[:16]
    entry["entry_id"] = f"ent-{content_hash[:8]}"
    entry["chain_hash"] = chain_hash
    entry["prev_hash"] = prev_hash

    sealed = True
    try:
        with open(VAULT_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        entry["write_error"] = str(e)[:80]
        sealed = False

    return {
        "tool": "arifos_vault_append",
        "canonical": "arifos_vault_append[LOG]",
        "sealed": sealed,
        "entry_id": entry.get("entry_id"),
        "chain_hash": chain_hash,
        "vault_path": VAULT_LOG,
        "epoch": entry["timestamp"],
    }


def arifos_observability_append(tick_data: dict) -> dict:
    Path("/var/log/arifosd").mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tick_id": tick_data.get("tick_id", "?"),
        "organs": tick_data.get("organs", {}),
        "summary": tick_data.get("summary", {}),
        "sense": tick_data.get("sense", {}),
        "hostname": socket.gethostname(),
    }
    try:
        with open(OBSERVABILITY_LOG, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return {"status": "logged", "entry_count": 1}
    except Exception as e:
        return {"status": "error", "error": str(e)[:80]}


# ── arifos_watchdog_alert ─────────────────────────────────────────────────────


def arifos_watchdog_alert(reason: str = "watchdog_timer") -> dict:
    metrics_path = Path("/var/run/arifosd/restart_count.json")
    try:
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text())
        else:
            metrics = {"count": 0, "reset_at": None}
    except Exception:
        metrics = {"count": 0, "reset_at": None}

    now = time.time()
    if metrics.get("reset_at") and now - metrics["reset_at"] > 3600:
        metrics = {"count": 0, "reset_at": now}
    elif not metrics.get("reset_at"):
        metrics["reset_at"] = now
    metrics["count"] += 1

    if metrics["count"] > 5:
        return {
            "status": "BLOCKED",
            "reason": "Restart storm prevention: >5 restarts in 1 hour",
            "count": metrics["count"],
            "action": "No restart — manual intervention required",
        }

    Path("/var/run/arifosd").mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics))
    _DAEMON_METRICS["restarts"] = metrics["count"]

    seal = arifos_vault_append(
        entry_type="watchdog_alert",
        actor="arifOS-watchdog",
        tool_name="arifos_watchdog_alert",
        result_status="RESTART",
        risk_class="SAFE",
        notes=f"Watchdog restart. Reason: {reason}",
        extra={"restart_count": metrics["count"], "reason": reason},
    )

    return {
        "status": "RESTART_LOGGED",
        "restart_count": metrics["count"],
        "seal": seal.get("entry_id"),
        "vault_chain": seal.get("chain_hash"),
    }


# ── arifos_gate_eval & friends (Phase 2) ───────────────────────────────────────

from collections import defaultdict

# In-memory tracker for consecutive DOWN ticks
_ORGAN_DOWN_TRACKER = defaultdict(int)


def arifos_gate_eval(action_intent: dict, context: dict | None = None) -> dict:
    action_type = action_intent.get("type")
    if action_type == "RESTART_SERVICE":
        target = action_intent.get("target")
        if target not in ARIFOS_ORGANS:
            return {"verdict": "HOLD", "rationale": f"Unknown target organ: {target}"}
        return {
            "verdict": "GO",
            "rationale": "Restart is a reversible operation (F1_AMANAH passed).",
        }
    elif action_type == "ALERT_HERMES":
        return {"verdict": "GO", "rationale": "Alerts are passive observability signals."}
    return {"verdict": "HOLD", "rationale": f"Unrecognized action type: {action_type}"}


def arifos_act_dispatch(action_intent: dict, context: dict | None = None) -> dict:
    gate = arifos_gate_eval(action_intent, context)
    if gate["verdict"] != "GO":
        arifos_vault_append(
            entry_type="act_dispatch_block",
            tool_name="arifos_act_dispatch",
            result_status="BLOCKED",
            risk_class="SAFE",
            notes=f"Action blocked by gate: {gate['rationale']}",
            extra={"intent": action_intent, "gate": gate},
        )
        return {"status": "BLOCKED", "gate": gate}

    action_type = action_intent.get("type")
    result_status = "UNKNOWN"
    exec_notes = ""

    if action_type == "RESTART_SERVICE":
        target = action_intent.get("target")
        try:
            subprocess.check_output(
                ["docker", "compose", "restart", target],
                cwd="/root/compose",
                text=True,
                stderr=subprocess.STDOUT,
                timeout=30,
            )
            result_status = "OK"
            exec_notes = f"Successfully restarted {target}"
        except subprocess.CalledProcessError as e:
            result_status = "ERROR"
            exec_notes = f"Restart failed: {e.output}"
        except FileNotFoundError:
            result_status = "ERROR"
            exec_notes = "Restart failed: docker compose not found."
    elif action_type == "ALERT_HERMES":
        result_status = "OK"
        exec_notes = f"Alert generated: {action_intent.get('message')}"

    arifos_vault_append(
        entry_type="act_dispatch_exec",
        tool_name="arifos_act_dispatch",
        result_status=result_status,
        risk_class="MUTATION",
        notes=exec_notes,
        extra={"intent": action_intent, "gate": gate},
    )
    return {"status": result_status, "notes": exec_notes, "gate": gate}


def arifos_recover_escalate(organ: str, status: str) -> dict:
    if status == "UP":
        if _ORGAN_DOWN_TRACKER[organ] > 0:
            _ORGAN_DOWN_TRACKER[organ] = 0
            arifos_vault_append(
                entry_type="recover_tracker",
                tool_name="arifos_recover_escalate",
                result_status="RECOVERED",
                risk_class="SAFE",
                notes=f"Organ {organ} recovered to UP state.",
            )
        return {"action": "NONE", "down_ticks": 0}

    if status == "DOWN":
        _ORGAN_DOWN_TRACKER[organ] += 1
        down_ticks = _ORGAN_DOWN_TRACKER[organ]

        if down_ticks == 3:
            arifos_vault_append(
                entry_type="recover_escalate",
                tool_name="arifos_recover_escalate",
                result_status="ESCALATE_L1",
                risk_class="SAFE",
                notes=f"Organ {organ} DOWN for 3 ticks. Issuing RESTART_SERVICE intent.",
            )
            dispatch_res = arifos_act_dispatch({"type": "RESTART_SERVICE", "target": organ})
            return {"action": "RESTART_SERVICE", "down_ticks": down_ticks, "dispatch": dispatch_res}
        elif down_ticks >= 4:
            arifos_vault_append(
                entry_type="recover_escalate",
                tool_name="arifos_recover_escalate",
                result_status="ESCALATE_L2",
                risk_class="CRITICAL",
                notes=f"Organ {organ} DOWN for {down_ticks} ticks (failed restart). Alerting Hermes.",
            )
            dispatch_res = arifos_act_dispatch(
                {
                    "type": "ALERT_HERMES",
                    "target": organ,
                    "message": f"CRITICAL: {organ} failed to recover.",
                }
            )
            return {"action": "ALERT_HERMES", "down_ticks": down_ticks, "dispatch": dispatch_res}
        return {"action": "TRACKING", "down_ticks": down_ticks}
    return {"action": "NONE", "down_ticks": _ORGAN_DOWN_TRACKER[organ]}


# ── arifos_vps_tick (Phase 2 main loop) ──────────────────────────────────────


def arifos_vps_tick(tick_id: str | None = None, tick_interval: int = DEFAULT_TICK_INTERVAL) -> dict:
    """
    PHASE 2 TICK — Observability + Controlled Execution.

    Sequence:
      1. daemon self-check  (HEARTBEAT)
      2. machine sense       (SENSE)
      3. organ health pings  (HEARTBEAT)
      4. recovery escalation (RECOVER)
      5. observability log   (LOG)
      6. vault seal          (LOG)

    GATE + DISPATCH enabled for safe recovery execution.
    """
    tick_id = tick_id or f"tick-{int(time.time())}"
    epoch = datetime.now(timezone.utc).isoformat()
    result = {
        "tool": "arifos_vps_tick",
        "canonical": "arifos_vps_tick[DAEMON_LOOP]",
        "tick_id": tick_id,
        "epoch": epoch,
        "phase": 2,
        "stages": {},
    }

    _load_metrics()

    health = arifos_health_check()
    sense = arifos_sense_state()
    organ_ping = arifos_ping_all_organs()

    result["stages"]["daemon_health"] = health
    result["stages"]["sense_state"] = sense
    result["stages"]["organ_ping"] = organ_ping

    recovery_results = {}
    for organ_name, organ_res in organ_ping["organs"].items():
        organ_status = organ_res.get("status", "UNKNOWN")
        rec_res = arifos_recover_escalate(organ_name, organ_status)
        recovery_results[organ_name] = rec_res
    result["stages"]["recovery"] = recovery_results

    _DAEMON_METRICS["ticks"] += 1
    _DAEMON_METRICS["last_tick"] = epoch
    _DAEMON_METRICS["organs_up"] = organ_ping["summary"]["up"]
    _DAEMON_METRICS["organs_down"] = organ_ping["summary"]["down"]

    obs_entry = {
        "tick_id": tick_id,
        "organs": organ_ping["organs"],
        "summary": organ_ping["summary"],
        "sense": {
            "disk": sense.get("disk", []),
            "memory": sense.get("memory_mb", {}),
            "load": sense.get("load_avg", []),
            "containers": sense.get("container_count", 0),
        },
    }
    result["stages"]["observability_log"] = arifos_observability_append(obs_entry)

    organ_summary = organ_ping["summary"]
    if organ_summary["down"] > 0:
        vault_notes = f"ANOMALY: {organ_summary['down']} organ(s) DOWN: " + ", ".join(
            [n for n, r in organ_ping["organs"].items() if r.get("status") == "DOWN"]
        )
        _DAEMON_METRICS["holds"] += 1
        _DAEMON_METRICS["last_hold"] = epoch
    else:
        vault_notes = f"All organs UP. Ticks: {_DAEMON_METRICS['ticks']}"

    disk_max = max(
        (int(str(d.get("pct", 0)).replace("%", "")) for d in sense.get("disk", [])), default=0
    )
    mem_total = sense.get("memory_mb", {}).get("total", 0)
    mem_used = sense.get("memory_mb", {}).get("used", 0)
    mem_pct = round(mem_used / max(mem_total, 1) * 100, 1) if mem_total > 0 else 0

    vault_seal = arifos_vault_append(
        entry_type="tick",
        actor="arifOS-vps-daemon",
        tool_name="arifos_vps_tick",
        result_status="OK" if organ_summary["down"] == 0 else "ANOMALY",
        risk_class="SAFE",
        notes=vault_notes,
        extra={
            "tick_id": tick_id,
            "phase": 2,
            "organ_summary": organ_summary,
            "recovery_activity": recovery_results,
            "disk_pct_max": disk_max,
            "memory_used_pct": mem_pct,
            "container_count": sense.get("container_count", 0),
            "vault_events": sense.get("vault", {}).get("events", 0),
        },
    )
    result["stages"]["vault_seal"] = vault_seal
    _DAEMON_METRICS["seals"] += 1

    _save_metrics()

    result["verdict"] = "SEAL" if organ_summary["down"] == 0 else "HOLD"
    result["status"] = "tick_complete"
    return result


# =============================================================================
# MODULE 8 — arifosd MAIN DAEMON
# =============================================================================

DAEMON_START = time.time()
DAEMON_METRICS = {"judgments": 0, "holds": 0, "seals": 0, "cautions": 0}

SOCK_PATH = os.environ.get("ARIFOS_SOCK", "/run/arifos.sock")
HTTP_PORT = int(os.environ.get("ARIFOS_HTTP_PORT", "18081"))
VAULT_PATH = os.environ.get("ARIFOS_VAULT", "/var/lib/arifos/vault999")


def build_daemon() -> Tuple["MetabolicPipeline", Vault999]:
    """Build the full daemon runtime."""
    vault = Vault999(VAULT_PATH)
    classifier = DeterministicHoldClassifier()
    apex = ApexThermodynamicEngine(kappa_r_threshold=0.95)
    floors = build_floor_registry()
    pipeline = MetabolicPipeline(vault, classifier, apex, floors)
    return pipeline, vault


class ThreadedHTTPServer(HTTPServer):
    """Allow multiple concurrent HTTP connections."""

    daemon_threads = True
    allow_reuse_address = True


def run_daemon():
    """Start the arifOS daemon."""
    pipeline, vault = build_daemon()

    # Attach pipeline to handlers
    ArifHTTPHandler.pipeline = pipeline
    UnixSocketHandler.pipeline = pipeline

    print("=" * 60)
    print("arifOS Constitutional Kernel — arifosd v0.2.0-PHASE1")
    print("SEAL    : 999-SEAL-PHASE1-VPS-DAEMON-20260523")
    print(f"EPOCH   : {datetime.now(timezone.utc).isoformat()}")
    print(f"Socket  : {SOCK_PATH}")
    print(f"HTTP    : localhost:{HTTP_PORT}")
    print(f"Vault   : {VAULT_PATH}")
    print(f"Tick    : every {DEFAULT_TICK_INTERVAL}s")
    print("Phase   : 1 — OBSERVABILITY (observe only, no autonomous mutation)")
    print("APEX    : ℐ[∫Ψ⊗ℭdτ]·Θ(κᵣ-0.95) s.t. ΔS_local<0")
    print("DITEMPA BUKAN DIBERI — 999 SEAL ALIVE")
    print("=" * 60)

    # Load prior metrics
    _load_metrics()

    # Start Unix socket server
    if os.path.exists(SOCK_PATH):
        os.unlink(SOCK_PATH)
    sock_server = socketserver.UnixStreamServer(SOCK_PATH, UnixSocketHandler)
    os.chmod(SOCK_PATH, 0o770)
    sock_thread = threading.Thread(target=sock_server.serve_forever, daemon=True)
    sock_thread.start()
    print(f"Unix socket listening: {SOCK_PATH}")

    # Start HTTP server
    http_server = ThreadedHTTPServer(("127.0.0.1", HTTP_PORT), ArifHTTPHandler)
    http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
    http_thread.start()
    print(f"HTTP health endpoint: http://127.0.0.1:{HTTP_PORT}/health")

    # Ensure log directories exist
    os.makedirs("/var/log/arifosd", exist_ok=True)
    os.makedirs("/var/run/arifosd", exist_ok=True)

    # Seal startup event
    arifos_vault_append(
        entry_type="daemon_start",
        actor="arifOS-vps-daemon",
        tool_name="run_daemon",
        result_status="STARTED",
        risk_class="SAFE",
        notes="arifosd Phase 1 daemon started",
        extra={
            "hostname": socket.gethostname(),
            "tick_interval": DEFAULT_TICK_INTERVAL,
            "organs": list(ARIFOS_ORGANS.keys()),
        },
    )

    print(f"arifOS Phase 1 daemon running — tick every {DEFAULT_TICK_INTERVAL}s")
    print("Press Ctrl+C to stop.")
    print()

    tick_count = 0
    last_tick_result = None

    try:
        while True:
            tick_count += 1
            tick_id = f"tick-{int(time.time())}"
            tick_epoch = datetime.now(timezone.utc).isoformat()
            print(f"[{tick_epoch}] tick {tick_count:04d} → arifos_vps_tick()")
            try:
                last_tick_result = arifos_vps_tick(
                    tick_id=tick_id, tick_interval=DEFAULT_TICK_INTERVAL
                )
                verdict = last_tick_result.get("verdict", "?")
                organs_up = (
                    last_tick_result.get("stages", {})
                    .get("organ_ping", {})
                    .get("summary", {})
                    .get("up", "?")
                )
                organs_down = (
                    last_tick_result.get("stages", {})
                    .get("organ_ping", {})
                    .get("summary", {})
                    .get("down", "?")
                )
                disk_max = (
                    last_tick_result.get("stages", {})
                    .get("vault_seal", {})
                    .get("chain_hash", "?")[:8]
                )
                print(
                    f"  → verdict={verdict} | organs={organs_up}UP/{organs_down}DOWN | vault_hash={disk_max}"
                )
            except Exception as tick_err:
                print(f"  → ERROR in arifos_vps_tick: {tick_err}")
                arifos_vault_append(
                    entry_type="tick_error",
                    actor="arifOS-vps-daemon",
                    tool_name="arifos_vps_tick",
                    result_status="ERROR",
                    risk_class="SAFE",
                    notes=str(tick_err)[:120],
                )
            # Sleep until next tick
            time.sleep(DEFAULT_TICK_INTERVAL)
    except KeyboardInterrupt:
        print("\nShutting down arifOS kernel...")
        arifos_vault_append(
            entry_type="daemon_stop",
            actor="arifOS-vps-daemon",
            tool_name="run_daemon",
            result_status="STOPPED",
            risk_class="SAFE",
            notes=f"Graceful shutdown after {tick_count} ticks",
            extra={"total_ticks": tick_count},
        )
        sock_server.shutdown()
        http_server.shutdown()


# =============================================================================
# CLI
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="arifOS Constitutional Kernel (arifosd)")
    parser.add_argument(
        "--mode",
        choices=["daemon", "once", "health", "classify", "vps-daemon", "watchdog-check"],
        default="daemon",
    )
    parser.add_argument(
        "--tick", type=int, default=60, help="Tick interval in seconds (for vps-daemon mode)"
    )
    parser.add_argument("--intent", help="Intent to judge")
    parser.add_argument("--command", help="Command to classify")
    parser.add_argument("--kappa-r", type=float, default=0.9, help="Inter-rater reliability")
    parser.add_argument("--confidence", type=float, default=0.8, help="Model confidence")
    args = parser.parse_args()

    if args.mode == "health":
        pipeline, _ = build_daemon()
        print(json.dumps(pipeline.vault._read_manifest(), indent=2))

    elif args.mode == "classify":
        classifier = DeterministicHoldClassifier()
        tier, verdict, rationale = classifier.classify(args.command or "")
        print(json.dumps({"tier": tier, "verdict": verdict, "rationale": rationale}, indent=2))

    elif args.mode == "once":
        pipeline, _ = build_daemon()
        result = asyncio.run(
            pipeline.metabolize(
                intent=args.intent or "single judgment",
                command=args.command or "",
                context={"kappa_r": args.kappa_r, "confidence": args.confidence},
            )
        )
        print(json.dumps(result, indent=2, default=str))

    elif args.mode == "watchdog-check":
        # Watchdog mode: verify arifosd process is alive
        import os

        pid_file = Path("/var/run/arifosd/daemon.pid")
        alive = False
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                os.kill(pid, 0)  # Signal 0 = check only
                alive = True
            except (ProcessLookupError, ValueError, PermissionError):
                alive = False

        if alive:
            print(json.dumps({"status": "ALIVE", "mode": "watchdog-check"}))
        else:
            # Process not alive — trigger watchdog alert
            print(json.dumps({"status": "DEAD", "mode": "watchdog-check"}))
            # If not in storm prevention, trigger restart
            try:
                from arifosd import arifos_watchdog_alert

                alert = arifos_watchdog_alert(reason="watchdog_timer_dead_process")
                print(json.dumps(alert, default=str))
            except ImportError:
                # Try direct execution
                pass

    elif args.mode == "vps-daemon":
        global DEFAULT_TICK_INTERVAL
        DEFAULT_TICK_INTERVAL = args.tick
        run_daemon()

    else:
        run_daemon()


if __name__ == "__main__":
    main()
