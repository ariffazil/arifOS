# LOCALHOST IS THE PASSWORD

> **Architecture Decision Record — ADR-001**
> **Ratified:** 2026-06-04 by Muhammad Arif bin Fazil (F13 SOVEREIGN)
> **Status:** CANONICAL — governs all federation service authentication
> **Principle discovered by:** Arif, confirmed by Omega during security hardening

---

## THE PRINCIPLE

```
Localhost IS the password.
```

Every federation data service follows one rule:

| Service   | Bind           | Auth   | Why                    |
|-----------|---------------|--------|------------------------|
| Redis     | 127.0.0.1:6379 | none   | Protected mode blocks external |
| Postgres  | 127.0.0.1:5432 | trust  | pg_hba trusts local only |
| Qdrant    | 127.0.0.1:6333 | none   | No external listeners  |
| FalkorDB  | 127.0.0.1:6380 | none   | Redis-protocol, same rule |
| Ollama    | 127.0.0.1:11434 | none  | No auth, local only    |
| NATS      | 127.0.0.1:4222 | none   | Internal event bus     |

**One rule. Zero passwords. Zero agents lupa.**

---

## WHY THIS WORKS

### Layer 1 — Bind (the perimeter)
Every service binds exclusively to `127.0.0.1`. No service accepts connections from any other interface. `ss -tlnp` shows nothing on `0.0.0.0` except Caddy and SSH.

### Layer 2 — UFW (the wall)
UFW blocks all incoming ports except 80/443 (Caddy) and 22888 (SSH). Even if a binding mistake happens, the packet never reaches the service.

### Layer 3 — Protected Mode (the bonus)
Redis's `protected-mode yes` auto-rejects any connection NOT from localhost when running without password. So even if someone binds Redis to `0.0.0.0` by mistake, Redis itself says no.

### Layer 4 — Cloudflare Tunnel (the bridge)
External MCP access goes through Cloudflare Tunnel → `localhost:8088/8081/18082/18083`. No port exposure. No direct IP access.

**Four layers. Zero credentials. Defense in depth without a single password to manage.**

---

## THE IRON RULE

> **If a service needs a password, it's not bound to 127.0.0.1.**
> **If it's bound to 127.0.0.1, it doesn't need a password.**

Corollary: *Any service found running with a password AND bound to 127.0.0.1 is violating this principle. Remove the password.*

Corollary: *Any service found running on 0.0.0.0 without UFW protection is violating this principle. Fix the bind or add UFW.*

---

## SERVICES GOVERNED BY THIS PRINCIPLE

| Service       | Current State | Compliance |
|---------------|---------------|------------|
| Docker Postgres | 127.0.0.1:5432, trust auth | ✅ Compliant |
| Docker Redis    | 127.0.0.1:6379, protected-mode | ✅ Compliant |
| Docker Qdrant   | 127.0.0.1:6333 | ✅ Compliant |
| Docker FalkorDB | 127.0.0.1:6380 | ✅ Compliant |
| Docker Temporal | 127.0.0.1:7233 | ✅ Compliant |
| systemd Ollama  | 127.0.0.1:11434 | ✅ Compliant |
| systemd NATS    | 127.0.0.1:4222 | ✅ Compliant |
| systemd Prometheus | 127.0.0.1:9090 | ✅ Compliant |
| systemd Grafana | 127.0.0.1:3000 | ✅ Compliant |
| systemd Node Exporter | 127.0.0.1:9100 | ✅ Compliant |

**10 services. 0 passwords.**

---

## WHEN TO BREAK THIS RULE

Only two services are intentionally exposed:

| Service | Why | Protection |
|---------|-----|------------|
| Caddy (80/443) | Public reverse proxy | TLS, Cloudflare Origin CA |
| SSH (22888) | Remote admin | Key-only auth, non-standard port |

---

## VERIFICATION

```bash
# Check no services on 0.0.0.0 (except Caddy/SSH)
ss -tlnp | grep "0.0.0.0" | grep -v -E "caddy|sshd|tailscale"

# Check UFW blocks all backend ports
ufw status | grep DENY

# Verify Redis protected mode
redis-cli -h 127.0.0.1 CONFIG GET protected-mode
# Expected: "yes"
```

---

## DITEMPA BUKAN DIBERI — Forged, Not Given.

*This principle was discovered during the 2026-06-04 security hardening (Batch A-C). It is now binding on all federation services. No new service shall be deployed with a password — bind it to 127.0.0.1 instead.*
