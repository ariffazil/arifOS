# ruff: noqa: F821
"""
arifosmcp/runtime/model_registry_client.py
==========================================

File-based model registry client. Reads directly from the JSON passport files
mounted at ARIFOS_REGISTRY_ROOT (default: /app/arifos-model-registry).

No HTTP. No separate container. Just a file database.

Wired to:
- arif_session_init (000) — identity verification + APEX gating
- arif_ops_measure (777) — registry health vitals
- arif_stack_health_probe (777) — federation health
- kernel routing — governance posture enforcement

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


# Registry root — ARIFOS_REGISTRY_ROOT env var is authoritative.
# Without it, attempts common deployment locations as best-effort fallbacks.
# Sovereign deployments MUST set ARIFOS_REGISTRY_ROOT for reliable operation.
def _detect_registry_root() -> Path:
    env = os.environ.get("ARIFOS_REGISTRY_ROOT")
    if env:
        root = Path(env)
        if (root / "catalog.json").exists():
            return root
        logger.warning(
            "ARIFOS_REGISTRY_ROOT=%s set but catalog.json not found. "
            "Falling back to common locations.",
            env,
        )
    for candidate in [
        "/root/arifos-model-registry",  # af-forge VPS (production)
        "/app/registry",  # Docker container default
    ]:
        p = Path(candidate)
        if (p / "catalog.json").exists():
            return p
    logger.warning(
        "No model registry found. Set ARIFOS_REGISTRY_ROOT to the path "
        "of your arifos-model-registry clone. See docs/SPINE_CONFIG.md"
    )
    return Path("/app/registry")  # last-resort Docker default


REGISTRY_ROOT = _detect_registry_root()


class ModelRegistryClient:
    """
    File-based registry client. Reads JSON passports directly from disk.

    The registry root contains:
      catalog.json          — master index
      models/               — model passports (provider/family/variant.json)
      provider_souls/       — provider soul files
      runtime_profiles/     — runtime deployment profiles
    """

    def __init__(self, root: Path | str | None = None):
        self.root = Path(root) if root else REGISTRY_ROOT
        self._catalog: dict | None = None
        self._model_cache: dict[str, ModelProfile] = {}
        self._soul_cache: dict[str, ProviderSoul] = {}
        self._runtime_cache: dict[str, RuntimeProfile] = {}

    # ── Low-level file readers ──

    def _read_json(self, rel_path: str) -> dict:
        path = self.root / rel_path
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(f"Failed to read registry file {rel_path}: {exc}")
            return {}

    def _load_catalog(self) -> dict:
        if self._catalog is None:
            self._catalog = self._read_json("catalog.json")
        return self._catalog

    # ── Health ──

    def health(self) -> dict:
        """Check registry health (filesystem access)."""
        try:
            catalog = self._load_catalog()
            models = catalog.get("models", [])
            souls = catalog.get("soul_archetypes", [])
            profiles = catalog.get("runtime_profiles", [])
            return {
                "status": "healthy",
                "version": catalog.get("registry_version", "unknown"),
                "models_count": len(models),
                "souls_count": len(souls),
                "runtime_profiles_count": len(profiles),
                "root": str(self.root),
            }
        except Exception as exc:
            return {"status": "unavailable", "error": str(exc)}

    # ── Model Profile ──

    def _resolve_model_path(self, model_key: str) -> str | None:
        path = f"models/{model_key}.json"
        if (self.root / path).exists():
            return path
        return None

    def get_model_profile(self, model_key: str) -> ModelProfile | None:
        if model_key in self._model_cache:
            return self._model_cache[model_key]
        path = self._resolve_model_path(model_key)
        if path is None:
            return self._fuzzy_find_model(model_key)
        data = self._read_json(path)
        if not data:
            return None
        profile = self._parse_model(data, model_key)
        self._model_cache[model_key] = profile
        return profile

    def _fuzzy_find_model(self, variant: str) -> ModelProfile | None:
        models_dir = self.root / "models"
        if not models_dir.exists():
            return None
        for json_file in models_dir.rglob("*.json"):
            data = self._read_json(str(json_file.relative_to(self.root)))
            if not data:
                continue
            identity = data.get("identity", {})
            if identity.get("variant") == variant or variant in identity.get("aliases", []):
                key = data.get("id", str(json_file.relative_to(self.root)))
                profile = self._parse_model(data, key)
                self._model_cache[key] = profile
                return profile
        return None

    def _parse_model(self, data: dict, model_key: str) -> ModelProfile:
        identity = data.get("identity", {})
        capabilities = data.get("capabilities", {})
        governance = data.get("governance", {})
        lifecycle = data.get("lifecycle", {})
        return ModelProfile(
            provider=identity.get("provider", ""),
            family=identity.get("family", ""),
            variant=identity.get("variant", ""),
            model_key=model_key,
            canonical_model_id=data.get("id", model_key),
            aliases=identity.get("aliases", []),
            status=lifecycle.get("status", "unknown"),
            evidence_tier=lifecycle.get("evidence_tier", "unknown"),
            soul_archetype=identity.get("soul_key", ""),
            runtime_class=identity.get("runtime_class", ""),
            capabilities=capabilities if isinstance(capabilities, dict) else {},
            governance_posture=governance if isinstance(governance, dict) else {},
            identity_integrity={},
            lifecycle=lifecycle if isinstance(lifecycle, dict) else {},
            apex={
                "apex_composite": governance.get("apex_score"),
                "amanah_score": governance.get("amanah_score"),
            },
            sources=data.get("sources", []),
            notes=data.get("notes", ""),
            raw=data,
        )

    def get_provider_soul(self, soul_key: str) -> ProviderSoul | None:
        """Get provider soul by key (filename without .json)."""
        if soul_key in self._soul_cache:
            return self._soul_cache[soul_key]

        # Try exact filename
        data = self._read_json(f"provider_souls/{soul_key}.json")
        if not data:
            # Try by provider_key matching
            data = self._find_soul_by_provider_key(soul_key)
        if not data:
            return None

        soul = ProviderSoul(
            soul_key=soul_key,
            provider_name=data.get("provider_key", soul_key),
            soul_label=data.get("soul_label", ""),
            archetype=data.get("soul_label", ""),
            origin=data.get("origin", ""),
            governance=data.get("governance", ""),
            character_summary=data.get("character_summary", ""),
            in_one_sentence=data.get("in_one_sentence", ""),
            constitutional_alignment=data.get("constitutional_alignment", {}),
            default_behavior=data.get("default_behavior", {}),
        )
        self._soul_cache[soul_key] = soul
        return soul

    def _find_soul_by_provider_key(self, provider_key: str) -> dict:
        """Fuzzy match provider soul by provider_key field."""
        souls_dir = self.root / "provider_souls"
        if not souls_dir.exists():
            return {}
        for json_file in souls_dir.glob("*.json"):
            data = self._read_json(str(json_file.relative_to(self.root)))
            if data.get("provider_key") == provider_key:
                return data
        return {}

    # ── Runtime Profile ──

    def get_runtime_profile(self, deployment_id: str) -> RuntimeProfile | None:
        """Get runtime profile by deployment ID."""
        if deployment_id in self._runtime_cache:
            return self._runtime_cache[deployment_id]

        data = self._read_json(f"runtime_profiles/{deployment_id}.json")
        if not data:
            return None

        cap = data.get("capabilities", {})
        boundary = data.get("self_claim_boundary", {})
        profile = RuntimeProfile(
            deployment_id=data.get("deployment_id", deployment_id),
            provider_key=data.get("provider_key", ""),
            family_key=data.get("family_key", ""),
            model_id=data.get("model_id", ""),
            routing_mode=data.get("routing_mode", "direct"),
            tools_live=data.get("tools_live", []),
            web_on=data.get("web_on", False),
            memory_mode=data.get("memory_mode", "session_only"),
            execution_mode=data.get("execution_mode", "governed"),
            side_effects_allowed=data.get("side_effects_allowed", False),
            auth_level=data.get("auth_level", ""),
            capabilities=cap if isinstance(cap, dict) else {},
            self_claim_boundary=boundary if isinstance(boundary, dict) else {},
            notes=data.get("notes", ""),
        )
        self._runtime_cache[deployment_id] = profile
        return profile

    # ── Identity Verification (L11 grounding) ──

    def verify_identity(
        self, claimed_identity: str, claimed_provider: str | None = None
    ) -> IdentityVerification:
        """
        Verify a model's claimed identity against the canonical registry.

        Steps:
          1. Look up model passport
          2. Check status — reject speculative
          3. Check provider match if claimed
          4. Return full verification with APEX scores + governance posture
        """
        profile = self.get_model_profile(claimed_identity)
        if profile is None:
            return IdentityVerification(
                verified=False,
                declared=claimed_identity,
                matched_key=None,
                model=None,
                mismatch_detected=True,
                drift_risk="high",
                block_reason="model not found in registry",
            )

        # Check status — reject speculative
        if profile.is_speculative:
            return IdentityVerification(
                verified=False,
                declared=claimed_identity,
                matched_key=profile.model_key,
                model=profile.raw,
                mismatch_detected=True,
                drift_risk="high",
                status=profile.status,
                evidence_tier=profile.evidence_tier,
                block_reason="model is speculative — not grounded in production attestation",
            )

        # Check provider match
        provider_mismatch = False
        if claimed_provider and profile.provider != claimed_provider:
            provider_mismatch = True

        # Determine drift risk
        if profile.evidence_tier in ("official_doc", "official_blog"):
            drift_risk = "low"
        elif profile.evidence_tier == "provider_api":
            drift_risk = "medium"
        elif profile.evidence_tier == "third_party_report":
            drift_risk = "moderate"
        elif profile.evidence_tier == "self_asserted":
            drift_risk = "high"
        else:
            drift_risk = "unknown"

        block_reason = None
        if provider_mismatch:
            block_reason = (
                f"provider mismatch: claimed '{claimed_provider}', "
                f"registry has '{profile.provider}'"
            )

        return IdentityVerification(
            verified=not provider_mismatch,
            declared=claimed_identity,
            matched_key=profile.model_key,
            model=profile.raw,
            mismatch_detected=provider_mismatch,
            drift_risk=drift_risk,
            status=profile.status,
            evidence_tier=profile.evidence_tier,
            amanah_score=profile.amanah_score,
            apex_composite=profile.apex_composite,
            governance_posture=profile.governance_posture,
            block_reason=block_reason,
        )

    # ── Listing ──

    def list_models(self) -> list[str]:
        """List all registered model keys from catalog."""
        catalog = self._load_catalog()
        models = catalog.get("models", [])
        if isinstance(models, list):
            return [
                m if isinstance(m, str) else m.get("canonical_model_id", str(m)) for m in models
            ]
        return list(models.keys()) if isinstance(models, dict) else []

    def list_providers(self) -> list[str]:
        """List all registered provider soul keys from catalog."""
        catalog = self._load_catalog()
        return catalog.get("soul_archetypes", [])

    def list_runtime_profiles(self) -> list[str]:
        """List all runtime profile deployment IDs."""
        rp_dir = self.root / "runtime_profiles"
        if not rp_dir.exists():
            return []
        return sorted([f.stem for f in rp_dir.glob("*.json")])

    def get_catalog(self) -> dict:
        """Get the full registry catalog."""
        return self._load_catalog()


# ═══════════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════════

_registry_client: ModelRegistryClient | None = None


def get_model_registry_client() -> ModelRegistryClient:
    """Get or create the singleton model registry client."""
    global _registry_client
    if _registry_client is None:
        _registry_client = ModelRegistryClient()
    return _registry_client


async def verify_model_identity(
    claimed_identity: str,
    claimed_provider: str | None = None,
) -> IdentityVerification:
    """
    Convenience function for L11 identity verification.

    Usage:
        result = await verify_model_identity("claude-sonnet-4", "anthropic")
        if result.verified:
            print(f"APEX: {result.apex_composite}, AMANAH: {result.amanah_score}")
        if result.status == "speculative":
            print(f"REJECTED: {result.block_reason}")
    """
    client = get_model_registry_client()
    return client.verify_identity(claimed_identity, claimed_provider)
