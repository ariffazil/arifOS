import warnings

warnings.warn(
    "arifos.api is deprecated. Use arifos.core.integration.api for REST or AAA_MCP for MCP.",
    DeprecationWarning,
    stacklevel=2,
)

from arifos.core.integration.api import create_app, app
from .server import run_server

__all__ = ["create_app", "app", "run_server"]
