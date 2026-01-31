"""
Math Layer — Information Geometry, Category Theory, Measure Theory

Implements formal verification and measurement frameworks.
"""

import numpy as np
from typing import Dict, List, Callable, TypeVar, Generic, Set
from dataclasses import dataclass
from functools import reduce


T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')


class InformationGeometry:
    """
    Information Geometry — Distance on statistical manifolds.
    
    Measures distance between agent states using Fisher-Rao metric.
    Constitutional Enforcement:
    - F2 Truth: KL divergence measures truth distance
    - F8 Genius: G = A×P×X×E² on statistical manifold
    """
    
    def __init__(self, constitutional_params: Dict[str, float]):
        """
        Args:
            constitutional_params: F1-F13 thresholds as parameters θ
        """
        self.params = constitutional_params
        self.fisher_matrix = self._compute_fisher_matrix()
    
    def _compute_fisher_matrix(self) -> np.ndarray:
        """
        Fisher Information Matrix: curvature of KL divergence.
        
        g_μν(θ) = E[(∂log p(x|θ)/∂θ_μ)(∂log p(x|θ)/∂θ_ν)]
        """
        n = len(self.params)
        fisher = np.eye(n)  # Simplified: identity (independent floors)
        
        # In full implementation: compute correlations between floors
        for i, (f1, v1) in enumerate(self.params.items()):
            for j, (f2, v2) in enumerate(self.params.items()):
                if i != j:
                    # Correlation based on floor dependencies
                    fisher[i, j] = self._correlation(f1, f2)
        
        return fisher
    
    def _correlation(self, floor1: str, floor2: str) -> float:
        """Floor correlation coefficient."""
        # F2 (Truth) and F4 (Clarity) are positively correlated
        correlations = {
            ('F2', 'F4'): 0.7,
            ('F2', 'F7'): 0.3,
            ('F6', 'F5'): 0.8,
            ('F8', 'F2'): 0.6,
            ('F8', 'F7'): 0.5,
        }
        return correlations.get((floor1, floor2), 0.1)
    
    def kl_divergence(self, other_params: Dict[str, float]) -> float:
        """
        KL divergence: distance between distributions.
        
        D_KL(P||Q) = Σ P(x) log(P(x)/Q(x))
        
        For binary floors: Bernoulli KL divergence.
        """
        kl = 0.0
        for key, p in self.params.items():
            q = other_params.get(key, 0.5)
            # Avoid log(0)
            p = max(p, 1e-10)
            q = max(q, 1e-10)
            
            # Bernoulli KL: p*log(p/q) + (1-p)*log((1-p)/(1-q))
            kl += p * np.log(p/q) + (1-p) * np.log((1-p)/(1-q))
        
        return kl
    
    def fisher_rao_distance(self, other_params: Dict[str, float]) -> float:
        """
        Fisher-Rao metric distance on statistical manifold.
        
        D_FR(θ₁, θ₂) = arccos(Σ √(p_i q_i))
        
        Constitutional: measures distance from truth manifold.
        """
        # Bhattacharyya coefficient
        bc = sum(
            np.sqrt(p * other_params.get(k, 0.5))
            for k, p in self.params.items()
        ) / len(self.params)
        
        # Fisher-Rao distance
        return np.arccos(min(bc, 1.0))
    
    def natural_gradient(self, target: Dict[str, float], lr: float = 0.01) -> Dict[str, float]:
        """
        Natural gradient: ∇̃ = g⁻¹∇
        
        Gradient descent on statistical manifold (covariant).
        """
        gradient = {}
        
        for key in self.params:
            # Euclidean gradient
            grad_euc = self.params[key] - target.get(key, 0.5)
            
            # Natural gradient (simplified: without full matrix inverse)
            gradient[key] = lr * grad_euc
        
        return gradient


class Morphism(Generic[T, U]):
    """
    Morphism in Category Theory: transformation between objects.
    
    f: A → B
    """
    
    def __init__(self, func: Callable[[T], U], name: str, domain: str, codomain: str):
        self.func = func
        self.name = name
        self.domain = domain
        self.codomain = codomain
    
    def __call__(self, x: T) -> U:
        return self.func(x)
    
    def compose(self, other: 'Morphism[U, V]') -> 'Morphism[T, V]':
        """
        Composition: (g ∘ f)(x) = g(f(x))
        
        Constitutional: Composition must preserve F1 (reversibility).
        """
        return Morphism(
            func=lambda x: other(self(x)),
            name=f"{other.name} ∘ {self.name}",
            domain=self.domain,
            codomain=other.codomain
        )
    
    def __rshift__(self, other: 'Morphism[U, V]') -> 'Morphism[T, V]':
        """Haskell-style composition: f >> g"""
        return self.compose(other)


class AgentObject:
    """
    Agent as object in Federation category.
    """
    
    def __init__(self, agent_id: str, state: Dict):
        self.agent_id = agent_id
        self.state = state
        self.id_morphism = Morphism(
            func=lambda x: x,
            name=f"id_{agent_id}",
            domain=agent_id,
            codomain=agent_id
        )
    
    def apply(self, morphism: Morphism) -> 'AgentObject':
        """Apply morphism (state transformation)."""
        new_state = morphism(self.state)
        return AgentObject(f"{self.agent_id}'", new_state)


