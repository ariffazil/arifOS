"""Build information for arifOS MCP Server.

Single SoT: doctrine, Floors, and architecture live in ariffazil/arifOS.
This module provides runtime traceability back to that canonical repo.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arifosmcp.canon import canon_attestation, canon_manifest
from arifosmcp.runtime.DNA import VERSION as DNA_VERSION

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = ROOT / "pyproject.toml"
PROCESS_STARTED_AT = datetime.now(UTC).isoformat()

_CRITICAL_MODULES = (
    "arifosmcp/tools/session.py",
    "arifosmcp/runtime/crypto_auth.py",
    "arifosmcp/runtime/convergence_tracker.py",
    "arifosmcp/runtime/cooling_verbs.py",
    "arifosmcp/runtime/forge_session_runtime.py",
    "arifosmcp/runtime/governance_identity.py",
    "arifosmcp/runtime/rest_routes/rest_routes.py",
    # T3a Item 3 (2026-07-17): server-side BOOT attestation — the gate that
    # refuses authority-grade bands when the kernel cannot prove its own
    # integrity. Fail-closed by design.
    "arifosmcp/runtime/boot_attestation.py",
    # BANGANG P0 FIX (2026-07-19): authority computation + governance gate chain.
    # interceptor.py was hot-patched without the attestation hash moving — a
    # change to the most security-critical component was invisible to boot
    # attestation. Added by Fable's re-probe finding. Also covers authority.py
    # (authority state read), phoenix_72.py (tri-witness with positional debt),
    # and governance_pipeline.py (GateResult cryptographic hashing).
    "arifosmcp/kernel/interceptor.py",
    "arifosmcp/runtime/authority.py",
    "arifosmcp/runtime/phoenix_72.py",
    "arifosmcp/runtime/governance_pipeline.py",
    # P0 ADVERSARIAL FIXES (2026-07-25): Ed25519 forge gate, empty evidence
    # BLOCK, evidence_receipt passthrough, F13 ordering. Hot-patched by
    # Fable5's adversarial spec — now source-sealed and runtime-attested.
    "arifosmcp/runtime/forge_preflight.py",
    "arifosmcp/runtime/kernel/judge.py",
    "arifosmcp/tools/forge.py",
    "arifosmcp/tools/judge.py",
    # FHS canon plane (2026-09-16): /etc/arifos/canon resolution is an
    # authority path — a silent swap here would redefine ratified policy.
    "arifosmcp/canon.py",
    "arifosmcp/memory/admissibility.py",
)


def _sha256_file(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except (OSError, PermissionError):
        return None


DEPLOYED_COMMIT_STAMP = Path("/opt/arifos/releases/deployed-commit")
_LEGACY_APP_STAMP = Path("/opt/arifos/app/.git_commit")
_REPO_COMMIT_STAMP = Path("/root/arifOS/.git_commit")


def _read_commit_stamp() -> str:
    """Deployed commit: stable release stamp → legacy app stamp → repo stamp."""
    for stamp in (DEPLOYED_COMMIT_STAMP, _LEGACY_APP_STAMP, _REPO_COMMIT_STAMP):
        try:
            value = stamp.read_text().strip()
            if len(value) >= 7:
                return value
        except OSError:
            pass
    return "unknown"


def _full_source_commit() -> str:
    """Return the source commit that produced the running binary.

    Priority: deployed-commit stamp (what was actually built and deployed)
    → release manifest git_commit → git HEAD (working directory).
    Git HEAD is LAST because the working directory may be on a different
    branch than what was deployed (e.g. test branches), causing false
    drift detection in get_runtime_attestation().
    """
    # 1. Deployed commit stamp — written by deploy-release.sh at deploy time
    value = _read_commit_stamp()
    if value != "unknown":
        return value
    # 2. Release manifest
    release_manifest = Path("/opt/arifos/releases/release-manifest.json")
    if release_manifest.exists():
        try:
            data = json.loads(release_manifest.read_text())
            commit = data.get("git_commit")
            if commit and len(commit) >= 7:
                return commit
        except Exception:
            pass
    # 3. Git HEAD — last resort (may be on wrong branch)
    git_head = Path("/root/arifOS/.git/HEAD")
    try:
        value = git_head.read_text().strip()
        if value.startswith("ref: "):
            ref = Path("/root/arifOS/.git") / value[5:]
            if ref.exists():
                return ref.read_text().strip()
        if len(value) >= 7:
            return value
    except OSError:
        pass
    return "unknown"


def _full_deployed_commit() -> str:
    """Return the deployed commit SHA (release stamp → legacy app stamp)."""
    return _read_commit_stamp()


def _full_built_commit() -> str:
    """Return the built commit SHA from installed release manifest."""
    env_commit = os.getenv("ARIFOS_BUILT_COMMIT", "").strip()
    if env_commit:
        return env_commit
    release_manifest = Path("/opt/arifos/releases/release-manifest.json")
    if release_manifest.exists():
        try:
            data = json.loads(release_manifest.read_text())
            commit = data.get("git_commit")
            if commit and len(commit) >= 7:
                return commit
        except Exception:
            pass
    return _full_deployed_commit()


def _installation_manifest_hash() -> str | None:
    """Hash the installed distribution RECORD (the reproducible install manifest)."""
    candidates = sorted(
        Path("/opt/arifos/venv/lib").glob(
            "python*/site-packages/arifos-*.dist-info/RECORD"
        )
    )
    return _sha256_file(candidates[-1]) if candidates else None


def _read_git_head(git_dir: str) -> str:
    """Read the current HEAD commit from a git repository."""
    try:
        head_path = Path(git_dir) / "HEAD"
        if not head_path.exists():
            return "unknown"
        content = head_path.read_text().strip()
        if content.startswith("ref: "):
            ref_path = Path(git_dir) / content[5:]
            if ref_path.exists():
                return ref_path.read_text().strip()
        if len(content) >= 7:
            return content
    except OSError:
        pass
    return "unknown"


def _compute_tool_surface_hash() -> str:
    """Hash the canonical public tool schemas for surface integrity verification.

    Hashes the tools the public wire actually lists and accepts — the
    constitutional verbs for the active mode plus the coordination channels.
    Measured 2026-10-29: this covered only the 8 constitutional tools while the
    public `tools/list` exposed 14, so the six coordination tools could be added
    or removed without moving the hash.
    """
    try:
        from arifosmcp.runtime.public_surface import public_exposed_tool_names

        schemas: dict[str, Any] = {}
        for name in sorted(public_exposed_tool_names()):
            schemas[name] = {"name": name}
        raw = json.dumps(schemas, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()
    except Exception:
        return "unavailable"


ACTIVE_VENV_ROOT = os.environ.get("ARIFOS_ACTIVE_VENV_ROOT", "/opt/arifos/current/venv")


def _runtime_origin() -> str:
    """Physical import origin of the live arifosmcp package (ONE_ORIGIN axis A)."""
    try:
        import arifosmcp

        return str(Path(arifosmcp.__file__).resolve())
    except Exception:
        return "unknown"


def _origin_ok() -> bool:
    """True when the live package origin is the active release venv (wheel origin).

    Enforcement is opt-in via ARIFOS_ENFORCE_ORIGIN=1 (set by the production
    unit drop-in) so dev checkouts and test environments never false-drift.
    """
    if os.getenv("ARIFOS_ENFORCE_ORIGIN", "").strip() != "1":
        return True
    origin = _runtime_origin()
    return origin != "unknown" and origin.startswith(
        str(Path(ACTIVE_VENV_ROOT).resolve()) + "/"
    )


def _git_blob_sha1(data: bytes) -> str:
    """Git object SHA-1 of a blob: sha1(b'blob <size>\\0' + data)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _content_parity(
    source_commit: str,
    *,
    package_root: Path | None = None,
    repo_path: Path | None = None,
) -> dict[str, Any]:
    """CONTENT-PARITY (2026-11-03): installed BYTES vs the committed tree.

    Stamps can agree while bytes diverge. Measured 2026-11-03 on the live box:
    built==deployed==source==f26af25 and drift=false, while the running package
    held 2 modified files + 7 files with NO git history at all — a false
    negative, because drift compares SHAs, never content.

    Method: git blob SHA-1 of every *.py under the installed package vs
    `git ls-tree -r <source_commit> arifosmcp`.

    Fail-closed by law: any error (unknown commit, unreadable file, git
    unavailable) returns state=UNKNOWN — absent/unchecked is NEVER MATCH.
    Always measured; flips `drift` only under ARIFOS_CONTENT_PARITY_ENFORCE=1.
    """
    root = package_root
    if root is None:
        root_override = os.getenv("ARIFOS_PACKAGE_ROOT", "").strip()
        if root_override:
            root = Path(root_override)
        else:
            try:
                import arifosmcp as _pkg

                root = Path(_pkg.__file__).resolve().parent
            except Exception:
                root = Path(__file__).resolve().parents[1]
    repo = Path(repo_path or os.getenv("ARIFOS_REPO_PATH", "/root/arifOS"))
    out: dict[str, Any] = {
        "state": "UNKNOWN",
        "method": "git_blob_sha1_vs_ls-tree",
        "package_root": str(root),
        "repo": str(repo),
        "commit": source_commit,
        "files_compared": 0,
        "files_changed": 0,
        "files_untracked": 0,
        "files_missing": 0,
        "sample_changed": [],
        "sample_untracked": [],
        "sample_missing": [],
        "reason": None,
    }
    if not source_commit or source_commit == "unknown":
        out["reason"] = "source_commit unknown — cannot compare"
        return out
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", "-r", source_commit, "arifosmcp"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:  # git missing/timeout
        out["reason"] = f"git unavailable: {type(exc).__name__}"
        return out
    if proc.returncode != 0:
        out["reason"] = f"ls-tree failed rc={proc.returncode}"
        return out
    committed: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        try:
            meta, path = line.split("\t", 1)
            sha = meta.split()[2]
        except (ValueError, IndexError):
            continue
        if path.endswith(".py"):
            committed[path] = sha
    if not committed:
        out["reason"] = "commit resolves but holds no arifosmcp/*.py"
        return out
    local: dict[str, str] = {}
    try:
        for path in sorted(Path(root).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = "arifosmcp/" + str(path.relative_to(root))
            local[rel] = _git_blob_sha1(path.read_bytes())
    except OSError as exc:
        out["reason"] = f"unreadable package file: {type(exc).__name__}"
        return out
    changed = sorted(p for p in local if p in committed and committed[p] != local[p])
    untracked = sorted(p for p in local if p not in committed)
    missing = sorted(p for p in committed if p not in local)
    out.update(
        files_compared=len(local),
        files_changed=len(changed),
        files_untracked=len(untracked),
        files_missing=len(missing),
        sample_changed=changed[:8],
        sample_untracked=untracked[:8],
        sample_missing=missing[:8],
    )
    out["state"] = "MISMATCH" if (changed or untracked or missing) else "MATCH"
    return out


def get_runtime_attestation(*, detail: bool = False) -> dict[str, Any]:
    """Public, machine-readable binding from release to this live process.

    KUTIP SAMPAH M5 (2026-08-05): default is compact — hash manifest + drift only.
    Full critical_module_hashes and prose semantics available with detail=True
    (or /health?detail=1). Target success payload tax < 2 KB on compact path.
    """
    source_commit = _full_source_commit()
    deployed_commit = _full_deployed_commit()
    built_commit = _full_built_commit()

    critical_module_hashes = {
        rel: digest
        for rel in _CRITICAL_MODULES
        if (digest := _sha256_file(ROOT / rel)) is not None
    }
    wheel_hash = (
        os.getenv("ARIFOS_WHEEL_SHA256", "").strip() or _installation_manifest_hash()
    )
    manifest = {
        "source_commit": source_commit,
        "wheel_hash": wheel_hash,
        "critical_module_hashes": critical_module_hashes,
    }
    runtime_manifest_hash = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    )

    # Truthful drift calculation:
    # Drift is True if source repo HEAD != deployed code stamp,
    # or if built package metadata != deployed code stamp.
    drift = False
    if source_commit != "unknown" and deployed_commit != "unknown":
        if not (
            source_commit.startswith(deployed_commit[:7])
            or deployed_commit.startswith(source_commit[:7])
        ):
            drift = True
    if built_commit != "unknown" and deployed_commit != "unknown":
        if not (
            built_commit.startswith(deployed_commit[:7])
            or deployed_commit.startswith(built_commit[:7])
        ):
            drift = True

    # ONE_ORIGIN (2026-09-16): drift must also fire when the live package
    # origin is not the active release venv — the runtime executing from any
    # other tree (cwd shadow, editable finder, stale app copy) is drift,
    # whatever the stamps say.
    runtime_import_path = _runtime_origin()
    origin_ok = _origin_ok()
    if not origin_ok:
        drift = True

    # P1-5 (repair-2026-11-01, audit D1): identity rendered FROM the canonical
    # identity source (single source). Replaces the inline git probe that
    # derived the repo from the IMPORT location (live kernel in
    # site-packages got repo=null) and WIDENS detection per the audit:
    #   drift_scope = binary_build_stamps + repo_head_vs_deployed +
    #                 stamp_reachability (orphaned pre-rewrite stamps).
    # T3b's repo delta stays visible as its own fields.
    try:
        from arifosmcp.runtime.deployment_identity import (
            canonical_identity as _canonical_identity,
        )

        _ident_src = _canonical_identity()
    except Exception:  # noqa: BLE001 — attestation must never raise
        _ident_src = {}
    repo_head_commit = _ident_src.get("repo_head_commit")
    _ident_drift = _ident_src.get("drift") or {}
    repo_head_in_sync = _ident_drift.get("in_sync")
    _identity_drift = bool(_ident_drift.get("identity_drift"))
    _repo_gap = _ident_src.get("repo_gap") or {}
    _deployed_reachable = _ident_src.get("deployed_reachable")
    # WIDENED (D1): repo-vs-deployed divergence and unreachable stamps are
    # identity drift — drift now reflects them, scope declares the full set.
    if _identity_drift:
        drift = True

    # CONTENT-PARITY (2026-11-03): stamp agreement ≠ byte agreement. Measured
    # false negative: built==deployed==source==f26af25 + drift=false while the
    # running package held 2 modified + 7 never-committed files. Always
    # MEASURED here; it flips `drift` only when F13 turns the switch on —
    # enforcement would immediately clamp today's box (content MISMATCH is the
    # current measured state), so it stays off until sovereign decision.
    content_parity = _content_parity(source_commit)
    _content_enforced = os.getenv("ARIFOS_CONTENT_PARITY_ENFORCE", "").strip() == "1"
    if _content_enforced and content_parity.get("state") == "MISMATCH":
        drift = True

    surface_hash = _compute_tool_surface_hash()

    release_id = os.getenv("ARIFOS_RELEASE_ID", "").strip() or (
        f"arifos-{source_commit[:12]}" if source_commit != "unknown" else "unknown"
    )
    compact = {
        "release_id": release_id,
        "source_commit": source_commit,
        "built_commit": built_commit,
        "deployed_commit": deployed_commit,
        "drift": drift,
        # P1-5 widened (2026-11-01, audit D1): drift now ALSO covers
        # repo HEAD vs deployed + deploy-stamp reachability.
        "drift_scope": (
            "binary_build_stamps+repo_head_vs_deployed+stamp_reachability+content_hash"
            if _content_enforced
            else "binary_build_stamps+repo_head_vs_deployed+stamp_reachability"
            "(content_hash=measured_only)"
        ),
        # CONTENT-PARITY (2026-11-03): bytes-vs-commit verdict, always measured.
        "content_parity": content_parity,
        "content_parity_enforced": _content_enforced,
        "repo_head_commit": repo_head_commit,
        "repo_head_in_sync": repo_head_in_sync,
        "repo_gap": _repo_gap,  # P1-5: both-direction commit counts
        "deployed_reachable": _deployed_reachable,  # P1-5: orphan-stamp detector
        "identity_drift": _identity_drift,
        "wheel_hash": wheel_hash,
        "runtime_manifest_hash": runtime_manifest_hash,
        "surface_hash": surface_hash,
        "canon": canon_attestation(),
        "runtime_import_path": runtime_import_path,
        "origin_ok": origin_ok,
        "active_venv_root": ACTIVE_VENV_ROOT,
        "origin_enforced": os.getenv("ARIFOS_ENFORCE_ORIGIN", "").strip() == "1",
        "service_pid": os.getpid(),
        "service_started_at": PROCESS_STARTED_AT,
        "critical_module_hash_count": len(critical_module_hashes),
        "payload_mode": "compact",
        # F2 TRUTH fix 2026-10-16: explicit semantic labels so a consumer
        # can disambiguate software_release.* from vps_snapshot.organ_shas.*
        # without a separate docs read. Audit ticket: arif_init_source_commit
        # labelling. Without _field_semantics, the field names alone cannot
        # distinguish deployed-binary source from a VPS snapshot of repo HEAD.
        "_field_semantics": {
            "drift": (
                "True when any ENFORCED attested dimension diverges. The SHA/stamp "
                "dimensions are always enforced; the content_hash dimension is "
                "MEASURED always but enforced only under "
                "ARIFOS_CONTENT_PARITY_ENFORCE=1 (default off — enforcement would "
                "currently clamp the box; measured content MISMATCH on 2026-11-03). "
                "While enforcement is off, drift=false must NOT be read as "
                "'running bytes == committed bytes' — check content_parity."
            ),
            "content_parity": (
                "Git-blob-SHA1 comparison of every *.py in the installed package "
                "against `git ls-tree -r source_commit`. MATCH = bytes equal the "
                "commit; MISMATCH = modified/untracked/missing files present "
                "(sample_* lists them); UNKNOWN = the check could not run "
                "(unknown commit, unreadable file, git unavailable) and is NEVER "
                "to be read as MATCH."
            ),
            "release_id": (
                "Human-readable identifier combining product and source SHA prefix. "
                "Equals arifos-{source_commit[:12]} when source is known."
            ),
            "source_commit": (
                "Git SHA of the source tree at the moment this deployed binary was "
                "BUILT. This is the deployed-binary source SHA, NOT the live "
                "repository HEAD — those may differ. Compare against "
                "vps_snapshot.organ_shas.arifos for the live repo HEAD."
            ),
            "built_commit": (
                "Git SHA recorded in the wheel's RECORD.json / build manifest. "
                "Equals source_commit on a clean build."
            ),
            "deployed_commit": (
                "Git SHA stamped into the runtime at package install time. "
                "Should equal source_commit and built_commit on a clean deployment. "
                "drift=true means one or more of these three SHAs diverge — a "
                "SHA-only statement; byte-level coverage lives in content_parity."
            ),
            "wheel_hash": (
                "SHA-256 of the installed wheel when ARIFOS_WHEEL_SHA256 is set; "
                "otherwise hash of the installation RECORD. Verifies the wheel "
                "bytes on disk match what was attested at build time."
            ),
            "runtime_manifest_hash": (
                "SHA-256 of the {source_commit, wheel_hash, critical_module_hashes} "
                "manifest. Binds release identity to specific bytes."
            ),
            "surface_hash": (
                "SHA-256 of the registered tool-surface schema. Detects schema "
                "drift even when source/deployed SHAs match."
            ),
            "canon": (
                "Active constitutional canon attestation. Independent of source "
                "commits — the constitution is signed canon, not a build artifact."
            ),
            "runtime_import_path": (
                "Filesystem path the live interpreter imported arifosmcp from. "
                "origin_ok=true means it lives under active_venv_root."
            ),
        },
    }
    if not detail:
        return compact
    return {
        **compact,
        "payload_mode": "detail",
        "critical_module_hashes": critical_module_hashes,
        "deployment_invariant": {
            "rule": "source_commit == built_commit == deployed_commit == health_commit AND runtime origin == active venv",
            "source_commit": source_commit,
            "built_commit": built_commit,
            "deployed_commit": deployed_commit,
            "runtime_import_path": runtime_import_path,
            "origin_ok": origin_ok,
            "drift": drift,
            "note": "Deployment must refuse to report healthy when drift is true.",
        },
        "attestation_semantics": {
            "kernel_epoch": "constitutional/protocol epoch; not a software build date",
            "wheel_hash": "ARIFOS_WHEEL_SHA256 when injected, otherwise installed RECORD hash",
        },
    }


