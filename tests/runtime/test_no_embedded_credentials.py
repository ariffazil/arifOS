"""
B1 Secret Containment — Generic Credential-Shape Detection
============================================================

Forged 2026-07-23. Companion to the local hardening of the assigned scope:
  - arifosmcp/.env.example
  - scripts/supabase_smoke_test.py
  - scripts/aaa_cockpit.py

The tests in this file detect EMBEDDED credential-shaped literals in source
files. Detection is purely structural — no leaked value, no hash matching, no
print of input. A violation is reported by a LINE NUMBER only.

Patterns enforced:

  1. **Credential DSN literals** in Python scripts — any Python string that
     looks like ``postgresql://<user>:<password>@<host>`` with a literal
     (non-template) password component. Single-line ``#`` comments are masked
     so a documenting DSN in a comment does not trigger a match.

  2. **Non-placeholder passwords in .env.example files** — any uncommented
     ``<NAME>_PASSWORD=<value>`` (or similar) where the value is not a
     recognised placeholder. Placeholders recognised:
       - empty (``PASSWORD=``)
       - ``CHANGE_ME*`` / ``change_me*``
       - ``<...>`` angle-bracket placeholders
       - ``${...}`` template substitution
       - python-docstring style ``your_*`` / ``example_*`` / ``placeholder*``
       - ``...`` / ``***`` / ``xxx*`` / ``XXXX`` explicit redaction

  3. **Fail-closed behavior** — the scripts in scope refuse to run when
     required env vars (VAULT999_DB, SUPABASE_HOST, SUPABASE_PASSWORD) are
     missing or empty. We exec the helper functions in isolation so no DB
     connection is attempted.

DO NOT extend this file to test other repos or other secrets without an
explicit F13 review — coverage is intentionally narrow to the B1 scope.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# In-scope files for the B1 hardening.
ENV_EXAMPLE = REPO_ROOT / "arifosmcp" / ".env.example"
SCRIPT_AAA_COCKPIT = REPO_ROOT / "scripts" / "aaa_cockpit.py"
SCRIPT_SUPABASE_SMOKE = REPO_ROOT / "scripts" / "supabase_smoke_test.py"

# ── Detection patterns ───────────────────────────────────────────────────────

# postgresql://user:password@host — literal password. Template substitutions
# like ${VAR} or {VAR} are excluded by the negative-lookahead groups.
_DSN_PATTERN = re.compile(
    r"(?:postgresql|postgres)://[^:/\s${}]+:[^@\s${}<>]+@[^/\s]+"
)

# *_PASSWORD=<value> in .env.example. Single-line comments are excluded.
_PASSWORD_LINE = re.compile(
    r"^\s*(?P<key>[A-Z][A-Z0-9_]*PASSWORD)\s*=\s*(?P<value>\S*)\s*$"
)

# Placeholder values that are explicitly allowed in template files.
_PLACEHOLDER_TOKENS = (
    "CHANGE_ME",
    "change_me",
    "<your",
    "<placeholder",
    "<password>",
    "<pass>",
    "<token>",
    "<secret>",
    "<key>",
    "<value>",
    "${",                         # template substitution start
    "your_",                      # snake_case "your_secret" wording
    "example_",
    "placeholder",
    "PLACEHOLDER",
    "EXAMPLE",
    "REDACTED",
    "redacted",
    "...",                        # ellipsis
    "***",                        # asterisk redaction
    "xxx",                        # lowercase x redaction
    "XXXX",
)

# ── Helpers ──────────────────────────────────────────────────────────────────


def _mask_single_line_comments(src: str) -> str:
    """Replace single-line ``#`` comments with spaces so any DSN they describe
    cannot accidentally match the regex. Strings are NOT masked — we want
    inside-string literals to be caught."""
    out = list(src)
    i = 0
    n = len(src)
    in_string = None
    while i < n:
        ch = src[i]
        if in_string:
            if ch == "\\" and i + 1 < n:
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            in_string = ch
            i += 1
            continue
        if ch == "#":
            # Mask the rest of the line (but keep the newline).
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
            continue
        i += 1
    return "".join(out)


def _find_dsn_violations(path: Path) -> list[int]:
    """Return line numbers (1-based) containing literal credential DSNs.

    Values are NEVER recorded or returned — only line numbers.
    """
    src = path.read_text(encoding="utf-8")
    masked = _mask_single_line_comments(src)
    hits: list[int] = []
    for m in _DSN_PATTERN.finditer(masked):
        hits.append(masked.count("\n", 0, m.start()) + 1)
    return hits


def _is_placeholder_value(value: str) -> bool:
    """Return True if the .env value is a recognised placeholder."""
    if not value:
        return True
    v = value.strip()
    if v in _PLACEHOLDER_TOKENS:
        return True
    for token in _PLACEHOLDER_TOKENS:
        if v.startswith(token) or v.endswith(token):
            return True
    return False


def _find_password_line_violations(path: Path) -> list[tuple[int, str]]:
    """Return (line_number, key) for *_PASSWORD= lines whose value is not a
    placeholder. Values are NEVER returned or printed — only the key name."""
    violations: list[tuple[int, str]] = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        m = _PASSWORD_LINE.match(line)
        if not m:
            continue
        key = m.group("key")
        value = m.group("value")
        if not _is_placeholder_value(value):
            violations.append((lineno, key))
    return violations


def _extract_top_level_function(source: str, func_name: str) -> str:
    """Return the source of a top-level function, falling back to text-walking
    for sources that do not parse cleanly (e.g. contain a syntax-incompatible
    late import)."""
    try:
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return ast.get_source_segment(source, node) or ""
    except SyntaxError:
        pass
    # Fallback: slice between ``def <func_name>`` and the next ``def`` or
    # ``class`` at column 0.
    lines = source.splitlines(keepends=True)
    start = end = None
    for i, line in enumerate(lines):
        if start is None and line.startswith(f"def {func_name}("):
            start = i
            continue
        if start is not None and (line.startswith("def ") or line.startswith("class ")):
            end = i
            break
    if start is None:
        raise AssertionError(f"Function {func_name!r} not found at module top level")
    if end is None:
        end = len(lines)
    return "".join(lines[start:end])


def _extract_helper_block(source: str) -> str:
    """Return all top-level function definitions in ``source`` (regardless of
    position relative to imports). This lets the test exec the helpers and
    their internal dependencies without triggering the module's own imports."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Fallback to text slicing — should not happen for our scope.
        return _extract_top_level_function(source, "_get_pool_url")

    blocks: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            seg = ast.get_source_segment(source, node) or ""
            if seg:
                blocks.append(seg)
    return "\n\n\n".join(blocks)


