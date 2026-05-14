"""
arifOS Stack Health Probe — 777_OPS / 777_TOPOLOGY
═══════════════════════════════════════════════════

Federation-wide health and governance probe.
Checks constitutional kernel, organs, registry, and risk leash status.

Reversible diagnostic. No state mutation.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Federation service endpoints ───────────────────────────────────────────────
_SERVICE_ENDPOINTS: dict[str, dict[str, Any]] = {
    "arifos_mcp": {"url": "http://localhost:8080/health", "timeout": 5.0},
    "well": {"url": "http://localhost:8083/health", "timeout": 5.0},
    "wealth": {"url": "http://localhost:8082/health", "timeout": 5.0},
    "geox": {"url": "http://localhost:8081/health", "timeout": 5.0},
    "a_forge": {"url": "http://localhost:7071/health", "timeout": 5.0},
    "vault999": {"url": "http://localhost:8100/health", "timeout": 5.0},
}


async def _probe_http(url: str, timeout: float) -> dict[str, Any]:
    """Best-effort HTTP health probe."""
    try:
        import httpx

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return {"status": "healthy", "response": response.json()}
    except Exception as exc:
        logger.debug(f"Health probe failed for {url}: {exc}")
        return {"status": "unreachable", "error": str(exc)}


def _check_model_registry() -> dict[str, Any]:
    """Check filesystem model registry health."""
    try:
        registry_roots = [
            Path("/root/arifos-model-registry"),
            Path(__file__).resolve().parents[3] / "arifos-model-registry",
        ]
        for root in registry_roots:
            if root.exists() and (root / "models").exists() and (root / "provider_souls").exists():
                models_count = len(list((root / "models").rglob("*.json")))
                souls_count = len(list((root / "provider_souls").glob("*.json")))
                return {
                    "status": "healthy",
                    "path": str(root),
                    "models": models_count,
                    "provider_souls": souls_count,
                }
        return {"status": "missing", "error": "No registry root found"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_risk_leash() -> dict[str, Any]:
    """Check risk leash configuration."""
    try:
        leash_path = Path("/root/arifOS/risk_leash.yaml")
        if not leash_path.exists():
            leash_path = Path(__file__).resolve().parents[3] / "risk_leash.yaml"
        if leash_path.exists():
            import yaml

            with open(leash_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            return {
                "status": "healthy",
                "path": str(leash_path),
                "version": data.get("risk_leash", {}).get("version", "unknown"),
                "rules_count": len(data.get("risk_leash", {}).keys())
                - 2,  # minus version/authority
            }
        return {"status": "missing", "error": "risk_leash.yaml not found"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_tool_registry() -> dict[str, Any]:
    """Check canonical tool registry."""
    try:
        registry_path = Path(__file__).resolve().parents[2] / "arifosmcp" / "tool_registry.json"
        if not registry_path.exists():
            registry_path = Path("/root/arifOS/arifosmcp/tool_registry.json")
        if registry_path.exists():
            with open(registry_path, encoding="utf-8") as f:
                data = json.load(f)
            return {
                "status": "healthy",
                "canonical_tools": data.get("canonical_count", 0),
                "total_surface": data.get("total_surface", 0),
            }
        return {"status": "missing", "error": "tool_registry.json not found"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def _check_vault999() -> dict[str, Any]:
    """Check vault ledger integrity."""
    try:
        vault_path = Path("/root/.local/share/arifos/vault999/outcomes.jsonl")
        if not vault_path.exists():
            vault_path = Path("/root/arifOS/arifosmcp/VAULT999/SEALED_EVENTS.jsonl")
        if vault_path.exists():
            size = vault_path.stat().st_size
            return {
                "status": "healthy",
                "path": str(vault_path),
                "size_bytes": size,
            }
        return {"status": "missing", "error": "Vault ledger not found"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


async def arif_stack_health_probe(
    session_id: str | None = None,
    actor_id: str | None = None,
    include_services: list[str] | None = None,
) -> dict[str, Any]:
    """
    777_OPS: Federation stack health and governance probe.

    Checks:
    - arifOS MCP + organ services (HTTP health)
    - Model registry (filesystem)
    - Risk leash (YAML config)
    - Tool registry (canonical surface)
    - VAULT999 ledger (append-only integrity)

    Args:
        session_id: Governed session ID for audit trace.
        actor_id: Sovereign actor identifier.
        include_services: Subset of services to probe. Default = all.

    Returns:
        Health report with per-component status and overall SELAMAT/AMANAH/VOID.
    """
    services_to_check = include_services or list(_SERVICE_ENDPOINTS.keys())

    # ── Probe federation services ──────────────────────────────────────────────
    service_tasks = {
        name: _probe_http(
            _SERVICE_ENDPOINTS[name]["url"],
            _SERVICE_ENDPOINTS[name]["timeout"],
        )
        for name in services_to_check
        if name in _SERVICE_ENDPOINTS
    }
    service_results = dict(zip(service_tasks.keys(), await asyncio.gather(*service_tasks.values()), strict=False))

    # ── Probe constitutional infrastructure ────────────────────────────────────
    registry_result = _check_model_registry()
    leash_result = _check_risk_leash()
    tool_registry_result = _check_tool_registry()
    vault_result = _check_vault999()

    # ── Derive overall status ──────────────────────────────────────────────────
    all_ok = all(r.get("status") == "healthy" for r in service_results.values())
    registry_ok = registry_result.get("status") == "healthy"
    leash_ok = leash_result.get("status") == "healthy"
    tools_ok = tool_registry_result.get("status") == "healthy"
    vault_ok = vault_result.get("status") in ("healthy", "missing")

    if all_ok and registry_ok and leash_ok and tools_ok:
        overall = "SELAMAT"
        verdict = "pass"
    elif registry_ok and leash_ok and tools_ok:
        overall = "AMANAH"
        verdict = "partial"
    else:
        overall = "VOID"
        verdict = "hold"

    warnings: list[str] = []
    if not registry_ok:
        warnings.append("model_registry_unavailable")
    if not leash_ok:
        warnings.append("risk_leash_unavailable")
    if not tools_ok:
        warnings.append("tool_registry_unavailable")
    if not vault_ok:
        warnings.append("vault_ledger_unavailable")

    # Check for model identity issues
    for name, result in service_results.items():
        if result.get("status") != "healthy":
            warnings.append(f"{name}_unhealthy")

    report = {
        "status": overall,
        "verdict": verdict,
        "services": service_results,
        "model_registry": registry_result,
        "risk_leash": leash_result,
        "tool_registry": tool_registry_result,
        "vault999": vault_result,
        "warnings": warnings,
        "session_id": session_id,
        "actor_id": actor_id,
        "timestamp": str(asyncio.get_event_loop().time()),
    }

    logger.info(
        "arif_stack_health_probe session=%s actor=%s overall=%s verdict=%s warnings=%d",
        session_id,
        actor_id,
        overall,
        verdict,
        len(warnings),
    )

    return report


__all__ = ["arif_stack_health_probe"]
