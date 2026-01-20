"""
Constitutional Cost Tracker with F6 (Amanah) Enforcement
X7K9F24 - Entropy Reduction via Budget-Aware Governance

This module implements token budgeting and cost tracking with constitutional governance,
ensuring search operations respect F6 (Amanah) integrity constraints.

Features:
- Token budgeting system with F6 (Amanah) enforcement
- Cost-aware reasoning for search decisions
- Budget validation before API calls
- Integration with arifos_ledger for audit trails
- Real-time cost tracking and alerts

Status: SEALED
Nonce: X7K9F24
"""

import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from arifos.ledger import LedgerStore

logger = logging.getLogger("arifos.cost_tracker")


class BudgetLevel(Enum):
    """Budget alert levels for constitutional governance."""
    NORMAL = "normal"
    CAUTION = "caution"  # 75% of budget used
    WARNING = "warning"  # 90% of budget used
    CRITICAL = "critical"  # 95% of budget used
    EXCEEDED = "exceeded"  # 100%+ of budget used


class CostType(Enum):
    """Types of costs tracked by the system."""
    SEARCH_API = "search_api"
    TOKEN_PROCESSING = "token_processing"
    CACHE_OPERATION = "cache_operation"
    LEDGER_WRITE = "ledger_write"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    SEMANTIC_ANALYSIS = "semantic_analysis"


@dataclass
class CostEstimate:
    """Cost estimate for an operation."""
    operation_type: str
    estimated_cost: float
    confidence: float  # 0.0-1.0
    breakdown: Dict[str, float]
    risk_factors: List[str]
    constitutional_impact: Dict[str, float]  # Floor scores impact


@dataclass
class ActualCost:
    """Actual cost recorded for an operation."""
    operation_type: str
    actual_cost: float
    timestamp: float = field(default_factory=time.time)
    details: Dict[str, Any] = field(default_factory=dict)
    constitutional_verdict: str = "SEAL"


class BudgetExceededError(Exception):
    """Raised when budget limits are exceeded."""
    pass


class ConstitutionalBudgetError(Exception):
    """Raised when budget decisions violate constitutional constraints."""
    pass


