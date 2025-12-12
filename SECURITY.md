# arifOS Security Policy

**Version:** v38.0.0 | **Last Updated:** 2025-12-13
**Runtime Law:** v35Omega | **Measurement:** v38 | **Memory/EUREKA:** v38Omega | **License:** AGPL-3.0

---

If you discover a security vulnerability in arifOS, thank you — please report it responsibly and confidentially.

**Preferred reporting channels (in order):**
1. **GitHub Security Advisory** (recommended) — open a private security advisory in this repository.
2. **Encrypted email** to the security contact below (PGP).
3. If neither is possible, email: arifbfazil@gmail.com

**Do NOT** post PoCs or exploit details publicly before a coordinated fix is available.

---

## How to Report

Please include:
1. A short title and affected component (e.g., `Memory Write Policy: VOID band bypass`).
2. Affected version(s) or commit SHA.
3. Minimal proof-of-concept or reproduction steps.
4. Impact assessment (what an attacker could do).
5. Suggested mitigation/patch (if available).
6. Contact details (optional) for follow-up.

If sending sensitive PoCs by email, encrypt them using the project PGP key (publish the fingerprint in the repo). If using GitHub Security Advisory, attach the PoC privately.

**Governance-Aware Reporting:** If your finding relates to **constitutional law** (canon/ files) or **Memory Stack v38Omega**, mention this explicitly so it can be routed through Phoenix-72 governance.

**Out-of-scope / Do not:**
- Do not test on production systems without explicit permission.
- Do not publicly disclose the vulnerability until a coordinated disclosure is arranged.
- Do not include large amounts of personal data unless requested.

---

## Contact & Encryption

**Primary security contact (confidential reports):** arifbfazil@gmail.com

**PGP key fingerprint:** (publish project key fingerprint here — add to this file once available)

Preferred: use GitHub Security Advisories. If emailing encrypted reports, include your public key or request a one-time secure channel.

---

## Response Commitments & Severity Handling

### Severity Levels

| Severity | Definition | arifOS-Specific Examples | Response |
|----------|------------|--------------------------|----------|
| **Critical** | Remote code execution, private key compromise, systemic compromise | Ability to forge/delete Cooling Ledger or Memory Ledger entries without detection; Bypass of VOID isolation (VOID entries reaching LEDGER/ACTIVE); AI self-sealing canon/amendments without human approval; Downgrade/disable constitutional floors without canon/spec change | Acknowledge: 24h; Patch: 7 days |
| **High** | Privilege escalation, significant bypass | Systematic bypass of APEX PRIME/Amanah lock via config/API; Breaking hash-chain or disabling verification; Disabling or raising recall confidence ceiling beyond 0.85; Bypass of Memory Write Policy invariants | Acknowledge: 24-48h; Fix: 14 days |
| **Medium** | Information exposure, non-critical DoS | Single-session DoS on governance pipeline (e.g., repeated SABAR loops) without long-term data compromise; Partial floor bypass in edge cases | Acknowledge: 48h; Fix: next minor release |
| **Low** | UI issues, minor bugs | Minor logging issues, cosmetic problems | Acknowledge: 5 business days |

### Responsible-Disclosure Timeline

1. Acknowledge within 24 hours (advisory reference number).
2. Preliminary triage & action plan within 3 days.
3. Fix or mitigation for high severity within 14 days (or a concrete timeline).
4. Public advisory within 30 days (unless extended coordination required).

---

## Scope

### In-Scope

We consider issues affecting:

- **arifOS core runtime** (`arifos_core/`):
  - `arifos_core/APEX_PRIME.py` (verdict engine)
  - `arifos_core/memory/*` (EUREKA, bands, audit, retention)
  - `arifos_core/integration/memory_*.py` (pipeline-memory integration)
  - `arifos_core/waw/*` and `arifos_core/eye/*` (governance organs)
  - `arifos_core/zkpc_runtime.py` (zkPC runtime)
  - `arifos_core/floor_detectors/` (Python-sovereign enforcement)

- **Cooling Ledger** and **Vault-999** implementations.

- **Memory Stack v38Omega** files and 6 Memory Bands.

- **APEX PRIME**, guardrails, and constitutional enforcement logic.

- **Repository deployment scripts** and **CI/CD definitions**.

- **Canon files** (`canon/`) that define constitutional law.

### Exclusions

- Third-party libraries (report to vendor and optionally to us).
- Misconfiguration of a private deployment not caused by upstream code.
- Downstream forks that diverge from canonical canon/spec without upstream involvement.

