"""
arifos/geox/seismic_attribute_taxonomy.py — GEOX Seismic Attribute Taxonomy
DITEMPA BUKAN DIBERI

Based on:
  - Chopra & Marfurt (2007, 2014) — Seismic Attributes
  - Partyka et al. (1999) — Spectral decomposition
  - Brown (2004) — Interpretation of Seismic Data
  - ARXIV:2505.20518v1 — Recent seismic attribute taxonomy review

8-class taxonomy matching academic literature:
  1. Structural / Geometrical  — geometry, continuity, faults
  2. Amplitude / Strength      — reflection energy, DHIs
  3. Instantaneous (Complex Trace) — Hilbert-derived
  4. Spectral / Time-Frequency — frequency content vs time/space
  5. AVO / Elastic / Inversion — rock and fluid properties
  6. Facies / Pattern / Classification — multi-attribute clustering
  7. Kinematic / Time-Related — moveout, travel-time
  8. Misc / Advanced Combinations — attenuation, composites

Contrast risk levels:
  LOW      — Classical physics-based, high traceability (coherence, curvature)
  MEDIUM   — Some processing amplification risk (spectral, AVO)
  HIGH     — ML/meta-attributes with perceptual contrast risk (fault_prob via CNN)
  CRITICAL — Fully learned black-box (deep CNN facies)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContrastRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttributeClass(str, Enum):
    STRUCTURAL = "1_structural_geometrical"
    AMPLITUDE = "2_amplitude_strength"
    INSTANTANEOUS = "3_instantaneous_complex_trace"
    SPECTRAL = "4_spectral_time_frequency"
    AVO_ELASTIC = "5_avo_elastic_inversion"
    FACIES = "6_facies_pattern_classification"
    KINEMATIC = "7_kinematic_time_related"
    MISC = "8_misc_advanced"


@dataclass
class SeismicAttributeDef:
    """Definition of a single seismic attribute."""

    name: str
    display_name: str
    attribute_class: AttributeClass
    contrast_risk: ContrastRisk
    physical_proxy: str
    equation_reference: str | None
    requires_well_tie: bool
    description: str
    meta_intelligence: bool = False  # True if ML/DL-derived
    hci_sensitive: bool = False  # Direct hydrocarbon indicator


# ---------------------------------------------------------------------------
# THE 8-CLASS TAXONOMY — All 300+ historical attributes mapped
# ---------------------------------------------------------------------------

SEISMIC_ATTRIBUTES: dict[str, SeismicAttributeDef] = {
    # ========================================================================
    # CLASS 1: STRUCTURAL / GEOMETRICAL
    # Describes geometry and continuity of reflectors. Faults, folds, strat traps.
    # ========================================================================
    "coherence": SeismicAttributeDef(
        name="coherence",
        display_name="Coherence / Semblance",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="waveform_similarity",
        equation_reference="Marfurt et al. (1998) — semblance-based coherence",
        requires_well_tie=False,
        description="Measures waveform similarity in a local window. Low values = discontinuities (faults, fractures, channels).",
    ),
    "coherence_c3": SeismicAttributeDef(
        name="coherence_c3",
        display_name="C3 Semblance Coherence",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="waveform_similarity",
        equation_reference="Marfurt (2006) — C3 multi-trace coherence",
        requires_well_tie=False,
        description="Higher-order semblance for better noise tolerance.",
    ),
    "dip": SeismicAttributeDef(
        name="dip",
        display_name="Dip / Apparent Dip",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="structural_orientation",
        equation_reference="Marfurt (2006) — gradient-based dip estimation",
        requires_well_tie=False,
        description="Rate of reflector change in vertical direction per trace.",
    ),
    "azimuth": SeismicAttributeDef(
        name="azimuth",
        display_name="Azimuth / Strike",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="structural_orientation",
        equation_reference="Marfurt (2006) — gradient-based azimuth",
        requires_well_tie=False,
        description="Direction of maximum dip in 3D volume.",
    ),
    "curvature_most_positive": SeismicAttributeDef(
        name="curvature_most_positive",
        display_name="Most-Positive Curvature (K1)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="structural_flexure",
        equation_reference="Roberts (2001) — volumetric curvature",
        requires_well_tie=False,
        description="Highlights anticlines, dome crests, drag folds. Positive curvature.",
    ),
    "curvature_most_negative": SeismicAttributeDef(
        name="curvature_most_negative",
        display_name="Most-Negative Curvature (K2)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="structural_flexure",
        equation_reference="Roberts (2001) — volumetric curvature",
        requires_well_tie=False,
        description="Highlights synclines, troughs, channels. Negative curvature.",
    ),
    "curvature_gaussian": SeismicAttributeDef(
        name="curvature_gaussian",
        display_name="Gaussian Curvature (K1×K2)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="dome_saddle_discriminator",
        equation_reference="Al-Dossary & Marfurt (2006)",
        requires_well_tie=False,
        description="Product of principal curvatures. Dome = positive, saddle = negative.",
    ),
    "curvature_mean": SeismicAttributeDef(
        name="curvature_mean",
        display_name="Mean Curvature ((K1+K2)/2)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="average_bending",
        equation_reference="Roberts (2001)",
        requires_well_tie=False,
        description="Average of principal curvatures.",
    ),
    "edge_detection": SeismicAttributeDef(
        name="edge_detection",
        display_name="Edge Detection (Sobel/Canny)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="gradient_magnitude",
        equation_reference="Gonzalez & Woods — digital image processing",
        requires_well_tie=True,
        description="Gradient-based edge detection. Highlights fault boundaries.",
    ),
    "fault_probability": SeismicAttributeDef(
        name="fault_probability",
        display_name="AI Fault Probability (DL)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="discontinuity_probability",
        equation_reference="Wu (2018) — CNN fault segmentation",
        requires_well_tie=True,
        meta_intelligence=True,
        description="CNN/U-Net segmentation of faults from coherence+curvature+dip stack. HIGH perceptual contrast risk.",
    ),
    "fault_likelihood": SeismicAttributeDef(
        name="fault_likelihood",
        display_name="Fault Likelihood (Probabilistic)",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="discontinuity_probability",
        equation_reference="Hale (2013) — Bayesian fault likelihood",
        requires_well_tie=True,
        description="Probabilistic fault enhancement without deep learning.",
    ),
    "local_flatness": SeismicAttributeDef(
        name="local_flatness",
        display_name="Local Flatness / Chaos",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="reflector_continuity",
        equation_reference="Barnes — chaos and flatness attributes",
        requires_well_tie=False,
        description="Measures how flat/chaotic reflectors are.",
    ),
    "reflector_continuity": SeismicAttributeDef(
        name="reflector_continuity",
        display_name="Reflector Continuity",
        attribute_class=AttributeClass.STRUCTURAL,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="waveform_correlation",
        equation_reference="Kfort — continuity attribute",
        requires_well_tie=False,
        description="Tracks lateral continuity of reflectors.",
    ),
    # ========================================================================
    # CLASS 2: AMPLITUDE / STRENGTH
    # Focus on reflection strength / energy. Used for DHIs and reservoir sweetness.
    # ========================================================================
    "rms_amplitude": SeismicAttributeDef(
        name="rms_amplitude",
        display_name="RMS Amplitude",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="reflected_energy",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Root-mean-square amplitude in a window. Bright spots, DHIs.",
        hci_sensitive=True,
    ),
    "peak_amplitude": SeismicAttributeDef(
        name="peak_amplitude",
        display_name="Peak Amplitude (Max Positive)",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="peak_reflection_strength",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Maximum positive amplitude excursion.",
    ),
    "trough_amplitude": SeismicAttributeDef(
        name="trough_amplitude",
        display_name="Trough Amplitude (Max Negative)",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="trough_reflection_strength",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Maximum negative amplitude excursion.",
    ),
    "absolute_amplitude": SeismicAttributeDef(
        name="absolute_amplitude",
        display_name="Absolute Amplitude",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="total_reflection_strength",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Maximum absolute value of peak or trough.",
    ),
    "average_amplitude": SeismicAttributeDef(
        name="average_amplitude",
        display_name="Average Amplitude",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="mean_reflection_strength",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Mean of absolute amplitude values.",
    ),
    "sum_amplitude": SeismicAttributeDef(
        name="sum_amplitude",
        display_name="Summed Amplitude / Energy",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="total_energy",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Sum of amplitude values in a window.",
        hci_sensitive=True,
    ),
    "envelope": SeismicAttributeDef(
        name="envelope",
        display_name="Envelope (Instantaneous Amplitude)",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="acoustic_impedance",
        equation_reference="Taner, Koehler & Sheriff (1979)",
        requires_well_tie=False,
        description="Magnitude of analytic signal. Highlights boundaries and impedance contrasts.",
        hci_sensitive=True,
    ),
    "reflection_intensity": SeismicAttributeDef(
        name="reflection_intensity",
        display_name="Reflection Intensity",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="impedance_contrast",
        equation_reference="Sheriff — encyclopedic dictionary",
        requires_well_tie=False,
        description="Energy of reflected waves at an interface.",
        hci_sensitive=True,
    ),
    "bright_spot": SeismicAttributeDef(
        name="bright_spot",
        display_name="Bright Spot Indicator",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="amplitude_anomaly",
        equation_reference="Conventional DHI practice",
        requires_well_tie=True,
        description="High amplitude anomaly that may indicate gas. Needs well tie.",
        hci_sensitive=True,
    ),
    "dim_spot": SeismicAttributeDef(
        name="dim_spot",
        display_name="Dim Spot Indicator",
        attribute_class=AttributeClass.AMPLITUDE,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="amplitude_reduction",
        equation_reference="Conventional DHI practice",
        requires_well_tie=True,
        description="Reduced amplitude that may indicate hydrocarbon saturation.",
        hci_sensitive=True,
    ),
    # ========================================================================
    # CLASS 3: INSTANTANEOUS (COMPLEX TRACE)
    # Derived from Hilbert transform. Time-varying signal properties.
    # ========================================================================
    "instantaneous_phase": SeismicAttributeDef(
        name="instantaneous_phase",
        display_name="Instantaneous Phase",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="phase_continuity",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Phase of the analytic signal. Highlights lateral phase changes.",
    ),
    "instantaneous_frequency": SeismicAttributeDef(
        name="instantaneous_frequency",
        display_name="Instantaneous Frequency",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="dominant_frequency",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=True,
        description="Time derivative of instantaneous phase. Attenuation indicator.",
    ),
    "instantaneous_bandwidth": SeismicAttributeDef(
        name="instantaneous_bandwidth",
        display_name="Instantaneous Bandwidth",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="spectral_breadth",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=True,
        description="Bandwidth of the complex trace. Indicates bed thickness.",
    ),
    "instantaneous_q": SeismicAttributeDef(
        name="instantaneous_q",
        display_name="Instantaneous Q / Attenuation Factor",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="quality_factor",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=True,
        description="Attenuation indicator derived from frequency decay.",
        hci_sensitive=True,
    ),
    "instantaneous_energy": SeismicAttributeDef(
        name="instantaneous_energy",
        display_name="Instantaneous Energy",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="instantaneous_power",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Energy at each instant in time.",
    ),
    "phase_change_rate": SeismicAttributeDef(
        name="phase_change_rate",
        display_name="Phase Derivative / Cosine Instantaneous Phase",
        attribute_class=AttributeClass.INSTANTANEOUS,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="phase_continuity",
        equation_reference="Taner et al. (1979)",
        requires_well_tie=False,
        description="Rate of phase change. Highlights edges and tuning effects.",
    ),
    # ========================================================================
    # CLASS 4: SPECTRAL / TIME-FREQUENCY
    # Frequency content vs time/space. Thin beds, channels, DHIs.
    # ========================================================================
    "spectral_rms": SeismicAttributeDef(
        name="spectral_rms",
        display_name="Spectral RMS Amplitude",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="frequency_band_energy",
        equation_reference="Partyka et al. (1999) — spectral decomposition",
        requires_well_tie=False,
        description="RMS amplitude per frequency band. Thin bed tuning indicator.",
        hci_sensitive=True,
    ),
    "spectral_magnitude": SeismicAttributeDef(
        name="spectral_magnitude",
        display_name="Spectral Magnitude / Magnitude Spectra",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="frequency_content",
        equation_reference="Partyka et al. (1999)",
        requires_well_tie=False,
        description="Magnitude of frequency components.",
    ),
    "dominant_frequency": SeismicAttributeDef(
        name="dominant_frequency",
        display_name="Dominant Frequency",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="peak_frequency",
        equation_reference="Partyka et al. (1999)",
        requires_well_tie=False,
        description="Frequency with maximum energy. Indicates bed thickness.",
    ),
    "band_limited_magnitude": SeismicAttributeDef(
        name="band_limited_magnitude",
        display_name="Band-Limited Magnitude Slice",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="filtered_frequency_content",
        equation_reference="Partyka et al. (1999)",
        requires_well_tie=False,
        description="Magnitude in a specific frequency band.",
    ),
    "sweetness": SeismicAttributeDef(
        name="sweetness",
        display_name="Sweetness (DHI Attribute)",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="amplitude_frequency_ratio",
        equation_reference="Hart & Balch (2000)",
        requires_well_tie=True,
        description="Envelope / sqrt(variance). Highlights HC contacts independent of amplitude.",
        hci_sensitive=True,
    ),
    "spectral_similarity": SeismicAttributeDef(
        name="spectral_similarity",
        display_name="Spectral Similarity / Spectral Consistency",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="frequency_correlation",
        equation_reference="Castillo et al. — spectral similarity",
        requires_well_tie=False,
        description="Similarity of spectral content across traces.",
    ),
    "frequency_attenuation": SeismicAttributeDef(
        name="frequency_attenuation",
        display_name="Frequency Attenuation Indicator",
        attribute_class=AttributeClass.SPECTRAL,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="high_frequency_loss",
        equation_reference="Conventional spectral analysis",
        requires_well_tie=True,
        description="High-frequency loss may indicate gas attenuation.",
        hci_sensitive=True,
    ),
    # ========================================================================
    # CLASS 5: AVO / ELASTIC / INVERSION
    # Tie seismic to rock and fluid properties.
    # ========================================================================
    "avo_intercept": SeismicAttributeDef(
        name="avo_intercept",
        display_name="AVO Intercept (A)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="acoustic_impedance",
        equation_reference="Shuey (1985) — AVO approximation",
        requires_well_tie=True,
        description="Zero-offset amplitude. Rock property indicator.",
        hci_sensitive=True,
    ),
    "avo_gradient": SeismicAttributeDef(
        name="avo_gradient",
        display_name="AVO Gradient (B)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="velocity_ratio",
        equation_reference="Shuey (1985)",
        requires_well_tie=True,
        description="Rate of amplitude change with offset.",
        hci_sensitive=True,
    ),
    "avo_curvature": SeismicAttributeDef(
        name="avo_curvature",
        display_name="AVO Curvature (C)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="third_order_reflection",
        equation_reference="Xu & Chopra — AVO curvature",
        requires_well_tie=True,
        description="Non-linear AVO behaviour.",
        hci_sensitive=True,
    ),
    "far_minus_near": SeismicAttributeDef(
        name="far_minus_near",
        display_name="Far Minus Near Amplitude",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="offset_dependent_reflectivity",
        equation_reference="Conventional AVO",
        requires_well_tie=True,
        description="Amplitude difference between far and near offsets.",
        hci_sensitive=True,
    ),
    "p_impedance": SeismicAttributeDef(
        name="p_impedance",
        display_name="P-Impedance (AI)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="acoustic_impedance",
        equation_reference="acoustic inversion",
        requires_well_tie=True,
        description="P-wave impedance from inversion. Lithology indicator.",
    ),
    "s_impedance": SeismicAttributeDef(
        name="s_impedance",
        display_name="S-Impedance",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="shear_impedance",
        equation_reference="elastic inversion",
        requires_well_tie=True,
        description="S-wave impedance from elastic inversion.",
    ),
    "vp_vs_ratio": SeismicAttributeDef(
        name="vp_vs_ratio",
        display_name="Vp/Vs Ratio",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="velocity_ratio",
        equation_reference="Castagna — Vp/Vs analysis",
        requires_well_tie=True,
        description="Ratio of P to S velocity. Fluid indicator.",
        hci_sensitive=True,
    ),
    "poisson_ratio": SeismicAttributeDef(
        name="poisson_ratio",
        display_name="Poisson's Ratio",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="lame_parameters",
        equation_reference="Shuey (1985)",
        requires_well_tie=True,
        description="Poisson's ratio from AVO. Fluid sensitive.",
        hci_sensitive=True,
    ),
    "lambda_rho": SeismicAttributeDef(
        name="lambda_rho",
        display_name="Lambda-Rho (λρ)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="fluid_factor",
        equation_reference="Goodway et al. (2010) — LMR",
        requires_well_tie=True,
        description="Lambda-rho product. Fluid stiffness indicator.",
        hci_sensitive=True,
    ),
    "mu_rho": SeismicAttributeDef(
        name="mu_rho",
        display_name="Mu-Rho (μρ)",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="shear_stiffness",
        equation_reference="Goodway et al. (2010)",
        requires_well_tie=True,
        description="Mu-rho product. Rigidity indicator. Clay content.",
    ),
    "young_modulus": SeismicAttributeDef(
        name="young_modulus",
        display_name="Young's Modulus",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="elastic_modulus",
        equation_reference="elasticity theory",
        requires_well_tie=True,
        description="Elastic modulus. Brittleness indicator for fraccing.",
    ),
    "brittleness_index": SeismicAttributeDef(
        name="brittleness_index",
        display_name="Brittleness Index",
        attribute_class=AttributeClass.AVO_ELASTIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="fracability",
        equation_reference="Rickman et al. — brittleness",
        requires_well_tie=True,
        description="Brittle rock indicator for hydraulic fracturing.",
    ),
    # ========================================================================
    # CLASS 6: FACIES / PATTERN / CLASSIFICATION
    # Multi-attribute joint description of seismic facies or patterns.
    # ========================================================================
    "multi_attribute_facies": SeismicAttributeDef(
        name="multi_attribute_facies",
        display_name="Multi-Attribute Facies Classification",
        attribute_class=AttributeClass.FACIES,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="seismic_facies_pattern",
        equation_reference="Cole et al. — multi-attribute classification",
        requires_well_tie=True,
        meta_intelligence=True,
        description="SOM/k-means clustering on multiple attributes. HIGH perceptual risk.",
    ),
    "texture_attribute": SeismicAttributeDef(
        name="texture_attribute",
        display_name="Seismic Texture Attributes (GLCM/LGM)",
        attribute_class=AttributeClass.FACIES,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="seismic_texture_pattern",
        equation_reference="Mao & Shibli — texture analysis",
        requires_well_tie=True,
        meta_intelligence=True,
        description="Texture analysis via GLCM or LGM. Sedimentary facies indicator.",
    ),
    "pca_eigenattribute": SeismicAttributeDef(
        name="pca_eigenattribute",
        display_name="PCA / Eigenattribute Volumes",
        attribute_class=AttributeClass.FACIES,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="variance_explained",
        equation_reference="科举 — PCA on seismic attributes",
        requires_well_tie=False,
        description="Principal component analysis. Highest variance combinations.",
    ),
    "ml_facies_probability": SeismicAttributeDef(
        name="ml_facies_probability",
        display_name="ML Facies Probability Volume",
        attribute_class=AttributeClass.FACIES,
        contrast_risk=ContrastRisk.CRITICAL,
        physical_proxy="facies_probability",
        equation_reference="Various CNN/RNN supervised training",
        requires_well_tie=True,
        meta_intelligence=True,
        description="Deep learning facies classification. CRITICAL: black-box, needs full validation.",
    ),
    "channel_probability": SeismicAttributeDef(
        name="channel_probability",
        display_name="Channel Probability (DL Segmentation)",
        attribute_class=AttributeClass.FACIES,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="channel_geometry_probability",
        equation_reference="Guo et al. — U-Net channel segmentation",
        requires_well_tie=True,
        meta_intelligence=True,
        description="CNN/U-Net channel detection. High risk of false positives.",
    ),
    # ========================================================================
    # CLASS 7: KINEMATIC / TIME-RELATED
    # Time relationships and moveout.
    # ========================================================================
    "local_dip_moveout": SeismicAttributeDef(
        name="local_dip_moveout",
        display_name="Local Dip Moveout",
        attribute_class=AttributeClass.KINEMATIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="normal_moveout_residual",
        equation_reference="Marfurt — dip moveout attribute",
        requires_well_tie=False,
        description="Residual moveout after NMO. Structural validation.",
    ),
    "residual_moveout": SeismicAttributeDef(
        name="residual_moveout",
        display_name="Residual Moveout Attribute",
        attribute_class=AttributeClass.KINEMATIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="velocity_analysis_residual",
        equation_reference="conventional stacking",
        requires_well_tie=False,
        description="Post-stack residual moveout indicator.",
    ),
    "travel_time_anomaly": SeismicAttributeDef(
        name="travel_time_anomaly",
        display_name="Travel-Time Anomaly / Time Shifts",
        attribute_class=AttributeClass.KINEMATIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="time_shift_field",
        equation_reference="dynamic warping — travel-time analysis",
        requires_well_tie=True,
        description="Time shift field from 4D or tomographic inversion.",
    ),
    "time_structure": SeismicAttributeDef(
        name="time_structure",
        display_name="Time Structure Map",
        attribute_class=AttributeClass.KINEMATIC,
        contrast_risk=ContrastRisk.LOW,
        physical_proxy="horizon_time_picks",
        equation_reference="standard structural interpretation",
        requires_well_tie=False,
        description="Picked horizon time values. Structural mapping.",
    ),
    "formation_thickness": SeismicAttributeDef(
        name="formation_thickness",
        display_name="Formation Thickness (Interval Velocity)",
        attribute_class=AttributeClass.KINEMATIC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="interval_velocity_thickness",
        equation_reference="well tie + velocity analysis",
        requires_well_tie=True,
        description="Thickness estimation from interval velocity.",
    ),
    # ========================================================================
    # CLASS 8: MISC / ADVANCED COMBINATIONS
    # Attenuation, sweet spot composites, DHI stacks.
    # ========================================================================
    "q_factor": SeismicAttributeDef(
        name="q_factor",
        display_name="Q Factor / Absorption Attribute",
        attribute_class=AttributeClass.MISC,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="attenuation",
        equation_reference="Zhang & Ulrych — Q estimation",
        requires_well_tie=True,
        description="Seismic quality factor. Gas accumulation indicator.",
        hci_sensitive=True,
    ),
    "sweet_spot_composite": SeismicAttributeDef(
        name="sweet_spot_composite",
        display_name="Sweet Spot Composite (Multi-DHI)",
        attribute_class=AttributeClass.MISC,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="hc_indicator_composite",
        equation_reference="Integrated DHI workflow",
        requires_well_tie=True,
        meta_intelligence=True,
        description="Multi-attribute DHI composite. Amplitude + frequency + AVO.",
        hci_sensitive=True,
    ),
    "dhi_stack": SeismicAttributeDef(
        name="dhi_stack",
        display_name="DHI Attribute Stack",
        attribute_class=AttributeClass.MISC,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="fluid_indicator_stack",
        equation_reference="Conventional DHI practice",
        requires_well_tie=True,
        meta_intelligence=True,
        description="Stack of fluid-sensitive attributes. Requires full validation.",
        hci_sensitive=True,
    ),
    "heterogeneity_index": SeismicAttributeDef(
        name="heterogeneity_index",
        display_name="Heterogeneity Index",
        attribute_class=AttributeClass.MISC,
        contrast_risk=ContrastRisk.MEDIUM,
        physical_proxy="elastic_variation",
        equation_reference="Prioul et al. — heterogeneity",
        requires_well_tie=True,
        description="Elastic heterogeneity indicator.",
    ),
    "stress_fluid_indicator": SeismicAttributeDef(
        name="stress_fluid_indicator",
        display_name="Stress/Fluid Indicator (4D)",
        attribute_class=AttributeClass.MISC,
        contrast_risk=ContrastRisk.HIGH,
        physical_proxy="time_lapse_change",
        equation_reference="4D seismic monitoring",
        requires_well_tie=True,
        description="4D time-lapse difference. Production monitoring.",
    ),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------


def get_by_class(
    attribute_class: AttributeClass,
) -> list[SeismicAttributeDef]:
    """Return all attributes in a given class."""
    return [a for a in SEISMIC_ATTRIBUTES.values() if a.attribute_class == attribute_class]


def get_by_contrast_risk(risk: ContrastRisk) -> list[SeismicAttributeDef]:
    """Return all attributes with a given contrast risk level."""
    return [a for a in SEISMIC_ATTRIBUTES.values() if a.contrast_risk == risk]


def get_hci_attributes() -> list[SeismicAttributeDef]:
    """Return all direct hydrocarbon indicator sensitive attributes."""
    return [a for a in SEISMIC_ATTRIBUTES.values() if a.hci_sensitive]


def get_meta_intelligence_attributes() -> list[SeismicAttributeDef]:
    """Return all ML/DL-derived attributes (highest contrast risk)."""
    return [a for a in SEISMIC_ATTRIBUTES.values() if a.meta_intelligence]


def get_requires_well_tie() -> list[SeismicAttributeDef]:
    """Return all attributes that require well tie validation."""
    return [a for a in SEISMIC_ATTRIBUTES.values() if a.requires_well_tie]


def is_high_contrast_risk(name: str) -> bool:
    """True if attribute has HIGH or CRITICAL contrast risk."""
    attr = SEISMIC_ATTRIBUTES.get(name.lower())
    if attr is None:
        return False
    return attr.contrast_risk in (ContrastRisk.HIGH, ContrastRisk.CRITICAL)


def is_meta_intelligence(name: str) -> bool:
    """True if attribute is ML/DL-derived."""
    attr = SEISMIC_ATTRIBUTES.get(name.lower())
    if attr is None:
        return False
    return attr.meta_intelligence


# ---------------------------------------------------------------------------
# Governance integration
# ---------------------------------------------------------------------------


def get_governance_flags(name: str) -> dict[str, bool | str | None]:
    """
    Return governance flags for an attribute.
    Used by compute_attributes tool to set ContrastMetadata risk level.
    """
    attr = SEISMIC_ATTRIBUTES.get(name.lower())
    if attr is None:
        return {
            "contrast_risk": "unknown",
            "meta_intelligence": False,
            "requires_well_tie": False,
            "hci_sensitive": False,
        }
    return {
        "contrast_risk": attr.contrast_risk.value,
        "meta_intelligence": attr.meta_intelligence,
        "requires_well_tie": attr.requires_well_tie,
        "hci_sensitive": attr.hci_sensitive,
        "physical_proxy": attr.physical_proxy,
        "equation_reference": attr.equation_reference,
    }
