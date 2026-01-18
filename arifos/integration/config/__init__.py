"""arifOS Configuration Module.

Provides typed, validated access to arifOS governance specifications.

Usage:
    from arifos.integration.config import InterfaceAuthorityConfig
    
    config = InterfaceAuthorityConfig.load()
"""

from .interface_authority_config import (
    InterfaceAuthorityConfig,
    VerdictType,
    VetoType,
    FederatedAgent,
    Identity,
    LLMContract,
    Roles,
    DeploymentPolicy,
    ToolAndActionPolicy,
)

__all__ = [
    "InterfaceAuthorityConfig",
    "VerdictType",
    "VetoType",
    "FederatedAgent",
    "Identity",
    "LLMContract",
    "Roles",
    "DeploymentPolicy",
    "ToolAndActionPolicy",
]