def _git_sha_short() -> str:
    """
    1. Native Bare-Metal deployment stamp (.git_commit) — HIGHEST PRIORITY
    2. DEPLOY_GIT_COMMIT env var (baked into image at docker build time)
    3. ARIFOS_BUILD_SHA env var (passed at container start)
    4. Canonical repo .git/HEAD fallback
    5. Fallback "unknown"
    """
    # 1. Native Bare-Metal deployment stamp (highest priority: deployed-commit → legacy app → repo)
    _stamp = _read_commit_stamp()
    if _stamp != "unknown":
        return _stamp[:7]

    # 2. Image-baked env (legacy docker)
    for env_key in ("DEPLOY_GIT_COMMIT", "ARIFOS_BUILD_SHA", "GIT_SHA", "GIT_COMMIT"):
        env_sha = os.environ.get(env_key, "").strip()
        if env_sha and env_sha not in ("unknown", ""):
            return env_sha[:7]

    # 3. Try reading .git/HEAD from known bind-mount paths (fallback)
    _possible_git_dirs = [
        "/root/arifOS/.git",  # ← Canonical source repo on this VPS
        "/app/.git",  # ← Generic fallback (WELL repo)
        "/usr/src/app/.git",
        "/usr/src/app/arifOS/.git",
        "/usr/src/project/.git",
    ]

    # Explicit identity markers — prevents Grok/AAA-APEX ↔ legacy OpenClaw context bleed

    for _git_dir in _possible_git_dirs:
        try:
            _head_path = os.path.join(_git_dir, "HEAD")
            if os.path.exists(_head_path):
                with open(_head_path) as _f:
                    _content = _f.read().strip()
                if _content.startswith("ref: refs/heads/"):
                    _branch = _content.split("ref: refs/heads/", 1)[1].strip()
                    _ref_path = os.path.join(_git_dir, "refs", "heads", _branch)
                    if os.path.exists(_ref_path):
                        with open(_ref_path) as _f:
                            _sha = _f.read().strip()
                        return _sha[:7]
                elif len(_content) >= 7:
                    return _content[:7]
        except Exception:
            pass

    # 4. Truthful final fallback
    return "unknown"


