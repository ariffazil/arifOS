# Security Policy

## Supported Versions

The arifOS Federation operates on a rolling release model. The latest commit on
`main` across all organs is the supported version.

| Version | Supported          |
| ------- | ------------------ |
| `main`  | :white_check_mark: |
| Other   | :x:                |

## Reporting a Vulnerability

We take security seriously. arifOS runs infrastructure that handles governance,
audit trails, and potentially sensitive biometric and financial data.

**Please do NOT open a public issue for security vulnerabilities.**

Instead:
1. Contact the maintainers directly at **arifbfazil@gmail.com**
2. Include a description of the vulnerability, steps to reproduce, and potential impact.
3. We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Security Architecture

- **Localhost-first**: Core services (Postgres, Redis, Qdrant, Ollama, NATS) bind
  `127.0.0.1` with no auth — firewalled by UFW, not exposed to the public internet.
- **Constitutional gates**: Every action passes through F1–F13 constitutional floors
  before execution. Unauthorized mutations are blocked by design.
- **Immutable audit ledger**: VAULT999 maintains an append-only record of all
  sealed outcomes (67K+ records, 0 broken lines).
- **Separation of powers**: The judge (arifOS kernel) never executes. The executor
  (A-FORGE) never self-certifies. No single component can act and approve itself.

## Known Security Boundaries

- All federation communication occurs over a private Tailscale mesh (`100.64.0.0/24`).
- Reverse proxy (Caddy) handles TLS termination and rate limiting.
- Secrets are stored in `/root/.secrets/kunci-root.env` with `mode 600` — never
  committed to git, never exposed in logs.

## Acknowledgments

We welcome responsible disclosure and will credit reporters who follow our
coordinated disclosure process.
