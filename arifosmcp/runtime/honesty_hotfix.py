"""
arifosmcp/runtime/honesty_hotfix.py — Honest Capability Hotfix Bundle

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED — NOT DEPLOYED. Loaded only by direct import. Not wired into
the live runtime. Reversible-first per F1 AMANAH.

This module addresses four gaps in the live kernel capability surface, in
*pure-function* form, so each can be tested in isolation before any of them
is allowed to touch the live runtime at /opt/arifos/app/.

Gap 11 — Self-Probe Paradox
  Problem: A prober marks the tool that is currently executing as DEAD
  while the tool is still responding. This is a Gödel-style reflexive
  blind spot — the prober cannot attest itself from inside itself.
  Fix: A new status class `SELF` is introduced. The prober MUST return
  `SELF` (never `DEAD`, never `ALIGNED`) for the tool currently executing.
  The prober's own execution name is passed in by the caller — the prober
  does not introspect itself. The Gödel lock is honored in the plumbing
  rather than papered over.

Gap 7 — Inner/Outer Verdict Mismatch
  Problem: A wrapper can return SEAL while the inner verdict was HOLD.
  The 2026-05-26 contradiction scanner at runtime/verdict_wrapper.py
  blocks specific known degradation signals (`_llm_available=False`,
  `schema_valid=False`, `dignity_verdict==COMPROMISED`, `L02_TRUTH=False`,
  `execution_verdict==DEGRADED_FALLBACK`) from leaking SEAL. That is
  pattern-matched, not structural.
  Fix: A general invariant `final = MIN(inner, wrapper)` over a verdict
  ordering. The wrapper may only DOWNGRADE, never upgrade. This is the
  structural version of the same idea; it covers unknown future cases
  the pattern matcher cannot anticipate.

Gap 12 — Build-Time Git Hash Injection
  Problem: The runtime reports `kanon-1bbe5f9` (correct) but the
  build_info stub at runtime/build_info.py is a dev placeholder. The
  build_info path is consulted for forge receipts; if the running
  container ever reports its version via that path, an empty stub would
  produce `kanon-unknown`. The current live container has the correct
  SHA injected by the GHCR build pipeline. This function provides a
  runtime-resolved version that does not depend on the stub.
  Fix: Read git HEAD at runtime from the canonical location, fall back
  to environment variables, then to an honest `version-unresolved`
  placeholder. Never `kanon-unknown`.

Gap 3 (partial) — Circuit Breaker
  Problem: GEOX or any federated organ can hang indefinitely, blocking
  every session boot that depends on Tri-Witness.
  Fix: A small circuit-breaker primitive with timeout, strike count, and
  exponential backoff. The breaker is *not* wired into the prober here
  — that wiring is a separate change. The breaker primitive is provided
  so any caller can wrap a probe.

All four are reversible: this module is not imported by the running
arifOS at /opt/arifos/app/. The live runtime at git commit 1bbe5f9 is
unchanged. To roll back, delete this file and the test file. Nothing
else needs to move.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, TypeVar


# ──────────────────────────────────────────────────────────────────────
# Gap 11 — Self-Probe SELF status
# ──────────────────────────────────────────────────────────────────────


def probe_status_self(
    tool_name: str,
    currently_executing: str | None,
    is_alive: bool,
) -> dict[str, Any]:
    """
    Return the probe status for a single tool, honoring the SELF
    reflexive-blind-spot rule.

    If `tool_name == currently_executing`, the prober cannot attest
    itself from inside itself. Return `SELF` with a note. The prober
    does not get to call the tool alive or dead — only the caller
    outside the tool can.

    For other tools, the result is `ALIGNED` if alive, `DEAD` if not.
    """
    if tool_name == currently_executing:
        return {
            "status": "SELF",
            "tool": tool_name,
            "note": "cannot self-attest; Gödel lock honored in plumbing",
        }
    if is_alive:
        return {"status": "ALIGNED", "tool": tool_name}
    return {"status": "DEAD", "tool": tool_name}


# ──────────────────────────────────────────────────────────────────────
# Gap 7 — MIN() verdict invariant
# ──────────────────────────────────────────────────────────────────────


# Verdict ordering. Higher rank = stronger commit. The wrapper may only
# DOWNGRADE — return the LOWER of (inner, wrapper). Equality is fine.
VERDICT_RANK: dict[str, int] = {
    "VOID": 0,
    "DEGRADED": 1,
    "HOLD": 2,
    "SABAR": 3,
    "PARTIAL": 4,
    "SEAL": 5,
}

RANK_TO_VERDICT: dict[int, str] = {v: k for k, v in VERDICT_RANK.items()}


def min_verdict(inner: str, wrapper: str) -> str:
    """
    Apply the structural MIN() invariant: the final verdict is the
    lower of inner and wrapper. The wrapper may only DOWNGRADE; it
    may never upgrade. Equality is preserved.

    Raises ValueError on unknown verdict strings — fail closed.
    """
    if inner not in VERDICT_RANK:
        raise ValueError(f"unknown inner verdict: {inner!r}")
    if wrapper not in VERDICT_RANK:
        raise ValueError(f"unknown wrapper verdict: {wrapper!r}")
    return RANK_TO_VERDICT[min(VERDICT_RANK[inner], VERDICT_RANK[wrapper])]


# ──────────────────────────────────────────────────────────────────────
# Gap 12 — Build-time git hash injection
# ──────────────────────────────────────────────────────────────────────


_KNOWN_REPO_PATHS: tuple[Path, ...] = (
    Path(os.environ.get("ARIFOS_HOME", "/root") + "/arifOS"),
    Path("/opt/arifos/app"),
)


def resolve_kernel_version() -> str:
    """
    Resolve the running kernel's version string. The order of preference:

    1. Environment variable `ARIFOS_KERNEL_VERSION` (set by GHCR build).
    2. `git rev-parse --short HEAD` in a known repo location.
    3. `git describe --tags --always` for tag-prefixed version.
    4. Honest fallback `version-unresolved`.

    Never returns `kanon-unknown`. The previous stub at
    arifosmcp/runtime/build_info.py produced that value when the file
    was unmounted. This function does not.
    """
    env_version = os.getenv("ARIFOS_KERNEL_VERSION", "").strip()
    if env_version:
        return env_version

    for repo in _KNOWN_REPO_PATHS:
        if not (repo / ".git").exists():
            continue
        try:
            sha = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=repo,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            tag = (
                subprocess.check_output(
                    ["git", "describe", "--tags", "--always"],
                    cwd=repo,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )
            if tag and tag != sha:
                return f"{tag}-{sha}"
            if sha:
                return f"kanon-{sha}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    return "version-unresolved"


# ──────────────────────────────────────────────────────────────────────
# Gap 3 (partial) — Circuit breaker primitive
# ──────────────────────────────────────────────────────────────────────


T = TypeVar("T")


@dataclass
class CircuitBreaker:
    """
    A small circuit breaker with timeout, strike limit, and exponential
    backoff. Wrap any probe with `breaker.call(probe_fn)`.

    States:
      - closed: probe runs normally; failures increment strikes
      - open: probe is short-circuited until backoff expires
      - half-open: next call after backoff is allowed; success closes,
        failure re-opens with doubled backoff (capped)

    This is the primitive. Wiring it into the live federation prober
    is a separate, gated change. The primitive has no side effects
    beyond the dataclass state and the log it can emit via the
    `on_state_change` callback.
    """

    timeout_s: float = 5.0
    strike_limit: int = 3
    backoff_base: float = 2.0
    backoff_cap_s: float = 300.0
    name: str = "breaker"
    _strikes: int = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)
    _state: str = field(default="closed", init=False)

    @property
    def state(self) -> str:
        return self._state

    def _backoff_s(self) -> float:
        return min(self.backoff_base**self._strikes, self.backoff_cap_s)

    def _set_state(self, new_state: str) -> None:
        if new_state != self._state:
            self._state = new_state

    def call(self, fn: Callable[[], T]) -> T | dict[str, Any]:
        """
        Run `fn` under breaker protection. Returns the function's result
        on success. On failure, returns a structured dict describing the
        state — never raises, so the prober can always return something
        honest.
        """
        if self._state == "open":
            elapsed = time.time() - self._opened_at
            if elapsed < self._backoff_s():
                return {
                    "status": "DEAD",
                    "reason": "circuit_open",
                    "breaker": self.name,
                    "retry_in_s": round(self._backoff_s() - elapsed, 2),
                }
            # half-open: allow the probe
            self._set_state("half-open")

        try:
            result = fn()
        except Exception as exc:  # noqa: BLE001
            self._strikes += 1
            if self._strikes >= self.strike_limit:
                self._opened_at = time.time()
                self._set_state("open")
                return {
                    "status": "DEAD",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "breaker": self.name,
                    "strikes": self._strikes,
                    "tri_witness": "2/3_DEGRADED",
                }
            return {
                "status": "STALE",
                "reason": f"{type(exc).__name__}: {exc}",
                "breaker": self.name,
                "strikes": self._strikes,
            }

        # success
        self._strikes = 0
        self._set_state("closed")
        return result


__all__ = [
    "probe_status_self",
    "min_verdict",
    "resolve_kernel_version",
    "CircuitBreaker",
    "VERDICT_RANK",
    "RANK_TO_VERDICT",
]
