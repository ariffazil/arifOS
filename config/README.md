# 🔐 Canonical Secret Registry System

## The Problem This Solves

**Interface Mismatch Chaos:**
- `arifosmcp_server` wants `OPENAI_API_KEY`
- `agent_zero_reasoner` wants `OPENAI_KEY` (different name!)
- `openclaw_gateway` wants `OPENAI_API_KEY` again
- `n8n` wants JSON config
- `postgres` wants Docker secrets

**Before:** You manually maintained `.env` files with different formats for each app.

**After:** One canonical registry, auto-generated per-app configs.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ HUMAN INPUT                                                         │
│   /root/.secrets/vault.env (14 keys, 600 perms)                    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ CANONICAL REGISTRY                                                  │
│   /root/arifOS/config/secret-registry.yaml                         │
│                                                                     │
│   Canonical names:          Maps to vault keys:                     │
│   llm.openai.api_key   →    OPENAI_API_KEY                          │
│   llm.anthropic.api_key →   ANTHROPIC_API_KEY                       │
│   infra.postgres.password → POSTGRES_PASSWORD                       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ APP REGISTRY (who needs what)                                       │
│   arifosmcp_server:  requires llm.openai.api_key                    │
│                       render OPENAI_API_KEY: llm.openai.api_key    │
│                                                                     │
│   agent_zero_reasoner: requires llm.openai.api_key                  │
│                         render OPENAI_KEY: llm.openai.api_key      │
│                         ↑ Same canonical, different output!        │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│ ADAPTERS (auto-generated)                                           │
│   .env format → /root/arifOS/rendered/{project}/{app}.env          │
│   JSON format → /root/arifOS/rendered/{project}/{app}.json         │
│   Docker secret → /root/arifOS/secrets/{name}.txt                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Usage

### 1. Add a secret (you type in terminal)
```bash
vault set openai sk-your-key-here
```

### 2. Register a new app in secret-registry.yaml
```yaml
apps:
  my_new_app:
    project: arifos
    requires:
      - llm.openai.api_key
    render:
      format: env
      mapping:
        # App expects MY_OPENAI_KEY, we map from canonical
        MY_OPENAI_KEY: llm.openai.api_key
```

### 3. Generate configs
```bash
# One app
vault-render my_new_app

# One project
vault-render arifos

# All projects
vault-render all
```

### 4. Use in docker-compose
```yaml
services:
  my_new_app:
    env_file:
      - /root/arifOS/rendered/arifos/my_new_app.env
```

## Project Isolation

| Project | Apps | Secrets Access |
|---------|------|----------------|
| `arifos` | 11 containers | Global (llm.*, search.*) + arifos infra |
| `server` | 5 containers | Global + server infra (isolated from arifos) |
| `portainer-wireguard` | 3 containers | None (isolated, no LLM access) |

**888 HOLD:** Never share infra secrets across projects.

## Canonical Naming Convention

| Prefix | Purpose | Example |
|--------|---------|---------|
| `llm.*` | LLM providers | `llm.openai.api_key` |
| `search.*` | Search APIs | `search.brave.api_key` |
| `infra.*` | Infrastructure | `infra.postgres.password` |
| `integration.*` | External services | `integration.notion.api_key` |

## Adapter Formats

| Format | Use Case | Output |
|--------|----------|--------|
| `env` | Most apps | `KEY=value` file |
| `json` | Config-heavy apps | `{"key": "value"}` file |
| `docker_secret` | Docker Swarm | `/root/arifOS/secrets/*.txt` |
| `none` | No secrets needed | Nothing generated |

## Validation

Before rendering, the system checks:
1. All required secrets exist in vault
2. No circular dependencies
3. Project isolation rules followed
4. Sensitivity levels appropriate for format

Missing secrets are flagged but rendering continues (with comments in output).

## Commands

```bash
# List all apps and their status
vault-render --list

# Render specific app
vault-render arifosmcp_server

# Render entire project
vault-render arifos

# Render everything
vault-render all
```

## Files

| File | Purpose |
|------|---------|
| `/root/arifOS/config/secret-registry.yaml` | Canonical schema and app mappings |
| `/root/arifOS/rendered/{project}/` | Generated per-app configs |
| `/root/arifOS/rendered/{project}/{project}.env` | Combined env for docker-compose |
| `/root/arifOS/secrets/*.txt` | Docker secret files |

## Integration with VAULT999

The canonical registry is **Tier 0.5** - between human input and sovereign control:

```
Tier 0: Human → vault.env
Tier 0.5: Registry → secret-registry.yaml (canonical names)
Tier 1: Adapters → rendered configs
Tier 2: VAULT999 → attestation + cold storage
```

Attestation includes registry checksum:
```bash
python3 /root/arifOS/core/vault999/bridge_from_vault.py attest
```

---
*888_JUDGE | 999_SEAL | DITEMPA BUKAN DIBERI*
