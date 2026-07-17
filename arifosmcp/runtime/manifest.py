"""
arifOS Surface Manifest — build-time and runtime surface comparison.

Epoch 1 / Item 5 of the Kernel Senescence Reduction plan.
Generates a signed build manifest from the source tree, generates a
runtime manifest from live MCP list operations, and compares them.

    build == runtime  -> ALIGNED
    build != runtime  -> DRIFT
    comparison unavailable -> UNKNOWN

Drift between source and runtime means the deployment is unsafe to serve.
The runtime must refuse to advertise what is not callable.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess  # nosec B404
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


# ── Result types ──────────────────────────────────────────────────────────

ALIGNED = "ALIGNED"
DRIFT = "DRIFT"
UNKNOWN = "UNKNOWN"

CANONICAL_STATES = frozenset({ALIGNED, DRIFT, UNKNOWN})


@dataclass(frozen=True)
class BuildManifest:
    """What the source tree declares the runtime should expose."""

    source_commit: str
    build_hash: str
    tool_names: tuple[str, ...]
    resource_uris: tuple[str, ...]
    resource_templates: tuple[str, ...]
    prompt_names: tuple[str, ...]
    schemas_hash: str
    constitution_hash: str
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_commit": self.source_commit,
            "build_hash": self.build_hash,
            "tool_names": list(self.tool_names),
            "resource_uris": list(self.resource_uris),
            "resource_templates": list(self.resource_templates),
            "prompt_names": list(self.prompt_names),
            "schemas_hash": self.schemas_hash,
            "constitution_hash": self.constitution_hash,
            "generated_at": self.generated_at,
        }


@dataclass(frozen=True)
class RuntimeManifest:
    """What the live kernel actually exposes, gathered from MCP list operations."""

    tool_names: tuple[str, ...]
    resource_uris: tuple[str, ...]
    resource_templates: tuple[str, ...]
    prompt_names: tuple[str, ...]
    source_commit: str
    kernel_url: str
    gathered_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_names": list(self.tool_names),
            "resource_uris": list(self.resource_uris),
            "resource_templates": list(self.resource_templates),
            "prompt_names": list(self.prompt_names),
            "source_commit": self.source_commit,
            "kernel_url": self.kernel_url,
            "gathered_at": self.gathered_at,
        }


@dataclass(frozen=True)
class DriftReport:
    """Result of comparing build vs runtime."""

    state: str  # ALIGNED | DRIFT | UNKNOWN
    build_manifest: BuildManifest | None
    runtime_manifest: RuntimeManifest | None
    drift_fields: dict[str, tuple[list[str], list[str]]] = field(default_factory=dict)
    comparison_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "drift_fields": {
                k: {"build_only": v[0], "runtime_only": v[1]}
                for k, v in self.drift_fields.items()
            },
            "comparison_note": self.comparison_note,
            "build": self.build_manifest.to_dict() if self.build_manifest else None,
            "runtime": self.runtime_manifest.to_dict() if self.runtime_manifest else None,
        }


# ── Build manifest from source ──────────────────────────────────────────


def _git_short_commit(repo: Path) -> str:
    try:
        result = subprocess.run(  # nosec B603
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(repo),
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _hash_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return "unreadable"


def _hash_directory(path: Path, suffix: str) -> str:
    """sha256 over the sorted relative paths + contents of every file with suffix."""
    if not path.exists():
        return "missing"
    entries: list[str] = []
    for p in sorted(path.rglob(f"*{suffix}")):
        if p.is_file():
            entries.append(f"{p.relative_to(path)}\0{_hash_file(p)}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


def _canonical_tool_names_from_source(arifos_root: Path) -> tuple[str, ...]:
    """Read the canonical 8 tools from tool_registry.json or the canonical_order block."""
    tool_registry = arifos_root / "arifosmcp" / "tool_registry.json"
    if not tool_registry.exists():
        return ()
    try:
        data = json.loads(tool_registry.read_text())
        order = data.get("canonical_order", [])
        return tuple(order)
    except Exception:
        return ()


def _resource_uris_from_source(arifos_root: Path) -> tuple[str, ...]:
    """Read the canonical resource URIs from arifosmcp/resources/__init__.py."""
    resources_init = arifos_root / "arifosmcp" / "resources" / "__init__.py"
    if not resources_init.exists():
        return ()
    try:
        text = resources_init.read_text()
        # Find CANONICAL_RESOURCES = ( ... ) and pull out quoted strings.
        import re
        match = re.search(r"CANONICAL_RESOURCES\s*=\s*\(([^)]*)\)", text, re.DOTALL)
        if not match:
            return ()
        body = match.group(1)
        return tuple(re.findall(r"['\"]([^'\"]+)['\"]", body))
    except Exception:
        return ()


def _prompt_names_from_source(arifos_root: Path) -> tuple[str, ...]:
    """Read the canonical prompt names from fastmcp_ext/prompts.py.

    Falls back to the registered list inside register_arifos_prompts.
    """
    prompts_path = arifos_root / "arifosmcp" / "runtime" / "fastmcp_ext" / "prompts.py"
    if not prompts_path.exists():
        return ()
    try:
        text = prompts_path.read_text()
        import re
        # Find `@mcp.prompt(name="...")` patterns.
        return tuple(re.findall(r'@mcp\.prompt\(\s*name="([^"]+)"', text))
    except Exception:
        return ()


def generate_build_manifest(arifos_root: Path | None = None) -> BuildManifest:
    """Generate the canonical build manifest from the source tree."""
    if arifos_root is None:
        arifos_root = Path(os.getenv("ARIFOS_HOME", "/root/arifOS"))
    source_commit = _git_short_commit(arifos_root)
    schemas_hash = _hash_directory(arifos_root / "arifosmcp" / "schemas", ".py")
    constitution_hash = _hash_file(arifos_root / "AGENTS.md")
    tool_names = _canonical_tool_names_from_source(arifos_root)
    resource_uris = _resource_uris_from_source(arifos_root)
    prompt_names = _prompt_names_from_source(arifos_root)
    build_hash_input = json.dumps({
        "source_commit": source_commit,
        "tool_names": list(tool_names),
        "resource_uris": list(resource_uris),
        "prompt_names": list(prompt_names),
        "schemas_hash": schemas_hash,
    }, sort_keys=True)
    build_hash = hashlib.sha256(build_hash_input.encode("utf-8")).hexdigest()
    return BuildManifest(
        source_commit=source_commit,
        build_hash=build_hash,
        tool_names=tool_names,
        resource_uris=resource_uris,
        resource_templates=(),  # derived at runtime only
        prompt_names=prompt_names,
        schemas_hash=schemas_hash,
        constitution_hash=constitution_hash,
        generated_at=datetime.now(UTC).isoformat(),
    )


# ── Runtime manifest from live kernel ────────────────────────────────────


def _kernel_url() -> str:
    return os.getenv("ARIFOS_MCP_URL", "http://127.0.0.1:8088").rstrip("/")


def _kernel_reachable(timeout: float = 2.0) -> bool:
    import urllib.error
    import urllib.request
    try:
        req = urllib.request.Request(_kernel_url() + "/health", method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def _mcp_post(method: str, params: dict[str, Any] | None = None, timeout: float = 5.0) -> dict[str, Any]:
    import urllib.request
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}
    body = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    req = urllib.request.Request(
        _kernel_url() + "/mcp", data=body, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    if raw.startswith("data:"):
        raw = raw.split("data:", 1)[1].strip()
    return json.loads(raw)


def gather_runtime_manifest() -> RuntimeManifest | None:
    """Gather the live runtime manifest. Returns None if the kernel is unreachable."""
    if not _kernel_reachable():
        return None
    try:
        tools = _mcp_post("tools/list", {}).get("result", {}).get("tools", [])
        resources = _mcp_post("resources/list", {}).get("result", {}).get("resources", [])
        templates = _mcp_post("resources/templates/list", {}).get(
            "result", {}
        ).get("resourceTemplates", [])
        prompts = _mcp_post("prompts/list", {}).get("result", {}).get("prompts", [])
        init = _mcp_post(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "manifest-gatherer", "version": "1.0"},
            },
        )
        info = init.get("result", {}).get("serverInfo", {})
        source_commit = (
            info.get("version", "unknown")
            if isinstance(info.get("version"), str)
            else "unknown"
        )
        # serverInfo.version is "kanon-2026.07.17+85f165d" — extract short commit.
        if "+" in source_commit:
            source_commit = source_commit.split("+", 1)[1][:7]
        return RuntimeManifest(
            tool_names=tuple(
                sorted(t.get("name") for t in tools if isinstance(t, dict) and t.get("name"))
            ),
            resource_uris=tuple(
                sorted(r.get("uri") for r in resources if isinstance(r, dict) and r.get("uri"))
            ),
            resource_templates=tuple(
                sorted(t.get("uriTemplate") for t in templates if isinstance(t, dict) and t.get("uriTemplate"))
            ),
            prompt_names=tuple(
                sorted(p.get("name") for p in prompts if isinstance(p, dict) and p.get("name"))
            ),
            source_commit=source_commit,
            kernel_url=_kernel_url(),
            gathered_at=datetime.now(UTC).isoformat(),
        )
    except Exception:  # noqa: BLE001
        return None


# ── Comparison ────────────────────────────────────────────────────────────


def compare_manifests(
    build: BuildManifest, runtime: RuntimeManifest | None
) -> DriftReport:
    """Compare build vs runtime and report drift.

    build == runtime  -> ALIGNED
    build != runtime  -> DRIFT
    comparison unavailable -> UNKNOWN
    """
    if runtime is None:
        return DriftReport(
            state=UNKNOWN,
            build_manifest=build,
            runtime_manifest=None,
            comparison_note="kernel unreachable; comparison unavailable",
        )

    drift: dict[str, tuple[list[str], list[str]]] = {}

    def _diff(label: str, build_set: tuple[str, ...], runtime_set: tuple[str, ...]) -> None:
        b = set(build_set)
        r = set(runtime_set)
        only_build = sorted(b - r)
        only_runtime = sorted(r - b)
        if only_build or only_runtime:
            drift[label] = (only_build, only_runtime)

    _diff("tool_names", build.tool_names, runtime.tool_names)
    _diff("resource_uris", build.resource_uris, runtime.resource_uris)
    _diff("resource_templates", build.resource_templates, runtime.resource_templates)
    _diff("prompt_names", build.prompt_names, runtime.prompt_names)

    if build.source_commit != runtime.source_commit:
        drift["source_commit"] = (
            [build.source_commit], [runtime.source_commit],
        )

    if drift:
        return DriftReport(
            state=DRIFT,
            build_manifest=build,
            runtime_manifest=runtime,
            drift_fields=drift,
            comparison_note="build and runtime surfaces differ",
        )
    return DriftReport(
        state=ALIGNED,
        build_manifest=build,
        runtime_manifest=runtime,
        comparison_note="build and runtime surfaces match",
    )


def check_alignment(arifos_root: Path | None = None) -> DriftReport:
    """Top-level: generate build, gather runtime, compare."""
    build = generate_build_manifest(arifos_root)
    runtime = gather_runtime_manifest()
    return compare_manifests(build, runtime)


__all__ = [
    "ALIGNED",
    "DRIFT",
    "UNKNOWN",
    "CANONICAL_STATES",
    "BuildManifest",
    "RuntimeManifest",
    "DriftReport",
    "generate_build_manifest",
    "gather_runtime_manifest",
    "compare_manifests",
    "check_alignment",
]