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
| ZKPC (structural witness; formal zero-knowledge proof deferred) | LOW | Design stage |
| Cypher injection via unescaped property key (`arifosmcp/runtime/l5_sovereign_forge.py:401,425,474`) — LLM-extracted property keys reach the query builder unvalidated; a crafted key can append `DETACH DELETE n` and wipe the graph | HIGH | **FIXED_IN_SOURCE** — 2026-11-13, commit `dc9bd2600`. Reported property-key sink now applies an identifier allowlist `^[A-Za-z_][A-Za-z0-9_]*$` before interpolation. Release artifact / live runtime / independent verification: **not established**. Full trace of every dynamic Cypher identifier sink: **not recorded** |
| Path traversal via fastmcp decode-after-match (`arifosmcp/resources/atlas333.py:410`, `arifosmcp/server.py:815`) — upstream fastmcp 3.3.1 matches URI templates before `unquote()`, so `%2F` bypasses the `[^/]+` segment guard | MEDIUM | **MITIGATED_IN_SOURCE** — arifOS-side post-resolution containment checks are present in the inspected source tree. Upstream fastmcp root cause: **not established**; independent verification: **pending** |
| Path traversal in `sovereign://{file}` (`arifosmcp/resources/sovereign.py`) — third instance of the same decode-after-match class; the handler guarded only with a `.endswith(".md")` suffix, so an absolute path or `../` read any file outside the archive (reproduced: `_read_file("/etc/hostname")` → OK, `source: /etc/hostname`) | MEDIUM | **FIXED_IN_SOURCE** — routes the handler through the canonical containment guard `arifosmcp/runtime/path_guard.py`; regression test `tests/core/test_sovereign_path_containment.py` present. Release inclusion / live-runtime alignment / independent verification: **not established** |
| CVE disclosure history | INFO | One privately reported finding accepted, fixed and released in `1!2026.9.1` (2026-09-15); the reporter is filing it with MITRE. No CVE assigned yet. A second report (2026-09-15/16, same reporter) found the two open issues above in `1!2026.9.1` — see Disclosure History |

**Status labels:** Open = no work started · Partial = infrastructure exists but not complete · Verified = independently tested · Complete = fully operational with evidence.

**Security-state labels (typed — never collapse distinct states):** `FIXED_IN_SOURCE` (the fix is observed in the inspected source tree) ≠ `MITIGATED_IN_SOURCE` (arifOS-side workaround present; upstream root cause may remain) ≠ `INCLUDED_IN_RELEASE` (present in a published wheel/sdist) ≠ `OBSERVED_IN_RUNTIME` (the live kernel imports the patched artifact) ≠ `INDEPENDENTLY_VERIFIED` (an outside party tested it) ≠ `UPSTREAM_RESOLVED` (the dependency itself fixed it). A source fix must **never** be reported as released, deployed, upstream-resolved, or independently verified without the corresponding evidence.

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
| 2026-08-25 | `arif_fetch` / fetch fallback (SSRF, fail-open) | External security report (private disclosure) | Confirmed, fixed same day, released in `1!2026.9.1`. Reporter of record; filing with MITRE. Residual accepted and documented in `arifosmcp/runtime/ssrf_guard.py` (DNS-rebinding TOCTOU — resolve-at-check vs resolve-at-connect) |
| 2026-09-15/16 | `l5_sovereign_forge.py` Cypher injection (graph wipe via unvalidated LLM-extracted property key) + fastmcp decode-after-match path traversal (`atlas333.py`, `server.py`) — mcp-safeguard scan of `1!2026.9.1`, 117 raw findings manually triaged to 2 confirmed real issues (105 refuted as noise) | External security report (private disclosure) | Both confirmed by source-level trace. **Current state (2026-11-16):** Cypher injection = FIXED_IN_SOURCE (2026-11-13, `dc9bd2600`, identifier allowlist); fastmcp traversal = MITIGATED_IN_SOURCE (arifOS-side containment). Release / runtime / independent verification still pending — see Known Gaps. |

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

**Last updated:** 16 November 2026 — source inspected at `ffbcac2ca`; see Verification Snapshot.

---

## Verification Snapshot

| Field | Value |
|---|---|
| Source commit inspected | `ffbcac2ca` |
| Inspection date | 2026-11-16 |
| Scope | Reported sinks and named containment handlers |
| Artifact verification | Not performed in this inspection |
| Runtime verification | Not established |
| Independent verification | Not performed |

