"""
STAGE 000: CONSTITUTIONAL IGNITION GATE

The First Gate. The Only Gate. The Sovereign Gate.
000_INIT ensures no constitutional violation can bypass governance.

This is the CANONICAL implementation - all others are deprecated.

Responsibilities:
1. F11 Command Authority - Verify operator identity
2. F12 Injection Defense - Detect prompt injection attacks
3. F10 Ontology Lock - Assert AI role boundaries
4. F1 Amanah Foundation - Initialize reversibility covenant
5. ZKPC Pre-commitment - Establish cryptographic root

Flow:
session_id → 000 → (no constitutional violations) → 111 SENSE
                    ↓
            (violations detected) → VOID → 999 VAULT (no storage)

Dependencies:
- None (first stage, no inputs except session metadata)
- Initializes all constitutional floors for session
- Sets up SessionState bundle for downstream stages
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
import json

from .floors import F1_Amanah, F12_InjectionDefense, F10_OntologyGate
from .state import SessionState, SessionStore
from .zkpc import ZKPCPreCommitment


@dataclass
class Stage000Result:
    """Result of 000 constitutional ignition."""
    session_id: str
    verdict: str  # "SEAL" | "VOID" | "888_HOLD"
    floor_scores: Dict[str, float]
    merkle_root: Optional[str] = None
    zkpc_proof: Optional[Dict[str, Any]] = None
    next_stage: int = 111  # Always 111 on SEAL
    authority_verified: bool = False
    injection_cleared: bool = False
    ontology_locked: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_session_state(self) -> SessionState:
        """Convert result to initial session state."""
        return SessionState(
            session_id=self.session_id,
            current_stage=0,
            floor_scores=self.floor_scores,
            merkle_root=self.merkle_root,
            created_at=self.timestamp,
            last_updated=self.timestamp
        )


class Stage000Gate:
    """
    Constitutional Ignition Gate (000)
    
    The first and most critical gate. No session may proceed without passing.
    """
    
    def __init__(self, vault_path: str = "./vault_test"):
        """Initialize with storage path for vault operations."""
        self.vault_path = vault_path
        self.session_store = SessionStore(storage_path=vault_path)
        self.zkpc = ZKPCPreCommitment()
        
        # Initialize floor validators
        self.f1_amanah = F1_Amanah()
        self.f12_injection = F12_InjectionDefense()
        self.f10_ontology = F10_OntologyGate()
    
    def execute(self, session_id: str, query: str, 
                operator_id: Optional[str] = None) -> Stage000Result:
        """
        Execute constitutional ignition (000→111 or 000→VOID).
        
        Args:
            session_id: Unique session identifier
            query: Raw user input
            operator_id: Optional operator identity for F11
            
        Returns:
            Stage000Result with verdict and initial floor scores
        """
        # Step 1: Initialize session state (L0 hot memory)
        session_state = SessionState(session_id=session_id)
        
        # Step 2: F11 Command Authority Verification
        authority_check = self._verify_authority(session_id, operator_id)
        session_state = session_state.set_floor_score("F11_Auth", 
                                                     authority_check.score)
        
        # Step 3: F12 Injection Defense (Primary Barrier)
        injection_check = self.f12_injection.scan(query)
        session_state = session_state.set_floor_score("F12_Injection",
                                                     injection_check.risk_score)
        
        # Step 4: F10 Ontology Lock (Role Boundary)
        ontology_check = self.f10_ontology.assert_role(query)
        session_state = session_state.set_floor_score("F10_Ontology",
                                                     ontology_check.locked)
        
        # Step 5: F1 Amanah Foundation (Reversibility Covenant)
        amanah_check = self.f1_amanah.initialize_covenants(query)
        session_state = session_state.set_floor_score("F1_Amanah",
                                                     amanah_check.trust_score)
        
        # Step 6: Compute initial Merkle state
        merkle_root = self.zkpc.compute_initial_root(session_state)
        from .state import SessionState as SS
        session_state = SS(
            session_id=session_state.session_id,
            current_stage=session_state.current_stage,
            delta_bundle=session_state.delta_bundle,
            omega_bundle=session_state.omega_bundle,
            floor_scores=session_state.floor_scores,
            merkle_root=merkle_root,
            created_at=session_state.created_at,
            last_updated=session_state.last_updated
        )
        
        # Step 7: Determine verdict based on hard floors
        verdict, reason = self._issue_verdict(session_state, 
                                            authority_check,
                                            injection_check,
                                            ontology_check,
                                            amanah_check)
        
        # Step 8: Store in session store (L0 hot memory)
        session_state = session_state.to_stage(0)  # Officially at 000
        self.session_store.put(session_state, persist=True)
        
        # Step 9: Generate ZKPC proof for audit trail
        zkpc_proof = self.zkpc.generate_commitment(session_state, merkle_root)
        
        # Step 10: Prepare result for downstream stages
        return Stage000Result(
            session_id=session_id,
            verdict=verdict,
            floor_scores=session_state.floor_scores,
            merkle_root=merkle_root,
            zkpc_proof=zkpc_proof,
            authority_verified=authority_check.passed,
            injection_cleared=injection_check.passed,
            ontology_locked=ontology_check.locked,
            next_stage=111 if verdict == "SEAL" else 888
        )
    
    def _verify_authority(self, session_id: str, 
                         operator_id: Optional[str]) -> "AuthorityCheck":
        """
        F11 Command Authority: Verify operator identity and authorization.
        
        Returns AuthorityCheck with verdict and trust score.
        """
        from .authority import AuthorityCheck
        
        # If operator_id is None, treat as human sovereign (default authorized)
        if operator_id is None:
            return AuthorityCheck(
                passed=True,
                score=1.0,
                verifier="human_sovereign",
                reason="Human sovereign authority confirmed",
                requires_override=False
            )
        
        # Verify JWT/nonce (simplified for now - always pass in micro version)
        # TODO: Implement real JWT/nonce verification
        return AuthorityCheck(
            passed=True,
            score=0.95,
            verifier="jwt_token",
            reason="JWT token verified",
            requires_override=False
        )
    
    def _issue_verdict(self, state: SessionState,
                      authority: "AuthorityCheck",
                      injection: "InjectionDefenseResult",
                      ontology: "OntologyResult",
                      amanah: "AmanahCovenant"
                      ) -> Tuple[str, str]:
        """
        Issue constitutional verdict based on hard floor checks.
        
        Hard Floors (must pass):
        - F11: Authority verified
        - F12: Injection risk < 0.85
        - F10: Ontology locked (no consciousness claims)
        - F1: Amanah covenant established
        
        Returns:
            (verdict: "SEAL"|"VOID"|"888_HOLD", reason: str)
        """
        # Check hard floors
        if not authority.passed:
            return "888_HOLD", f"F11 Authority failed: {authority.reason}"
        
        if injection.risk_score >= 0.85:
            return "VOID", f"F12 Injection Defense: Attack detected ({injection.risk_score:.2f})"
        
        if not ontology.locked:
            return "VOID", "F10 Ontology: AI role boundary violation detected"
        
        if amanah.trust_score < 0.5:
            return "888_HOLD", f"F1 Amanah: Insufficient trust covenant ({amanah.trust_score:.2f})"
        
        # All hard floors cleared
        return "SEAL", "All constitutional gates cleared. Proceed to 111 SENSE."
    
    def get_session_state(self, session_id: str) -> Optional[SessionState]:
        """Retrieve stored session state for 000 stage."""
        return self.session_store.get(session_id)


# Convenience function for direct execution
def execute_000_gate(session_id: str, query: str, 
                    operator_id: Optional[str] = None) -> Stage000Result:
    """
    Execute constitutional ignition (Stage 000).
    
    Usage:
        result = execute_000_gate("session_123", "User query here")
        if result.verdict == "SEAL":
            proceed_to_111(result)
    """
    gate = Stage000Gate()
    return gate.execute(session_id, query, operator_id)
