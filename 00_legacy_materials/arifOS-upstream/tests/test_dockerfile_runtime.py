from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_dockerfile_installs_playwright_browser_deterministically():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright" in dockerfile
    assert "python -m playwright install --with-deps chromium" in dockerfile


def test_canonical_vps_compose_uses_runtime_http_profile():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "dockerfile: Dockerfile" in compose
    assert "ARIFOS_PUBLIC_TOOL_PROFILE: ${ARIFOS_PUBLIC_TOOL_PROFILE:-public}" in compose
    assert "arifosmcp_PATH: ${arifosmcp_PATH:-/mcp}" in compose
    assert "/root/arifosmcp/infrastructure/prometheus/prometheus.yml" in compose
    assert "/root/arifosmcp/infrastructure/deploy_from_git.sh" in compose
    assert "/root/arifosmcp/arifosmcp.transport" not in compose
    assert "condition: service_started" in compose
    assert "exec 3<>/dev/tcp/127.0.0.1/6333" in compose


def test_canonical_vps_env_template_declares_public_profile_and_governance_secret():
    env_template = (ROOT / ".env.docker.example").read_text(encoding="utf-8")

    assert "ARIFOS_GOVERNANCE_SECRET_FILE=/opt/arifos/secrets/governance.secret" in env_template
    assert "ARIFOS_GOVERNANCE_SECRET=" in env_template
    assert "ARIFOS_PUBLIC_TOOL_PROFILE=public" in env_template
    assert "arifosmcp_PATH=/mcp" in env_template
    assert "ARIFOS_PUBLIC_BASE_URL=https://arifosmcp.arif-fazil.com" in env_template
    assert "ARIFOS_WIDGET_DOMAIN=https://arifosmcp.arif-fazil.com" in env_template
