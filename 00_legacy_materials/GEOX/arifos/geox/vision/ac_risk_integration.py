"""
VisionGovernance — AC_Risk Integration for Vision Operations
DITEMPA BUKAN DIBERI

Provides convenient AC_Risk calculation wrappers for vision tasks.
"""

from ..ENGINE.ac_risk import ACRiskCalculator, ACRiskResult


class VisionGovernance:
    """
    Convenience class for applying AC_Risk to vision operations.
    """
    
    @staticmethod
    def assess_georeferencing(
        bound_divergence: float,
        scale_consistency: float,
        ocr_confidence: float,
        gcp_residuals: list[float],
    ) -> ACRiskResult:
        """
        Assess georeferencing operation.
        
        Args:
            bound_divergence: |claimed_bounds - detected_bounds|
            scale_consistency: Agreement between scale bar and bounds
            ocr_confidence: OCR confidence for grid labels
            gcp_residuals: List of GCP residual errors
        """
        # Transform stack for georeferencing
        transforms = ["perspective_warp", "ocr_extraction"]
        
        # Add GCP quality factor
        if gcp_residuals:
            avg_residual = sum(gcp_residuals) / len(gcp_residuals)
            gcp_quality = max(0.0, 1.0 - avg_residual / 10.0)  # Normalize
        else:
            gcp_quality = 0.0
        
        # Adjust U_phys based on GCP quality
        base_u_phys = (bound_divergence + (1 - scale_consistency)) / 2
        u_phys = max(base_u_phys, 1 - ocr_confidence, 1 - gcp_quality)
        
        return ACRiskCalculator.for_georeferencing(
            bound_divergence=bound_divergence,
            scale_consistency=scale_consistency,
            ocr_confidence=ocr_confidence,
            transform_stack=transforms,
        )
    
    @staticmethod
    def assess_analog_digitization(
        ocr_confidence: float,
        scale_consistency: float,
        ratlas_plausibility: float,
        curve_trace_confidence: float,
        transform_stack: list[str] | None = None,
    ) -> ACRiskResult:
        """
        Assess analog digitization operation.
        
        Args:
            ocr_confidence: OCR confidence for axis labels
            scale_consistency: Consistency between scale markers
            ratlas_plausibility: RATLAS physics consistency
            curve_trace_confidence: Curve tracing quality
            transform_stack: Additional transforms applied
        """
        transforms = transform_stack or []
        transforms.extend(["ocr_extraction", "curve_tracing", "color_decomposition"])
        
        return ACRiskCalculator.for_analog_digitization(
            ocr_confidence=ocr_confidence,
            scale_consistency=scale_consistency,
            physics_plausibility=ratlas_plausibility,
            transform_stack=transforms,
        )
    
    @staticmethod
    def assess_seismic_interpretation(
        view_consistency: float,
        physics_agreement: float,
        has_segy: bool,
        is_image_only: bool,
        transform_stack: list[str] | None = None,
    ) -> ACRiskResult:
        """
        Assess seismic VLM interpretation.
        
        Args:
            view_consistency: Cross-view feature consistency
            physics_agreement: VLM vs computed attributes agreement
            has_segy: Whether SEG-Y data available
            is_image_only: Whether interpreting from image only
            transform_stack: Display transforms applied
        """
        transforms = transform_stack or []
        
        if is_image_only:
            transforms.extend(["colormap_mapping", "vlm_inference"])
        
        return ACRiskCalculator.for_seismic_vision(
            view_consistency=view_consistency,
            physics_agreement=physics_agreement,
            has_segy=has_segy,
            transform_stack=transforms,
        )
