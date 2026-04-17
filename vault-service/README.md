# VAULT999 — Unified Merkle Ledger Service

WELD-003: Merkle-chained vault for arifOS federation.

## Overview

The VAULT999 service provides an immutable, append-only ledger with Merkle chain verification for the arifOS federation (GEOX, WEALTH, A-FORGE, arifOS).

## Chain Invariant

```
entry_n.chain_hash = SHA-256(entry_(n-1).chain_hash + entry_n.payload_hash)
```

Any tampering with a past entry breaks all downstream `chain_hash` values — detectable on read.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/vault/seal` | Write a governed action to the ledger |
| GET | `/vault/session/{id}` | Get full chain for a session |
| GET | `/health` | Service health check |

## Sealing Rules

Only `PROCEED` and `SEAL` verdicts are sealed. `HOLD` and `VOID` are **not** sealed — ungoverned states do not enter the chain.

## Usage

```python
from vault_service.client import VaultClient, seal_vault_entry

# Using convenience function
result = await seal_vault_entry(
    session_id="abc-123",
    domain="GEOX",
    tool="geox_prospect_evaluate",
    verdict="PROCEED",
    ac_risk=0.05,
    claim_tag="PLAUSIBLE",
    floor_violations=[],
)

# Or using the full client
async with VaultClient() as client:
    result = await client.seal(
        session_id="abc-123",
        domain="GEOX",
        tool="geox_prospect_evaluate",
        verdict="PROCEED",
        ac_risk=0.05,
        claim_tag="PLAUSIBLE",
    )
    chain = await client.get_session("abc-123")
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://arifos_admin:password@postgres:5432/arifos_vault` | Postgres connection |
| `PORT` | `8100` | Service port |

## DITEMPA BUKAN DIBERI