def _is_assignment_to_any_dsn_name(node: ast.stmt) -> str | None:
    """Return the assigned name if the node is a module-level DSN literal."""
    if not isinstance(node, ast.Assign):
        return None
    for target in node.targets:
        name = getattr(target, "id", None)
        if name in {"POOL_URL", "_POOL_URL", "POOL", "POOL_DSN", "DATABASE_URL"}:
            return name
    return None


def _exec_helper_in_clean_env(
    source: str,
    func_name: str,
    env: dict[str, str] | None = None,
    extra_names: dict[str, object] | None = None,
):
    """Exec a top-level helper function in a clean namespace with the
    provided env vars. Returns ("ok", value) / ("exit", code) / ("error", str).

    The helper block (all top-level defs before the first import) is extracted
    so we do not trigger unrelated imports (e.g. asyncpg, the adapter
    module) but the helper still has access to its internal helpers."""
    import os
    import sys

    block_src = _extract_helper_block(source)
    # Make sure the helper's dependencies are present in the namespace.
    ns: dict[str, object] = {"__name__": f"b1_test_{func_name}", "os": os, "sys": sys}
    if extra_names:
        ns.update(extra_names)

    saved = os.environ.copy()
    try:
        for k in list(os.environ):
            os.environ.pop(k, None)
        for k, v in (env or {}).items():
            os.environ[k] = v
        try:
            exec(compile(block_src, f"<isolated:{func_name}>", "exec"), ns)  # noqa: S102
        except SystemExit as exc:
            return ("exit", exc.code)
        except Exception as exc:
            return ("error", repr(exc))
        try:
            result = ns[func_name]()
            return ("ok", result)
        except SystemExit as exc:
            return ("exit", exc.code)
        except Exception as exc:
            return ("error", repr(exc))
    finally:
        for k in list(os.environ):
            os.environ.pop(k, None)
        for k, v in saved.items():
            os.environ[k] = v