class CostTracker:
    """
    Constitutional cost tracker with F6 (Amanah) enforcement.
    
    Provides comprehensive cost tracking and budget management with:
    - Real-time cost monitoring and alerts
    - Constitutional validation of budget decisions
    - Integration with cooling ledger for audit trails
    - Cost-aware reasoning for search operations
    """
    
    def __init__(
        self,
        initial_budget: float = 1000.0,  # Default budget in tokens
        ledger_store: Optional[LedgerStore] = None,
        enable_constitutional_enforcement: bool = True,
        alert_thresholds: Optional[Dict[BudgetLevel, float]] = None
    ):
        self.initial_budget = initial_budget
        self.current_budget = initial_budget
        self.ledger_store = ledger_store
        self.enable_constitutional_enforcement = enable_constitutional_enforcement
        
        # Default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            BudgetLevel.CAUTION: 0.75,   # 75%
            BudgetLevel.WARNING: 0.90,   # 90%
            BudgetLevel.CRITICAL: 0.95,  # 95%
            BudgetLevel.EXCEEDED: 1.00   # 100%
        }
        
        # Cost tracking data
        self._operation_history: List[ActualCost] = []
        self._cost_breakdown: Dict[CostType, float] = {cost_type: 0.0 for cost_type in CostType}
        self._session_start = time.time()
        
        # Constitutional compliance tracking
        self._constitutional_violations = 0
        self._budget_level = BudgetLevel.NORMAL
        
        logger.info(f"CostTracker initialized with budget: {initial_budget} tokens")
    
    def estimate_search_cost(
        self,
        query: str,
        search_providers: Optional[List[str]] = None,
        complexity_multiplier: float = 1.0
    ) -> CostEstimate:
        """
        Estimate cost for a search operation with constitutional reasoning.
        
        Args:
            query: Search query
            search_providers: List of search providers to use
            complexity_multiplier: Multiplier for query complexity
            
        Returns:
            Cost estimate with breakdown and risk assessment
        """
        # Base cost calculation
        query_length = len(query)
        base_cost = max(10.0, query_length * 0.5)  # Minimum 10 tokens
        
        # Provider costs
        provider_cost = 0.0
        providers = search_providers or ["default"]
        for provider in providers:
            # Different providers have different cost models
            if provider == "default":
                provider_cost += 50.0
            elif provider == "semantic":
                provider_cost += 75.0
            elif provider == "constitutional":
                provider_cost += 100.0  # Higher cost for constitutional search
            else:
                provider_cost += 60.0  # Default provider cost
        
        # Constitutional validation costs
        validation_cost = 25.0 * complexity_multiplier  # Base validation cost
        
        # Semantic analysis costs (if complex query)
        semantic_cost = 0.0
        if complexity_multiplier > 1.0:
            semantic_cost = 30.0 * (complexity_multiplier - 1.0)
        
        # Cache operation costs
        cache_cost = 5.0  # Basic cache operations
        
        # Ledger write costs
        ledger_cost = 10.0  # Audit trail logging
        
        # Total estimated cost
        total_cost = base_cost + provider_cost + validation_cost + semantic_cost + cache_cost + ledger_cost
        
        # Risk assessment
        risk_factors = []
        if len(query) > 200:
            risk_factors.append("Long query may increase processing costs")
        if len(providers) > 3:
            risk_factors.append("Multiple providers increase API costs")
        if complexity_multiplier > 2.0:
            risk_factors.append("High complexity multiplier indicates complex analysis needed")
        
        # Constitutional impact assessment
        constitutional_impact = {
            "F1": 0.95,  # Truth - high confidence in cost estimation
            "F2": 0.90,  # Clarity - reasonable clarity in cost breakdown
            "F6": 0.85,  # Amanah - budget integrity maintained
            "F9": 1.00,  # Anti-Hantu - no consciousness claims in cost estimation
        }
        
        # Adjust confidence based on risk factors
        confidence = max(0.7, 1.0 - (len(risk_factors) * 0.1))
        
        return CostEstimate(
            operation_type="search",
            estimated_cost=total_cost,
            confidence=confidence,
            breakdown={
                "base": base_cost,
                "providers": provider_cost,
                "validation": validation_cost,
                "semantic": semantic_cost,
                "cache": cache_cost,
                "ledger": ledger_cost
            },
            risk_factors=risk_factors,
            constitutional_impact=constitutional_impact
        )
    
    def validate_budget_for_operation(
        self,
        estimated_cost: float,
        operation_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Validate if budget allows operation with constitutional reasoning.
        
        Args:
            estimated_cost: Estimated cost of operation
            operation_type: Type of operation
            context: Optional context for decision making
            
        Returns:
            True if budget allows operation, False otherwise
            
        Raises:
            ConstitutionalBudgetError: If constitutional constraints are violated
        """
        context = context or {}
        
        # Check current budget level
        budget_used_ratio = 1.0 - (self.current_budget / self.initial_budget)
        current_level = self._get_budget_level(budget_used_ratio)
        
        # Constitutional validation
        if self.enable_constitutional_enforcement:
            # F6 (Amanah) - Budget integrity must be maintained
            if budget_used_ratio > 0.95 and estimated_cost > 0:
                raise ConstitutionalBudgetError(
                    f"F6 (Amanah) violation: Budget integrity at risk ({budget_used_ratio:.1%} used)"
                )
            
            # F2 (Truth) - Cost estimates must be honest
            if estimated_cost < 0:
                raise ConstitutionalBudgetError(
                    "F2 (Truth) violation: Negative cost estimates are not truthful"
                )
            
            # F1 (Truth) - Operation must be within stated budget
            if estimated_cost > self.current_budget:
                # Check if this is a critical operation that needs human approval
                if context.get("requires_human_approval", False):
                    logger.warning(f"Budget exceeded but human approval granted: {estimated_cost} > {self.current_budget}")
                    return True
                else:
                    raise ConstitutionalBudgetError(
                        f"F1 (Truth) violation: Operation cost {estimated_cost} exceeds available budget {self.current_budget}"
                    )
        
        # Standard budget check
        if estimated_cost > self.current_budget:
            logger.warning(f"Budget insufficient: {estimated_cost} > {self.current_budget}")
            return False
        
        # Budget level warnings
        if current_level in [BudgetLevel.WARNING, BudgetLevel.CRITICAL]:
            logger.warning(f"Budget level {current_level.value}: {budget_used_ratio:.1%} used, {self.current_budget} remaining")
        
        return True
    
    def track_operation_cost(
        self,
        operation_type: str,
        actual_cost: float,
        details: Optional[Dict[str, Any]] = None,
        constitutional_verdict: str = "SEAL"
    ) -> ActualCost:
        """
        Track actual cost of an operation with audit trail.
        
        Args:
            operation_type: Type of operation
            actual_cost: Actual cost incurred
            details: Additional details about the operation
            constitutional_verdict: Constitutional verdict for the operation
            
        Returns:
            Actual cost record
            
        Raises:
            BudgetExceededError: If operation exceeds budget
        """
        details = details or {}
        
        # Check if this would exceed budget
        if actual_cost > self.current_budget:
            raise BudgetExceededError(
                f"Operation cost {actual_cost} exceeds remaining budget {self.current_budget}"
            )
        
        # Deduct from budget
        self.current_budget -= actual_cost
        
        # Create cost record
        cost_record = ActualCost(
            operation_type=operation_type,
            actual_cost=actual_cost,
            details=details,
            constitutional_verdict=constitutional_verdict
        )
        
        # Add to history
        self._operation_history.append(cost_record)
        
        # Update cost breakdown
        cost_type = self._map_operation_to_cost_type(operation_type)
        self._cost_breakdown[cost_type] += actual_cost
        
        # Check budget level and log if changed
        budget_used_ratio = 1.0 - (self.current_budget / self.initial_budget)
        new_level = self._get_budget_level(budget_used_ratio)
        
        if new_level != self._budget_level:
            self._budget_level = new_level
            logger.warning(f"Budget level changed to {new_level.value}: {budget_used_ratio:.1%} used")
        
        # Log to ledger if available
        if self.ledger_store:
            self._log_cost_to_ledger(cost_record, budget_used_ratio)
        
        logger.info(f"Tracked operation cost: {operation_type} = {actual_cost} tokens (remaining: {self.current_budget})")
        return cost_record
    
    def track_search_cost(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        search_providers: Optional[List[str]] = None
    ) -> float:
        """
        Track actual search cost based on results and providers.
        
        Args:
            query: Search query
            search_results: Search results returned
            search_providers: Search providers used
            
        Returns:
            Actual cost tracked
        """
        # Calculate cost based on result complexity
        result_count = len(search_results)
        result_complexity = sum(len(str(result)) for result in search_results) / 1000  # KB
        
        # Base cost
        base_cost = 50.0
        
        # Result count cost
        count_cost = result_count * 10.0
        
        # Complexity cost
        complexity_cost = result_complexity * 5.0
        
        # Provider multiplier
        providers = search_providers or ["default"]
        provider_multiplier = 1.0 + (len(providers) - 1) * 0.2
        
        # Total actual cost
        total_cost = (base_cost + count_cost + complexity_cost) * provider_multiplier
        
        # Track the cost
        details = {
            "query_length": len(query),
            "result_count": result_count,
            "result_complexity_kb": result_complexity,
            "providers": providers,
            "provider_multiplier": provider_multiplier
        }
        
        self.track_operation_cost("search", total_cost, details)
        return total_cost
    
    def update_budget(self, amount: float, reason: str = "") -> float:
        """
        Update budget by adding or removing funds.
        
        Args:
            amount: Amount to add (positive) or remove (negative)
            reason: Reason for budget update
            
        Returns:
            New budget amount
        """
        old_budget = self.current_budget
        self.current_budget = max(0.0, self.current_budget + amount)
        
        logger.info(f"Budget updated: {old_budget} -> {self.current_budget} (change: {amount}, reason: {reason})")
        
        # Log to ledger if significant change
        if abs(amount) > self.initial_budget * 0.1 and self.ledger_store:
            self._log_budget_update_to_ledger(amount, reason, old_budget)
        
        return self.current_budget
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status and statistics."""
        budget_used = self.initial_budget - self.current_budget
        budget_used_ratio = budget_used / self.initial_budget if self.initial_budget > 0 else 0.0
        current_level = self._get_budget_level(budget_used_ratio)
        
        # Calculate average costs by type
        avg_costs = {}
        for cost_type in CostType:
            operations_of_type = [
                cost for cost in self._operation_history
                if self._map_operation_to_cost_type(cost.operation_type) == cost_type
            ]
            if operations_of_type:
                avg_costs[cost_type.value] = sum(cost.actual_cost for cost in operations_of_type) / len(operations_of_type)
            else:
                avg_costs[cost_type.value] = 0.0
        
        session_duration = time.time() - self._session_start
        
        return {
            "initial_budget": self.initial_budget,
            "current_budget": self.current_budget,
            "budget_used": budget_used,
            "budget_remaining": self.current_budget,
            "budget_used_ratio": budget_used_ratio,
            "budget_level": current_level.value,
            "constitutional_violations": self._constitutional_violations,
            "total_operations": len(self._operation_history),
            "cost_breakdown": {k.value: v for k, v in self._cost_breakdown.items()},
            "average_costs": avg_costs,
            "session_duration": session_duration,
            "operations_per_hour": len(self._operation_history) / (session_duration / 3600) if session_duration > 0 else 0
        }
    
    def get_budget_recommendations(self) -> List[Dict[str, Any]]:
        """Get budget optimization recommendations."""
        recommendations = []
        
        status = self.get_budget_status()
        budget_level = status["budget_level"]
        
        # Level-specific recommendations
        if budget_level == BudgetLevel.CRITICAL.value:
            recommendations.append({
                "priority": "HIGH",
                "type": "budget_exhaustion",
                "message": "Budget critically low. Consider emergency budget increase or operation suspension.",
                "action": "Request human approval for budget increase or pause non-critical operations"
            })
        elif budget_level == BudgetLevel.WARNING.value:
            recommendations.append({
                "priority": "MEDIUM",
                "type": "budget_efficiency",
                "message": "Budget usage high. Optimize operation efficiency and reduce costs.",
                "action": "Enable more aggressive caching, reduce provider count, optimize queries"
            })
        elif budget_level == BudgetLevel.CAUTION.value:
            recommendations.append({
                "priority": "LOW",
                "type": "budget_monitoring",
                "message": "Budget usage elevated. Monitor costs and prepare optimization strategies.",
                "action": "Review operation patterns and identify cost reduction opportunities"
            })
        
        # Cost breakdown analysis
        highest_cost_type = max(self._cost_breakdown.items(), key=lambda x: x[1])
        if highest_cost_type[1] > self.initial_budget * 0.3:
            recommendations.append({
                "priority": "MEDIUM",
                "type": "cost_optimization",
                "message": f"{highest_cost_type[0].value} operations consuming significant budget.",
                "action": f"Optimize {highest_cost_type[0].value} operations or find alternatives"
            })
        
        # Operation frequency analysis
        if status["operations_per_hour"] > 100:
            recommendations.append({
                "priority": "LOW",
                "type": "operation_frequency",
                "message": "High operation frequency detected. Consider batching or throttling.",
                "action": "Implement operation batching or rate limiting to reduce costs"
            })
        
        return recommendations
    
    def _get_budget_level(self, budget_used_ratio: float) -> BudgetLevel:
        """Get budget level based on usage ratio."""
        for level, threshold in self.alert_thresholds.items():
            if budget_used_ratio >= threshold:
                return level
        return BudgetLevel.NORMAL
    
    def _map_operation_to_cost_type(self, operation_type: str) -> CostType:
        """Map operation type to cost type category."""
        operation_type = operation_type.lower()
        
        if "search" in operation_type:
            return CostType.SEARCH_API
        elif "token" in operation_type or "processing" in operation_type:
            return CostType.TOKEN_PROCESSING
        elif "cache" in operation_type:
            return CostType.CACHE_OPERATION
        elif "ledger" in operation_type or "audit" in operation_type:
            return CostType.LEDGER_WRITE
        elif "constitutional" in operation_type or "validation" in operation_type:
            return CostType.CONSTITUTIONAL_VALIDATION
        elif "semantic" in operation_type or "analysis" in operation_type:
            return CostType.SEMANTIC_ANALYSIS
        else:
            return CostType.TOKEN_PROCESSING  # Default
    
    def _log_cost_to_ledger(self, cost_record: ActualCost, budget_used_ratio: float) -> None:
        """Log cost operation to cooling ledger."""
        if not self.ledger_store:
            return
        
        ledger_entry = {
            "timestamp": cost_record.timestamp,
            "operation_type": cost_record.operation_type,
            "actual_cost": cost_record.actual_cost,
            "budget_used_ratio": budget_used_ratio,
            "current_budget": self.current_budget,
            "constitutional_verdict": cost_record.constitutional_verdict,
            "details": cost_record.details,
            "stage": "COST_TRACKING"
        }
        
        try:
            ledger_id = self.ledger_store.append_atomic(**ledger_entry)
            logger.debug(f"Cost operation logged to ledger: {ledger_id}")
        except Exception as e:
            logger.error(f"Failed to log cost to ledger: {e}")
    
    def _log_budget_update_to_ledger(self, amount: float, reason: str, old_budget: float) -> None:
        """Log budget update to cooling ledger."""
        if not self.ledger_store:
            return
        
        ledger_entry = {
            "timestamp": time.time(),
            "operation_type": "budget_update",
            "amount": amount,
            "old_budget": old_budget,
            "new_budget": self.current_budget,
            "reason": reason,
            "stage": "BUDGET_MANAGEMENT"
        }
        
        try:
            ledger_id = self.ledger_store.append_atomic(**ledger_entry)
            logger.debug(f"Budget update logged to ledger: {ledger_id}")
        except Exception as e:
            logger.error(f"Failed to log budget update to ledger: {e}")
    
    # Convenience methods
    def get_total_operations(self) -> int:
        """Get total number of tracked operations."""
        return len(self._operation_history)
    
    def get_total_cost(self) -> float:
        """Get total cost of all operations."""
        return sum(cost.actual_cost for cost in self._operation_history)
    
    def get_budget_remaining(self) -> float:
        """Get remaining budget."""
        return self.current_budget
    
    def get_cost_by_type(self, cost_type: CostType) -> float:
        """Get total cost for a specific cost type."""
        return self._cost_breakdown.get(cost_type, 0.0)
    
    def get_operation_history(self, limit: int = 100) -> List[ActualCost]:
        """Get recent operation history."""
        return self._operation_history[-limit:] if self._operation_history else []
    
    def enforce_budget_limit(self, current_cost: float, budget: float) -> str:
        """
        Constitutional budget enforcement with F1 (Amanah) and F6 (Amanah) compliance.
        
        Args:
            current_cost: Current cost to evaluate
            budget: Budget limit
            
        Returns:
            Constitutional verdict: ALLOW or VOID
            
        Constitutional Logic:
        - F1 Amanah: Must be reversible - VOID provides reversible veto
        - F6 Amanah: Must respect budget mandate - within budget is ALLOW
        """
        if current_cost > budget:
            return "VOID"  # ✅ F1 Amanah: Reversible veto for overspending
        else:
            return "ALLOW"  # ✅ F6 Amanah: Within mandate, proceed
