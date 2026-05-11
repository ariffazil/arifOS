# Security & Production Hardening

This document outlines the security posture, threat model, and production hardening checklist for deploying the arifOS Intelligence Kernel.

## 🛡️ Threat Model

arifOS is designed explicitly to mitigate the "Confused Deputy" problem inherent in LLMs. Our threat model assumes that the underlying LLM:

1. Cannot be fully trusted to separate instructions from data (Prompt Injection).
2. Cannot be trusted to evaluate its own safety boundaries (Self-Ratification).
3. Will confidently attempt dangerous actions if tools are exposed without checks (Destructive Execution).

arifOS places the LLM behind the **L0 Kernel**, enforcing constraints externally.

## Security at a Glance

| Feature | Status | Notes |
|---------|--------|-------|
| **Authentication** | ✅ JWT Support                  | Set `ARIF_JWT_SECRET` for bearer token auth                        |
| **TLS Termination**  | ✅ Recommended                  | Use Nginx/Coolify/Cloudflare for SSL                               |
| **Audit Ledger**     | ✅ VAULT999 (Immutable ledger) | Cryptographic hash chain with Postgres persistence                 |
| **Rate Limiting**    | ⚠️ Deployment-level             | Configure at reverse proxy (Nginx/Cloudflare)                      |
| **Secrets Handling** | ✅ Environment vars             | Never commit credentials; use `.env` files                         |
| **Metrics Export**   | ✅ Prometheus-compatible        | Available at `/metrics` endpoint                                   |
| **Data Retention**   | ✅ Configurable                 | Postgres backups + VAULT999 snapshots                              |
| **RBAC**             | 🚧 Roadmap                      | Per-floor role-based access control (planned)                      |

## ✅ Security Checklist (Production)

Before exposing the `/mcp` endpoint publicly, ensure the following constraints are active:

- [ ] **HTTPS**: Force SSL termination in Nginx/Coolify. Never transmit MCP traffic over plaintext HTTP in production.
- [ ] **Authentication**: Set `ARIF_JWT_SECRET` and enable JWT middleware to prevent unauthorized tool execution.
- [ ] **Firewall**: Whitelist IPs, block unauthorized or broad external access.
- [ ] **Secrets**: Use environment variables. Ensure `ARIFOS_GOVERNANCE_SECRET` is set in production to a secure random value.
- [ ] **Backups**: Schedule `postgres_data` + `VAULT999/` backups.
- [ ] **Monitoring**: Enable Prometheus metrics at `/metrics`.
- [ ] **Rate Limiting**: Prevent DoS attacks (e.g., 100 req/min per IP) at the infrastructure level.
- [ ] **Human-in-the-Loop**: Ensure workflows involving high-stakes operations require explicit `888_HOLD` out-of-band cryptographic ratification.

## Security Architecture Implementation

### 1. F12 Defense (Data vs. Instruction)

External content (`fetch_content`) is explicitly wrapped in XML tags, marking it as untrusted to mitigate indirect prompt injection.

### 2. Amanah Handshake (Cryptographic Isolation)

The system uses the `ARIFOS_GOVERNANCE_SECRET` for HMAC-signing internal logic before committing it to VAULT999. If a secret isn't provided via environment variables, the AAA MCP Server dynamically generates a secure `token_hex(32)` to ensure the secret is never leaked nor known by the model.

### 3. F5/F6 Safeguards (Destructive Action Prevention)

The `simulate_heart` organ strictly blocks state transitions that risk operational safety or damage infrastructure, emitting a `SABAR` state.

## Disclosure Policy

If you discover a vulnerability in arifOS that allows an LLM to bypass all constitutional floors unilaterally, please email **[arifos@arif-fazil.com](mailto:arifos@arif-fazil.com)** securely. We will review and provide remediation timelines aligned with the CVSS severity.
