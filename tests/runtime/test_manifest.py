"""Tests for the build-vs-runtime manifest comparison (Epoch 1 / Item 5)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch


# ── Build manifest ────────────────────────────────────────────────────────


def test_generate_build_manifest_reads_canonical_eight_tools():
    """The build manifest reads the canonical 8 tools from tool_registry.json."""
    from arifosmcp.runtime.manifest import generate_build_manifest

    manifest = generate_build_manifest(Path("/root/arifOS"))
    assert "arif_init" in manifest.tool_names
    assert "arif_seal" in manifest.tool_names
    assert len(manifest.tool_names) >= 7  # canonical 7 + maybe more


def test_generate_build_manifest_source_commit_is_present():
    from arifosmcp.runtime.manifest import generate_build_manifest

    manifest = generate_build_manifest(Path("/root/arifOS"))
    assert isinstance(manifest.source_commit, str)
    assert manifest.source_commit != ""


def test_generate_build_manifest_hash_is_deterministic_for_same_source():
    """Same source -> same hash (modulo timestamp)."""
    from arifosmcp.runtime.manifest import generate_build_manifest

    m1 = generate_build_manifest(Path("/root/arifOS"))
    # Same logical content, different timestamp -> different hash overall,
    # but the build_hash is content-only (timestamp excluded).
    m2 = generate_build_manifest(Path("/root/arifOS"))
    assert m1.build_hash == m2.build_hash


def test_generate_build_manifest_serializable_to_dict():
    from arifosmcp.runtime.manifest import generate_build_manifest

    m = generate_build_manifest(Path("/root/arifOS"))
    as_dict = m.to_dict()
    assert "source_commit" in as_dict
    assert "build_hash" in as_dict
    assert "tool_names" in as_dict
    assert "resource_uris" in as_dict
    assert "prompt_names" in as_dict
    assert "schemas_hash" in as_dict


# ── Runtime manifest (with mocked kernel) ────────────────────────────────


def test_gather_runtime_manifest_returns_none_when_kernel_unreachable():
    from arifosmcp.runtime.manifest import gather_runtime_manifest

    with patch(
        "arifosmcp.runtime.manifest._kernel_reachable",
        return_value=False,
    ):
        result = gather_runtime_manifest()
    assert result is None


def test_gather_runtime_manifest_collects_from_mcp_lists():
    """Runtime manifest is built from real MCP list operations, not registries."""
    from arifosmcp.runtime.manifest import gather_runtime_manifest

    def _mcp(method: str, params: dict[str, Any] | None = None, timeout: float = 5.0) -> dict[str, Any]:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "protocolVersion": "2025-11-25",
                    "serverInfo": {"name": "arifOS", "version": "kanon-2026.07.17+85f165d"},
                },
            }
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": 1,
                    "result": {"tools": [{"name": "arif_init"}, {"name": "arif_seal"}]}}
        if method == "resources/list":
            return {"jsonrpc": "2.0", "id": 1,
                    "result": {"resources": [{"uri": "arifos://session/test"}]}}
        if method == "resources/templates/list":
            return {"jsonrpc": "2.0", "id": 1,
                    "result": {"resourceTemplates": []}}
        if method == "prompts/list":
            return {"jsonrpc": "2.0", "id": 1,
                    "result": {"prompts": [{"name": "🌱 BOOT"}]}}
        return {"jsonrpc": "2.0", "id": 1, "result": {}}

    with patch(
        "arifosmcp.runtime.manifest._kernel_reachable",
        return_value=True,
    ), patch(
        "arifosmcp.runtime.manifest._mcp_post",
        side_effect=_mcp,
    ):
        runtime = gather_runtime_manifest()

    assert runtime is not None
    assert "arif_init" in runtime.tool_names
    assert "arif_seal" in runtime.tool_names
    assert "arifos://session/test" in runtime.resource_uris
    assert "🌱 BOOT" in runtime.prompt_names
    assert runtime.source_commit == "85f165d"


# ── Comparison ────────────────────────────────────────────────────────────


def test_compare_aligned_when_build_and_runtime_match():
    from arifosmcp.runtime.manifest import (
        ALIGNED,
        BuildManifest,
        RuntimeManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="abc1234",
        build_hash="h",
        tool_names=("arif_init", "arif_seal"),
        resource_uris=("arifos://session/x",),
        resource_templates=(),
        prompt_names=("🌱 BOOT",),
        schemas_hash="s",
        constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    runtime = RuntimeManifest(
        tool_names=("arif_init", "arif_seal"),
        resource_uris=("arifos://session/x",),
        resource_templates=(),
        prompt_names=("🌱 BOOT",),
        source_commit="abc1234",
        kernel_url="http://127.0.0.1:8088",
        gathered_at="2026-07-17T00:00:01Z",
    )
    report = compare_manifests(build, runtime)
    assert report.state == ALIGNED
    assert report.drift_fields == {}


def test_compare_drift_when_tool_names_differ():
    from arifosmcp.runtime.manifest import (
        DRIFT,
        BuildManifest,
        RuntimeManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="x", build_hash="h",
        tool_names=("arif_init", "arif_seal", "arif_obsolete"),
        resource_uris=(), resource_templates=(),
        prompt_names=(), schemas_hash="s", constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    runtime = RuntimeManifest(
        tool_names=("arif_init", "arif_seal"),
        resource_uris=(), resource_templates=(),
        prompt_names=(),
        source_commit="x",
        kernel_url="http://127.0.0.1:8088",
        gathered_at="2026-07-17T00:00:01Z",
    )
    report = compare_manifests(build, runtime)
    assert report.state == DRIFT
    assert "tool_names" in report.drift_fields
    build_only, runtime_only = report.drift_fields["tool_names"]
    assert "arif_obsolete" in build_only
    assert runtime_only == []


def test_compare_drift_when_runtime_has_extra_tool():
    """Drift fires when runtime exposes a tool not declared in build manifest."""
    from arifosmcp.runtime.manifest import (
        DRIFT,
        BuildManifest,
        RuntimeManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="x", build_hash="h",
        tool_names=("arif_init",),
        resource_uris=(), resource_templates=(), prompt_names=(),
        schemas_hash="s", constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    runtime = RuntimeManifest(
        tool_names=("arif_init", "arif_ghost"),
        resource_uris=(), resource_templates=(), prompt_names=(),
        source_commit="x",
        kernel_url="http://127.0.0.1:8088",
        gathered_at="2026-07-17T00:00:01Z",
    )
    report = compare_manifests(build, runtime)
    assert report.state == DRIFT
    build_only, runtime_only = report.drift_fields["tool_names"]
    assert build_only == []
    assert "arif_ghost" in runtime_only


def test_compare_unknown_when_runtime_unreachable():
    from arifosmcp.runtime.manifest import (
        UNKNOWN,
        BuildManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="x", build_hash="h",
        tool_names=(), resource_uris=(), resource_templates=(), prompt_names=(),
        schemas_hash="s", constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    report = compare_manifests(build, None)
    assert report.state == UNKNOWN
    assert report.runtime_manifest is None


def test_compare_drift_on_source_commit_mismatch():
    from arifosmcp.runtime.manifest import (
        DRIFT,
        BuildManifest,
        RuntimeManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="abc1234", build_hash="h",
        tool_names=(), resource_uris=(), resource_templates=(), prompt_names=(),
        schemas_hash="s", constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    runtime = RuntimeManifest(
        tool_names=(), resource_uris=(), resource_templates=(), prompt_names=(),
        source_commit="def5678",
        kernel_url="http://127.0.0.1:8088",
        gathered_at="2026-07-17T00:00:01Z",
    )
    report = compare_manifests(build, runtime)
    assert report.state == DRIFT
    assert "source_commit" in report.drift_fields


# ── DriftReport shape ─────────────────────────────────────────────────────


def test_drift_report_serializable_to_dict():
    from arifosmcp.runtime.manifest import (
        BuildManifest,
        RuntimeManifest,
        compare_manifests,
    )

    build = BuildManifest(
        source_commit="x", build_hash="h",
        tool_names=(), resource_uris=(), resource_templates=(), prompt_names=(),
        schemas_hash="s", constitution_hash="c",
        generated_at="2026-07-17T00:00:00Z",
    )
    runtime = RuntimeManifest(
        tool_names=(), resource_uris=(), resource_templates=(), prompt_names=(),
        source_commit="x",
        kernel_url="http://127.0.0.1:8088",
        gathered_at="2026-07-17T00:00:01Z",
    )
    report = compare_manifests(build, runtime)
    as_dict = report.to_dict()
    assert as_dict["state"] in {"ALIGNED", "DRIFT", "UNKNOWN"}
    assert "build" in as_dict
    assert "runtime" in as_dict


def test_three_state_taxonomy_is_closed():
    from arifosmcp.runtime.manifest import (
        ALIGNED,
        CANONICAL_STATES,
        DRIFT,
        UNKNOWN,
    )

    assert CANONICAL_STATES == frozenset({ALIGNED, DRIFT, UNKNOWN})
    assert len(CANONICAL_STATES) == 3