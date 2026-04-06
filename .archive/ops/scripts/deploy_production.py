"""
arifOS Production Deployment Script
===================================

Automated deployment helpers for Railway, Docker, and the canonical
VPS overlay-image flow used by production.

Usage:
    python scripts/deploy_production.py --platform validate
    python scripts/deploy_production.py --platform railway
    python scripts/deploy_production.py --platform docker
    python scripts/deploy_production.py --platform vps-overlay

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shlex
import subprocess
import sys
import textwrap
from pathlib import Path

import tomllib

sys.path.insert(0, str(Path(__file__).parent.parent))

from arifosmcp.runtime.public_registry import (
    deployment_tool_contract as registry_deployment_tool_contract,
)
from arifosmcp.runtime.public_registry import (
    public_tool_names,
)

ROOT = Path(__file__).parent.parent
DEFAULT_VPS_HOST = "root@72.62.71.199"
DEFAULT_PUBLIC_BASE_URL = "https://arifosmcp.arif-fazil.com"
PUBLIC_DEPLOYMENT_TOOLS = public_tool_names()


class Colors:
    """ASCII-only color codes (Windows-safe)."""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def log_ok(msg: str) -> None:
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")


def log_warn(msg: str) -> None:
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")


def log_err(msg: str) -> None:
    print(f"{Colors.RED}[ERR]{Colors.RESET} {msg}")


def log_info(msg: str) -> None:
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")


def read_project_version(root: Path = ROOT) -> str:
    """Read the project version from pyproject.toml."""
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def normalize_release_version(version: str) -> str:
    """Normalize YYYY.M.D style versions to YYYY.MM.DD for release tagging."""
    parts = version.split(".")
    if len(parts) < 3:
        return version
    year, month, day, *rest = parts
    if year.isdigit() and month.isdigit() and day.isdigit() and len(year) == 4:
        normalized = f"{year}.{int(month):02d}.{int(day):02d}"
        return ".".join([normalized, *rest]) if rest else normalized
    return version


def read_git_sha(root: Path = ROOT) -> str:
    """Read the current short git SHA."""
    result = subprocess.run(
        ["git", "rev-parse", "--short=8", "HEAD"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def build_overlay_image_tag(version: str, git_sha: str, base_repo: str = "arifos/arifosmcp") -> str:
    """Build the immutable image tag used by the VPS overlay deploy."""
    return f"{base_repo}:{normalize_release_version(version)}-{git_sha[:8]}"


def deployment_tool_contract(public_profile: str) -> tuple[int, tuple[str, ...]]:
    """Return the minimum public tool contract for a deployment profile."""
    return registry_deployment_tool_contract(public_profile)


def build_vps_overlay_script(
    *,
    host: str,
    app_dir: str,
    image_tag: str,
    version: str,
    git_sha: str,
    base_image: str,
    container_name: str,
    candidate_name: str,
    candidate_port: int,
    env_file: str,
    prod_bind: str,
    public_base_url: str,
    expected_tools: int,
    required_tools: tuple[str, ...],
) -> str:
    """Render the remote bash script for immutable VPS image deployment."""
    public_health_url = f"{public_base_url.rstrip('/')}/health"
    public_tools_url = f"{public_base_url.rstrip('/')}/tools"

    return textwrap.dedent(
        f"""\
        set -euo pipefail

        APP_DIR={shlex.quote(app_dir)}
        IMAGE_TAG={shlex.quote(image_tag)}
        VERSION={shlex.quote(version)}
        GIT_SHA={shlex.quote(git_sha[:8])}
        CONTAINER_NAME={shlex.quote(container_name)}
        CANDIDATE_NAME={shlex.quote(candidate_name)}
        CANDIDATE_PORT={candidate_port}
        ENV_FILE={shlex.quote(env_file)}
        PROD_BIND={shlex.quote(prod_bind)}
        PUBLIC_HEALTH_URL={shlex.quote(public_health_url)}
        PUBLIC_TOOLS_URL={shlex.quote(public_tools_url)}

        cd "$APP_DIR"
        git fetch origin
        git checkout main
        git pull --ff-only origin main

        trap 'docker rm -f "$CANDIDATE_NAME" >/dev/null 2>&1 || true' EXIT

        BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

        docker rm -f "$CANDIDATE_NAME" >/dev/null 2>&1 || true
        docker build \\
          -t "$IMAGE_TAG" \\
          --build-arg ARIFOS_VERSION="$VERSION" \\
          --build-arg GIT_SHA="$GIT_SHA" \\
          --build-arg BUILD_TIME="$BUILD_TIME" \\
          .

        docker run -d \\
          --name "$CANDIDATE_NAME" \\
          --env-file "$ENV_FILE" \\
          -p 127.0.0.1:${{CANDIDATE_PORT}}:8080 \\
          "$IMAGE_TAG" >/dev/null

        for i in $(seq 1 45); do
          if curl -fsS "http://127.0.0.1:${{CANDIDATE_PORT}}/health" \\
             >/tmp/arifos_candidate_health.json 2>/dev/null; then
            break
          fi
          sleep 2
        done

        curl -fsS "http://127.0.0.1:${{CANDIDATE_PORT}}/tools" >/tmp/arifos_candidate_tools.json

        python3 - <<'PY'
        import json
        from pathlib import Path

        data = json.loads(Path("/tmp/arifos_candidate_tools.json").read_text())
        names = {{tool["name"] for tool in data["tools"] if "name" in tool}}
        count = len(names)
        missing = sorted(set({required_tools!r}) - names)
        if count < {expected_tools}:
            raise SystemExit(f"candidate tool count too low: {{count}} < {expected_tools}")
        if missing:
            raise SystemExit(f"candidate missing core tools: {{', '.join(missing)}}")
        print(f"candidate_tools={{count}}")
        PY

        docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
        docker run -d \\
          --name "$CONTAINER_NAME" \\
          --restart unless-stopped \\
          --env-file "$ENV_FILE" \\
          -p "$PROD_BIND" \\
          "$IMAGE_TAG" >/dev/null

        for i in $(seq 1 45); do
          if curl -fsS http://127.0.0.1:8088/health >/tmp/arifos_prod_health.json 2>/dev/null; then
            break
          fi
          sleep 2
        done

        curl -fsS "$PUBLIC_HEALTH_URL" >/tmp/arifos_public_health.json
        curl -fsS "$PUBLIC_TOOLS_URL" >/tmp/arifos_public_tools.json

        python3 - <<'PY'
        import json
        from pathlib import Path

        public_tools = json.loads(Path("/tmp/arifos_public_tools.json").read_text())
        names = {{tool["name"] for tool in public_tools["tools"] if "name" in tool}}
        count = len(names)
        missing = sorted(set({required_tools!r}) - names)
        if count < {expected_tools}:
            raise SystemExit(f"public tool count too low: {{count}} < {expected_tools}")
        if missing:
            raise SystemExit(f"public missing core tools: {{', '.join(missing)}}")
        print(f"public_tools={{count}}")
        PY

        echo ---LOCAL-PROD-HEALTH---
        cat /tmp/arifos_prod_health.json
        echo
        echo ---PUBLIC-HEALTH---
        cat /tmp/arifos_public_health.json
        echo
        echo ---MOUNTS---
        docker inspect "$CONTAINER_NAME" --format '{{{{json .Mounts}}}}'
        echo
        echo ---IMAGE---
        docker ps --filter "name=$CONTAINER_NAME" \\
          --format '{{{{.Names}}}}\\t{{{{.Image}}}}\\t{{{{.Status}}}}'
        """
    )


def run_remote_bash(host: str, script: str) -> subprocess.CompletedProcess[bytes]:
    """Run a bash script remotely with LF-normalized stdin for Windows clients."""
    normalized = script.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    return subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", host, "/bin/bash", "-s"],
        input=normalized,
    )


async def validate_environment() -> bool:
    """Validate environment before deployment."""
    print("=" * 60)
    print("PRODUCTION DEPLOYMENT VALIDATION")
    print("=" * 60)
    print()

    checks_passed = 0
    checks_failed = 0

    version = sys.version_info
    if version >= (3, 10):
        log_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        checks_passed += 1
    else:
        log_err(f"Python {version.major}.{version.minor} (need >= 3.10)")
        checks_failed += 1

    try:
        from core.pipeline import forge

        log_ok("Core organs importable")
        checks_passed += 1
    except Exception as e:
        log_err(f"Core import failed: {e}")
        checks_failed += 1

    try:
        from arifosmcp.runtime.server import create_aaa_mcp_server

        create_aaa_mcp_server()
        log_ok("AAA runtime hub importable")
        checks_passed += 1
    except Exception as e:
        log_err(f"AAA runtime import failed: {e}")
        checks_failed += 1

    try:
        result = await forge("Validation test", actor_id="deploy")
        log_ok(f"Pipeline executes ({result.verdict})")
        checks_passed += 1
    except Exception as e:
        log_err(f"Pipeline execution failed: {e}")
        checks_failed += 1

    env_prod = ROOT / ".env.docker"
    if env_prod.exists():
        log_ok("Docker env template exists")
        checks_passed += 1
    else:
        log_warn("No .env.docker template")

    dockerfile = ROOT / "Dockerfile"
    if dockerfile.exists():
        log_ok("Dockerfile present")
        checks_passed += 1
    else:
        log_err("Dockerfile missing")
        checks_failed += 1

    railway_toml = ROOT / "railway.toml"
    if railway_toml.exists():
        log_ok("railway.toml present")
        checks_passed += 1
    else:
        log_warn("railway.toml missing")

    print()
    print("=" * 60)
    log_info(f"Checks: {checks_passed} passed, {checks_failed} failed")

    if checks_failed > 0:
        log_err("VALIDATION FAILED - Fix errors before deployment")
        return False

    log_ok("VALIDATION PASSED - Ready for production")
    return True


def deploy_railway() -> bool:
    """Deploy to Railway."""
    print()
    print("=" * 60)
    print("RAILWAY DEPLOYMENT")
    print("=" * 60)
    print()

    result = subprocess.run(["railway", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        log_err("Railway CLI not found")
        print()
        print("Install Railway CLI:")
        print("  npm install -g @railway/cli")
        print()
        print("Or use Railway Dashboard:")
        print("  https://railway.app/new/template/arifos")
        return False

    log_ok(f"Railway CLI: {result.stdout.strip()}")

    result = subprocess.run(["railway", "whoami"], capture_output=True, text=True)
    if result.returncode != 0:
        log_warn("Not logged in to Railway")
        print("Run: railway login")
        return False

    log_ok(f"Logged in as: {result.stdout.strip()}")

    result = subprocess.run(["railway", "status"], capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        log_warn("Project not linked to Railway")
        print()
        print("Options:")
        print("  1. Link existing project: railway link")
        print("  2. Create new project: railway init")
        print()
        return False

    log_ok("Project linked to Railway")
    log_info("Checking environment variables...")
    env_vars = {
        "PORT": "8080",
        "HOST": "0.0.0.0",
        "AAA_MCP_TRANSPORT": "http",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "arifosmcp_PATH": "/mcp",
        "ARIFOS_PUBLIC_TOOL_PROFILE": "public",
    }

    for key, default in env_vars.items():
        result = subprocess.run(
            ["railway", "variables", "get", key], capture_output=True, text=True, cwd=str(ROOT)
        )
        if result.returncode != 0:
            log_warn(f"Setting {key}={default}")
            subprocess.run(
                ["railway", "variables", "set", key, default], cwd=str(ROOT), capture_output=True
            )

    print()
    log_info("Starting deployment...")
    print()

    subprocess.run(["railway", "up"], cwd=str(ROOT))

    print()
    log_ok("Deployment complete!")
    print()
    print("View logs: railway logs")
    print("Open app:  railway open")

    return True


def deploy_docker() -> bool:
    """Deploy using Docker."""
    print()
    print("=" * 60)
    print("DOCKER DEPLOYMENT")
    print("=" * 60)
    print()

    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    if result.returncode != 0:
        log_err("Docker not found")
        return False

    log_ok(f"Docker: {result.stdout.strip()}")
    log_info("Building Docker image...")
    result = subprocess.run(
        ["docker", "build", "-t", "arifos-mcp:latest", "."],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log_err("Docker build failed")
        print(result.stderr)
        return False

    log_ok("Image built: arifos-mcp:latest")

    print()
    log_info("Starting container...")
    print()

    subprocess.run(
        [
            "docker",
            "run",
            "-p",
            "8080:8080",
            "-e",
            "PORT=8080",
            "-e",
            "HOST=0.0.0.0",
            "-e",
            "AAA_MCP_TRANSPORT=http",
            "-e",
            "arifosmcp_PATH=/mcp",
            "-e",
            "ARIFOS_PUBLIC_TOOL_PROFILE=public",
            "--name",
            "arifos-mcp",
            "arifos-mcp:latest",
        ]
    )

    return True


def deploy_vps_overlay(args: argparse.Namespace) -> bool:
    """Deploy current main to the VPS as an immutable overlay image."""
    version = normalize_release_version(read_project_version(ROOT))
    git_sha = read_git_sha(ROOT)
    image_tag = args.image_tag or build_overlay_image_tag(version, git_sha, args.image_repo)
    contract_tool_count, required_tools = deployment_tool_contract(args.public_profile)
    expected_tools = args.expected_tools or contract_tool_count
    script = build_vps_overlay_script(
        host=args.host,
        app_dir=args.app_dir,
        image_tag=image_tag,
        version=version,
        git_sha=git_sha,
        base_image=args.base_image,
        container_name=args.container_name,
        candidate_name=args.candidate_name,
        candidate_port=args.candidate_port,
        env_file=args.env_file,
        prod_bind=args.prod_bind,
        public_base_url=args.public_base_url,
        expected_tools=expected_tools,
        required_tools=required_tools,
    )

    if args.dry_run:
        print(script)
        return True

    log_info(f"Deploying immutable overlay image to {args.host}")
    log_info(f"Image tag: {image_tag}")

    result = run_remote_bash(args.host, script)

    if result.returncode != 0:
        log_err("VPS overlay deployment failed")
        return False

    log_ok("VPS overlay deployment complete")
    return True


def generate_railway_template() -> None:
    """Generate Railway template for sharing."""
    template = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {"builder": "DOCKERFILE", "dockerfilePath": "Dockerfile"},
        "deploy": {
            "startCommand": "uvicorn arifosmcp.runtime.server:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 30,
            "restartPolicyType": "on_failure",
            "restartPolicyMaxRetries": 3,
        },
        "variables": {
            "PORT": "8080",
            "HOST": "0.0.0.0",
            "AAA_MCP_TRANSPORT": "http",
            "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
            "arifosmcp_PATH": "/mcp",
            "ARIFOS_PUBLIC_TOOL_PROFILE": "public",
        },
    }

    output = ROOT / "railway.template.json"
    output.write_text(json.dumps(template, indent=2), encoding="utf-8")

    log_ok(f"Railway template generated: {output}")
    print()
    print("Deploy via template:")
    print("  https://railway.app/new/template/arifos")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy arifOS to production")
    parser.add_argument(
        "--platform",
        "-p",
        choices=["railway", "docker", "validate", "vps-overlay"],
        default="validate",
        help="Deployment platform",
    )
    parser.add_argument(
        "--generate-template", "-t", action="store_true", help="Generate Railway template"
    )
    parser.add_argument("--host", default=DEFAULT_VPS_HOST, help="SSH host for VPS deploy")
    parser.add_argument("--app-dir", default="/root/arifOS", help="Remote app directory")
    parser.add_argument("--base-image", default="arifos/arifosmcp:latest", help="Base image")
    parser.add_argument("--image-repo", default="arifos/arifosmcp", help="Target image repository")
    parser.add_argument("--image-tag", default="", help="Override full image tag")
    parser.add_argument("--container-name", default="arifosmcp", help="Prod container name")
    parser.add_argument(
        "--candidate-name", default="arifosmcp_candidate_overlay", help="Candidate container name"
    )
    parser.add_argument(
        "--candidate-port", type=int, default=18089, help="Candidate localhost port"
    )
    parser.add_argument("--env-file", default=".env.docker", help="Remote env file path")
    parser.add_argument("--prod-bind", default="127.0.0.1:8088:8080", help="Prod bind mapping")
    parser.add_argument(
        "--public-profile",
        choices=["public", "full", "chatgpt"],
        default="public",
        help="Expected public tool profile exposed by the runtime server",
    )
    parser.add_argument(
        "--public-base-url",
        default=DEFAULT_PUBLIC_BASE_URL,
        help="Public base URL used for post-deploy verification",
    )
    parser.add_argument(
        "--expected-tools",
        type=int,
        default=0,
        help="Override minimum public tool count; defaults to the selected public profile contract",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print remote script and exit")

    args = parser.parse_args()

    if args.generate_template:
        generate_railway_template()
        return

    if args.platform == "validate":
        success = asyncio.run(validate_environment())
        sys.exit(0 if success else 1)
    if args.platform == "railway":
        success = deploy_railway()
        sys.exit(0 if success else 1)
    if args.platform == "docker":
        success = deploy_docker()
        sys.exit(0 if success else 1)
    if args.platform == "vps-overlay":
        success = deploy_vps_overlay(args)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
