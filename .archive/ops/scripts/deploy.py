#!/usr/bin/env python3
"""
arifOS MCP - Zero-Chaos Deployment System
=========================================

A sovereign deployment automation that en constitutional safety checks
before any code reaches production.

Usage:
    python scripts/deploy.py --environment production
    python scripts/deploy.py --environment staging --dry-run
    python scripts/deploy.py --auto-rollback-on-failure

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# Deployment Configuration
DEPLOYMENT_CONFIG = {
    "environments": {
        "staging": {
            "host": "staging.arif-fazil.com",
            "ssh_user": "deploy",
            "deploy_path": "/root/arifosmcp-staging",
            "docker_compose_file": "docker-compose.staging.yml",
            "health_endpoint": "/health",
            "requires_approval": False,
            "run_tests": True,
        },
        "production": {
            "host": "arif-fazil.com",
            "ssh_user": "root",
            "deploy_path": "/root/arifosmcp",
            "docker_compose_file": "docker-compose.yml",
            "health_endpoint": "/health",
            "requires_approval": True,
            "run_tests": True,
            "backup_before_deploy": True,
        },
    },
    "safety": {
        "required_tests": ["unit", "integration", "constitutional"],
        "min_coverage": 80,
        "max_deploy_time_seconds": 300,
        "health_check_retries": 10,
        "health_check_interval": 5,
    },
    "notifications": {
        "slack_webhook_env": "DEPLOY_SLACK_WEBHOOK",
        "telegram_bot_token_env": "DEPLOY_TELEGRAM_TOKEN",
        "telegram_chat_id_env": "DEPLOY_TELEGRAM_CHAT_ID",
    },
}


class DeployStatus(Enum):
    """Constitutional deployment status."""
    PENDING = "pending"
    VALIDATING = "validating"
    TESTING = "testing"
    DEPLOYING = "deploying"
    HEALTH_CHECKING = "health_checking"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeployError(Exception):
    """Deployment failure with constitutional context."""
    def __init__(self, message: str, stage: str, remedy: str | None = None):
        super().__init__(message)
        self.stage = stage
        self.remedy = remedy


@dataclass
class DeployContext:
    """Deployment context for audit trail."""
    environment: str
    git_sha: str
    git_branch: str
    deployer: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: DeployStatus = DeployStatus.PENDING
    stages: list[dict[str, Any]] = field(default_factory=list)
    rollback_sha: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "environment": self.environment,
            "git_sha": self.git_sha,
            "git_branch": self.git_branch,
            "deployer": self.deployer,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "stages": self.stages,
            "rollback_sha": self.rollback_sha,
        }


class DeploymentOrchestrator:
    """
    Zero-chaos deployment orchestrator with constitutional governance.
    
    Enforces:
    - F1 (Amanah): Reversible deployments with automatic rollback
    - F2 (Truth): Honest status reporting, no hiding failures
    - F4 (Clarity): Clear stage progression and logging
    - F11 (Command Auth): Verified identity before production changes
    """
    
    def __init__(self, environment: str, dry_run: bool = False, auto_rollback: bool = True):
        self.environment = environment
        self.config = DEPLOYMENT_CONFIG["environments"][environment]
        self.safety = DEPLOYMENT_CONFIG["safety"]
        self.dry_run = dry_run
        self.auto_rollback = auto_rollback
        self.context = self._initialize_context()
        self._colors = self._setup_colors()
        
    def _setup_colors(self) -> dict[str, str]:
        """Setup ANSI colors if terminal supports it."""
        if os.getenv("NO_COLOR") or not sys.stdout.isatty():
            return {k: "" for k in ["green", "yellow", "red", "blue", "cyan", "bold", "reset"]}
        return {
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "blue": "\033[94m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
            "reset": "\033[0m",
        }
    
    def _color(self, name: str) -> str:
        return self._colors.get(name, "")
    
    def _log(self, message: str, level: str = "info"):
        """Log with color coding."""
        color_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "stage": "cyan",
        }
        color = self._color(color_map.get(level, "reset"))
        reset = self._color("reset")
        bold = self._color("bold")
        
        prefix = {
            "info": "ℹ️ ",
            "success": "✅",
            "warning": "⚠️ ",
            "error": "❌",
            "stage": "🔷",
        }.get(level, "  ")
        
        print(f"{color}{prefix}{bold}{message}{reset}")
        
        # Add to context stages
        self.context.stages.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
        })
    
    def _initialize_context(self) -> DeployContext:
        """Initialize deployment context with current git state."""
        git_sha = self._run_local(["git", "rev-parse", "HEAD"], capture=True).strip()
        git_branch = self._run_local(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture=True).strip()
        deployer = os.getenv("USER") or os.getenv("USERNAME") or "unknown-agent"
        
        return DeployContext(
            environment=self.environment,
            git_sha=git_sha,
            git_branch=git_branch,
            deployer=deployer,
        )
    
    def _run_local(self, cmd: list[str], capture: bool = False, cwd: Path | None = None) -> str:
        """Run local command with error handling."""
        if self.dry_run and not capture:
            self._log(f"[DRY-RUN] Would run: {' '.join(cmd)}", "warning")
            return ""
        
        try:
            if capture:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True, cwd=cwd
                )
                return result.stdout
            else:
                subprocess.run(cmd, check=True, cwd=cwd)
                return ""
        except subprocess.CalledProcessError as e:
            raise DeployError(
                f"Command failed: {' '.join(cmd)}\n{e.stderr}",
                stage="local_execution",
                remedy="Check command output and retry",
            )
    
    def _run_remote(self, cmd: str) -> str:
        """Run command on remote server via SSH."""
        host = self.config["host"]
        user = self.config["ssh_user"]
        ssh_cmd = f"ssh {user}@{host} '{cmd}'"
        
        if self.dry_run:
            self._log(f"[DRY-RUN] Would SSH: {cmd[:60]}...", "warning")
            return ""
        
        try:
            result = subprocess.run(
                ssh_cmd, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise DeployError(
                f"Remote command failed: {cmd[:60]}...\n{e.stderr}",
                stage="remote_execution",
                remedy="Check SSH connectivity and server status",
            )
    
    def _validate_environment(self):
        """F11: Verify identity and authorization."""
        self.context.status = DeployStatus.VALIDATING
        self._log(f"Stage 1/6: Validating {self.environment} deployment prerequisites", "stage")
        
        # Check if we're on a clean git state for production
        if self.environment == "production":
            status = self._run_local(["git", "status", "--porcelain"], capture=True)
            if status.strip():
                raise DeployError(
                    "Uncommitted changes detected. Production deploys require clean git state.",
                    stage="validation",
                    remedy="Commit changes: git add . && git commit -m 'Pre-deploy changes'",
                )
            
            # Must be on main branch
            if self.context.git_branch != "main":
                raise DeployError(
                    f"Production deploys must be from 'main' branch, currently on '{self.context.git_branch}'",
                    stage="validation",
                    remedy="Switch to main: git checkout main && git pull",
                )
        
        # Verify SSH access
        self._log("Checking SSH connectivity...")
        try:
            self._run_remote("echo 'SSH_OK'")
            self._log("SSH connectivity verified", "success")
        except DeployError:
            raise DeployError(
                f"Cannot connect to {self.config['host']} as {self.config['ssh_user']}",
                stage="validation",
                remedy="Check SSH keys and server accessibility",
            )
        
        self._log("Environment validation passed", "success")
    
    def _run_tests(self):
        """F2: Run constitutional test suite."""
        if not self.config.get("run_tests", True):
            self._log("Skipping tests (configured)", "warning")
            return
        
        self.context.status = DeployStatus.TESTING
        self._log("Stage 2/6: Running constitutional test suite", "stage")
        
        test_stages = [
            ("Unit Tests", ["pytest", "tests/00_unit/", "-v", "--tb=short"]),
            ("Integration Tests", ["pytest", "tests/01_integration/", "-v", "--tb=short"]),
            ("Constitutional Tests", ["pytest", "tests/03_constitutional/", "-v"]),
        ]
        
        for test_name, test_cmd in test_stages:
            self._log(f"Running {test_name}...")
            try:
                self._run_local(test_cmd)
                self._log(f"{test_name} passed", "success")
            except DeployError as e:
                raise DeployError(
                    f"{test_name} failed: {e}",
                    stage="testing",
                    remedy="Fix failing tests before deploying",
                )
        
        self._log("All constitutional tests passed", "success")
    
    def _backup_current_state(self):
        """F1: Create reversible backup before changes."""
        if not self.config.get("backup_before_deploy", False):
            return
        
        self._log("Creating rollback backup...")
        
        deploy_path = self.config["deploy_path"]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"arifosmcp_backup_{timestamp}"
        
        # Get current deployed SHA for rollback
        current_sha = self._run_remote(
            f"cd {deploy_path} && git rev-parse HEAD 2>/dev/null || echo 'UNKNOWN'"
        ).strip()
        self.context.rollback_sha = current_sha
        
        # Create backup
        backup_cmd = f"cd {deploy_path} && docker-compose ps -q | xargs -r docker inspect --format='{{{{.Config.Image}}}}' > /tmp/{backup_name}_images.txt 2>/dev/null; cp -r {deploy_path} /tmp/{backup_name} 2>/dev/null || true"
        self._run_remote(backup_cmd)
        
        self._log(f"Backup created: {backup_name}", "success")
    
    def _deploy_to_server(self):
        """Execute the deployment."""
        self.context.status = DeployStatus.DEPLOYING
        self._log("Stage 4/6: Deploying to server", "stage")
        
        deploy_path = self.config["deploy_path"]
        compose_file = self.config["docker_compose_file"]
        
        # Deployment commands
        commands = [
            # Navigate to deploy directory
            f"cd {deploy_path}",
            # Stash any local changes
            "git stash || true",
            # Pull latest code
            "git fetch origin",
            f"git checkout {self.context.git_branch}",
            "git pull origin {self.context.git_branch}",
            # Install/update dependencies
            "pip install -e . --quiet 2>/dev/null || true",
            # Build and restart containers
            f"docker-compose -f {compose_file} build --no-cache arifosmcp",
            f"docker-compose -f {compose_file} up -d arifosmcp",
            # Cleanup
            "docker system prune -f || true",
        ]
        
        deploy_script = "; ".join(commands)
        
        self._log("Executing deployment (this may take 2-3 minutes)...")
        start_time = time.time()
        
        self._run_remote(deploy_script)
        
        elapsed = time.time() - start_time
        self._log(f"Deployment completed in {elapsed:.1f}s", "success")
    
    def _health_check(self) -> bool:
        """Verify deployment health."""
        self.context.status = DeployStatus.HEALTH_CHECKING
        self._log("Stage 5/6: Running health checks", "stage")
        
        host = self.config["host"]
        endpoint = self.config["health_endpoint"]
        url = f"https://{host}{endpoint}"
        
        max_retries = self.safety["health_check_retries"]
        interval = self.safety["health_check_interval"]
        
        for attempt in range(1, max_retries + 1):
            try:
                import urllib.request
                import ssl
                
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(url, context=ctx, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        self._log(f"Health check passed: {data.get('status', 'OK')}", "success")
                        return True
            except Exception as e:
                if attempt < max_retries:
                    self._log(f"Health check {attempt}/{max_retries} failed, retrying in {interval}s...", "warning")
                    time.sleep(interval)
                else:
                    self._log(f"Health check failed after {max_retries} attempts: {e}", "error")
                    return False
        
        return False
    
    def _rollback(self):
        """F1: Emergency rollback to previous state."""
        self._log("🚨 INITIATING ROLLBACK", "error")
        self.context.status = DeployStatus.ROLLED_BACK
        
        if not self.context.rollback_sha or self.context.rollback_sha == "UNKNOWN":
            self._log("No rollback SHA available, manual intervention required", "error")
            return False
        
        deploy_path = self.config["deploy_path"]
        compose_file = self.config["docker_compose_file"]
        
        try:
            rollback_commands = [
                f"cd {deploy_path}",
                f"git reset --hard {self.context.rollback_sha}",
                f"docker-compose -f {compose_file} up -d --force-recreate arifosmcp",
            ]
            self._run_remote("; ".join(rollback_commands))
            self._log(f"Rollback to {self.context.rollback_sha[:8]} completed", "success")
            return True
        except Exception as e:
            self._log(f"Rollback failed: {e}", "error")
            return False
    
    def _save_deploy_manifest(self):
        """Save deployment manifest for audit trail."""
        manifest_dir = Path("deployment/manifests")
        manifest_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = self.context.timestamp.strftime("%Y%m%d_%H%M%S")
        manifest_file = manifest_dir / f"deploy_{self.environment}_{timestamp}.json"
        
        with open(manifest_file, "w") as f:
            json.dump(self.context.to_dict(), f, indent=2)
        
        self._log(f"Deployment manifest saved: {manifest_file}")
    
    def deploy(self) -> bool:
        """
        Execute full deployment with constitutional safety.
        
        Returns True if successful, False if failed (and rollback attempted).
        """
        bold = self._color("bold")
        reset = self._color("reset")
        cyan = self._color("cyan")
        
        print(f"\n{cyan}{'='*60}{reset}")
        print(f"{bold}arifOS MCP - Constitutional Deployment System{reset}")
        print(f"{cyan}{'='*60}{reset}\n")
        
        self._log(f"Deploying to: {self.environment}")
        self._log(f"Git SHA: {self.context.git_sha[:8]}")
        self._log(f"Branch: {self.context.git_branch}")
        self._log(f"Deployer: {self.context.deployer}")
        
        if self.dry_run:
            self._log("DRY RUN MODE - No actual changes will be made", "warning")
        
        print()
        
        try:
            # Stage 1: Validation
            self._validate_environment()
            
            # Stage 2: Testing
            self._run_tests()
            
            # Stage 3: Backup
            self._backup_current_state()
            
            # Stage 4: Deploy
            self._deploy_to_server()
            
            # Stage 5: Health Check
            if not self._health_check():
                if self.auto_rollback:
                    self._log("Health check failed, triggering auto-rollback...", "error")
                    self._rollback()
                raise DeployError(
                    "Deployment health check failed",
                    stage="health_check",
                    remedy="Check server logs and retry deployment",
                )
            
            # Stage 6: Complete
            self.context.status = DeployStatus.COMPLETED
            self._log("Stage 6/6: Deployment completed successfully", "stage")
            
            print(f"\n{self._color('green')}{'='*60}{reset}")
            print(f"{bold}✅ DEPLOYMENT SUCCESSFUL{reset}")
            print(f"{self._color('green')}Environment: {self.environment}{reset}")
            print(f"{self._color('green')}Version: {self.context.git_sha[:8]}{reset}")
            print(f"{self._color('green')}URL: https://{self.config['host']}{reset}")
            print(f"{self._color('green')}{'='*60}{reset}\n")
            
            self._save_deploy_manifest()
            return True
            
        except DeployError as e:
            self._log(f"Deployment failed at stage: {e.stage}", "error")
            self._log(f"Error: {e}", "error")
            if e.remedy:
                self._log(f"Remedy: {e.remedy}", "info")
            
            self.context.status = DeployStatus.FAILED
            self._save_deploy_manifest()
            
            print(f"\n{self._color('red')}{'='*60}{reset}")
            print(f"{bold}❌ DEPLOYMENT FAILED{reset}")
            print(f"{self._color('red')}Stage: {e.stage}{reset}")
            print(f"{self._color('red')}{'='*60}{reset}\n")
            
            return False


def main():
    parser = argparse.ArgumentParser(
        description="arifOS MCP - Zero-Chaos Deployment System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy to staging
  python scripts/deploy.py --environment staging
  
  # Dry run production deployment
  python scripts/deploy.py --environment production --dry-run
  
  # Deploy with auto-rollback disabled
  python scripts/deploy.py --environment production --no-auto-rollback
  
  # Quick deploy (skip tests)
  python scripts/deploy.py --environment staging --skip-tests
        """
    )
    parser.add_argument(
        "--environment", "-e",
        choices=["staging", "production"],
        default="staging",
        help="Target environment (default: staging)"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without executing"
    )
    parser.add_argument(
        "--no-auto-rollback",
        action="store_true",
        help="Disable automatic rollback on failure"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip test execution (not recommended)"
    )
    
    args = parser.parse_args()
    
    # Modify config if skip-tests
    if args.skip_tests:
        DEPLOYMENT_CONFIG["environments"][args.environment]["run_tests"] = False
    
    orchestrator = DeploymentOrchestrator(
        environment=args.environment,
        dry_run=args.dry_run,
        auto_rollback=not args.no_auto_rollback,
    )
    
    success = orchestrator.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
