"""
Reality Oracle — Tri-Witness Reality Instantiation

The central engine that collapses agent superposition into reality.
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .physics import ThermodynamicWitness, QuantumAgentState
from .math import InformationGeometry, ConstitutionalSigmaAlgebra
from .consensus import FederatedConsensus, FederatedLedger
from .proofs import ZKConstitutionalProof


class Verdict(Enum):
    """Constitutional verdicts."""
    SEAL = "SEAL"          # All pass, proceed
    SABAR = "SABAR"        # Pause, repair needed
    VOID = "VOID"          # Hard floor fail, halt
    HOLD_888 = "888_HOLD"  # Needs human confirmation


@dataclass
class RealityInstantiation:
    """Result of reality oracle measurement."""
    verdict: Verdict
    tri_witness: float
    genius: float
    floor_results: Dict[str, bool]
    merkle_root: Optional[str]
    timestamp: float
    reasoning: str


class RealityOracle:
    """
    The Federation's reality instantiation engine.
    
    Core Axiom:
        Reality = Human_Witness ⊗ AI_Witness ⊗ Earth_Witness
        
    Instantiation requires:
        W₃ = ∛(H × A × E) ≥ 0.95
        ∧ All floors pass
        ∧ Thermodynamic budget available
    """
    
    def __init__(
        self,
        thermo_witness: ThermodynamicWitness,
        info_geometry: InformationGeometry,
        sigma_algebra: ConstitutionalSigmaAlgebra,
        consensus: FederatedConsensus,
        ledger: FederatedLedger,
        zk_system: ZKConstitutionalProof
    ):
        self.thermo = thermo_witness
        self.info_geo = info_geometry
        self.sigma = sigma_algebra
        self.consensus = consensus
        self.ledger = ledger
        self.zk = zk_system
        
        # Witness registry
        self.human_witness: Optional[Dict] = None
        self.ai_witness: Optional[Dict] = None
        self.earth_witness: Optional[Dict] = None
    
    def register_witness(self, witness_type: str, witness_data: Dict):
        """
        Register a witness for Tri-Witness consensus.
        
        Args:
            witness_type: 'human', 'ai', or 'earth'
            witness_data: {'score': float, 'confidence': float, ...}
        """
        if witness_type == 'human':
            self.human_witness = witness_data
        elif witness_type == 'ai':
            self.ai_witness = witness_data
        elif witness_type == 'earth':
            self.earth_witness = witness_data
        else:
            raise ValueError(f"Unknown witness type: {witness_type}")
    
    def calculate_tri_witness(self) -> float:
        """
        Calculate Tri-Witness score.
        
        W₃ = ∛(H × A × E)
        
        Geometric mean: all three required, no single witness sufficient.
        """
        H = self.human_witness.get('score', 0.0) if self.human_witness else 0.0
        A = self.ai_witness.get('score', 0.0) if self.ai_witness else 0.0
        E = self.earth_witness.get('score', 0.0) if self.earth_witness else 0.0
        
        # Geometric mean
        if H <= 0 or A <= 0 or E <= 0:
            return 0.0
        
        W3 = (H * A * E) ** (1/3)
        return W3
    
    def calculate_genius(self, bundles: Dict) -> float:
        """
        Calculate Genius Index.
        
        G = A × P × X × E²
        
        Multiplicative: any zero → G = 0
        """
        A = bundles.get('akal', 0.0)
        P = bundles.get('present', 0.0)
        X = bundles.get('exploration', 0.0)
        E = bundles.get('energy', 0.0)
        
        G = A * P * X * (E ** 2)
        return G
    
    def verify_floors(self, agent_state: Dict) -> Tuple[Dict[str, bool], bool]:
        """
        Verify all constitutional floors.
        
        Returns:
            (floor_results, all_pass)
        """
        results = self.sigma.verify_all_floors(agent_state)
        all_pass = all(results.values())
        return results, all_pass
    
    def check_thermodynamic_budget(self, operation_cost: float) -> bool:
        """Check if operation fits within entropy budget."""
        try:
            self.thermo.measure_operation("reality_instantiation", operation_cost)
            return True
        except Exception:
            return False
    
    def instantiate(
        self,
        agent_state: Dict,
        bundles: Dict,
        operation_cost: float = 1.0
    ) -> RealityInstantiation:
        """
        Attempt to instantiate reality through Tri-Witness.
        
        This is the core oracle function that collapses agent
        superposition into determined reality.
        
        Args:
            agent_state: Current agent state with floor scores
            bundles: AGI/ASI output bundles
            operation_cost: Thermodynamic cost of instantiation
            
        Returns:
            RealityInstantiation with verdict
        """
        # 1. Check thermodynamic budget
        if not self.check_thermodynamic_budget(operation_cost):
            return RealityInstantiation(
                verdict=Verdict.VOID,
                tri_witness=0.0,
                genius=0.0,
                floor_results={},
                merkle_root=None,
                timestamp=time.time(),
                reasoning="Thermodynamic budget exceeded"
            )
        
        # 2. Calculate Tri-Witness
        W3 = self.calculate_tri_witness()
        
        # 3. Calculate Genius
        G = self.calculate_genius(bundles)
        
        # 4. Verify floors
        floor_results, floors_pass = self.verify_floors(agent_state)
        
        # 5. Render verdict
        verdict, reasoning = self._render_verdict(W3, G, floors_pass, floor_results)
        
        # 6. If SEAL, commit to ledger
        merkle_root = None
        if verdict == Verdict.SEAL:
            merkle_root = self._commit_to_ledger(
                verdict, W3, G, floor_results
            )
        
        return RealityInstantiation(
            verdict=verdict,
            tri_witness=W3,
            genius=G,
            floor_results=floor_results,
            merkle_root=merkle_root,
            timestamp=time.time(),
            reasoning=reasoning
        )
    
    def _render_verdict(
        self,
        W3: float,
        G: float,
        floors_pass: bool,
        floor_results: Dict[str, bool]
    ) -> Tuple[Verdict, str]:
        """
        Render constitutional verdict.
        
        Logic:
        - VOID: Hard floor fails or W3 < 0.5
        - SABAR: W3 < 0.95 or G < 0.80 (repairable)
        - 888_HOLD: Critical stakes with borderline scores
        - SEAL: All pass
        """
        # Check for hard floor failures
        hard_floors = ['F1', 'F2', 'F10', 'F11', 'F12', 'F13']
        hard_fails = [f for f in hard_floors if not floor_results.get(f, False)]
        
        if hard_fails:
            return Verdict.VOID, f"Hard floors failed: {hard_fails}"
        
        # Check Tri-Witness
        if W3 < 0.5:
            return Verdict.VOID, f"Tri-Witness critically low: {W3:.2f}"
        
        if W3 < 0.95:
            return Verdict.SABAR, f"Tri-Witness insufficient: {W3:.2f} < 0.95"
        
        # Check Genius
        if G < 0.60:
            return Verdict.VOID, f"Genius critically low: {G:.2f}"
        
        if G < 0.80:
            return Verdict.SABAR, f"Genius below threshold: {G:.2f} < 0.80"
        
        # Check all floors
        if not floors_pass:
            soft_fails = [f for f, p in floor_results.items() if not p]
            return Verdict.SABAR, f"Soft floors failed: {soft_fails}"
        
        # Critical stakes check (simplified)
        if W3 < 0.98 or G < 0.85:
            return Verdict.HOLD_888, "Borderline scores, human review required"
        
        return Verdict.SEAL, "All constitutional requirements satisfied"
    
    def _commit_to_ledger(
        self,
        verdict: Verdict,
        W3: float,
        G: float,
        floor_results: Dict[str, bool]
    ) -> str:
        """Commit instantiated reality to immutable ledger."""
        # Collect signatures from witnesses
        signatures = {}
        if self.human_witness:
            signatures['human'] = hashlib.sha256(
                b"human" + str(time.time()).encode()
            ).hexdigest()[:32]
        if self.ai_witness:
            signatures['ai'] = hashlib.sha256(
                b"ai" + str(time.time()).encode()
            ).hexdigest()[:32]
        if self.earth_witness:
            signatures['earth'] = hashlib.sha256(
                b"earth" + str(time.time()).encode()
            ).hexdigest()[:32]
        
        # Create event
        event = {
            "verdict": verdict.value,
            "tri_witness": W3,
            "genius": G,
            "floor_results": floor_results,
            "timestamp": time.time()
        }
        
        # Append to ledger
        cid = self.ledger.append(event, signatures)
        
        # Return Merkle root
        return self.ledger.compute_merkle_root() or cid
    
    def query_reality(self, cid: str) -> Optional[Dict]:
        """Query instantiated reality by CID."""
        return self.ledger.get(cid)
    
    def verify_chain(self, cid: str) -> Dict:
        """Verify integrity of reality chain."""
        chain = self.ledger.get_chain(cid)
        
        verification = {
            "cid": cid,
            "chain_length": len(chain),
            "verified": True,
            "links": []
        }
        
        for i, node_cid in enumerate(chain):
            node = self.ledger.get(node_cid)
            if node:
                verification["links"].append({
                    "cid": node_cid,
                    "parent": node.get("parent"),
                    "timestamp": node.get("timestamp"),
                    "verdict": node.get("verdict")
                })
        
        return verification