def _image_tag() -> str:
    """Resolve container image tag from env vars.

    NOTE: Returns a ghcr.io image tag regardless of whether the runtime is
    actually a container. Use _detect_deployment_mode() to determine if the
    image tag is meaningful (only true when deployment_source == "container").
    The ghcr.io image is built and pushed for portability/rollback purposes
    but the canonical production runtime on VPS af-forge is NATIVE bare-metal
    (see make deploy-local).
    """
    for key in ("ARIFOS_IMAGE", "DEPLOY_IMAGE", "IMAGE_TAG"):
        val = os.environ.get(key, "").strip()
        if val and val not in ("unknown", "", "not-injected"):
            return val
    commit = _git_sha_short()
    if commit and commit not in ("unknown", "not-injected"):
        return f"ghcr.io/ariffazil/arifos:{commit}"
    return "not-injected"


def _detect_deployment_mode() -> str:
    """Detect actual runtime deployment mode at process startup.

    Determines whether the arifOS process is running inside a container
    (Docker / Kubernetes / LXC / containerd) or natively on bare-metal.

    Detection priority (highest first):
        1. ``/.dockerenv`` file existence — definitive for Docker
        2. ``/proc/1/cgroup`` containing docker/kubepods/lxc/containerd
           patterns — definitive for Kubernetes, LXC, containerd
        3. ``DEPLOY`` env var explicitly set to ``"container"`` — opt-in
        4. Default: ``"native"``

    Returns:
        ``"container"`` if running inside a container, ``"native"`` otherwise.

    F2 TRUTH: Health endpoint ``deployment_source`` MUST reflect this value,
    not a hardcoded string. The federation root cannot lie about its own
    runtime state (FORGE audit 2026-06-27).
    """
    # 1. .dockerenv file — definitive for Docker
    if os.path.exists("/.dockerenv"):
        return "container"

    # 2. cgroup inspection — kubepods/lxc/docker/containerd patterns
    try:
        cgroup_path = Path("/proc/1/cgroup")
        if cgroup_path.exists():
            cgroup = cgroup_path.read_text(errors="replace")
            if any(
                token in cgroup
                for token in ("docker-", "kubepods", "/lxc/", "containerd-")
            ):
                return "container"
    except (FileNotFoundError, PermissionError, OSError):
        pass

    # 3. Explicit env override — opt-in container declaration
    deploy_env = os.environ.get("DEPLOY", "").strip().lower()
    if deploy_env == "container":
        return "container"

    # 4. Default — native bare-metal
    return "native"


