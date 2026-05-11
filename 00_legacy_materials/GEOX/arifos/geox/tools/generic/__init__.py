"""
GEOX Generic Tools — Domain-Agnostic Contrast-Governed Tools
DITEMPA BUKAN DIBERI

Tools that work across all domains (seismic, medical, satellite, etc.):

  - ContrastGovernedTool: Base class for all ToAC-governed tools
  - AttributePipeline: Chain physical attribute computations
  - VisualizationAuditor: Audit any visualization for conflation

These tools provide the foundation that domain-specific tools extend.
"""

from .contrast_governed_tool import ContrastGovernedTool, ToolResult
from .attribute_pipeline import AttributePipeline, PipelineStage
from .visualization_auditor import VisualizationAuditor, VisualizationAuditResult

__all__ = [
    # Base classes
    "ContrastGovernedTool",
    "ToolResult",
    # Pipeline
    "AttributePipeline",
    "PipelineStage",
    # Auditor
    "VisualizationAuditor",
    "VisualizationAuditResult",
]
