"""
arifOS APEX Judicial Core (Ψ) — APEX Room 777→999 (v52.1)

Implements the COOL PHASE as a real pipeline:
- 777 FORGE: format/prepare response (no new reasoning)
- 888 JUDGE: 13-floor validation + p(truth)
- 889 PROOF: Merkle root + Ed25519 signature (APEX key)
- 999 SEAL: immutable append via session ledger + Phoenix-72 cooling metadata
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from codebase.system.apex_prime import APEXPrime
from codebase.mcp.constitutional_metrics import get_stage_result, store_stage_result
from codebase.mcp.session_ledger import seal_memory

# v53.5.0: PsiKernel (Soul) + TrinityNine (9-Paradox) — NOW WIRED
import logging as _apex_logging
_apex_logger = _apex_logging.getLogger("codebase.apex.kernel")


@dataclass
class EntropyMeasurement:
    pre_entropy: float
    post_entropy: float
    entropy_reduction: float
    thermodynamic_valid: bool


class ConstitutionalEntropyProfiler:
    """Agent Zero Component: Measures ΔS (character-entropy proxy)."""

    @staticmethod
    def _calc_entropy(text: str) -> float:
        if not text:
            return 0.0
        counts: Dict[str, int] = {}
        for ch in text:
            counts[ch] = counts.get(ch, 0) + 1
        length = len(text)
        probs = [c / length for c in counts.values()]
        return -sum(p * math.log(p, 2.0) for p in probs if p > 0)

    async def measure_constitutional_cooling(self, pre_text: str, post_text: str) -> EntropyMeasurement:
        pre_e = self._calc_entropy(pre_text)
        post_e = self._calc_entropy(post_text)
        reduction = pre_e - post_e
        return EntropyMeasurement(
            pre_entropy=pre_e,
            post_entropy=post_e,
            entropy_reduction=reduction,
            thermodynamic_valid=reduction >= 0.0,
        )


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _compute_merkle_root(items: List[str]) -> str:
    """Compute a Merkle root from hex leaf hashes."""
    if not items:
        return _sha256_hex(b"EMPTY_MERKLE")
    level = list(items)
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])
        next_level: List[str] = []
        for i in range(0, len(level), 2):
            next_level.append(_sha256_hex((level[i] + level[i + 1]).encode("utf-8")))
        level = next_level
    return level[0]


def _runtime_vault_dir() -> Path:
    # .../arifos/core/apex/kernel.py -> repo root is 3 levels up from `arifos/`
    repo_root = Path(__file__).resolve().parents[3]
    vault = repo_root / "runtime" / "vault_999"
    vault.mkdir(parents=True, exist_ok=True)
    return vault


def _load_or_create_apex_key() -> Ed25519PrivateKey:
    """Load or create the persistent APEX Ed25519 signing key (runtime-only)."""
    key_path = _runtime_vault_dir() / "apex_ed25519_private_key.b64"
    if key_path.exists():
        raw = base64.b64decode(key_path.read_text(encoding="utf-8").strip())
        return Ed25519PrivateKey.from_private_bytes(raw)

    key = Ed25519PrivateKey.generate()
    raw = key.private_bytes_raw()
    key_path.write_text(base64.b64encode(raw).decode("ascii"), encoding="utf-8")
    return key


def _safe_json(obj: Any) -> Any:
    """Best-effort JSON serializer for mixed dataclass/dict objects."""
    if obj is None:
        return None
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, dict):
        return {k: _safe_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe_json(v) for v in obj]
    if hasattr(obj, "to_dict"):
        return _safe_json(obj.to_dict())
    if hasattr(obj, "__dataclass_fields__"):
        return _safe_json(asdict(obj))
    if hasattr(obj, "__dict__"):
        return _safe_json({k: v for k, v in obj.__dict__.items() if not k.startswith("_")})
    return str(obj)


class APEXJudicialCore:
    """Unified APEX kernel for both `apex_judge` and `vault_999` routers."""

    def __init__(self) -> None:
        self.entropy_profiler = ConstitutionalEntropyProfiler()
        self._signing_key = _load_or_create_apex_key()

    # -------------------------------------------------------------------------
    # 777 FORGE
    # -------------------------------------------------------------------------

    @staticmethod
    async def forge_777(response: str, merged_bundle: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Stage 777: Prepare response without changing reasoning."""
        draft = response or (merged_bundle or {}).get("draft", "")
        return {
            "stage": "777_FORGE",
            "draft": draft,
            "draft_size": len(draft),
            "no_reasoning_change": True,
        }

    # -------------------------------------------------------------------------
    # 888 JUDGE
    # -------------------------------------------------------------------------

    @staticmethod
    def _extract_votes(agi_result: Optional[Dict[str, Any]], asi_result: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Extract tri-witness votes from mixed AGI/ASI result shapes."""
        agi = agi_result or {}
        asi = asi_result or {}

        # Mind vote: prefer think.confidence, fallback to truth_score, else 0.9.
        think = agi.get("think") or {}
        mind = float(think.get("confidence", agi.get("truth_score", 0.9)) or 0.9)

        # Heart vote: prefer empathy.kappa_r / empathy_score
        empathy = asi.get("empathy") or {}
        heart = float(empathy.get("kappa_r", asi.get("kappa_r", asi.get("empathy_score", 0.8))) or 0.8)

        # Earth witness: if evidence present, use its grounding score else baseline 0.95
        evidence = asi.get("evidence") or {}
        earth = float(evidence.get("truth_score", evidence.get("truth_grounding", 0.95)) or 0.95)

        return {"mind": mind, "heart": heart, "earth": earth}

    def judge_888(
        self,
        *,
        session_id: str,
        query: str,
        response: str,
        agi_result: Optional[Dict[str, Any]],
        asi_result: Optional[Dict[str, Any]],
        user_id: str,
        lane: str,
    ) -> Dict[str, Any]:
        """Stage 888: full floor validation with p(truth)."""
        from codebase.enforcement.floor_validators import validate_f4_clarity

        votes = self._extract_votes(agi_result, asi_result)
        tri_witness = sum(votes.values()) / 3.0

        # Build minimal floor bundles for APEXPrime (F1-F9 family).
        # We keep these conservative: if signal missing, it does not auto-fail.
        from codebase.system.types import FloorCheckResult, Metrics

        truth_score = float(votes["mind"])
        kappa_r = float(votes["heart"])
        peace_squared = float((asi_result or {}).get("peace_squared", 1.0) or 1.0)
        omega_0 = float((asi_result or {}).get("omega_0", 0.04) or 0.04)
        delta_res = validate_f4_clarity(query, {"response": response})
        delta_s = float(delta_res.get("delta_s", 0.0))
        delta_s_passed = bool(delta_res.get("pass", True))

        metrics = Metrics(
            truth=truth_score,
            delta_s=delta_s,
            peace_squared=peace_squared,
            kappa_r=kappa_r,
            omega_0=omega_0,
            amanah=True,
            tri_witness=tri_witness,
            rasa=True,
            anti_hantu=True,
        )

        agi_floors = [
            FloorCheckResult("F2", "Truth", 0.99, truth_score, truth_score >= 0.99, is_hard=True),
            FloorCheckResult(
                "F6",
                "Clarity (ΔS)",
                0.0,
                delta_s,
                delta_s_passed,
                is_hard=True,
                reason=str(delta_res.get("reason", "")),
            ),
        ]
        asi_floors = [
            FloorCheckResult("F3", "Peace²", 1.0, peace_squared, peace_squared >= 1.0, is_hard=False),
            FloorCheckResult("F4", "Empathy (κᵣ)", 0.95, kappa_r, kappa_r >= 0.95, is_hard=False),
            FloorCheckResult("F5", "Humility (Ω₀)", 0.03, omega_0, 0.03 <= omega_0 <= 0.05, is_hard=True),
            FloorCheckResult("F8", "Tri-Witness", 0.95, tri_witness, tri_witness >= 0.95, is_hard=(lane == "HARD")),
        ]

        prime = APEXPrime(high_stakes=(lane == "HARD"))
        apex_verdict = prime.judge_output(
            query=query,
            response=response,
            agi_results=agi_floors,
            asi_results=asi_floors,
            user_id=user_id,
            context={"lane": lane, "evidence_ratio": float((asi_result or {}).get("evidence_ratio", 1.0) or 1.0)},
        )

        # =================================================================
        # v53.5.0: TrinityNine 9-Paradox Synchronization (NOW LIVE)
        # =================================================================
        nine_fold = None
        try:
            from codebase.apex.trinity_nine import TrinityNine
            tn = TrinityNine(session_id=session_id)
            agi_delta = {
                "F2_truth": truth_score,
                "F4_clarity": abs(delta_s),
                "F7_humility": omega_0,
                "kalman_gain": float((agi_result or {}).get("kalman_gain", 0.5)),
                "hierarchy_depth": float((agi_result or {}).get("hierarchy_depth", 5)),
                "efe_score": float((agi_result or {}).get("efe", -1.0)),
            }
            asi_omega = {
                "kappa_r": kappa_r,
                "peace_squared": peace_squared,
                "justice": float((asi_result or {}).get("trinity_balance", {}).get("society", 0.9) if isinstance((asi_result or {}).get("trinity_balance"), dict) else 0.9),
                "reversibility": float((asi_result or {}).get("reversibility", 1.0)),
                "consent": 1.0 if (asi_result or {}).get("consent", True) else 0.0,
                "weakest_protection": float((asi_result or {}).get("weakest_protection", 0.8)),
            }
            # TrinityNine.synchronize is async but judge_888 is sync —
            # use the solver directly for the equilibrium calculation
            from codebase.apex.trinity_nine import create_nine_paradoxes, EquilibriumSolver
            import numpy as np
            paradoxes = create_nine_paradoxes()
            for key, paradox in paradoxes.items():
                agi_key = {"truth_care": "F2_truth", "clarity_peace": "F4_clarity", "humility_justice": "F7_humility",
                           "precision_reversibility": "kalman_gain", "hierarchy_consent": "hierarchy_depth",
                           "agency_protection": "efe_score", "urgency_sustainability": "efe_score",
                           "certainty_doubt": "kalman_gain", "unity_diversity": "F2_truth"}.get(key, "F2_truth")
                asi_key = {"truth_care": "kappa_r", "clarity_peace": "peace_squared", "humility_justice": "justice",
                           "precision_reversibility": "reversibility", "hierarchy_consent": "consent",
                           "agency_protection": "weakest_protection", "urgency_sustainability": "justice",
                           "certainty_doubt": "kappa_r", "unity_diversity": "kappa_r"}.get(key, "kappa_r")
                agi_val = agi_delta.get(agi_key, 0.5)
                asi_val = asi_omega.get(asi_key, 0.5)
                paradox.score = float(np.sqrt(max(0, agi_val) * max(0, asi_val)))
            solver = EquilibriumSolver()
            equilibrium = solver.solve(paradoxes)
            nine_fold = equilibrium  # EquilibriumState with geometric_mean, std_deviation
        except Exception as e:
            _apex_logger.warning(f"TrinityNine sync skipped: {e}")
            nine_fold = None

        # =================================================================
        # v53.5.0: PsiKernel F8 Genius Validation (NOW LIVE)
        # =================================================================
        final_verdict = apex_verdict.verdict.value
        final_reason = apex_verdict.reason
        psi_verdict_data = {}
        try:
            from codebase.apex.psi_kernel import PsiKernel
            from dataclasses import dataclass as _dc

            @_dc
            class _DeltaProxy:
                passed: bool = True
                failures: list = None
                f1_amanah: bool = True
                f2_clarity: bool = True
                def __post_init__(self):
                    self.failures = self.failures or []

            @_dc
            class _OmegaProxy:
                passed: bool = True
                failures: list = None
                f3_tri_witness: bool = True
                f4_peace_squared: bool = True
                f5_kappa_r: bool = True
                f6_omega_0: bool = True
                f7_rasa: bool = True
                f9_c_dark: bool = True
                def __post_init__(self):
                    self.failures = self.failures or []

            delta_proxy = _DeltaProxy(
                passed=truth_score >= 0.99 and delta_s_passed,
                f1_amanah=True, f2_clarity=delta_s_passed,
            )
            omega_proxy = _OmegaProxy(
                passed=peace_squared >= 1.0 and kappa_r >= 0.95,
                f3_tri_witness=tri_witness >= 0.95,
                f4_peace_squared=peace_squared >= 1.0,
                f5_kappa_r=kappa_r >= 0.95,
                f6_omega_0=0.03 <= omega_0 <= 0.05,
            )

            # F8 Genius: use nine-fold equilibrium GM if available, else tri_witness
            genius_score = nine_fold.geometric_mean if nine_fold and hasattr(nine_fold, 'geometric_mean') else tri_witness

            hypervisor_passed = all(
                f not in (apex_verdict.violated_floors or []) for f in ("F10", "F11", "F12")
            )
            hypervisor_failures = [f for f in (apex_verdict.violated_floors or []) if f in ("F10", "F11", "F12")]

            psi = PsiKernel(genius_threshold=0.80)
            psi_result = psi.evaluate(
                delta_verdict=delta_proxy, omega_verdict=omega_proxy,
                genius=genius_score, hypervisor_passed=hypervisor_passed,
                hypervisor_failures=hypervisor_failures,
            )

            psi_verdict_val = psi_result.verdict.value if hasattr(psi_result.verdict, 'value') else str(psi_result.verdict)
            severity = {"SABAR": 5, "VOID": 4, "888_HOLD": 3, "HOLD_888": 3, "PARTIAL": 2, "SEAL": 1}
            if severity.get(psi_verdict_val, 0) > severity.get(final_verdict, 0):
                final_verdict = psi_verdict_val
                final_reason = f"PsiKernel override: {psi_result.metadata.get('verdict_reason', psi_verdict_val)} (F8={genius_score:.3f})"

            psi_verdict_data = {
                "psi_verdict": psi_verdict_val, "psi_f8_genius": genius_score,
                "psi_passed": psi_result.passed, "psi_overrode": severity.get(psi_verdict_val, 0) > severity.get(apex_verdict.verdict.value, 0),
            }
        except Exception as e:
            _apex_logger.warning(f"PsiKernel evaluation skipped: {e}")

        # =================================================================
        # Build final verdict struct
        # =================================================================
        verdict_struct = {
            "stage": "888_JUDGE",
            "session_id": session_id,
            "lane": lane,
            "verdict": final_verdict,
            "reason": final_reason,
            "p_truth": float(apex_verdict.genius_stats.get("p_truth", 0.0)) if apex_verdict.genius_stats else 0.0,
            "tri_witness": tri_witness,
            "votes": votes,
            "violated_floors": list(apex_verdict.violated_floors),
            "cooling": apex_verdict.cooling_metadata or {},
            "proof_hash": apex_verdict.proof_hash,
            "metrics": _safe_json(metrics),
            "psi_kernel": psi_verdict_data,
            "nine_fold": {
                "equilibrium_gm": nine_fold.geometric_mean if nine_fold and hasattr(nine_fold, 'geometric_mean') else None,
                "equilibrium_std": nine_fold.std_deviation if nine_fold and hasattr(nine_fold, 'std_deviation') else None,
            } if nine_fold else {},
        }

        store_stage_result(session_id, "apex", verdict_struct)
        return verdict_struct

    # -------------------------------------------------------------------------
    # 889 PROOF
    # -------------------------------------------------------------------------

    def proof_889(self, *, session_id: str, verdict_struct: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 889: Merkle tree + Ed25519 signature."""
        floors = verdict_struct.get("metrics") or {}
        # Leaf hashes include floor summary + verdict fields for immutability.
        leaf_payloads = [
            json.dumps({"k": k, "v": floors.get(k)}, sort_keys=True, default=str).encode("utf-8")
            for k in sorted(floors.keys())
        ]
        leaves = [_sha256_hex(p) for p in leaf_payloads]
        leaves.append(_sha256_hex(json.dumps({"verdict": verdict_struct.get("verdict")}, sort_keys=True).encode()))

        merkle_root = _compute_merkle_root(leaves)
        signature = self._signing_key.sign(merkle_root.encode("utf-8")).hex()
        public_key = self._signing_key.public_key().public_bytes_raw().hex()

        proof = {
            "stage": "889_PROOF",
            "session_id": session_id,
            "merkle_root": merkle_root,
            "signature_ed25519": signature,
            "public_key_ed25519": public_key,
            "leaves": leaves,
        }
        return proof

    # -------------------------------------------------------------------------
    # 999 SEAL (Vault IO)
    # -------------------------------------------------------------------------

    @staticmethod
    def _summarize(verdict_struct: Dict[str, Any]) -> str:
        verdict = verdict_struct.get("verdict", "UNKNOWN")
        reason = verdict_struct.get("reason", "")
        return f"{verdict}: {reason}".strip()

    async def seal_999(
        self,
        *,
        session_id: str,
        verdict_struct: Dict[str, Any],
        init_result: Optional[Dict[str, Any]],
        agi_result: Optional[Dict[str, Any]],
        asi_result: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Stage 999: Seal session to ledger (JSON+Markdown) with Phoenix metadata."""
        proof = self.proof_889(session_id=session_id, verdict_struct=verdict_struct)

        telemetry = {
            "verdict": verdict_struct.get("verdict"),
            "p_truth": verdict_struct.get("p_truth"),
            "TW": verdict_struct.get("tri_witness"),
            "dS": (verdict_struct.get("metrics") or {}).get("delta_s"),
            "peace2": (verdict_struct.get("metrics") or {}).get("peace_squared"),
            "kappa_r": (verdict_struct.get("metrics") or {}).get("kappa_r"),
            "omega_0": (verdict_struct.get("metrics") or {}).get("omega_0"),
            "cooling": verdict_struct.get("cooling"),
            "proof": {"merkle_root": proof.get("merkle_root"), "public_key": proof.get("public_key_ed25519")},
        }

        seal_result = seal_memory(
            session_id=session_id,
            verdict=str(verdict_struct.get("verdict", "SABAR")),
            init_result=init_result or {},
            genius_result=agi_result or {},
            act_result=asi_result or {},
            judge_result={"verdict_struct": verdict_struct, "proof": proof},
            telemetry=telemetry,
            context_summary=self._summarize(verdict_struct),
            key_insights=list((verdict_struct.get("violated_floors") or [])[:8]),
        )

        return {
            "stage": "999_SEAL",
            "status": "SEALED" if seal_result.get("sealed") else "ERROR",
            "session_id": session_id,
            "verdict": verdict_struct.get("verdict", "UNKNOWN"),
            "seal": seal_result,
            "proof": proof,
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        }

    # -------------------------------------------------------------------------
    # Vault read/list helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _sessions_dir() -> Path:
        from codebase.mcp.session_ledger import SESSION_PATH

        return SESSION_PATH

    def _list_session_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        path = self._sessions_dir()
        if not path.exists():
            return []
        files = sorted(path.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[: max(1, limit)]
        entries: List[Dict[str, Any]] = []
        for f in files:
            try:
                data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
                entries.append(
                    {
                        "entry_hash": data.get("entry_hash"),
                        "session_id": data.get("session_id"),
                        "timestamp": data.get("timestamp"),
                        "verdict": data.get("verdict"),
                        "merkle_root": data.get("merkle_root"),
                        "prev_hash": data.get("prev_hash"),
                    }
                )
            except Exception:
                continue
        return entries

    def _read_entry(self, entry_hash_prefix: str) -> Optional[Dict[str, Any]]:
        path = self._sessions_dir()
        if not path.exists():
            return None
        for f in path.glob(f"{entry_hash_prefix}*.json"):
            try:
                return json.loads(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                return None
        return None

    # -------------------------------------------------------------------------
    # Router entry point
    # -------------------------------------------------------------------------

    async def execute(self, action: str, kwargs: dict) -> dict:
        """Unified APEX execution entry point (used by MCP bridge routers)."""
        session_id = str(kwargs.get("session_id") or "")
        query = str(kwargs.get("query") or "")
        response = str(kwargs.get("response") or kwargs.get("draft") or "")
        user_id = str(kwargs.get("user_id") or "anonymous")
        lane = str(kwargs.get("lane") or "SOFT").upper()

        # Load missing bundles from in-memory session store (when client doesn't pass them).
        agi_result = kwargs.get("agi_result") or get_stage_result(session_id, "agi")
        asi_result = kwargs.get("asi_result") or get_stage_result(session_id, "asi")
        init_result = kwargs.get("init_result") or get_stage_result(session_id, "init")

        if action in {"forge", "eureka"}:
            forged = await self.forge_777(response, merged_bundle=kwargs.get("merged_bundle"))
            store_stage_result(session_id, "apex", forged)
            return {"status": "SEAL", "verdict": "SEAL", "session_id": session_id, **forged}

        if action == "judge":
            verdict_struct = self.judge_888(
                session_id=session_id,
                query=query,
                response=response,
                agi_result=agi_result,
                asi_result=asi_result,
                user_id=user_id,
                lane=lane,
            )
            return {"status": verdict_struct["verdict"], "verdict": verdict_struct["verdict"], **verdict_struct}

        if action == "proof":
            verdict_struct = kwargs.get("verdict_struct") or get_stage_result(session_id, "apex")
            if not isinstance(verdict_struct, dict):
                return {"status": "VOID", "verdict": "VOID", "reason": "Missing verdict_struct for proof"}
            proof = self.proof_889(session_id=session_id, verdict_struct=verdict_struct)
            return {"status": "SEAL", "verdict": "SEAL", "session_id": session_id, **proof}

        if action == "full":
            forged = await self.forge_777(response, merged_bundle=kwargs.get("merged_bundle"))
            verdict_struct = self.judge_888(
                session_id=session_id,
                query=query,
                response=forged.get("draft", response),
                agi_result=agi_result,
                asi_result=asi_result,
                user_id=user_id,
                lane=lane,
            )
            proof = self.proof_889(session_id=session_id, verdict_struct=verdict_struct)
            full = {"forge": forged, "judge": verdict_struct, "proof": proof}
            store_stage_result(session_id, "apex", full)
            return {
                "status": verdict_struct["verdict"],
                "verdict": verdict_struct["verdict"],
                "session_id": session_id,
                **full,
            }

        # Vault operations (Tool 5 uses this same kernel via bridge_vault_router).
        if action == "seal":
            verdict_struct = kwargs.get("verdict_struct") or get_stage_result(session_id, "apex")
            if isinstance(verdict_struct, dict) and "judge" in verdict_struct:
                verdict_struct = verdict_struct.get("judge", verdict_struct)
            if not isinstance(verdict_struct, dict):
                verdict_struct = self.judge_888(
                    session_id=session_id,
                    query=query,
                    response=response,
                    agi_result=agi_result,
                    asi_result=asi_result,
                    user_id=user_id,
                    lane=lane,
                )
            sealed = await self.seal_999(
                session_id=session_id,
                verdict_struct=verdict_struct,
                init_result=init_result,
                agi_result=agi_result,
                asi_result=asi_result,
            )
            store_stage_result(session_id, "apex", sealed)
            return sealed

        if action == "list":
            limit = int((kwargs.get("data") or {}).get("limit", 10) if isinstance(kwargs.get("data"), dict) else 10)
            entries = self._list_session_entries(limit=limit)
            return {"status": "SEAL", "verdict": "SEAL", "entries": entries, "total": len(entries)}

        if action == "read":
            data = kwargs.get("data")
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except Exception:
                    data = {"entry_hash": data}
            data = data or {}
            entry_hash = str(data.get("entry_hash", "")).strip()
            if not entry_hash:
                return {"status": "VOID", "verdict": "VOID", "reason": "Missing entry_hash"}
            entry = self._read_entry(entry_hash_prefix=entry_hash[:16])
            if not entry:
                return {"status": "VOID", "verdict": "VOID", "reason": "Entry not found"}
            return {"status": "SEAL", "verdict": "SEAL", "entry": entry}

        return {"status": "VOID", "verdict": "VOID", "reason": f"Unknown APEX action: {action}"}


__all__ = ["APEXJudicialCore"]
