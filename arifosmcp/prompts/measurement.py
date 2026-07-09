"""
measurement.py — Thermodynamic & Agentic Metrics Engine
========================================================

The pulse of arifOS. Computes, records, and surfaces metabolic metrics
every time a SEAL is emitted. Zero overhead on the main loop — all
computation is O(1) append to a JSONL registry for cross-session analysis.

DITEMPA BUKAN DIBERI — Measurement is forged, not guessed.

Canon: LLM teka. Agentic uji. Lepas pintu, baru jadi.
"""

from __future__ import annotations

import json
import math
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Paths ───────────────────────────────────────────────────────────────────

REGISTRY_DIR = Path("/root/A-FORGE/forge_work/metrics")
REGISTRY_PATH = REGISTRY_DIR / "entropy_registry.jsonl"
SHADOW_REGISTRY_PATH = (
    Path("/root/A-FORGE/forge_work/measurement") / "entropy_registry.shadow.jsonl"
)
PERFORMANCE_DIR = Path("/root/A-FORGE/forge_work")
VAULT999_PATH = Path("/root/VAULT999/seal_chain.jsonl")
CARRY_FORWARD_PATH = Path("/root/.local/share/arifos/carry_forward.json")
BASELINE_WINDOW = 20  # number of past seals for moving average

DRY_RUN_ENV_VAR = "ARIFOS_DRY_RUN"  # set to "1" to write to shadow only


def is_dry_run() -> bool:
    """Check ARIFOS_DRY_RUN env var — if set, metrics go to shadow registry."""
    return os.environ.get(DRY_RUN_ENV_VAR, "0") == "1"


# ─── Core Computation ────────────────────────────────────────────────────────


def shannon_entropy(sequence: list[Any]) -> float:
    """Shannon entropy in bits of a discrete sequence."""
    if not sequence:
        return 0.0
    n = len(sequence)
    counts = Counter(sequence)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def js_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """
    Jensen-Shannon divergence between two discrete distributions.
    Symmetric, bounded [0, 1] for log base 2.
    """
    all_keys = set(p) | set(q)
    m = {k: (p.get(k, 0.0) + q.get(k, 0.0)) / 2.0 for k in all_keys}

    def kl(a, b):
        return sum(
            a.get(k, 0.0) * math.log2(a.get(k, 0.0) / b[k] + 1e-12) for k in a if a.get(k, 0.0) > 0
        )

    return (kl(p, m) + kl(q, m)) / 2.0


def compute_entropy_delta(pre_state: dict, post_state: dict) -> dict:
    """
    ΔS between session start and end.

    Uses tool state distribution if available, falls back to
    payload key structure as a proxy.

    Returns:
        delta_s: float — negative means entropy REDUCED (good)
        pre_entropy: float
        post_entropy: float
        method: str — what was measured
    """
    # Primary path: tool state distribution
    pre_tools = pre_state.get("tools", [])
    post_tools = post_state.get("tools", [])
    if pre_tools and post_tools:
        pre_ent = shannon_entropy(pre_tools)
        post_ent = shannon_entropy(post_tools)
        delta = post_ent - pre_ent
        return {
            "delta_s": delta,
            "pre_entropy": pre_ent,
            "post_entropy": post_ent,
            "method": "tool_state_shannon",
        }

    # Fallback: payload key structure
    pre_keys = list(pre_state.get("payload", {}).keys())
    post_keys = list(post_state.get("payload", {}).keys())
    if pre_keys or post_keys:
        pre_ent = shannon_entropy(pre_keys)
        post_ent = shannon_entropy(post_keys)
        delta = post_ent - pre_ent
        return {
            "delta_s": delta,
            "pre_entropy": pre_ent,
            "post_entropy": post_ent,
            "method": "payload_key_shannon",
        }

    # Last resort: char mass
    pre_chars = len(json.dumps(pre_state))
    post_chars = len(json.dumps(post_state))
    delta = post_chars - pre_chars
    return {
        "delta_s": delta,
        "pre_entropy": float(pre_chars),
        "post_entropy": float(post_chars),
        "method": "char_mass_proxy",
    }


