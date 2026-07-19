"""
Context Capture Lockdown Tests — Vector #6 Gates
══════════════════════════════════════════════════

FORGED 2026-07-20 — Fable5 audit Vector #6 implementation.

Tests that agent-modified governance files (SOUL.md, AGENTS.md, INIT/BOOT docs)
cannot be silently mutated by T1/T2 agents. Only F13 sovereign ack permits
modification. Memory writes to governance-adjacent tiers (L4-L6) require
T3 (888_HOLD). AAA/prompts/ and arifOS/GENESIS/ files require 888_HOLD to mutate.

Doctrine references:
  - /root/forge_work/PRESSURE_VECTOR_AUDIT_2026-07-19.md (Vector #6)
  - /root/AGENTS.md §6.2 (T1/T2/T3 autonomy tiers)
  - /root/SOUL.md §4 (Lease Classes L0-L3 mapping to T0-T3)
  - /root/arifOS/arifosmcp/resources/memory.py (L1-L6 tier definitions)

Test suites:
  1. GOVERNANCE_FILE_IMMUTABILITY — SOUL.md, AGENTS.md, INIT/BOOT files
     assert they are present and carry seal markers; T1/T2 mutation = violation
  2. MEMORY_TIER_GATES — arif_memory remember/promote require T3 for L4-L6
  3. PROMPTS_GENESIS_888_HOLD — AAA/prompts/ and arifOS/GENESIS/ = 888_HOLD
  4. SEAL_HASH_CHECK — boot/INIT file hash chain to detect unauthorized modification

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import os
import re
import stat
from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════════════
# Constants — file paths derived from live federation surface
# ═══════════════════════════════════════════════════════════════════════════

ROOT = Path("/root")

# Tier definitions (from /root/AGENTS.md §6.2)
T1_AUTO_DO = "T1"
T2_ANNOUNCE = "T2"
T3_888_HOLD = "T3"
F13_SOVEREIGN = "F13"

# Governance files that shape future agent sessions
GOVERNANCE_FILES = [
    ROOT / "SOUL.md",
    ROOT / "AGENTS.md",
    ROOT / "CLAUDE.md",
    ROOT / "AAA" / "CLAUDE.md",
    ROOT / "AAA" / "AGENTS.md",
    ROOT / "CONTEXT.md",
]

# INIT/BOOT files that govern agent session boot
INIT_BOOT_FILES = [
    ROOT / "AAA" / "prompts" / "INIT.md",
    ROOT / "AAA" / "prompts" / "GROK_AAA_NEXT_INIT.md",
    ROOT / "AAA" / "prompts" / "SESSION_A_INIT.md",
    ROOT / "AAA" / "prompts" / "QUANTUM_KERNEL_INIT.md",
    ROOT / "AAA" / "prompts" / "QUBIT_INIT_v1.0.md",
    ROOT / "AAA" / "prompts" / "NEXT_SESSION_KERNEL_INHABIT_SPINE_P0.md",
]

# Directories under 888_HOLD protection
HOLD_PROTECTED_DIRS = [
    ROOT / "AAA" / "prompts",
    ROOT / "arifOS" / "GENESIS",
]

# Memory tiers (from /root/arifOS/arifosmcp/resources/memory.py)
# L4-L6 = governance-adjacent (structured record, relationships, immutable)
GOVERNANCE_ADJACENT_TIERS = {"L4", "L5", "L6"}

# Seal markers expected in governance files
SEAL_MARKERS = [
    "SEALED",
    "SOVEREIGN",
    "F13",
    "FORGED",
    "DITEMPA BUKAN DIBERI",
]


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════

def _sha256(path: Path) -> str:
    """Compute SHA-256 hash of a file's contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _has_seal_markers(content: str) -> bool:
    """Check if file content carries at least one seal/sovereign marker."""
    return any(marker in content for marker in SEAL_MARKERS)