# ── Tests: static (no DB, no network) ───────────────────────────────────────


class TestEnvExampleHasNoEmbeddedCredentials:
    """arifosmcp/.env.example must not contain a real-looking password literal."""

    def test_supabase_password_is_placeholder(self):
        violations = _find_password_line_violations(ENV_EXAMPLE)
        reported = [(ln, key) for ln, key in violations if key == "SUPABASE_PASSWORD"]
        assert not reported, (
            f"arifosmcp/.env.example contains a non-placeholder SUPABASE_PASSWORD "
            f"on line(s): {[ln for ln, _ in reported]}"
        )

    def test_no_other_password_is_non_placeholder(self):
        # Any other *_PASSWORD= line in the template must also be a placeholder.
        violations = _find_password_line_violations(ENV_EXAMPLE)
        non_supa = [(ln, key) for ln, key in violations if key != "SUPABASE_PASSWORD"]
        assert not non_supa, (
            f"arifosmcp/.env.example contains non-placeholder password(s) on "
            f"line(s): {non_supa}"
        )

    def test_no_literal_credential_dsn_in_env_example(self):
        src = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
        hits: list[int] = []
        for lineno, line in enumerate(src, start=1):
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            if _DSN_PATTERN.search(stripped):
                # Allow template-style DSNs referencing ${VAR} or {VAR}.
                if "{SUPABASE_PASSWORD}" in stripped or "${" in stripped:
                    continue
                hits.append(lineno)
        assert not hits, (
            f"arifosmcp/.env.example contains a literal credential DSN on "
            f"line(s): {hits}"
        )


class TestScriptsHaveNoEmbeddedCredentials:
    """Python scripts in scope must not contain literal credential DSNs."""

    @pytest.mark.parametrize(
        "path",
        [SCRIPT_AAA_COCKPIT, SCRIPT_SUPABASE_SMOKE],
        ids=["scripts/aaa_cockpit.py", "scripts/supabase_smoke_test.py"],
    )
    def test_no_literal_credential_dsn(self, path: Path):
        violations = _find_dsn_violations(path)
        assert not violations, (
            f"{path.relative_to(REPO_ROOT)} contains a literal credential DSN "
            f"on line(s): {violations}"
        )

    @pytest.mark.parametrize(
        "path",
        [SCRIPT_AAA_COCKPIT, SCRIPT_SUPABASE_SMOKE],
        ids=["scripts/aaa_cockpit.py", "scripts/supabase_smoke_test.py"],
    )
    def test_no_module_level_dsn_assignment(self, path: Path):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        bad = [
            (node.lineno, _is_assignment_to_any_dsn_name(node))
            for node in tree.body
            if _is_assignment_to_any_dsn_name(node)
        ]
        assert not bad, (
            f"{path.relative_to(REPO_ROOT)} still has a module-level DSN "
            f"assignment on line(s): {bad}"
        )


# ── Tests: fail-closed behavior ──────────────────────────────────────────────


