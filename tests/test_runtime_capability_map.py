from __future__ import annotations

import arifosmcp.runtime.capability_map as capability_map_module

from arifosmcp.runtime.capability_map import build_runtime_capability_map


def test_capability_map_reports_file_backed_governance_secret(monkeypatch, tmp_path):
    secret_file = tmp_path / "governance.secret"
    secret_file.write_text("file-backed-secret", encoding="utf-8")

    monkeypatch.delenv("ARIFOS_GOVERNANCE_OPEN_MODE", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_SECRET", raising=False)
    monkeypatch.delenv("ARIFOS_GOVERNANCE_TOKEN_SECRET", raising=False)
    monkeypatch.setenv("ARIFOS_GOVERNANCE_SECRET_FILE", str(secret_file))

    capability_map = build_runtime_capability_map()

    assert capability_map["server_identity"]["continuity_signing"] == "configured"
    assert capability_map["capabilities"]["governed_continuity"] == "enabled"


def test_capability_map_enables_external_grounding_with_ddgs(monkeypatch):
    monkeypatch.delenv("BRAVE_API_KEY", raising=False)
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    monkeypatch.delenv("PPLX_API_KEY", raising=False)
    monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("BROWSERLESS_TOKEN", raising=False)
    monkeypatch.setattr(capability_map_module, "_module_available", lambda name: name == "ddgs")

    capability_map = build_runtime_capability_map()

    assert capability_map["providers"]["ddgs_local"] == "configured"
    assert capability_map["capabilities"]["external_grounding"] == "enabled"
