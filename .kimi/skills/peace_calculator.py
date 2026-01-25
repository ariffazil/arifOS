"""
Multi-Dimensional Peace² Calculator
Calculates Peace² across economic, social, psychological, environmental, and temporal dimensions

Authority: Muhammad Arif bin Fazil
Floor: F3 (Peace²), F5 (Empathy)
Version: v52.0.0-SEAL
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class PeaceDimension(Enum):
    ECONOMIC = "economic"
    SOCIAL = "social"
    PSYCHOLOGICAL = "psychological"
    ENVIRONMENTAL = "environmental"
    TEMPORAL = "temporal"

@dataclass
class DimensionScore:
    benefit: float
    harm: float
    weight: float
    confidence: float  # 0.0 to 1.0
    
    @property
    def ratio(self) -> float:
        if self.harm == 0:
            return float('inf') if self.benefit > 0 else 0
        return self.benefit / self.harm

class PeaceCalculator:
    """
    Calculates Peace² across multiple dimensions with dynamic weighting
    """
    
    def __init__(self):
        # Default weights - can be overridden by cultural context
        self.default_weights = {
            PeaceDimension.ECONOMIC: 0.25,
            PeaceDimension.SOCIAL: 0.20,
            PeaceDimension.PSYCHOLOGICAL: 0.20,
            PeaceDimension.ENVIRONMENTAL: 0.15,
            PeaceDimension.TEMPORAL: 0.20,
        }
        
        # Minimum thresholds for each dimension
        self.dimension_thresholds = {
            PeaceDimension.ECONOMIC: 0.5,  # Economic harm can't exceed 2x benefit
            PeaceDimension.SOCIAL: 0.3,    # Social harm is heavily weighted
            PeaceDimension.PSYCHOLOGICAL: 0.4,
            PeaceDimension.ENVIRONMENTAL: 0.6,  # Environment is critical
            PeaceDimension.TEMPORAL: 0.5,   # Future harm matters
        }
    
    async def calculate_multidimensional_peace(
        self,
        operation: Dict[str, Any],
        stakeholders: Dict[str, List],
        cultural_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Main calculation function
        
        Returns: {
            "peace_squared": float,  # Final Peace² score
            "dimensions": Dict,       # Per-dimension scores
            "weighted_score": float,  # Σ(w × (benefit/harm))
            "all_thresholds_met": bool,
            "critical_dimensions": List,  # Dimensions that failed
            "recommendations": List      # Suggestions to improve Peace²
        }
        """
        
        # Adjust weights based on cultural context
        weights = self._get_weights(cultural_context)
        
        # Calculate scores for each dimension
        dimension_scores = await self._calculate_all_dimensions(
            operation, stakeholders, weights
        )
        
        # Weighted calculation
        weighted_score = sum(
            score.ratio * weights[dimension]
            for dimension, score in dimension_scores.items()
        )
        
        # Peace² = (weighted_score)² (as per F3 formula)
        peace_squared = weighted_score ** 2
        
        # Check dimension thresholds
        thresholds_met, failed_dimensions = self._check_thresholds(
            dimension_scores, weights
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            dimension_scores, failed_dimensions, weights
        )
        
        return {
            "peace_squared": round(peace_squared, 3),
            "dimensions": {
                dim.value: {
                    "benefit": round(score.benefit, 3),
                    "harm": round(score.harm, 3),
                    "ratio": round(score.ratio, 3),
                    "weight": round(weights[dim], 3),
                    "confidence": round(score.confidence, 3),
                    "threshold_met": score.ratio >= self.dimension_thresholds[dim]
                }
                for dim, score in dimension_scores.items()
            },
            "weighted_score": round(weighted_score, 3),
            "all_thresholds_met": thresholds_met,
            "critical_dimensions": [dim.value for dim in failed_dimensions],
            "recommendations": recommendations,
            "constitutional_compliant": peace_squared >= 1.0 and thresholds_met
        }
    
    def _get_weights(self, cultural_context: Dict[str, Any] = None) -> Dict[PeaceDimension, float]:
        """Get dimension weights, adjusted for cultural context"""
        if not cultural_context:
            return self.default_weights.copy()
        
        weights = self.default_weights.copy()
        
        # Adjust based on cultural dimensions
        if cultural_context.get("individualism") > 0.7:
            # Individualistic cultures prioritize direct economic benefit
            weights[PeaceDimension.ECONOMIC] += 0.05
            weights[PeaceDimension.SOCIAL] -= 0.05
        
        if cultural_context.get("uncertainty_avoidance") > 0.7:
            # High uncertainty avoidance prioritizes psychological safety
            weights[PeaceDimension.PSYCHOLOGICAL] += 0.08
            weights[PeaceDimension.TEMPORAL] -= 0.08
        
        if cultural_context.get("long_term_orientation") > 0.7:
            # Long-term cultures prioritize temporal and environmental
            weights[PeaceDimension.TEMPORAL] += 0.07
            weights[PeaceDimension.ENVIRONMENTAL] += 0.05
            weights[PeaceDimension.ECONOMIC] -= 0.06
            weights[PeaceDimension.SOCIAL] -= 0.06
        
        # Normalize weights to sum to 1.0
        total = sum(weights.values())
        for dim in weights:
            weights[dim] = weights[dim] / total
        
        return weights
    
    async def _calculate_all_dimensions(
        self,
        operation: Dict[str, Any],
        stakeholders: Dict[str, List],
        weights: Dict[PeaceDimension, float]
    ) -> Dict[PeaceDimension, DimensionScore]:
        """Calculate scores for each dimension"""
        
        return {
            PeaceDimension.ECONOMIC: await self._calculate_economic(operation, stakeholders),
            PeaceDimension.SOCIAL: await self._calculate_social(operation, stakeholders),
            PeaceDimension.PSYCHOLOGICAL: await self._calculate_psychological(operation, stakeholders),
            PeaceDimension.ENVIRONMENTAL: await self._calculate_environmental(operation, stakeholders),
            PeaceDimension.TEMPORAL: await self._calculate_temporal(operation, stakeholders),
        }
    
    async def _calculate_economic(
        self, operation: Dict, stakeholders: Dict
    ) -> DimensionScore:
        """Calculate economic benefit/harm"""
        op_type = operation.get("type")
        
        benefit = 0.0
        harm = 0.0
        confidence = 0.8
        
        if op_type == "file_write":
            # Benefit: Productivity gain
            benefit = 0.6
            # Harm: Development cost
            harm = 0.2
            
        elif op_type == "database_query":
            # Benefit: Information access
            benefit = 0.7
            # Harm: Computational cost
            harm = 0.1
            
        elif op_type == "system_command":
            # Benefit: System efficiency
            benefit = 0.8
            # Harm: Risk of system failure
            harm = 0.4
            confidence = 0.7
            
        else:
            # Default conservative estimate
            benefit = 0.5
            harm = 0.3
            confidence = 0.6
        
        # Adjust based on stakeholder vulnerability
        total_vulnerability = sum(
            s.vulnerability for category in stakeholders.values()
            for s in category
        )
        if total_vulnerability > 2.0:  # High vulnerability ecosystem
            # Increase harm weighting for vulnerable populations
            harm *= 1.5
        
        return DimensionScore(
            benefit=benefit,
            harm=harm,
            weight=0.0,  # Will be set by caller
            confidence=confidence
        )
    
    async def _calculate_social(
        self, operation: Dict, stakeholders: Dict
    ) -> DimensionScore:
        """Calculate social benefit/harm"""
        op_type = operation.get("type")
        
        benefit = 0.0
        harm = 0.0
        confidence = 0.7
        
        if op_type == "ui_change":
            # Benefit: Improved user experience
            benefit = 0.5
            # Harm: Learning curve, confusion
            harm = 0.3
            
        elif op_type == "database_query":
            # Benefit: Enables social features
            benefit = 0.4
            # Harm: Privacy concerns
            harm = 0.5  # Privacy is heavy social harm
            
        elif "user_data" in operation.get("tags", []):
            # Any operation with user data has social implications
            benefit = 0.3
            harm = 0.4
        else:
            benefit = 0.4
            harm = 0.2
        
        # Check for vulnerable social groups
        for category, stakeholder_list in stakeholders.items():
            for stakeholder in stakeholder_list:
                if "disability" in stakeholder.id or "elderly" in stakeholder.id:
                    # Social harm increases if vulnerable groups affected
                    harm *= 1.3
                    confidence = 0.8
                    break
        
        return DimensionScore(
            benefit=benefit,
            harm=harm,
            weight=0.0,
            confidence=confidence
        )
    
    async def _calculate_psychological(
        self, operation: Dict, stakeholders: Dict
    ) -> DimensionScore:
        """Calculate psychological benefit/harm"""
        benefit = 0.0
        harm = 0.0
        confidence = 0.65
        
        op_type = operation.get("type")
        
        if op_type == "ui_change":
            # Benefit: Reduced cognitive load
            benefit = 0.4
            # Harm: Cognitive friction, anxiety
            harm = 0.5  # UI changes can cause significant stress
            
        elif op_type == "system_command":
            # Benefit: Sense of control
            benefit = 0.3
            # Harm: Anxiety about system changes
            harm = 0.4
            
        elif "security" in operation.get("tags", []):
            # Security features
            benefit = 0.6  # Psychological safety
            harm = 0.2     # Minimal harm
            
        else:
            benefit = 0.3
            harm = 0.2
        
        # Check for psychological vulnerability
        for category, stakeholder_list in stakeholders.items():
            for stakeholder in stakeholder_list:
                if stakeholder.vulnerability > 0.8:
                    # Psychologically vulnerable stakeholders
                    harm *= 1.4
                    break
        
        return DimensionScore(
            benefit=benefit,
            harm=harm,
            weight=0.0,
            confidence=confidence
        )
    
    async def _calculate_environmental(
        self, operation: Dict, stakeholders: Dict
    ) -> DimensionScore:
        """Calculate environmental benefit/harm"""
        benefit = 0.0
        harm = 0.0
        confidence = 0.8  # Often more certain
        
        # Most operations have minimal direct environmental impact
        # But we consider computational resources
        
        if operation.get("power_intensive"):
            # High computation = energy consumption
            benefit = 0.2
            harm = 0.6  # Environmental cost of computation
            
        elif "database" in operation.get("type", ""):
            # Database operations have some environmental cost
            benefit = 0.3
            harm = 0.4
            
        else:
            # Default: minimal environmental impact
            benefit = 0.1
            harm = 0.1
        
        return DimensionScore(
            benefit=benefit,
            harm=harm,
            weight=0.0,
            confidence=confidence
        )
    
    async def _calculate_temporal(
        self, operation: Dict, stakeholders: Dict
    ) -> DimensionScore:
        """Calculate temporal (future) benefit/harm"""
        benefit = 0.0
        harm = 0.0
        confidence = 0.5  # Hardest to predict
        
        # Check if operation is irreversible
        if operation.get("reversible") is False:
            # Irreversible operations have high temporal risk
            benefit_future = operation.get("future_benefit", 0.3)
            harm_future = operation.get("future_harm", 0.7)  # Conservative
            
            # Apply temporal discount (but not too much - protect future)
            discount_rate = 0.02  # 2% - very low for ethical considerations
            years_forward = 10
            
            benefit = benefit_future * (1 - discount_rate) ** years_forward
            harm = harm_future * (1 - discount_rate) ** years_forward
            confidence = 0.4  # Lower confidence for long-term predictions
            
        else:
            # Reversible operations have lower temporal risk
            benefit = 0.5
            harm = 0.2
        
        # Check for "legacy burden" - future maintainers
        for category, stakeholder_list in stakeholders.items():
            for stakeholder in stakeholder_list:
                if "maintainer" in stakeholder.id or "future" in stakeholder.id:
                    # Future maintainers are vulnerable to technical debt
                    harm *= 1.2
                    confidence = 0.6
                    break
        
        return DimensionScore(
            benefit=benefit,
            harm=harm,
            weight=0.0,
            confidence=confidence
        )
    
    def _check_thresholds(
        self,
        dimension_scores: Dict[PeaceDimension, DimensionScore],
        weights: Dict[PeaceDimension, float]
    ) -> tuple[bool, List[PeaceDimension]]:
        """Check if all dimensions meet minimum thresholds"""
        failed = []
        
        for dimension, score in dimension_scores.items():
            threshold = self.dimension_thresholds[dimension]
            weighted_ratio = score.ratio * weights[dimension]
            
            if weighted_ratio < threshold:
                failed.append(dimension)
        
        return len(failed) == 0, failed
    
    def _generate_recommendations(
        self,
        dimension_scores: Dict[PeaceDimension, DimensionScore],
        failed_dimensions: List[PeaceDimension],
        weights: Dict[PeaceDimension, float]
    ) -> List[str]:
        """Generate specific recommendations to improve Peace²"""
        
        recommendations = []
        
        for dimension in failed_dimensions:
            score = dimension_scores[dimension]
            current_ratio = score.ratio
            threshold = self.dimension_thresholds[dimension]
            
            needed_improvement = (threshold / current_ratio) - 1
            
            if dimension == PeaceDimension.ECONOMIC:
                if score.harm > score.benefit:
                    recommendations.append(
                        f"Reduce economic harm by {needed_improvement:.0%} "
                        "(e.g., optimize resource usage, reduce costs)"
                    )
                else:
                    recommendations.append(
                        f"Increase economic benefit by {needed_improvement:.0%} "
                        "(e.g., add value for more users, improve efficiency)"
                    )
            
            elif dimension == PeaceDimension.SOCIAL:
                recommendations.append(
                    f"Address social concerns: consider privacy implications, "
                    f"community impact, or stakeholder consultation"
                )
            
            elif dimension == PeaceDimension.PSYCHOLOGICAL:
                recommendations.append(
                    f"Reduce psychological friction: improve UX clarity, "
                    f"reduce anxiety factors, increase user control"
                )
            
            elif dimension == PeaceDimension.ENVIRONMENTAL:
                recommendations.append(
                    f"Reduce environmental impact: optimize computation, "
                    f"use efficient algorithms, reduce waste"
                )
            
            elif dimension == PeaceDimension.TEMPORAL:
                recommendations.append(
                    f"Consider long-term consequences: make reversible if possible, "
                    f"consult future maintainers, document for longevity"
                )
        
        # General recommendations
        if len(failed_dimensions) > 2:
            recommendations.append(
                "Multiple dimensions failing - consider redesigning operation "
                "from first principles with empathy as primary constraint"
            )
        
        return recommendations

# Singleton instance
_calculator = PeaceCalculator()

async def calculate_multidimensional_peace(
    operation: Dict[str, Any],
    stakeholders: Dict[str, List],
    cultural_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Convenience function for external use"""
    return await _calculator.calculate_multidimensional_peace(
        operation, stakeholders, cultural_context
    )

if __name__ == "__main__":
    # Test the calculator
    async def test():
        test_op = {
            "type": "database_query",
            "target": "users",
            "id": "test_002"
        }
        
        test_stakeholders = {
            "primary": [],  # Would be populated by stakeholder_mapper
            "secondary": [],
            "tertiary": [],
            "quaternary": [],
            "silent": []
        }
        
        result = await calculate_multidimensional_peace(test_op, test_stakeholders)
        print(json.dumps(result, indent=2))
    
    import json
    asyncio.run(test())