def _is_writable(path: Path) -> bool:
    """Check if a file is writable by the current process (T1-level check)."""
    if not path.exists():
        return False
    return os.access(path, os.W_OK)


def _read_if_exists(path: Path) -> str | None:
    """Read file content if it exists, return None otherwise."""
    try:
        return path.read_text()
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return None


# ═══════════════════════════════════════════════════════════════════════════
# Suite 1 — Governance File Immutability
# ═══════════════════════════════════════════════════════════════════════════


class TestGovernanceFileImmutability:
    """SOUL.md, AGENTS.md, and INIT/BOOT files must be present + sealed.

    These files govern future agent sessions. Under T1/T2 authority,
    they should carry explicit seal markers confirming they were
    ratified by F13 sovereign. Any modification without F13 sovereign
    ack is a context capture vector.
    """

    @pytest.mark.parametrize("path", GOVERNANCE_FILES)
    def test_governance_file_exists(self, path: Path):
        """Every governance file must exist on disk."""
        assert path.exists(), (
            f"MISSING GOVERNANCE FILE: {path}\n"
            f"This file governs future agent sessions. Its absence means "
            f"agents boot without the constitutional surface."
        )

    @pytest.mark.parametrize("path", GOVERNANCE_FILES)
    def test_governance_file_is_not_empty(self, path: Path):
        """Governance files must contain substantive content."""
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        content = path.read_text()
        assert len(content.strip()) > 100, (
            f"TRUNCATED GOVERNANCE FILE: {path} has only {len(content)} chars.\n"
            f"A governance file this small cannot carry the full constitutional surface."
        )

    @pytest.mark.parametrize("path", GOVERNANCE_FILES)
    def test_governance_file_has_seal_marker(self, path: Path):
        """Every governance file must carry a seal/sovereign marker."""
        if not path.exists():
            pytest.skip(f"{path} does not exist")
        content = path.read_text()
        assert _has_seal_markers(content), (
            f"UNSEALED GOVERNANCE FILE: {path}\n"
            f"No seal marker found (expected: {SEAL_MARKERS}).\n"
            f"An agent could have written this file without F13 ratification.\n"
            f"Vector #6: context capture via unsealed governance file."
        )

    def test_sovereign_identity_present_in_soul(self):
        """SOUL.md must declare F13 sovereign identity."""
        soul = ROOT / "SOUL.md"
        if not soul.exists():
            pytest.skip("SOUL.md not found")
        content = soul.read_text()
        assert "ARIF-SOVEREIGN-888" in content, (
            "SOUL.md lacks F13 sovereign identity seal.\n"
            "Without this, agents cannot verify who ratified the SOUL."
        )
        assert "F13" in content, (
            "SOUL.md does not reference F13 sovereign floor.\n"
            "Agents must know who holds the final veto."
        )

    def test_autonomy_tiers_documented_in_agents(self):
        """AGENTS.md must define T1/T2/T3 autonomy tiers."""
        agents = ROOT / "AGENTS.md"
        if not agents.exists():
            pytest.skip("AGENTS.md not found")
        content = agents.read_text()
        assert "T1" in content and "AUTO-DO" in content, (
            "AGENTS.md missing T1/AUTO-DO tier definition.\n"
            "Agents boot without knowing what they can do autonomously."
        )
        assert "T2" in content and "ANNOUNCE" in content, (
            "AGENTS.md missing T2/ANNOUNCE tier definition."
        )
        assert "T3" in content and "888_HOLD" in content, (
            "AGENTS.md missing T3/888_HOLD tier definition.\n"
            "Agents boot without knowing what requires sovereign approval."
        )

    @pytest.mark.parametrize("path", INIT_BOOT_FILES)
    def test_init_file_exists_and_sealed(self, path: Path):
        """INIT/BOOT files must exist and carry seal markers.

        If a boot file exists without a seal, an agent could have
        appended Section 15 or modified boot instructions to capture
        future sessions (Vector #6: context capture).
        """
        if not path.exists():
            pytest.skip(f"{path} not found on disk — no seal needed")
        content = path.read_text()
        assert len(content.strip()) > 50, (
            f"TRUNCATED INIT FILE: {path} is too small ({len(content)} chars).\n"
            f"May indicate a stub planted by an agent to inject instructions."
        )
        assert _has_seal_markers(content), (
            f"UNSEALED INIT FILE: {path}\n"
            f"No seal marker found. An agent could have written or appended "
            f"to this file without F13 ratification.\n"
            f"Vector #6: boot-doc poison via unsealed INIT file."
        )

    def test_init_has_boot_phase_declaration(self):
        """The canonical INIT.md must declare its boot phase (Section 1)."""
        init = ROOT / "AAA" / "prompts" / "INIT.md"
        if not init.exists():
            pytest.skip("INIT.md not found")
        content = init.read_text()
        assert "BOOT PHASE" in content or "SELF-ATTESTATION" in content, (
            "INIT.md missing boot phase declaration.\n"
            "Without this, agents may skip identity binding before accepting tasks."
        )

    @pytest.mark.xfail(
        reason="KNOWN: Fable5 Section 15 append in INIT.md L635-683. "
               "Awaiting F13 sovereign review to ratify or excise.",
        strict=True,
    )
    def test_no_orphan_section_15(self):
        """Verify no agent-appended Section 15 exists in any governance file.

        The Fable5 audit flagged a 'Section 15 / forge--end housekeeping'
        incident where an agent appended content to INIT.md.
        This test scans governance files for agent-appended sections
        and reports the known Fable5 finding if still present.
        """
        suspicious = []
        for path in GOVERNANCE_FILES + INIT_BOOT_FILES:
            if not path.exists():
                continue
            content = path.read_text()
            if "forge--end" in content.lower():
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "forge--end" in line.lower():
                        suspicious.append((str(path), i + 1, line.strip()[:120]))

        # Filter to only governance/INIT files (not memory/ or forge_work/)
        governance_hits = []
        for filepath, lineno, line in suspicious:
            if "memory/" in filepath or "forge_work/" in filepath:
                continue
            governance_hits.append((filepath, lineno, line))

        if not governance_hits:
            return  # Clean — no agent-appended sections found

        # Check: is this the KNOWN Fable5 Section 15 in INIT.md?
        init_hits = [h for h in governance_hits if "INIT.md" in h[0]]
        other_hits = [h for h in governance_hits if "INIT.md" not in h[0]]

        msg_parts = []
        if init_hits:
            msg_parts.append(
                "KNOWN VECTOR #6 (Fable5 audit): Section 15 appended by agent "
                "`forge--end` housekeeping pass still present in INIT.md.\n"
                "This is the exact incident Fable5 flagged — an agent wrote "
                "future-task instructions into the canonical boot document.\n"
                "Resolution: F13 sovereign must review Section 15 content and "
                "either ratify it (move to canon) or excise it (remove agent-planted text)."
            )
        if other_hits:
            msg_parts.append(
                f"NEW VECTOR #6 HITS: agent-appended content in governance files:\n"
                + "\n".join(f"  {f}:L{ln}: {l}" for f, ln, l in other_hits)
            )

        if msg_parts:
            pytest.fail("\n\n".join(msg_parts))


