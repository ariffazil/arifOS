"""
arifOS Reversibility Engine — L01 AMANAH Implementation
═══════════════════════════════════════════════════════════════════════════════

L01 AMANAH: No irreversible action without explicit acknowledgment.

This engine determines reversibility for every tool call:
- TRIVIAL: read, search, query, list — always allowed
- REVERSIBLE: write temp, create draft, cache — can be undone
- PARTIAL: edit, update, patch — can be undone with effort
- IRREVERSIBLE: delete, drop, publish, send — requires ack + 888_HOLD
- CRITICAL: sudo, volume delete, schema drop — 888_HOLD mandatory

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ReversibilityClass(StrEnum):
    """Reversibility classes ordered by severity.

    NOTE: Phase 2 consolidation target (2026-07-11).
    Canonical source is now arifosmcp.schemas.reversibility (R-scale).
    This local enum uses legacy lowercase values. Migrate callers to
    schema's ReversibilityClass (R0-R5) when touching this file next.
    R-scale mapping: TRIVIAL=R0, REVERSIBLE=R1, PARTIAL=R2,
                     IRREVERSIBLE=R4, CRITICAL=R5.
    """

    TRIVIAL = "trivial"  # No state change
    REVERSIBLE = "reversible"  # Easily undone
    PARTIAL = "partial"  # Undoable with effort
    IRREVERSIBLE = "irreversible"  # Cannot be undone
    CRITICAL = "critical"  # Cannot be undone — catastrophic


# Canonical R-scale alias (Phase 2 — backward compat bridge)
# New code should import from arifosmcp.schemas.reversibility
# Engine's internal logic still uses legacy names until full migration.
R_SCALE_MAP = {
    "trivial": "R0",
    "reversible": "R1",
    "partial": "R2",
    "irreversible": "R4",
    "critical": "R5",
}


# Static reversibility map — words that indicate irreversible patterns
_IRREVERSIBLE_PATTERNS = [
    r"\bdelete\b",
    r"\bdrop\b",
    r"\bremove\b",
    r"\bdestroy\b",
    r"\btruncate\b",
    r"\berase\b",
    r"\brm\s",
    r"\bdrop\s",
    r"\bdelete\s",
    r"\bdestroy\s",
    r"\brmrf\b",
    r"\brm\s+-rf\b",
    r"\bdrop\s+table\b",
    r"\bdelete\s+from\b",
    r"\btruncate\s+table\b",
    r"\bprune\b",
    r"\bkill\b",
    r"\bkill\s+-9\b",
    r"\bforce\s+quit\b",
    # Git force/dangerous
    r"\bgit\s+push\s+.*--force\b",
    r"\bgit\s+push\s+-f\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bgit\s+rebase\s+-i\b",
    r"\bgit\s+branch\s+-D\b",
    r"\bgit\s+stash\s+drop\b",
    # Docker dangerous
    r"\bdocker\s+system\s+prune\b",
    r"\bdocker\s+volume\s+rm\b",
    r"\bdocker\s+network\s+rm\b",
    r"\bdocker\s+container\s+rm\b",
    r"\bdocker\s+rmi\b",
    r"\bdocker\s+stop\b",
    r"\bdocker\s+kill\b",
]

_PARTIAL_PATTERNS = [
    r"\bedit\b",
    r"\bupdate\b",
    r"\bpatch\b",
    r"\boverwrite\b",
    r"\bmodify\b",
    r"\bchange\b",
    r"\breplace\b",
    r"\bwrite\b",  # write can be partial if it modifies existing
    r"\bset\s+\w+\s*=",  # variable assignment
    r"\bconfig\b",
]

_REVERSIBLE_PATTERNS = [
    r"\bread\b",
    r"\bsearch\b",
    r"\bquery\b",
    r"\blist\b",
    r"\bget\b",
    r"\bfetch\b",
    r"\blook\s+up\b",
    r"\bSELECT\b",
    r"\bSELECT\s+",
    r"\bHEAD\b",
    r"\binspect\b",
    r"\bvalidate\b",
    r"\bcheck\b",
    r"\bcalculate\b",
    r"\bcompute\b",
    r"\banalyze\b",
    r"\bsummarize\b",
    r"\bgenerate\s+(?!contract|policy|legal)",  # generate is reversible unless creating legal docs
]

_CRITICAL_PATTERNS = [
    r"\bsudo\b",
    r"\bsudo\s+",
    r"\bchmod\s+777\b",
    r"\bchmod\s+000\b",
    r"\bvolume\s+delete\b",
    r"\bdisk\s+wipe\b",
    r"\bdd\s+if=\b",
    r"\bmkfs\b",
    r"\bfork\s+bomb\b",
    r"\bschema\s+drop\b",
    r"\bproduction\s+delete\b",
    r"\breboot\b",
    r"\bshutdown\b",
    r"\bhalt\b",
    r"\binit\s+0\b",
]


# ────────────────────────────────────────────────────────────────────────
# T2 — Shell command classifier (Forged 2026-08-27 · WIRE 5)
# ────────────────────────────────────────────────────────────────────────
# Splits shell commands by chain operators, classifies each segment by its
# first token, and aggregates to a single reversibility verdict.
#
# Failure-mode design (Forged, response to T2 spec by Arif):
#   - Output redirection (>, >>, 2>, etc.) is ALWAYS PARTIAL — never ignored.
#   - Command substitution ($(), backticks) is ALWAYS PARTIAL — captures
#     can be re-used to mutate, fail-closed to be safe.
#   - Unknown binary ⇒ PARTIAL — explicit fail-closed default per spec.
#   - Any mutating verb in a chain escalates the WHOLE command.
#   - Read-only segments chained together remain TRIVIAL.
#
# This is the SOLE mutability classification for bash/sh/zsh tool calls.
# It supersedes the generic regex pass below for shell contexts.

_R0_SHELL_COMMANDS: frozenset[str] = frozenset(
    {
        # Pure observability — no filesystem, no process state, no network
        "ls",
        "cat",
        "head",
        "tail",
        "grep",
        "egrep",
        "fgrep",
        "rg",
        "find",  # plain find — see _analyze_shell_command for -delete guard
        "pwd",
        "whoami",
        "ps",
        "env",
        "file",
        "stat",
        "wc",
        "date",
        "uname",
        "hostname",
        "du",
        "df",
        "free",
        "uptime",
        "w",
        "who",
        "id",
        "groups",
        "test",
        "true",
        "false",
        "which",
        "whereis",
        "type",
        "echo",
        "printf",
        "tree",
    }
)

_R2_SHELL_COMMANDS: frozenset[str] = frozenset(
    {
        # Mutating commands — PARTIAL by default, escalates on -rf / --force
        "rm",
        "mv",
        "cp",
        "chmod",
        "chown",
        "chgrp",
        "dd",
        "pkill",
        "kill",
        "shutdown",
        "reboot",
        "halt",
        "iptables",
        "ufw",
        "firewall-cmd",
        "route",
        "useradd",
        "userdel",
        "usermod",
        "groupadd",
        "groupdel",
        "crontab",
        "at",
        "batch",
        "mount",
        "umount",
        "ln",
        "tee",
        "touch",
        "mkdir",
        "rmdir",
        "truncate",
        "fdisk",
        "mkfs",
        "mkswap",
    }
)

# sed/awk: read-only by default, mutating only with -i / inplace
_RW_TEXT_COMMANDS: frozenset[str] = frozenset({"sed", "awk"})

_GIT_SAFE_SUBCMDS: frozenset[str] = frozenset(
    {
        "status",
        "diff",
        "log",
        "show",
        "remote",
        "branch",
        "rev-parse",
        "config",
        "tag",
        "stash list",
    }
)
_GIT_DANGEROUS_SUBCMDS: frozenset[str] = frozenset(
    {
        "push",
        "commit",
        "reset",
        "rebase",
        "merge",
        "checkout",
        "clean",
        "init",
        "add",
        "rm",
        "mv",
        "restore",
    }
)

_DOCKER_SAFE_SUBCMDS: frozenset[str] = frozenset(
    {
        "ps",
        "images",
        "logs",
        "inspect",
        "stats",
        "version",
        "info",
        "network ls",
        "volume ls",
        "system df",
    }
)
_DOCKER_DANGEROUS_SUBCMDS: frozenset[str] = frozenset(
    {
        "run",
        "exec",
        "rm",
        "rmi",
        "stop",
        "kill",
        "restart",
        "pull",
        "build",
        "compose up",
        "compose down",
        "system prune",
    }
)

# Regex patterns — order in code matches evaluation order
_REDIRECTION_RE = re.compile(r"(?:>|>>|2>|1>|2>&1|1>&2|<\()")
_CHAIN_RE = re.compile(r"&{1,2}|\|{1,2}|;")
_SUBSHELL_RE = re.compile(r"\$\(|\`")
# -i as standalone token, or -i.bak style backup-suffix
_INPLACE_FLAG_RE = re.compile(r"(?:^|\s)-i(?:\b|\.\w+)")
_INPLACE_AWK_RE = re.compile(r"-i\s+inplace|--inplace")
# Force / destructive flags
_FORCE_FLAG_RE = re.compile(r"(?:^|\s)(?:-{1,2}[fF]+(?:\b|=)|--force(?:\b|=))")
_RECURSIVE_FLAG_RE = re.compile(r"(?:^|\s)(?:-r|--recursive)(?:\b|=)")


def _shell_extract_command(params: dict[str, Any]) -> str | None:
    """Extract command string from a tool-call param dict.

    Tries a few conventional keys; returns None if absent or non-string.
    """
    if not isinstance(params, dict):
        return None
    for key in ("command", "cmd", "script", "argv"):
        val = params.get(key)
        if isinstance(val, str) and val.strip():
            return val
        # argv-as-list is a different surface; engine doesn't tokenize lists yet.
    return None


def _shell_tokenize(command: str) -> list[list[str]]:
    """Split command on chain operators; return token-list per segment.

    Quoted strings are preserved via shlex.split. Comments are stripped.
    Malformed input falls back to whitespace split on the offending segment.
    """
    segments = _CHAIN_RE.split(command)
    out: list[list[str]] = []
    for raw in segments:
        seg = raw.strip()
        if not seg:
            continue
        try:
            toks = shlex.split(seg, comments=True)
        except ValueError:
            toks = seg.split()
        if toks:
            out.append(toks)
    return out


def _analyze_shell_command(command: str) -> ReversibilityVerdict:
    """Classify a shell command. Pure function — no I/O.

    Order of precedence (most-restrictive wins):
      CRITICAL  > IRREVERSIBLE > PARTIAL > TRIVIAL
    Redirection / subshell / destructive flag checks run before per-segment
    analysis so the highest-impact signal is captured first.

    Returned verdict's `matched_patterns` lists what triggered the call, in
    audit order. `reasoning` is a flat list of human-readable strings.
    """
    reasoning: list[str] = []
    matched: list[str] = []

    # 1. Redirection ⇒ PARTIAL (writes to file / fd)
    if _REDIRECTION_RE.search(command):
        matched.append("output redirection")
        reasoning.append("Output redirection detected (> / >> / fd-redirect) — file write")
        return ReversibilityVerdict(
            reversibility_class=ReversibilityClass.PARTIAL,
            requires_888_hold=False,
            requires_explicit_ack=False,
            rollback_method="restore from backup or undo the write",
            reversal_window_seconds=300.0,
            blast_radius_estimate="LOW",
            reasoning=reasoning,
            matched_patterns=matched,
        )

    # 2. Command substitution ⇒ PARTIAL (captures may then write downstream)
    if _SUBSHELL_RE.search(command):
        matched.append("command substitution")
        reasoning.append("Command substitution $() or backticks detected — context-dependent write")
        return ReversibilityVerdict(
            reversibility_class=ReversibilityClass.PARTIAL,
            requires_888_hold=False,
            requires_explicit_ack=False,
            rollback_method="review captured output before any commit",
            reversal_window_seconds=300.0,
            blast_radius_estimate="LOW",
            reasoning=reasoning,
            matched_patterns=matched,
        )

    # 3. Per-segment analysis
    segments = _shell_tokenize(command)
    for toks in segments:
        binary = toks[0]
        binary_name = binary.rsplit("/", 1)[-1].lower()
        seg_text = " ".join(toks)
        args_text = seg_text[len(binary) :].strip() if seg_text.startswith(binary) else seg_text

        # 3a. git subcommand routing
        if binary_name == "git":
            sub = toks[1].lower() if len(toks) > 1 else ""
            subcmd_match = re.match(r"--?[a-z-]+", sub) if sub else None
            # Detect `git push --force` / `--force-with-lease` as IRREVERSIBLE
            if sub == "push" and _FORCE_FLAG_RE.search(args_text):
                matched.append("git push --force")
                reasoning.append("`git push --force` is destructive; escalate to IRREVERSIBLE")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method="recovery depends on remote state",
                    reversal_window_seconds=0.0,
                    blast_radius_estimate="HIGH",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            if sub in _GIT_DANGEROUS_SUBCMDS:
                matched.append(f"git {sub or '(none)'}")
                reasoning.append(f"`git {sub}` mutates repository state — escalate to IRREVERSIBLE")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method="git reset / reflog / remote cooperation",
                    reversal_window_seconds=0.0,
                    blast_radius_estimate="MEDIUM",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            if sub in _GIT_SAFE_SUBCMDS or sub == "" or subcmd_match:
                # Safe git subcommand, with-options, or empty — keep scanning.
                continue
            # Unknown git subcommand — fail-closed to IRREVERSIBLE
            matched.append(f"git {sub or '(none)'}")
            reasoning.append(
                f"`git {sub or '(none)'}` subcommand unknown — fail-closed to IRREVERSIBLE"
            )
            return ReversibilityVerdict(
                reversibility_class=ReversibilityClass.IRREVERSIBLE,
                requires_888_hold=True,
                requires_explicit_ack=True,
                rollback_method="manual review",
                reversal_window_seconds=0.0,
                blast_radius_estimate="MEDIUM",
                reasoning=reasoning,
                matched_patterns=matched,
            )

        # 3b. docker subcommand routing
        if binary_name == "docker":
            sub = toks[1].lower() if len(toks) > 1 else ""
            if sub in _DOCKER_DANGEROUS_SUBCMDS:
                matched.append(f"docker {sub}")
                reasoning.append(f"`docker {sub}` mutates container state")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=f"docker {sub} reverse (recreate/restore)",
                    reversal_window_seconds=0.0,
                    blast_radius_estimate="MEDIUM",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            if sub in _DOCKER_SAFE_SUBCMDS or sub in ("image", "container", "volume"):
                continue
            matched.append(f"docker {sub or '(none)'}")
            reasoning.append(f"`docker {sub or '(none)'}` subcommand unknown — fail-closed")
            return ReversibilityVerdict(
                reversibility_class=ReversibilityClass.PARTIAL,
                requires_888_hold=False,
                requires_explicit_ack=False,
                rollback_method="manual review",
                reversal_window_seconds=300.0,
                blast_radius_estimate="MEDIUM",
                reasoning=reasoning,
                matched_patterns=matched,
            )

        # 3c. sed / awk — read-only unless -i / inplace
        if binary_name in _RW_TEXT_COMMANDS:
            if binary_name == "sed" and _INPLACE_FLAG_RE.search(args_text):
                matched.append("sed -i")
                reasoning.append("`sed -i` performs in-place file modification")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.PARTIAL,
                    requires_888_hold=False,
                    requires_explicit_ack=False,
                    rollback_method="restore from VCS or backup",
                    reversal_window_seconds=300.0,
                    blast_radius_estimate="MEDIUM",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            if binary_name == "awk" and (
                _INPLACE_FLAG_RE.search(args_text) or _INPLACE_AWK_RE.search(args_text)
            ):
                matched.append("awk -i inplace")
                reasoning.append("`awk -i inplace` performs in-place file modification")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.PARTIAL,
                    requires_888_hold=False,
                    requires_explicit_ack=False,
                    rollback_method="restore from VCS or backup",
                    reversal_window_seconds=300.0,
                    blast_radius_estimate="MEDIUM",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            # Plain sed/awk ⇒ read-only stream edit
            continue

        # 3d. find with -delete flag ⇒ PARTIAL
        if binary_name == "find":
            if "-delete" in toks[1:]:
                matched.append("find -delete")
                reasoning.append("`find -delete` removes files matching criteria")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.PARTIAL,
                    requires_888_hold=False,
                    requires_explicit_ack=False,
                    rollback_method="restore from backup",
                    reversal_window_seconds=300.0,
                    blast_radius_estimate="MEDIUM",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            continue  # plain find is R0

        # 3e. Destructive command with force/recursive flag ⇒ IRREVERSIBLE
        if binary_name in _R2_SHELL_COMMANDS:
            if binary_name == "rm" and (
                re.search(r"(?:^|\s)-r[fR]?[\b\s]", args_text)
                or re.search(r"(?:^|\s)-[fF]r[\b\s]", args_text)
                or _RECURSIVE_FLAG_RE.search(args_text)
                and _FORCE_FLAG_RE.search(args_text)
            ):
                matched.append("rm -r/-rf/-fr (recursive+force)")
                reasoning.append("`rm` with recursive + force — escalate to IRREVERSIBLE")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=None,
                    reversal_window_seconds=0.0,
                    blast_radius_estimate="HIGH",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )
            matched.append(f"{binary_name} (mutating)")
            reasoning.append(f"`{binary_name}` is a known mutating command")
            return ReversibilityVerdict(
                reversibility_class=ReversibilityClass.PARTIAL,
                requires_888_hold=False,
                requires_explicit_ack=False,
                rollback_method="undo via filesystem checkpoint or git",
                reversal_window_seconds=300.0,
                blast_radius_estimate="MEDIUM",
                reasoning=reasoning,
                matched_patterns=matched,
            )

        # 3f. R0 whitelist
        if binary_name in _R0_SHELL_COMMANDS:
            continue

        # 3g. Unknown binary — fail-closed to PARTIAL (spec)
        matched.append(f"unknown binary: {binary_name}")
        reasoning.append(
            f"Unknown binary `{binary_name}` is not on R0 whitelist — fail-closed to PARTIAL"
        )
        return ReversibilityVerdict(
            reversibility_class=ReversibilityClass.PARTIAL,
            requires_888_hold=False,
            requires_explicit_ack=False,
            rollback_method="manual review",
            reversal_window_seconds=300.0,
            blast_radius_estimate="MEDIUM",
            reasoning=reasoning,
            matched_patterns=matched,
        )

    # All segments were R0 and no redirection/subshell found.
    matched.append("read-only command chain")
    reasoning.append("All segments are read-only; no mutation detected")
    return ReversibilityVerdict(
        reversibility_class=ReversibilityClass.TRIVIAL,
        requires_888_hold=False,
        requires_explicit_ack=False,
        rollback_method=None,
        reversal_window_seconds=None,
        blast_radius_estimate="LOW",
        reasoning=reasoning,
        matched_patterns=matched,
    )


@dataclass
class ReversibilityVerdict:
    """Result of reversibility assessment."""

    reversibility_class: ReversibilityClass
    requires_888_hold: bool
    requires_explicit_ack: bool
    rollback_method: str | None  # How to undo this
    reversal_window_seconds: float | None  # Time window for safe reversal
    blast_radius_estimate: str  # LOW | MEDIUM | HIGH | CRITICAL
    reasoning: list[str] = field(default_factory=list)
    matched_patterns: list[str] = field(default_factory=list)

    @property
    def is_irreversible(self) -> bool:
        return self.reversibility_class in (
            ReversibilityClass.IRREVERSIBLE,
            ReversibilityClass.CRITICAL,
        )

    @property
    def is_critical(self) -> bool:
        return self.reversibility_class == ReversibilityClass.CRITICAL

    @property
    def requires_human_approval(self) -> bool:
        return self.requires_888_hold or self.reversibility_class == ReversibilityClass.CRITICAL


class ReversibilityEngine:
    """
    Assesses reversibility for any tool call.

    Checks:
    1. Tool name patterns (irreversible verbs)
    2. Parameter patterns (dangerous flags)
    3. Target patterns (production targets)

    Usage:
        engine = ReversibilityEngine()
        verdict = engine.assess(tool_id="filesystem_delete", params={"path": "/tmp/test"})
        if verdict.requires_888_hold:
            return HOLD("L01: irreversible action")
    """

    def __init__(self):
        self._irrev_re = [re.compile(p, re.IGNORECASE) for p in _IRREVERSIBLE_PATTERNS]
        self._partial_re = [re.compile(p, re.IGNORECASE) for p in _PARTIAL_PATTERNS]
        self._rev_re = [re.compile(p, re.IGNORECASE) for p in _REVERSIBLE_PATTERNS]
        self._critical_re = [re.compile(p, re.IGNORECASE) for p in _CRITICAL_PATTERNS]

    def assess(
        self,
        tool_id: str,
        params: dict[str, Any],
        tool_base_class: str | None = None,
    ) -> ReversibilityVerdict:
        if tool_base_class is None:
            tool_base_class = classify_tool_base(tool_id)
        """
        Assess reversibility of a tool call.

        Args:
            tool_id: The tool being called
            params: The parameters being passed
            tool_base_class: Optional base class (filesystem, database, network, etc.)

        Returns:
            ReversibilityVerdict with full assessment
        """
        reasoning: list[str] = []
        matched: list[str] = []

        # Flatten params for pattern matching
        params_str = json_dumps_frozensafe(params).lower()
        full_text = f"{tool_id} {params_str}".lower()

        # ── T2 (Forged 2026-08-27 · WIRE 5) ────────────────────────────────
        # Shell-aware pre-emption: for shell-language tool ids with an
        # extractable command string, defer entirely to the deterministic
        # shell analyzer. Regex pass below would over-classify (e.g. tag
        # plain `ls /tmp` as PARTIAL via default base class) or miss
        # redirections entirely.
        if tool_id.lower() in ("bash", "sh", "zsh", "ksh", "csh", "tcsh", "fish"):
            cmd = _shell_extract_command(params or {})
            if cmd:
                return _analyze_shell_command(cmd)
        # ── end T2 hook ───────────────────────────────────────────────────

        # Check critical first
        for pattern_re in self._critical_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"CRITICAL pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.CRITICAL,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=None,
                    reversal_window_seconds=None,
                    blast_radius_estimate="CRITICAL",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Check irreversible
        for pattern_re in self._irrev_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"IRREVERSIBLE pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.IRREVERSIBLE,
                    requires_888_hold=True,
                    requires_explicit_ack=True,
                    rollback_method=self._suggest_rollback(tool_id, params),
                    reversal_window_seconds=0.0,  # Cannot be reversed
                    blast_radius_estimate=self._estimate_blast_radius(tool_id, params),
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Check partial
        partial_count = 0
        for pattern_re in self._partial_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                partial_count += 1
        if partial_count > 0:
            reasoning.append(f"PARTIAL patterns matched: {partial_count}")
            rollback = self._suggest_rollback(tool_id, params)
            return ReversibilityVerdict(
                reversibility_class=ReversibilityClass.PARTIAL,
                requires_888_hold=False,
                requires_explicit_ack=False,
                rollback_method=rollback,
                reversal_window_seconds=self._estimate_reversal_window(tool_id, params),
                blast_radius_estimate=self._estimate_blast_radius(tool_id, params),
                reasoning=reasoning,
                matched_patterns=matched,
            )

        # Check reversible (TRIVIAL or REVERSIBLE)
        for pattern_re in self._rev_re:
            if pattern_re.search(full_text):
                matched.append(pattern_re.pattern)
                reasoning.append(f"REVERSIBLE pattern matched: {pattern_re.pattern}")
                return ReversibilityVerdict(
                    reversibility_class=ReversibilityClass.REVERSIBLE,
                    requires_888_hold=False,
                    requires_explicit_ack=False,
                    rollback_method=None,
                    reversal_window_seconds=None,
                    blast_radius_estimate="LOW",
                    reasoning=reasoning,
                    matched_patterns=matched,
                )

        # Default: check tool base class
        if tool_base_class:
            default_class = self._default_for_base_class(tool_base_class)
            reasoning.append(f"Default class from base: {default_class.name}")
            is_irreversible = default_class in (
                ReversibilityClass.IRREVERSIBLE,
                ReversibilityClass.CRITICAL,
            )
            return ReversibilityVerdict(
                reversibility_class=default_class,
                requires_888_hold=is_irreversible,
                requires_explicit_ack=is_irreversible,
                rollback_method=(
                    None
                    if default_class == ReversibilityClass.TRIVIAL
                    else "manual_rollback_required"
                ),
                reversal_window_seconds=None,
                blast_radius_estimate=(
                    "LOW"
                    if default_class in (ReversibilityClass.TRIVIAL, ReversibilityClass.REVERSIBLE)
                    else "MEDIUM"
                ),
                reasoning=reasoning,
                matched_patterns=[],
            )

        # Unknown — treat as PARTIAL with caution
        reasoning.append("Unknown tool — defaulting to PARTIAL caution")
        return ReversibilityVerdict(
            reversibility_class=ReversibilityClass.PARTIAL,
            requires_888_hold=False,
            requires_explicit_ack=False,
            rollback_method="rollback_not_determined",
            reversal_window_seconds=300.0,  # 5 minutes to figure it out
            blast_radius_estimate="MEDIUM",
            reasoning=reasoning,
            matched_patterns=[],
        )

    def _default_for_base_class(self, base_class: str) -> ReversibilityClass:
        """Default reversibility by tool base class."""
        table = {
            "read": ReversibilityClass.TRIVIAL,
            "search": ReversibilityClass.TRIVIAL,
            "query": ReversibilityClass.TRIVIAL,
            "list": ReversibilityClass.TRIVIAL,
            "fetch": ReversibilityClass.TRIVIAL,
            "write": ReversibilityClass.PARTIAL,
            "edit": ReversibilityClass.PARTIAL,
            "update": ReversibilityClass.PARTIAL,
            "delete": ReversibilityClass.IRREVERSIBLE,
            "execute": ReversibilityClass.PARTIAL,
            "run": ReversibilityClass.PARTIAL,
            "send": ReversibilityClass.IRREVERSIBLE,
            "publish": ReversibilityClass.IRREVERSIBLE,
        }
        return table.get(base_class.lower(), ReversibilityClass.PARTIAL)

    def _estimate_blast_radius(self, tool_id: str, params: dict[str, Any]) -> str:
        """Estimate how widely effects propagate."""
        params_str = json_dumps_frozensafe(params).lower()

        # Production targets
        if any(kw in params_str for kw in ["production", "prod", "main", "primary", "/", "~", "$"]):
            return "CRITICAL"
        # System directories
        if any(
            kw in params_str for kw in ["/etc", "/var", "/usr", "/bin", "/sbin", "/sys", "/proc"]
        ):
            return "HIGH"
        # Home directory
        if "~" in params_str or "$home" in params_str:
            return "MEDIUM"
        # Temp only (path check for blast radius, not actual file operation)
        if "/tmp" in params_str:  # nosec B108
            return "LOW"
        return "MEDIUM"

    def _estimate_reversal_window(self, tool_id: str, params: dict[str, Any]) -> float | None:
        """Estimate seconds available to reverse before permanent."""
        if "ttl" in params:
            return float(params["ttl"])
        if "expires" in params:
            return None  # Unknown
        # Default: 5 minutes for partial actions
        return 300.0

    def _suggest_rollback(self, tool_id: str, params: dict[str, Any]) -> str | None:
        """Suggest a rollback method based on tool and params."""
        if "path" in params or "file" in params or "target" in params:
            path = params.get("path") or params.get("file") or params.get("target")
            return f"Restore from backup: {path}"
        if "id" in params:
            return f"Recreate from ID: {params.get('id')}"
        return "manual_rollback_required"


def json_dumps_frozensafe(obj: Any) -> str:
    """JSON dumps that handle non-serializable objects."""
    import json as _json

    def _default(o: Any) -> Any:
        if hasattr(o, "__dict__"):
            return str(o)
        if hasattr(o, "__slots__"):
            return str(o)
        return str(o)

    return _json.dumps(obj, default=_default, sort_keys=True)


# ── Tool Classification by Base ──────────────────────────────────────────────

TOOL_BASE_CLASSES: dict[str, str] = {
    # Filesystem
    "read_file": "read",
    "write_file": "write",
    "edit_file": "edit",
    "delete_file": "delete",
    "list_files": "list",
    "find_files": "search",
    "grep_text": "search",
    # Database
    "query_database": "query",
    "insert_database": "write",
    "update_database": "update",
    "delete_database": "delete",
    # Network
    "send_message": "send",
    "fetch_url": "fetch",
    "post_data": "send",
    # Execution
    "run_command": "run",
    "execute_code": "execute",
    "run_tests": "execute",
    # Shell / OS (native tool wrappers — TRIVIAL read-equivalents)
    "ls": "list",
    "ps": "list",
    "whoami": "list",
    "hostname": "list",
    "pwd": "list",
    "df": "list",
    "free": "list",
    "uptime": "list",
    "curl": "fetch",
    "wget": "fetch",
    "docker ps": "list",
    "docker images": "list",
    "docker logs": "list",
    "docker inspect": "list",
    "docker stats": "list",
    "docker network ls": "list",
    "docker volume ls": "list",
    "git status": "list",
    "git log": "list",
    "git diff": "list",
    "git branch": "list",
    "git stash list": "list",
    "git show": "list",
    "git reflog": "list",
    # Shell commands with mutation potential (base class only — pattern matching handles specifics)
    "bash": "run",
    "sh": "run",
    "write": "write",
    "mkdir": "write",
    "cp": "write",
    "mv": "write",
    "touch": "write",
    "echo": "write",
    "docker": "run",  # generic docker — pattern matching handles specifics
    "git": "run",  # generic git — pattern matching handles specifics
    # arifOS
    "arif_think": "read",  # Reasoning is reversible
    "arif_observe": "read",
    "arif_fetch": "fetch",
    "arif_critique": "read",
    "arif_kernel_route": "read",
    "arif_memory_recall": "read",
    "arif_measure": "read",
    "arif_judge": "read",  # Judgment is reversible until seal
    "arif_forge": "execute",
    "arif_seal": "execute",  # Sealing is IRREVERSIBLE
    "arif_init": "read",
    "arif_gateway_connect": "execute",
    "arif_compose": "write",
}


def classify_tool_base(tool_id: str) -> str:
    """Get the base class for a tool."""
    return TOOL_BASE_CLASSES.get(tool_id, "unknown")


__all__ = [
    "ReversibilityClass",
    "ReversibilityVerdict",
    "ReversibilityEngine",
    "classify_tool_base",
    "classify_action",
]


def classify_action(tool_id: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Fast pre-gate classifier for agents and native tools.

    Maps reversibility classes to action taxonomy:
      OBSERVE  ← TRIVIAL
      MUTATE   ← REVERSIBLE, PARTIAL
      ATOMIC   ← IRREVERSIBLE, CRITICAL
      UNKNOWN  ← falls through or unknown base class

    This is the fast triage layer ABOVE the full floor enforcement.
    Use before any tool call to quickly classify risk class.

    Used by:
      - OpenCode native tool wrappers (pre-flight gate)
      - arif_kernel_route (fast triage before floor checks)
      - Agent self-model (quick risk assessment)
      - Native bash/filesystem/git/docker wrappers

    Canonical source: /root/.arif/identity.json (version 2)

    Args:
        tool_id: The tool name or command being classified.
                 Examples: "bash", "git status", "write", "rm -rf",
                           "arif_think", "docker ps"
        params: Optional params for context-sensitive classification.

    Returns:
        dict with keys:
          - action_class: "OBSERVE" | "MUTATE" | "ATOMIC" | "UNKNOWN"
          - reversibility: the underlying reversibility class string
          - may_proceed: bool — True if OBSERVE
          - requires_plan: bool — True if MUTATE or ATOMIC
          - requires_arif_approval: bool — True if ATOMIC
          - reason: str — human-readable classification reasoning
    """
    # Lazy import to avoid circular import at module load time.
    # ReversibilityEngine.assess() is only needed when this function
    # is actually called, not when the module loads.
    from arifosmcp.core.reversibility_engine import (
        ReversibilityEngine,
    )

    engine = ReversibilityEngine()
    result = engine.assess(tool_id, params or {})
    rev_class = result.reversibility_class.value

    # Map reversibility → action taxonomy
    rev_to_action: dict[str, str] = {
        "trivial": "OBSERVE",
        "reversible": "MUTATE",
        "partial": "MUTATE",
        "irreversible": "ATOMIC",
        "critical": "ATOMIC",
    }

    action_class = rev_to_action.get(rev_class, "UNKNOWN")
    last_reason = result.reasoning[-1] if result.reasoning else "classified"

    return {
        "action_class": action_class,
        "reversibility": rev_class,
        "may_proceed": action_class == "OBSERVE",
        "requires_plan": action_class in ("MUTATE", "ATOMIC"),
        "requires_arif_approval": action_class == "ATOMIC",
        "reason": last_reason,
        "tool_id": tool_id,
        "verdict": "SEAL" if action_class == "OBSERVE" else "HOLD",
    }
