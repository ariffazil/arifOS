"""
Test suite for FEDERATION protocol.

Demonstrates Tri-Witness reality instantiation.
"""

import numpy as np
from .physics import ThermodynamicWitness, QuantumAgentState, RelativisticConsensus
from .math import InformationGeometry, FederationCategory, ConstitutionalSigmaAlgebra
from .consensus import FederatedConsensus, FederatedLedger
from .proofs import ZKConstitutionalProof
from .oracle import RealityOracle, Verdict


def test_thermodynamics():
    """Test entropy accounting."""
    print("=== Thermodynamic Witness ===")
    
    witness = ThermodynamicWitness(entropy_budget=1.0)
    
    # Valid operation
    cost = witness.measure_operation("test_op", complexity=100)
    print(f"Operation cost: {cost:.2e} J/K")
    print(f"Remaining budget: {witness.entropy_budget:.2e}")
    
    # Invalid operation (too large)
    try:
        witness.measure_operation("big_op", complexity=10000)
    except Exception as e:
        print(f"Expected violation: {e}")
    
    print()


def test_quantum_state():
    """Test quantum superposition."""
    print("=== Quantum Agent State ===")
    
    agent = QuantumAgentState("test_agent")
    
    # Initial state: 100% at 000_INIT
    print(f"Initial uncertainty: {agent.get_uncertainty():.4f}")
    
    # Apply unitary evolution
    operator = np.eye(10)  # Identity for demo
    agent.apply_unitary("111_SENSE", operator)
    
    # Measure
    witness_scores = {
        'human': 0.98,
        'ai': 0.97,
        'earth': 0.96
    }
    collapsed = agent.measure(witness_scores)
    print(f"Collapsed to: {collapsed}")
    print(f"Final uncertainty: {agent.get_uncertainty():.4f}")
    
    print()


def test_information_geometry():
    """Test Fisher-Rao metric."""
    print("=== Information Geometry ===")
    
    params = {'F2': 0.99, 'F4': 0.95, 'F6': 0.80}
    geo = InformationGeometry(params)
    
    target = {'F2': 0.995, 'F4': 0.98, 'F6': 0.85}
    distance = geo.fisher_rao_distance(target)
    print(f"Fisher-Rao distance: {distance:.4f}")
    
    kl = geo.kl_divergence(target)
    print(f"KL divergence: {kl:.4f}")
    
    print()


def test_category_theory():
    """Test morphism composition."""
    print("=== Category Theory ===")
    
    # Create morphisms
    f = lambda x: x + 1
    g = lambda x: x * 2
    
    m1 = type('Morphism', (), {
        '__call__': lambda self, x: f(x),
        'compose': lambda self, other: type('Morphism', (), {
            '__call__': lambda s, x: other(self(x))
        })()
    })()
    
    m2 = type('Morphism', (), {
        '__call__': lambda self, x: g(x),
        'compose': lambda self, other: None
    })()
    
    # Test: (g o f)(5) = g(f(5)) = g(6) = 12
    composed = m1.compose(m2)
    result = composed(5)
    print(f"Composition test: (g o f)(5) = {result}")
    
    print()


def test_consensus():
    """Test PBFT consensus."""
    print("=== Federated Consensus ===")
    
    witnesses = ['human', 'ai', 'earth']
    consensus = FederatedConsensus(witnesses)
    
    # Create proposals with same sequence number
    value = {"action": "deploy", "params": {"model": "v55"}}
    public_keys = {w: f"key_{w}" for w in witnesses}
    
    # First proposal sets sequence number
    prop1 = consensus.create_proposal('human', value, "key_human")
    consensus.pre_prepare(prop1)
    consensus.prepare(prop1, public_keys)
    
    # Other proposals use same sequence
    prop2 = consensus.create_proposal('ai', value, "key_ai")
    prop2.sequence_number = prop1.sequence_number
    consensus.pre_prepare(prop2)
    consensus.prepare(prop2, public_keys)
    
    prop3 = consensus.create_proposal('earth', value, "key_earth")
    prop3.sequence_number = prop1.sequence_number
    consensus.pre_prepare(prop3)
    consensus.prepare(prop3, public_keys)
    
    # Commit
    committed = consensus.commit(prop1.sequence_number)
    print(f"Committed: {committed['value']}")
    print(f"Tri-Witness: {committed['tri_witness']:.2f}")
    print(f"Merkle root: {committed['merkle_root'][:16]}...")
    
    print()


