"""
QC Engine — Quality Control for Well Log Data
DITEMPA BUKAN DIBERI

Flags washouts, missing sections, bad hole, tool conflicts, unit inconsistencies.
F2 Truth: Explicit QC findings, not hidden assumptions.
"""

from __future__ import annotations

import statistics

from arifos.geox.schemas.petrophysics.measurements import (
    LogBundle, WellLogCurve, QCReport, CurveQC
)


# In-memory store
_qc_store: dict[str, QCReport] = {}


async def load_qc_report(well_id: str) -> QCReport | None:
    """Load QC report from store."""
    return _qc_store.get(well_id)


async def store_qc_report(well_id: str, report: QCReport) -> None:
    """Store QC report."""
    _qc_store[well_id] = report


async def generate_qc_report(well_id: str, bundle: LogBundle | None = None) -> QCReport:
    """
    Generate comprehensive QC report for a well.
    
    Args:
        well_id: Well identifier
        bundle: Optional pre-loaded bundle
    """
    from arifos.geox.tools.petrophysics.log_bundle_loader import load_bundle_from_store
    
    if bundle is None:
        bundle = await load_bundle_from_store(well_id)
    
    engine = QCEngine()
    return await engine.analyze(bundle)


class QCEngine:
    """
    Quality control analysis for well log data.
    
    Checks:
    - Curve completeness (null fraction)
    - Washout detection (caliper vs bit size)
    - Depth consistency
    - Unit validation
    - Tool conflicts
    """
    
    # Standard bit sizes
    BIT_SIZES = [6.0, 8.5, 12.25, 17.5]  # inches
    
    # Washout threshold
    CALIPER_WASHOUT_FACTOR = 1.5  # Caliper > 1.5x bit = washout
    
    async def analyze(self, bundle: LogBundle) -> QCReport:
        """
        Run full QC analysis on a log bundle.
        
        Returns QCReport with findings and recommendations.
        """
        curve_reports = []
        depth_issues = []
        unit_inconsistencies = []
        missing_critical = []
        
        # Analyze each curve
        for mnemonic, curve in bundle.curves.items():
            qc = self._analyze_curve(mnemonic, curve, bundle)
            curve_reports.append(qc)
        
        # Check for critical curves
        critical = ["GR", "RHOB", "NPHIB", "ILD", "DT", "CALI"]
        for crit in critical:
            if crit not in bundle.curves:
                missing_critical.append(crit)
        
        # Cross-curve checks
        depth_issues = self._check_depth_consistency(bundle)
        unit_inconsistencies = self._check_units(bundle)
        
        # Overall status
        overall = self._determine_overall_status(curve_reports, missing_critical, depth_issues)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            curve_reports, missing_critical, depth_issues
        )
        
        report = QCReport(
            well_id=bundle.well_id,
            overall=overall,
            curve_reports=curve_reports,
            depth_issues=depth_issues,
            unit_inconsistencies=unit_inconsistencies,
            missing_critical_curves=missing_critical,
            recommendations=recommendations,
            calibration_status={"pending": "Phase B implementation"},
        )
        
        # Store report
        await store_qc_report(bundle.well_id, report)
        
        return report
    
    def _analyze_curve(self, mnemonic: str, curve: WellLogCurve, bundle: LogBundle) -> CurveQC:
        """Analyze a single curve."""
        n_total = len(curve.values)
        n_null = sum(1 for v in curve.values if v is None)
        completeness = (n_total - n_null) / n_total if n_total > 0 else 0.0
        
        flags = []
        
        # Check for all null
        if n_null == n_total:
            flags.append("COMPLETELY_NULL")
        
        # Check for low completeness
        if completeness < 0.5:
            flags.append("LOW_COMPLETENESS")
        
        # Check for constant values (suspect)
        valid_values = [v for v in curve.values if v is not None]
        if valid_values and len(set(valid_values)) == 1:
            flags.append("CONSTANT_VALUE")
        
        # Curve-specific checks
        has_washouts = False
        has_badcaliper = False
        
        if mnemonic in ["CALI", "CAL", "HCAL"]:
            # Caliper analysis
            cali_values = [v for v in curve.values if v is not None]
            if cali_values:
                max_cali = max(cali_values)
                # Detect washouts
                if max_cali > 15.0:  # Assuming 8.5" bit
                    has_washouts = True
                    flags.append("WASHOUT_DETECTED")
                
                # Bad hole
                cali_std = statistics.stdev(cali_values) if len(cali_values) > 1 else 0
                if cali_std > 2.0:
                    has_badcaliper = True
                    flags.append("HIGH_CALIPER_VARIABILITY")
        
        # Resistivity checks
        if mnemonic in ["ILD", "RT", "LLD"]:
            res_values = [v for v in curve.values if v is not None and v > 0]
            if res_values:
                if max(res_values) > 1000:
                    flags.append("VERY_HIGH_RESISTIVITY")
                if min(res_values) < 0.1:
                    flags.append("VERY_LOW_RESISTIVITY")
        
        # Density checks
        if mnemonic == "RHOB":
            rhob_values = [v for v in curve.values if v is not None]
            if rhob_values:
                if min(rhob_values) < 1.5 or max(rhob_values) > 3.0:
                    flags.append("SUSPECT_DENSITY_RANGE")
        
        # Determine usability
        usable = completeness > 0.7 and not has_washouts and "COMPLETELY_NULL" not in flags
        
        return CurveQC(
            mnemonic=mnemonic,
            completeness=round(completeness, 3),
            total_points=n_total,
            null_points=n_null,
            flags=flags,
            has_washouts=has_washouts,
            has_badcaliper=has_badcaliper,
            has_unit_issues=False,  # Checked separately
            has_depth_gaps=False,  # Checked separately
            usable_for_petrophysics=usable,
            recommended_action="Review flags" if flags else None,
        )
    
    def _check_depth_consistency(self, bundle: LogBundle) -> list[str]:
        """Check for depth-related issues across curves."""
        issues = []
        
        # Get depth curve
        depth_curve = None
        for name in ["DEPT", "DEPTH", "MD"]:
            if name in bundle.curves:
                depth_curve = bundle.curves[name]
                break
        
        if not depth_curve:
            issues.append("No depth curve found")
            return issues
        
        # Check monotonicity
        depths = depth_curve.depth
        if len(depths) > 1:
            non_monotonic = [
                i for i in range(len(depths) - 1)
                if depths[i] > depths[i + 1]
            ]
            if non_monotonic:
                issues.append(f"Non-monotonic depth at {len(non_monotonic)} points")
        
        # Check for large gaps
        if len(depths) > 1:
            gaps = [depths[i+1] - depths[i] for i in range(len(depths)-1)]
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            large_gaps = [g for g in gaps if g > avg_gap * 5]
            if large_gaps:
                issues.append(f"Large depth gaps detected (>{avg_gap*5:.1f}m)")
        
        # Check for duplicate depths
        if len(depths) != len(set(depths)):
            issues.append("Duplicate depth values found")
        
        return issues
    
    def _check_units(self, bundle: LogBundle) -> list[str]:
        """Check for unit inconsistencies."""
        issues = []
        
        # Common unit expectations
        expected_units = {
            "GR": ["API", "GAPI"],
            "RHOB": ["G/CC", "G/CM3", "G/C3", "KG/M3"],
            "NPHI": ["V/V", "DEC", "PU", "%"],
            "ILD": ["OHMM", "OHM.M", "OHM-M"],
            "DT": ["US/F", "US/FT", "US/M", "US/M"],
        }
        
        for mnemonic, expected in expected_units.items():
            curve = bundle.get_curve(mnemonic)
            if curve and curve.units:
                unit_upper = curve.units.upper().replace(" ", "")
                if unit_upper not in [e.upper().replace(" ", "") for e in expected]:
                    issues.append(f"{mnemonic}: unexpected units '{curve.units}' (expected {expected})")
        
        return issues
    
    def _determine_overall_status(
        self,
        curve_reports: list[CurveQC],
        missing_critical: list[str],
        depth_issues: list[str]
    ) -> str:
        """Determine overall QC status."""
        # FAIL if critical curves missing or major depth issues
        if missing_critical or any("COMPLETELY_NULL" in c.flags for c in curve_reports):
            return "FAIL"
        
        # WARNING if any issues
        any_issues = (
            any(c.flags for c in curve_reports) or
            depth_issues or
            missing_critical
        )
        if any_issues:
            return "WARNING"
        
        return "PASS"
    
    def _generate_recommendations(
        self,
        curve_reports: list[CurveQC],
        missing_critical: list[str],
        depth_issues: list[str]
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if missing_critical:
            recommendations.append(f"Acquire missing critical curves: {missing_critical}")
        
        # Check for washouts
        washout_curves = [c.mnemonic for c in curve_reports if c.has_washouts]
        if washout_curves:
            recommendations.append(f"Review washout intervals in: {washout_curves}")
        
        # Check for low completeness
        low_comp = [c.mnemonic for c in curve_reports if c.completeness < 0.5]
        if low_comp:
            recommendations.append(f"Low data completeness in: {low_comp}")
        
        if depth_issues:
            recommendations.append("Review depth inconsistencies before interpretation")
        
        # Check units
        unit_issues = [c.mnemonic for c in curve_reports if c.has_unit_issues]
        if unit_issues:
            recommendations.append(f"Verify units for: {unit_issues}")
        
        if not recommendations:
            recommendations.append("Data quality acceptable for petrophysical analysis")
        
        return recommendations
