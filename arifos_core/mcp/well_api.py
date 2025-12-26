"""
well_api.py - @WELL Universal REST API Server

FastAPI server providing universal HTTP interface for governed file operations.
All AI coding agents can use this REST API regardless of their native tool format.

Migrated from: L4_MCP/arifos_well/server/app.py (v42 migration)

Endpoints:
- GET  /health              - Server health check
- GET  /well/status         - @WELL status and version
- GET  /well/list-files     - List files with protection status
- GET  /well/check-health   - Repository health check
- POST /well/heal-structure - Create missing layer directories
- POST /well/relocate       - Move file with audit trail
- POST /well/duplicate      - Copy file with audit trail
- POST /well/retire         - Archive file instead of delete
- POST /well/undo-last-care - Undo last reversible operation
- POST /well/batch-relocate - Batch file operations (888_HOLD for large)
- GET  /well/audit-history  - Get audit trail

Version: v42.0.0
License: AGPL-3.0

DITEMPA BUKAN DIBERI - Forged, not given
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import from L3 core
try:
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        WellHealthReport,
        WellOperationResult,
        create_well_file_care,
    )
except ImportError:
    # Fallback for standalone testing
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        WellHealthReport,
        WellOperationResult,
        create_well_file_care,
    )


# -----------------------------------------------------------------------------
# Pydantic Models for API
# -----------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Server health response."""
    status: str = "healthy"
    service: str = "@WELL Universal API"
    version: str = WellConstants.VERSION


class WellStatusResponse(BaseModel):
    """@WELL status response."""
    version: str
    codename: str
    repo_root: str
    audit_log: str
    protected_files: List[str]
    valid_layers: List[str]


class FileInfo(BaseModel):
    """File information."""
    path: str
    name: str
    is_dir: bool
    size: int
    modified: str
    checksum: Optional[str] = None
    protected: bool = False
    protection_reason: Optional[str] = None


class ListFilesResponse(BaseModel):
    """List files response."""
    path: str
    pattern: str
    recursive: bool
    files: List[FileInfo]
    total: int


class HealthReportResponse(BaseModel):
    """Health check response."""
    is_healthy: bool
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]
    file_count: int
    directory_count: int
    layer_status: Dict[str, bool]


class RelocateRequest(BaseModel):
    """Relocate file request."""
    source: str = Field(..., description="Source file path")
    target: str = Field(..., description="Target file path")
    create_backup: bool = Field(True, description="Create backup before moving")


class DuplicateRequest(BaseModel):
    """Duplicate file request."""
    source: str = Field(..., description="Source file path")
    target: str = Field(..., description="Target file path")


class RetireRequest(BaseModel):
    """Retire file request."""
    path: str = Field(..., description="File path to retire")
    archive_dir: str = Field("archive", description="Archive directory")


class BatchRelocateRequest(BaseModel):
    """Batch relocate request."""
    operations: List[Dict[str, str]] = Field(
        ...,
        description="List of {source, target} operations"
    )
    dry_run: bool = Field(False, description="Validate without executing")


class OperationResponse(BaseModel):
    """Single operation response."""
    success: bool
    operation_type: str
    source_path: str
    target_path: Optional[str] = None
    message: str
    audit_entry: Optional[Dict[str, Any]] = None


class BatchOperationResponse(BaseModel):
    """Batch operation response."""
    total: int
    successful: int
    failed: int
    results: List[OperationResponse]


class AuditHistoryResponse(BaseModel):
    """Audit history response."""
    total: int
    entries: List[Dict[str, Any]]


# -----------------------------------------------------------------------------
# Application Factory
# -----------------------------------------------------------------------------


