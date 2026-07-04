# ADR-014: Market Convergence Gap Analysis — arifOS vs Top 10 Agentic Runtimes

**Status:** DRAFT
**Date:** 2026-06-29
**Sovereign:** Arif (F13)
**Forge session:** Hermes ASI, Telegram DM thread 104127
**Trigger:** Market scan of top 10 agentic apps → gap analysis against F1-F13 constitutional surface
**Related:** ADR-001 (Kernel-Issued Leases), ADR-011 (Plan Membrane), ADR-012 (Receipt Lineage)

---

## 1. Context

Arif dropped a market scan of the top 10 agentic apps (Codex, Claude Code, Cursor, Manus,
Replit Agent, Zapier Agents, Make/Gumloop, Microsoft Copilot Studio, Google Gemini/Spark,
OpenClaw). The signal: **"Software is becoming delegable."** The market is converging toward
constitutional runtime — tool access, memory, permissions, execution logs, rollback, human
approval gates, multi-agent orchestration, MCP/API surfaces.

This ADR maps each competitor's runtime pattern against the F1-F13 constitutional surface,
identifies where arifOS leads, where it lags, and names the 3 highest-impact engineering
gaps to close.

---

## 2. Competitor Runtime Pattern Map

### 2.1 What arifOS Already Has (Constitutional Lead)

| Capability | arifOS | Market Status |
|------------|--------|---------------|
| Explicit constitutional floors (F1-F13) | ✅ Enforced at every tool boundary | ❌ No competitor has named, enforceable floors |
| Pre-tool constitutional reflex (ART) | ✅ POWER/TRUST/STATE check before every call | ⚠️ Claude Code has hooks; others have approval only |
| Append-only immutable ledger (VAULT999) | ✅ Hash-chained, sealed events | ⚠️ Claude Code: append-only sessions; no sealed chain |
| Metabolic pipeline (000→999) | ✅ 7-stage governed pipeline | ❌ No competitor has staged governance |
| Tri-witness (Human/AI/Earth) | ✅ Constitutional defaults | ❌ Unique to arifOS |
| Lease system (A-FORGE) | ✅ Time-bounded, revocable execution grants | ⚠️ Claude Code subagent delegation; Codex worktrees |
| M/D boundary (kernel vs presentation) | ✅ Deterministic M-Layer + human-facing D-Layer | ❌ Unique to arifOS |
| Scar registry (identity by consequence) | ✅ Permanent malu_index + tebus_salah recovery | ❌ Unique to arifOS |
| Rasa contract (affective governance) | ✅ Phase 1+2, typed governance metadata | ❌ Unique to arifOS |
| KSR membrane (kernel-state vs memory) | ✅ Live authority vs advisory past | ⚠️ Claude Code: session state; no explicit membrane |

### 2.2 Per-Competitor Runtime Pattern Analysis

| Competitor | Runtime Pattern | Permission Model | Isolation | Rollback | Observability |
|------------|----------------|-----------------|-----------|----------|---------------|
| **OpenAI Codex** | Dual: cloud sandbox + local CLI. Git worktrees. Multi-agent threads. | 3 approval levels (Suggest, Auto Edit, Full Auto). Named profiles. | Git worktrees per agent thread | Git-based (worktree isolation = natural rollback) | Visual diff viewer, context window indicator, thread inventory |
| **Claude Code** | Single agentic loop (queryLoop). ReAct pattern. | 7 permission modes + ML classifier. Deny-first. Graduated trust. Defense-in-depth (deny rules, hooks, classifier, sandbox). | Subagent delegation with isolated context | Append-only session storage. Reversibility-weighted risk. | Permission classifier visibility. CLAUDE.md memory (file-based, transparent). |
| **Cursor** | IDE-native (VS Code fork). Parallel agents + Composer. Cloud sandbox for background agents. | Explicit approval gates per agent action. Per-task scope. | Cloud sandbox for background agents | Multi-file diff review before accept | Visual diff review, parallel agent panel |
| **Manus** | Cloud sandbox. Async general-purpose agent. | Sandbox boundary only. No fine-grained permission model. | Sandbox only | None visible | Report output only |
| **Replit Agent** | Hosted sandbox. Natural language → app pipeline. | Sandbox is the only gate. | Hosted environment | Replit's version history | Live preview |
| **Zapier Agents** | Workflow automation. App integration layer. | Pre-existing app permissions. Enterprise trust model. | Per-app connection | Workflow version history | Workflow run logs |
| **OpenClaw** | Gateway control plane. Multi-channel adapters. Plugin extensibility. | Tool sandboxing. Session-based security. Tool policy precedence. | Tool sandboxing. Session boundaries. | Session state + memory search | Gateway logs, channel adapters |
| **Microsoft Copilot Studio** | Enterprise distribution via M365. | Enterprise tenant permissions. | Tenant boundary | Tenant audit logs | Power Platform analytics |
| **Google Gemini/Spark** | Workspace-integrated. Always-on cloud tasks. | Google Workspace permissions. | Cloud project boundary | Workspace version history | Google Cloud monitoring |
| **Make/Gumloop** | Low-code workflow automation. | Per-step configuration. | Workflow scoping | Workflow version history | Run history dashboard |

