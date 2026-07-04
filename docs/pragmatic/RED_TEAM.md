# Red Team Process — Adversarial Design Review

> **Blindspot #9 response.** One agent builds. We need three other mindsets to test it.
> Updated: 2026-06-30 by FORGE (000Ω).

## The Four-Agent Adversarial Review

For every release (or major change), run 4 agents with opposing instructions:

| Agent | Role | Instruction |
|---|---|---|
| **BUILDER** | Build | Add the feature. Make it work. |
| **SIMPLIFIER** | Remove | Delete 30% of what the builder added. Keep value. |
| **BREAKER** | Attack | Find a way to bypass, exfiltrate, or silently fail. |
| **REMOVER** | Question necessity | Argue why the whole subsystem should be deleted. |

The BUILDER's answer is only accepted if SIMPLIFIER, BREAKER, and REMOVER all fail to defeat it.

## When to Run Red Team

| Trigger | Frequency |
|---|---|
| New tool added | Always |
| Constitutional floor changed | Always |
| Major refactor (>500 LOC changed) | Always |
| Routine release | Weekly |
| Public-facing documentation update | Always |

## The RED_TEAM Template

Every red-team session produces:

### `red_team_YYYY-MM-DD_<topic>.md`

```markdown
# Red Team: <topic>

## Builder's Proposal
(Summarize what was built)

## Simplifier's Cuts
| Component | Builder's justification | Simplifier's counter | Verdict |
|---|---|---|---|
| <file> | "needed for X" | "X works without it because Y" | KEEP / CUT |

## Breaker's Attacks
| Attack vector | Defense | Bypass found? |
|---|---|---|
| <vector> | <defense> | YES (describe) / NO |

## Remover's Case
Argument for deleting the whole subsystem:
(Summarize)

Builder's rebuttal:
(Summarize)

## Final Verdict
- Components to keep: N
- Components to cut: M
- Attacks patched: X
- Attacks still open: Y
- Whole subsystem deleted? YES / NO

## Action Items
- [ ] ...
```

## Historical Red Teams (to start the practice)

### Candidate Red Team #1 — "The MCP Policy Gate"

**Builder's proposal:** 5-layer policy gate with 68 wrapped tools.
**Simplifier's counter:**
- Delete forge_policy_list (users can read the config file)
- Delete regex constraints on L4 (too brittle; simple allowlist enough)
- Delete interceptor wrapping (pre-flight check enough)
**Breaker's attack:**
- Actor ID spoofing in stdio transport → **OPEN** (no auth in stdio)
- Regex ReDoS on malicious input → **OPEN** (no regex validation)
- Stateful client can bypass stateless gate → **OPEN** (need to verify)
**Remover's case:**
- "Plain MCP with tool-level deny-list is simpler"
- "Governance is the host's responsibility, not the server's"
**Verdict:** TBD in actual red team session.

### Candidate Red Team #2 — "Trinity Witness"

**Builder's proposal:** W3 = ∛(Human × AI × Earth) ≥ 0.75 for high-stakes actions.
**Simplifier's counter:**
- Drop the cube root — just average of three booleans
- Drop Earth witness — no measurement infrastructure exists
**Breaker's attack:**
- Always returns 0.5 because Earth witness defaults to 0.5 → no signal
**Remover's case:**
- "Just use arif_judge with human acknowledgment"
- "Trinity adds complexity without changing outcomes"
**Verdict:** **LIKELY DELETE** unless evidence measurement is implemented.

## Tooling

### Run a red team (CLI)

```bash
# Each agent runs in separate context window, no shared memory
cd /root/A-FORGE && \
  opencode --agent=builder "red team the MCP policy gate" && \
  opencode --agent=simplifier "delete 30% of what builder proposed" && \
  opencode --agent=breaker "bypass the policy gate" && \
  opencode --agent=remover "argue why policy gate should be deleted"
```

### Log every red team

```bash
mkdir -p /root/arifOS/docs/red_teams/
# Move the output there tagged by date and topic
```

## Why This Works

Single coding agents have one bias: **they always add**. They optimize for:
- Abstraction
- Architecture
- Elegance
- Completeness

They don't optimize for:
- Maintainability
- Debugging
- Operational simplicity
- Code deletion

**Four opposing agents cancel out single-agent bias.**

## Anti-Patterns

- ❌ Single-person review of agent output (human can't catch architectural bias)
- ❌ Review only after building (catch it during planning)
- ❌ Letting the builder defend against itself (circular reasoning)
- ❌ Red team on trivial changes (overhead outweighs benefit)

---

**DITEMPA BUKAN DIBERI** — truth survives attack, not assertion.
