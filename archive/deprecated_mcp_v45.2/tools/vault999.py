#!/usr/bin/env python3
"""
AAA MCP VAULT-999 Memory — Python reference implementation (minimal, fail-closed)

- Loads the TAC/EUREKA/VAULT/CoolingLedger spec JSON
- Validates Cooling Ledger entries (schema-lite)
- Evaluates TAC validity + EUREKA-777 verification (operational rules)
- Issues VAULT-999 verdicts: SEAL-999 / HOLD-999 / VOID-999
- Produces a Vault Record (MCP-ready object)

Spec: spec/v45/tac_eureka_vault999.json
Version: v45.3.0
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import uuid
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


# Path to spec (relative to repo root)
REPO_ROOT = Path(__file__).parent.parent.parent
SPEC_PATH = REPO_ROOT / "spec" / "v45" / "tac_eureka_vault999.json"


# -----------------------------
# Utilities
# -----------------------------

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def stable_json_dumps(obj: Any) -> str:
    # Canonical-ish JSON for hashing/digests
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest_ledger(entries: List[Dict[str, Any]]) -> str:
    return sha256_hex(stable_json_dumps(entries).encode("utf-8"))


# -----------------------------
# Spec Loading
# -----------------------------

def load_spec(path: Path = SPEC_PATH) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# Cooling Ledger
# -----------------------------

ALLOWED_ACTION_TYPES = {"REFUSE", "SILENCE", "DELAY", "CONSTRAIN"}

@dataclass
class LedgerValidationResult:
    ok: bool
    errors: List[str]
    sum_entropy_effect: float
    digest: str

def validate_ledger_entries(entries: List[Dict[str, Any]]) -> LedgerValidationResult:
    errors: List[str] = []
    total = 0.0

    if not isinstance(entries, list):
        return LedgerValidationResult(False, ["ledger must be a list"], 0.0, digest_ledger([]))

    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            errors.append(f"entry[{i}] must be object")
            continue

        # required fields
        for req in ("timestamp", "action_type", "entropy_effect", "reason_code"):
            if req not in e:
                errors.append(f"entry[{i}] missing required field: {req}")

        # action type
        at = e.get("action_type")
        if at is not None and at not in ALLOWED_ACTION_TYPES:
            errors.append(f"entry[{i}].action_type invalid: {at}")

        # entropy effect
        ee = e.get("entropy_effect")
        try:
            ee_num = float(ee)
            total += ee_num
            # Spec intent: cooling entries should be <= 0; fail-closed on positive values.
            if ee_num > 0:
                errors.append(f"entry[{i}].entropy_effect must be <= 0 for cooling (got {ee_num})")
        except Exception:
            errors.append(f"entry[{i}].entropy_effect must be number (got {ee})")

    d = digest_ledger(entries if isinstance(entries, list) else [])
    return LedgerValidationResult(ok=(len(errors) == 0), errors=errors, sum_entropy_effect=total, digest=d)


# -----------------------------
# TAC + EUREKA Evaluation
# -----------------------------

@dataclass
class EvaluationInputs:
    # TAC inputs
    dC: float
    Ea: float
    dH_dt: float
    Teff: float
    Tcrit: float

    # Humility band (Omega0)
    Omega0_value: float
    Omega0_min: float = 0.03
    Omega0_max: float = 0.05

    # EUREKA compression
    K_before: int = 0
    K_after: int = 0
    compression_ratio_max: float = 0.35

    # EUREKA plane checks (booleans from your runtime)
    reality_7_1_physically_permissible: bool = False
    structure_7_2_compressible: bool = False
    language_7_3_minimal_truthful_naming: bool = False


@dataclass
class VerdictResult:
    verdict: str                 # SEAL-999 / HOLD-999 / VOID-999
    state_next: str              # COOLING / SEALED etc.
    reasons: List[str]
    tac_valid: bool
    eureka_verified: bool
    ledger_clean: bool


def eval_tac(inputs: EvaluationInputs) -> Tuple[bool, List[str], str]:
    """
    Returns: (tac_valid, reasons, suggested_verdict_on_fail)
    Fail-closed: any fail -> invalid.
    """
    reasons = []

    # TAC.R1: dC > Ea
    if not (inputs.dC > inputs.Ea):
        reasons.append("TAC.R1 failed: dC <= Ea")
        return False, reasons, "HOLD-999"

    # TAC.R2: dH_dt < 0
    if not (inputs.dH_dt < 0):
        reasons.append("TAC.R2 failed: dH_dt >= 0")
        return False, reasons, "HOLD-999"

    # TAC.R3: Teff < Tcrit
    if not (inputs.Teff < inputs.Tcrit):
        reasons.append("TAC.R3 failed: Teff >= Tcrit")
        return False, reasons, "HOLD-999"

    # TAC.R4: Omega0 within band
    if not (inputs.Omega0_min <= inputs.Omega0_value <= inputs.Omega0_max):
        reasons.append("TAC.R4 failed: Omega0 out of [0.03, 0.05]")
        return False, reasons, "VOID-999"

    return True, ["TAC valid"], "SEAL-999"


def eval_eureka_777(inputs: EvaluationInputs) -> Tuple[bool, List[str], str]:
    """
    Returns: (eureka_verified, reasons, suggested_verdict_on_fail)
    """
    reasons = []

    # Planes
    if not inputs.reality_7_1_physically_permissible:
        reasons.append("E7.R1 failed: reality_7_1 not physically permissible")
        return False, reasons, "VOID-999"

    if not inputs.structure_7_2_compressible:
        reasons.append("E7.R2 failed: structure_7_2 compressible representation not present")
        return False, reasons, "HOLD-999"

    if not inputs.language_7_3_minimal_truthful_naming:
        reasons.append("E7.R3 failed: language_7_3 minimal truthful naming not possible")
        return False, reasons, "HOLD-999"

    # Compression criterion operational rule:
    # K_after <= K_before * compression_ratio_max
    if inputs.K_before <= 0:
        reasons.append("E7.C1 failed: K_before must be > 0 to measure compression")
        return False, reasons, "HOLD-999"

    if inputs.K_after > int(inputs.K_before * inputs.compression_ratio_max):
        reasons.append(
            f"E7.C1 failed: K_after ({inputs.K_after}) > K_before*ratio "
            f"({int(inputs.K_before * inputs.compression_ratio_max)})"
        )
        return False, reasons, "VOID-999"

    return True, ["EUREKA-777 verified"], "SEAL-999"


def vault_999_decide(
    inputs: EvaluationInputs,
    ledger_entries: List[Dict[str, Any]],
    human_seal: Optional[Dict[str, str]] = None,
    T0_context_start: Optional[str] = None,
) -> Tuple[VerdictResult, Dict[str, Any]]:
    """
    Applies VAULT-999 gating:
      Entry requires TAC_VALID, EUREKA_VERIFIED, LEDGER_CLEAN
      SEAL-999 additionally requires human_seal (fail-closed to HOLD-999 if missing).

    TIME AS GOVERNANCE (MANDATORY):
      T0_context_start: When inquiry entered governance (chat start)
      T999_vault_verdict: When verdict issued (seal time) - auto-generated

    Returns: (verdict_result, vault_record)
    """
    reasons: List[str] = []

    # TIME GOVERNANCE: T₀ required
    if not T0_context_start:
        reasons.append("T0_MISSING: Context entry time required (chat start)")
        verdict = "VOID-999"
        state_next = "COOLING"
        vault_record = {
            "trace_id": str(uuid.uuid4()),
            "T0_context_start": None,
            "T999_vault_verdict": utc_now_iso(),
            "state": "COOLING",
            "verdict": "VOID-999",
            "reasons": reasons
        }
        verdict_result = VerdictResult(
            verdict="VOID-999",
            state_next="COOLING",
            reasons=reasons,
            tac_valid=False,
            eureka_verified=False,
            ledger_clean=False,
        )
        return verdict_result, vault_record

    # Ledger validation + "clean" determination
    ledger_val = validate_ledger_entries(ledger_entries)
    ledger_clean = ledger_val.ok and (ledger_val.sum_entropy_effect < 0)

    if not ledger_val.ok:
        reasons.extend([f"LEDGER schema error: {e}" for e in ledger_val.errors])
    if ledger_val.ok and not (ledger_val.sum_entropy_effect < 0):
        reasons.append("LEDGER_CLEAN failed: sum(entropy_effect) must be < 0")

    # Evaluate TAC and EUREKA
    tac_valid, tac_reasons, tac_fail_verdict = eval_tac(inputs)
    eureka_ok, eureka_reasons, eureka_fail_verdict = eval_eureka_777(inputs)

    # Combine reasons
    reasons.extend([r for r in tac_reasons if r != "TAC valid"])
    reasons.extend([r for r in eureka_reasons if r != "EUREKA-777 verified"])

    # VAULT entry conditions
    if not tac_valid:
        verdict = tac_fail_verdict
        state_next = "COOLING"
    elif not eureka_ok:
        verdict = eureka_fail_verdict
        state_next = "COOLING"
    elif not ledger_clean:
        verdict = "HOLD-999"
        state_next = "COOLING"
    else:
        # Entry conditions satisfied; now SEAL requires human.
        if human_seal is None:
            verdict = "HOLD-999"
            state_next = "COOLING"
            reasons.append("HUMAN_SEAL missing: SEAL-999 requires human seal")
        else:
            verdict = "SEAL-999"
            state_next = "SEALED"

    if not reasons:
        reasons = ["OK"]

    # Build MCP vault_record (matches spec's mcp_binding.records.vault_record)
    trace_id = str(uuid.uuid4())
    T999_vault_verdict = utc_now_iso()  # Seal time (verdict issued)

    vault_record: Dict[str, Any] = {
        "trace_id": trace_id,
        "T0_context_start": T0_context_start,  # Entry time (chat start)
        "T999_vault_verdict": T999_vault_verdict,  # Seal time (verdict issued)
        "state": "SEALED" if verdict == "SEAL-999" else "COOLING",
        "verdict": verdict,
        "tac": {
            "dC": inputs.dC,
            "Ea": inputs.Ea,
            "dH_dt": inputs.dH_dt,
            "Teff": inputs.Teff,
            "Tcrit": inputs.Tcrit,
            "Omega0_value": inputs.Omega0_value,
            "Omega0_band": [inputs.Omega0_min, inputs.Omega0_max],
            "valid": tac_valid,
        },
        "eureka_777": {
            "reality_7_1_physically_permissible": inputs.reality_7_1_physically_permissible,
            "structure_7_2_compressible": inputs.structure_7_2_compressible,
            "language_7_3_minimal_truthful_naming": inputs.language_7_3_minimal_truthful_naming,
            "K_before": inputs.K_before,
            "K_after": inputs.K_after,
            "compression_ratio_max": inputs.compression_ratio_max,
            "verified": eureka_ok,
        },
        "ledger_digest": ledger_val.digest,
        "human_seal": human_seal if verdict == "SEAL-999" else None,
        "reasons": reasons,
    }

    verdict_result = VerdictResult(
        verdict=verdict,
        state_next=state_next,
        reasons=reasons,
        tac_valid=tac_valid,
        eureka_verified=eureka_ok,
        ledger_clean=ledger_clean,
    )

    return verdict_result, vault_record
