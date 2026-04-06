"""Canonical ABI location for arifosmcp.

Provides get_request_schema / get_response_schema and all Pydantic model classes
from the ABI registry. Gracefully falls back to stubs if arifos_mcp is unavailable.
"""

from __future__ import annotations

from typing import Any

try:
    from arifos_mcp.abi.v1_0 import (  # type: ignore[import]
        ABI_SCHEMAS,
        BaseRequest,
        BaseResponse,
        InitAnchorRequest,
        InitAnchorResponse,
        IdentityResolution,
        ArifOSKernelRequest,
        ArifOSKernelResponse,
        ApexJudgeRequest,
        ApexJudgeResponse,
        VaultLedgerRequest,
        VaultLedgerResponse,
        AgiMindRequest,
        AgiMindResponse,
        AsiHeartRequest,
        AsiHeartResponse,
        EngineeringMemoryRequest,
        EngineeringMemoryResponse,
        PhysicsRealityRequest,
        PhysicsRealityResponse,
        MathEstimatorRequest,
        MathEstimatorResponse,
        CodeEngineRequest,
        CodeEngineResponse,
        ArchitectRegistryRequest,
        ArchitectRegistryResponse,
        get_request_schema,
        get_response_schema,
        validate_request,
        validate_response,
    )
    _ABI_AVAILABLE = True
except Exception:
    _ABI_AVAILABLE = False
    ABI_SCHEMAS: dict = {}  # type: ignore[assignment]

    def get_request_schema(tool_name: str) -> type | None:  # type: ignore[misc]
        return None

    def get_response_schema(tool_name: str) -> type | None:  # type: ignore[misc]
        return None

    def validate_request(tool_name: str, payload: dict[str, Any]) -> Any:  # type: ignore[misc]
        return payload

    def validate_response(tool_name: str, payload: dict[str, Any]) -> Any:  # type: ignore[misc]
        return payload

    # Stub model classes so governance tools can import without crashing
    from pydantic import BaseModel  # noqa: F401

    class BaseRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class BaseResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class InitAnchorRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class InitAnchorResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class IdentityResolution(BaseModel):  # type: ignore[no-redef]
        pass

    class ArifOSKernelRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class ArifOSKernelResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class ApexJudgeRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class ApexJudgeResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class VaultLedgerRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class VaultLedgerResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class AgiMindRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class AgiMindResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class AsiHeartRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class AsiHeartResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class EngineeringMemoryRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class EngineeringMemoryResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class PhysicsRealityRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class PhysicsRealityResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class MathEstimatorRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class MathEstimatorResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class CodeEngineRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class CodeEngineResponse(BaseModel):  # type: ignore[no-redef]
        pass

    class ArchitectRegistryRequest(BaseModel):  # type: ignore[no-redef]
        pass

    class ArchitectRegistryResponse(BaseModel):  # type: ignore[no-redef]
        pass


__all__ = [
    "ABI_SCHEMAS",
    "BaseRequest", "BaseResponse",
    "InitAnchorRequest", "InitAnchorResponse", "IdentityResolution",
    "ArifOSKernelRequest", "ArifOSKernelResponse",
    "ApexJudgeRequest", "ApexJudgeResponse",
    "VaultLedgerRequest", "VaultLedgerResponse",
    "AgiMindRequest", "AgiMindResponse",
    "AsiHeartRequest", "AsiHeartResponse",
    "EngineeringMemoryRequest", "EngineeringMemoryResponse",
    "PhysicsRealityRequest", "PhysicsRealityResponse",
    "MathEstimatorRequest", "MathEstimatorResponse",
    "CodeEngineRequest", "CodeEngineResponse",
    "ArchitectRegistryRequest", "ArchitectRegistryResponse",
    "get_request_schema", "get_response_schema",
    "validate_request", "validate_response",
]
