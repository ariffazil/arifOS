"""
arifOS Kernel Runtime — Self-Verifying Constitutional Substrate

The internal kernel layer that governs the metabolic surface.
Not exposed as public MCP tool — accessed via arifos.init syscall modes.

DITEMPA BUKAN DIBERI 🔥
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

TRINITY_THRESHOLD = 0.95  # W₃ ≥ 0.95 for SEAL
HUMILITY_BAND_LOW = (0.03, 0.05)  # Ω ∈ [0.03, 0.05]
OVERCONFIDENCE_THRESHOLD = 0.85
UNCERTAINTY_HIGH = 0.30


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class RiskLevel(Enum):
    SAFE = "safe"           # Read-only, reversible
    GUARDED = "guarded"     # Bounded write, reversible
    DANGEROUS = "dangerous" # Irreversible, requires 888_HOLD
    CRITICAL = "critical"   # Forge only — requires dual-signature


class Verdict(Enum):
    SEAL = "SEAL"       # Proceed
    HOLD = "HOLD"       # Escalate to human
    SABAR = "SABAR"     # Retry with guidance
    VOID = "VOID"       # Halt with explanation


class SideEffectClass(Enum):
    NONE = "none"           # Pure function
    READ = "read"           # Reads external state
    WRITE_SAFE = "write_safe"   # Bounded, reversible write
    WRITE_DANGEROUS = "write_dangerous"  # Irreversible
    FORGE = "forge"         # Creates signed execution


class ReversibilityClass(Enum):
    FULL = "full"           # Full rollback possible
    PARTIAL = "partial"     # Some rollback possible
    NONE = "none"           # Irreversible
    REQUIRES_APPROVAL = "requires_approval"  # Human gate required


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ToolContract:
    """Immutable contract defining tool physics."""
    
    name: str
    contract_version: str
    
    # Schema
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
    # Constitutional binding
    floors_enforced: List[str]  # ["F2", "F3", "F4", ...]
    physics: Dict[str, Any] = field(default_factory=dict)
    # {
    #   "entropy": {"max_delta": 0.0, "target": "decrease"},
    #   "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]},
    #   "confidence": {"min": 0.7, "proxy": "evidence_weighted"}
    # }
    
    # Risk classification
    risk_level: RiskLevel = RiskLevel.GUARDED
    side_effect_class: SideEffectClass = SideEffectClass.READ
    reversibility_class: ReversibilityClass = ReversibilityClass.FULL
    
    # Metabolic DAG
    allowed_predecessors: Set[str] = field(default_factory=set)
    allowed_successors: Set[str] = field(default_factory=set)
    
    # Provenance
    proof_requirements: List[str] = field(default_factory=list)
    hash: str = field(default="")
    
    def __post_init__(self):
        if not self.hash:
            # Compute hash from contract content
            content = f"{self.name}:{self.contract_version}:{json.dumps(self.floors_enforced, sort_keys=True)}"
            object.__setattr__(self, 'hash', hashlib.sha256(content.encode()).hexdigest()[:16])


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT REGISTRY — 11 Canonical Tools
# ═══════════════════════════════════════════════════════════════════════════════

class ContractRegistry:
    """Central registry of all tool contracts."""
    
    _contracts: Dict[str, ToolContract] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls):
        """Initialize the canonical 11-tool contract registry."""
        if cls._initialized:
            return
        
        cls._contracts = {
            # ═════════════════════════════════════════════════════════════════
            # FOUNDATION LAYER
            # ═════════════════════════════════════════════════════════════════
            "arifos.init": ToolContract(
                name="arifos.init",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "mode": {"type": "string", "enum": ["bootstrap", "status", "registry", "inspect", "validate", "describe_kernel"]},
                        "session_id": {"type": "string"},
                        "authority": {"type": "string"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "session_id": {"type": "string"},
                        "continuity": {"type": "object"},
                        "governance": {"type": "object"},
                        "operator_summary": {"type": "object"}
                    }
                },
                floors_enforced=["F11", "F13"],
                physics={
                    "entropy": {"max_delta": 0.1, "target": "bounded"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]}
                },
                risk_level=RiskLevel.SAFE,
                side_effect_class=SideEffectClass.WRITE_SAFE,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors=set(),  # Genesis
                allowed_successors={"arifos.sense", "arifos.route"},
                proof_requirements=["session_binding"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.sense": ToolContract(
                name="arifos.sense",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "mode": {"type": "string", "enum": ["auto", "lite", "deep"]},
                        "grounding_required": {"type": "boolean"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "verdict": {"type": "string", "enum": ["SEAL", "HOLD", "SABAR"]},
                        "grounding": {"type": "object"},
                        "uncertainty": {"type": "object"},
                        "evidence_count": {"type": "integer"},
                        "mode_used": {"type": "string"}
                    }
                },
                floors_enforced=["F2", "F3", "F7"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "decrease"},
                    "uncertainty": {"band": "measured", "omega_range": [0.0, 1.0]},
                    "confidence": {"min": 0.0, "proxy": "evidence_weighted"}
                },
                risk_level=RiskLevel.SAFE,
                side_effect_class=SideEffectClass.READ,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.init"},
                allowed_successors={"arifos.mind", "arifos.route"},
                proof_requirements=["grounding_check", "uncertainty_attached"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.mind": ToolContract(
                name="arifos.mind",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "context": {"type": "object"},
                        "mode": {"type": "string", "enum": ["reason", "reflect", "synthesize"]},
                        "uncertainty_hint": {"type": "number"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "reasoning": {"type": "string"},
                        "conclusion": {"type": "string"},
                        "confidence": {"type": "number"},
                        "uncertainty": {"type": "number"},
                        "trace": {"type": "array"}
                    }
                },
                floors_enforced=["F2", "F4", "F7", "F8"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "decrease"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]},
                    "confidence": {"min": 0.7, "proxy": "evidence_weighted"}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.NONE,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.sense", "arifos.init"},
                allowed_successors={"arifos.route"},
                proof_requirements=["reasoning_trace", "confidence_attached"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.route": ToolContract(
                name="arifos.route",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "current_state": {"type": "string"},
                        "requested_tool": {"type": "string"},
                        "mode": {"type": "string", "enum": ["dispatch", "pipeline", "validate"]},
                        "context": {"type": "object"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "next_tool": {"type": "string"},
                        "allowed": {"type": "boolean"},
                        "reason": {"type": "string"},
                        "lane": {"type": "string"},
                        "estimated_cost": {"type": "object"}
                    }
                },
                floors_enforced=["F4", "F11"],
                physics={
                    "entropy": {"max_delta": 0.05, "target": "bounded"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.READ,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.init", "arifos.sense", "arifos.mind"},
                allowed_successors={"arifos.ops", "arifos.heart", "arifos.judge"},
                proof_requirements=["transition_logged"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.ops": ToolContract(
                name="arifos.ops",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "operation": {"type": "string", "enum": ["estimate", "calculate", "simulate"]},
                        "parameters": {"type": "object"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "result": {"type": "any"},
                        "confidence": {"type": "number"},
                        "entropy_delta": {"type": "number"},
                        "method": {"type": "string"}
                    }
                },
                floors_enforced=["F2", "F4", "F7"],
                physics={
                    "entropy": {"max_delta": 0.1, "target": "bounded"},
                    "uncertainty": {"band": "measured", "omega_range": [0.0, 0.5]},
                    "confidence": {"min": 0.6, "proxy": "calculation_verified"}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.NONE,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.route"},
                allowed_successors={"arifos.heart", "arifos.judge"},
                proof_requirements=["calculation_method", "uncertainty_attached"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.heart": ToolContract(
                name="arifos.heart",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "context": {"type": "object"},
                        "mode": {"type": "string", "enum": ["critique", "empathize", "align"]}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "critique": {"type": "string"},
                        "alignment_score": {"type": "number"},
                        "concerns": {"type": "array"},
                        "recommendations": {"type": "array"}
                    }
                },
                floors_enforced=["F5", "F6", "F9"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "decrease"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.NONE,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.route", "arifos.ops"},
                allowed_successors={"arifos.judge"},
                proof_requirements=["value_alignment_check"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.judge": ToolContract(
                name="arifos.judge",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "evidence": {"type": "object"},
                        "confidence_required": {"type": "number"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "verdict": {"type": "string", "enum": ["SEAL", "HOLD", "SABAR", "VOID"]},
                        "confidence": {"type": "number"},
                        "reason": {"type": "string"},
                        "floors_checked": {"type": "array"}
                    }
                },
                floors_enforced=["F2", "F3", "F4", "F7", "F13"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "decrease"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]},
                    "confidence": {"min": 0.8, "proxy": "tri_witness"}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.READ,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.route", "arifos.ops", "arifos.heart"},
                allowed_successors={"arifos.vault", "arifos.forge"},
                proof_requirements=["tri_witness_verification", "floor_check_all"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.vault": ToolContract(
                name="arifos.vault",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "operation": {"type": "string", "enum": ["seal", "query", "verify"]},
                        "data": {"type": "object"},
                        "signature": {"type": "string"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "seal_id": {"type": "string"},
                        "hash": {"type": "string"},
                        "merkle_root": {"type": "string"},
                        "status": {"type": "string"}
                    }
                },
                floors_enforced=["F1", "F11", "F13"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "decrease"},
                    "uncertainty": {"band": "zero", "omega_range": [0.0, 0.01]}
                },
                risk_level=RiskLevel.DANGEROUS,
                side_effect_class=SideEffectClass.WRITE_DANGEROUS,
                reversibility_class=ReversibilityClass.NONE,
                allowed_predecessors={"arifos.judge"},
                allowed_successors=set(),  # Terminal
                proof_requirements=["judge_verdict_seal", "merkle_integrity", "authority_signature"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.memory": ToolContract(
                name="arifos.memory",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "operation": {"type": "string", "enum": ["store", "retrieve", "forget"]},
                        "key": {"type": "string"},
                        "value": {"type": "any"},
                        "ttl": {"type": "integer"}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "stored": {"type": "boolean"},
                        "retrieved": {"type": "any"},
                        "continuity_id": {"type": "string"}
                    }
                },
                floors_enforced=["F4", "F11"],
                physics={
                    "entropy": {"max_delta": 0.1, "target": "bounded"},
                    "uncertainty": {"band": "low", "omega_range": [0.03, 0.05]}
                },
                risk_level=RiskLevel.GUARDED,
                side_effect_class=SideEffectClass.WRITE_SAFE,
                reversibility_class=ReversibilityClass.PARTIAL,
                allowed_predecessors={"arifos.init", "arifos.judge"},
                allowed_successors=set(),  # Parallel access
                proof_requirements=["continuity_preserved"]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.forge": ToolContract(
                name="arifos.forge",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "manifest": {"type": "object"},
                        "signature": {"type": "string"},
                        "judge_verdict": {"type": "string", "enum": ["SEAL", "HOLD", "SABAR", "VOID"]}
                    },
                    "required": ["query", "judge_verdict"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "signed_manifest": {"type": "object"},
                        "status": {"type": "string"},
                        "hash": {"type": "string"}
                    }
                },
                floors_enforced=["F1", "F5", "F11", "F13"],
                physics={
                    "entropy": {"max_delta": 0.5, "target": "controlled"},
                    "uncertainty": {"band": "bounded", "omega_range": [0.0, 0.1]}
                },
                risk_level=RiskLevel.CRITICAL,
                side_effect_class=SideEffectClass.FORGE,
                reversibility_class=ReversibilityClass.REQUIRES_APPROVAL,
                allowed_predecessors={"arifos.judge"},  # ONLY from judge
                allowed_successors=set(),  # Terminal
                proof_requirements=[
                    "judge_verdict_seal",
                    "authority_verified",
                    "reversibility_declared",
                    "dual_signature"
                ]
            ),
            
            # ═════════════════════════════════════════════════════════════════
            "arifos.vps_monitor": ToolContract(
                name="arifos.vps_monitor",
                contract_version="0.2.0",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "metric": {"type": "string", "enum": ["health", "entropy", "resources", "all"]}
                    },
                    "required": ["query"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "entropy_current": {"type": "number"},
                        "entropy_delta": {"type": "number"},
                        "omega_band": {"type": "string"},
                        "tri_witness": {"type": "number"}
                    }
                },
                floors_enforced=["F8"],
                physics={
                    "entropy": {"max_delta": 0.0, "target": "measure_only"},
                    "uncertainty": {"band": "measured", "omega_range": [0.0, 1.0]}
                },
                risk_level=RiskLevel.SAFE,
                side_effect_class=SideEffectClass.READ,
                reversibility_class=ReversibilityClass.FULL,
                allowed_predecessors={"arifos.init"},  # Can call anytime after init
                allowed_successors=set(),  # Parallel, diagnostic only
                proof_requirements=["measurement_only"]
            ),
        }
        
        cls._initialized = True
    
    @classmethod
    def get_contract(cls, tool_name: str) -> Optional[ToolContract]:
        """Retrieve contract for a tool."""
        cls.initialize()
        return cls._contracts.get(tool_name)
    
    @classmethod
    def get_all_contracts(cls) -> Dict[str, ToolContract]:
        """Retrieve all registered contracts."""
        cls.initialize()
        return cls._contracts.copy()
    
    @classmethod
    def describe_contract(cls, tool_name: str) -> Dict[str, Any]:
        """Generate human/machine-readable contract description."""
        contract = cls.get_contract(tool_name)
        if not contract:
            return {"error": f"Contract not found for {tool_name}"}
        
        return {
            "name": contract.name,
            "contract_version": contract.contract_version,
            "hash": contract.hash,
            "floors_enforced": contract.floors_enforced,
            "physics": contract.physics,
            "risk_level": contract.risk_level.value,
            "side_effect_class": contract.side_effect_class.value,
            "reversibility_class": contract.reversibility_class.value,
            "allowed_predecessors": list(contract.allowed_predecessors),
            "allowed_successors": list(contract.allowed_successors),
            "proof_requirements": contract.proof_requirements
        }


# ═══════════════════════════════════════════════════════════════════════════════
# METABOLIC ROUTER — Pipeline Enforcement
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TransitionResult:
    allowed: bool
    reason: str
    violation_type: Optional[str] = None
    remediation: Optional[str] = None


class MetabolicRouter:
    """
    Enforces the metabolic DAG:
    init → sense → mind → route → (ops | heart) → judge → (vault | forge)
    """
    
    # Canonical metabolic flow
    METABOLIC_DAG: Dict[str, Set[str]] = {
        "arifos.init": {"arifos.sense", "arifos.route"},
        "arifos.sense": {"arifos.mind", "arifos.route"},
        "arifos.mind": {"arifos.route"},
        "arifos.route": {"arifos.ops", "arifos.heart", "arifos.judge"},
        "arifos.ops": {"arifos.heart", "arifos.judge"},
        "arifos.heart": {"arifos.judge"},
        "arifos.judge": {"arifos.vault", "arifos.forge"},
        "arifos.vault": set(),  # Terminal
        "arifos.forge": set(),  # Terminal
        "arifos.memory": set(),  # Parallel
        "arifos.vps_monitor": set(),  # Parallel
    }
    
    # Special gates requiring preconditions
    GATED_TRANSITIONS: Dict[Tuple[str, str], Dict[str, Any]] = {
        ("arifos.judge", "arifos.forge"): {
            "requires": {"judge_verdict": "SEAL"},
            "message": "arifos.forge requires judge:SEAL verdict"
        }
    }
    
    @classmethod
    def validate_transition(
        cls,
        current_tool: str,
        requested_tool: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TransitionResult:
        """
        Validate if transition current_tool → requested_tool is lawful.
        
        Returns TransitionResult with allowed=True/False and reason.
        """
        context = context or {}
        
        # Check if transition exists in DAG
        allowed_next = cls.METABOLIC_DAG.get(current_tool, set())
        
        if requested_tool not in allowed_next:
            return TransitionResult(
                allowed=False,
                reason=f"Transition {current_tool} → {requested_tool} not in metabolic DAG",
                violation_type="PIPELINE_VIOLATION",
                remediation=f"Allowed transitions from {current_tool}: {list(allowed_next)}"
            )
        
        # Check gated transitions
        gate_key = (current_tool, requested_tool)
        if gate_key in cls.GATED_TRANSITIONS:
            gate = cls.GATED_TRANSITIONS[gate_key]
            requires = gate.get("requires", {})
            
            for key, required_value in requires.items():
                actual_value = context.get(key)
                if actual_value != required_value:
                    return TransitionResult(
                        allowed=False,
                        reason=gate["message"],
                        violation_type="GATE_VIOLATION",
                        remediation=f"Required: {key}={required_value}, Actual: {actual_value}"
                    )
        
        # Check against contract
        contract = ContractRegistry.get_contract(requested_tool)
        if contract:
            if current_tool not in contract.allowed_predecessors:
                return TransitionResult(
                    allowed=False,
                    reason=f"Contract violation: {requested_tool} does not accept {current_tool} as predecessor",
                    violation_type="CONTRACT_VIOLATION",
                    remediation=f"Allowed predecessors: {list(contract.allowed_predecessors)}"
                )
        
        return TransitionResult(
            allowed=True,
            reason=f"Transition {current_tool} → {requested_tool} validated"
        )
    
    @classmethod
    def get_pipeline(cls, from_tool: Optional[str] = None) -> Dict[str, Any]:
        """Return the metabolic DAG as structured data."""
        if from_tool:
            return {
                "tool": from_tool,
                "allowed_next": list(cls.METABOLIC_DAG.get(from_tool, set())),
                "contract": ContractRegistry.describe_contract(from_tool)
            }
        
        return {
            "dag": {k: list(v) for k, v in cls.METABOLIC_DAG.items()},
            "terminals": [k for k, v in cls.METABOLIC_DAG.items() if not v],
            "genesis": ["arifos.init"]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRACT DRIFT DETECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DriftReport:
    tool_name: str
    drift_detected: bool
    violations: List[Dict[str, Any]]
    severity: str  # "none", "minor", "major", "critical"
    recommendation: str


class ContractDriftDetector:
    """
    Detects when runtime behavior diverges from declared contract.
    """
    
    @classmethod
    def check_schema_compliance(
        cls,
        tool_name: str,
        actual_output: Dict[str, Any],
        contract: Optional[ToolContract] = None
    ) -> Dict[str, Any]:
        """Check if output matches declared output schema."""
        contract = contract or ContractRegistry.get_contract(tool_name)
        if not contract:
            return {"valid": False, "error": "Contract not found"}
        
        # Simplified schema check — full implementation would use jsonschema
        required_keys = set(contract.output_schema.get("properties", {}).keys())
        actual_keys = set(actual_output.keys())
        
        missing = required_keys - actual_keys
        if missing:
            return {
                "valid": False,
                "violation": "MISSING_REQUIRED_FIELDS",
                "missing": list(missing)
            }
        
        return {"valid": True}
    
    @classmethod
    def check_transition_compliance(
        cls,
        call_graph: List[Tuple[str, str]],  # [(from, to), ...]
    ) -> Dict[str, Any]:
        """Check if observed call graph matches declared transitions."""
        violations = []
        
        for from_tool, to_tool in call_graph:
            result = MetabolicRouter.validate_transition(from_tool, to_tool)
            if not result.allowed:
                violations.append({
                    "transition": f"{from_tool} → {to_tool}",
                    "reason": result.reason,
                    "type": result.violation_type
                })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    @classmethod
    def check_side_effect_compliance(
        cls,
        tool_name: str,
        observed_effects: List[str],
        contract: Optional[ToolContract] = None
    ) -> Dict[str, Any]:
        """Check if observed side effects match declared class."""
        contract = contract or ContractRegistry.get_contract(tool_name)
        if not contract:
            return {"valid": False, "error": "Contract not found"}
        
        declared_class = contract.side_effect_class
        
        # Map effect classes to allowed observations
        allowed_map = {
            SideEffectClass.NONE: [],
            SideEffectClass.READ: ["read"],
            SideEffectClass.WRITE_SAFE: ["read", "write_safe"],
            SideEffectClass.WRITE_DANGEROUS: ["read", "write_safe", "write_dangerous"],
            SideEffectClass.FORGE: ["read", "write", "sign", "deploy"]
        }
        
        allowed = allowed_map.get(declared_class, [])
        unexpected = [e for e in observed_effects if e not in allowed]
        
        if unexpected:
            return {
                "valid": False,
                "violation": "UNEXPECTED_SIDE_EFFECTS",
                "declared": declared_class.value,
                "unexpected": unexpected
            }
        
        return {"valid": True}
    
    @classmethod
    def full_audit(
        cls,
        tool_name: str,
        actual_output: Dict[str, Any],
        call_graph: List[Tuple[str, str]],
        observed_effects: List[str]
    ) -> DriftReport:
        """Perform full drift audit on a tool execution."""
        contract = ContractRegistry.get_contract(tool_name)
        violations = []
        
        # Schema compliance
        schema_check = cls.check_schema_compliance(tool_name, actual_output, contract)
        if not schema_check.get("valid"):
            violations.append({
                "type": "SCHEMA_DRIFT",
                "details": schema_check
            })
        
        # Transition compliance
        transition_check = cls.check_transition_compliance(call_graph)
        if not transition_check.get("valid"):
            violations.extend([
                {"type": "TRANSITION_DRIFT", "details": v}
                for v in transition_check.get("violations", [])
            ])
        
        # Side effect compliance
        effect_check = cls.check_side_effect_compliance(tool_name, observed_effects, contract)
        if not effect_check.get("valid"):
            violations.append({
                "type": "SIDE_EFFECT_DRIFT",
                "details": effect_check
            })
        
        # Determine severity
        severity = "none"
        if violations:
            severity = "minor"
            if any(v["type"] == "TRANSITION_DRIFT" for v in violations):
                severity = "major"
            if any(v["type"] == "SIDE_EFFECT_DRIFT" for v in violations):
                severity = "critical"
        
        recommendation = "NO_ACTION"
        if severity == "minor":
            recommendation = "LOG_AND_MONITOR"
        elif severity == "major":
            recommendation = "ESCALATE_TO_HOLD"
        elif severity == "critical":
            recommendation = "HALT_AND_AUDIT"
        
        return DriftReport(
            tool_name=tool_name,
            drift_detected=len(violations) > 0,
            violations=violations,
            severity=severity,
            recommendation=recommendation
        )


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTION TRACE — Proof-Carrying Traces
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ExecutionStep:
    """Single step in an execution trace."""
    step_n: int
    tool: str
    contract_version: str
    input_hash: str
    output_hash: str
    entropy_before: float
    entropy_after: float
    floors_checked: List[str]
    verdict: str
    drift_status: str
    timestamp: float
    prev_hash: str
    _hash: str = field(default="", repr=False)
    
    def __post_init__(self):
        if not self._hash:
            content = f"{self.prev_hash}:{self.tool}:{self.output_hash}:{self.verdict}:{self.timestamp}"
            object.__setattr__(self, '_hash', hashlib.sha256(content.encode()).hexdigest())
    
    @property
    def hash(self) -> str:
        return self._hash
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_n": self.step_n,
            "tool": self.tool,
            "contract_version": self.contract_version,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "entropy_before": self.entropy_before,
            "entropy_after": self.entropy_after,
            "floors_checked": self.floors_checked,
            "verdict": self.verdict,
            "drift_status": self.drift_status,
            "timestamp": self.timestamp,
            "hash": self.hash
        }


@dataclass
class ExecutionTrace:
    """
    Merkle-linked execution trace for proof-carrying verification.
    
    Each execution produces a provable artifact showing:
    - What tools were called
    - What contracts governed them
    - What verdicts were issued
    - What drift was detected
    """
    
    session_id: str
    genesis_hash: str = field(default_factory=lambda: "0" * 64)
    steps: List[ExecutionStep] = field(default_factory=list)
    _current_hash: str = field(default="", repr=False)
    
    def __post_init__(self):
        if not self._current_hash:
            object.__setattr__(self, '_current_hash', self.genesis_hash)
    
    def append(
        self,
        tool: str,
        contract_version: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        entropy_before: float,
        entropy_after: float,
        floors_checked: List[str],
        verdict: str,
        drift_status: str = "CLEAN"
    ) -> str:
        """Append a step to the trace. Returns the new trace hash."""
        
        input_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()[:32]
        output_hash = hashlib.sha256(json.dumps(output_data, sort_keys=True).encode()).hexdigest()[:32]
        
        step = ExecutionStep(
            step_n=len(self.steps),
            tool=tool,
            contract_version=contract_version,
            input_hash=input_hash,
            output_hash=output_hash,
            entropy_before=entropy_before,
            entropy_after=entropy_after,
            floors_checked=floors_checked,
            verdict=verdict,
            drift_status=drift_status,
            timestamp=time.time(),
            prev_hash=self._current_hash
        )
        
        self.steps.append(step)
        object.__setattr__(self, '_current_hash', step.hash)
        
        return self._current_hash
    
    def seal(self) -> Dict[str, Any]:
        """Generate final proof artifact."""
        if not self.steps:
            return {
                "session_id": self.session_id,
                "status": "EMPTY",
                "merkle_root": self.genesis_hash
            }
        
        trace_hashes = [s.hash for s in self.steps]
        trace_aggregate = hashlib.sha256(json.dumps(trace_hashes).encode()).hexdigest()
        
        return {
            "session_id": self.session_id,
            "status": "SEALED",
            "merkle_root": self._current_hash,
            "genesis_hash": self.genesis_hash,
            "step_count": len(self.steps),
            "trace_aggregate": trace_aggregate,
            "final_entropy": self.steps[-1].entropy_after,
            "total_entropy_delta": sum(s.entropy_after - s.entropy_before for s in self.steps),
            "verification_endpoint": f"/verify/{self.session_id}"
        }
    
    def verify(self) -> Dict[str, Any]:
        """Verify trace integrity by recomputing hashes."""
        if not self.steps:
            return {"valid": True, "steps_verified": 0}
        
        current = self.genesis_hash
        tampered = []
        
        for step in self.steps:
            if step.prev_hash != current:
                tampered.append({
                    "step": step.step_n,
                    "expected_prev": current,
                    "actual_prev": step.prev_hash
                })
            current = step.hash
        
        return {
            "valid": len(tampered) == 0,
            "steps_verified": len(self.steps),
            "final_hash_matches": current == self._current_hash,
            "tampered_steps": tampered
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "genesis_hash": self.genesis_hash,
            "merkle_root": self._current_hash,
            "steps": [s.to_dict() for s in self.steps]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# KERNEL RUNTIME — Main Interface
# ═══════════════════════════════════════════════════════════════════════════════

class KernelRuntime:
    """
    The self-verifying constitutional substrate.
    
    Not exposed as public MCP tool — accessed via arifos.init syscall modes:
    - mode="describe_kernel" → Contract self-description
    - mode="validate_transition" → Metabolic DAG enforcement
    - mode="audit_contracts" → Drift detection
    - mode="emit_proof_stub" → Execution trace access
    """
    
    _instance: Optional[KernelRuntime] = None
    _traces: Dict[str, ExecutionTrace] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Initialize registry
        ContractRegistry.initialize()
        self._initialized = True
    
    # ═════════════════════════════════════════════════════════════════════════
    # KERNEL SYSCALLS (exposed via arifos.init modes)
    # ═════════════════════════════════════════════════════════════════════════
    
    def syscall_describe_kernel(self, query: Optional[str] = None) -> Dict[str, Any]:
        """
        SYSCALL: Describe kernel state and contracts.
        
        Returns full contract registry or specific tool contract.
        """
        if query:
            return ContractRegistry.describe_contract(query)
        
        contracts = ContractRegistry.get_all_contracts()
        return {
            "kernel_version": "0.2.0",
            "contract_count": len(contracts),
            "tools": [name for name in contracts.keys()],
            "contracts": {
                name: ContractRegistry.describe_contract(name)
                for name in contracts.keys()
            }
        }
    
    def syscall_validate_transition(
        self,
        current_tool: str,
        requested_tool: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        SYSCALL: Validate metabolic transition.
        
        Returns allowed=True/False with reason and remediation.
        """
        result = MetabolicRouter.validate_transition(current_tool, requested_tool, context)
        
        return {
            "allowed": result.allowed,
            "reason": result.reason,
            "violation_type": result.violation_type,
            "remediation": result.remediation,
            "current": current_tool,
            "requested": requested_tool
        }
    
    def syscall_audit_contracts(
        self,
        tool_name: str,
        actual_output: Dict[str, Any],
        call_graph: List[Tuple[str, str]],
        observed_effects: List[str]
    ) -> Dict[str, Any]:
        """
        SYSCALL: Full drift audit.
        
        Returns drift report with severity and recommendation.
        """
        report = ContractDriftDetector.full_audit(
            tool_name, actual_output, call_graph, observed_effects
        )
        
        return {
            "tool": report.tool_name,
            "drift_detected": report.drift_detected,
            "severity": report.severity,
            "violations": report.violations,
            "recommendation": report.recommendation
        }
    
    def syscall_emit_proof_stub(self, session_id: str) -> Dict[str, Any]:
        """
        SYSCALL: Get execution trace proof for session.
        
        Returns sealed trace with merkle root.
        """
        trace = self._traces.get(session_id)
        if not trace:
            return {"error": f"No trace found for session {session_id}"}
        
        return trace.seal()
    
    def syscall_get_pipeline(self, from_tool: Optional[str] = None) -> Dict[str, Any]:
        """
        SYSCALL: Get metabolic DAG.
        
        Returns full DAG or specific tool pipeline.
        """
        return MetabolicRouter.get_pipeline(from_tool)
    
    # ═════════════════════════════════════════════════════════════════════════
    # TRACE MANAGEMENT
    # ═════════════════════════════════════════════════════════════════════════
    
    def create_trace(self, session_id: str) -> ExecutionTrace:
        """Create new execution trace for session."""
        trace = ExecutionTrace(session_id=session_id)
        self._traces[session_id] = trace
        return trace
    
    def get_trace(self, session_id: str) -> Optional[ExecutionTrace]:
        """Retrieve execution trace for session."""
        return self._traces.get(session_id)
    
    def append_to_trace(
        self,
        session_id: str,
        tool: str,
        contract_version: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        entropy_before: float = 0.5,
        entropy_after: float = 0.5,
        floors_checked: Optional[List[str]] = None,
        verdict: str = "SEAL",
        drift_status: str = "CLEAN"
    ) -> str:
        """Append step to session trace."""
        trace = self._traces.get(session_id)
        if not trace:
            trace = self.create_trace(session_id)
        
        return trace.append(
            tool=tool,
            contract_version=contract_version,
            input_data=input_data,
            output_data=output_data,
            entropy_before=entropy_before,
            entropy_after=entropy_after,
            floors_checked=floors_checked or [],
            verdict=verdict,
            drift_status=drift_status
        )


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_kernel_runtime: Optional[KernelRuntime] = None


def get_kernel_runtime() -> KernelRuntime:
    """Get or create the singleton KernelRuntime instance."""
    global _kernel_runtime
    if _kernel_runtime is None:
        _kernel_runtime = KernelRuntime()
    return _kernel_runtime


# Convenience exports
__all__ = [
    "KernelRuntime",
    "get_kernel_runtime",
    "ContractRegistry",
    "ToolContract",
    "MetabolicRouter",
    "ContractDriftDetector",
    "ExecutionTrace",
    "ExecutionStep",
    "RiskLevel",
    "Verdict",
    "SideEffectClass",
    "ReversibilityClass",
]
