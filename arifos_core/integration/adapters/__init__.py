"""
arifos_core.integration.adapters - LLM Provider Adapters

Contains LLM interface and governed LLM wrapper.

Version: v42.0.0
"""

from .llm_interface import LLMInterface
from .governed_llm import GovernedPipeline

__all__ = [
    "LLMInterface",
    "GovernedPipeline",
]

# v42: Backward compat alias
GovernedLLM = GovernedPipeline
