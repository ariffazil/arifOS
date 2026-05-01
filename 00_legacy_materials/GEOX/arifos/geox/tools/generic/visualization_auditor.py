"""
VisualizationAuditor — Audit Any Visualization for Conflation
DITEMPA BUKAN DIBERI

Audits visualizations (images, displays, renderings) to detect:
  - Anomalous contrast ratios
  - Unknown transform chains
  - Missing physical provenance
  - Conflation risks

Works across all domains: seismic, medical, satellite, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from ...THEORY import ContrastTaxonomy, assess_conflation_risk, GEOX_HOLD
from ...ENGINE import get_registry


@dataclass
class VisualizationAuditResult:
    """Result of auditing a visualization."""
    
    # Audit outcome
    can_trust_visual: bool
    confidence: float  # 0-1 confidence in this assessment
    
    # Risk assessment
    anomalous_contrast_detected: bool
    anomalous_score: float
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Issues found
    issues: list[dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    
    # Transform chain analysis
    transform_chain: list[str] = field(default_factory=list)
    chain_risk: dict[str, Any] | None = None
    
    # Contrast space representation
    contrast_space_summary: dict[str, Any] | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "can_trust_visual": self.can_trust_visual,
            "confidence": self.confidence,
            "anomalous_contrast_detected": self.anomalous_contrast_detected,
            "anomalous_score": self.anomalous_score,
            "risk_level": self.risk_level,
            "issue_count": len(self.issues),
            "recommendations": self.recommendations,
            "transform_chain": self.transform_chain,
        }


class VisualizationAuditor:
    """
    Auditor for visualizations.
    
    Analyzes any visualization (image file, display buffer, etc.) to
