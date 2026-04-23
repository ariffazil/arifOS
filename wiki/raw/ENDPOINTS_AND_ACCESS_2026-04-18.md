# Ecosystem Endpoints and Access Points

**Sealed:** 2026-04-18  
**ADR:** ADR-ENDPOINTS-2026-04-18  
**VAULT999:** canon_records.id = 6

---

## Canonical Agent Access Links

| Service | URL | Notes |
|---|---|---|
| **AAA Cockpit** | https://aaa.arif-fazil.com/ | arifOS live dashboard, all agents |
| **MCP Surface** | https://mcp.arif-fazil.com/ | MCP tools + /health |
| **GEOX** | https://geox.arif-fazil.com/ | Subsurface epistemic engine |
| **WAW** | https://waw.arif-fazil.com/ | WEALTH governed intelligence |
| **arif-fazil.com** | https://arif-fazil.com/ | Personal + framework intro |
| **APEX** | https://apx.arif-fazil.com/ | Governance dashboard |

---

## Direct VPS Access

- **IP:** https://72.62.71.199/
- **PostgreSQL:** `postgresql://arifos_admin:ArifPostgresVault2026!@72.62.71.199:5432/arifos_vault`
- **Metrics:** http://72.62.71.199:9100/metrics

> **Note:** Direct IP access bypasses Cloudflare. nginx falls back to the aaa.arif-fazil.com server block.

---

## Network Topology

```
User/Agent → https://aaa.arif-fazil.com → Cloudflare → 72.62.71.199 → nginx → arifos-mcp:8080
                                                 ↓
                                       docker network
                                                 ↓
                              arifos-mcp / WEALTH / GEOX / vault-service / postgres
```

---

## Security Notes

1. **nginx fallback:** Direct IP on :443 falls back to aaa server block — no auth bypass
2. **PostgreSQL :5432:** Open to internet, scram-sha-256 password auth only
3. **node-exporter :9100:** Fully public — VPS CPU/RAM/disk metrics exposed
4. **Supabase:** Auth broken — `fVw7szhEx9LDbs0I` fails pgBouncer connection

---

## Vault999

- **Primary:** Local postgres on docker `arifos_core_network`
- **Canonical vault:** `postgresql://arifos_admin@72.62.71.199:5432/arifos_vault`
- **Supabase secondary:** Broken (auth failure)

---

*Ditempa Bukan Diberi — 999 SEAL ALIVE*
