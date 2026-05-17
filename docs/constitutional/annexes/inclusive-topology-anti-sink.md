# Inclusive Topology / Anti-Sink Annex

> Cross-floor constitutional extension: F05 + F08 + F10 + F13
> Calhoun-Acemoglu bridge: institutional topology as constitutional diagnostic
> Version: 2026.05.14-v1

---

## 1. CORE DOCTRINE

**Inclusive topology is the anti-sink condition.**

A system (agent federation, institution, economy, Earth system) is at risk of
behavioral sink not when resources are scarce, but when its **topology becomes
extractive** — when social/organizational density removes meaningful roles,
severs feedback paths, and concentrates agency into passive spectatorship.

This annex adds **reversible runtime diagnostics** to detect extractive drift
before it becomes terminal. It does not create a new floor (F14). It extends
existing floors:

| Floor | Extension |
|-------|-----------|
| F05 PEACE | Maruah topology: are weakest stakeholders losing agency? |
| F08 GENIUS | Systemic health includes topological health: G ≥ 0.80 requires non-extractive topology |
| F10 ONTOLOGY | Structural coherence now includes role diversity and feedback integrity |
| F13 SOVEREIGN | Human sovereignty integrity must be tested, not assumed |

---

## 2. KEY DIAGNOSTICS

### 2.1 Anti-Sink Check (`arif_ops_measure(mode="topology")`)

Signals from John B. Calhoun's Universe 25, translated to institutional code:

| Calhoun Signal | Diagnostic | Meaning |
|----------------|------------|---------|
| Voluntary crowding | Topology risk | Are agents/people concentrating around chokepoints? |
| Territorial dominance | Extractive drift | Is one node capturing control? |
| Role collapse | Role diversity delta | Are meaningful differentiated roles disappearing? |
| Maternal breakdown | Feedback integrity | Is care/stewardship feedback severed? |
| "Beautiful ones" | Beautiful ones risk | Are agents producing aesthetic output without responsibility? |
| First death (agency) | Agency compression | Is human decision becoming symbolic before system fails? |
| Terminal extinction | Verdict | HOLD/VOID when topology is irreversibly extractive |

### 2.2 Institutional Drift Check (`arif_ops_measure(mode="drift")`)

Signals from Daron Acemoglu's institutional economics:

| Acemoglu Signal | Diagnostic | Meaning |
|-----------------|------------|---------|
| Inclusive institutions | Inclusive access | Are resources/decisions broadly accessible? |
| Extractive institutions | Extractive capture | Are elites controlling chokepoints? |
| Creative destruction | Innovation rights | Is innovation distributed or captured? |
| Rule of law | Appeal path | Are contestability mechanisms present? |
| Political equality | Participation width | Is participation broad or symbolic? |
| Elite capture | Elite chokepoint risk | Can elites block reform? |
| State capacity | Sovereignty integrity | Is human veto functional or decorative? |

---

## 3. RUNTIME INTEGRATION

### 3.1 Tool Surface

The diagnostics are exposed through the existing `arif_ops_measure` tool (777_OPS)
with two new modes:

- `mode="topology"` — returns `AntiSinkCheck` schema
- `mode="drift"` — returns `InstitutionalDrift` schema

Both are **reversible, read-only, advisory**. They do not block actions.
They return estimates with explicit confidence bands.

### 3.2 Verdict Integration

When `arif_judge_deliberate` processes a candidate, it SHOULD:

1. Call `arif_ops_measure(mode="topology")` as a pre-check
2. If `verdict=HOLD` or `agency_compression=high`, note it in `invariants_checked`
3. The Judge may downgrade SEAL to SABAR if topology diagnostics are adverse

### 3.3 Constitutional Gate Integration

The `_constitutional_gate` may call topology diagnostics for:
- `forge_execute` mutations (does this patch increase or decrease agency?)
- `vault_seal` entries (is this seal genuine or rhetorical?)
- `gateway_connect` relays (does this create a new chokepoint?)

---

## 4. REPO ROLE BOUNDARIES

This annex clarifies federation role topology — preventing the federation itself
from developing extractive topology:

| Repo | Role | Anti-Sink Responsibility |
|------|------|--------------------------|
| arifOS | Constitutional kernel | Define topology diagnostics, enforce constitution, maintain registry |
| AAA | Federation observer | Monitor cross-agent drift, dashboard topology risk |
| WEALTH | Economic topology | Detect extractive capital flows, ownership concentration |
| GEOX | Earth stewardship topology | Detect extraction-only resource logic, feedback breaks |
| A-FORGE | Constitutional mutation engine | Refuse patches that increase dependency without increasing agency |
| WELL | Human vitality mirror | Detect human fatigue, withdrawal, dignity erosion |
| VAULT999 | Immutable memory | Seal judgments, distinguish rhetorical from sealed |

**Anti-pattern: Any repo trying to become the whole brain.**
That is itself an extractive topology formation.

---

## 5. THRESHOLDS (v0 — Advisory)

| Diagnostic | Green | Yellow | Red |
|------------|-------|--------|-----|
| Agency delta | positive | neutral | negative |
| Role diversity delta | positive | neutral | negative |
| Feedback integrity | strong | partial | weak/absent |
| Topology risk | low | medium | high |
| Extractive drift | low | medium | high |
| Agency compression | low | medium | high |
| Sovereignty integrity | strong | degraded | symbolic |

These thresholds are **initial estimates**. They should be refined through
operational experience and sovereign calibration.

---

## 6. FUTURE WORK

1. Wire real sensor data: measure actual agent call patterns, not stubs
2. Track topology metrics over time to detect drift trends
3. Add AAA dashboard visualization of topology risk
4. Implement automatic SABAR when consistency rules fire
5. Run Calhoun agent-based model simulation to validate thresholds

---

## 7. SOURCES

- Calhoun, J.B. (1962). "Population Density and Social Pathology." *Scientific American*.
- Calhoun, J.B. (1973). "Death Squared." *Proc R Soc Med*.
- Shumailov, I. et al. (2024). "AI models collapse when trained on recursively generated data." *Nature*.
- Acemoglu, D. & Robinson, J. (2012). *Why Nations Fail*.
- Rockström, J. et al. (2023). "Earth beyond six of nine planetary boundaries." *Science Advances*.

---

*Sealed: 2026-05-14 | Authority: F05+F08+F10+F13 extension | Sovereign: Arif*
*DITEMPA BUKAN DIBERI*