determine if it can be trusted as a representation of physical data.
    
    Key checks:
      1. Source provenance (where did this image come from?)
      2. Transform chain analysis (what processing was applied?)
      3. Contrast ratio assessment (display vs physical)
      4. Anomaly detection (suspicious patterns)
    """
    
    def __init__(self):
        self.registry = get_registry()
    
    async def audit(
        self,
        visual_data: np.ndarray | str,  # Image array or file path
        source_type: str = "unknown",  # "segy", "raster", "rendered", etc.
        claimed_transforms: list[str] | None = None,
        physical_provenance: dict[str, Any] | None = None,
    ) -> VisualizationAuditResult:
        """
        Audit a visualization for conflation risks.
        
        Args:
            visual_data: The visualization (numpy array or file path)
            source_type: Type of source ("segy", "raster", "rendered")
            claimed_transforms: List of transforms claimed to be applied
            physical_provenance: Metadata about physical source data
            
        Returns:
            VisualizationAuditResult with full assessment
        """
        issues = []
        recommendations = []
        
        # Step 1: Source provenance check
        source_trust = self._assess_source_trust(source_type)
        if source_trust < 0.3:
            issues.append({
                "type": "untrusted_source",
                "severity": "HIGH",
                "description": f"Source type '{source_type}' has low trust",
            })
            recommendations.append(
                "Acquire raw data (SEG-Y, DICOM, etc.) instead of rendered image"
            )
        
        # Step 2: Transform chain analysis
        transforms = claimed_transforms or []
        chain_risk = self.registry.analyze_chain(transforms) if transforms else None
        
        if chain_risk:
            if chain_risk.get("risk_level") == "HIGH":
                issues.append({
                    "type": "high_risk_transforms",
                    "severity": "HIGH",
                    "description": f"Transform chain has HIGH risk: {chain_risk.get('warnings', [])}",
                })
                recommendations.append(
                    "Review transform chain and reduce amplification factors"
                )
        else:
            issues.append({
                "type": "unknown_transforms",
                "severity": "MEDIUM",
                "description": "Transform chain is unknown or not provided",
            })
            recommendations.append(
                "Document all transforms applied to create this visualization"
            )
        
        # Step 3: Contrast analysis
        anomalous_score = self._estimate_anomalous_score(
            source_type, chain_risk, physical_provenance
        )
        anomalous_detected = anomalous_score > 2.0
        
        if anomalous_detected:
            issues.append({
                "type": "anomalous_contrast",
                "severity": "HIGH",
                "description": f"Estimated anomalous contrast score: {anomalous_score:.1f}",
            })
            recommendations.append(
                "Display contrast significantly exceeds physical signal. "
                "Do not interpret without verifying against raw data."
            )
        
        # Step 4: Physical provenance check
        if not physical_provenance:
            issues.append({
                "type": "missing_provenance",
                "severity": "CRITICAL",
                "description": "No physical provenance information provided",
            })
            recommendations.append(
                "CRITICAL: Cannot verify visualization represents physical data"
            )
        
        # Calculate overall risk
        risk_level = self._calculate_risk_level(issues, anomalous_score)
        can_trust = risk_level in ("LOW", "MEDIUM") and not anomalous_detected
        
        # Estimate confidence in assessment
        confidence = self._calculate_confidence(
            source_trust, bool(physical_provenance), bool(chain_risk)
        )
        
        return VisualizationAuditResult(
            can_trust_visual=can_trust,
            confidence=confidence,
            anomalous_contrast_detected=anomalous_detected,
            anomalous_score=anomalous_score,
            risk_level=risk_level,
            issues=issues,
            recommendations=recommendations,
            transform_chain=transforms,
            chain_risk=chain_risk,
        )
    
    def _assess_source_trust(self, source_type: str) -> float:
        """Assess trust level for a source type."""
        trust_levels = {
            "segy": 0.9,      # Raw SEG-Y - high trust
            "seismic": 0.9,   # Generic seismic raw data
            "dicom": 0.9,     # Medical raw data
            "geotiff": 0.8,   # Satellite raw data
            "numpy": 0.85,    # Raw array
            "rendered": 0.3,  # Pre-rendered - low trust
            "raster": 0.2,    # Raster image - very low trust
            "png": 0.15,      # Image file - very low trust
            "jpg": 0.1,       # Compressed image - minimal trust
            "unknown": 0.0,   # Unknown - no trust
        }
        return trust_levels.get(source_type.lower(), 0.0)
    
    def _estimate_anomalous_score(
        self,
        source_type: str,
        chain_risk: dict[str, Any] | None,
        physical_provenance: dict[str, Any] | None,
    ) -> float:
        """Estimate anomalous contrast score."""
        score = 1.0  # Baseline
        
        # Source factor
        if source_type in ("raster", "png", "jpg", "rendered"):
            score *= 3.0  # High risk for pre-rendered
        elif source_type in ("segy", "dicom", "numpy"):
            score *= 1.0  # Neutral for raw
        else:
            score *= 2.0  # Moderate for unknown
        
        # Transform chain factor
        if chain_risk:
            total_amp = chain_risk.get("total_amplification", 1.0)
            score *= max(1.0, total_amp / 2.0)
        else:
            score *= 2.5  # Unknown transforms = high risk
        
        # Provenance factor
        if not physical_provenance:
            score *= 1.5
        
        return score
    
    def _calculate_risk_level(
        self,
        issues: list[dict],
        anomalous_score: float,
    ) -> str:
        """Calculate overall risk level from issues."""
        # Check for critical issues
        critical_count = sum(1 for i in issues if i.get("severity") == "CRITICAL")
        high_count = sum(1 for i in issues if i.get("severity") == "HIGH")
        
        if critical_count > 0 or anomalous_score > 5.0:
            return "CRITICAL"
        if high_count >= 2 or anomalous_score > 3.0:
            return "HIGH"
        if high_count == 1 or anomalous_score > 2.0:
            return "MEDIUM"
        return "LOW"
    
    def _calculate_confidence(
        self,
        source_trust: float,
        has_provenance: bool,
        has_chain_info: bool,
    ) -> float:
        """Calculate confidence in the audit assessment."""
        confidence = 0.5  # Base
        
        # Source trust contributes
        confidence += source_trust * 0.3
        
        # Provenance contributes
        if has_provenance:
            confidence += 0.1
        
        # Chain info contributes
        if has_chain_info:
            confidence += 0.1
        
        return min(confidence, 0.95)  # Cap at 0.95 (F7 Humility)
    
    def audit_taxonomy(
        self,
        taxonomy: ContrastTaxonomy,
        domain: str = "generic",
    ) -> VisualizationAuditResult:
        """Audit using an existing ContrastTaxonomy."""
        # Extract transform chain from taxonomy
        transforms = [
            t.transform_name for t in taxonomy.visual_transforms
        ]
        
        # Run assessment
        verdict, triggers, metadata = assess_conflation_risk(taxonomy, domain)
        
        # Determine trust based on data source
        source_trust = self._assess_source_trust(taxonomy.data_source.source_type)
        
        # Calculate anomalous score from metadata
        anomalous_score = metadata.get("amplification_ratio", 1.0)
        
        # Build issues from triggers
        issues = [
            {
                "type": t.trigger_type,
                "severity": "HIGH" if t.is_critical else "MEDIUM",
                "description": t.description,
            }
            for t in triggers
        ]
        
        # Calculate risk level
        risk_level = metadata.get("risk_level", "UNKNOWN")
        
        # Determine if visual can be trusted
        can_trust = (
            verdict.to_geox_verdict() != GEOX_HOLD and
            risk_level in ("LOW", "MEDIUM") and
            anomalous_score < 3.0
        )
        
        return VisualizationAuditResult(
            can_trust_visual=can_trust,
            confidence=0.7 + source_trust * 0.2,
            anomalous_contrast_detected=anomalous_score > 2.0,
            anomalous_score=anomalous_score,
            risk_level=risk_level,
            issues=issues,
            recommendations=metadata.get("recommendations", []),
            transform_chain=transforms,
        )