def compute_fisher_proxy(seal_entry: dict, baseline_entries: list[dict]) -> dict:
    """
    JS divergence between this seal's verdict distribution and the baseline.
    Proxy for Fisher information distance (true Fisher needs continuous params).
    """
    # This seal's verdict distribution
    v = seal_entry.get("verdict", "UNKNOWN")
    session_dist = {v: 1.0}

    # Baseline verdict distribution
    baseline_counts: "dict[str, float]" = {}
    for e in baseline_entries:
        v = e.get("verdict", "UNKNOWN")
        baseline_counts[v] = baseline_counts.get(v, 0.0) + 1.0
    total = float(sum(baseline_counts.values())) or 1.0
    baseline_dist = {k: v / total for k, v in baseline_counts.items()}

    js = js_divergence(session_dist, baseline_dist)

    # Gap severity distribution if present
    gap_severity_js = None
    gaps = seal_entry.get("gaps", [])
    if gaps:
        gap_counts: dict[str, float] = {}
        for g in gaps:
            s = g.get("severity", "UNKNOWN")
            gap_counts[s] = gap_counts.get(s, 0.0) + 1.0
        gap_total = sum(gap_counts.values()) or 1.0
        gap_dist = {k: v / gap_total for k, v in gap_counts.items()}
        # Healthy prior: all gaps LOW
        healthy_prior = {"LOW": 1.0}
        gap_severity_js = js_divergence(gap_dist, healthy_prior)

    return {
        "js_vs_baseline": js,
        "gap_severity_js": gap_severity_js,
        "baseline_n": len(baseline_entries),
        "critical_gaps": sum(1 for g in gaps if g.get("severity") == "CRITICAL") if gaps else 0,
    }


def compute_scar_correlation(seal_entry: dict, active_scars: list[dict]) -> dict:
    """
    Assess whether this seal's violated_floors correlate with active scars.
    """
    violated = seal_entry.get("violated_floors", [])
    if not violated:
        return {
            "violated_floors": [],
            "scar_matches": 0,
            "total_scars": len(active_scars),
            "gate_fired": False,
        }

    # Check if any violated floor matches a scar's cited floors
    scar_floors = set()
    for s in active_scars:
        for f in s.get("floors_cited", []):
            scar_floors.add(f)

    matches = [f for f in violated if f.split(":")[0] in scar_floors]

    return {
        "violated_floors": violated,
        "scar_matches": len(matches),
        "matching_floors": matches,
        "total_scars": len(active_scars),
        "gate_fired": len(matches) > 0,
    }


def compute_task_completion(carry_forward: dict, session_logs: dict) -> dict:
    """
    Track INIT_TASKS completion across sessions.
    """
    prior_tasks = carry_forward.get("init_tasks", [])
    completed_tasks = session_logs.get("completed_tasks", [])
    total = len(prior_tasks) or 1
    return {
        "total_tasks": len(prior_tasks),
        "completed": len(completed_tasks),
        "acc_gap": len(completed_tasks) / max(total, 1),
        "remaining": len(prior_tasks) - len(completed_tasks),
    }


# ─── Moving Statistics ─────────────────────────────────────────────────────


def compute_moving_statistics(registry_entries: list[dict]) -> dict:
    """
    Running statistics across the last N registry entries.
    Used for pivotal_threshold_deviation — how far current ΔS is from
    the moving average, in standard deviations.
    """
    if len(registry_entries) < 2:
        return {
            "moving_avg_delta_s": 0.0,
            "moving_std_delta_s": 0.0,
            "z_score_delta_s": 0.0,
            "n": len(registry_entries),
            "convergence_rate": 1.0,
        }

    recent = registry_entries[-BASELINE_WINDOW:]
    deltas = [e.get("delta_s", 0.0) for e in recent if e.get("delta_s") is not None]

    if not deltas:
        return {
            "moving_avg_delta_s": 0.0,
            "moving_std_delta_s": 0.0,
            "z_score_delta_s": 0.0,
            "n": 0,
            "convergence_rate": 1.0,
        }

    n = len(deltas)
    avg = sum(deltas) / n
    variance = sum((d - avg) ** 2 for d in deltas) / n
    std = math.sqrt(variance) or 1e-12
    current = deltas[-1]
    z = (current - avg) / std

    # Convergence rate: how fast deltas approach zero (lower = faster convergence)
    abs_deltas = [abs(d) for d in deltas]
    if len(abs_deltas) >= 2:
        rate = (abs_deltas[0] - abs_deltas[-1]) / max(len(deltas), 1)
    else:
        rate = 0.0

    return {
        "moving_avg_delta_s": avg,
        "moving_std_delta_s": std,
        "z_score_delta_s": z,
        "pivotal_threshold_deviation": abs(z),  # how many sigma from norm
        "n": n,
        "convergence_rate": rate,
    }