---

## The 9 Constitutional Floors (Security Invariants)

arifOS enforces **9 constitutional floors** as runtime invariants. Any bypass or systemic disablement of these floor checks in code, config, or runtime wiring should be treated as at least **HIGH** severity. If it enables persistent violation of F1/F2/F6/F9, treat as **CRITICAL**.

| # | Floor | Metric | Threshold | Type | Security Impact |
|---|-------|--------|-----------|------|-----------------|
| **F1** | Amanah (Integrity) | Reversibility lock | LOCK | Hard | Prevents irreversible harm; bypass = CRITICAL |
| **F2** | Truth | Factual accuracy | >= 0.99 | Hard | Prevents hallucination; bypass = CRITICAL |
| **F3** | Tri-Witness | Human+AI+Earth consensus | >= 0.95 | Hard | Ensures auditability |
| **F4** | DeltaS (Clarity) | Entropy change | >= 0 | Hard | Prevents obfuscation |
| **F5** | Peace-squared | Tone safety | >= 1.0 | Soft | Prevents toxicity |
| **F6** | kappa-r (Empathy) | Reciprocity | >= 0.95 | Soft | Protects vulnerable; bypass = HIGH |
| **F7** | Omega-0 (Humility) | Confidence bounds | 0.03-0.05 | Hard | Prevents overconfidence |
| **F8** | G (Genius) | Governed intelligence | >= 0.80 | Derived | Measures governance health |
| **F9** | C_dark | Dark cleverness | < 0.30 | Derived | Ungoverned risk; bypass = CRITICAL |

**Hard floor fail = VOID (stop). Soft floor fail = PARTIAL (warn).**

**Python-Sovereign Enforcement:** Floors F1 (Amanah) and F9 (Anti-Hantu) are enforced by `arifos_core/floor_detectors/` — code overrides LLM self-assessment. These are the most critical security boundaries.

---

## Memory & EUREKA Security (v38)

v38 introduces the **Memory Write Policy Engine** with 4 core invariants that are security-critical:

### The 4 Core Invariants

| # | Invariant | Enforcement | Security Severity if Bypassed |
|---|-----------|-------------|-------------------------------|
| **INV-1** | VOID verdicts NEVER become canonical memory | `MemoryWritePolicy.should_write()` gates all writes | **CRITICAL** — bad decisions become precedent |
| **INV-2** | Authority boundary: humans seal law, AI proposes | `MemoryAuthorityCheck.authority_boundary_check()` | **CRITICAL** — AI self-modification of constitution |
| **INV-3** | Every write must be auditable (evidence chain) | `MemoryAuditLayer.record_write()` with hash-chain | **HIGH/CRITICAL** — undetectable tampering |
| **INV-4** | Recalled memory = suggestion, not fact | Confidence ceiling (0.85) on all recalls | **HIGH** — memory becomes oracle |

### The 6 Memory Bands

| Band | Purpose | Retention | Security Notes |
|------|---------|-----------|----------------|
| **VAULT** | Read-only constitution (L0) | PERMANENT (COLD) | MUST be immutable; any write = CRITICAL |
| **LEDGER** | Hash-chained audit trail | 90 days (WARM) | Chain integrity critical; tampering = CRITICAL |
| **ACTIVE** | Volatile working state | 7 days (HOT) | Session-scoped; less sensitive |
| **PHOENIX** | Amendment proposals pending | 90 days (WARM) | Human approval required before seal |
| **WITNESS** | Soft evidence, scars | 90 days (WARM) | Diagnostic; lower sensitivity |
| **VOID** | Diagnostic only, NEVER canonical | 90 days (auto-delete) | MUST stay isolated; leakage = CRITICAL |

### Verdict to Band Routing (Security-Critical)

```text
SEAL    -> LEDGER + ACTIVE (canonical memory + session state)
SABAR   -> LEDGER + ACTIVE (canonical with failure reason logged)
PARTIAL -> PHOENIX + LEDGER (pending Phoenix-72 review)
VOID    -> VOID only (NEVER canonical - diagnostic retention)
888_HOLD -> LEDGER (logged, awaiting human approval)
```

**Critical Security Rule:** VOID entries MUST NEVER route to LEDGER, ACTIVE, or any canonical band. Any code path that allows this is a **CRITICAL** vulnerability.

---

## Cryptography & Key Management

### Hashing

