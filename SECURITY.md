# arifOS Security Policy

If you discover a security vulnerability in arifOS, thank you — please report it responsibly and confidentially.

Preferred reporting channels (in order)
1. GitHub Security Advisory (recommended) — open a private security advisory in this repository.
2. Encrypted email to the security contact below (PGP).
3. If neither is possible, email: arifbfazil@gmail.com

Do NOT post PoCs or exploit details publicly before a coordinated fix is available.

---

## How to report

Please include:
1. A short title and affected component (e.g., `Cooling Ledger: chain verification bypass`).
2. Affected version(s) or commit SHA.
3. Minimal proof-of-concept or reproduction steps.
4. Impact assessment (what an attacker could do).
5. Suggested mitigation/patch (if available).
6. Contact details (optional) for follow-up.

If sending sensitive PoCs by email, encrypt them using the project PGP key (publish the fingerprint in the repo). If using GitHub Security Advisory, attach the PoC privately.

Out-of-scope / Do not:
- Do not test on production systems without explicit permission.
- Do not publicly disclose the vulnerability until a coordinated disclosure is arranged.
- Do not include large amounts of personal data unless requested.

---

## Contact & encryption

Primary security contact (confidential reports): arifbfazil@gmail.com

PGP key fingerprint: (publish project key fingerprint here — add to this file once available)

Preferred: use GitHub Security Advisories. If emailing encrypted reports, include your public key or request a one-time secure channel.

---

## Response commitments & severity handling

Severity levels (guideline)
- Critical: remote code execution, private key compromise, ability to forge ledger entries, systemic compromise.
  - Acknowledge: within 24 hours.
  - Plan/mitigation: immediate; patch within 7 days (or published mitigation plan).
- High: privilege escalation, bypass of APEX/Amanah without key compromise.
  - Acknowledge: within 24–48 hours.
  - Fix/mitigation: within 14 days.
- Medium: information exposure, non-critical DoS.
  - Acknowledge: within 48 hours.
  - Fix: next minor release or designated patch window.
- Low: UI issues, minor bugs.
  - Acknowledge: within 5 business days.

Responsible-disclosure timeline:
1. Acknowledge within 24 hours (advisory reference number).
2. Preliminary triage & action plan within 3 days.
3. Fix or mitigation for high severity within 14 days (or a concrete timeline).
4. Public advisory within 30 days (unless extended coordination required).

---

## Scope

We consider issues affecting:
- arifOS core runtime and libraries (arifos_core).
- Cooling Ledger and Vault‑999 implementations.
- APEX PRIME, guardrails, and constitutional enforcement logic.
- Repository deployment scripts and CI/CD definitions.

Exclusions:
- Third-party libraries (report to vendor and optionally to us).
- Misconfiguration of a private deployment not caused by upstream code.

---

## Security practices & runtime invariants

arifOS enforces constitutional floors as runtime invariants where applicable:
- Truth ≥ 0.99
- ΔS ≥ 0
- Peace² ≥ 1.0
- κᵣ ≥ 0.95
- Ω₀ ∈ [0.03, 0.05]
- Amanah = LOCK
- RASA = TRUE
- Tri‑Witness ≥ 0.95

If you find bypasses or means to disable these invariants in code/config, report as HIGH severity.

---

## Cryptography & key management

- Cooling Ledger: deterministic (canonical) serialization before hashing.
- Hashing: SHA3‑256 recommended (or SHA‑256 in FIPS environments).
- Production signing keys: KMS/HSM-backed (AWS KMS, Azure Key Vault, GCP KMS, or HSM).
- Private keys MUST NOT be committed nor stored in CI logs.
- Local dev/testing: use ephemeral keys clearly marked for development only.

Recommended production setup:
- Centralize key rotation with immutable rotation logs recorded in the ledger.
- Strict IAM and audit logging for key usage.

---

## Key compromise procedure (high-level)

If you suspect key compromise:
1. Revoke the key in KMS/HSM immediately and rotate to a new key.
2. Notify maintainers and create an incident ticket (we will acknowledge within 24 hours).
3. Mark affected seals as SUSPECT in ledger metadata; create a Vault‑999 amendment record.
4. Re-verify or re-seal affected critical decisions with fresh APEX verdicts where feasible.
5. Publish a security advisory once scope & remediation are clear.

Indicators of compromise:
- Unexpected signing activity.
- Missing or altered ledger entries.
- Alerts from KMS or IAM logs for anomalous access.

---

## CI/CD & automation

We recommend/aim to run:
- Dependabot (or similar) for dependency alerts (weekly).
- CodeQL / SAST scanning for repository code.
- Secrets scanning: gitleaks / git-secrets in CI and pre-commit.
- Automated unit tests, type checks (mypy), and linters on all PRs.

Merge policy:
- All PRs must pass tests and type checks.
- Changes touching APEX, Ledger, Vault, or guard modules require code-owner review and at least one security reviewer.

---

## Monitoring & detection

In production monitor:
- Ledger verification failures and mismatched hashes.
- Unusual signing patterns or KMS key usage.
- APEX override or attempted bypass events.
- Failed tri-witness gating for high-stakes operations.

Configure alerting to notify on-call engineers for critical events.

---

## Responsible disclosure & credit

We appreciate coordinated disclosure. Researchers who follow this policy will be credited in advisories or release notes unless they request anonymity.

---

## References & compliance

- OWASP secure coding practices — https://owasp.org/
- NIST Cybersecurity Framework — https://www.nist.gov/cyberframework
- CWE/SANS Top 25 — https://cwe.mitre.org/top25/

---

**Last Updated:** 2025-11-24  
**Version:** v33Ω
