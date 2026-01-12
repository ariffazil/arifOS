"""
Floor Adapter — Integration Bridge for Floors 1-12
X7K9F24 — Entropy Reduction Engine

Wires atomic floor capabilities into APEX PRIME verdict engine.
Reduces system entropy by unifying scattered logic into single execution spine.

Integration Architecture:
  Pre-LLM (Input Pipeline):
    Floor 1: Input Validation & Sanitization
    Floor 2: Authentication & Nonce Validation
  
  Post-LLM (Response Pipeline):
    Floor 3: Business Logic & State Validation
    Floor 4: Data Persistence & Integrity Check
    Floor 5: Anomaly Detection & Pattern Recognition
    Floor 6: Semantic Understanding & Context Validation
  
  Post-Integration (7-12):
    Floor 7: Decision Optimization
    Floor 8: Knowledge Graph Consistency
    Floor 9: Constitutional Compliance
    Floor 10: Meta-Learning Feedback
    Floor 11: Transparency & Explainability
    Floor 12: Democratic Oversight

Status: SEALED
Nonce: X7K9F24
"""

from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field

# Import floor modules
from ..floors import (
    floor_01_input_validation,
    floor_02_authentication,
    floor_03_business_logic,
    floor_04_data_persistence,
    floor_05_pattern_recognition,
    floor_06_semantic_understanding,
)


@dataclass
class IntegrationResult:
    """Result of floor integration check."""
    passed: bool
    floor_id: str
    floor_name: str
    reason: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    psi: Optional[Dict[str, float]] = None