### 2.3 Market Convergence Signals

Six patterns are converging across all top competitors:

1. **Permission graduations** — Binary allow/deny is dead. Everyone has 3-7 trust levels.
2. **Execution isolation** — Git worktrees (Codex), subagent isolation (Claude), cloud sandboxes (Cursor, Manus, Replit).
3. **Append-only audit** — Claude Code's session storage, Codex's git commits, arifOS's VAULT999.
4. **Human-in-the-loop at tool boundaries** — Not just "approve the plan." Approve the specific action.
5. **Multi-agent orchestration** — Codex multi-agent v2, Cursor parallel agents, Claude Code subagents.
6. **Runtime governance as a layer** — Separate from model weights. Gartner confirms 4-layer stack; "runtime enforcement" is now a named category.

---

## 3. F1-F13 Coverage: Where arifOS Leads

| Floor | arifOS Coverage | Best Competitor Coverage | Gap Direction |
|-------|---------------|-------------------------|---------------|
| **F1 AMANAH** | Reversible-first. Irreversible → 888 HOLD. | Claude Code: reversibility-weighted risk. | arifOS leads (explicit floor vs implicit heuristic) |
| **F2 TRUTH** | ≥0.99 accuracy or declare uncertainty band. Epistemic tagging (TAHU/NAMPAK/RASA/TAK TAHU). | Claude Code: model emits tool_use, harness validates. No epistemic tagging. | arifOS leads |
| **F3 WITNESS** | Theory·constitution·intent alignment. Tri-witness defaults. | None. | arifOS uniquely leads |
| **F4 CLARITY** | ΔS ≤ 0. Output entropy reduction enforced. | None explicit. | arifOS leads |
| **F5 PEACE** | Peace ≥ 1.0. Maruah guard. | None explicit. | arifOS leads |
| **F6 EMPATHY** | Dignity-first. ASEAN/MY context. M-Layer Maruah. | None explicit. | arifOS leads |
| **F7 HUMILITY** | Ω₀ ∈ [0.03, 0.05]. No fake certainty. | None explicit. | arifOS leads |
| **F8 GENIUS** | Intelligence quality, system health. Verification parity. | Claude Code: capability amplification value. | Comparable |
| **F9 ANTIHANTU** | C_dark < 0.30. No consciousness claims. | Claude Code: safety/security value. No explicit anti-hallucination formula. | arifOS leads |
| **F10 ONTOLOGY** | AI-only ontology. No soul/feelings claims. | None explicit. | arifOS leads |
| **F11 AUTH** | Identity verification before sensitive ops. Sovereign geometry. | Claude Code: device pairing. Codex: named profiles. | Comparable |
| **F12 INJECTION** | Input sanitization. Prompt injection guard. | Claude Code: prompt injection addressed in safety model. | Comparable |
| **F13 SOVEREIGN** | Human veto absolute. 888_HOLD. | Claude Code: "Human Decision Authority" value. Codex: approval levels. | arifOS leads (constitutional, not configurable) |

**Verdict:** arifOS leads on 10/13 floors, is comparable on 3 (F8, F11, F12). No competitor surpasses arifOS on any floor. **The constitutional kernel is ahead.**

