#!/usr/bin/env python3
"""
arifosmcp/evals/rollback_verifier.py — Rollback Verification Tool

Verifies that rollback mechanisms are functional:
- Docker image tags available
- Docker-compose backup exists
- Git rollback points (tags/branches)
- Database snapshots (if applicable)
- Config backups

Usage:
  # Verify rollback before deployment
  python rollback_verifier.py --pre-deploy
  
  # Create rollback point
  python rollback_verifier.py --create-point "v2026.04.07"
  
  # Execute rollback
  python rollback_verifier.py --rollback-to "v2026.04.06"

Authority: 000_THEORY, 888_APEX
DITEMPA BUKAN DIBERI — F1 Amanah
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from arifosmcp.runtime.models import Verdict

logger = logging.getLogger(__name__)


@dataclass
class RollbackPoint:
    """A single rollback point"""
    name: str
    timestamp: str
    git_sha: str | None
    docker_image: str | None
    compose_backup: bool
    config_backup: bool


@dataclass
class RollbackReport:
    """Rollback verification report"""
    timestamp: str
    current_git_sha: str | None
    rollback_points: list[RollbackPoint]
    can_rollback: bool
    recommended_point: str | None
    
    @property
    def verdict(self) -> Verdict:
        return Verdict.SEAL if self.can_rollback else Verdict.HOLD


class RollbackVerifier:
    """Verifies and manages rollback capabilities"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
    
    def _run_cmd(self, cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
        """Run a shell command and return (returncode, stdout, stderr)"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def _get_git_sha(self) -> str | None:
        """Get current git SHA"""
        rc, stdout, _ = self._run_cmd(["git", "rev-parse", "HEAD"])
        return stdout.strip()[:12] if rc == 0 else None
    
    def _get_git_tags(self) -> list[str]:
        """Get all rollback tags"""
        rc, stdout, _ = self._run_cmd(["git", "tag", "-l", "rollback-*"])
        return [t.strip() for t in stdout.strip().split("\n") if t.strip()]
    
    def _get_docker_images(self) -> list[str]:
        """Get available docker image tags"""
        rc, stdout, _ = self._run_cmd([
            "docker", "images", "arifosmcp",
            "--format", "{{.Tag}}|{{.CreatedAt}}"
        ])
        if rc != 0:
            return []
        return [line.strip() for line in stdout.strip().split("\n") if line.strip()]
    
    def _check_compose_backup(self) -> bool:
        """Check if docker-compose backup exists"""
        backup_paths = [
            self.project_root / "docker-compose.yml.backup",
            self.project_root / "docker-compose.yml.bak",
            self.project_root / ".backup" / "docker-compose.yml",
        ]
        return any(p.exists() for p in backup_paths)
    
    def _check_config_backup(self) -> bool:
        """Check if config backup exists"""
        backup_paths = [
            self.project_root / "config" / "backup",
            self.project_root / ".backup" / "config",
        ]
        return any(p.exists() and p.is_dir() for p in backup_paths)
    
    async def verify(self) -> RollbackReport:
        """Verify rollback capabilities"""
        
        print("=" * 80)
        print("ROLLBACK VERIFICATION")
        print("=" * 80)
        
        current_sha = self._get_git_sha()
        print(f"Current Git SHA: {current_sha or 'unknown'}")
        
        rollback_points: list[RollbackPoint] = []
        
        # Check git rollback tags
        print("\n[Git Rollback Points]")
        git_tags = self._get_git_tags()
        for tag in git_tags[:5]:  # Last 5 tags
            # Get SHA for tag
            rc, stdout, _ = self._run_cmd(["git", "rev-list", "-n", "1", tag])
            tag_sha = stdout.strip()[:12] if rc == 0 else None
            
            point = RollbackPoint(
                name=tag,
                timestamp=datetime.now(timezone.utc).isoformat(),
                git_sha=tag_sha,
                docker_image=None,
                compose_backup=False,
                config_backup=False
            )
            rollback_points.append(point)
            print(f"  ✅ {tag} -> {tag_sha}")
        
        if not git_tags:
            print("  ⚠️ No rollback tags found (create with --create-point)")
        
        # Check docker images
        print("\n[Docker Images]")
        docker_images = self._get_docker_images()
        for img in docker_images[:5]:
            parts = img.split("|")
            tag = parts[0] if parts else img
            print(f"  ✅ arifosmcp:{tag}")
        
        if not docker_images:
            print("  ⚠️ No docker images found")
        
        # Check compose backup
        print("\n[Compose Backup]")
        compose_backup = self._check_compose_backup()
        if compose_backup:
            print("  ✅ docker-compose.yml backup exists")
        else:
            print("  ⚠️ No compose backup found")
        
        # Check config backup
        print("\n[Config Backup]")
        config_backup = self._check_config_backup()
        if config_backup:
            print("  ✅ Config backup exists")
        else:
            print("  ⚠️ No config backup found")
        
        # Determine if rollback is possible
        can_rollback = len(git_tags) > 0 or len(docker_images) > 0
        recommended = git_tags[-1] if git_tags else (docker_images[0].split("|")[0] if docker_images else None)
        
        return RollbackReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            current_git_sha=current_sha,
            rollback_points=rollback_points,
            can_rollback=can_rollback,
            recommended_point=recommended
        )
    
    async def create_rollback_point(self, name: str) -> bool:
        """Create a new rollback point"""
        
        print("=" * 80)
        print(f"CREATING ROLLBACK POINT: {name}")
        print("=" * 80)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        tag_name = f"rollback-{name}-{timestamp}"
        
        # 1. Create git tag
        print("\n[1/4] Creating git tag...")
        rc, _, stderr = self._run_cmd(["git", "tag", "-a", tag_name, "-m", f"Rollback point: {name}"])
        if rc == 0:
            print(f"  ✅ Tag created: {tag_name}")
        else:
            print(f"  ❌ Failed to create tag: {stderr}")
            return False
        
        # 2. Backup docker-compose
        print("\n[2/4] Backing up docker-compose...")
        compose_path = self.project_root / "docker-compose.yml"
        backup_path = self.project_root / f"docker-compose.yml.backup.{timestamp}"
        if compose_path.exists():
            import shutil
            shutil.copy(compose_path, backup_path)
            print(f"  ✅ Backed up to {backup_path}")
        else:
            print("  ⚠️ docker-compose.yml not found")
        
        # 3. Tag docker image
        print("\n[3/4] Tagging docker image...")
        rc, _, stderr = self._run_cmd([
            "docker", "tag", "arifosmcp:latest", f"arifosmcp:{name}"
        ])
        if rc == 0:
            print(f"  ✅ Image tagged: arifosmcp:{name}")
        else:
            print(f"  ⚠️ Could not tag image: {stderr}")
        
        # 4. Backup config
        print("\n[4/4] Backing up config...")
        config_path = self.project_root / "config"
        backup_dir = self.project_root / ".backup"
        backup_dir.mkdir(exist_ok=True)
        config_backup = backup_dir / f"config_{timestamp}"
        if config_path.exists():
            import shutil
            shutil.copytree(config_path, config_backup, dirs_exist_ok=True)
            print(f"  ✅ Config backed up to {config_backup}")
        else:
            print("  ⚠️ config/ not found")
        
        print(f"\n{'=' * 80}")
        print(f"ROLLBACK POINT CREATED: {tag_name}")
        print(f"{'=' * 80}")
        
        return True
    
    async def execute_rollback(self, target: str) -> bool:
        """Execute rollback to a specific point"""
        
        print("=" * 80)
        print(f"EXECUTING ROLLBACK TO: {target}")
        print(f"{'=' * 80}")
        print("\n⚠️  WARNING: This will revert the system to a previous state!")
        print("     Current changes may be lost.")
        print("")
        
        # Confirm rollback
        confirm = input("Type 'ROLLBACK' to confirm: ")
        if confirm != "ROLLBACK":
            print("Rollback cancelled.")
            return False
        
        # 1. Git rollback
        print("\n[1/3] Git rollback...")
        rc, _, stderr = self._run_cmd(["git", "checkout", target])
        if rc == 0:
            print(f"  ✅ Checked out: {target}")
        else:
            print(f"  ❌ Git checkout failed: {stderr}")
            return False
        
        # 2. Docker rollback
        print("\n[2/3] Docker rollback...")
        rc, _, stderr = self._run_cmd([
            "docker", "tag", f"arifosmcp:{target}", "arifosmcp:latest"
        ])
        if rc == 0:
            print("  ✅ Docker image rolled back")
        else:
            print(f"  ⚠️ Docker rollback warning: {stderr}")
        
        # 3. Restart services
        print("\n[3/3] Restarting services...")
        rc, _, stderr = self._run_cmd(["docker-compose", "up", "-d"])
        if rc == 0:
            print("  ✅ Services restarted")
        else:
            print(f"  ❌ Service restart failed: {stderr}")
            return False
        
        print(f"\n{'=' * 80}")
        print(f"ROLLBACK COMPLETE: {target}")
        print(f"{'=' * 80}")
        
        return True
    
    def print_report(self, report: RollbackReport):
        """Print human-readable rollback report"""
        print("\n" + "=" * 80)
        print("ROLLBACK VERIFICATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {report.timestamp}")
        print(f"Current SHA: {report.current_git_sha or 'unknown'}")
        print(f"\nRollback Points: {len(report.rollback_points)}")
        for point in report.rollback_points:
            print(f"  - {point.name} ({point.git_sha})")
        
        print(f"\nCan Rollback: {report.can_rollback}")
        if report.recommended_point:
            print(f"Recommended Point: {report.recommended_point}")
        
        print("\n" + "=" * 80)
        print(f"VERDICT: {report.verdict.value}")
        print("=" * 80)
        
        if report.verdict == Verdict.SEAL:
            print("✅ ROLLBACK READY: Safe to proceed with deployment")
        else:
            print("⏸️ ROLLBACK NOT READY: Create rollback point before deploying")


async def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Rollback Verifier")
    parser.add_argument("--verify", "-v", action="store_true",
                       help="Verify rollback capabilities (default)")
    parser.add_argument("--create-point", "-c", metavar="NAME",
                       help="Create a new rollback point")
    parser.add_argument("--rollback-to", "-r", metavar="TARGET",
                       help="Execute rollback to target")
    parser.add_argument("--output", "-o", default="rollback_report.json",
                       help="Output file for verification report")
    
    args = parser.parse_args()
    
    verifier = RollbackVerifier()
    
    if args.create_point:
        success = await verifier.create_rollback_point(args.create_point)
        sys.exit(0 if success else 1)
    
    elif args.rollback_to:
        success = await verifier.execute_rollback(args.rollback_to)
        sys.exit(0 if success else 1)
    
    else:
        # Default: verify
        report = await verifier.verify()
        verifier.print_report(report)
        
        # Save JSON
        with open(args.output, 'w') as f:
            json.dump({
                "timestamp": report.timestamp,
                "current_git_sha": report.current_git_sha,
                "can_rollback": report.can_rollback,
                "recommended_point": report.recommended_point,
                "verdict": report.verdict.value,
                "rollback_points": [
                    {
                        "name": p.name,
                        "timestamp": p.timestamp,
                        "git_sha": p.git_sha
                    }
                    for p in report.rollback_points
                ]
            }, f, indent=2)
        
        print(f"\n📄 Report saved to: {args.output}")
        
        # Exit code
        sys.exit(0 if report.verdict == Verdict.SEAL else 1)


if __name__ == "__main__":
    asyncio.run(main())