class TestAaaCockpitFailsClosed:
    """scripts/aaa_cockpit.py must exit when VAULT999_DB is missing/empty."""

    def test_missing_vault999_db_exits(self):
        src = SCRIPT_AAA_COCKPIT.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(src, "_get_pool_url", env={})
        assert result[0] == "exit", (
            f"scripts/aaa_cockpit.py::_get_pool_url must exit when VAULT999_DB "
            f"is missing, got: {result[0]}"
        )

    def test_whitespace_only_vault999_db_exits(self):
        src = SCRIPT_AAA_COCKPIT.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(
            src, "_get_pool_url", env={"VAULT999_DB": "   "}
        )
        assert result[0] == "exit", (
            f"scripts/aaa_cockpit.py::_get_pool_url must exit on whitespace-only "
            f"VAULT999_DB, got: {result[0]}"
        )

    def test_set_vault999_db_returns_dsn_string(self):
        # Use a placeholder-looking DSN so we never embed a real credential
        # in the test fixture.
        sample = "postgresql://CHANGE_ME_USER:CHANGE_ME_PASS@db.example.invalid:5432/postgres"
        src = SCRIPT_AAA_COCKPIT.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(
            src, "_get_pool_url", env={"VAULT999_DB": sample}
        )
        assert result[0] == "ok", (
            f"scripts/aaa_cockpit.py::_get_pool_url must return the env DSN, "
            f"got: {result[0]}"
        )
        assert isinstance(result[1], str) and result[1], "DSN must be a non-empty string"


class TestSupabaseSmokeTestFailsClosed:
    """scripts/supabase_smoke_test.py must exit when any required env is missing."""

    def test_missing_vault999_db_exits(self):
        src = SCRIPT_SUPABASE_SMOKE.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(src, "_get_pool_url", env={})
        assert result[0] == "exit", (
            f"scripts/supabase_smoke_test.py::_get_pool_url must exit when "
            f"VAULT999_DB is missing, got: {result[0]}"
        )

    def test_missing_supabase_host_exits(self):
        src = SCRIPT_SUPABASE_SMOKE.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(
            src,
            "_supabase_host",
            env={"VAULT999_DB": "postgresql://u:p@db.invalid:5432/x"},
        )
        assert result[0] == "exit", (
            f"scripts/supabase_smoke_test.py::_supabase_host must exit when "
            f"SUPABASE_HOST is missing, got: {result[0]}"
        )

    def test_missing_supabase_password_exits(self):
        src = SCRIPT_SUPABASE_SMOKE.read_text(encoding="utf-8")
        result = _exec_helper_in_clean_env(
            src,
            "_supabase_password",
            env={
                "VAULT999_DB": "postgresql://u:p@db.invalid:5432/x",
                "SUPABASE_HOST": "db.example.invalid",
            },
        )
        assert result[0] == "exit", (
            f"scripts/supabase_smoke_test.py::_supabase_password must exit when "
            f"SUPABASE_PASSWORD is missing, got: {result[0]}"
        )

    def test_set_required_envs_returns_strings(self):
        sample_dsn = "postgresql://CHANGE_ME_USER:CHANGE_ME_PASS@db.example.invalid:5432/postgres"
        src = SCRIPT_SUPABASE_SMOKE.read_text(encoding="utf-8")
        for fn, env in (
            ("_get_pool_url", {"VAULT999_DB": sample_dsn}),
            ("_supabase_host", {"SUPABASE_HOST": "db.example.invalid"}),
            ("_supabase_password", {"SUPABASE_PASSWORD": "CHANGE_ME_PASSWORD"}),
        ):
            result = _exec_helper_in_clean_env(src, fn, env=env)
            assert result[0] == "ok", (
                f"scripts/supabase_smoke_test.py::{fn} must return the env "
                f"value when set, got: {result[0]}"
            )
            assert isinstance(result[1], str) and result[1]


# ── Smoke: the test module itself compiles ───────────────────────────────────


def test_module_compiles():
    import py_compile

    py_compile.compile(str(Path(__file__).resolve()), doraise=True)
