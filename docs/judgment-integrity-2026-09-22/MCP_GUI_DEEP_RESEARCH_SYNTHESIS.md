# MCP GUI Architecture — Deep Research Synthesis
## 2026-09-22 — after Copilot external deep research

Source: paste 8 (MCP-UI spec URL) + deep research report from external Copilot (2026-09-22).
Source quality: HIGH on MCP Apps protocol/security; MED-HIGH on federation implementation; LOW on CHRON (no live contract).

---

### The Compressed Invariant Set (canonical form)

**5 positive invariants (a GUI is needed when AT LEAST ONE applies):**

| Code | Name | Need |
|---|---|---|
| **W** | Direct Witness | Human must inspect evidence that would be materially distorted by generative or serial translation |
| **R** | Relational Perception | Geometry, comparison, anomaly or trend is decision-relevant and visual encoding measurably improves the task |
| **S** | Continuing State | Safe action requires persistent context, freshness, or temporal history across turns |
| **C** | Consequence Friction | High-impact transitions require deliberate review proportional to reversibility and blast radius |
| **A** | Transaction-Bound Authority | Execution requires human authority that the model cannot create, replay, or redirect |

**3 hard vetoes (STOP even if any invariant matches):**

| Veto | Condition |
|---|---|
| Epistemic | Inconsistent or unversioned backend state — `HOLD / INCONSISTENT STATE` shown, authorization disabled |
| Redundancy | Existing probe/surface already satisfies the task — don't build |
| Exposure | Privacy or attack-surface cost exceeds decision value — redesign or don't build |

### The Minimal Decision Test

```
Start: JSON/text only.
  → If no human decision, witnessing, or continuing oversight is required → STOP: no GUI.
  → Otherwise check W/R/S/C/A:
    none match → no GUI
    only W/R/S → smallest read-only embedded witness
    deep spatial manipulation needed → standalone workbench
    C or A → narrow decision/authority surface + server-side transaction binding
  → Then check vetoes:
    inconsistent backend → HOLD/no authority UI
    duplicate observability → don't build
    unnecessary private exposure → redesign or don't build
```

---

### What the Research Got Right That My Original List Was Light On

