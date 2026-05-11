#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ALL_ZERO = "0" * 40
SAFETY_TEST_PATTERNS = [
    re.compile(r"^tests/.+", re.IGNORECASE),
    re.compile(r"^tests/.*/", re.IGNORECASE),
]
SAFETY_KEYWORDS = (
    "constitutional",
    "adversarial",
    "security",
    "floor",
    "judge",
    "mind_reason",
)
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


@dataclass
class Finding:
    level: str
    message: str


def run_git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")
    return proc.stdout.strip()


def parse_remote_repo(remote_url: str) -> str:
    m = re.search(r"github\.com[/:]([^/]+)/([^/.]+)(?:\.git)?$", remote_url)
    if not m:
        return ""
    owner = m.group(1).strip().lower()
    repo = m.group(2).strip().lower()
    return f"{owner}/{repo}"


def read_push_updates() -> list[tuple[str, str, str, str]]:
    updates = []
    for line in sys.stdin.read().splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 4:
            continue
        updates.append((parts[0], parts[1], parts[2], parts[3]))
    return updates


def commit_list(old_sha: str, new_sha: str) -> list[str]:
    if new_sha == ALL_ZERO:
        return []
    if old_sha == ALL_ZERO:
        out = run_git(["rev-list", new_sha, "--not", "--remotes"])
        return [c for c in out.splitlines() if c]
    out = run_git(["rev-list", f"{old_sha}..{new_sha}"])
    return [c for c in out.splitlines() if c]


def changed_files(commits: list[str]) -> list[tuple[str, str]]:
    files: list[tuple[str, str]] = []
    for commit in commits:
        out = run_git(["diff-tree", "--no-commit-id", "--name-status", "-r", commit])
        for line in out.splitlines():
            if not line.strip():
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            status, path = parts
            files.append((status.strip(), path.strip()))
    return files


def read_commit_bodies(commits: list[str]) -> list[str]:
    bodies = []
    for commit in commits:
        body = run_git(["show", "-s", "--format=%B", commit])
        bodies.append(body)
    return bodies


def declared_repo_from_body(body: str) -> str | None:
    for line in body.splitlines():
        if line.lower().startswith("repo="):
            return line.split("=", 1)[1].strip().lower()
    return None


def scan_for_secrets(paths: list[str]) -> list[str]:
    hits: list[str] = []
    for p in paths:
        fp = Path(p)
        if not fp.exists() or fp.is_dir():
            continue
        try:
            content = fp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                hits.append(p)
                break
    return hits


def validate_changed_json(paths: list[str]) -> list[str]:
    bad: list[str] = []
    for p in paths:
        if not p.endswith(".json"):
            continue
        if "charter" not in p and "manifest" not in p:
            continue
        fp = Path(p)
        if not fp.exists() or fp.is_dir():
            continue
        try:
            json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            bad.append(p)
    return bad


def is_safety_test(path: str) -> bool:
    if not path.endswith(".py"):
        return False
    p = path.lower()
    if not any(rx.match(path) for rx in SAFETY_TEST_PATTERNS):
        return False
    return any(k in p for k in SAFETY_KEYWORDS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Severity-based repo guard for pre-push")
    parser.add_argument("--remote-name", default="origin")
    parser.add_argument("--remote-url", default="")
    args = parser.parse_args()

    findings: list[Finding] = []
    updates = read_push_updates()
    if not updates:
        findings.append(Finding("INFO", "No ref updates to validate."))
        print_findings(findings)
        return 0

    remote_repo = parse_remote_repo(args.remote_url)
    remote_slug = remote_repo.split("/", 1)[1] if "/" in remote_repo else remote_repo
    all_commits: list[str] = []
    pushes_to_main = False

    for local_ref, local_sha, _remote_ref, old_remote_sha in updates:
        if local_ref == "refs/heads/main":
            pushes_to_main = True
        all_commits.extend(commit_list(old_remote_sha, local_sha))

    # de-dupe preserving order
    seen = set()
    commits = [c for c in all_commits if not (c in seen or seen.add(c))]

    if not commits:
        findings.append(Finding("INFO", "No new commits detected in push range."))
        print_findings(findings)
        return 0

    commit_bodies = read_commit_bodies(commits)

    if pushes_to_main:
        findings.append(Finding("WARN", "Direct push to main detected; PR flow is preferred."))
        for idx, body in enumerate(commit_bodies):
            declared_repo = declared_repo_from_body(body)
            if not declared_repo:
                findings.append(
                    Finding(
                        "HOLD",
                        f"Commit {commits[idx][:8]} missing REPO=<owner/repo> trailer.",
                    )
                )
            elif remote_repo and declared_repo not in {remote_repo, remote_slug}:
                findings.append(
                    Finding(
                        "HOLD",
                        "Commit "
                        f"{commits[idx][:8]} REPO trailer mismatch "
                        f"(declared={declared_repo}, remote={remote_repo}).",
                    )
                )
            elif remote_repo and declared_repo == remote_slug:
                findings.append(
                    Finding(
                        "WARN",
                        "Commit "
                        f"{commits[idx][:8]} uses legacy REPO trailer format '{remote_slug}'; "
                        f"prefer '{remote_repo}'.",
                    )
                )

    files = changed_files(commits)
    changed_paths = sorted({p for _s, p in files})

    deleted_safety = [p for s, p in files if s.startswith("D") and is_safety_test(p)]
    if deleted_safety:
        findings.append(
            Finding(
                "BLOCK",
                "Deletion of safety-critical tests detected: " + ", ".join(deleted_safety),
            )
        )

    bad_json = validate_changed_json(changed_paths)
    if bad_json:
        findings.append(
            Finding("BLOCK", "Malformed governance JSON detected: " + ", ".join(bad_json))
        )

    secret_hits = scan_for_secrets(changed_paths)
    if secret_hits:
        findings.append(
            Finding("BLOCK", "Potential secret patterns detected in: " + ", ".join(secret_hits))
        )

    if not findings:
        findings.append(Finding("INFO", "No issues found by repo guard."))

    print_findings(findings)

    has_block = any(f.level == "BLOCK" for f in findings)
    has_hold = any(f.level == "HOLD" for f in findings)
    hold_ack = os.getenv("ARIFOS_HOLD_ACK", "").strip().lower() in {"1", "true", "yes"}

    if has_block:
        return 1
    if has_hold and not hold_ack:
        print("[HOLD] Acknowledgment required: set ARIFOS_HOLD_ACK=1 to proceed.")
        return 1
    return 0


def print_findings(findings: list[Finding]) -> None:
    order = {"INFO": 0, "WARN": 1, "HOLD": 2, "BLOCK": 3}
    for f in sorted(findings, key=lambda x: order.get(x.level, 99)):
        print(f"[{f.level}] {f.message}")


if __name__ == "__main__":
    raise SystemExit(main())
