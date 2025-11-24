```markdown
# arifOS Security Policy

If you discover a security vulnerability in arifOS, thank you — please report it responsibly and confidentially.

Preferred reporting channels (in order)
1. GitHub Security Advisory (recommended) — open a private security advisory in this repository.
2. Encrypted email to the security contact below (PGP) — see instructions for encryption.
3. If neither is possible, email: arifbfazil@gmail.com

When reporting, provide as much detail as possible. See the "How to report" section below.

Do NOT post PoCs or exploit details publicly before a fix is available.

---

## How to report

Please include:
1. A short title and affected component (e.g., `Cooling Ledger: chain verification bypass`)
2. Affected version(s) or commit SHA
3. Proof-of-concept or reproduction steps (minimal test case)
4. Impact assessment (what an attacker could do)
5. Suggested mitigation or patch (if you have one)
6. Contact details (optional) and an indication if you can be contacted for follow-up

If you want to send encrypted details, please encrypt to the project's PGP key (publish the fingerprint here). If you send via GitHub Security Advisory, you can attach a private PoC there.

Out-of-scope / Do not
- Do not test on production systems without explicit permission.
- Do not publicly disclose the vulnerability until a coordinated disclosure is arranged.
- Do not send large amounts of data or personal data unless requested.

---

## Contact & encryption

Primary contact (for confidential reports): arifbfazil@gmail.com

We strongly prefer GitHub Security Advisories. If you must use email and will send sensitive PoC information, encrypt it using PGP to the project's public key:

- PGP key fingerprint: (publish your public key fingerprint here)
- If you do not see a PGP fingerprint published and need to send a PoC, use a GitHub Security Advisory or ask for a one-time secure channel.

If you report via email, we will acknowledge receipt and provide an advisory reference number.

---

## Response commitments & severity handling

We will triage reports according to severity. These are guidelines; final prioritization may vary.

Severity levels (guideline)
- Critical: remote code execution, private key compromise, ability to forge ledger entries, or other systemic compromise. Response: acknowledge within 24 hours; patch or mitigations within 7 days (or provide plan).
- High: privilege escalation, bypass of APEX/Amanah without key compromise. Response: acknowledge within 24–48 hours; fix or mitigation within 14 days.
- Medium: information exposure, denial of service against a non-critical component. Response: acknowledge within 48 hours; fix in next minor release.
- Low: UI issues, low-impact bugs. Response: acknowledge within 5 business days.

Responsible-disclosure timeline
1. Within 24 hours: acknowledge receipt with an advisory reference.
2. Within 3 days: preliminary triage and action plan.
3. Within 14 days: publish fix or mitigation for high severity, or a concrete timeline to fix.
4. Within 30 days: public disclosure with advisory (unless longer coordination required).

If you prefer a different timeline (e.g., for research projects), state that in your report.

---

## Scope: what we cover

We consider issues affecting:
- arifOS core runtime and libraries (arifos_core)
- Cooling Ledger and Vault-999 implementation
- APEX PRIME, guardrails, and constitutional enforcement
- Deployment scripts and CI/CD definitions in this repository

Exclusions:
- Third-party services or libraries (report to vendor and optionally to us)
- Misconfiguration of a user's private deployment not caused by upstream code
- Social-engineering issues outside codebase

---

## Security practices and runtime invariants

arifOS places emphasis on constitutional governance and operational invariants. We aim to enforce the following floors at runtime and by design:

- Truth ≥ 0.99
- ΔS ≥ 0
- Peace² ≥ 1.0
- κᵣ ≥ 0.95
- Ω₀ ∈ [0.03, 0.05]
- Amanah = LOCK
- RASA = TRUE
- Tri-Witness ≥ 0.95

These are enforced by runtime checks, unit tests, integration tests, and monitoring where practical. If you believe a code path permits bypassing these invariants, please report it as high severity.

---

## Cryptography & key management

- Cooling Ledger entries must be serialized deterministically (canonical JSON) before hashing.
- We use SHA3-256 (or SHA-256 in FIPS environments) for chain linkage. High-stakes seals must be signed with KMS/HSM-backed keys in production.
- Private signing keys MUST NOT be committed to the repository or to CI logs.
- For local development, use ephemeral dev keys and mark them clearly in test configurations.

Recommended production setup:
- Use AWS KMS / Azure Key Vault / GCP KMS / Hardware Security Module (HSM) for signing keys.
- Centralize key rotation, with an immutable rotation log recorded in the ledger.
- Enforce strict IAM policies and audit logging for key usage.

---

## Key compromise procedure (high-level)

If you believe a signing key is compromised:
1. Immediately revoke the key in KMS/HSM and rotate to a new key.
2. Notify maintainers and create an internal incident ticket. We will acknowledge within 24 hours.
3. Mark affected seals as SUSPECT in ledger metadata and create a Vault‑999 amendment record for key rotation.
4. Re-verify affected seals with fresh APEX PRIME verdicts if possible; append re-verification entries to ledger.
5. Publish a security advisory once impact and remediation are clear.

Indicators of compromise:
- Unexpected signing activity from unknown principal
- Missing or altered ledger entries
- Alerts from KMS or IAM logs for unauthorized access

---

## CI/CD and automation

We recommend and aim to run:
- Dependabot (or similar) for dependency vulnerability alerts (weekly)
- CodeQL / SAST scanning for repository code
- Secrets scanning (gitleaks / git-secrets) in CI and pre-commit
- Automated unit tests, type checks (mypy), and linters on all PRs

Merge policy:
- All PRs must pass tests and type checks.
- Changes to APEX, Ledger, Vault, or guard modules require explicit code-owner reviews and at least one additional security reviewer.

---

## Monitoring & detection

In production, monitor:
- Ledger verification failures and mismatched hashes
- Unusual signing patterns or KMS key usage
- APEX override or attempted bypass events
- Failed tri-witness gating for high-stakes operations

Configure alerting so on-call engineers are notified for critical security events.

---

## Responsible disclosure & credit

We appreciate coordinated disclosure. Reporters who follow this policy and provide practical, actionable reports will be credited in release notes or a public security advisory unless they request anonymity.

---

## Compliance & standards

arifOS is developed with reference to:
- NIST AI RMF
- ISO/IEC 42001 (AI management)
- EU AI Act (governance)
- OWASP secure coding practices

---

## References

- OWASP Secure Coding Practices: https://owasp.org/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CWE/SANS Top 25: https://cwe.mitre.org/top25/

---

**Last Updated:** 2025-11-24  
**Version:** v33Ω
```