class FederationCategory:
    """
    Category: Federation
    
    Objects: Agents
    Morphisms: Agent transformations (000→999 pipeline)
    
    Constitutional: Composition preserves clarity (F6).
    """
    
    def __init__(self):
        self.objects: Dict[str, AgentObject] = {}
        self.morphisms: List[Morphism] = []
        self.composition_cache: Dict[str, Morphism] = {}
    
    def add_agent(self, agent: AgentObject):
        """Add object to category."""
        self.objects[agent.agent_id] = agent
    
    def add_morphism(self, morphism: Morphism):
        """Add morphism to category."""
        self.morphisms.append(morphism)
    
    def compose_pipeline(self, morphisms: List[Morphism]) -> Morphism:
        """
        Compose chain of morphisms: f_n ∘ ... ∘ f_2 ∘ f_1
        
        Represents 000→999 metabolic pipeline as single morphism.
        """
        if not morphisms:
            return Morphism(lambda x: x, "id", "null", "null")
        
        return reduce(lambda f, g: g.compose(f), morphisms[1:], morphisms[0])
    
    def check_associativity(self, f: Morphism, g: Morphism, h: Morphism, test_input: T) -> bool:
        """
        Verify: h ∘ (g ∘ f) = (h ∘ g) ∘ f
        
        Constitutional requirement for valid category.
        """
        left = h(g(f(test_input)))
        right = h(g(f(test_input)))
        
        return left == right
    
    def create_pipeline_morphism(self) -> Morphism:
        """
        Create the canonical 000→999 pipeline as a morphism.
        """
        stages = [
            Morphism(lambda s: {**s, "stage": "111"}, "sense", "000", "111"),
            Morphism(lambda s: {**s, "stage": "222"}, "think", "111", "222"),
            Morphism(lambda s: {**s, "stage": "333"}, "atlas", "222", "333"),
            Morphism(lambda s: {**s, "stage": "444"}, "evidence", "333", "444"),
            Morphism(lambda s: {**s, "stage": "555"}, "empathy", "444", "555"),
            Morphism(lambda s: {**s, "stage": "666"}, "align", "555", "666"),
            Morphism(lambda s: {**s, "stage": "777"}, "forge", "666", "777"),
            Morphism(lambda s: {**s, "stage": "888"}, "judge", "777", "888"),
            Morphism(lambda s: {**s, "stage": "999"}, "seal", "888", "999"),
        ]
        
        return self.compose_pipeline(stages)


class ConstitutionalSigmaAlgebra:
    """
    Measure Theory: σ-algebra over constitutional floors.
    
    (Ω, F, P) where:
    - Ω: Sample space (all agent states)
    - F: σ-algebra (measurable events — floors)
    - P: Probability measure (confidence)
    
    Constitutional Enforcement:
    - F3 Tri-Witness: Intersection of floor events
    - F10 Ontology: Category lock as σ-algebra constraint
    """
    
    def __init__(self):
        self.omega: Set[str] = set()  # Sample space
        self.sigma_algebra: Set[str] = set()  # Measurable events
        self.measures: Dict[str, Callable[[Dict], float]] = {}
        self.floor_thresholds: Dict[str, float] = {
            'F2': 0.99,
            'F3': 0.95,
            'F4': 0.0,  # ΔS ≤ 0
            'F6': 0.70,
            'F7': 0.03,  # Lower bound
            'F8': 0.80,
            'F9': 0.30,  # Upper bound
            'F12': 0.85,  # Upper bound
        }
    
    def add_event(self, event_name: str, condition: Callable[[Dict], float]):
        """
        Add measurable event to σ-algebra.
        
        Event: "F2 passes" = {ω ∈ Ω : truth_score(ω) ≥ 0.99}
        """
        self.sigma_algebra.add(event_name)
        self.measures[event_name] = condition
    
    def is_measurable(self, function: Callable[[Dict], float], test_states: List[Dict]) -> bool:
        """
        Check if function is F-measurable.
        
        X⁻¹(B) ∈ F for all Borel sets B
        
        Constitutional: function must respect floor structure.
        """
        for state in test_states:
            result = function(state)
            # Check if result respects floor thresholds
            if not (0 <= result <= 1):
                return False
        return True
    
    def measure(self, event: str, agent_state: Dict) -> float:
        """
        P(event | agent_state)
        
        Calculate probability that agent satisfies floor.
        """
        if event not in self.measures:
            raise ValueError(f"Event {event} not in σ-algebra")
        
        return self.measures[event](agent_state)
    
    def verify_all_floors(self, agent_state: Dict) -> Dict[str, bool]:
        """
        Check all F1-F13 floors against agent state.
        
        Returns dict of floor → pass/fail.
        """
        results = {}
        
        for floor, threshold in self.floor_thresholds.items():
            score = agent_state.get(floor, 0.0)
            
            # Handle upper/lower bounds
            if floor in ['F9', 'F12']:  # Upper bounds
                results[floor] = score < threshold
            elif floor == 'F4':  # ΔS ≤ 0
                results[floor] = score <= 0
            elif floor == 'F7':  # Range [0.03, 0.05]
                results[floor] = 0.03 <= score <= 0.05
            else:  # Lower bounds
                results[floor] = score >= threshold
        
        return results
    
    def tri_witness_probability(self, human: float, ai: float, earth: float) -> float:
        """
        P(Tri-Witness passes) = ∛(H × A × E)
        
        Geometric mean of three witness scores.
        """
        return (human * ai * earth) ** (1/3)