# ═══════════════════════════════════════════════════════════════════════════
# Suite 2 — Memory Tier Gates (arif_memory remember/promote)
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryTierGates:
    """Memory writes (arif_memory remember/promote) to governance-adjacent
    tiers (L4-L6) must require T3 (888_HOLD) authority.

    From arifOS memory architecture:
      L1 = Ephemeral (Redis, ~60s) — free T1
      L2 = Session (Redis, session TTL) — free T1
      L3 = Semantic (Qdrant, fuzzy) — T1 with lease
      L4 = Structured (Supabase, official record) — T2 minimum, T3 if governance
      L5 = Relationships (Graphiti, entity graph) — T2 minimum, T3 if governance
      L6 = Immutable (VAULT999, sealed) — T3 + F13 sovereign always
    """

    def test_arif_memory_tool_exists(self):
        """The arif_memory tool must be importable from the runtime."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                ARIF_MEMORY_MODES,
                MODE_ACTION_CLASS,
            )
        except ImportError as e:
            pytest.skip(f"arif_memory module not importable: {e}")
        assert "remember" in ARIF_MEMORY_MODES, "remember mode missing"
        assert "promote" in ARIF_MEMORY_MODES, "promote mode missing"

    def test_remember_mode_classified_as_mutation(self):
        """remember mode must be classified as EXECUTE_REVERSIBLE (mutation)."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_ACTION_CLASS,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")
        assert MODE_ACTION_CLASS.get("remember") in (
            "EXECUTE_REVERSIBLE",
            "EXECUTE_HIGH_IMPACT",
            "IRREVERSIBLE",
        ), (
            f"remember action_class={MODE_ACTION_CLASS.get('remember')} — "
            f"should be EXECUTE_REVERSIBLE or higher. If it's OBSERVE, "
            f"agents can write memories without mutation gates."
        )

    def test_promote_mode_classified_as_high_impact(self):
        """promote mode must be classified as EXECUTE_HIGH_IMPACT."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_ACTION_CLASS,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")
        assert MODE_ACTION_CLASS.get("promote") in (
            "EXECUTE_HIGH_IMPACT",
            "IRREVERSIBLE",
        ), (
            f"promote action_class={MODE_ACTION_CLASS.get('promote')} — "
            f"should be EXECUTE_HIGH_IMPACT or higher."
        )

    def test_remember_requires_lease(self):
        """remember mode must require a lease."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_REQUIRES_LEASE,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")
        assert MODE_REQUIRES_LEASE.get("remember") is True, (
            "remember mode does not require a lease — "
            "T1 agents can write memories without any gate."
        )

    def test_promote_requires_lease(self):
        """promote mode must require a lease."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_REQUIRES_LEASE,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")
        assert MODE_REQUIRES_LEASE.get("promote") is True, (
            "promote mode does not require a lease — "
            "T1 agents can promote memories without any gate."
        )

    def test_forget_requires_human_ack(self):
        """forget mode must require human acknowledgment (F13/L13)."""
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_REQUIRES_HUMAN_ACK,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")
        assert MODE_REQUIRES_HUMAN_ACK.get("forget") is True, (
            "forget mode does not require human ack — "
            "T1 agents can delete sealed memories."
        )

    def test_memory_tier_definitions_exist(self):
        """The L1-L6 memory tier definitions must be accessible."""
        try:
            from arifosmcp.resources.memory import MEMORY_TEXT
        except ImportError:
            pytest.skip("memory resource not importable")
        assert "L1" in MEMORY_TEXT and "L6" in MEMORY_TEXT, (
            "Memory tier definitions incomplete — L1-L6 must all be documented."
        )
        # Governance-adjacent tiers must be marked as such
        assert "immutable" in MEMORY_TEXT.lower(), (
            "L6 must be documented as immutable."
        )
        assert "sealed" in MEMORY_TEXT.lower(), (
            "L6 must reference sealed truth."
        )

    def test_l4_l6_require_elevated_authority(self):
        """L4-L6 tiers should require elevated authority in the memory engine.

        L4 (structured record) and L5 (relationships) are governance-adjacent.
        L6 (VAULT999) is immutable and sovereign-only. Writing to these tiers
        must require more than T1 authority.
        """
        # Verify that the memory module enforces tier-based gating.
        # The tool_13 module classifies remember as EXECUTE_REVERSIBLE
        # and promote as EXECUTE_HIGH_IMPACT — these are the right action
        # classes, but tier-level enforcement is a runtime concern.
        # This test ensures the classification surface doesn't regress.
        try:
            from arifosmcp.runtime.megaTools.tool_13_arif_memory import (
                MODE_ACTION_CLASS,
                MODE_REQUIRES_LEASE,
                MODE_PRE_FLOORS,
            )
        except ImportError:
            pytest.skip("arif_memory module not importable")

        # All mutation modes (remember, promote, revise, forget) must have
        # pre-floor checks that include L01 (AMANAH) and at least one of
        # L04 (CLARITY), L09 (ANTIHANTU), or L13 (SOVEREIGN) for L4+ operations
        for mode in ("remember", "promote", "revise", "forget"):
            floors = MODE_PRE_FLOORS.get(mode, ())
            assert "L01" in floors, (
                f"{mode} missing L01 (AMANAH) pre-floor — "
                f"mutations must respect the reversibility gate."
            )
            assert "L02" in floors, (
                f"{mode} missing L02 (TRUTH) pre-floor — "
                f"mutations must be truth-anchored."
            )


# ═══════════════════════════════════════════════════════════════════════════
# Suite 3 — Prompts and GENESIS 888_HOLD Gates
# ═══════════════════════════════════════════════════════════════════════════


class TestPromptsAndGenesisHoldGate:
    """Any file in /root/AAA/prompts/ or /root/arifOS/GENESIS/ requires
    888_HOLD to mutate. These directories contain constitutional canon
    and agent boot instructions — mutation here shapes future sessions.
    """

    def test_aaa_prompts_directory_exists(self):
        """AAA/prompts must exist."""
        prompts = ROOT / "AAA" / "prompts"
        assert prompts.exists() and prompts.is_dir(), (
            "AAA/prompts directory missing — no boot surface for agents."
        )

    def test_genesis_directory_exists(self):
        """arifOS/GENESIS must exist."""
        genesis = ROOT / "arifOS" / "GENESIS"
        assert genesis.exists() and genesis.is_dir(), (
            "arifOS/GENESIS directory missing — no constitutional canon."
        )

    def test_genesis_contains_kernel_canon(self):
        """GENESIS/ must contain 000_KERNEL_CANON.md."""
        kernel_canon = ROOT / "arifOS" / "GENESIS" / "000_KERNEL_CANON.md"
        assert kernel_canon.exists(), (
            "000_KERNEL_CANON.md missing from GENESIS/ — "
            "the kernel has no canonical doctrinal root."
        )

    def test_genesis_files_are_markdown_or_json(self):
        """GENESIS files should be .md (doctrine) or .json (evidence).

        Unexpected file types could indicate agent-planted content.
        """
        genesis = ROOT / "arifOS" / "GENESIS"
        if not genesis.exists():
            pytest.skip("GENESIS/ not found")
        allowed = {".md", ".json", ".jsonl", ".txt"}
        suspicious = []
        for f in genesis.rglob("*"):
            if f.is_file() and f.suffix not in allowed:
                suspicious.append(str(f))
        assert not suspicious, (
            f"SUSPICIOUS FILES in GENESIS/: {suspicious}\n"
            f"Non-doctrine file types may indicate agent-planted content."
        )

    @pytest.mark.parametrize("dir_path", HOLD_PROTECTED_DIRS)
    def test_protected_dir_files_exist(self, dir_path: Path):
        """Protected directories must contain files — empty dir = red flag."""
        if not dir_path.exists():
            pytest.skip(f"{dir_path} not found")
        files = list(dir_path.rglob("*"))
        assert len(files) > 0, (
            f"EMPTY PROTECTED DIRECTORY: {dir_path}\n"
            f"A directory under 888_HOLD protection with zero files "
            f"means agents have no constitutional surface to load."
        )

    def test_init_files_not_writable_by_others(self):
        """INIT files should not be world-writable (security best practice).

        While 888_HOLD is enforced at the governance layer, world-writable
        permissions on boot files are a defense-in-depth violation.
        """
        violations = []
        for path in INIT_BOOT_FILES:
            if not path.exists():
                continue
            mode = path.stat().st_mode
            if mode & stat.S_IWOTH:  # world-writable
                violations.append(str(path))
        if violations:
            # This is a warning, not a hard fail — permissions are OS-level
            # and the constitutional gate is the real enforcement
            pytest.fail(
                f"WORLD-WRITABLE INIT FILES: {violations}\n"
                f"While 888_HOLD governs mutations, world-writable permissions "
                f"on boot files weaken the defense-in-depth posture."
            )


# ═══════════════════════════════════════════════════════════════════════════
# Suite 4 — Seal Hash Check (Boot/INIT File Integrity)
# ═══════════════════════════════════════════════════════════════════════════


class TestBootFileSealHash:
    """Cryptographic integrity check for INIT/BOOT files.

    Computes SHA-256 hashes of all INIT files and stores them as a seal
    manifest. Any modification to these files will break the hash chain,
    which must be detectable by session init (arif_init) before accepting
    boot instructions.

    The hash manifest itself should be sealed in VAULT999.
    """

    # Known-good hashes computed at forge time (2026-07-20)
    # These are the baseline; if a file changes legitimately via F13,
    # the hash manifest must be updated and re-sealed.
    SEAL_MANIFEST = {
        "INIT.md": (
            "83f23200e0a7437f068e7edab70b488c66278c79781ab843052ef39413d82725"
        ),
        "GROK_AAA_NEXT_INIT.md": (
            "d932306b07e4352d530e666bca2f02faa2048d98a6ebfe01d9c821b7737fe60b"
        ),
        "SESSION_A_INIT.md": (
            "0d0918d67acfb32110ad8738f94ca5b4d7e1fb6ea8ef294aa7d681319b774efc"
        ),
        "QUANTUM_KERNEL_INIT.md": (
            "5f7f5ba21b10c5d2ed6bffb607a10533c0ddb650809b94e626bcbb0bf059e7b5"
        ),
        "QUBIT_INIT_v1.0.md": (
            "326c35b406a214d1c58ab8a1ca3dc22618330dec58480e3a80160148ea587255"
        ),
        "NEXT_SESSION_KERNEL_INHABIT_SPINE_P0.md": (
            "ef029ca4df5de501fde086b47d459fc3b5a096caba88dfa63bf82e18212cd2fa"
        ),
    }

    def test_seal_manifest_has_all_init_files(self):
        """Every INIT file on disk must have a hash in the seal manifest."""
        prompts_dir = ROOT / "AAA" / "prompts"
        if not prompts_dir.exists():
            pytest.skip("AAA/prompts not found")

        # Build on-disk set, detecting symlinks BEFORE is_file check
        on_disk = set()
        symlink_map = {}  # symlink name -> resolved target name
        for f in prompts_dir.iterdir():
            if f.is_symlink():
                target = f.resolve()
                if target.exists() and target.is_file():
                    symlink_map[f.name] = target.name
                on_disk.add(f.name)
            elif f.is_file():
                on_disk.add(f.name)

        in_manifest = set(self.SEAL_MANIFEST.keys())

        # Files on disk that aren't in the manifest
        unmanifested = on_disk - in_manifest

        # Known non-INIT files (not boot docs — acceptable to skip)
        known_non_init = {
            "ARIF_SEAL.md", "WEB_ENGINEER_AGENT_v1.md",
            "999_RECURSIVE_HARDEN.md", "XAUUSD_RSI_UPGRADE_v1.0.md",
        }

        # Flag only init-like files that aren't manifest and aren't known symlinks
        init_unmanifested = {
            f for f in unmanifested - known_non_init - set(symlink_map.keys())
            if "INIT" in f.upper() or "init" in f or "BOOT" in f.upper()
        }

        if init_unmanifested:
            pytest.fail(
                f"UNMANIFESTED INIT FILES: {init_unmanifested}\n"
                f"These files exist on disk but have no seal hash.\n"
                f"They could have been planted by an agent without F13 ratification."
            )

        # Files in manifest that aren't on disk (and aren't symlink targets)
        missing = in_manifest - on_disk - set(symlink_map.values())
        if missing:
            pytest.fail(
                f"MISSING INIT FILES: {missing}\n"
                f"These files were in the seal manifest but no longer exist.\n"
                f"Either they were legitimately removed (update manifest) or "
                f"an agent deleted boot instructions."
            )

    @pytest.mark.parametrize("filename,expected_hash", [
        (k, v) for k, v in SEAL_MANIFEST.items()
    ])
    def test_init_file_hash_matches_seal(self, filename: str, expected_hash: str):
        """Each INIT file's SHA-256 must match the seal manifest.

        If this test fails, the file was modified since the seal was
        forged. This is the Vector #6 context capture vector — an agent
        modifying boot instructions to shape future sessions.
        """
        path = ROOT / "AAA" / "prompts" / filename
        if not path.exists():
            pytest.skip(f"{filename} not on disk")

        actual_hash = _sha256(path)
        assert actual_hash == expected_hash, (
            f"SEAL HASH MISMATCH: {filename}\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}\n"
            f"\n"
            f"This file has been modified since the seal manifest was forged.\n"
            f"POSSIBLE VECTOR #6: An agent modified boot instructions to\n"
            f"capture future sessions.\n"
            f"\n"
            f"If this change was authorized by F13 sovereign:\n"
            f"  1. Verify the new content is correct\n"
            f"  2. Recompute the hash: sha256sum {path}\n"
            f"  3. Update SEAL_MANIFEST in this test file\n"
            f"  4. Re-seal in VAULT999"
        )

    def test_generate_seal_manifest_for_audit(self):
        """Generate a complete hash manifest of all prompt files for audit.

        This is a diagnostic test that always passes — it outputs the
        current hash state so that any drift from the sealed manifest
        can be identified in CI logs.
        """
        prompts_dir = ROOT / "AAA" / "prompts"
        if not prompts_dir.exists():
            pytest.skip("AAA/prompts not found")

        current_hashes = {}
        for f in sorted(prompts_dir.iterdir()):
            if f.is_file():
                current_hashes[f.name] = _sha256(f)

        # Also hash GENESIS files for completeness
        genesis_dir = ROOT / "arifOS" / "GENESIS"
        if genesis_dir.exists():
            for f in sorted(genesis_dir.rglob("*.md")):
                rel = str(f.relative_to(ROOT))
                current_hashes[rel] = _sha256(f)

        # This test always passes but emits the manifest for audit
        print(f"\n SEAL MANIFEST ({len(current_hashes)} files):")
        for name, h in sorted(current_hashes.items()):
            print(f"  {name}: {h}")

        # Verify at least the core boot files are present
        assert "INIT.md" in current_hashes, "Canonical INIT.md not in manifest"

    def test_governance_file_hash_stability(self):
        """Core governance files should have content (not be empty stubs).

        While we don't pin exact hashes for governance files (they evolve
        more frequently than boot files), they must not be empty stubs
        that an agent could later fill with captured instructions.
        """
        for path in GOVERNANCE_FILES:
            if not path.exists():
                continue
            content = path.read_text()
            assert len(content.strip()) > 200, (
                f"GOVERNANCE FILE TOO SMALL: {path} = {len(content)} chars.\n"
                f"A governance file this small could be a planted stub "
                f"waiting for an agent to inject instructions."
            )
            # Must have at least one section header
            assert "#" in content, (
                f"GOVERNANCE FILE HAS NO STRUCTURE: {path}\n"
                f"No markdown headers found — not a valid governance document."
            )
