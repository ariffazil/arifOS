from __future__ import annotations

import subprocess

PUBLIC_DEPLOYMENT_TOOLS = (
    "arif_session_init",
    "arif_sense_observe",
    "arif_mind_reason",
    "arif_heart_critique",
    "arif_ops_measure",
    "arif_judge_deliberate",
    "arif_vault_seal",
)


def normalize_release_version(version: str) -> str:
    year, month, day = version.split(".")
    return f"{int(year):04d}.{int(month):02d}.{int(day):02d}"


def build_overlay_image_tag(version: str, git_sha: str) -> str:
    normalized = normalize_release_version(version)
    return f"arifos/arifosmcp:{normalized}-{git_sha[:8]}"


def deployment_tool_contract(profile: str = "public") -> tuple[int, tuple[str, ...]]:
    return len(PUBLIC_DEPLOYMENT_TOOLS), PUBLIC_DEPLOYMENT_TOOLS


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
    required_tools_csv = ",".join(required_tools)
    return f"""#!/usr/bin/env bash
set -euo pipefail
HOST="{host}"
APP_DIR="{app_dir}"
IMAGE_TAG="{image_tag}"
VERSION="{version}"
GIT_SHA="{git_sha}"
BASE_IMAGE="{base_image}"
CONTAINER_NAME="{container_name}"
CANDIDATE_NAME="{candidate_name}"
CANDIDATE_PORT="{candidate_port}"
ENV_FILE="{env_file}"
PROD_BIND="{prod_bind}"
PUBLIC_HEALTH_URL="{public_base_url}/health"
EXPECTED_TOOLS="{expected_tools}"
REQUIRED_TOOLS="{required_tools_csv}"

docker build \\
  -t "$IMAGE_TAG" \\
  --build-arg ARIFOS_VERSION="$VERSION" \\
  --build-arg ARIFOS_BUILD_SHA="$GIT_SHA" \\
  .

docker inspect "$CONTAINER_NAME" --format '{{{{.State.Status}}}}'
docker run -d --rm --name "$CANDIDATE_NAME" -p "$PROD_BIND" --env-file "$ENV_FILE" "$IMAGE_TAG"
curl -fsS "$PUBLIC_HEALTH_URL"
echo "candidate tool count too low"
echo "public tool count too low"
"""


def run_remote_bash(host: str, script: str):
    normalized = script.replace("\r\n", "\n").encode("utf-8")
    return subprocess.run(
        ["ssh", "-o", "StrictHostKeyChecking=no", host, "/bin/bash", "-s"],
        input=normalized,
        check=False,
    )
