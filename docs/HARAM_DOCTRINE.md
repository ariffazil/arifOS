# HARAM_DOCTRINE — arifOS Constitutional Rejects

> **Version:** 1.0
> **Forged:** 2026-06-13
> **Authority:** F13 SOVEREIGN (canon is sovereign-ratified)
> **Seal type for additions/removals:** `INTEGRATION_FORGE_DISTILL_MXC_DS_BH_HARAM_<seq>`
> **Source brief:** `distill-mxc-ds-bh-2026-06-13` §2.3, decision ADRs 002/003/004/005/009
> **Reversibility:** this file is **read-only canon**. Adding or removing a HARAM entry is F13 territory.

---

## What is HARAM?

In the 5-tier Fiqh moral-grammar surface (WAJIB · SUNAT · HARUS · MAKRUH · HARAM),
**HARAM** is the explicit "must reject" tier. A pattern lands here when its
adoption would violate one or more F1–F13 floors. Unlike WAJIB (must absorb) and
SUNAT (absorb if cheap), HARAM entries are **negative canon** — they exist so
future agents and humans do not re-litigate the decision.

The 5-tier Fiqh is the moral-grammar surface. The 5 rejects below are the
**load-bearing examples** as of 2026-06-13. The pattern that produced each is
the thing we are rejecting, not the specific tool or repo that surfaced it.

---

## The 5 Rejects (H1–H5)

### H1 — `--experimental` global flag for new backends/tools

- **Source:** MXC CLI / SDK pattern (the "Microsoft Insiders" model)
- **Why haram:** arifOS's canonical 13-tool surface is the **constitutional contract**
  (see `arifosmcp/constitutional_map.py::CANONICAL_TOOLS`). The PHOENIX-72
  absorption pattern forbids adding a 14th tool. A global `--experimental`
  flag is a backdoor to that rule — it smuggles new surfaces past the floor
  system by labeling them "experimental" instead of "new."
- **F-floor violation:** F1 AMANAH (irreversible surface growth), F4 CLARITY
  (the surface stops being a single readable list).
- **arifOS position:** A new MCP tool either is in the canonical 13, or it
  does not exist. New capabilities live on existing tools as a new `mode`,
  or in A-FORGE (the execution arm). No flag, no carve-out.

### H2 — "Skills are written by the harness, not by you" (agent self-authors canon)

- **Source:** browser-harness `README.md:61`
- **Why haram:** F11 AUTH + F12 INJECTION failure mode. If the agent writes
  its own canon, you have memory poisoning + agent self-authorisation. The
  F13 SOVEREIGN floor requires that constitutional surfaces are
  human-authored. The agent's job is to **enforce** canon, not **write** it.
- **F-floor violation:** F11 AUTH (no human authorship = no sovereign
  authority), F12 INJECTION (canon becomes a vector for memory poisoning).
- **arifOS position:** Helpers (skill implementations, mode dispatchers) may
  be agent-editable under the W3 negative-space contract. **Canon is
  sovereign-ratified.** Never the reverse. Adding to the canon is F13 work.

### H3 — YOLO mode (auto-approve all tools, lift workspace boundary)

- **Source:** DeepSeek TUI `deepseek-tui.md:49`
- **Why haram:** Constitutional exit wound. Auto-approving all tools and
  lifting the workspace boundary in a single toggle violates F13 SOVEREIGN
  (the human veto becomes a footnote) and F1 AMANAH (every action becomes
  effectively irreversible because the floor is off). The Plan/Agent triad
  that some harnesses pair with YOLO is fine — it is just UX over the
  existing floor system. The YOLO slot itself is haram.
- **F-floor violation:** F13 SOVEREIGN (veto bypassed), F1 AMANAH (floor
  bypassed), F5 PEACE (no de-escalation surface).
- **arifOS position:** The 5-tier Fiqh (WAJIB/SUNAT/HARUS/MAKRUH/HARAM) is
  the moral-grammar surface. There is no auto-approve mode. There is no
  "skip the floors" mode. There is no Plan/Agent triad that exempts a tool
  call from the F1–F13 envelope.

### H4 — Backward-compat via deprecation aliases

- **Source:** MXC SDK pattern (`appcontainer` → `processcontainer` rename)
- **Why haram:** Aliases accumulate technical debt forever. The
  `appcontainer` name lives in old configs, old tests, old docs, old
  institutional memory — and the alias is the only thing keeping it
  working. arifOS's deprecation story is **git revert + version-bump seal**,
  not parser aliases. The constitution is versioned, not aliased.
- **F-floor violation:** F1 AMANAH (a parser alias is an irreversible
  commitment to keep both names working), F4 CLARITY (the schema stops
  being a single readable list — there are now two names for the same
  thing).
- **arifOS position:** F11 seal **is** the deprecation signal. A
  `vault_seal` with `seal_type=DEPRECATION_<seq>` is the public record
  that a name has been retired. There are no parser aliases. There is no
  "for backward compatibility" comment in any parser.

### H5 — "Don't write secrets" as a courtesy (community-PR skill model)

- **Source:** browser-harness `SKILL.md:122`, `README.md:62` (the open-source
  "PRs welcome" model)
- **Why haram:** F11 AUTH is **cryptographic**, not courteous. "Don't write
  secrets" as a guideline is a different threat model than "secrets can
  never enter any memory tier because the kernel refuses them at the L1
  boundary." The community-PR skill model compounds the problem: a
  public-corpus skill is one PR away from leaking an operator's
  institutional knowledge into a public registry.
- **F-floor violation:** F11 AUTH (the secret never enters the kernel in
  the first place — not a courtesy, a property), F2 TRUTH (a public
  corpus cannot be the source of truth for a sovereign operator).
- **arifOS position:** SOPS + AGE + ED25519 + per-IPC token (W9 / S3). Every
  cross-organ call into a sovereign-isolated surface (`vault999-writer`,
  `supabase-writer`, `arifOS MCP`) requires a per-session token, action-
  scoped, TTL-bounded. **Skills cross into the federation via
  sovereign-ratified merge, not via community PR.**

---

## How to add or remove a HARAM entry

**Both directions are F13 territory.** The procedure is:

1. Surface the pattern in an ADR with `Status: PROPOSED` and the floor(s)
   it would violate.
2. Reference the source eureka (file:line).
3. State the arifOS alternative — what we do instead.
4. Submit to `arif_judge_deliberate` for SEAL. Without 888, the entry
   does not exist.
5. On SEAL, append a new section to this file (H6, H7, ...) and write a
   `vault_seal` line with `seal_type=INTEGRATION_FORGE_DISTILL_MXC_DS_BH_HARAM_<seq>`.
6. **Do not** modify an existing entry silently. The history of why a
   pattern was rejected is part of the canon. If the rejection is wrong,
   the entry is superseded, not edited.

## Why negative canon matters

Most codebases have a "what we do" document. Few have a "what we
explicitly do not do" document. The HARAM list is the immune system of
the constitution: when a new agent or human proposes a pattern, the
first question is *"is this on the HARAM list?"* If yes, the proposal
needs an F13 override, not a re-debate.

The 5 rejects here are not permanent. They are the **load-bearing
examples** as of 2026-06-13. New rejects are added by F13. Old rejects
are removed by F13. The list grows when the federation encounters a
new pattern that would break the floor system; the list shrinks when
the floor system itself changes.

---

*DITEMPA BUKAN DIBERI — The rejects are forged, not given. To remove one, F13.*
