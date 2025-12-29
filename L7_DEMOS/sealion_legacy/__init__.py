"""
SEA-LION Integration Shim for arifOS

This module provides import compatibility for the SEA-LION integration.
The actual SEA-LION adapter is in arifos_core/integration/adapters/llm_sealion.py

Version: v42.0.0
"""

from typing import Any, Dict, Optional

# Re-export from arifos_core.integration.adapters.llm_sealion if available
try:
    from arifos_core.integration.adapters.llm_sealion import (
        SEALIONAdapter,
        SEALIONConfig,
        create_sealion_adapter,
    )
except ImportError:
    # SEA-LION adapter not yet implemented, provide stubs
    class SEALIONConfig:
        """Configuration for SEA-LION adapter (stub)."""
        def __init__(
            self,
            model_name: str = "aisingapore/sea-lion-7b-instruct",
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            **kwargs: Any
        ) -> None:
            self.model_name = model_name
            self.api_key = api_key
            self.base_url = base_url
            self.extra_config = kwargs

    class SEALIONAdapter:
        """SEA-LION adapter for arifOS (stub)."""
        def __init__(self, config: Optional[SEALIONConfig] = None) -> None:
            self.config = config or SEALIONConfig()

        def generate(self, prompt: str, **kwargs: Any) -> str:
            """Generate response (stub - raises NotImplementedError)."""
            raise NotImplementedError(
                "SEA-LION adapter not yet implemented. "
                "Install aisingapore/sea-lion and configure arifos_core."
            )

        def is_available(self) -> bool:
            """Check if SEA-LION is available."""
            return False

    def create_sealion_adapter(config: Optional[Dict[str, Any]] = None) -> SEALIONAdapter:
        """Factory function to create SEA-LION adapter."""
        if config:
            return SEALIONAdapter(SEALIONConfig(**config))
        return SEALIONAdapter()


__all__ = [
    "SEALIONAdapter",
    "SEALIONConfig",
    "create_sealion_adapter",
]