1. **"Authority from a non-AI channel" (Inv #6 in original) is INSUFFICIENT.** Strengthened to **transaction-bound human authority**: actor-bound, transaction-bound, state-bound, scope-bound, fresh, single-use, server-enforced. The model can prepare the transaction but cannot mint or satisfy the authority proof.

2. **"A button is not authority."** MCP App widgets can call `sendPrompt` programmatically. If the design isn't careful, a widget can "type on the human's behalf". Invariant #6 only holds if the approve button isn't callable by the model.

3. **Typed phrases are weak.** "Type 'YES' to confirm" is mainly protection against accidental clicks, not strong identity or transaction proof. **Ambiguous chat "yes" should never authorize high-impact execution** because the model can generate identical text.

4. **HCI evidence matters.** Cleveland & McGill 1984: position-on-common-scale > length > angle for accuracy. Ondov et al.: overlay and mirror symmetry outperform small-multiples for some tasks. Invariants #3, #4, #7 are task-specific perceptual claims, not "visual is always better."

5. **Persistent display has costs.** Every persistent surface needs freshness, source, and state-version indicators. Stale state is worse than no display.

6. **Counter-invariant C is hard stop.** Polished canonical card over contradictory backend is **epistemically harmful**. The research is harsher than I was — not just "block", but "this is a worse failure mode than no GUI at all."

---

### Proportional Friction Table (from research)

| Consequence | Minimum sufficient control |
|---|---|
| Read-only / harmless | No confirmation |
| Reversible local change | Clear button or concise chat confirmation |
| Material but readily reversible | Preview + explicit action + audit receipt |
| Destructive / external / costly | Exact target+delta preview + separate confirm action + short-lived nonce |
| Privileged or financially consequential | Above + re-auth + server-side authorization |
| Catastrophic / poorly reversible | Two-step prepare/commit + independent policy or second approver |

This is the **friction calibration by consequence**. My `next_safe_action` fix (crack #7) was the start of this; the broader application needs an authority service (not just button wiring).

---

### Federation GUI Classification (per research)

| Organ | Classification | Smallest justified primitive | Decision |
|---|---|---|---|
| GEOX | **REQUIRED** for spatial witness; **JUSTIFIED** embedded review | Seismic/map/log/cross-section witness; uncertainty/provenance overlay | **Retain** JSON + selected embedded witnesses. Standalone ONLY for deep 3D manipulation. **Reduce surface count** (currently overlapping). |
| arifOS | **REQUIRED** only as authority/decision surface | One verdict, evidence, contradictions, common-axis alternatives, risk/reversibility, state hash, authorization control | **No ops dashboard.** Contradictory verdicts force HOLD. |
| WEALTH | **JUSTIFIED** | Side-by-side scenario distributions on common axes | **No market dashboard** unless persistent monitoring is actually required |
| CHRON | **UNKNOWN** | — | **HOLD GUI** until runtime contract verified |
| WELL | **OPTIONAL; potentially HARMFUL** | Private, user-controlled indicator with minimum disclosure | **No team dashboard.** Text + private views. |
| A-FORGE | **JUSTIFIED** at commit boundary only | Diff/plan preview, blast radius, gate result, rollback | **Reuse existing ops probes.** No duplicate dashboard. |
| HERMES | **OPTIONAL; default text-native** | Task/result stream or structured handoff receipt | Full GUI unjustified absent a proven bottleneck |

---

### Do-Not-Build List (the research was emphatic)

- Federation-wide "single pane of glass"
- Full arifOS dashboard
- Separate GUI for every MCP tool
- UI-only execution path
- **Authority button without transaction-bound server authorization** ← most important
- Dashboard reproducing Grafana/Prometheus/health probes
- WELL team visibility by default
- CHRON surface before its canonical runtime contract exists
- Any polished surface over contradictory backend truth

---

### Self-Correction on My Crack #6+#2 Design

The research refines my approach. The **minimum required change** to crack #6+#2 is NOT just "rename fields". It's:

1. **Canonicalize the verdict contract first** (this is my #6+#2 work, but smaller: just `verdict` and `next_safe_action`)
2. **DO NOT build any UI until the kernel is clean** (counter-invariant C blocks it)
3. **When GUI is built, it MUST consume the canonical contract** (don't let it pick the "nicer verdict" — show `HOLD / INCONSISTENT` if state diverges)
4. **Authority must be transaction-bound server-side**, not a button-click

**My revised crack #6+#2 design still holds**, but I should make the "stop condition" explicit in the code: if `verdict != effective_verdict`, render `HOLD/INCONSISTENT` and **disable any authority control**.

---

### Updated Roadmap (per research)

1. **Canonicalize contracts first** ← my Tier 2 (crack #6+#2)
2. **Preserve JSON data plane** ← JSON remains canonical, UI is progressive enhancement
3. **Consolidate GEOX witnesses** ← reduce GEOX surface count (currently overlapping)
4. **Implement arifOS read-only decision surface (NO execute control initially)** ← after verdict canonical
5. **Implement authority service (prepare/commit state machine, single-use grant, state recheck, receipt)** ← BEFORE any irreversible execute control
6. **Add WEALTH scenario comparison** ← only with proven common axes
7. **Define CHRON before visualization** ← HOLD GUI until contract verified
8. **Keep WELL private; HERMES text-native**

---

### Bijaksana Lens (re-applied)

- **F2 (Truth)**: the canonical verdict contract IS the truth. The duplicate `effective_verdict` is a Truth leak.
- **F11 (Capability ≠ Authority)**: a button isn't authority. The model can prepare, only the human + server can authorize.
- **F1 (Reality)**: the live probe proved the response has only 2 verdict fields, not 4. Don't design against assumptions.
- **F4 (Reversibility)**: my rename + reconciliation function is additive. Revert = behavior identical.
- **Counter-invariant C**: never build UI on contradictory state. The veto is **hard**, not "soft".

---

### What I'll Do With This

1. Update `CRACK6_DESIGN.md` to incorporate the canonical-form invariants (5+3) + the explicit "stop condition: HOLD/INCONSISTENT" rule
2. Hold the broader arifOS GUI until after the verdict canonical lands AND the authority service exists
3. Keep JSON as the canonical data plane for everything

### Decisions Needed

Same as before:
1. Continue with revised crack #6+#2? (yes/no/reprioritize)
2. Same admin-squash strategy as #7? (yes/no)
3. Commit the design doc + probe script as tracked artifact? (yes/no)
4. **New**: should I also create a `arifOS_AUTHORITY_SERVICE_DESIGN.md` for the prepare/commit/grant/receipt pattern that the research surfaced? (yes/no)