---

## 4. Engineering Gaps: Where arifOS Lags

The gap is not constitutional depth — it's **operational surface**. Competitors ship faster, show more, isolate better.

### Gap Analysis Matrix

| Engineering Capability | Codex | Claude Code | Cursor | arifOS | Gap Severity |
|------------------------|-------|-------------|--------|--------|--------------|
| **Live observability dashboard** | Visual diff + context indicator + thread inventory | Permission classifier visibility | Visual diff + parallel agent panel | VAULT999 (sealed, not surfaced live) | 🔴 CRITICAL |
| **Filesystem isolation (worktree/sandbox)** | Git worktrees per thread | Subagent isolation | Cloud sandbox | A-FORGE leases (no fs isolation) | 🔴 CRITICAL |
| **Automated rollback (git revert on receipt)** | Git-based (natural) | Append-only + reversibility-weighted | Multi-file diff review | VAULT999 records but can't revert | 🟡 HIGH |
| **Graduated permission UX** | 3 approval levels + named profiles | 7 permission modes + ML classifier | Explicit approval gates | ART binary: PROCEED/HOLD | 🟡 HIGH |
| **Context compaction pipeline** | Context window indicator | 5-layer compaction | Unknown | Memory tiers, no active compaction | 🟡 HIGH |
| **Multi-channel delivery** | CLI + Desktop + SDK | CLI + headless + SDK + IDE | IDE-native | Telegram only | 🟢 MEDIUM |
| **Plugin marketplace** | 90+ plugin marketplace | MCP + plugins + skills + hooks | MCP servers | Skills library (no marketplace) | 🟢 MEDIUM |
| **Cloud sandbox execution** | Cloud sandbox + local CLI | Local only | Cloud + local | Local only | 🟢 MEDIUM |
| **Subagent spawn UX** | Multi-agent threads v2 | Subagent delegation | Parallel agents panel | delegate_task + A-FORGE spawn | 🟢 LOW |

---

## 5. Top 3 Engineering Gaps (Ranked by Impact)

### Gap 1: Live Observability & Execution Receipts Surfaced to UI 🔴

**What competitors do:**
- Codex: Visual diff viewer shows files being written in real-time. Context window indicator shows token usage. Thread inventory shows all active agents.
- Claude Code: Permission classifier surfaces WHY an action was allowed/denied. CLAUDE.md is transparent, version-controllable memory.
- Cursor: Parallel agent panel shows each agent's status. Multi-file diff review before accept.

**What arifOS has:**
- VAULT999 seals every action with hash-chain integrity.
- AAA cockpit shows organ health but NOT agent execution state.
- ART reflex evaluates every tool call but the verdict (PROCEED/HOLD) is not surfaced to a live dashboard.
- No real-time view of: which agent is doing what, which tool is active, what the blast radius is, what the last N verdicts were.

**What to build:**
- `arif_observe` live stream → AAA cockpit WebSocket.
- Per-agent execution panel: current tool, current verdict, blast radius badge, last 5 actions with receipt hashes.
- "Why HOLD?" explainer: which floor(s) triggered, what evidence is missing, what the human needs to do.
- Receipt lineage viewer: click any sealed receipt → see full chain (what led to this, what followed).

**Impact:** This is the gap between "governed" and "governed AND visible." Without it, arifOS governance is real but invisible — the operator trusts the kernel but can't see it working.

### Gap 2: Filesystem Isolation for Concurrent Agents 🔴

**What competitors do:**
- Codex: Every agent thread gets its own git worktree. Agents cannot collide on file mutations.
- Claude Code: Subagents get isolated contexts. Parent agent sees only the result, not intermediate state.
- Cursor: Background agents run in cloud sandboxes, isolated from local filesystem.

**What arifOS has:**
- A-FORGE leases: time-bounded, revocable execution grants. But no filesystem isolation.
- When Hermes spawns OpenClaw and both touch `/root/`, there's no worktree barrier.
- One agent's `write_file` can collide with another's `patch`.

