"""
SLSA v1.0 Provenance — Build provenance generation.

https://slsa.dev/spec/v1.0/provenance
TRINITY-33: F8+K4 SUPPLY_CHAIN_INTEGRITY

Generates SLSA provenance attestations for CI builds.
Integrates with Sigstore for signing (future).
"""

from __future__ import annotations

import json
import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Optional


def generate_provenance(
    builder_id: str,
    build_type: str,
    materials: list[dict],
    invocation: Optional[dict] = None,
    build_config: Optional[dict] = None,
    metadata: Optional[dict] = None,
) -> dict:
    """
    Generate SLSA v1.0 provenance predicate.

    Args:
        builder_id: URI identifying the builder (e.g., "https://github.com/ariffazil/arifOS/.github/workflows/01-unified-ci.yml@refs/heads/main")
        build_type: Type of build (e.g., "https://slsa.dev/provenance/v1")
        materials: List of input artifacts with URIs and digests
        invocation: Parameters, environment, entrypoint
        build_config: Build configuration
        metadata: Build metadata (reproducible, completeness)

    Returns:
        SLSA v1.0 provenance envelope
    """
    predicate = {
        "buildDefinition": {
            "buildType": build_type,
            "resolvedDependencies": materials,
        },
        "runDetails": {
            "builder": {"id": builder_id},
            "buildMetadata": metadata or {},
        },
    }
    if invocation:
        predicate["runDetails"]["invocation"] = invocation
    if build_config:
        predicate["buildDefinition"]["externalParameters"] = build_config

    return {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": predicate,
    }


def material_digest(uri: str, content: bytes) -> str:
    """SHA-256 digest for a build material."""
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def ci_provenance(
    repo: str,
    workflow: str,
    ref: str,
    sha: str,
    materials: Optional[list[dict]] = None,
) -> dict:
    """
    Generate SLSA provenance for a CI build.

    Args:
        repo: Repository name (e.g., "ariffazil/arifOS")
        workflow: Workflow file path (e.g., ".github/workflows/01-unified-ci.yml")
        ref: Git ref (e.g., "refs/heads/main")
        sha: Commit SHA
        materials: Optional input artifacts with digests
    """
    builder_id = f"https://github.com/{repo}/{workflow}@{ref}"
    return generate_provenance(
        builder_id=builder_id,
        build_type="https://slsa.dev/provenance/v1",
        materials=materials or [],
        invocation={
            "configSource": {
                "uri": f"git+https://github.com/{repo}",
                "digest": {ref: sha},
                "entryPoint": workflow,
            },
        },
        metadata={
            "buildInvocationId": f"{repo}-{sha[:7]}",
            "buildStartedOn": datetime.now(timezone.utc).isoformat(),
            "buildFinishedOn": datetime.now(timezone.utc).isoformat(),
            "completeness": {"parameters": True, "environment": False, "materials": bool(materials)},
            "reproducible": os.environ.get("CI", "false") == "true",
        },
    )


def provenance_to_json(provenance: dict) -> str:
    return json.dumps(provenance, indent=2, ensure_ascii=False)
