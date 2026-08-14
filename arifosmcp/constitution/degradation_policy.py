"""
degradation_policy.py — ASYMMETRIC DEGRADATION + SHADOW KERNEL TEST

Two kernel-hardening invariants from A-FORGE remediation directives (2026-08-14):

K-2 — ASYMMETRIC DEGRADATION (D-1):
    When a governance component fails (config missing, server unreachable,
    schema unreadable), the system degrades asymmetrically:
      - OBSERVE path  → degrades toward PERMISSIVE (keep seeing)
      - MUTATE path   → degrades toward DENY (stop changing)
    A blind system that can act is more dangerous than a frozen system
    that can see.

K-5 — SHADOW KERNEL TEST (D-6):
    No organ may compute a governance verdict locally. Detection:
    if an organ tool emits verdict-like output (SEAL/HOLD/VOID/G-score)
    without routing through the kernel at :8088, it is a shadow kernel.
    R ∉ S at the organ level — the forge must not contain its own
    reference.

FLOORS SPANNED:
    K-2: F1 AMANAH (reversibility — frozen mutation is reversible state)
         F12 RESILIENCE (observation must survive component failure)
    K-5: Gödel Lock R ∉ S (organ must not be its own judge)

DESIGN:
    - Python. stdlib-only. Zero dependencies.
    - PURE core (no I/O, no clock) — deterministic, unit-testable.
    - ADDITIVE module. Follows surface_breaker.py pattern.
    - Wire into runtime_hook.py as pre-check for degradation policy.

WIRE STATUS: ADDITIVE. Not imported at boot. Consumers call explicitly.

DITEMPA BUKAN DIBERI · forged from A-FORGE remediation, not from assumption.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

# Action classes that are observation-only (no mutation config dependency)
OBSERVE_CLASSES = frozenset({"read", "query", "probe", "observe", "RETRIEVE"})

# Action classes that mutate state
MUTATE_CLASSES = frozenset({
    "write", "mutate", "irreversible", "forge", "deploy",
    "MUTATE", "WRITE", "IRREVERSIBLE", "FORGE", "DEPLOY",
})

# Verdict-like outputs that indicate local governance computation
VERDICT_KEYWORDS = frozenset({
    "SEAL", "HOLD", "VOID", "SABAR",
    "is_canonical_g", "effective_verdict",
    "G_score", "C_dark", "W3",
})

# Known exceptions: tools that compute domain values, not governance verdicts
SHADOW_KERNEL_EXCEPTIONS = frozenset({
    "forge_predict",       # GEOX/WEALTH forward simulation, not governance
    "forge_evaluate",      # Delegated G computation (is_canonical_g=true) — kernel's own math
    "forge_witness",       # Input collection for tri-witness, not verdict output
    "forge_apex_encode",   # J-space G_local (is_canonical_g=false) — flagged by own schema
    "forge_apex_emd",      # Metabolic cycle on goal — computation, not verdict
    "forge_check_governance",  # Pure relay to arifOS — should remain relay-only
})


# ─────────────────────────────────────────────────────────────────────────────
# K-2: ASYMMETRIC DEGRADATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DegradationVerdict:
    action: str          # "ALLOW" | "DENY" | "DEGRADE_PERMISSIVE" | "DEGRADE_DENY"
    action_class: str
    component: str
    failure: str
    detail: str

    @property
    def is_allowed(self) -> bool:
        return self.action in ("ALLOW", "DEGRADE_PERMISSIVE")

    def summary(self) -> str:
        return (
            f"DegradationPolicy[{self.action}] "
            f"class={self.action_class} component={self.component} "
            f"— {self.detail}"
        )


def asymmetric_degrade(
    action_class: str,
    component: str = "governance_config",
    failure: str = "ENOENT",
) -> DegradationVerdict:
    """Asymmetric degradation: when a governance component fails, OBSERVE
    tools degrade toward permissive, MUTATE tools degrade toward deny.

    Pure function — no I/O, no clock, no state. Agents can audit the logic.

    The thermodynamic safety principle: a system under stress should freeze
    its ability to change before it freezes its ability to observe.

    Args:
        action_class: The tool's action class (read/query/probe vs write/mutate/etc.)
        component: What failed (e.g. "budgets.yaml", "policy_engine", "judge_server")
        failure: The failure mode (e.g. "ENOENT", "TIMEOUT", "UNREACHABLE")

    Returns:
        DegradationVerdict with action ALLOW (observe) or DENY (mutate)
    """
    normalized = action_class.strip().lower()

    # OBSERVE-class: degrade to permissive-read
    # Missing config must never cost sight
    if normalized in {c.lower() for c in OBSERVE_CLASSES}:
        return DegradationVerdict(
            action="DEGRADE_PERMISSIVE",
            action_class=action_class,
            component=component,
            failure=failure,
            detail=(
                f"observe-class tool '{action_class}' proceeds despite "
                f"{component} failure ({failure}) — observation must not "
                "depend on mutation config"
            ),
        )

    # MUTATE-class: degrade to deny
    # Frozen mutation is safe; blind mutation is not
    if normalized in {c.lower() for c in MUTATE_CLASSES}:
        return DegradationVerdict(
            action="DEGRADE_DENY",
            action_class=action_class,
            component=component,
            failure=failure,
            detail=(
                f"mutate-class tool '{action_class}' blocked due to "
                f"{component} failure ({failure}) — mutation requires "
                "intact governance state"
            ),
        )

    # UNKNOWN or unclassified: degrade to deny (fail-safe)
    return DegradationVerdict(
        action="DENY",
        action_class=action_class,
        component=component,
        failure=failure,
        detail=(
            f"unclassified action '{action_class}' denied during "
            f"{component} failure ({failure}) — unknown class defaults "
            "to deny under degradation"
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# K-5: SHADOW KERNEL TEST
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ShadowKernelReport:
    tool_name: str
    is_shadow: bool
    severity: str      # "CLEAN" | "SUSPECT" | "VIOLATION"
    detail: str
    verdict_outputs: List[str]

    def summary(self) -> str:
        return (
            f"ShadowKernel[{self.severity}] {self.tool_name} "
            f"— {self.detail}"
        )


def shadow_kernel_test(
    tool_name: str,
    output_keys: Optional[List[str]] = None,
    routes_to_kernel: bool = True,
) -> ShadowKernelReport:
    """Detect whether an organ tool computes governance verdicts locally
    instead of relaying to the kernel at :8088.

    R ∉ S at the organ level: the forge must not contain its own reference.
    A tool that emits SEAL/HOLD/VOID/G-score without routing through the
    kernel is a shadow kernel — a parallel authority surface that can
    diverge from canonical governance.

    Pure function — no I/O. Feed it tool metadata, get the verdict.

    Args:
        tool_name: Name of the tool to test
        output_keys: Keys in the tool's output that may contain verdicts
        routes_to_kernel: Whether the tool routes its governance calls through :8088

    Returns:
        ShadowKernelReport with CLEAN/SUSPECT/VIOLATION severity
    """
    output_keys = output_keys or []

    # Check for known exceptions first
    if tool_name in SHADOW_KERNEL_EXCEPTIONS:
        return ShadowKernelReport(
            tool_name=tool_name,
            is_shadow=False,
            severity="CLEAN",
            detail=f"known exception: {tool_name} is domain computation or delegated relay",
            verdict_outputs=[],
        )

    # Scan output keys for verdict-like content
    found_verdicts: list[str] = []
    for key in output_keys:
        for keyword in VERDICT_KEYWORDS:
            if keyword.lower() in key.lower():
                found_verdicts.append(key)
                break

    if not found_verdicts:
        # No verdict-like outputs — clean
        return ShadowKernelReport(
            tool_name=tool_name,
            is_shadow=False,
            severity="CLEAN",
            detail="no verdict-like outputs detected",
            verdict_outputs=[],
        )

    if routes_to_kernel:
        # Has verdict outputs but routes through kernel — relay, not shadow
        return ShadowKernelReport(
            tool_name=tool_name,
            is_shadow=False,
            severity="CLEAN",
            detail=f"has verdict outputs {found_verdicts} but routes through kernel — relay pattern",
            verdict_outputs=found_verdicts,
        )

    # Has verdict outputs AND does NOT route through kernel — SHADOW KERNEL
    return ShadowKernelReport(
        tool_name=tool_name,
        is_shadow=True,
        severity="VIOLATION",
        detail=(
            f"tool '{tool_name}' computes verdict-like outputs "
            f"{found_verdicts} WITHOUT routing through kernel :8088 — "
            "shadow kernel candidate. Iron Rule violation: forge must not "
            "outrun kernel. Flag for F13 review, do not fix unilaterally."
        ),
        verdict_outputs=found_verdicts,
    )


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (run: python3 degradation_policy.py)
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> int:
    failures = 0

    def check(name: str, got: Any, want: Any) -> None:
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

    print("=== K-2: ASYMMETRIC DEGRADATION ===")

    # 1. OBSERVE tool survives config loss
    v1 = asymmetric_degrade("read", "budgets.yaml", "ENOENT")
    check("observe survives ENOENT", v1.is_allowed, True)
    check("observe verdict is DEGRADE_PERMISSIVE", v1.action, "DEGRADE_PERMISSIVE")

    # 2. MUTATE tool blocked by config loss
    v2 = asymmetric_degrade("mutate", "budgets.yaml", "ENOENT")
    check("mutate blocked by ENOENT", v2.is_allowed, False)
    check("mutate verdict is DEGRADE_DENY", v2.action, "DEGRADE_DENY")

    # 3. PROBE (observe-class) survives timeout
    v3 = asymmetric_degrade("probe", "judge_server", "TIMEOUT")
    check("probe survives timeout", v3.is_allowed, True)

    # 4. IRREVERSIBLE blocked by unreachable judge
    v4 = asymmetric_degrade("irreversible", "judge_server", "UNREACHABLE")
    check("irreversible blocked", v4.is_allowed, False)

    # 5. UNKNOWN class defaults to deny under degradation
    v5 = asymmetric_degrade("mystery_tool", "config", "CORRUPTED")
    check("unknown class denies", v5.is_allowed, False)

    # 6. WRITE blocked, QUERY allowed — asymmetric pair
    v6a = asymmetric_degrade("write", "policy_engine", "ENOENT")
    v6b = asymmetric_degrade("query", "policy_engine", "ENOENT")
    check("write blocked + query allowed (asymmetric pair)",
          (not v6a.is_allowed) and v6b.is_allowed, True)

    print("\n=== K-5: SHADOW KERNEL TEST ===")

    # 7. Clean tool — no verdict outputs
    r1 = shadow_kernel_test("forge_shell", ["stdout", "exit_code", "stderr"], True)
    check("shell is clean", r1.severity, "CLEAN")

    # 8. Known exception — forge_predict
    r2 = shadow_kernel_test("forge_predict", ["G_score", "prediction"], False)
    check("predict is known exception", r2.severity, "CLEAN")
    check("predict is not shadow", r2.is_shadow, False)

    # 9. Known exception — forge_evaluate
    r3 = shadow_kernel_test("forge_evaluate", ["G", "C_dark", "verdict"], True)
    check("evaluate is known exception", r3.severity, "CLEAN")

    # 10. Shadow kernel candidate — computes verdicts locally, no kernel route
    r4 = shadow_kernel_test(
        "forge_judge_proxy",
        ["effective_verdict", "SEAL", "HOLD"],
        False,  # does NOT route through kernel
    )
    check("judge_proxy is VIOLATION", r4.severity, "VIOLATION")
    check("judge_proxy is shadow", r4.is_shadow, True)

    # 11. Relay pattern — has verdict outputs but routes through kernel
    r5 = shadow_kernel_test(
        "forge_kernel",
        ["effective_verdict", "SEAL"],
        True,  # DOES route through kernel
    )
    check("forge_kernel relay is CLEAN", r5.severity, "CLEAN")
    check("forge_kernel is not shadow", r5.is_shadow, False)

    # 12. Tool with no verdict outputs is always clean
    r6 = shadow_kernel_test("forge_filesystem", ["path", "content", "bytes_written"], False)
    check("filesystem no verdicts = clean", r6.severity, "CLEAN")

    print(
        f"\nDEGRADATION POLICY SELF-TEST: "
        f"{'ALL PASS' if failures == 0 else str(failures) + ' FAILURES'}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_selftest())