**What to build:**
- `arif_forge` with `isolation: worktree` mode: auto-create git worktree in `/root/forge_work/worktrees/<session_id>/`.
- Agent works in isolated worktree; on completion, changes are merged via `git merge` with receipt hash in commit message.
- Collision detection: if two agents touch the same file, second agent gets HOLD + "file locked by session X."
- Cleanup: worktree pruned on lease expiry or explicit `arif_forge` close.

**Impact:** Without this, multi-agent arifOS is dangerous-by-default. With it, concurrent agents (Hermes + OpenClaw + cron jobs) can run safely.

### Gap 3: Automated Rollback Primitives 🟡

**What competitors do:**
- Codex: Every agent action is a git commit in a worktree. Rollback = `git revert`.
- Claude Code: Reversibility-weighted risk assessment. Append-only session storage means every state change is recoverable.
- Cursor: Multi-file diff review before accept = human veto before mutation lands.

**What arifOS has:**
- VAULT999 records every sealed action with hash-chain integrity.
- F1 AMANAH requires reversible-first.
- But: no automated rollback. If an agent writes a bad file, VAULT999 knows it happened but can't undo it.

**What to build:**
- `arif_rollback(receipt_hash: str)` → identifies the git commit containing that VAULT999 receipt, runs `git revert`, seals the rollback as a new VAULT999 event.
- Every agent file mutation auto-wrapped in `git commit` with `receipt: <hash>` in the message.
- Rollback eligibility: reversible mutations only. Irreversible (external side-effect, sent email, deployed code) → HOLD with human confirmation.
- Rollback chain: VAULT999 event `rollback_initiated` → `git revert` → `rollback_sealed` with new receipt.

**Impact:** Closes the loop between "governed" and "recoverable." F1 AMANAH demands reversible-first; this makes it operational at the tool level.

---

## 6. Strategic Recommendation

### Don't Copy. Expose Governance As UX.

The competitors are converging toward constitutional runtime. They're building implicit versions of F1-F13. arifOS already has the explicit constitutional kernel. The move is NOT to copy their UX patterns — it's to **expose arifOS's constitutional depth as the UX differentiator.**

| Competitor | Their UX | arifOS Counter-UX |
|------------|----------|-------------------|
| Codex "3 approval levels" | User picks Suggest/Auto/Full | arifOS: "This action is F1 AMANAH-compliant (reversible). Proceeding. [receipt: sha256:abc123]" |
| Claude Code "permission denied" | Model classifier says no | arifOS: "HOLD — F11 AUTH: identity not verified. Authenticate or escalate to 888." |
| Cursor "review diff" | Human reviews before accept | arifOS: "MUTATION sealed. Rollback available: arif_rollback(sha256:def456). [VAULT999: event #12345]" |

### Build Order

1. **Gap 1 (Observability Dashboard)** — Highest impact. Makes governance visible. Enables all other gaps to be seen.
2. **Gap 2 (Filesystem Isolation)** — Safety prerequisite for multi-agent. Without it, Gap 3 is less useful.
3. **Gap 3 (Rollback Primitives)** — Closes the F1 AMANAH loop. Operationalizes reversibility.

**Estimated effort:** Each gap is a 3-5 artifact constitutional patch (spec doc + Pydantic contract + implementation + adoption recipe + lineage audit). See `arifos-constitutional-patch-authoring` skill for the canonical 5-artifact shape.

---

## 7. Constitutional Invariants (Must Hold After Any Patch)

1. **F1 AMANAH:** No action becomes less reversible. New isolation/rollback must increase reversibility.
2. **F13 SOVEREIGN:** Dashboard shows, never overrides. Human veto path must remain shorter than any dashboard path.
3. **VAULT999 integrity:** Observability reads from VAULT999; never writes. Dashboard is a view, not a new authority surface.

---

## 8. Open Questions

1. Should the observability dashboard live in AAA cockpit (port 3001) or be a new organ?
2. Worktree isolation: per-session or per-agent? (Per-agent = more isolation, more disk. Per-session = simpler, less safe.)
3. Rollback scope: file mutations only, or also database/supabase/email? (Start with file mutations; external side-effects need human-in-loop by definition.)

---

*DITEMPA BUKAN DIBERI — The market converges toward constitutional runtime. arifOS is already there. The gap is visibility, not depth.*
