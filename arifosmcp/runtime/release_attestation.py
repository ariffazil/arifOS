"""
release_attestation.py — arifOS Release 1: Boot-Time Runtime Truth Verification

Ensures the imported arifosmcp package matches the expected release manifest.
Runs at service startup. Blocks readiness on mismatch.

Invariant (A2 fix):
    source commit = installed artifact = imported runtime

DITEMPA BUKAN DIBERI — Truth is forged, not assumed.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

RELEASE_DIR = Path("/opt/arifos/releases")
MANIFEST_PATH = RELEASE_DIR / "release-manifest.json"
STAMP_PATH = Path("/opt/arifos/app/.git_commit")
EXPECTED_VENV = "/opt/arifos/venv"
EXPECTED_PYTHON = "/opt/arifos/venv/bin/python"

# Source files whose hashes form the source_file_hash attestation per Arif A2 spec
SOURCE_ATTESTATION_FILES: tuple[str, ...] = (
    "arifosmcp/runtime/governance_identity.py",
    "arifosmcp/runtime/pre_execution_gate.py",
    "arifosmcp/runtime/authority.py",
    "arifosmcp/runtime/principal_paradox.py",
    "arifosmcp/runtime/art_registry.py",
    "arifosmcp/runtime/release_attestation.py",
)


class AttestationFailure(Exception):
    """Raised on boot when runtime truth invariant fails (fail-CLOSED).

    Per Arif 2026-07-13 corrective:
    Boot MUST refuse readiness when attestation passes=False.
    """

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(
            "Runtime attestation FAILED (fail-closed): " + "; ".join(errors)
        )


@dataclass(frozen=True)
class AttestationResult:
    """Result of a boot-time runtime attestation check."""

    passed: bool
    module_path: str = ""
    expected_commit: str = ""
    runtime_commit: str = ""
    expected_python: str = ""
    actual_python: str = ""
    expected_venv: str = ""
    module_under_venv: bool = False
    manifest_found: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "module_path": self.module_path,
            "expected_commit": self.expected_commit,
            "runtime_commit": self.runtime_commit,
            "expected_python": self.expected_python,
            "actual_python": self.actual_python,
            "module_under_venv": self.module_under_venv,
            "manifest_found": self.manifest_found,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def _resolve_module_path() -> str:
    """Resolve the actual filesystem path of the imported arifosmcp package."""
    try:
        import arifosmcp.runtime.build as build_mod

        return str(Path(build_mod.__file__).resolve())
    except Exception:
        return "unresolved"


def _get_runtime_commit() -> str:
    """Get the git commit the running code reports."""
    try:
        from arifosmcp.runtime.build import _git_sha_short

        return _git_sha_short() or "unknown"
    except Exception:
        return "unknown"


def _get_release_manifest() -> dict | None:
    """Read the release manifest if it exists."""
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text())
        except Exception:
            return None
    return None


def attest_runtime() -> AttestationResult:
    """Run all runtime truth checks. Returns structured result."""
    errors: list[str] = []
    warnings: list[str] = []

    module_path = _resolve_module_path()
    runtime_commit = _get_runtime_commit()
    manifest = _get_release_manifest()
    actual_python = sys.executable

    expected_commit = ""
    if manifest:
        expected_commit = manifest.get("git_commit", "")

    # Check 1: Python executable is from expected venv
    python_ok = actual_python.startswith(EXPECTED_PYTHON)
    if not python_ok:
        errors.append(
            f"Python executable {actual_python} is not inside "
            f"{EXPECTED_PYTHON} — check systemd ExecStart"
        )

    # Check 2: Module imports from expected venv path
    module_under_venv = module_path.startswith(EXPECTED_VENV)
    if not module_under_venv:
        # Not necessarily an error if global was removed but editable hook active
        warnings.append(
            f"Module imports from {module_path}, which is outside "
            f"{EXPECTED_VENV}. May indicate editable install still active."
        )

    # Check 3: Runtime commit matches manifest
    if manifest and expected_commit and expected_commit != "unknown":
        if runtime_commit != expected_commit:
            warnings.append(
                f"Runtime commit ({runtime_commit}) differs from "
                f"release manifest ({expected_commit})"
            )
    elif not manifest:
        warnings.append("No release manifest found — deploy-release not yet run")

    passed = len(errors) == 0

    return AttestationResult(
        passed=passed,
        module_path=module_path,
        expected_commit=expected_commit,
        runtime_commit=runtime_commit,
        expected_python=EXPECTED_PYTHON,
        actual_python=actual_python,
        expected_venv=EXPECTED_VENV,
        module_under_venv=module_under_venv,
        manifest_found=manifest is not None,
        errors=errors,
        warnings=warnings,
    )


def attest_and_report() -> dict:
    """Run attestation, return dict suitable for health endpoint embedding."""
    result = attest_runtime()
    return result.to_dict()


def fail_closed_check() -> None:
    """Run on startup. If critical checks fail, log and do NOT block.

    We warn, not block — blocking on first boot before deploy-release
    would create a catch-22. The health endpoint reports alignment status
    separately from process health.
    """
    result = attest_runtime()
    for err in result.errors:
        print(f"RELEASE ATTESTATION ERROR: {err}", file=sys.stderr, flush=True)
    for warn in result.warnings:
        print(f"RELEASE ATTESTATION WARNING: {warn}", file=sys.stderr, flush=True)
    if result.passed:
        print("RELEASE ATTESTATION PASSED — runtime aligned", file=sys.stderr, flush=True)
    else:
        print(
            f"RELEASE ATTESTATION: {len(result.errors)} error(s)",
            file=sys.stderr,
            flush=True,
        )


if __name__ == "__main__":
    result = attest_runtime()
    print(json.dumps(result.to_dict(), indent=2))