- **Cooling Ledger & Memory Audit:** SHA-256 (current default) with deterministic (canonical) serialization before hashing.
- **Future:** SHA3-256 MAY be introduced in future versions; if used, MUST be clearly declared in canon/spec and tests.
- **Amendment Policy:** Any change to hash algorithm or canonical serialization format of the ledger is a **Phoenix-72 amendment** topic, not a normal refactor.

### Key Management

- **Production signing keys:** KMS/HSM-backed (AWS KMS, Azure Key Vault, GCP KMS, or HSM).
- **Private keys MUST NOT** be committed nor stored in CI logs.
- **Local dev/testing:** use ephemeral keys clearly marked for development only.

### Recommended Production Setup

- Centralize key rotation with immutable rotation logs recorded in the ledger.
- Strict IAM and audit logging for key usage.

### AGPL-3.0 Compliance

Operators running arifOS as a network service MUST ensure that AGPL-3.0 source disclosure requirements are compatible with their threat model and deployment process.

---

## Key Compromise Procedure

If you suspect key compromise:

1. **Revoke** the key in KMS/HSM immediately and rotate to a new key.
2. **Notify** maintainers and create an incident ticket (we will acknowledge within 24 hours).
3. **Mark** affected seals as SUSPECT in ledger metadata; create a Vault-999 amendment record.
4. **Re-verify** or re-seal affected critical decisions with fresh APEX verdicts where feasible.
5. **Publish** a security advisory once scope & remediation are clear.

### Indicators of Compromise

- Unexpected signing activity.
- Missing or altered ledger entries.
- Alerts from KMS or IAM logs for anomalous access.
- Hash-chain verification failures.
- VOID band entries appearing in canonical bands.

---

## CI/CD & Automation

### Required Checks

We recommend/aim to run:

- **Dependabot** (or similar) for dependency alerts (weekly).
- **CodeQL / SAST** scanning for repository code.
- **Secrets scanning:** gitleaks / git-secrets in CI and pre-commit.
- **Automated tests:** unit tests, type checks (mypy), and linters on all PRs.

### Memory & Governance Tests (v38)

The following tests MUST run in CI:

```bash
# Memory tests
pytest tests/test_memory_policy.py -v
pytest tests/test_memory_bands.py -v

# Memory-floor integration
pytest tests/integration/test_memory_floor_integration.py -v

# Hash-chain verification
arifos-verify-ledger
```

### Merge Policy

- All PRs must pass tests and type checks.
- Changes touching **APEX, Ledger, Vault, Memory, or guard modules** require code-owner review and at least one security reviewer.
- Changes to **canon/** files require Phoenix-72 governance review.

---

## Monitoring & Detection

In production, monitor:

- **Ledger verification failures** and mismatched hashes.
- **Memory audit verification failures** (hash-chain breaks).
- **Unusual signing patterns** or KMS key usage.
- **APEX override** or attempted bypass events.
- **Failed tri-witness gating** for high-stakes operations.
- **VOID band write counts** significantly deviating from historical baselines (possible probing / adversarial pressure on floors).
- **Recall confidence values** exceeding 0.85 ceiling.

Configure alerting to notify on-call engineers for critical events.

---

## Responsible Disclosure & Credit

We appreciate coordinated disclosure. Researchers who follow this policy will be credited in advisories or release notes unless they request anonymity.

**Recognition:** Major governance bugs that improve constitutional safety may be recognized in canon documentation (with researcher permission).

---

## References & Compliance

- **OWASP** secure coding practices — https://owasp.org/
- **NIST** Cybersecurity Framework — https://www.nist.gov/cyberframework
- **CWE/SANS** Top 25 — https://cwe.mitre.org/top25/
- **AGPL-3.0** License — https://www.gnu.org/licenses/agpl-3.0.html

---

## Key Files (Security-Critical)

```text
arifos_core/APEX_PRIME.py           - Verdict engine (CRITICAL)
arifos_core/floor_detectors/        - Python-sovereign enforcement (CRITICAL)
arifos_core/memory/policy.py        - Memory Write Policy Engine (CRITICAL)
arifos_core/memory/bands.py         - 6 Memory Bands + router (CRITICAL)
arifos_core/memory/authority.py     - Human seal enforcement (CRITICAL)
arifos_core/memory/audit.py         - Hash-chain audit layer (CRITICAL)
arifos_core/memory/retention.py     - Hot/Warm/Cold/Void lifecycle
arifos_core/integration/            - Pipeline <-> Memory integration
canon/                              - Constitutional law (Phoenix-72 governed)
```

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.

**Version:** v38.0.0 | **Status:** PRODUCTION | **Safety Ceiling:** 97%
