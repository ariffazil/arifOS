"""
AttributePipeline — Chain Physical Attribute Computations
DITEMPA BUKAN DIBERI

Chains multiple attribute computations with:
  - Dependency tracking
  - Uncertainty propagation
  - Transform chain accumulation
  - Checkpoint governance

Ensures the PHYSICAL_SIGNAL layer is complete before any VISUAL_ENCODING.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable
from enum import Enum, auto


class StageStatus(Enum):
    """Status of a pipeline stage."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETE = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class PipelineStage:
    """
    A single stage in an attribute pipeline.
    
    Each stage:
      - Has a name and computation function
      - Declares dependencies (other stages that must run first)
      - Produces output that later stages can use
      - Has its own transform chain contribution
    """
    name: str
    description: str
    
    # Computation
    compute: Callable[..., Awaitable[tuple[Any, list[str]]]]
    
    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    
    # Status
    status: StageStatus = StageStatus.PENDING
    
    # Results
    output: Any = None
    transform_chain: list[str] = field(default_factory=list)
    error: str | None = None
    
    # Uncertainty
    uncertainty: float = 0.1  # 0-1 uncertainty in this stage's output
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.name,
            "depends_on": self.depends_on,
            "has_output": self.output is not None,
            "transform_count": len(self.transform_chain),
            "uncertainty": self.uncertainty,
        }


class AttributePipeline:
    """
    Pipeline for chaining attribute computations.
    
    Ensures proper ordering:
      1. Primary physical attributes (no dependencies)
      2. Derived attributes (depend on primary)
      3. Composite attributes (depend on multiple)
    
    Tracks cumulative:
      - Transform chain (for conflation assessment)
      - Uncertainty (for F7 Humility)
      - Execution order (for audit trail)
    """
    
    def __init__(self, name: str = "unnamed_pipeline"):
        self.name = name
        self.stages: dict[str, PipelineStage] = {}
        self._outputs: dict[str, Any] = {}
        self._complete_chain: list[str] = []
        self._cumulative_uncertainty: float = 0.0
    
    def add_stage(self, stage: PipelineStage) -> "AttributePipeline":
        """Add a stage to the pipeline."""
        self.stages[stage.name] = stage
        return self
    
    def get_stage(self, name: str) -> PipelineStage | None:
        """Get a stage by name."""
        return self.stages.get(name)
    
    def get_execution_order(self) -> list[str]:
        """
        Determine execution order based on dependencies.
        
        Uses topological sort to ensure dependencies are satisfied.
        """
        # Simple topological sort
        executed = set()
        order = []
        remaining = set(self.stages.keys())
        
        while remaining:
            # Find stages whose dependencies are all satisfied
            ready = {
                name for name in remaining
                if all(d in executed for d in self.stages[name].depends_on)
            }
            
            if not ready:
                # Circular dependency or missing dependency
                raise ValueError(f"Cannot resolve dependencies for: {remaining}")
            
            for name in ready:
                order.append(name)
                executed.add(name)
                remaining.remove(name)
        
        return order
    
    async def execute(self, initial_input: Any | None = None) -> dict[str, Any]:
        """
        Execute all stages in dependency order.
        
        Returns summary of execution results.
        """
        order = self.get_execution_order()
        
        for stage_name in order:
            stage = self.stages[stage_name]
            stage.status = StageStatus.RUNNING
            
            try:
                # Prepare inputs from dependencies
                inputs = {
                    dep: self._outputs[dep]
                    for dep in stage.depends_on
                }
                
                # Add initial input if this is the first stage
                if initial_input is not None and not stage.depends_on:
                    inputs["input"] = initial_input
                
                # Execute stage
                if inputs:
                    output, chain = await stage.compute(**inputs)
                else:
                    output, chain = await stage.compute()
                
                # Store results
                stage.output = output
                stage.transform_chain = chain
                stage.status = StageStatus.COMPLETE
                self._outputs[stage_name] = output
                self._complete_chain.extend(chain)
                
                # Accumulate uncertainty
                self._cumulative_uncertainty = min(
                    1.0,
                    self._cumulative_uncertainty + stage.uncertainty
                )
                
            except Exception as e:
                stage.status = StageStatus.FAILED
                stage.error = str(e)
                # Continue with other stages unless critical
        
        return self.get_summary()
    
    def get_summary(self) -> dict[str, Any]:
        """Get execution summary."""
        completed = sum(1 for s in self.stages.values() if s.status == StageStatus.COMPLETE)
        failed = sum(1 for s in self.stages.values() if s.status == StageStatus.FAILED)
        
        return {
            "pipeline_name": self.name,
            "stage_count": len(self.stages),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / len(self.stages) if self.stages else 0,
            "cumulative_uncertainty": round(self._cumulative_uncertainty, 3),
            "transform_chain_length": len(self._complete_chain),
            "transforms": self._complete_chain,
            "stages": [s.to_dict() for s in self.stages.values()],
            "outputs": {k: type(v).__name__ for k, v in self._outputs.items()},
        }
    
    def get_output(self, stage_name: str) -> Any:
        """Get output from a completed stage."""
        stage = self.stages.get(stage_name)
        if stage and stage.status == StageStatus.COMPLETE:
            return stage.output
        return None
    
    def get_all_outputs(self) -> dict[str, Any]:
        """Get all stage outputs."""
        return {
            name: stage.output
            for name, stage in self.stages.items()
            if stage.status == StageStatus.COMPLETE
        }