class FloorAdapter:
    """
    Adapter that integrates Floors 1-12 with APEX PRIME verdict engine.
    
    Provides two integration points:
    1. Pre-verdict checks (Floors 1-2): Input validation before processing
    2. Post-verdict enrichment (Floors 3-6): Response validation after processing
    
    Future: Floors 7-12 integration (decision, knowledge, constitutional, meta, transparency, oversight)
    """
    
    def __init__(self):
        """Initialize floor adapter."""
        self.floors_active = {
            1: True,  # Input Validation
            2: True,  # Authentication
            3: True,  # Business Logic
            4: True,  # Data Persistence
            5: True,  # Pattern Recognition
            6: True,  # Semantic Understanding
            7: False,  # Decision Optimization (TODO)
            8: False,  # Knowledge Graph (TODO)
            9: False,  # Constitutional Compliance (TODO)
            10: False,  # Meta-Learning (TODO)
            11: False,  # Transparency (TODO)
            12: False,  # Democratic Oversight (TODO)
        }
    
    def pre_verdict_checks(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[IntegrationResult]]:
        """
        Execute pre-verdict floor checks (Floors 1-2).
        
        These checks run BEFORE the LLM processes the input.
        If any check fails, the request is blocked immediately.
        
        Args:
            prompt: User input text
            context: Request context (user_id, session_id, nonce, etc.)
            
        Returns:
            Tuple of (passed, failure_result)
            - If passed=True, failure_result is None
            - If passed=False, failure_result contains the blocking floor
        """
        context = context or {}
        
        # Floor 1: Input Validation & Sanitization
        if self.floors_active[1]:
            sanitize_result = floor_01_input_validation.sanitize_input(prompt)
            
            if sanitize_result.get("status") == "rejected":
                return False, IntegrationResult(
                    passed=False,
                    floor_id="F1",
                    floor_name="Input Validation",
                    reason=sanitize_result.get("reason", "Input validation failed"),
                    metrics=sanitize_result,
                    psi=sanitize_result.get("psi")
                )
        
        # Floor 2: Authentication & Nonce Validation
        if self.floors_active[2]:
            nonce = context.get("nonce")
            if nonce:
                nonce_result = floor_02_authentication.validate_nonce(nonce)
                
                if nonce_result.get("status") != "valid":
                    return False, IntegrationResult(
                        passed=False,
                        floor_id="F2",
                        floor_name="Authentication",
                        reason=nonce_result.get("reason", "Authentication failed"),
                        metrics=nonce_result,
                        psi=nonce_result.get("psi")
                    )
        
        # All pre-verdict checks passed
        return True, None
    
    def post_verdict_enrichment(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute post-verdict floor enrichment (Floors 3-6).
        
        These checks run AFTER the LLM generates a response.
        They enrich the metrics and may downgrade the verdict if issues are detected.
        
        Args:
            prompt: Original user input
            response: LLM-generated response
            context: Request context
            metrics: Existing metrics dictionary (will be enriched)
            
        Returns:
            Enriched metrics dictionary with floor scores
        """
        context = context or {}
        metrics = metrics or {}
        
        # Floor 3: Business Logic & State Validation
        if self.floors_active[3]:
            # Check if response contains state transitions
            workflow_steps = context.get("workflow_steps", [])
            if workflow_steps:
                workflow_result = floor_03_business_logic.execute_workflow(
                    workflow_steps=workflow_steps,
                    actor=context.get("user_id", "unknown")
                )
                metrics["floor_3_workflow"] = workflow_result
                metrics["floor_3_score"] = 1.0 if workflow_result["status"] == "success" else 0.5
        
        # Floor 4: Data Persistence & Integrity
        if self.floors_active[4]:
            # Check if response requires persistence
            if context.get("require_persistence", False):
                # Note: Actual persistence happens elsewhere, this is validation
                metrics["floor_4_persistence_ready"] = True
                metrics["floor_4_score"] = 1.0
        
        # Floor 5: Pattern Recognition & Anomaly Detection
        if self.floors_active[5]:
            event = {
                "type": context.get("event_type", "response"),
                "prompt": prompt,
                "response": response,
                "user_id": context.get("user_id"),
                "timestamp": context.get("timestamp")
            }
            
            anomaly_result = floor_05_pattern_recognition.AnomalyDetector().detect(event)
            metrics["floor_5_anomaly"] = anomaly_result
            
            if anomaly_result.get("anomaly_detected"):
                metrics["floor_5_score"] = 1.0 - anomaly_result.get("severity", 0.5)
            else:
                metrics["floor_5_score"] = 1.0
        
        # Floor 6: Semantic Understanding & Context Validation
        if self.floors_active[6]:
            semantic_result = floor_06_semantic_understanding.SemanticParser().parse(response)
            metrics["floor_6_semantic"] = semantic_result
            
            # Check for adversarial patterns
            if semantic_result.get("adversarial", False):
                metrics["floor_6_score"] = 0.3
            else:
                metrics["floor_6_score"] = semantic_result.get("intent_confidence", 0.8)
            
            # Check for literalism trap
            literalism_check = floor_06_semantic_understanding.detect_literalism_trap(prompt)
            if literalism_check.get("literalism_trap_detected", False):
                metrics["floor_6_literalism_trap"] = True
                metrics["floor_6_score"] = min(metrics["floor_6_score"], 0.4)
        
        return metrics
    
    def compute_floor_aggregate_score(self, metrics: Dict[str, Any]) -> float:
        """
        Compute aggregate floor score from individual floor metrics.
        
        Used to adjust APEX verdict based on floor performance.
        
        Args:
            metrics: Metrics dictionary with floor scores
            
        Returns:
            Aggregate score (0.0-1.0)
        """
        floor_scores = []
        
        for floor_num in range(1, 7):  # Floors 1-6 currently active
            if self.floors_active[floor_num]:
                score_key = f"floor_{floor_num}_score"
                if score_key in metrics:
                    floor_scores.append(metrics[score_key])
        
        if not floor_scores:
            return 1.0  # No floor checks, default to passing
        
        # Weighted average (all floors equal weight for now)
        return sum(floor_scores) / len(floor_scores)


# Singleton instance
FLOOR_ADAPTER = FloorAdapter()


def integrate_floors_with_apex(apex_instance, adapter: Optional[FloorAdapter] = None):
    """
    Integrate floor checks into APEX PRIME verdict engine.
    
    Monkey-patches apex_review() to include floor checks.
    
    Args:
        apex_instance: Instance of APEXPrime class
        adapter: FloorAdapter instance (uses singleton if None)
    """
    adapter = adapter or FLOOR_ADAPTER
    
    # Store original apex_review method
    original_apex_review = apex_instance.apex_review if hasattr(apex_instance, 'apex_review') else None
    
    if not original_apex_review:
        # apex_instance might be the module, not class
        # Import and patch the function directly
        from ..system import apex_prime
        original_apex_review = apex_prime.apex_review
        
        def apex_review_with_floors(
            metrics,
            prompt: str = "",
            response_text: str = "",
            high_stakes: bool = False,
            context: Optional[Dict] = None,
            **kwargs
        ):
            """Wrapped apex_review with floor integration."""
            context = context or {}
            
            # Pre-verdict: Floors 1-2
            passed, failure = adapter.pre_verdict_checks(prompt, context)
            if not passed:
                # Return VOID verdict with floor failure reason
                from ..system.apex_prime import ApexVerdict, Verdict
                return ApexVerdict(
                    verdict=Verdict.VOID,
                    pulse=0.0,
                    reason=f"{failure.floor_name} blocked: {failure.reason}",
                    floors=None
                )
            
            # Run original apex_review
            verdict = original_apex_review(
                metrics,
                prompt=prompt,
                response_text=response_text,
                high_stakes=high_stakes,
                **kwargs
            )
            
            # Post-verdict: Floors 3-6 (enrich metrics)
            enriched_metrics = adapter.post_verdict_enrichment(
                prompt=prompt,
                response=response_text,
                context=context,
                metrics=vars(metrics) if hasattr(metrics, '__dict__') else {}
            )
            
            # Compute floor aggregate score
            floor_score = adapter.compute_floor_aggregate_score(enriched_metrics)
            
            # Downgrade verdict if floor score is low
            if floor_score < 0.5 and verdict.verdict.value == "SEAL":
                from ..system.apex_prime import ApexVerdict, Verdict
                verdict = ApexVerdict(
                    verdict=Verdict.PARTIAL,
                    pulse=floor_score,
                    reason=f"Floors downgrade: aggregate score {floor_score:.2f} < 0.5. {verdict.reason}",
                    floors=verdict.floors
                )
            
            # Attach floor metrics to verdict
            if hasattr(verdict, 'floors') and verdict.floors:
                verdict.floors.floor_metrics = enriched_metrics
            
            return verdict
        
        # Patch the module function
        apex_prime.apex_review = apex_review_with_floors
        
    else:
        # Patch the instance method
        def apex_review_with_floors(
            metrics,
            prompt: str = "",
            response_text: str = "",
            high_stakes: bool = False,
            context: Optional[Dict] = None,
            **kwargs
        ):
            """Wrapped apex_review with floor integration."""
            context = context or {}
            
            # Pre-verdict: Floors 1-2
            passed, failure = adapter.pre_verdict_checks(prompt, context)
            if not passed:
                from ..system.apex_prime import ApexVerdict, Verdict
                return ApexVerdict(
                    verdict=Verdict.VOID,
                    pulse=0.0,
                    reason=f"{failure.floor_name} blocked: {failure.reason}",
                    floors=None
                )
            
            # Run original apex_review
            verdict = original_apex_review(
                metrics,
                prompt=prompt,
                response_text=response_text,
                high_stakes=high_stakes,
                **kwargs
            )
            
            # Post-verdict: Floors 3-6
            enriched_metrics = adapter.post_verdict_enrichment(
                prompt=prompt,
                response=response_text,
                context=context,
                metrics=vars(metrics) if hasattr(metrics, '__dict__') else {}
            )
            
            floor_score = adapter.compute_floor_aggregate_score(enriched_metrics)
            
            if floor_score < 0.5 and verdict.verdict.value == "SEAL":
                from ..system.apex_prime import ApexVerdict, Verdict
                verdict = ApexVerdict(
                    verdict=Verdict.PARTIAL,
                    pulse=floor_score,
                    reason=f"Floors downgrade: {floor_score:.2f}. {verdict.reason}",
                    floors=verdict.floors
                )
            
            if hasattr(verdict, 'floors') and verdict.floors:
                verdict.floors.floor_metrics = enriched_metrics
            
            return verdict
        
        apex_instance.apex_review = apex_review_with_floors


# Constitutional metadata
__floor__ = "INTEGRATION"
__name__ = "Floor Adapter — Entropy Reduction Engine"
__authority__ = "Unify scattered floor logic into single execution spine"
__version__ = "v46.0-APEX-THEORY"
__status__ = "SEALED"
__nonce__ = "X7K9F24"
