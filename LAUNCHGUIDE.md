# ArifOS MCP Server

> Listing metadata for MCP Marketplace scans. All facts below are probe-verified
> (2026-10-16) and generated from the same truth as the README. If this file and the
> marketplace listing disagree, this file is newer.

## Tagline
Constitutional AI kernel that governs AI agent actions before execution. 8 MCP tools, 666 JUDGE verdict pipeline, VAULT999 ledger.

## Description
arifOS is a model-independent authority plane for AI agents. When an agent proposes to write, delete, deploy, or spend, arifOS evaluates the proposal against 13 constitutional floors (F1–F13) and returns a governed verdict — SEAL, HOLD, SABAR, PARTIAL, PROVISIONAL, HOLD_888, or VOID — before execution occurs. Consequential verdicts are written to VAULT999, an append-only hash-chained audit ledger. The judge never executes; the executor never certifies. Proposer ≠ Judge ≠ Executor ≠ Witness. Human sovereignty stays above machine authority.

Public surface: 8 canonical MCP verbs (arif_init, arif_observe, arif_think, arif_route, arif_memory, arif_judge, arif_forge, arif_seal) over Streamable HTTP. Verdict evaluation is deterministic where the constitution is decidable (`gate: hard_deterministic` — no LLM consulted for rejections).

## Setup Requirements
- No API key required for the public remote endpoint. Self-hosting: `pip install arifos` then `PORT=8088 arifos-mcp streamable-http`.

## Category
Developer Tools

## Features
- Constitutional verdicts before execution: SEAL / HOLD / SABAR / PARTIAL / PROVISIONAL / HOLD_888 / VOID
- Deterministic rejection — the judge refuses on the constitution, not on a model opinion
- 13 non-compensatory floors (F1 AMANAH … F13 SOVEREIGN); one floor failure propagates; no compensating score
- VAULT999 append-only hash-chained receipts (self-verifiable today; external anchoring not yet implemented — see SECURITY.md known gaps)
- Session binding with authority bands (OBSERVE_ONLY → LIMITED_MUTATE); unattested callers are never silently upgraded
- Machine-readable surfaces: tools.json schemas, llms.txt, CITATION.cff, generated current-state + badge feeds
- Honest known-gaps ledger published in README ("What Is Not Yet Proven")

## Getting Started
- "Evaluate this proposed action against the constitutional floors: delete the production audit table"
- "What is my authority band, and what evidence would upgrade it?"
- Tool: arif_judge — evaluate a proposal; returns verdict + failed floors + next_safe_action
- Tool: arif_init — bind a governed session (actor identity + authority band) before any judgment
- Tool: arif_seal — append a completed chain's receipt to VAULT999 (after a SEAL verdict)

## Tags
governance, constitutional-ai, ai-safety, mcp, verdict-engine, audit-ledger, agent-governance, policy-engine, vault, authority

## Documentation URL
https://github.com/ariffazil/arifOS

## Health Check URL
https://arifos.arif-fazil.com/health

## Version note (marketplace maintainers)
The listing description previously read "13 MCP tools, 888_JUDGE verdict pipeline". Both were stale mirror text: the public surface is **8** canonical tools (a 25-verb canonical superset exists with 13 hidden verbs — likely the source of "13"), and the judge stage is **666** (the 888 judge label was retired 2026-07-31; `888_HOLD` survives only as the sovereign-escalation verdict). Release `1!2026.10.16` also raises the anyio floor to `>=4.14.2`, resolving CVE-2026-63374 and CVE-2026-64847 at the declaration level (GHSA-82r6-8w77-94w6, GHSA-5p39-cfhj-2xmp).
