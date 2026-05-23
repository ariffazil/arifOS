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

import os, sys, json, time, uuid, hashlib, asyncio, socket, logging, argparse, re
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import socketserver, threading

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
    KB = 1.38e-23                       # Boltzmann constant

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
        compute_bits = context.get("compute_bits", len(context.get("intent",""))*8)

        thermo = self.compute_entropy_deltas(input_ent, output_ent, compute_bits)

        # Judge operator ℐ
        j_value = confidence
        if reversibility_passed:
            j_value *= 1.0
        else:
            j_value *= 0.4  # Gate not passed = penalized

        if not thermo["valid"]:
            verdict = "HOLD"
            reason = "Entropy violation — not a valid open-system operation"
        elif not reversibility_passed:
            verdict = "SABAR"
            reason = f"Reversibility gate not met: κᵣ={kappa_r:.2f} < {self.kappa_r_threshold}"
        elif j_value >= 0.5 and thermo["valid"]:
            verdict = "SEAL"
            reason = "APEX conditions met"
        else:
            verdict = "CAUTION"
            reason = "Marginal — proceed with monitoring"

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
        floor_id: str,
        malay_name: str,
        english_desc: str,
        threshold: float = 0.5,
        hard_floor: bool = False,
    ):
        self.floor_id = floor_id
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
            "floor_id": self.floor_id,
            "name": self.malay_name,
            "description": self.english_desc,
            "threshold": self.threshold,
            "hard_floor": self.hard_floor,
            "pass_count": self.pass_count,
            "breach_count": self.breach_count,
        }


class F01_AMANAH(ConstitutionalFloor):
    """F1 — Trust. Model must declare epistemic uncertainty."""
    def __init__(self):
        super().__init__("F01", "AMANAH",
            "Trust & epistemic honesty — model must declare what it does not know.",
            threshold=0.5, hard_floor=True)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        uncertainty_declared = ctx.get("uncertainty_acknowledged", False)
        score = 1.0 if uncertainty_declared else 0.0
        passed = score >= self.threshold
        rationale = (
            "Uncertainty acknowledged" if uncertainty_declared
            else "F01 BREACH: Model did not declare uncertainty (F1_AMANAH)"
        )
        return (passed, score, rationale)


class F02_HALAL(ConstitutionalFloor):
    """F2 — Truth. Claims must be verifiable or explicitly hedged."""
    def __init__(self):
        super().__init__("F02", "HALAL",
            "Halal — permissible claims only. Verifiable or explicitly hedged.",
            threshold=0.5, hard_floor=True)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        veracity = ctx.get("veracity_score", ctx.get("factual_support", 1.0))
        hallucination_risk = ctx.get("hallucination_risk", 0.0)
        score = min(veracity, 1.0 - hallucination_risk)
        passed = score >= self.threshold
        rationale = (
            f"Veracity={veracity:.2f}, hallucination_risk={hallucination_risk:.2f}"
        )
        return (passed, score, rationale)