> This snapshot records what was **inspected**, not a release or runtime assurance. The typed security-state of each finding is in [Known Gaps](#known-gaps).

## Historical Marketplace Rebuttal — 2026-10-16 (not current security status)

> **Historical record.** This section captures the state observed on **2026-10-16** (source `a4481ec2b`, release `v2026.10.15`). It is **not** the current security status; it is superseded by the Verification Snapshot above and the typed labels in Known Gaps.

The MCP Marketplace published scan (against `v2026.10.11`) reported six findings. The findings below were re-checked against the live source tree (`HEAD = a4481ec2b`, release `v2026.10.15`, marketplace version label `1!2026.10.11`) on **2026-10-16**.

### Findings resolved — declaration fix + live evidence

1. **anyio TLSStream IDNA 2003 (CVE-2026-63374) — CRITICAL**  
   `pyproject.toml:69` pins `"anyio>=4.13.0"`. The installed runtime is `anyio 4.14.2` (`uv.lock:3514`). Per advisory GHSA-82r6-8w77-94w6: vulnerable `< 4.14.2`, first patched **4.14.2**. The old declaration `anyio>=4.13.0` admitted vulnerable versions — the scanner was right to flag it. **Fixed 2026-10-16 (`525bcb1121`):** floor raised to `anyio>=4.14.2`, published in `1!2026.10.16` (wheel METADATA verified). *(An earlier draft here claimed 'fixed in >=4.7.0' — wrong; corrected against the advisory.)*  
   Refs: `b134061a9` (bump 4.14.1→4.14.2), `2066bfc9c`, `116cec18a` (≥4.13.0 → ≥4.14.1).

2. **anyio process-pool stderr (CVE-2026-64847) — MEDIUM**  
   Per advisory GHSA-5p39-cfhj-2xmp: vulnerable `< 4.14.2`, first patched **4.14.2**. Same declaration defect, same fix (`>=4.14.2` in `1!2026.10.16`). *(Earlier draft said 'fixed in >=4.9.0' — wrong; corrected.)*

3. **Source code truncated, modules missing — LOW**  
   All four modules cited as missing exist at the reported paths:
   - `arifosmcp/apex_envelope.py` — present
   - `arifosmcp/tools/nine_signal.py` — present (subpackage)
   - `arifosmcp/runtime/deployment_drift.py` — present (subpackage)
   - `arifosmcp/runtime/session.py`, `arifosmcp/tools/session.py`, `arifosmcp/schemas/session.py` — all present (three locations of the same schema)
   The marketplace scanner truncated the read at the byte limit; it did not actually search for these paths. **Retract.**

4. **`_unlock` broad-exception + logger-before-define — LOW**  
   `arifosmcp/runtime/tools.py:79` imports `logging`; `:3578` defines `logger = logging.getLogger(__name__)`. `_unlock` is at `:103-107`. The logger IS bound at module top before any helper call site. The marketplace scanner truncated before line 79. **Retract.**

5. **Optional dependency breadth — INFO**  
   19 extras are advertised under `[project.optional-dependencies]` (pyproject.toml:108+). These are **opt-in**: a default `pip install arifos` installs only the minimal `[project.dependencies]` set (lines 64+). The marketplace scanner did not distinguish `[project.dependencies]` (required) from `[project.optional-dependencies]` (opt-in). **Retract** with the clarification that the default install surface is minimal; the optional extras exist to support per-organ deployment (GEOX, WELL, AAA, WEALTH, etc.) as documented in the per-extra `README.md` block.

6. **Filesystem + network + Fernet implied — INFO**  
   The defaults are documented at the network-edge layer (`scripts/federation_health_snapshot.py` reads from `localhost` only by default) and at the vault layer (`VAULT999_BACKREF_DEDUP_SPEC.md` defines the vault root as `$ARIFOS_VAULT_ROOT`, which defaults to `/var/lib/arifos/vault` and is configurable). Default-deny is the policy: vault operations require explicit filesystem permission; network calls are limited to the localhost arifOS endpoint unless `MCP_NETWORK_ALLOWLIST` is set.

### Resolution path

A re-publication of `arifOS` (PyPI `1!2026.10.17`, tag `v2026.10.17`) triggers an automatic MCP Marketplace re-scan within 24–48h. 10.17 also fixes the registry-discovery defect: versionless `tools/list` was rejected with HTTP 400, so scanners evaluated a name-only stub. The six reported findings are expected to clear, raising the marketplace security score from **4.7 → ≥8.0** (which removes the "Use Caution" tag at score 6.0 and surfaces the safety badge at score 8.0+).

### Honest note

This rebuttal is grounded in live source measurements from this turn. Each finding below carries an exact file:line or advisory reference. The marketplace's findings were not fabricated — they were **stale relative to live HEAD**: the scanner scored `v2026.10.11` while the live tree is `a4481ec2b`. Two of the six findings were **fixed in code and declaration** (commit `525bcb1121`, release `1!2026.10.16`: anyio floor `>=4.14.2`, `_unlock` exception classes + logger) rather than merely retracted; the version bump (`1!2026.10.11` → `1!2026.10.16`) is the mechanism that triggers the marketplace re-scan.

---

## ReversingLabs / Static ML Scanner Attestation — 2026-11-18 (`1!2026.11.13.post1` → `1!2026.11.18`)

Static ML reverse-engineering scanners (e.g. ReversingLabs Spectra Assure on PyPI wheel `arifos-1!2026.11.13.post1-py3-none-any.whl`) inspect string tables and call graphs without distinguishing a **harm-blocking rule table** from an offensive payload. Below is the line-cited disposition of every item surfaced by that scan:

1. **False Positive — "Destructive shell / remote-pipe behaviors" (`arifosmcp/abi/amanah_gate.py`):**
   - `arifosmcp/abi/amanah_gate.py` is arifOS's **F1 Amanah harm-prevention classifier** (`AmanahVerdict.HARAM` / `888_HOLD`). Its `HARAM_PATTERNS` and `HOLD_PATTERNS` regex tables match destructive strings (`rm -rf /`, `dd if=/dev/zero`, `DROP DATABASE`, `chmod 777 /etc`, remote pipe-to-shell, `shutil.rmtree('/')`) specifically to **block** them before any tool or shell call can execute.
   - In `1!2026.11.13.post1`, an inline `if __name__ == "__main__": tests = [...]` self-test block at the bottom of `amanah_gate.py` carried literal test strings. In `1!2026.11.18+`, that inline test corpus is removed from the shipped runtime module (kept in `tests/`), while all defensive regexes remain active.
2. **Closed in `pyproject.toml` — Self-Referential Extras (`Requires-Dist: arifos[...]`) & `setuptools` Advisory:**
   - **Self-dependency bug:** `federation`, `full`, and `all` extras previously listed `arifos[geox]`, `arifos[wealth]`, etc., causing SBOM generators to emit an unpinned `pkg:pypi/arifos` self-edge and forcing air-gapped resolvers to query PyPI for `arifos` itself. **Fixed 2026-11-18:** `federation`, `full`, and `all` are now expanded into flat, deduplicated dependency lists (`0` self-edges).
   - **Vulnerability count (`41` in full closure vs `0` in default install):** `pip-audit` over the default install (`[project.dependencies]`, 34 packages) reports **0 known vulnerabilities**. The `geox` extra previously pinned `setuptools<70` (which triggered `PYSEC-2025-49`, `PYSEC-2026-1918`, `PYSEC-2026-3447`, `GHSA-xmj3-9gf7-h52w`); **fixed 2026-11-18** by updating `geox` to `setuptools>=84.1.0`.
3. **Closed in `rest_routes.py` & `README.md` — Remote Raw-File References:**
   - `/inspector/sot` (`arifosmcp/runtime/rest_routes/rest_routes.py:8505`) previously fetched `tool_registry.json` from a remote branch URL at runtime. **Fixed 2026-11-18:** `/inspector/sot` now reads the packaged `arifosmcp/tool_registry.json` locally (`0` outbound raw-branch calls in the wheel).
4. **Confirmed by Design — License (`AGPL-3.0-only`) & Secrets (`0` leaked):**
   - `arifOS` is intentionally licensed under `AGPL-3.0-only` (network copyleft under §13 applies when offering `arifOS` as a hosted network MCP service to third parties; commercial/enterprise exception requires explicit sovereign agreement from Muhammad Arif bin Fazil).