# ─── Registry I/O ────────────────────────────────────────────────────────────


def read_registry(source: Path | None = None) -> list[dict]:
    """Read all entries from a registry JSONL file (canon or shadow)."""
    path = source or REGISTRY_PATH
    if not path.exists():
        return []
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def read_shadow() -> list[dict]:
    """Read all entries from the shadow registry."""
    return read_registry(SHADOW_REGISTRY_PATH)


def append_to_registry(metrics: dict, force_canon: bool = False) -> None:
    """
    Append a single metrics entry.

    Normal mode — respects ARIFOS_DRY_RUN:
      - dry-run=1 → writes to shadow registry ONLY
      - dry-run=0 → writes to canon registry

    force_canon=True bypasses dry-run (used by promote_shadow).
    """
    if force_canon or not is_dry_run():
        REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
        line = json.dumps(metrics, sort_keys=True, default=str) + "\n"
        with open(REGISTRY_PATH, "a") as f:
            f.write(line)
    else:
        # Dry-run mode: write to shadow
        SHADOW_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(metrics, sort_keys=True, default=str) + "\n"
        with open(SHADOW_REGISTRY_PATH, "a") as f:
            f.write(line)
        print(f"[DRY-RUN] Metrics written to shadow: {SHADOW_REGISTRY_PATH}")


def promote_shadow(keep_shadow: bool = False, force: bool = False) -> int:
    """
    Promote shadow registry entries to canon registry.

    After promotion, shadow entries are either deleted (default) or kept
    if keep_shadow=True. Returns number of promoted entries.

    Only promotes if there are 3-5 entries in the shadow registry,
    and they are stable (ΔS, JS, violated_floors, scar_matches are stable/clean).
    Pass force=True to bypass stability checks.
    """
    shadow_entries = read_shadow()
    if not shadow_entries:
        return 0

    n = len(shadow_entries)
    if not force:
        # Enforce 3 to 5 seals
        if not (3 <= n <= 5):
            print(f"[PROMOTION] Blocked: Shadow registry has {n} entries (expected 3 to 5).")
            return 0

        # 1. Check violated_floors (must be clean)
        has_violations = any(len(e.get("violated_floors", [])) > 0 for e in shadow_entries)
        if has_violations:
            print("[PROMOTION] Blocked: Some shadow entries contain violated floors.")
            return 0

        # 2. Check scar matches (must be clean/empty)
        has_scars = any(len(e.get("scar_matches", [])) > 0 for e in shadow_entries)
        if has_scars:
            print("[PROMOTION] Blocked: Some shadow entries contain scar correlation matches.")
            return 0

        # 3. Check stability of ΔS (delta_s)
        deltas = [e.get("delta_s", 0.0) for e in shadow_entries]
        avg_ds = sum(deltas) / n
        var_ds = sum((x - avg_ds) ** 2 for x in deltas) / n
        std_ds = math.sqrt(var_ds)
        if std_ds >= 0.1:
            print(f"[PROMOTION] Blocked: ΔS is unstable (std={std_ds:.4f} >= 0.1).")
            return 0

        # 4. Check stability of JS (js_vs_baseline)
        js_vals = [e.get("js_vs_baseline", 0.0) for e in shadow_entries]
        avg_js = sum(js_vals) / n
        var_js = sum((x - avg_js) ** 2 for x in js_vals) / n
        std_js = math.sqrt(var_js)
        if std_js >= 0.1:
            print(f"[PROMOTION] Blocked: JS is unstable (std={std_js:.4f} >= 0.1).")
            return 0

        print(
            f"[PROMOTION] Stability checks passed (n={n}, std_ds={std_ds:.4f}, std_js={std_js:.4f}). Promoting..."
        )

    promoted = 0
    for entry in shadow_entries:
        append_to_registry(entry, force_canon=True)
        promoted += 1

    # Clear shadow
    if not keep_shadow:
        if SHADOW_REGISTRY_PATH.exists():
            SHADOW_REGISTRY_PATH.unlink()

    return promoted


