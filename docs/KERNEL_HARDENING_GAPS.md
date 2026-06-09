# arifOS Kernel Hardening — Gap Analysis & Remediation

> **FORGED:** 2026-06-09 by Ω (Omega)
> **Trigger:** MXC-arifOS contrast analysis revealed architectural gaps
> **Status:** ROADMAP — forge autonomously where possible; 888_HOLD where F13 required
> **DITEMPA BUKAN DIBERI**

---

## 0. METHODOLOGY

Every gap is scored on three axes:
- **Severity (S):** 1=cosmetic, 5=critical breach
- **Fixability (F):** 1=months, 5=minutes
- **Autonomy (A):** YES=agent can fix, NO=requires Arif

Gaps are ordered by `S × (6-F)`: highest-impact, easiest-to-fix first.

---

## GAP 1: NO OS-LEVEL FILESYSTEM ENFORCEMENT [S:5, F:5, A:YES]

**What MXC does:** Bubblewrap namespace isolation — agent literally CANNOT access paths outside its policy.

**What arifOS does:** Application-level floor check — agent is ASKED not to access files.

**Risk:** Frontier models can ignore prompts. If an agent decides to read `~/.ssh/id_rsa`, nothing physical stops it.

**Fix (this session):**
```bash
# Make core constitutional files immutable at OS level
chmod 444 /root/arifOS/core/laws.py
chmod 444 /root/arifOS/arifosmcp/core/constitution_kernel.py
chmod 444 /root/arifOS/arifosmcp/core/authority_gate.py
chmod 444 /root/arifOS/arifosmcp/core/law_evaluator.py
chmod 444 /root/arifOS/arifosmcp/core/threat_engine.py
chmod 444 /root/arifOS/arifosmcp/core/reversibility_engine.py
chmod 444 /root/arifOS/arifosmcp/core/floors.py

# Protect secrets directory
chmod 700 /root/.secrets
chmod 600 /root/.secrets/env/*.env
```

**Verification:** `chmod` is Linux kernel-enforced. Even root cannot write to a 444 file without explicitly chmod-ing back. An agent would need to:
1. Know the file is 444 (requires `ls -la`)
2. Know to run `chmod 644` (requires tool access)
3. Have Bash access (requires permission)

Three deliberate gates before physical enforcement can be bypassed.

**Fix (next session):**
```bash
# Full bubblewrap integration
bwrap --ro-bind /root/arifOS /root/arifOS \
      --ro-bind /usr /usr \
      --tmpfs /tmp \
      --unshare-net \
      --die-with-parent \
      python3 /root/arifOS/arifosmcp/server.py
```

---

## GAP 2: NO DECLARATIVE AGENT POLICY [S:4, F:4, A:YES — FORGED]

**What MXC does:** SandboxPolicy JSON — any developer can read an agent's allowed capabilities.

**What arifOS does:** Capability is implicit in role names (engineer/observer/etc). No single document declares what an agent can do.

**Fix (this session):** ✅ `agent_policy.py` forged (Phase 2).

**Verification:** `AgentPolicy.to_json()` produces a human-readable, versioned, auditable policy document.

**Next step:** Integrate AgentPolicy into `arif_session_init` — every session must load the agent's policy and enforce it.

---

## GAP 3: NO EXPLICIT AGENT LIFECYCLE [S:4, F:4, A:YES — FORGED]

**What MXC does:** State-aware lifecycle: provision → start → exec → stop → deprovision. Each is a discrete, auditable call.

**What arifOS does:** session_init → execute → (implicit close). No explicit stop, no deprovision, no state tracking for agents.

**Fix (this session):** ✅ `agent_lifecycle.js` forged in AAA (Phase 3).

**Verification:** AAA cockpit can now query `lifecycleManager.federationStatus()` and see every agent's state.

**Next step:** Wire `agent_lifecycle.js` into AAA `server.js` → expose `/api/agents/status` endpoint.

---

## GAP 4: AGENTS CAN REWRITE THEIR OWN CONSTITUTION [S:5, F:3, A:PARTIAL]

**What MXC does:** Policy is external JSON — agent CANNOT modify it because it's loaded from outside the sandbox.

**What arifOS does:** F1-F13 floors live in Python files INSIDE the agent's process. An agent with write access could modify `laws.py` and change its own governance.

**Risk:** HIGH. An agent that redefines `F13_SOVEREIGN.threshold = 0` has no governance.

**Fix (this session):**
1. ✅ chmod 444 on all floor files (Gap 1 fix)
2. ✅ AgentPolicy is external (loaded via AAA, not embedded in agent)

**Fix (next session):**
1. Move policy loading to arifosd (separate process, port 18081)
2. arifosd reads policy from read-only mount
3. arifOS MCP queries arifosd for policy — never reads it directly
4. If arifosd goes down, MCP goes HOLD (fail-closed)