def create_app(repo_root: Optional[str] = None) -> FastAPI:
    """
    Create FastAPI application with @WELL endpoints.

    Args:
        repo_root: Root directory of the repository (default: current directory)

    Returns:
        FastAPI application instance
    """
    app = FastAPI(
        title="@WELL Universal API",
        description=(
            "Universal file care interface for governed migrations.\n\n"
            "Supports: Claude MCP, GitHub Copilot, ChatGPT Codex, Google Gemini CLI\n\n"
            "**DITEMPA BUKAN DIBERI** - Forged, not given"
        ),
        version=WellConstants.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS for cross-platform access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create @WELL instance
    well = create_well_file_care(repo_root)

    # -------------------------------------------------------------------------
    # Health Endpoints
    # -------------------------------------------------------------------------

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check() -> HealthResponse:
        """Server health check."""
        return HealthResponse()

    @app.get("/well/status", response_model=WellStatusResponse, tags=["Status"])
    async def well_status() -> WellStatusResponse:
        """Get @WELL status and configuration."""
        return WellStatusResponse(
            version=WellConstants.VERSION,
            codename=WellConstants.CODENAME,
            repo_root=str(well.repo_root),
            audit_log=str(well.audit_log_path),
            protected_files=list(WellConstants.PROTECTED_FILES),
            valid_layers=list(WellConstants.VALID_LAYERS),
        )

    # -------------------------------------------------------------------------
    # File Listing Endpoints
    # -------------------------------------------------------------------------

    @app.get("/well/list-files", response_model=ListFilesResponse, tags=["Files"])
    async def list_files(
        path: str = Query(".", description="Directory path"),
        pattern: str = Query("*", description="Glob pattern"),
        recursive: bool = Query(False, description="Recurse into subdirectories"),
    ) -> ListFilesResponse:
        """List files in a directory with protection status."""
        files = well.list_files(path=path, pattern=pattern, recursive=recursive)
        return ListFilesResponse(
            path=path,
            pattern=pattern,
            recursive=recursive,
            files=[FileInfo(**f) for f in files],
            total=len(files),
        )

    # -------------------------------------------------------------------------
    # Health Check Endpoints
    # -------------------------------------------------------------------------

    @app.get("/well/check-health", response_model=HealthReportResponse, tags=["Health"])
    async def check_health() -> HealthReportResponse:
        """Check repository structure health."""
        report = well.check_health()
        return HealthReportResponse(**report.to_dict())

    @app.post("/well/heal-structure", response_model=HealthReportResponse, tags=["Health"])
    async def heal_structure(
        create_missing_layers: bool = Query(True, description="Create missing L1-L7 directories"),
    ) -> HealthReportResponse:
        """Heal repository structure by creating missing directories."""
        report = well.heal_structure(create_missing_layers=create_missing_layers)
        return HealthReportResponse(**report.to_dict())

    # -------------------------------------------------------------------------
    # File Operation Endpoints
    # -------------------------------------------------------------------------

    @app.post("/well/relocate", response_model=OperationResponse, tags=["Operations"])
    async def relocate_file(request: RelocateRequest) -> OperationResponse:
        """
        Relocate (move) a file with full audit trail.

        F1 Amanah compliant: Creates backup, verifies checksum, logs operation.
        """
        result = well.relocate(
            source=request.source,
            target=request.target,
            create_backup=request.create_backup,
        )
        return OperationResponse(
            success=result.success,
            operation_type=result.operation_type.value,
            source_path=result.source_path,
            target_path=result.target_path,
            message=result.message,
            audit_entry=result.audit_entry.to_dict() if result.audit_entry else None,
        )

    @app.post("/well/duplicate", response_model=OperationResponse, tags=["Operations"])
    async def duplicate_file(request: DuplicateRequest) -> OperationResponse:
        """
        Duplicate (copy) a file with audit trail.

        Creates a copy while preserving the original.
        """
        result = well.duplicate(
            source=request.source,
            target=request.target,
        )
        return OperationResponse(
            success=result.success,
            operation_type=result.operation_type.value,
            source_path=result.source_path,
            target_path=result.target_path,
            message=result.message,
            audit_entry=result.audit_entry.to_dict() if result.audit_entry else None,
        )

    @app.post("/well/retire", response_model=OperationResponse, tags=["Operations"])
    async def retire_file(request: RetireRequest) -> OperationResponse:
        """
        Retire (archive) a file instead of deleting it.

        Moves file to archive directory with timestamp.
        """
        result = well.retire(
            path=request.path,
            archive_dir=request.archive_dir,
        )
        return OperationResponse(
            success=result.success,
            operation_type=result.operation_type.value,
            source_path=result.source_path,
            target_path=result.target_path,
            message=result.message,
            audit_entry=result.audit_entry.to_dict() if result.audit_entry else None,
        )

    @app.post("/well/undo-last-care", response_model=OperationResponse, tags=["Operations"])
    async def undo_last_care() -> OperationResponse:
        """
        Undo the last reversible operation.

        Reverses the most recent relocate or duplicate operation.
        """
        result = well.undo_last()
        return OperationResponse(
            success=result.success,
            operation_type=result.operation_type.value,
            source_path=result.source_path,
            target_path=result.target_path,
            message=result.message,
            audit_entry=result.audit_entry.to_dict() if result.audit_entry else None,
        )

    # -------------------------------------------------------------------------
    # Batch Operation Endpoints
    # -------------------------------------------------------------------------

    @app.post("/well/batch-relocate", response_model=BatchOperationResponse, tags=["Batch"])
    async def batch_relocate(request: BatchRelocateRequest) -> BatchOperationResponse:
        """
        Batch relocate files.

        888_HOLD triggered if batch size exceeds limit (10 files).
        Use dry_run=true to validate operations first.
        """
        results = well.batch_relocate(
            operations=request.operations,
            dry_run=request.dry_run,
        )

        # Count successes/failures
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        return BatchOperationResponse(
            total=len(results),
            successful=successful,
            failed=failed,
            results=[
                OperationResponse(
                    success=r.success,
                    operation_type=r.operation_type.value,
                    source_path=r.source_path,
                    target_path=r.target_path,
                    message=r.message,
                    audit_entry=r.audit_entry.to_dict() if r.audit_entry else None,
                )
                for r in results
            ],
        )

    # -------------------------------------------------------------------------
    # Audit History Endpoints
    # -------------------------------------------------------------------------

    @app.get("/well/audit-history", response_model=AuditHistoryResponse, tags=["Audit"])
    async def get_audit_history(
        limit: int = Query(100, description="Maximum entries to return"),
    ) -> AuditHistoryResponse:
        """Get audit trail history."""
        # Load history if not already loaded
        well.load_audit_history()
        history = well.get_audit_history(limit=limit)

        return AuditHistoryResponse(
            total=len(history),
            entries=[e.to_dict() for e in history],
        )

    return app


# Create default app instance
app = create_app()


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------


def main():
    """Run @WELL API server."""
    import uvicorn

    host = os.environ.get("WELL_HOST", "127.0.0.1")
    port = int(os.environ.get("WELL_PORT", "8042"))
    repo_root = os.environ.get("WELL_REPO_ROOT")

    print(f"Starting @WELL Universal API Server...")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Repo: {repo_root or 'current directory'}")
    print(f"  Docs: http://{host}:{port}/docs")
    print()
    print("DITEMPA BUKAN DIBERI - Forged, not given")

    # Create app with custom repo root if specified
    if repo_root:
        global app
        app = create_app(repo_root)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
