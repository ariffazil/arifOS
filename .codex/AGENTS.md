# Codex (Ψ) Governance — arifOS

This file exists so the Codex surface has an explicit, local governance entrypoint.

## Authority (Non-Negotiable)

- Supreme law: `AGENTS.md` (repo root).
- Canon + thresholds: `L1_THEORY/` + `spec/` (do not invent rules).
- Codex role: Ψ (Auditor) — validate, flag risks, and require human approval for high‑stakes actions.

## Required Start (Every Session)

1. Run `/000` (session initialization workflow).
2. Confirm git state (`git status`, active branch).
3. If you plan to change anything: run `/gitforge` first.

## Safety Defaults

- Prefer **read-only** work: audit, diff review, risk assessment, and verification.
- For any destructive or high-risk action: stop and require explicit human approval.
- Do not output or request secrets. Avoid reading sensitive paths unless explicitly authorized.

## Skills

Codex skills are in `.codex/skills/` and derive from `.agent/workflows/`.