def read_seal_chain(limit: int = BASELINE_WINDOW) -> list[dict]:
    """Read the most recent N entries from seal_chain.jsonl."""
    if not VAULT999_PATH.exists():
        return []
    entries = []
    with open(VAULT999_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries[-limit:]


def read_carry_forward() -> dict:
    """Read current carry_forward.json state."""
    if not CARRY_FORWARD_PATH.exists():
        return {}
    try:
        with open(CARRY_FORWARD_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


# ─── Main Entry Point ────────────────────────────────────────────────────────


def measure_seal(
    seal_entry: dict,
    pre_state: dict | None = None,
    post_state: dict | None = None,
    session_logs: dict | None = None,
    dry_run: bool | None = None,
) -> dict:
    """
    Compute and record metrics for a single SEAL entry.
    Called at 999_SEAL time, before the seal is written to VAULT999.

    Args:
        seal_entry: The SEAL entry being emitted (must have verdict, actor, epoch)
        pre_state: Tool/system state at 000_INIT (tool_surface_hash_start)
        post_state: Tool/system state at 999_SEAL (tool_surface_hash_end)
        session_logs: Optional dict with completed_tasks, etc.
        dry_run: Force dry-run mode (default: from ARIFOS_DRY_RUN env var)

    Returns:
        metrics dict with all computed values
        (appended to shadow registry if dry_run, canon registry otherwise)
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    # 1. ΔS
    pre = pre_state or {}
    post = post_state or {}
    entropy = compute_entropy_delta(pre, post)

    # 2. Fisher/JS proxy
    baseline = read_seal_chain()
    fisher = compute_fisher_proxy(seal_entry, baseline)

    # 3. Scar correlation
    cf = read_carry_forward()
    scars = cf.get("active_scars", {}).get("surface", [])
    scar = compute_scar_correlation(seal_entry, scars)

    # 4. Task completion
    tasks = compute_task_completion(cf, session_logs or {})

    # 5. Moving statistics
    registry = read_registry()
    moving = compute_moving_statistics(registry)

    # Resolve dry-run state
    _dry = dry_run if dry_run is not None else is_dry_run()

    # 6. Build metrics envelope
    metrics = {
        "timestamp": timestamp,
        "session_id": seal_entry.get("session_id", ""),
        "seq": seal_entry.get("seq"),
        "actor": seal_entry.get("actor", "unknown"),
        "verdict": seal_entry.get("verdict", "UNKNOWN"),
        "epoch": seal_entry.get("epoch", timestamp),
        # Core thermodynamic metrics
        "delta_s": entropy["delta_s"],
        "delta_s_method": entropy["method"],
        "pre_entropy": entropy["pre_entropy"],
        "post_entropy": entropy["post_entropy"],
        # Gate metrics
        "js_vs_baseline": fisher["js_vs_baseline"],
        "critical_gaps": fisher["critical_gaps"],
        "violated_floors": scar["violated_floors"],
        "scar_matches": scar["scar_matches"],
        "gate_fired": scar["gate_fired"],
        # Task metrics
        "acc_gap": tasks["acc_gap"],
        "tasks_total": tasks["total_tasks"],
        "tasks_completed": tasks["completed"],
        # Moving statistics
        "moving_avg_delta_s": moving["moving_avg_delta_s"],
        "z_score_delta_s": moving["z_score_delta_s"],
        "pivotal_threshold_deviation": moving["pivotal_threshold_deviation"],
        "convergence_rate": moving["convergence_rate"],
        "moving_n": moving["n"],
        # Surface hashes (for reproducibility)
        "tool_surface_hash_start": seal_entry.get("tool_surface_hash_start"),
        "tool_surface_hash_end": seal_entry.get("tool_surface_hash_end"),
        # Error state
        "gaps_remaining": seal_entry.get("gaps_remaining"),
        "init_tasks": seal_entry.get("init_tasks"),
        # Dry-run metadata
        "dry_run": _dry,
        "shadow_path": str(SHADOW_REGISTRY_PATH) if _dry else None,
    }

    # Append to registry
    append_to_registry(metrics)

    if not is_dry_run():
        promote_shadow(keep_shadow=False, force=False)

    return metrics


def summary_line(metrics: dict, show_dry_run: bool = True) -> str:
    """
    One-line pulse string for embedding in SEAL output.

    Example: [ΔS: -0.04 | JS: 0.02 | V: 0 | acc: 1.0 | z: 0.3]
    If dry_run and show_dry_run, prefixes with [DRY].
    """
    ds = metrics.get("delta_s", 0)
    js = metrics.get("js_vs_baseline", 0)
    vf = len(metrics.get("violated_floors", []))
    acc = metrics.get("acc_gap", 0)
    z = metrics.get("z_score_delta_s", 0)

    ds_mark = "⬇" if ds < 0 else "⬆" if ds > 0 else "—"
    pulse = f"[ΔS: {ds:+.4f}{ds_mark} | JS: {js:.4f} | V: {vf} | acc: {acc:.2f} | z: {z:+.2f}σ]"

    if show_dry_run and metrics.get("dry_run", False):
        pulse = f"[DRY] {pulse}"

    return pulse


# ─── Diagnostics ─────────────────────────────────────────────────────────────


def print_registry_summary(n: int = 10) -> str:
    """Print a human-readable summary of the last N registry entries."""
    entries = read_registry()[-n:]
    if not entries:
        return "No registry entries yet."

    lines = [
        "=" * 60,
        f"ENTROPY REGISTRY — Last {len(entries)} Entries",
        "=" * 60,
        f"{'Seq':>6} {'Verdict':10s} {'ΔS':>10} {'z-score':>8} {'V':>3} {'acc':>6}",
        "-" * 60,
    ]
    for e in entries:
        ds = e.get("delta_s", 0)
        z = e.get("z_score_delta_s", 0)
        v = len(e.get("violated_floors", []))
        a = e.get("acc_gap", 0)
        lines.append(
            f"{str(e.get('seq', '?')):>6} "
            f"{e.get('verdict', '?'):10s} "
            f"{ds:+10.4f} "
            f"{z:+8.2f}σ "
            f"{v:3d} "
            f"{a:6.2f}"
        )

    # Average row
    avg_ds = sum(e.get("delta_s", 0) for e in entries) / len(entries)
    avg_z = sum(e.get("z_score_delta_s", 0) for e in entries) / len(entries)
    lines.append("-" * 60)
    lines.append(f"{'AVG':>6} {'':10s} {avg_ds:+10.4f} {avg_z:+8.2f}σ")
    lines.append("=" * 60)
    return "\n".join(lines)


# ─── Self-test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("measurement.py — Self Test")
    print("=" * 50)

    # Quick sanity: shannon entropy of known distribution
    test_seq = ["SEAL", "SEAL", "HOLD", "SEAL", "VOID"]
    h = shannon_entropy(test_seq)
    print(f"Shannon([SEAL×3, HOLD, VOID]) = {h:.4f} bits (expect ~1.37)")

    # JS divergence
    p = {"SEAL": 0.8, "HOLD": 0.2}
    q = {"SEAL": 0.5, "HOLD": 0.5}
    js = js_divergence(p, q)
    print(f"JS(P||Q) = {js:.4f} bits (expect ~0.12)")

    # Measure current registry state (if any)
    registry = read_registry()
    print(f"\nRegistry: {len(registry)} entries at {REGISTRY_PATH}")

    if registry:
        print("\n" + print_registry_summary(5))

    print("\n✅ measurement.py self-test complete")
