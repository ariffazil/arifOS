"""
ContrastGovernedTool — Base Class for All ToAC-Governed Tools
DITEMPA BUKAN DIBERI

Every GEOX tool extends this base class, inheriting:
  - Automatic contrast taxonomy creation
  - Transform chain documentation
  - Floor compliance checking (F1, F4, F7, F9, F13)
  - Verdict generation

This ensures ALL tools in GEOX follow the Theory of Anomalous Contrast.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from typing import Any
from abc import ABC, abstractmethod
import uuid

from ...THEORY import (
    ContrastTaxonomy,
    SourceDomain,
    VisualTransform,
    PhysicalProxy,
    ConfidenceClass,
    assess_conflation_risk,
    GEOX_BLOCK,
    GEOX_HOLD,
    GEOX_SEAL,
)
from ...ENGINE import AnomalyDetector


@dataclass
class ToolResult:
    """Standard result from any ContrastGovernedTool."""

    # Tool output
    output: Any
    success: bool = True
    error_message: str | None = None

    # Contrast governance
    taxonomy: ContrastTaxonomy | None = None
    transform_chain: list[str] = field(default_factory=list)

    # Verdict
    verdict: str = "PENDING"
    verdict_reason: str | None = None

    # Floor compliance
    floor_violations: list[str] = field(default_factory=list)

    # Audit trail
    tool_name: str = "unknown"
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "verdict": self.verdict,
            "verdict_reason": self.verdict_reason,
            "tool_name": self.tool_name,
            "execution_id": self.execution_id,
            "taxonomy": self.taxonomy.to_dict() if self.taxonomy else None,
            "transform_chain": self.transform_chain,
            "floor_violations": self.floor_violations,
            "has_output": self.output is not None,
        }


class ContrastGovernedTool(ABC):
    """
    Base class for all ToAC-governed tools.

    Subclasses MUST implement:
      - _execute_impl(): The actual tool logic
      - get_tool_metadata(): Tool description and requirements

    Subclasses SHOULD override:
      - _create_taxonomy(): Domain-specific taxonomy creation
      - _check_compliance(): Additional compliance checks

    The base class handles:
      - Taxonomy creation
      - Transform chain tracking
      - Floor compliance
      - Verdict generation
    """

    def __init__(self, domain: str = "generic"):
        self.domain = domain
        self.anomaly_detector = AnomalyDetector()
        self._execution_count = 0

    @property
    @abstractmethod
    def tool_name(self) -> str:
        """Tool name for identification."""
        pass

    @abstractmethod
    async def _execute_impl(self, *args, **kwargs) -> tuple[Any, list[str]]:
        """
        Implement the tool logic.

        Returns:
          - output: The tool output
          - transform_chain: List of transforms applied
        """
        pass

    def get_tool_metadata(self) -> dict[str, Any]:
        """Get tool metadata. Override for domain-specific info."""
        return {
            "name": self.tool_name,
            "domain": self.domain,
            "type": "contrast_governed",
            "description": self.__doc__ or "No description provided",
        }

    async def execute(self, *args, **kwargs) -> ToolResult:
        """
        Execute the tool with full ToAC governance.

        This method:
          1. Creates contrast taxonomy
          2. Runs the tool implementation
          3. Checks floor compliance
          4. Generates verdict
          5. Returns ToolResult with full metadata
        """
        self._execution_count += 1
        execution_id = f"{self.tool_name}-{self._execution_count}"

        try:
            # Step 1: Create taxonomy
            taxonomy = self._create_taxonomy(*args, **kwargs)

            # Step 2: Execute implementation
            output, transform_chain = await self._execute_impl(*args, **kwargs)

            # Step 3: Update taxonomy with transforms
            taxonomy = self._update_taxonomy_with_transforms(taxonomy, transform_chain)

            # Step 4: Check compliance
            floor_violations = self._check_compliance(output, taxonomy)

            # Step 5: Generate verdict
            verdict, reason = self._generate_verdict(taxonomy, transform_chain, floor_violations)

            return ToolResult(
                output=output,
                success=True,
                taxonomy=taxonomy,
                transform_chain=transform_chain,
                verdict=verdict,
                verdict_reason=reason,
                floor_violations=floor_violations,
                tool_name=self.tool_name,
                execution_id=execution_id,
            )

        except Exception as e:
            # Tool execution failed
            return ToolResult(
                output=None,
                success=False,
                error_message=str(e),
                verdict=GEOX_BLOCK,
                verdict_reason=f"Tool execution failed: {type(e).__name__}: {e}",
                tool_name=self.tool_name,
                execution_id=execution_id,
            )

    def _create_taxonomy(self, *args, **kwargs) -> ContrastTaxonomy:
        """
        Create contrast taxonomy for this execution.

        Override for domain-specific taxonomy creation.
        """
        # Default: create generic taxonomy
        return ContrastTaxonomy(
            source=SourceDomain.UNKNOWN,
            source_details={"type": "unknown"},
            transforms=[],
            proxy=PhysicalProxy(
                visual_feature="unknown",
                claimed_physical_quantity="unknown",
                proxy_validity="unverified",
                reliability=0.1,
            ),
            confidence=ConfidenceClass(
                value=0.05,
                confidence_type="detection",
                justification="Default confidence for unknown source",
            ),
            domain=self.domain,
        )

    def _update_taxonomy_with_transforms(
        self,
        taxonomy: ContrastTaxonomy,
        transform_chain: list[str],
    ) -> ContrastTaxonomy:
        """Update taxonomy with the transform chain that was applied."""
        from ...ENGINE import get_registry

        registry = get_registry()
        visual_transforms = []

        for transform_name in transform_chain:
            profile = registry.get(transform_name)
            if profile:
                # Map TransformProfile to VisualTransform
                visual_transforms.append(
                    VisualTransform(
                        name=profile.transform_name,
                        category=profile.transform_type,
                        artifact_risk=(
                            "low"
                            if profile.risk_level == "LOW"
                            else "medium" if profile.risk_level == "MEDIUM" else "high"
                        ),
                    )
                )
            else:
                # Unknown transform - high risk
                visual_transforms.append(
                    VisualTransform(
                        name=transform_name,
                        category="unknown",
                        artifact_risk="high",
                    )
                )

        # Return new taxonomy with updated transforms
        return ContrastTaxonomy(
            source=taxonomy.source,
            source_details=taxonomy.source_details,
            transforms=visual_transforms,
            proxy=taxonomy.proxy,
            confidence=taxonomy.confidence,
            domain=taxonomy.domain,
        )

    def _check_compliance(
        self,
        output: Any,
        taxonomy: ContrastTaxonomy,
    ) -> list[str]:
        """
        Additional compliance checks. Override for domain-specific checks.

        Returns list of violation descriptions.
        """
        return []

    def _generate_verdict(
        self,
        taxonomy: ContrastTaxonomy,
        transform_chain: list[str],
        floor_violations: list[str],
    ) -> tuple[str, str]:
        """
        Generate GEOX verdict based on compliance and risk.

        Returns (verdict, reason).
        """
        # Check for floor violations first
        if "F1_reversibility" in floor_violations:
            return GEOX_BLOCK, "F1 REVERSIBILITY VIOLATION: Cannot undo operation"

        if "F9_anti_hantu" in floor_violations:
            return GEOX_BLOCK, "F9 ANTI-HANTU VIOLATION: Phantom data detected"

        # Check transform chain risk
        from ...ENGINE import get_registry

        registry = get_registry()
        chain_analysis = registry.analyze_chain(transform_chain)

        if chain_analysis.get("risk_level") == "HIGH":
            return GEOX_HOLD, (
                f"HIGH RISK TRANSFORM CHAIN: "
                f"Total amplification {chain_analysis.get('total_amplification', 'unknown')}x. "
                f"Warnings: {chain_analysis.get('warnings', [])}"
            )

        # Check conflation risk
        verdict, triggers, metadata = assess_conflation_risk(taxonomy, self.domain)
        geox_verdict = verdict.to_geox_verdict()

        if geox_verdict == GEOX_HOLD:
            return GEOX_HOLD, f"CONFLATION RISK: {metadata.get('risk_level', 'unknown')}"

        if geox_verdict == GEOX_BLOCK:
            return GEOX_BLOCK, "CRITICAL CONFLATION RISK: Visual and physical conflation detected"

        # All checks passed
        return GEOX_SEAL, "All compliance checks passed, no critical conflation risk"


def contrast_governed(domain: str = "generic"):
    """
    Decorator to make a function a ContrastGovernedTool.

    Usage:
        @contrast_governed(domain="seismic")
        async def my_tool(data, param1):
            # Tool logic
            return output, ["transform1", "transform2"]
    """

    def decorator(func):
        class WrapperTool(ContrastGovernedTool):
            tool_name = func.__name__

            async def _execute_impl(self, *args, **kwargs):
                # Call the wrapped function
                result = await func(*args, **kwargs)

                # Result should be (output, transform_chain) or just output
                if isinstance(result, tuple) and len(result) == 2:
                    return result
                else:
                    # Default transform chain
                    return result, ["unknown_transform"]

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            tool = WrapperTool(domain=domain)
            return await tool.execute(*args, **kwargs)

        return wrapper

    return decorator
