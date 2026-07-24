#!/usr/bin/env python3
"""Read-only dependency source-of-truth audit for arifOS.

The canonical dependency chain is ``pyproject.toml`` → ``uv.lock`` →
``requirements.txt``.  This checker never resolves, installs, or writes
anything; it verifies the lock, compares the frozen export, and checks that
active root CI workflows use a frozen uv install.
"""

from __future__ import annotations

import re
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
LOCKFILE = ROOT / "uv.lock"
REQUIREMENTS = ROOT / "requirements.txt"
WORKFLOW_DIR = ROOT / ".github" / "workflows"

EXPORT_ARGS = (
    "export",
    "--frozen",
    "--format",
    "requirements-txt",
    "--all-extras",
    "--no-emit-project",
)
PIN_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)==([^\s\\]+)")
UV_SYNC_RE = re.compile(r"(?:^|&&|;|\|\|?)\s*uv\s+sync\b(?P<args>[^#\n]*)")


def _normalise_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _normalise_lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").splitlines()


def _pinned_versions(text: str) -> tuple[dict[str, str], dict[str, list[int]]]:
    versions: dict[str, str] = {}
    duplicates: dict[str, list[int]] = {}
    for line_number, line in enumerate(_normalise_lines(text), start=1):
        match = PIN_RE.match(line)
        if not match:
            continue
        name = _normalise_name(match.group(1))
        if name in versions:
            duplicates.setdefault(name, []).append(line_number)
        versions[name] = match.group(2)
    return versions, duplicates


def _run_uv(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def _failure(failures: list[str], message: str) -> None:
    failures.append(message)
    print(f"FAIL: {message}")


def _ok(message: str) -> None:
    print(f"OK: {message}")


def _command_error(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stderr or result.stdout).strip().splitlines()
    return output[-1] if output else f"exit status {result.returncode}"


def check_lock_metadata(failures: list[str]) -> None:
    try:
        project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
        lock = tomllib.loads(LOCKFILE.read_text(encoding="utf-8"))
        lock_root = next(package for package in lock["package"] if package["name"] == "arifos")
    except (KeyError, OSError, StopIteration, tomllib.TOMLDecodeError) as exc:
        _failure(failures, f"cannot read canonical dependency metadata: {exc}")
        return

    if project.get("version") != lock_root.get("version"):
        _failure(
            failures,
            "pyproject.toml project.version does not match the arifos package in uv.lock: "
            f"{project.get('version')!r} != {lock_root.get('version')!r}",
        )
    else:
        _ok(f"project version agrees with uv.lock ({project['version']})")

    project_python = re.sub(r"\s+", "", project.get("requires-python", ""))
    lock_python = re.sub(r"\s+", "", lock.get("requires-python", ""))
    if project_python != lock_python:
        _failure(
            failures,
            "pyproject.toml requires-python does not match uv.lock: "
            f"{project.get('requires-python')!r} != {lock.get('requires-python')!r}",
        )
    else:
        _ok(f"requires-python agrees with uv.lock ({project.get('requires-python')})")


def check_frozen_lock(failures: list[str]) -> str | None:
    result = _run_uv("lock", "--check")
    if result.returncode:
        _failure(failures, f"uv.lock is not current with pyproject.toml: {_command_error(result)}")
        return None
    _ok("uv.lock is current with pyproject.toml (uv lock --check)")

    export = _run_uv(*EXPORT_ARGS)
    if export.returncode:
        _failure(failures, f"frozen uv export failed: {_command_error(export)}")
        return None
    return export.stdout


def check_requirements(exported: str, failures: list[str]) -> None:
    try:
        requirements_text = REQUIREMENTS.read_text(encoding="utf-8")
    except OSError as exc:
        _failure(failures, f"cannot read requirements.txt: {exc}")
        return

    expected, _ = _pinned_versions(exported)
    actual, duplicates = _pinned_versions(requirements_text)
    if duplicates:
        _failure(failures, f"requirements.txt contains duplicate pins: {sorted(duplicates)}")

    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    mismatched = sorted(
        name for name in expected.keys() & actual.keys() if expected[name] != actual[name]
    )
    if missing or extra or mismatched:
        details = []
        if missing:
            details.append(f"missing={missing[:8]}")
        if extra:
            details.append(f"extra={extra[:8]}")
        if mismatched:
            details.append(
                "version_mismatch="
                + str([(name, actual[name], expected[name]) for name in mismatched[:8]])
            )
        _failure(
            failures,
            "requirements.txt pins disagree with frozen uv export (" + "; ".join(details) + ")",
        )
        return

    if _normalise_lines(requirements_text) != _normalise_lines(exported):
        _failure(failures, "requirements.txt is not the deterministic frozen uv export")
        return

    _ok(f"requirements.txt agrees with frozen uv export ({len(expected)} pinned packages)")


def _workflow_commands(path: Path) -> list[tuple[int, str]]:
    commands: list[tuple[int, str]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith(("- name:", "name:")):
            continue
        if line.startswith("- run:"):
            line = line[len("- run:") :].strip()
        elif line.startswith("run:"):
            line = line[len("run:") :].strip()
        if line.startswith(("echo ", "printf ")):
            continue
        if UV_SYNC_RE.search(line):
            commands.append((line_number, line))
    return commands


def check_ci_installs(failures: list[str]) -> None:
    if not WORKFLOW_DIR.is_dir():
        _failure(failures, f"active workflow directory is missing: {WORKFLOW_DIR}")
        return

    workflow_files = sorted((*WORKFLOW_DIR.glob("*.yml"), *WORKFLOW_DIR.glob("*.yaml")))
    commands: list[tuple[Path, int, str]] = []
    for workflow in workflow_files:
        commands.extend((workflow, line, command) for line, command in _workflow_commands(workflow))

    if not commands:
        _failure(failures, "no active root workflow uv sync install was found")
        return

    unfrozen = [
        (workflow, line, command)
        for workflow, line, command in commands
        if "--frozen" not in command and "--locked" not in command
    ]
    if unfrozen:
        for workflow, line, command in unfrozen:
            _failure(
                failures,
                (
                    f"{workflow.relative_to(ROOT)}:{line} uses uv sync without "
                    f"--frozen/--locked: {command}"
                ),
            )
        return

    _ok(f"active root CI uv sync installs are frozen ({len(commands)} commands)")


def main() -> int:
    print("== arifOS dependency SOT audit ==")
    failures: list[str] = []
    for path in (PYPROJECT, LOCKFILE, REQUIREMENTS, WORKFLOW_DIR):
        if not path.exists():
            _failure(failures, f"missing canonical dependency input: {path.relative_to(ROOT)}")

    if failures:
        print(f"DRIFT DETECTED ({len(failures)} issue(s))")
        return 1

    check_lock_metadata(failures)
    exported = check_frozen_lock(failures)
    if exported is not None:
        check_requirements(exported, failures)
    check_ci_installs(failures)

    print("== Verdict ==")
    if failures:
        print(f"DRIFT DETECTED ({len(failures)} issue(s))")
        return 1
    print("NO DRIFT DETECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
