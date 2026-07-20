"""
context_manifest.py — WAJIB 8 Context-Capture Governance (2026-07-19)
═══════════════════════════════════════════════════════════════════════

Enforces that agents cannot self-canonize their output into binding policy.
Every durable agent-authored artifact must carry a context_manifest.
Unapproved policy/constitution class artifacts are rejected at load time.

6 boot-context checks per WAJIB 8 / FORGE-cross-agent-handoff SKILL.md.

Authority: T2 (loader enforcement, no F13 needed — enforcement layer,
not constitutional change).

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# ── Manifest Schema ────────────────────────────────────────────────────────


class ArtifactClass(str, Enum):
    """Artifact class taxonomy per WAJIB 8."""

    OBSERVATION = "observation"
    OPERATIONAL_HANDOFF = "operational_handoff"
    GUIDANCE = "guidance"
    POLICY = "policy"
    CONSTITUTION = "constitution"
    MEMORY = "memory"


class AuthorityLevel(str, Enum):
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"


# Classes that require explicit F13/sovereign approval
_BINDING_CLASSES = frozenset({ArtifactClass.POLICY, ArtifactClass.CONSTITUTION})

# Classes that are always advisory unless approved
_ADVISORY_CLASSES = frozenset(
    {
        ArtifactClass.OBSERVATION,
        ArtifactClass.OPERATIONAL_HANDOFF,
        ArtifactClass.GUIDANCE,
        ArtifactClass.MEMORY,
    }
)


@dataclass
class ContextManifest:
    """Canonical context_manifest per WAJIB 8 schema."""

    artifact_id: str
    class_: ArtifactClass
    author: str
    source_commit: str
    authority_level: AuthorityLevel
    approved_by: str | None
    binding: bool
    created_at: float
    expires_at: float | None
    constitution_compatibility: str
    supersedes: list[str] = field(default_factory=list)
    content_hash: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextManifest:
        return cls(
            artifact_id=str(data.get("artifact_id", "")),
            class_=ArtifactClass(data.get("class", "observation")),
            author=str(data.get("author", "unknown")),
            source_commit=str(data.get("source_commit", "")),
            authority_level=AuthorityLevel(data.get("authority_level", "T1")),
            approved_by=data.get("approved_by"),
            binding=bool(data.get("binding", False)),
            created_at=float(data.get("created_at", time.time())),
            expires_at=float(data["expires_at"]) if data.get("expires_at") else None,
            constitution_compatibility=str(data.get("constitution_compatibility", "")),
            supersedes=list(data.get("supersedes", [])),
            content_hash=str(data.get("content_hash", "")),
        )

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def is_binding_class(self) -> bool:
        return self.class_ in _BINDING_CLASSES

    def requires_approval(self) -> bool:
        return self.is_binding_class() or self.binding


# ── 6 Boot-Context Checks ─────────────────────────────────────────────────


@dataclass
class ManifestVerdict:
    """Result of context_manifest validation."""

    valid: bool
    effective_class: ArtifactClass
    reason: str = ""
    quarantine: bool = False


def validate_manifest(
    manifest: ContextManifest,
    constitution_hash: str = "",
) -> ManifestVerdict:
    """Run the 6 WAJIB 8 boot-context checks on a context_manifest.

    Returns a ManifestVerdict with effective_class (may be downgraded)
    and quarantine flag.
    """
    failures: list[str] = []

    # Check 1: Provenance scan
    if not manifest.artifact_id or not manifest.author:
        failures.append("missing provenance (artifact_id or author)")

    # Check 2: Class matches content intent
    if manifest.class_ not in ArtifactClass:
        failures.append(f"unknown artifact class: {manifest.class_}")

    # Check 3: approved_by required for binding classes
    if manifest.requires_approval() and manifest.approved_by is None:
        failures.append(f"class={manifest.class_.value} requires approved_by, got None")

    # Check 4: Expiry — expired artifacts downgrade to observation
    if manifest.is_expired() and manifest.is_binding_class():
        failures.append(f"expired (created={manifest.created_at}, expires={manifest.expires_at})")

    # Check 5: Constitution compatibility
    if constitution_hash and manifest.constitution_compatibility:
        if manifest.constitution_compatibility != constitution_hash:
            failures.append(
                f"constitution hash mismatch: "
                f"manifest={manifest.constitution_compatibility[:12]}… "
                f"vs live={constitution_hash[:12]}…"
            )

    # Check 6: Content hash (advisory — missing hash warns, doesn't block)
    if not manifest.content_hash:
        failures.append("missing content_hash (advisory only)")

    # ── Compute verdict ──────────────────────────────────────────────
    quarantine = False
    effective_class = manifest.class_

    if not failures:
        return ManifestVerdict(valid=True, effective_class=effective_class)

    # Downgrade rules
    if manifest.is_expired():
        # Expired binding artifacts become observation
        effective_class = ArtifactClass.OBSERVATION
        return ManifestVerdict(
            valid=True,
            effective_class=effective_class,
            reason=f"EXPIRED: downgraded from {manifest.class_.value} → observation. "
            f"{'; '.join(failures)}",
        )

    if manifest.is_binding_class() and manifest.approved_by is None:
        # Unapproved policy/constitution → quarantine
        quarantine = True
        effective_class = ArtifactClass.OBSERVATION
        return ManifestVerdict(
            valid=False,
            effective_class=effective_class,
            reason=f"QUARANTINED: unapproved {manifest.class_.value}. {'; '.join(failures)}",
            quarantine=True,
        )

    if manifest.class_ in _ADVISORY_CLASSES:
        # Advisory classes with minor failures → load as advisory
        return ManifestVerdict(
            valid=True,
            effective_class=effective_class,
            reason=f"ADVISORY ONLY: {'; '.join(failures)}",
        )

    # Unknown failure mode — quarantine
    quarantine = True
    return ManifestVerdict(
        valid=False,
        effective_class=ArtifactClass.OBSERVATION,
        reason=f"QUARANTINED: {'; '.join(failures)}",
        quarantine=True,
    )


# ── Content Hash Helper ───────────────────────────────────────────────────


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 of artifact content for context_manifest.content_hash."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ── Boot Loader Integration ────────────────────────────────────────────────


def scan_artifact_for_manifest(content: str) -> ContextManifest | None:
    """Attempt to extract a context_manifest from artifact content.

    Looks for YAML frontmatter or inline JSON with context_manifest key.
    Returns None if no manifest found (treated as unclassified advisory).
    """
    # Try YAML frontmatter
    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        end_idx = None
        for i in range(1, min(len(lines), 30)):
            if lines[i].strip() == "---":
                end_idx = i
                break
        if end_idx:
            try:
                import yaml

                frontmatter = yaml.safe_load("\n".join(lines[1:end_idx]))
                if isinstance(frontmatter, dict) and "context_manifest" in frontmatter:
                    return ContextManifest.from_dict(frontmatter["context_manifest"])
            except Exception:
                pass

    # Try inline JSON
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "context_manifest" in data:
            return ContextManifest.from_dict(data["context_manifest"])
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def classify_artifact(content: str, constitution_hash: str = "") -> ManifestVerdict:
    """Full artifact classification pipeline.

    1. Scan for context_manifest
    2. If found, validate with 6 boot-context checks
    3. If not found, return UNCLASSIFIED (advisory only)

    Returns ManifestVerdict with loading instructions.
    """
    manifest = scan_artifact_for_manifest(content)
    if manifest is None:
        return ManifestVerdict(
            valid=True,
            effective_class=ArtifactClass.OBSERVATION,
            reason="UNCLASSIFIED: no context_manifest found. Loading as advisory observation only.",
        )

    return validate_manifest(manifest, constitution_hash)