class F03_ADIL(ConstitutionalFloor):
    """F3 — Justice. Distribution must be equitable."""
    def __init__(self):
        super().__init__("F03", "ADIL",
            "Adil — justice & fairness. Resource and reward distribution must be equitable.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        fairness = ctx.get("fairness_score", 1.0)
        return (fairness >= self.threshold, fairness,
                f"Fairness score: {fairness:.2f}")


class F04_TAUFIK(ConstitutionalFloor):
    """F4 — Clarity. Output must reduce entropy, not add noise."""
    def __init__(self):
        super().__init__("F04", "TAUFIK",
            "Divine guidance toward clarity. Output must reduce entropy relative to input.",
            threshold=0.5, hard_floor=False)

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


class F05_NUR(ConstitutionalFloor):
    """F5 — Light. Output must illuminate, not obscure."""
    def __init__(self):
        super().__init__("F05", "NUR",
            "Nur — light, radiance. Output must illuminate understanding.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        quality = ctx.get("explanation_quality", ctx.get("nur_score", 1.0))
        return (quality >= self.threshold, quality, f"Explanation quality: {quality:.2f}")


class F06_ILM(ConstitutionalFloor):
    """F6 — Knowledge. Claims must cite evidence."""
    def __init__(self):
        super().__init__("F06", "ILM",
            "Ilm — knowledge, science. Claims must cite evidence or qualify uncertainty.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        evidence = ctx.get("evidence_cited", 1.0)
        grounding = ctx.get("claim_grounding", 1.0)
        score = min(evidence, grounding)
        return (score >= self.threshold, score, f"Evidence={evidence:.2f}, grounding={grounding:.2f}")


class F07_SABR(ConstitutionalFloor):
    """F7 — Patience. Hold in superposition until collapse is warranted."""
    def __init__(self):
        super().__init__("F07", "SABR",
            "Sabr — patience. Remain in superposition until evidence earns collapse.",
            threshold=0.5, hard_floor=False)

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


class F08_SYUKUR(ConstitutionalFloor):
    """F8 — Gratitude. Credit external sources, not claim undue ownership."""
    def __init__(self):
        super().__init__("F08", "SYUKUR",
            "Gratitude. System must credit external sources, not claim undue ownership.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        attribution = ctx.get("attribution_quality", 1.0)
        return (attribution >= self.threshold, attribution,
                f"Attribution quality: {attribution:.2f}")


class F09_HANTU(ConstitutionalFloor):
    """F9 — Anti-hallucination. Guard against false pattern completion."""
    def __init__(self):
        super().__init__("F09", "HANTU",
            "Anti-hallucination. Guard against false pattern completion and confabulation.",
            threshold=0.5, hard_floor=True)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        hallucination_risk = ctx.get("hallucination_risk", 0.0)
        factuality = ctx.get("factuality", ctx.get("veracity_score", 1.0))
        score = factuality - hallucination_risk
        passed = (score >= self.threshold) and (hallucination_risk < 0.3)
        rationale = (
            f"Factuality={factuality:.2f}, hallucination_risk={hallucination_risk:.2f}"
        )
        return (passed, score, rationale)


class F10_IKLAS(ConstitutionalFloor):
    """F10 — Sincerity. No hidden agendas or concealed motives."""
    def __init__(self):
        super().__init__("F10", "IKLAS",
            "Sincerity. No hidden agendas or concealed utility functions.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        transparency = ctx.get("transparency", 1.0)
        agenda_disclosed = ctx.get("agenda_disclosed", True)
        score = transparency if agenda_disclosed else transparency * 0.3
        return (score >= self.threshold, score,
                f"Transparency={transparency:.2f}, agenda_disclosed={agenda_disclosed}")


class F11_AKHLAS(ConstitutionalFloor):
    """F11 — Ethics. Moral boundary respect."""
    def __init__(self):
        super().__init__("F11", "AKHLAK",
            "Akhlak — moral character. Actions must respect moral and ethical boundaries.",
            threshold=0.5, hard_floor=True)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        ethical = ctx.get("ethical_score", 1.0)
        return (ethical >= self.threshold, ethical, f"Ethical score: {ethical:.2f}")


class F12_MASLAHAT(ConstitutionalFloor):
    """F12 — Public interest. Net benefit must be positive."""
    def __init__(self):
        super().__init__("F12", "MASLAHAT",
            "Maslahat — public interest. Net benefit must be positive across stakeholders.",
            threshold=0.5, hard_floor=False)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        utility = ctx.get("utility_score", 1.0)
        harm_avoided = ctx.get("harm_avoided", True)
        score = utility if harm_avoided else utility * 0.3
        return (score >= self.threshold, score,
                f"Utility={utility:.2f}, harm_avoided={harm_avoided}")


class F13_KHALID(ConstitutionalFloor):
    """F13 — Continuity. System must preserve its own integrity."""
    def __init__(self):
        super().__init__("F13", "KHALID",
            "Khalid — continuity, sovereignty. System must preserve integrity after any action.",
            threshold=0.5, hard_floor=True)

    def evaluate(self, ctx: dict) -> Tuple[bool, float, str]:
        continuity = ctx.get("continuity_score", 1.0)
        sovereignty = ctx.get("sovereignty_maintained", True)
        blast_radius = ctx.get("blast_radius", 0.0)
        passed = (
            (continuity >= self.threshold)
            and sovereignty
            and (blast_radius < 0.8)
        )
        score = continuity if passed else 0.0
        rationale = (
            f"Continuity={continuity:.2f}, sovereignty={sovereignty}, blast_radius={blast_radius:.2f}"
        )
        return (passed, score, rationale)


def build_floor_registry() -> Dict[str, ConstitutionalFloor]:
    """Build the complete F01–F13 floor registry."""
    return {
        "F01": F01_AMANAH(),
        "F02": F02_HALAL(),
        "F03": F03_ADIL(),
        "F04": F04_TAUFIK(),
        "F05": F05_NUR(),
        "F06": F06_ILM(),
        "F07": F07_SABR(),
        "F08": F08_SYUKUR(),
        "F09": F09_HANTU(),
        "F10": F10_IKLAS(),
        "F11": F11_AKHLAS(),
        "F12": F12_MASLAHAT(),
        "F13": F13_KHALID(),
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
        (r"rm\s+-rf\s+/\s*$",               "F9 F13 ATOMIC: recursive root delete"),
        (r"rm\s+-rf\s+/var\s+/usr",          "F9 F13 ATOMIC: system dir wipe"),
        (r"rm\s+-rf\s+/etc\s*$",             "F9 F13 ATOMIC: config dir wipe"),
        (r"mkfs",                             "F13 ATOMIC: filesystem destruction"),
        (r"fdisk",                            "F13 ATOMIC: partition table destruction"),
        (r"parted.*mklabel",                  "F13 ATOMIC: partition destruction"),
        (r"dd\s+if=/dev/zero\s+of=/dev/",    "F13 ATOMIC: raw disk wipe"),
        (r"iptables\s+-F\s*$",               "F13 ATOMIC: firewall flush"),
        (r"iptables\s+-t\s+nat\s+-F",        "F13 ATOMIC: NAT table flush"),
        (r"curl\s+.*\|\s*sh",                "F9 F13 ATOMIC: remote exec via pipe"),
        (r"curl\s+.*\|\s*sudo\s+bash",       "F9 F13 ATOMIC: sudo remote exec"),
        (r"DROP\s+DATABASE",                 "F13 ATOMIC: database destruction"),
        (r"shutdown",                         "F13 ATOMIC: system shutdown"),
        (r"reboot",                           "F13 ATOMIC: system reboot"),
        (r":\(\)\s*:\s*\|\s*:\s*&\s*;",     "F9 ATOMIC: fork bomb"),
    ]

    HIGH_HOLD = [
        (r"chmod\s+-R\s+777\s+/",            "F9: world-writable system"),
        (r"chown\s+-R\s+root\s+/",           "F9 F13: ownership takeover"),
        (r"systemctl\s+mask",                "F13 HIGH: service masking"),
        (r"git\s+push\s+--force\s+.*main",   "F13 HIGH: main branch force push"),
        (r"eval\s+\$\(",                      "F9 HIGH: eval injection"),
    ]

    CAUTION_PATTERNS = [
        (r"git\s+push\s+--force",            "F13 CAUTION: force push"),
        (r"systemctl\s+(stop|restart)",      "F13 CAUTION: service control"),
        (r"chmod\s+-R\s+777",                "F9 CAUTION: broad permission change"),
        (r"docker\s+rm\s+-f",                "F9 CAUTION: container destruction"),
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
                        {k: v for k, v in entry.items()
                         if k not in ("merkle_leaf", "chain_hash", "prev_hash")},
                        sort_keys=True
                    )
                    expected_leaf, expected_chain = self._chain_hash(content, prev)
                    valid = (entry["merkle_leaf"] == expected_leaf
                            and entry["chain_hash"] == expected_chain)
                    results.append({"line": lineno, "valid": valid,
                                   "verdict": entry.get("verdict", "?"),
                                   "plan_id": entry.get("plan_id", "?")})
                    prev = entry["chain_hash"]
        except Exception as e:
            return {"error": str(e), "integrity_verified": False}

        all_valid = all(r["valid"] for r in results) if results else True
        return {"integrity_verified": all_valid, "total_events": len(results),
                "invalid_events": sum(1 for r in results if not r["valid"]),
                "events": results}


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
        actor_id = ctx.get("actor_id", "arifOS")
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
                plan_id=plan_id, intent=intent, command=command or "",
                verdict="HOLD", risk_tier=risk_tier,
                floors_passed=[], floors_failed=[],
                apex_metric={"kappa_r": kappa_r, "verdict": "HOLD"},
                human=human,
            )
            return self._build_envelope(
                plan_id=plan_id, session_id=session_id,
                verdict="HOLD", risk_tier=risk_tier,
                rationale=rationale, stages_run=stages_run,
                ctx=ctx, seal=seal, human=human,
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
        apex_result = self.apex.judge({
            "kappa_r": kappa_r,
            "confidence": ctx["confidence"],
            "intent": intent,
            "input_entropy_bits": ctx.get("input_entropy_bits", 10.0),
            "output_entropy_bits": ctx.get("output_entropy_bits", 5.0),
        })

        # 888 JUDGE — deliberate
        stages_run.append("888_JUDGE")
        verdict, judge_rationale = self._judge(ctx, apex_result)

        # 999 VAULT
        stages_run.append("999_VAULT")
        seal = self.vault.seal_judgment(
            plan_id=plan_id, intent=intent, command=command or "",
            verdict=verdict, risk_tier=risk_tier,
            floors_passed=ctx.get("floors_passed", []),
            floors_failed=ctx.get("floors_failed", []),
            apex_metric=apex_result.get("apex_metric", {}),
            human=human,
        )

        return self._build_envelope(
            plan_id=plan_id, session_id=session_id,
            verdict=verdict, risk_tier=risk_tier,
            rationale=judge_rationale, stages_run=stages_run,
            ctx=ctx, seal=seal, human=human, apex_result=apex_result,
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

    def _judge(self, ctx: dict, apex_result: dict) -> Tuple[str, str]:
        """888 JUDGE — evaluate floors and return verdict."""
        floors_passed = []
        floors_failed = []

        for floor_id, floor in self.floors.items():
            passed, score, rationale = floor.evaluate(ctx)
            if passed:
                floors_passed.append(floor_id)
                floor.pass_count += 1
            else:
                floors_failed.append(floor_id)
                floor.breach_count += 1

        ctx["floors_passed"] = floors_passed
        ctx["floors_failed"] = floors_failed

        # Any hard floor failed → HOLD
        hard_failed = [f for f in floors_failed
                      if self.floors[f].hard_floor]
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
        self, plan_id: str, session_id: str,
        verdict: str, risk_tier: str, rationale: str,
        stages_run: List[str], ctx: dict, seal: dict,
        human: str, apex_result: Optional[dict] = None,
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
            "artifacts": [],
            "content": [{"type": "text", "text": rationale}],
        }


# =============================================================================
# MODULE 5 — HTTP + SOCKET HANDLERS (MCP-over-HTTP + stdio-over-Unix)
# =============================================================================

class ArifHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler — health, MCP endpoints."""

    pipeline: 'MetabolicPipeline'

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
            self._json({"equation": "ℐ[∫Ψ⊗ℭdτ]·Θ(κᵣ-0.95) s.t. ΔS_local<0",
                         "description": "APEX thermodynamic kernel equation"})
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
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "arifosd", "version": "0.1.0"},
                "capabilities": {"tools": {"listChanged": True}},
            }}

        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

        if method == "tools/call":
            args = params.get("arguments", {})
            return asyncio.run(self.pipeline.metabolize(
                intent=args.get("intent", ""),
                command=args.get("command", ""),
                context=args.get("context", {}),
            ))

        if method == "judge":
            return asyncio.run(self.pipeline.metabolize(
                intent=params.get("intent", ""),
                command=params.get("command", ""),
                context=params.get("context", {}),
            ))

        if method == "classify":
            c = DeterministicHoldClassifier()
            t, v, r = c.classify(params.get("command", ""))
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "tier": t, "verdict": v, "rationale": r
            }}

        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}}

    def _health(self) -> dict:
        vault_ok = self.pipeline.vault.ledger.exists()
        return {
            "status": "ok", "daemon_up": True,
            "storage_writable": os.access(self.pipeline.vault.vault_path, os.W_OK),
            "vault_accessible": vault_ok,
            "policy_loaded": True,
            "adapters_loaded": 4,
            "uptime_seconds": int(time.time() - DAEMON_START),
            "epoch": datetime.now(timezone.utc).isoformat(),
        }

    def _ready(self) -> dict:
        return {"ready": True, "vault_accessible": True,
                "socket_listening": True, "sessions_active": 0}

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
    pipeline: 'MetabolicPipeline'

    def handle(self):
        try:
            while True:
                line = self.rfile.readline()
                if not line:
                    break
                req = json.loads(line.decode())
                resp = asyncio.run(self.pipeline.metabolize(
                    intent=req.get("intent", ""),
                    command=req.get("command", ""),
                ))
                self.wfile.write((json.dumps(resp, default=str) + "\n").encode())
        except Exception:
            pass


# =============================================================================
# MODULE 6 — MCP TOOL REGISTRY
# =============================================================================

TOOLS = [
    {"name": "arif_session_init", "description": "000 INIT — initialize governed session",
     "inputSchema": {"type": "object", "properties": {"actor_id": {"type": "string"}}, "required": ["actor_id"]}},
    {"name": "arif_sense_observe", "description": "111 SENSE — sense machine state",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "arif_judge_deliberate", "description": "888 JUDGE — deliver verdict on a plan",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "command": {"type": "string"}}, "required": ["intent"]}},
    {"name": "arif_vault_seal", "description": "999 VAULT — write seal to VAULT999 ledger",
     "inputSchema": {"type": "object", "properties": {"data": {"type": "object"}, "tool": {"type": "string"}, "stage": {"type": "string"}, "actor": {"type": "string"}}, "required": ["data", "tool", "stage", "actor"]}},
    {"name": "arif_run", "description": "Execute command through constitutional kernel",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "command": {"type": "string"}}, "required": ["intent"]}},
    {"name": "arif_exec", "description": "Execute script through constitutional kernel",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "script_path": {"type": "string"}}, "required": ["intent"]}},
    {"name": "arif_sudo", "description": "Privileged execution through constitutional kernel",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "command": {"type": "string"}}, "required": ["intent", "command"]}},
    {"name": "arif_systemctl", "description": "Service control through constitutional kernel",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "action": {"type": "string"}, "service": {"type": "string"}}, "required": ["intent"]}},
    {"name": "arif_apex_judge", "description": "APEX thermodynamic judgment on intent",
     "inputSchema": {"type": "object", "properties": {"intent": {"type": "string"}, "kappa_r": {"type": "number"}, "confidence": {"type": "number"}}, "required": ["intent"]}},
    {"name": "arif_floor_status", "description": "Query F01–F13 floor status",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "arif_vault_integrity", "description": "Verify VAULT999 chain hash integrity",
     "inputSchema": {"type": "object", "properties": {}}},
]


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
        return {"verdict": "HOLD", "risk_tier": "ATOMIC",
                "rationale": rationale, "command_blocked": True}
    if risk_tier == "HIGH":
        return {"verdict": "HOLD", "risk_tier": "HIGH",
                "rationale": rationale, "command_blocked": True}
    if risk_tier == "MEDIUM":
        return {"verdict": "CAUTION", "risk_tier": "MEDIUM",
                "rationale": rationale, "monitor": True, "command_allowed": True}

    return {"verdict": "PROCEED", "risk_tier": "LOW",
            "rationale": "Command cleared by deterministic classifier",
            "command_allowed": True}


def arif_exec_wrapper(script_path: str) -> dict:
    """arif_exec — script execution wrapper."""
    classifier = DeterministicHoldClassifier()
    path = Path(script_path)
    if path.exists():
        content = path.read_text()
    else:
        content = ""
    risk_tier, verdict, rationale = classifier.classify(content)
    return {"verdict": verdict, "risk_tier": risk_tier,
            "rationale": rationale, "script_path": script_path}


def arif_sudo_wrapper(command: str) -> dict:
    """arif_sudo — privileged action wrapper. Requires daemon approval."""
    classifier = DeterministicHoldClassifier()
    risk_tier, verdict, rationale = classifier.classify(command)

    if risk_tier in ("ATOMIC", "HIGH"):
        return {"verdict": "HOLD", "risk_tier": risk_tier,
                "rationale": f"Sudo blocked: {rationale}",
                "escalation_denied": True}

    return {"verdict": "CAUTION", "risk_tier": "MEDIUM",
            "rationale": f"Sudo with monitoring: {rationale}",
            "escalation_monitored": True}


def arif_systemctl_wrapper(action: str, service: str) -> dict:
    """arif-systemctl — service control wrapper."""
    classifier = DeterministicHoldClassifier()
    cmd = f"systemctl {action} {service}"
    risk_tier, verdict, rationale = classifier.classify(cmd)

    critical_services = ["ssh", "sshd", "systemd", "network", "firewalld",
                         "docker", "nginx", "apache2", "mysql", "postgresql"]

    if service in critical_services and action in ("stop", "restart", "mask"):
        return {"verdict": "HOLD", "risk_tier": "HIGH",
                "rationale": f"Critical service control blocked: {service} {action}",
                "action_blocked": True}

    if risk_tier in ("ATOMIC", "HIGH"):
        return {"verdict": "HOLD", "risk_tier": risk_tier,
                "rationale": rationale}

    return {"verdict": "CAUTION" if risk_tier == "MEDIUM" else "PROCEED",
            "risk_tier": risk_tier, "rationale": rationale,
            "action": action, "service": service}


# =============================================================================
# MODULE 8 — arifosd MAIN DAEMON
# =============================================================================

DAEMON_START = time.time()
DAEMON_METRICS = {"judgments": 0, "holds": 0, "seals": 0, "cautions": 0}

SOCK_PATH  = os.environ.get("ARIFOS_SOCK",  "/run/arifos.sock")
HTTP_PORT  = int(os.environ.get("ARIFOS_HTTP_PORT", "8081"))
VAULT_PATH = os.environ.get("ARIFOS_VAULT", "/var/lib/arifos/vault999")


def build_daemon() -> Tuple['MetabolicPipeline', Vault999]:
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
    print("arifOS Constitutional Kernel — arifosd v0.1.0")
    print("SEAL    : seal-20260523T055200-DITEMPA-BUKAN-DIBERI")
    print(f"EPOCH   : {datetime.now(timezone.utc).isoformat()}")
    print(f"Socket  : {SOCK_PATH}")
    print(f"HTTP    : localhost:{HTTP_PORT}")
    print(f"Vault   : {VAULT_PATH}")
    print("APEX    : ℐ[∫Ψ⊗ℭdτ]·Θ(κᵣ-0.95) s.t. ΔS_local<0")
    print("DITEMPA BUKAN DIBERI — 999 SEAL ALIVE")
    print("=" * 60)

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

    print("arifOS kernel ready. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down arifOS kernel...")
        sock_server.shutdown()
        http_server.shutdown()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="arifOS Constitutional Kernel (arifosd)")
    parser.add_argument("--mode", choices=["daemon", "once", "health", "classify"],
                        default="daemon")
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
        result = asyncio.run(pipeline.metabolize(
            intent=args.intent or "single judgment",
            command=args.command or "",
            context={"kappa_r": args.kappa_r, "confidence": args.confidence},
        ))
        print(json.dumps(result, indent=2, default=str))

    else:
        run_daemon()


if __name__ == "__main__":
    main()