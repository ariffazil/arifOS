from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "deploy_production.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("deploy_production", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_normalize_release_version_pads_month_and_day():
    module = _load_module()
    assert module.normalize_release_version("2026.2.28") == "2026.02.28"
    assert module.normalize_release_version("2026.12.3") == "2026.12.03"


def test_build_overlay_image_tag_uses_normalized_version_and_short_sha():
    module = _load_module()
    tag = module.build_overlay_image_tag("2026.2.28", "527f8e18abcd")
    assert tag == "arifos/arifosmcp:2026.02.28-527f8e18"


def test_build_vps_overlay_script_contains_full_build_and_mount_check():
    module = _load_module()
    script = module.build_vps_overlay_script(
        host="root@example.com",
        app_dir="/root/arifOS",
        image_tag="arifos/arifosmcp:2026.02.28-527f8e18",
        version="2026.02.28",
        git_sha="527f8e18",
        base_image="arifos/arifosmcp:latest",
        container_name="arifosmcp",
        candidate_name="arifosmcp_candidate_overlay",
        candidate_port=18089,
        env_file=".env.docker",
        prod_bind="127.0.0.1:8088:8080",
        public_base_url="https://arifosmcp.arif-fazil.com",
        expected_tools=7,
        required_tools=module.PUBLIC_DEPLOYMENT_TOOLS,
    )

    assert "docker build \\" in script
    assert '-t "$IMAGE_TAG" \\' in script
    assert '--build-arg ARIFOS_VERSION="$VERSION" \\' in script
    assert 'docker inspect "$CONTAINER_NAME" --format' in script
    assert "candidate tool count too low" in script
    assert "public tool count too low" in script
    assert 'curl -fsS "$PUBLIC_HEALTH_URL"' in script
    assert "Dockerfile.deploy-overlay" not in script


def test_deployment_tool_contract_matches_public_runtime_surface():
    module = _load_module()

    count, tools = module.deployment_tool_contract("public")

    assert count == len(module.PUBLIC_DEPLOYMENT_TOOLS)
    assert tools == module.PUBLIC_DEPLOYMENT_TOOLS


def test_run_remote_bash_normalizes_crlf_and_uses_bytes(monkeypatch):
    module = _load_module()
    recorded: dict[str, object] = {}

    class _Result:
        returncode = 0

    def _fake_run(cmd, input=None, **kwargs):
        recorded["cmd"] = cmd
        recorded["input"] = input
        recorded["kwargs"] = kwargs
        return _Result()

    monkeypatch.setattr(module.subprocess, "run", _fake_run)

    result = module.run_remote_bash("root@example.com", "set -euo pipefail\r\nprintf 'ok'\r\n")

    assert result.returncode == 0
    assert recorded["cmd"] == [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "root@example.com",
        "/bin/bash",
        "-s",
    ]
    assert recorded["input"] == b"set -euo pipefail\nprintf 'ok'\n"
    assert "text" not in recorded["kwargs"]
