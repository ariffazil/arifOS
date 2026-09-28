"""
P0-5 — Deployment Attestation Key-Name Consistency Test.

Verifies that _compute_runtime_drift() return keys match what every
call site reads. Catches the key-name mismatch bug class that caused
kernel DEPLOYMENT_DRIFT for weeks (source_commit vs live_commit,
built_commit vs build_commit, deployed_commit vs live_commit).

Regressions caught:
  - New call sites using wrong key names
  - _compute_runtime_drift() changing its return schema
  - Silent None propagation when keys don't match
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes.rest_routes import _compute_runtime_drift  # noqa: E402

# ═══════════════════════════════════════════════════════════════
# Phase 1: Verify _compute_runtime_drift() return schema
# ═══════════════════════════════════════════════════════════════

CANONICAL_RETURN_KEYS = frozenset(
    {
        "runtime_drift",
        "runtime_matches_build",
        "build_commit",
        "live_commit",
        "git_dirty",
    }
)

# The ONLY keys callers should use (remap of canonical names)
# This is the contract: callers read live_commit/build_commit,
# not source_commit/built_commit/deployed_commit
SAFE_CALLER_KEYS = {
    "live_commit",
    "build_commit",
    "runtime_drift",
    "runtime_matches_build",
    "git_dirty",
}


def test_drift_function_returns_canonical_keys():
    """_compute_runtime_drift MUST return only canonical keys."""
    result = _compute_runtime_drift()
    actual_keys = set(result.keys())
    assert actual_keys == CANONICAL_RETURN_KEYS, (
        f"Return key mismatch.\n"
        f"Expected: {sorted(CANONICAL_RETURN_KEYS)}\n"
        f"Got:      {sorted(actual_keys)}\n"
        f"Extra:    {sorted(actual_keys - CANONICAL_RETURN_KEYS)}\n"
        f"Missing:  {sorted(CANONICAL_RETURN_KEYS - actual_keys)}"
    )


def test_drift_function_returns_string_commits():
    """build_commit and live_commit MUST be strings, not None."""
    result = _compute_runtime_drift()
    assert isinstance(result["build_commit"], str), (
        f"build_commit is {type(result['build_commit'])}"
    )
    assert isinstance(result["live_commit"], str), f"live_commit is {type(result['live_commit'])}"


def test_drift_function_returns_valid_commits():
    """build_commit and live_commit SHOULD resolve to real SHAs."""
    result = _compute_runtime_drift()
    build = result["build_commit"]
    live = result["live_commit"]
    # At minimum, must not be empty
    assert len(build) > 0, "build_commit is empty"
    assert len(live) > 0, "live_commit is empty"
    # If unknown, must explicitly say "unknown" (not "?" or "")
    assert build not in ("?", ""), f"build_commit is sentinel: {build!r}"
    assert live not in ("?", ""), f"live_commit is sentinel: {live!r}"
    # A healthy kernel should have matching commits
    if build != "unknown" and live != "unknown":
        assert build[:7] == live[:7], f"Commit mismatch: build={build[:12]} live={live[:12]}"


def test_drift_function_booleans_are_consistent():
    """runtime_drift and runtime_matches_build MUST be logical inverses
    when both commits are known."""
    result = _compute_runtime_drift()
    build = result["build_commit"]
    live = result["live_commit"]
    if build != "unknown" and live != "unknown":
        expected_match = build[:7] == live[:7]
        assert result["runtime_matches_build"] == expected_match, (
            f"Inconsistent: matches_build={result['runtime_matches_build']} "
            f"but build={build[:10]} vs live={live[:10]}"
        )


# ═══════════════════════════════════════════════════════════════
# Phase 2: Verify NO caller uses wrong keys on the drift dict
# ═══════════════════════════════════════════════════════════════

DRIFT_CALL_SITES = [
    ("runtime/rest_routes/health_routes.py", "health_routes"),
    ("runtime/rest_routes/rest_routes.py", "rest_routes"),
]


def _extract_drift_key_reads(file_path: str) -> list[tuple[int, str]]:
    """AST-walk a file and find all drift.get() or drift[] calls."""
    root_rel = Path(__file__).resolve().parents[2] / "arifosmcp" / file_path
    if not root_rel.exists():
        return []
    tree = ast.parse(root_rel.read_text())

    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        # Match: drift.get("KEY") or drift["KEY"]
        if isinstance(node, ast.Call):
            # drift.get(...)
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in ("drift", "_drift")
            ):
                if node.args and isinstance(node.args[0], ast.Constant):
                    key = node.args[0].value
                    if key not in SAFE_CALLER_KEYS:
                        violations.append((node.lineno, key))
        elif isinstance(node, ast.Subscript):
            # drift["KEY"]
            if (
                isinstance(node.value, ast.Name)
                and node.value.id in ("drift", "_drift")
                and isinstance(node.slice, ast.Constant)
            ):
                key = node.slice.value
                if key not in SAFE_CALLER_KEYS:
                    violations.append((node.lineno, key))
    return violations


@pytest.mark.parametrize("file_path,label", DRIFT_CALL_SITES)
def test_no_caller_uses_wrong_key_on_drift_dict(file_path: str, label: str):
    """Every drift.get()/drift[] call MUST use only canonical keys.

    The bug pattern: _compute_runtime_drift() returns 'live_commit'
    but callers read 'source_commit' → None → deployment_drift=True.
    """
    violations = _extract_drift_key_reads(file_path)
    if violations:
        detail = "\n".join(
            f"  {file_path}:{lineno} reads drift[{key!r}] — NOT a canonical key"
            for lineno, key in sorted(violations)
        )
        pytest.fail(
            f"{len(violations)} key-name violation(s) in {label}:\n{detail}\n\n"
            f"Canonical keys: {sorted(SAFE_CALLER_KEYS)}\n"
            f"Fix: replace with the matching canonical key "
            f"(source_commit→live_commit, built_commit→build_commit, "
            f"deployed_commit→live_commit)"
        )


def test_health_routes_deployment_attestation_self_consistent():
    """The /health endpoint MUST report deployment_drift=aligned
    when all three commits match."""
    import urllib.request
    import json

    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8088/health", timeout=5)
        data = json.loads(resp.read().decode())
    except Exception:
        pytest.skip("Kernel not reachable")

    lh = data.get("layer_health", {}).get("runtime", {})
    src = lh.get("source_commit")
    built = lh.get("built_commit")

    # If the kernel resolves commits, they must not be None when runtime matches build
    if lh.get("runtime_matches_build") and data.get("status") == "healthy":
        assert src is not None, (
            f"source_commit is None but runtime_matches_build=True. "
            f"Bug: caller reads wrong key from _compute_runtime_drift()"
        )
        assert built is not None, (
            f"built_commit is None but runtime_matches_build=True. "
            f"Bug: caller reads wrong key from _compute_runtime_drift()"
        )
        assert str(src)[:7] == str(built)[:7], (
            f"Commit mismatch in health: source={src} vs built={built}"
        )


# ═══════════════════════════════════════════════════════════════
# Phase 3: smoke test — run from venv python
# ═══════════════════════════════════════════════════════════════


def test_smoke_kernel_healthy():
    """Quick smoke: kernel health endpoint returns without error."""
    import urllib.request
    import json

    try:
        resp = urllib.request.urlopen("http://127.0.0.1:8088/health", timeout=5)
        data = json.loads(resp.read().decode())
    except Exception:
        pytest.skip("Kernel not reachable")

    assert "status" in data
    # If the kernel is healthy, it must NOT have deployment_attestation drift
    if data.get("status") == "healthy":
        assert data.get("deployment_drift_status") == "aligned", (
            f"Kernel reports healthy but deployment_drift_status="
            f"{data.get('deployment_drift_status')}"
        )