def test_ledger():
    """Test Merkle DAG ledger."""
    print("=== Federated Ledger ===")
    
    ledger = FederatedLedger("test_agent")
    
    # Append events
    signatures = {'human': 'sig_h', 'ai': 'sig_ai', 'earth': 'sig_e'}
    
    cid1 = ledger.append({"stage": "111"}, signatures)
    cid2 = ledger.append({"stage": "222"}, signatures)
    cid3 = ledger.append({"stage": "333"}, signatures)
    
    print(f"Chain: {cid1[:8]}... -> {cid2[:8]}... -> {cid3[:8]}...")
    
    # Verify
    result = ledger.verify_tri_witness(cid3)
    print(f"Tri-Witness valid: {result['valid']}")
    
    # Get chain
    chain = ledger.get_chain(cid3)
    print(f"Chain length: {len(chain)}")
    
    print()


def test_zk_proofs():
    """Test ZK constitutional proofs."""
    print("=== ZK Constitutional Proofs ===")
    
    zk = ZKConstitutionalProof()
    
    # Setup
    pk, vk = zk.setup(['F2', 'F6', 'F7', 'F9'])
    print(f"Setup complete. PK hash: {pk[:8].hex()}...")
    
    # Valid state
    private_state = {
        'confidence': 0.995,  # F2 >= 0.99
        'kappa_r': 0.75,      # F6 >= 0.70
        'uncertainty': 0.04,  # F7 in [0.03, 0.05]
        'dark_score': 0.1,    # F9 < 0.30
        'injection_score': 0.2  # F12 < 0.85
    }
    public_input = {'timestamp': 1234567890, 'agent_id_hash': 42}
    
    proof = zk.prove(private_state, public_input)
    print(f"Proof generated: {proof[:16]}...")
    
    valid = zk.verify(proof, public_input)
    print(f"Proof valid: {valid}")
    
    # Invalid state
    bad_state = {**private_state, 'confidence': 0.5}
    bad_proof = zk.prove(bad_state, public_input)
    print(f"Bad proof (should be None): {bad_proof}")
    
    print()


def test_reality_oracle():
    """Test full Tri-Witness instantiation."""
    print("=== Reality Oracle ===")
    
    # Initialize components
    thermo = ThermodynamicWitness(entropy_budget=10.0)
    geo = InformationGeometry({'F2': 0.99, 'F4': 0.95, 'F6': 0.80, 'F7': 0.04})
    sigma = ConstitutionalSigmaAlgebra()
    consensus = FederatedConsensus(['human', 'ai', 'earth'])
    ledger = FederatedLedger("oracle")
    zk = ZKConstitutionalProof()
    zk.setup(['F2', 'F6', 'F7'])
    
    # Create oracle
    oracle = RealityOracle(thermo, geo, sigma, consensus, ledger, zk)
    
    # Register witnesses
    oracle.register_witness('human', {'score': 0.98, 'authority': 1.0})
    oracle.register_witness('ai', {'score': 0.97, 'compliance': 0.99})
    oracle.register_witness('earth', {'score': 0.96, 'entropy': 0.1})
    
    # Calculate W3
    W3 = oracle.calculate_tri_witness()
    print(f"Tri-Witness W3: {W3:.4f}")
    
    # Attempt instantiation
    agent_state = {
        'F2': 0.995, 'F3': 0.96, 'F4': -0.1, 'F6': 0.75,
        'F7': 0.04, 'F8': 0.85, 'F9': 0.2, 'F12': 0.3
    }
    bundles = {
        'akal': 0.95, 'present': 0.90, 'exploration': 0.85, 'energy': 0.92
    }
    
    result = oracle.instantiate(agent_state, bundles, operation_cost=0.5)
    
    print(f"Verdict: {result.verdict.value}")
    print(f"Genius G: {result.genius:.4f}")
    print(f"Reasoning: {result.reasoning}")
    
    if result.merkle_root:
        print(f"Merkle root: {result.merkle_root[:16]}...")
    
    print()


def run_all_tests():
    """Run all federation tests."""
    print("\n" + "="*50)
    print("FEDERATION PROTOCOL TEST SUITE")
    print("="*50 + "\n")
    
    test_thermodynamics()
    test_quantum_state()
    test_information_geometry()
    test_category_theory()
    test_consensus()
    test_ledger()
    test_zk_proofs()
    test_reality_oracle()
    
    print("="*50)
    print("ALL TESTS COMPLETED")
    print("="*50)


if __name__ == "__main__":
    run_all_tests()