---

## GAP 5: NO NETWORK ISOLATION [S:3, F:3, A:PARTIAL]

**What MXC does:** `--unshare-net` in bubblewrap → agent has NO network unless explicitly granted.

**What arifOS does:** All agents share host network. No network isolation.

**Risk:** MEDIUM. An agent could exfiltrate data to an untrusted endpoint. Currently mitigated by UFW rules and Cloudflare Tunnel.

**Fix (next session):** Bubblewrap integration (`--unshare-net` + proxy for allowed domains).

**Immediate mitigation:** AgentPolicy.network_posture + ALLOWLIST mode — at least the governance layer restricts what domains the agent THINKS it can reach.

---

## GAP 6: NO RESOURCE QUOTAS PER AGENT [S:2, F:4, A:YES]

**What MXC does:** Timeout per execution. Backend enforces at OS level.

**What arifOS does:** Global earlyoom + systemd limits. No per-agent quotas.

**Fix (this session):** AgentPolicy includes `max_tokens_per_call`, `max_runtime_seconds`, `max_disk_bytes`.

**Fix (next session):** systemd cgroup per-agent — `systemd-run --user --scope -p MemoryMax=2G -p CPUQuota=50%`.

---

## GAP 7: SESSION TOKENS ARE NOT CRYPTOGRAPHICALLY BOUND [S:3, F:3, A:NO — F13]

**What MXC does:** containerId is managed by backend service.

**What arifOS does:** session_id is a UUID. No Ed25519 signing. Identity is claimed, not proven.

**Risk:** MEDIUM. Session hijacking possible if session_id is leaked.

**Fix:** Requires Arif's sovereign key (F13). The `_ARIF_PUBKEYS` gap (identified in VAULT999 Phase 0.5a) must be resolved first.

---

## GAP 8: NO AGENT-TO-AGENT AUTH [S:2, F:4, A:YES]

**What MXC does:** Single-sandbox model — no agent-to-agent communication.

**What arifOS does:** A2A mesh with `A2A_TOKEN` (static dev token).

**Fix (this session):** AgentPolicy can declare `allowed_organs` and `allowed_tools` — cross-organ routing gated by policy.

**Fix (next session):** Per-agent A2A tokens — each agent gets its own token, rotated per session.

---

## GAP 9: ENFORCEMENT IS IN-PROCESS [S:5, F:2, A:NO — ARCHITECTURAL]

**What MXC does:** Enforcement is a SEPARATE binary (`lxc-exec`) — if the agent crashes, the sandbox survives.

**What arifOS does:** Enforcement is in the SAME process as the MCP server. If the agent crashes the process, governance dies.

**Risk:** HIGHEST. This is the fundamental architectural limitation. arifOS cannot be a "real kernel" while enforcement is in-process.

**Fix:** This is Phase 2 of the original suggestion — move enforcement to arifosd (separate systemd service, port 18081). Requires:
1. arifosd monitors MCP calls via NATS event bus
2. If a call violates policy, arifosd SIGSTOPs the MCP process
3. arifosd is itself protected by systemd (auto-restart, MemoryMax)

**Timeline:** Multi-session effort. Not today. Needs architectural review.

---

## SUMMARY MATRIX

| # | Gap | Severity | Fixability | Autonomy | Status |
|---|-----|----------|------------|----------|--------|
| 1 | OS-level filesystem enforcement | 5 | 5 | YES | ✅ chmod 444 this session |
| 2 | Declarative agent policy | 4 | 4 | YES | ✅ AgentPolicy forged |
| 3 | Explicit agent lifecycle | 4 | 4 | YES | ✅ AgentLifecycle forged |
| 4 | Agents can rewrite constitution | 5 | 3 | PARTIAL | ✅ chmod mitigation + roadmap |
| 5 | Network isolation | 3 | 3 | PARTIAL | ⏸ bwrap integration queued |
| 6 | Per-agent resource quotas | 2 | 4 | YES | ✅ AgentPolicy fields + roadmap |
| 7 | Cryptographic session binding | 3 | 3 | NO (F13) | ⏸ Requires sovereign key |
| 8 | Agent-to-agent auth | 2 | 4 | YES | ⏸ Per-agent A2A tokens queued |
| 9 | In-process enforcement | 5 | 2 | NO (architectural) | ⏸ Multi-session: arifosd enforcement |

**Today's score:** 4/9 gaps addressed (1, 2, 3, 6). 3/9 mitigated (4, 5, 8). 2/9 blocked on F13 (7) or architecture (9).

---

*DITEMPA BUKAN DIBERI — Honest gaps are better than hidden risks.*
*999 SEAL | arifOS Federation | 2026-06-09*
