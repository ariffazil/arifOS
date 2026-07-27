# Wire — 3-Layer Constitutional Enforcement

> **Authority:** 888 (arifOS Kernel) · **Sovereignty:** 999 (F13)
> **DITEMPA BUKAN DIBERI — Forged, Not Given.**

The Wire is the cross-organ enforcement surface that turns arifOS
constitutional floors (F1–F13) into POSIX physics: file paths, exit codes,
md5sums, file locks. Where prompt-based safety asks agents to behave,
the Wire makes misbehavior structurally impossible.

```
888 — SOVEREIGN (Arif) — F13 veto
  ↓
arif_judge — Kernel :8088 — SEAL/HOLD/VOID
  ↓
Layer 3: Reasoning — F4 Monitor + Circuit Breaker
  ↓
Layer 2: Runtime — Ghost JSON/ENV + dep-check
  ↓
Layer 1: Static — /etc/arifos/organ_dependencies.json
  ↓
ORGANS: arifOS  A-FORGE  AAA  GEOX  WEALTH  WELL
```

## Layer 1 — Static Dependency Manifest (F1 / F2)

**File:** `configs/organ_dependencies.json`

Each organ declares what it depends on and the action to take when the
dependency fails:

```json
{
  "WEALTH": {
    "depends_on": {
      "GEOX": {"required_status": "healthy", "action": "HOLD"},
      "WELL": {"min_clarity": 7, "action": "HOLD_if_below"}
    },
    "provides": ["npv", "irr", "market_data"]
  }
}
```

Possible actions: `HOLD` (block entirely), `HOLD_if_below` (block when
metric below threshold), `WARN` (advisory), `OBSERVE` (log only).

## Layer 2 — Runtime Ghost Surface (F2)

**Files:** `/var/run/arifos_state.json`, `/var/run/arifos_env.sh`

Two read-only surfaces for the same reality. Compute cost ≈ 0.

```sh
# Agent surface (machine-readable)
source /var/run/arifos_env.sh
echo $AF_DEGRADED_ORGANS        # WELL
echo $AF_VITALITY                # 0.5946
echo $AF_VERDICT                 # HOLD

# Shell fast-path (human + script)
arif-dependency-check
# exit 0 = all satisfied
# exit 1 = some unmet → 888_HOLD
```

## Layer 3 — Reasoning Anti-Loop (F4 / ΔS < 0)

| Tool | Max | Action |
|---|---|---|
| `arif-circuit-breaker` | 2 attempts | LOCK + 888_HOLD on action loop |
| `arif-f4-monitor` | 3 cycles (no state change) | F4 VIOLATION, AUTOHOLD |

Both write to `/var/run/arifos_f4_state.json` and `/var/log/arifos_*.log`.

## Tool Index

| Tool | Mode | Purpose |
|---|---|---|
| `arif-dependency-check` | (default) | Cross-organ dep validation, exit 0/1 |
| `arif-circuit-breaker` | `record` / `status` / `reset` | Anti-loop guard, lock after 2 fails |
| `arif-f4-monitor` | `check` / `status` / `reset` | Reasoning entropy cap |

## Installation

```sh
# From arifOS source tree
cd /root/arifOS
make wire-install          # installs binaries + configs
make wire-uninstall        # reverses cleanly

# Manual (when Makefile not available)
sudo install -m 0755 scripts/wire/arif-dependency-check /usr/local/bin/
sudo install -m 0755 scripts/wire/arif-circuit-breaker   /usr/local/bin/
sudo install -m 0755 scripts/wire/arif-f4-monitor        /usr/local/bin/
sudo install -m 0644 scripts/wire/configs/organ_dependencies.json /etc/arifos/
```

## Blindspots Sealed (5)

| # | Blindspot | Risk | Fix |
|---|---|---|---|
| 1 | Execution Authority | Agent mis-diagnoses H_WELL as M_WELL | Circuit Breaker + WELL tool routing block |
| 2 | Cross-Organ Cascade | GEOX→WEALTH without WELL check | Dependency Manifest + validation script |
| 3 | F4 Reasoning Loop | Read-loop infinite, token burn | F4 Monitor, auto-HOLD at cycle 3 |
| 4 | Dirty kernel state | Untracked registry drift | Surface Conformance Gate (P0) |
| 5 | Wire tool orphan | `/usr/local/bin/` with no source repo | This dir — `arifOS/scripts/wire/` |

## Philosophy

> *"Agents don't need to think to be safe. Architecture makes fatal
> failure impossible."*

Outside the federation, AI is controlled with prompts.
arifOS controls with POSIX physics:

- `exit 2` is a command, not a suggestion
- `chmod -x` is law
- `md5sum` is witness that cannot lie
- File lock is a prison that AI cannot hallucinate its way out of

---

**Last sealed:** 2026-07-27 (Wire federation commit)
**Next review:** when a new organ joins the federation
