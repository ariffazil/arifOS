"""F2 TRUTH — Health endpoint must not lie about deployment state.

FORGE audit 2026-06-27 found:
    /root/arifOS/arifosmcp/runtime/rest_routes/rest_routes.py:2560
    was HARDCODED to ``"deployment_source": "ghcr"`` and the image field was
    always set to ``ghcr.io/ariffazil/arifos:<commit>`` — regardless of whether
    the process was actually running in a container.

The federation root lied about its own runtime state. This test pins the
correct behaviour: deployment_source MUST be detected at runtime, and when
running natively, image MUST be ``None``.

These tests do not mock the runtime — they assert against the *actual* VPS
af-forge environment, which is native. They will fail loudly if anyone
re-introduces hardcoded "ghcr" labels.

F2 TRUTH: arifOS is the law engine. If its health endpoint lies, every
organ's provenance chain inherits the lie. This is regression-grade.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────


def _load_root_server_module():
    """Load /root/arifOS/server.py as a standalone module.

    Mirrors tests/test_runtime_health.py pattern.
    """
    server_path = Path(__file__).resolve().parents[1] / "server.py"
    spec = importlib.util.spec_from_file_location("root_server_truth", server_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ─────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────


def test_detect_deployment_mode_returns_known_value() -> None:
    """_detect_deployment_mode() must return exactly 'native' or 'container'."""
    from arifosmcp.runtime.build import _detect_deployment_mode

    mode = _detect_deployment_mode()
    assert mode in ("native", "container"), (
        f"deployment mode must be 'native' or 'container', got: {mode!r}"
    )


def test_get_deployment_mode_is_cached_and_stable() -> None:
    """get_deployment_mode() must match the detector and be idempotent."""
    from arifosmcp.runtime.build import _detect_deployment_mode, get_deployment_mode

    a = get_deployment_mode()
    b = get_deployment_mode()
    detected = _detect_deployment_mode()
    assert a == b == detected, f"deployment mode cache drift: a={a} b={b} detected={detected}"


def test_native_vps_has_no_dockerenv() -> None:
    """Sanity: on VPS af-forge (native), /.dockerenv must NOT exist.

    If this fails, either we're now running in a container (audit needed)
    or someone touched the root filesystem (security incident).
    """
    assert not os.path.exists("/.dockerenv"), (
        "/.dockerenv exists — runtime is in a Docker container, "
        "deployment_source should be 'container' (audit needed if unexpected)"
    )


def test_native_vps_cgroup_is_user_slice() -> None:
    """Sanity: /proc/1/cgroup must NOT mention docker/kubepods/lxc/containerd.

    On VPS af-forge (native), PID 1 cgroup is a user.slice session scope.
    Any other pattern means the runtime is in a container/orchestrator.
    """
    cgroup_path = Path("/proc/1/cgroup")
    if not cgroup_path.exists():
        pytest.skip("/proc/1/cgroup not readable on this host")
    cgroup = cgroup_path.read_text(errors="replace")
    for token in ("docker-", "kubepods", "/lxc/", "containerd-"):
        assert token not in cgroup, (
            f"cgroup contains {token!r} — runtime is in a container/orchestrator. "
            f"cgroup content:\n{cgroup}"
        )


def test_health_endpoint_deployment_source_is_detected() -> None:
    """F2 TRUTH: /health payload's deployment_source MUST NOT be hardcoded.

    Pre-fix bug: rest_routes.py:2560 hardcoded ``"deployment_source": "ghcr"``.
    Post-fix: must equal ``get_deployment_mode()``.
    """
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    response = client.get("/health")
    assert response.status_code == 200, f"/health returned {response.status_code}"
    payload = response.json()

    assert "deployment_source" in payload, "/health payload missing deployment_source"
    assert payload["deployment_source"] in ("native", "container"), (
        f"deployment_source must be detected, not hardcoded. Got: {payload['deployment_source']!r}"
    )


def test_health_endpoint_image_null_when_native() -> None:
    """F2 TRUTH: when running natively, ``image`` MUST be ``None``.

    Pre-fix bug: image was always ``ghcr.io/ariffazil/arifos:<commit>``,
    even when no container is running. Federation consumers would record
    a phantom container image in VAULT999 provenance.
    """
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    payload = client.get("/health").json()
    if payload["deployment_source"] == "native":
        assert payload.get("image") is None, (
            f"native deployment must NOT advertise container image. Got: {payload.get('image')!r}"
        )


def test_health_endpoint_runtime_drift_false_when_native() -> None:
    """F2 TRUTH: native deployment cannot have 'container drift'.

    Pre-fix bug: ``runtime_drift=true`` fired whenever build_commit marker
    diverged from live_commit, but the 'rebuild container' advice was wrong
    because no container was running. Native deployments have no drift in
    the container sense; marker-vs-git divergence is a separate signal.
    """
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    payload = client.get("/health").json()
    if payload["deployment_source"] == "native":
        assert payload.get("runtime_drift") is False, (
            f"native deployment must not report container-drift. "
            f"Got runtime_drift={payload.get('runtime_drift')!r}"
        )


def test_health_endpoint_exposes_deployment_marker_metadata() -> None:
    """New fields added in fix — must be present and truthful."""
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    payload = client.get("/health").json()
    assert "deployment_marker" in payload, (
        "/health must expose deployment_marker path for ops transparency"
    )
    assert "deployment_marker_exists" in payload, (
        "/health must expose deployment_marker_exists boolean"
    )
    assert "runtime_path" in payload, (
        "/health must expose runtime_path (where arifosmcp is imported from)"
    )
    # runtime_path must be a real directory
    assert Path(payload["runtime_path"]).is_dir(), (
        f"runtime_path {payload['runtime_path']!r} is not a directory"
    )


def test_runtime_fingerprint_deployment_source_matches() -> None:
    """/runtime_fingerprint must agree with /health on deployment_source.

    Both endpoints are reachable to federation organs. They MUST not disagree
    about basic runtime identity.
    """
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)

    health = client.get("/health").json()
    fingerprint = client.get("/runtime_fingerprint").json()

    assert "deployment_source" in fingerprint, "/runtime_fingerprint must include deployment_source"
    assert fingerprint["deployment_source"] == health["deployment_source"], (
        f"/runtime_fingerprint.deployment_source={fingerprint['deployment_source']!r} "
        f"!= /health.deployment_source={health['deployment_source']!r}"
    )
    # Image field consistency
    assert fingerprint.get("image") == health.get("image"), (
        f"/runtime_fingerprint.image={fingerprint.get('image')!r} "
        f"!= /health.image={health.get('image')!r}"
    )


# ─────────────────────────────────────────────────────────────────────────
# Guard: if test environment is misconfigured, fail loud
# ─────────────────────────────────────────────────────────────────────────


def test_runtime_is_not_a_container_at_test_time() -> None:
    """This test FILE assumes native runtime (VPS af-forge).

    If /health now reports 'container', either:
      (a) we migrated to container deployment (audit needed), or
      (b) the new detection logic has a bug.

    Mark xfail so CI surfaces the change rather than silently passing.
    """
    server_module = _load_root_server_module()
    client = TestClient(server_module.app)
    payload = client.get("/health").json()
    if payload["deployment_source"] != "native":
        pytest.xfail(
            f"arifOS now reports deployment_source={payload['deployment_source']!r}. "
            "This test assumed native. Update the test or audit the migration."
        )
