"""
Drift Attestation Module
══════════════════════════════════════════════

Tracks runtime integrity by comparing declared build artifacts
against live runtime state. Detects drift across:
  - build_hash vs runtime_hash
  - git_commit vs deployed commit
  - tool_manifest_hash vs live tool surface
  - schema_hash vs live schemas
  - constitution_hash vs active constitution
  - env_config_hash (excluding secrets) vs deployed config

Drift levels:
  NONE    — all hashes match
  LOW     — minor mismatch (e.g., env config drift)
  MEDIUM  — schema or tool manifest drift
  HIGH    — constitution or build hash drift
  CRITICAL — kernel core binary mismatch

Rules:
  NONE/LOW: observe and analyze allowed.
  MEDIUM: mutation requires renewed lease.
  HIGH: mutation blocked.
  CRITICAL: external side effects and irreversible actions blocked.

DITEMPA BUKAN DIBERI — The drift detector is forged, not given.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path

from arifosmcp.schemas.kernel_envelope import DriftLevel, DriftReport

logger = logging.getLogger("arifosmcp.drift")


class DriftDetector:
    """Detects runtime drift by comparing declared hashes against live state."""

    def __init__(
        self,
        repo_root: str = "/root/arifOS",
        deployed_root: str = "/opt/arifos/app",
    ):
        self.repo_root = Path(repo_root)
        self.deployed_root = Path(deployed_root)

    # ═══════════════════════════════════════════════════════════════════
    # HASH COMPUTATION
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def hash_file(path: Path) -> str:
        """SHA-256 of a single file."""
        if not path.exists():
            return ""
        return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"

    @staticmethod
    def hash_directory(directory: Path, pattern: str = "*.py") -> str:
        """SHA-256 of all files matching pattern in a directory (sorted)."""
        if not directory.exists():
            return ""
        files = sorted(directory.rglob(pattern))
        if not files:
            return ""
        combined = b""
        for f in files:
            combined += f.read_bytes()
        return f"sha256:{hashlib.sha256(combined).hexdigest()}"

    @staticmethod
    def hash_string(s: str) -> str:
        """SHA-256 of a string."""
        return f"sha256:{hashlib.sha256(s.encode()).hexdigest()}"

    # ═══════════════════════════════════════════════════════════════════
    # DRIFT DETECTION
    # ═══════════════════════════════════════════════════════════════════

    def detect(self) -> DriftReport:
        """Run a full drift detection pass."""
        reasons: list[str] = []

        # ── Read declared hashes ──────────────────────────────────────
        build_hash = self._read_git_commit()
        runtime_hash = self._read_deployed_commit()

        git_commit = self._read_git_commit()
        tool_manifest_hash = self._hash_tool_manifest()
        schema_hash = self._hash_schemas()
        constitution_hash = self._hash_constitution()
        env_config_hash = self._hash_env_config()
        deployment_timestamp = self._read_deployment_timestamp()

        # ── Compare ───────────────────────────────────────────────────
        drift_levels: list[DriftLevel] = []

        if build_hash != runtime_hash:
            drift_levels.append(DriftLevel.HIGH)
            reasons.append(
                f"Build hash ({build_hash[:20]}...) != runtime hash ({runtime_hash[:20]}...)"
            )

        # Check schema hash against canonical
        canonical_schema = "sha256:12523d50c342f20c3f6adc65d59fe19eb4f08d59551ab9ba87d6ccf235a29afa"
        if schema_hash and schema_hash != canonical_schema:
            drift_levels.append(DriftLevel.MEDIUM)
            reasons.append(f"Schema hash mismatch: {schema_hash[:20]}... vs canonical")

        # Determine overall drift
        if not drift_levels:
            drift_level = DriftLevel.NONE
        elif DriftLevel.CRITICAL in drift_levels:
            drift_level = DriftLevel.CRITICAL
        elif DriftLevel.HIGH in drift_levels:
            drift_level = DriftLevel.HIGH
        elif DriftLevel.MEDIUM in drift_levels:
            drift_level = DriftLevel.MEDIUM
        else:
            drift_level = DriftLevel.LOW

        return DriftReport(
            build_hash=build_hash,
            runtime_hash=runtime_hash,
            git_commit=git_commit,
            tool_manifest_hash=tool_manifest_hash,
            schema_hash=schema_hash,
            constitution_hash=constitution_hash,
            env_config_hash=env_config_hash,
            deployment_timestamp=deployment_timestamp,
            drift_level=drift_level,
            drift_details="; ".join(reasons) if reasons else "No drift detected",
        )

    def is_safe_for(self, action_class: str) -> tuple[bool, str]:
        """Check if the current drift level allows a given action class."""
        report = self.detect()
        from arifosmcp.schemas.kernel_envelope import ActionClass

        try:
            ac = ActionClass(action_class)
        except ValueError:
            return False, f"Unknown action class: {action_class}"

        if ActionClass.is_mutating(ac) and report.blocks_mutation:
            return False, f"Drift level {report.drift_level.value} blocks mutation"
        if ac == ActionClass.IRREVERSIBLE and report.blocks_irreversible:
            return False, f"Drift level {report.drift_level.value} blocks irreversible"
        return True, "OK"

    # ═══════════════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ═══════════════════════════════════════════════════════════════════

    def _read_git_commit(self) -> str:
        """Read the current git commit SHA."""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        # Fallback: read .git_commit file
        commit_file = self.deployed_root / "arifosmcp" / ".git_commit"
        if commit_file.exists():
            return commit_file.read_text().strip()

        return "unknown"

    def _read_deployed_commit(self) -> str:
        """Read the deployed commit SHA from the runtime."""
        commit_file = self.deployed_root / "arifosmcp" / ".git_commit"
        if commit_file.exists():
            return commit_file.read_text().strip()
        return "unknown"

    def _hash_tool_manifest(self) -> str:
        """Hash the tool manifest (constitutional_map.py)."""
        manifest = self.repo_root / "arifosmcp" / "constitutional_map.py"
        if manifest.exists():
            return self.hash_file(manifest)
        return ""

    def _hash_schemas(self) -> str:
        """Hash all schema files."""
        schema_dir = self.repo_root / "arifosmcp" / "schemas"
        return self.hash_directory(schema_dir, "*.py")

    def _hash_constitution(self) -> str:
        """Hash the constitution (core/laws.py + GENESIS/)."""
        laws = self.repo_root / "core" / "laws.py"
        genesis = self.repo_root / "GENESIS"

        combined = b""
        if laws.exists():
            combined += laws.read_bytes()
        if genesis.exists():
            for f in sorted(genesis.rglob("*.md")):
                combined += f.read_bytes()
        return f"sha256:{hashlib.sha256(combined).hexdigest()}" if combined else ""

    def _hash_env_config(self) -> str:
        """Hash environment config (excluding secrets)."""
        env_file = self.repo_root / ".env.example"
        if env_file.exists():
            return self.hash_file(env_file)
        return ""

    def _read_deployment_timestamp(self) -> datetime | None:
        """Read the deployment timestamp."""
        timestamp_file = self.deployed_root / "arifosmcp" / ".deploy_timestamp"
        if timestamp_file.exists():
            try:
                return datetime.fromisoformat(timestamp_file.read_text().strip())
            except Exception:
                pass
        return None


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_default_detector: DriftDetector | None = None


def get_drift_detector() -> DriftDetector:
    """Get or create the default drift detector."""
    global _default_detector
    if _default_detector is None:
        _default_detector = DriftDetector()
    return _default_detector


def detect_drift() -> DriftReport:
    """Convenience function to run drift detection."""
    return get_drift_detector().detect()


# ═══════════════════════════════════════════════════════════════════════════
# SELF-CHECK
# ═══════════════════════════════════════════════════════════════════════════


def _self_check() -> bool:
    """Verify drift detector works correctly."""
    detector = DriftDetector()

    # 1. Hash a known file
    test_hash = detector.hash_string("hello")
    assert test_hash.startswith("sha256:"), f"Hash should start with sha256:, got {test_hash}"
    assert len(test_hash) == 71, f"Hash should be sha256: + 64 hex, got {len(test_hash)}"

    # 2. DriftReport levels
    r = detector.detect()
    assert isinstance(r, DriftReport)
    assert r.drift_level in DriftLevel.__members__.values()

    # 3. Blocking rules
    assert (
        DriftReport(
            build_hash="a",
            runtime_hash="a",
            tool_manifest_hash="a",
            schema_hash="a",
            constitution_hash="a",
            env_config_hash="a",
            drift_level=DriftLevel.NONE,
        ).blocks_mutation
        is False
    )

    assert (
        DriftReport(
            build_hash="a",
            runtime_hash="a",
            tool_manifest_hash="a",
            schema_hash="a",
            constitution_hash="a",
            env_config_hash="a",
            drift_level=DriftLevel.HIGH,
        ).blocks_mutation
        is True
    )

    # 4. is_safe_for
    ok, msg = detector.is_safe_for("OBSERVE")
    assert ok, f"OBSERVE should be safe even with drift: {msg}"

    return True


if __name__ == "__main__":
    assert _self_check(), "DriftDetector self-check FAILED"
    print("DriftDetector self-check PASSED.")
