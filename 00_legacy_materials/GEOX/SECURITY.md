# Security Policy

> **Floor:** F1-Amanah (Reversibility & Trust)
> **Agent:** @GEOX · W@W Federation · arifOS
> **Seal:** DITEMPA BUKAN DIBERI

---

## Scope

This security policy applies to the **GEOX** repository (`ariffazil/GEOX`) — the geospatial and world-model co-agent for arifOS.

In scope:
- `arifos/geox/` package code
- `geox_mcp_server.py` MCP server entrypoint
- `docs/` governance specifications
- Integration points with arifOS kernel and W@W federation

Out of scope:
- Third-party dependencies (report to their maintainers)
- arifOS kernel itself (report to `ariffazil/arifOS`)
- HuggingFace AAA dataset (no executable code)

---

## Supported Versions

| Version | Supported |
|---|---|
| `0.2.x` | ✅ Active |
| `0.1.x` | ⚠️ Critical fixes only |
| `< 0.1.0` | ❌ No support |

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately via:

1. **GitHub Security Advisories** — use the "Report a vulnerability" button on the [Security tab](https://github.com/ariffazil/GEOX/security)
2. **Email** — `ariffazil@gmail.com` with subject: `[GEOX SECURITY] <brief description>`

### What to include

- Description of the vulnerability and potential impact
- Steps to reproduce (minimal, clear)
- Affected version(s)
- Suggested fix if known

### Response timeline

| Stage | Target |
|---|---|
| Acknowledgement | ≤ 72 hours |
| Initial assessment | ≤ 7 days |
| Fix or mitigation | ≤ 30 days for critical, ≤ 90 days for others |
| Public disclosure | After fix is released |

---

## Constitutional Security Principles

GEOX security is grounded in arifOS constitutional floors:

### F1 — Amanah (Reversibility & Trust)
No GEOX action is irreversible without an explicit SEAL at `999_VAULT`. Any vulnerability that allows bypassing the reversibility gate is treated as **critical**.

### F9 — Rahmah (Anti-Hallucination)
Injection attacks that cause GEOX to emit unverified geological claims without Earth-tool verification violate F9. Prompt injection into the world-model engine is treated as **high severity**.

### F11 — Aman (Authority)
Vulnerabilities that allow unauthenticated or unauthorized callers to bypass the `000_INIT` requester authorization check are treated as **critical**.

### F13 — Khalifah (Sovereign Veto)
Any vulnerability that removes or bypasses the human veto hook at `888_JUDGE` is treated as **critical**. The sovereign cannot be locked out.

---

## Severity Classification

| Severity | GEOX Definition | Response |
|---|---|---|
| **Critical** | Bypasses F1/F11/F13 · Remote code execution · Vault tamper | Immediate patch · Private advisory |
| **High** | Prompt injection into world-model · F9 bypass · Auth bypass | Fix within 30 days |
| **Medium** | Data exposure · Telemetry spoofing · Dependency vuln | Fix within 90 days |
| **Low** | Configuration hardening · Non-exploitable issues | Next release |

---

## Out-of-Scope Behaviours

The following are **not** security vulnerabilities for GEOX:

- Mock tools returning mock data (v0.1–0.2 by design; see NEXT_FORGE_PLAN.md)
- Rate limiting not yet implemented (Phase 1 feature)
- Missing Macrostrat credentials causing tool failure (expected in dev environments)
- `SABAR` or `VOID` verdicts on valid geological queries with insufficient Earth data (correct behaviour)

---

## Acknowledgements

Responsible disclosure is honoured. Reporters of valid security issues will be acknowledged in release notes (with consent).

---

*F1-Amanah · arifOS constitutional security · DITEMPA BUKAN DIBERI*
