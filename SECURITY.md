# Security — arifOS

## Maintainer

arifOS is maintained by one human, Muhammad Arif bin Fazil, who directs a federation of AI engineering agents. He designs and governs the system; the agents implement it and the commit author fields show it. See [Who Maintains This](./README.md#who-maintains-this).

Security reports: `arifbfazil@gmail.com`. No bug bounty. We do acknowledge reporters, we fix before we publish, and we tell you what we could not fix.

## Threat Model

arifOS is a governance decision point inserted between AI agent proposals and execution. Its security model addresses three primary threat classes:

### 1. Agent Bypass
**Threat:** An AI agent attempts to execute an action without passing through arifOS judgment.

**Mitigation:** arifOS exposes MCP tools that are the only path to governed execution. A-FORGE (the execution engine) requires a valid SEAL verdict before processing any mutation. The judge never executes; the executor never certifies.

**Status:** Architecturally enforced. Not independently penetration-tested.

### 2. Floor Evasion
**Threat:** A crafted proposal bypasses one or more constitutional floors (F1-F13).

**Mitigation:** All 13 floors are evaluated sequentially. A single floor failure produces VOID. Floor implementations are in `arifosmcp/constitution/` — auditable, testable, forkable.

**Status:** Self-tested. No adversarial bypass testing published.

### 3. Ledger Tampering
**Threat:** VAULT999 audit records are modified after creation.

**Mitigation:** VAULT999 is append-only JSONL with hash chaining. Records include previous record hash, creating a tamper-evident chain.

**Status:** Append-only enforced in code. Cryptographic integrity not independently verified. Zero-knowledge proof (ZKPC) is deferred.

---

## Known Gaps

| Gap | Severity | Status |
|-----|----------|--------|
| No independent penetration test | HIGH | In progress — one external researcher reviewing since 2026-08-25 (private disclosure; fix released in `1!2026.9.1`). No independent audit report published yet |
| SBOM — no CVE scan, no signing | HIGH | Partial — CycloneDX generator exists (`arifosmcp/arifos_sbom.py`; `sbom` job in `07-publish-pypi.yml` attaches SBOM to releases) |
| No signed releases | MEDIUM | Open |
| MCP conformance not independently certified | MEDIUM | Partial — CI workflow `06-mcp-conformance.yml` gates pushes to main and PRs touching the kernel surface; ABI drift guard passes |
| Request authentication/rate limiting not independently verified | HIGH | Partially addressed in internal audit |
| Development credentials may be present in dependencies | MEDIUM | Needs audit |
| Docker compose isolation not independently verified | MEDIUM | Needs audit |
| No reproducible build attestation | MEDIUM | Open |
| Observability — trace propagation fix in progress | MEDIUM | Partial — sovereign Postgres backend exists; arifFlow, FRAME, and Kabarkan live; trace propagation not yet complete |
| VAULT999 hash chain not independently verified | LOW | Open |
| ZKPC (zero-knowledge proof of constitution) deferred | LOW | Design stage |
| Cypher injection via unescaped property key (`arifosmcp/runtime/l5_sovereign_forge.py:401,425,474`) — LLM-extracted property keys reach the query builder unvalidated; a crafted key can append `DETACH DELETE n` and wipe the graph | HIGH | Open — fix is a key whitelist (`^[A-Za-z_][A-Za-z0-9_]*$`) before `_s(k)`, same pattern already used for edge labels |
| Path traversal via fastmcp decode-after-match (`arifosmcp/resources/atlas333.py:410`, `arifosmcp/server.py:815`) — upstream fastmcp 3.3.1 matches URI templates before `unquote()`, so `%2F` bypasses the `[^/]+` segment guard | MEDIUM | Open — fix is post-unquote path validation + containment check before filesystem access; root cause reported upstream to fastmcp |
| Path traversal in `sovereign://{file}` (`arifosmcp/resources/sovereign.py`) — third instance of the same decode-after-match class; the handler guarded only with a `.endswith(".md")` suffix, so an absolute path or `../` read any file outside the archive (reproduced: `_read_file("/etc/hostname")` → OK, `source: /etc/hostname`) | MEDIUM | Fixed in source 2026-09-22 — containment via `arifosmcp/runtime/path_guard.py` (single source of truth for the check); regression test `tests/core/test_sovereign_path_containment.py`. Not yet in a release |
| CVE disclosure history | INFO | One privately reported finding accepted, fixed and released in `1!2026.9.1` (2026-09-15); the reporter is filing it with MITRE. No CVE assigned yet. A second report (2026-09-15/16, same reporter) found the two open issues above in `1!2026.9.1` — see Disclosure History |

**Status labels:** Open = no work started · Partial = infrastructure exists but not complete · Verified = independently tested · Complete = fully operational with evidence.

## What Has Been Tested

- Internal code audit (April 2026) — identified gaps above
- Self-authored test suite — covers core judgment paths
- Live health endpoint — verifies floor status, deployment alignment
- Source-build-deploy alignment check — commit-level verification
- External private disclosure (2026-08-25) — a researcher traced the fetch surface by reading the code and reported a fail-open SSRF path without standing the substrate up. We reproduced it live rather than accept the reading alone, fixed it the same day (commits `285a956d8`, `e2759cf4b`, `22586943f`), and re-ran a blocked-target matrix against both the source tree and the published `1!2026.9.1` artifact — local, link-local (including the cloud metadata address), reserved, non-dotted IP notations, IPv4-mapped IPv6, and non-HTTP schemes all refused; public hosts still resolve

## What Has NOT Been Tested

- Adversarial prompt injection against floors
- MCP protocol fuzzing
- Supply chain dependency audit
- Third-party penetration test
- Enterprise deployment scenario testing
- Comparative benchmark against alternative governance frameworks

---

## Disclosure History

| Date | Surface | Reported by | Outcome |
|------|---------|-------------|---------|
| 2026-08-25 | `arif_fetch` / fetch fallback (SSRF, fail-open) | Syed Anas Mohiuddin (private report) | Confirmed, fixed same day, released in `1!2026.9.1`. Reporter of record; filing with MITRE. Residual accepted and documented in `arifosmcp/runtime/ssrf_guard.py` (DNS-rebinding TOCTOU — resolve-at-check vs resolve-at-connect) |
| 2026-09-15/16 | `l5_sovereign_forge.py` Cypher injection (graph wipe via unvalidated LLM-extracted property key) + fastmcp decode-after-match path traversal (`atlas333.py`, `server.py`) — mcp-safeguard scan of `1!2026.9.1`, 117 raw findings manually triaged to 2 confirmed real issues (105 refuted as noise) | Syed Anas Mohiuddin (private report) | Both confirmed by source-level trace. Cypher injection: HIGH, fix pending (key whitelist). Path traversal: MEDIUM, root cause is upstream fastmcp; arifOS-side mitigation (post-unquote validation) pending, upstream report pending |

---

## Disclosure Policy

If you discover a security vulnerability in arifOS:

1. **Do not** open a public GitHub issue
2. Email: arifbfazil@gmail.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
3. You will receive acknowledgment within 72 hours
4. A fix will be developed and released
5. Credit will be given in release notes (unless you prefer anonymity)

---

## Scope

**In scope:**
- arifOS kernel (arifosmcp/)
- MCP endpoint security
- VAULT999 ledger integrity
- Floor enforcement logic
- A-FORGE execution authorization

**Out of scope:**
- AI model behavior (arifOS does not run models)
- Network infrastructure (VPS, DNS, TLS)
- Third-party dependencies (report upstream)
- Social engineering attacks

---

## Security Contact

Muhammad Arif bin Fazil
arifbfazil@gmail.com

---

**Last updated:** 22 September 2026
