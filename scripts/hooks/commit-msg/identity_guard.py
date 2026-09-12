#!/usr/bin/env python3
"""
arifOS IDENTITY GUARD — runs as `git commit` commit-msg hook.

Incident that forged this (2026-09-13 00:21-00:29 MYT, KVM8/forge):
  A background worker wrote 9 lines of change to memory/identity/SOUL.md, then
  committed them inside ffe6cbdd9 whose subject was "fix(probe): tolerate
  stateless FastMCP". SOUL.md appears nowhere in that message. The canonical
  identity of the federation changed silently under an unrelated commit subject,
  cutting two F13_RATIFIED_CHAT references and injecting a stale pointer.

What this guard does — and deliberately does NOT do:
  It is a DISCLOSURE gate, not a content freeze. A legitimate, F13-authorized
  identity change must still be possible; it just cannot ride along silently.

  BLOCKS when a commit stages anything under PROTECTED and the commit message
  does not disclose it (path mention or explicit marker).
  ALLOWS otherwise. Every touch of PROTECTED is logged to the audit ledger,
  including the allowed ones (F11).

  Also BLOCKS a structural downgrade: turning a protected file into a symlink,
  or changing its mode. That is the fan-out vector (one write mutating every
  linked surface) that made this incident 29 surfaces wide.

Bypass: honest, logged, and attributable — never silent.
  IDENTITY_GUARD_ACK="<who> <why>" git commit ...
  The reason is recorded in the ledger with the commit subject.

Exit 0 -> allow commit
Exit 1 -> BLOCK commit (diagnostics on stderr)

DITEMPA BUKAN DIBERI
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

def _resolve_repo_root() -> Path:
    """Resolve the repo THIS hook was invoked in — never a hardcoded path.

    Bug that forged this (2026-09-13): the first version hardcoded
    /root/arifOS. Invoked from any other repo it inspected arifOS's (clean)
    index and therefore allowed every commit. A guard that checks the wrong
    repository is worse than no guard: it produces a passing test while
    protecting nothing.
    """
    env_repo = os.environ.get("IDENTITY_GUARD_REPO")
    if env_repo:
        return Path(env_repo)
    r = subprocess.run("git rev-parse --show-toplevel", shell=True,
                       capture_output=True, text=True, timeout=30)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    # last resort: the process cwd (git runs commit-msg hooks from repo root)
    return Path.cwd()


REPO_ROOT = _resolve_repo_root()
PROTECTED = ("memory/identity/",)
LEDGER_DIR = Path("/root/.hermes/governance")
LEDGER = LEDGER_DIR / "identity-guard-audit.jsonl"
ACK_ENV = "IDENTITY_GUARD_ACK"

# words that count as disclosure of an identity change in the message
DISCLOSURE_TOKENS = (
    "memory/identity",
    "SOUL.md",
    "soul.md",
    "identity file",
    "identity canon",
    "IDENTITY-CHANGE",
)


def sh(cmd: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, cwd=str(cwd),
                          capture_output=True, text=True, timeout=60)


def staged_files() -> list:
    """Files staged in this commit (name + status)."""
    out = sh("git diff --cached --name-status").stdout
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0], parts[-1]))
    return rows


def is_protected(path: str) -> bool:
    return any(path.startswith(p) or path == p.rstrip("/") for p in PROTECTED)


def structural_downgrade(status: str, path: str) -> str:
    """Return a reason string if this stage turns a protected file into a
    symlink or changes its mode; else empty string."""
    if status.startswith("D"):
        return f"deletes protected file {path}"
    # mode recorded in the index for this path
    ls = sh(f"git ls-files -s -- {path}").stdout.strip()
    if not ls:
        return ""
    mode = ls.split()[0]
    if mode == "120000":
        return f"{path} staged as SYMLINK (git mode 120000) — fan-out vector"
    if mode not in ("100644", "100755"):
        return f"{path} staged with unusual git mode {mode}"
    return ""


def msg_discloses(msg: str) -> bool:
    return any(tok in msg for tok in DISCLOSURE_TOKENS)


def marker_discloses(msg: str) -> bool:
    """Explicit human-readable marker, e.g. 'IDENTITY-CHANGE: restore F13 refs'."""
    return bool(re.search(r"IDENTITY-CHANGE\s*:", msg, re.IGNORECASE))


def audit(event: str, **kw):
    try:
        LEDGER_DIR.mkdir(parents=True, exist_ok=True)
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "event": event, "repo": str(REPO_ROOT),
               "pid": os.getpid(), "uid": os.getuid(), **kw}
        with open(LEDGER, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        # never let the ledger break a commit decision
        pass


def main() -> int:
    if len(sys.argv) < 2:
        print("[identity-guard] no message file arg — allowing (hook misuse)", file=sys.stderr)
        return 0

    msg_path = Path(sys.argv[1])
    try:
        msg = msg_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[identity-guard] cannot read message file: {e} — allowing", file=sys.stderr)
        return 0

    subject = msg.split("\n")[0][:120]
    staged = staged_files()
    protected = [(s, p) for s, p in staged if is_protected(p)]

    if not protected:
        return 0  # not an identity commit — stay out of the way

    ack = os.environ.get(ACK_ENV, "").strip()

    # ---- structural downgrade is never silently allowed ----
    structural = []
    for st, p in protected:
        r = structural_downgrade(st, p)
        if r:
            structural.append((st, p, r))

    disclosed = msg_discloses(msg) or marker_discloses(msg)

    if structural and not ack:
        print("=" * 74, file=sys.stderr)
        print("IDENTITY GUARD — BLOCKED (structural downgrade)", file=sys.stderr)
        print("=" * 74, file=sys.stderr)
        for st, p, r in structural:
            print(f"  {st:<4} {r}", file=sys.stderr)
        print("\n  Why: a protected identity file became a symlink or changed mode.", file=sys.stderr)
        print("  That couples this repo to every other surface sharing the inode —", file=sys.stderr)
        print("  one write then mutates all of them at once.", file=sys.stderr)
        print(f"\n  If F13 authorized this, re-run with:\n"
              f"    {ACK_ENV}=\"<who> <why>\" git commit ...", file=sys.stderr)
        audit("BLOCK_structural", subject=subject,
              paths=[p for _, p, _ in structural])
        return 1

    if not disclosed and not ack:
        print("=" * 74, file=sys.stderr)
        print("IDENTITY GUARD — BLOCKED (undisclosed identity change)", file=sys.stderr)
        print("=" * 74, file=sys.stderr)
        print("  This commit stages canonical identity file(s):", file=sys.stderr)
        for st, p in protected:
            print(f"    {st:<4} {p}", file=sys.stderr)
        print(f"\n  But the commit message never says so. Subject was:\n"
              f"    {subject}", file=sys.stderr)
        print("\n  Precedent: ffe6cbdd9 (2026-09-13) moved 9 lines of SOUL.md under the", file=sys.stderr)
        print("  subject \"fix(probe): tolerate stateless FastMCP\". Two F13_RATIFIED_CHAT", file=sys.stderr)
        print("  references were cut and nobody could see it in the log.", file=sys.stderr)
        print("\n  Fix — disclose it, one of:", file=sys.stderr)
        print("    * mention the path or filename in the message", file=sys.stderr)
        print("      (e.g. \"memory/identity/SOUL.md\" or \"SOUL.md\")", file=sys.stderr)
        print("    * add an explicit marker line:", file=sys.stderr)
        print("      IDENTITY-CHANGE: <what changed and under whose authority>", file=sys.stderr)
        print(f"\n  Or, if F13 authorized and you must keep this message verbatim:\n"
              f"    {ACK_ENV}=\"<who> <why>\" git commit ...", file=sys.stderr)
        audit("BLOCK_undisclosed", subject=subject, paths=[p for _, p in protected])
        return 1

    # ---- allowed: record it ----
    audit("ALLOW" if not ack else "ALLOW_with_ack",
          subject=subject, paths=[p for _, p in protected],
          disclosed=disclosed, ack=ack or None,
          structural=[r for _, _, r in structural] if structural else None)
    tag = "ack'd" if ack else "disclosed"
    print(f"[identity-guard] identity change {tag} — {len(protected)} protected file(s); "
          f"logged to {LEDGER}", file=sys.stderr)
    return 0


def selftest() -> int:
    """Run the guard against a throwaway repo and verify it BLOCKS what it
    should and ALLOWS what it should. A guard that only blocks is a brick;
    a guard that only allows is invisible. Both directions must work.

    Returns 0 on full pass, 1 on any failure. Never touches the canonical
    identity file — uses a throwaway repo under /tmp.
    """
    import shutil, tempfile
    tmp = Path(tempfile.mkdtemp(prefix="idguard-selftest-"))
    repo = tmp / "repo"
    repo.mkdir()
    try:
        def sh(cmd: str, cwd: Path = repo, env=None) -> subprocess.CompletedProcess:
            e = dict(os.environ); e.pop(ACK_ENV, None)
            if env: e.update(env)
            return subprocess.run(cmd, shell=True, cwd=str(cwd),
                                  capture_output=True, text=True, timeout=30, env=e)

        sh("git init -q .")
        sh("git config user.email t@t.local")
        sh("git config user.name tester")
        sh("git config --local core.hooksPath .git/hooks")
        (repo / "memory/identity").mkdir(parents=True)
        (repo / "scripts/hooks/commit-msg").mkdir(parents=True)
        (repo / ".git/hooks").mkdir(parents=True, exist_ok=True)
        (repo / "memory/identity/SOUL.md").write_text("# SOUL v1\n")

        # ── INSTALL the guard + hook into the throwaway repo ──────────────
        # Without this, git commit runs with NO hook: every case "allows"
        # trivially and the disclosed-identity cases pass for the wrong
        # reason. A selftest that tests nothing reports 4/6 and looks alive.
        shutil.copy(Path(__file__), repo / "scripts/hooks/commit-msg/identity_guard.py")
        hook = repo / ".git/hooks/commit-msg"
        hook.write_text(
            "#!/usr/bin/env bash\n"
            'REPO_ROOT="$(git rev-parse --show-toplevel)"\n'
            'GUARD="$REPO_ROOT/scripts/hooks/commit-msg/identity_guard.py"\n'
            '[[ -f "$GUARD" ]] || exit 0\n'
            'python3 "$GUARD" "$@"\n')
        hook.chmod(0o755)
        if not hook.stat().st_mode & 0o111:
            print("  [FAIL] hook tidak executable dalam selftest — git akan skip dia")
            return 1

        sh("git add -A && git commit -q -m init")

        # sanity: hook must actually fire, or every result below is meaningless
        canary = (repo / "memory/identity/SOUL.md")
        canary.write_text("# SOUL v1\ncanary\n"); sh("git add -A")
        probe = sh('git commit -q -m "fix(probe): canary undisclosed"')
        if probe.returncode == 0:
            print("  [FAIL] canary commit TIDAK diblok — hook tak dipanggil git, "
                  "semua keputusan berikut tak bermakna")
            return 1
        sh("git reset -q --hard HEAD")
        print("  [PASS] canary: hook disahkan dipanggil oleh git sebelum kes lain diuji")

        def attempt(label: str, msg: str, mutate, expect_block: bool, env=None) -> bool:
            mutate()
            e = dict(os.environ); e.pop(ACK_ENV, None)
            if env: e.update(env)
            r = sh(f"git commit -q -m {json.dumps(msg)}", cwd=repo, env=e)
            blocked = r.returncode != 0
            ok = blocked == expect_block
            tag = "BLOCK" if blocked else "ALLOW"
            want = "BLOCK" if expect_block else "ALLOW"
            print(f"  [{('PASS' if ok else 'FAIL')}] {label}  got={tag} want={want}")
            return ok

        def m_change(): (repo/"memory/identity/SOUL.md").write_text("# SOUL v1\nsmuggled\n"); sh("git add -A")
        def m_disclosed(): (repo/"memory/identity/SOUL.md").write_text("# SOUL v2\n"); sh("git add -A")
        def m_marker(): (repo/"memory/identity/SOUL.md").write_text("# SOUL v3\n"); sh("git add -A")
        def m_symlink():
            p = repo/"memory/identity/SOUL.md"; p.unlink(); p.symlink_to("/etc/hostname"); sh("git add -A")
        def m_unrelated():
            (repo/"other.py").write_text("x=1\n"); sh("git add -A")

        results = []
        print("  selftest — throwaway repo, canonical untouched:")
        results.append(attempt("undisclosed identity change", "fix(probe): x", m_change, expect_block=True))
        sh("git reset -q --hard HEAD~1", cwd=repo)
        results.append(attempt("disclosed via path mention", "fix: memory/identity/SOUL.md", m_disclosed, expect_block=False))
        results.append(attempt("disclosed via marker", "chore: x\n\nIDENTITY-CHANGE: F13 auth", m_marker, expect_block=False))
        results.append(attempt("symlink downgrade (fan-out)", "fix(soul): linkage", m_symlink, expect_block=True))
        sh("git reset -q --hard HEAD~1", cwd=repo)
        results.append(attempt("symlink + ack bypass", "fix(soul): linkage", m_symlink,
                               env={ACK_ENV: "F13 Arif deliberate"}, expect_block=False))
        sh("git reset -q --hard HEAD~1", cwd=repo)
        results.append(attempt("unrelated commit (guard stays out)", "fix(probe): x", m_unrelated, expect_block=False))

        passed = sum(1 for r in results if r)
        print(f"  selftest result: {passed}/{len(results)} passed")
        return 0 if passed == len(results) else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    # ── selftest runs OUTSIDE the fail-open wrapper ────────────────────────
    # A verification harness that crashes and then reports success is worse
    # than no harness: it manufactures a green light. Fail-open is correct
    # for the commit gate (never wedge a repo on the guard's own bug) and
    # wrong for selftest (its whole job is to prove the guard works).
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        try:
            sys.exit(selftest())
        except Exception as e:
            print(f"SELFTEST CRASHED ({type(e).__name__}: {e}) — treating as FAILURE, not PASS",
                  file=sys.stderr)
            import traceback; traceback.print_exc()
            sys.exit(1)

    try:
        sys.exit(main())
    except Exception as e:  # fail-open on guard's own bug, but never silently
        print(f"[identity-guard] guard error ({type(e).__name__}: {e}) — allowing commit",
              file=sys.stderr)
        try:
            audit("GUARD_ERROR", err=f"{type(e).__name__}: {e}")
        except Exception:
            pass
        sys.exit(0)
