# CODEX TASKS — arifOS v35Ω / v36.1Ω Bridge Addendum

This file records **local follow‑up work** performed after the original
`CODEX_TASKS_DEEPSCAN_v35Omega.md` report that was generated in the
remote context. It should be read as an **addendum**, not a replacement.

The goal of this addendum is simple:

- Capture the **v36.1Ω W@W Federation upgrade** that you just completed.
- Keep it in the same “deepscan report” style, so future engineers and
  LLMs can see what changed without re‑running a full scan.

---

## 9.7 W@W Federation v36.1Ω Bridge Architecture Upgrade

Scope: **W@W organs only** (WELL, RIF, WEALTH, GEOX, PROMPT).  
Epoch: **v36.1Ω measurement / architecture layer**, runtime verdicts remain
aligned with v35Ω law unless explicitly promoted.

### 9.7.1 What Changed

- **Bridge layer introduced for all 5 organs** under `arifos_core/waw/bridges/`:
  - `well_bridge.py` → optional tone/somatic safety socket (guardrails/langkit).
  - `geox_bridge.py` → optional reality/RAG socket (LlamaIndex‑style).
  - `rif_bridge.py` → optional epistemic rigor socket (Ragas/DSPy‑style).
  - `wealth_bridge.py` → optional policy/trust socket (Llama Guard‑style).
  - `prompt_bridge.py` → optional Anti‑Hantu / prompt‑structuring socket (Guidance/Outlines‑style).
- Each bridge:
  - Uses `try/except` imports; if libraries are missing, returns `None`.
  - Returns **deltas** or simple flags in small dataclasses
    (`WellBridgeResult`, `GeoxBridgeResult`, `RifBridgeResult`,
    `WealthBridgeResult`, `PromptBridgeResult`).
  - Never decides verdicts; organs remain sovereign.
- Organs updated to consult bridges *then* run their existing heuristics:
  - `WellOrgan` recomputes `peace_squared` and `kappa_r` from a neutral baseline,
    applies bridge deltas (when present), then regex penalties.
  - `RifOrgan` starts from `metrics.delta_s` and `metrics.truth`, applies bridge
    deltas, then hallucination/contradiction/certainty penalties.
  - `WealthOrgan` starts from `metrics.amanah`, treats bridge `amanah_breach`
    as an additional trust‑break, then applies scope/trust regex checks.
  - `GeoxOrgan` keeps its existing reality checks, with optional `e_earth_delta`
    from the bridge.
  - `PromptOrgan` keeps Anti‑Hantu/manipulation/exaggeration regex checks, with
    optional `anti_hantu_fail` flag and `c_budi_delta` from the bridge.

### 9.7.2 Floor & Behaviour Status

- **Zero‑Break guarantee**:
  - With no external libraries installed, all bridges return `None`.
  - Organs behave exactly as in the original v35Ω implementation; verdict
    thresholds and categories are unchanged.
- **Tests**:
  - `pytest tests/test_waw_organs.py -q` → **54/54 tests PASS** after the upgrade.
  - `scripts/test_waw_signals.py` confirms @WELL/@GEOX signals are sane in a
    small manual harness.
- **Truth Polarity diagnostics** (measurement‑layer only):
  - `scripts/torture_test_truth_polarity.py` verifies the v36.1Ω Truth
    Polarity logic (Truth‑Light, Shadow‑Truth, Weaponized Truth, False Claim).
  - This script uses a `MockApexJudge` and does not affect runtime verdicts;
    it is a regression test for the measurement canon.

### 9.7.3 Governance Interpretation

- W@W is now a **hybrid “cyborg” architecture**:
  - Law and veto logic still live in `arifos_core/waw/*.py` organs and
    `WAWFederationCore`.
  - Optional bridges allow future integration of industry‑grade detectors
    **without ceding sovereignty** to any single vendor library.
- Until explicit promotion:
  - v35Ω remains the binding runtime law.
  - v36.1Ω W@W bridge layer is a **structural upgrade** and a **measurement /
    integration surface**, not a change to constitutional floors or verdicts.

Floor status for this addendum: **SEAL** (no hard‑floor changes; behaviour
preserved; architecture documented for future migrations).