# Module-level cache — detection is cheap but called on every /health hit.
# Result is process-stable (cgroup + /.dockerenv cannot change at runtime).
_DEPLOYMENT_MODE: str = _detect_deployment_mode()


def get_deployment_mode() -> str:
    """Public accessor for cached deployment mode detection.

    Returns:
        ``"container"`` or ``"native"``.
    """
    return _DEPLOYMENT_MODE


def _build_time() -> str:
    """Resolve build timestamp from env vars."""
    for key in ("ARIFOS_BUILD_TIME", "BUILD_TIME", "DEPLOY_BUILD_TIME"):
        val = os.environ.get(key, "").strip()
        if val and val not in ("unknown", "", "not-injected"):
            return val
    return datetime.now(UTC).isoformat()


def _pyproject_version() -> str:
    dna_version = str(DNA_VERSION).strip()
    if dna_version:
        return dna_version if dna_version.startswith("v") else f"v{dna_version}"

    try:
        with open(PYPROJECT_PATH, "rb") as handle:
            project = tomllib.load(handle).get("project", {})
        version = str(project.get("version", "")).strip()
        if version:
            return f"v{version}"
    except Exception:
        pass
    return "v2026.04.18-UNIFIED"


def get_build_info() -> dict[str, Any]:
    """Return comprehensive version and environment metadata.

    Returns:
        Dict with version, protocol_version, governance info, SoT linkage,
        build metadata (commit, branch), and status.
    """
    commit = _git_sha_short()
    # 2026-10-06 FI-008 (F13 "observatory dynamic SOT"): ONE publisher for the
    # release version — the F13-ratified canon manifest, not the pyproject
    # PEP-440 epoch string ("1!2026.10.1" rendered publicly as "v1!2026.10.1").
    # Precedence: deploy env override → /etc/arifos/canon/canon-release.json →
    # pyproject fallback. Canon = canon_version "2026.10.05-<sha>".
    app_version = ""
    try:
        # canon.py is the sole reader of the canon dir (FHS single-owner).
        _canon_release = canon_manifest() or {}
        app_version = str(_canon_release.get("canon_version") or "")
    except Exception:
        app_version = ""
    app_version = (
        os.environ.get("ARIFOS_APP_VERSION", "").strip() or app_version
        # FI-008 "ONE publisher" canon manifest (C-3.1 amend 2026-10-06):
        # fail-closed if both env override AND canon-release.json are
        # missing/empty. Removed pyproject PEP-440 fallback — defeats
        # "ONE publisher" purpose (re-renders "1!2026.10.1" as "v1!2026.10.1"
        # when canon manifest is missing). Callers detect empty string
        # and surface the missing publisher. F13 binary: "amend dulu".
    )
    return {
        # Server version (semantic, required by A2A/WebMCP)
        "version": app_version,
        "server_version": app_version,
        "update_summary": (
            "5-Resource Canonical Consolidation. Enforced single Source-of-Truth architecture, "
            "consolidated 20+ fragmented resources into 5 canonical URIs "
            "(doctrine, vitals, schema, session, forge), and eliminated identity confusion."
        ),
        # MCP protocol compatibility
        "protocol_version": "2026-07-28",
        "supported_protocol_versions": [
            "2026-07-28",
            "2025-11-25",
            "2025-06-18",
            "2025-03-26",
            "2024-11-05",
        ],
        # Governance layer
        "governance_version": "registry-1.3.0",
        "policy_version": "arifOS.constitution.v1",
        "floors_version": "2026.04",
        "floors_active": 13,
        # Source-of-Truth linkage — ties runtime back to canonical doctrine repo
        "source_repo": "https://github.com/ariffazil/arifOS",
        "source_repo_name": "ariffazil/arifOS",
        # Build traceability — GIT_SHA and ARIFOS_APP_VERSION set by entrypoint from host git
        "build": {
            "commit": commit,
            "commit_short": commit,
            "image": _image_tag(),
            "built_at": _build_time(),
            "branch": "main",
        },
        "release_tag": app_version,
        # Status
        "status": "FORGED",
        "forge_date": "2026-04-13",
        # Display helpers
        "display": {
            "short": "2.0.0",
            "full": "arifOS MCP 2.0.0",
            "with_build": f"2.0.0+{commit}",
            "with_governance": "2.0.0 • Registry 1.2.0 • Policy v1",
        },
    }


def get_version_string(format: str = "short") -> str:
    """Get a formatted version string."""
    info = get_build_info()
    return info["display"].get(format, info["display"]["short"])
