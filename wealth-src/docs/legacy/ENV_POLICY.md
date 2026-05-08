# ENV Policy — Single Source, Low Chaos

This workspace uses one canonical environment file.

## Canonical Source

- Canonical env file: `/root/XXX/.env.master`
- Compatibility path: `/root/openclaw_data/.env` (must be symlink to canonical file)
- Memory cron must use: `OPENCLAW_ENV_FILE=/root/XXX/.env.master`

## Rules

- Do not inline secrets in crontab entries.
- Do not create per-feature `.env` files for the same runtime.
- Add runtime keys to canonical env only.
- Keep file permission `600` and owner `root:root`.

## Required Memory Keys

- `QDRANT_URL`
- `QDRANT_API_KEY`
- `MEMORY_EMBED_MODEL`
- `MEMORY_QDRANT_COLLECTION`

## Drift Detection

- Use `python3 memory_tools/memory_pipeline.py --workspace /root/openclaw_data/workspace env-lint`
- `run_cycle.sh` runs `env-lint` before daily memory operations.
- Heartbeat daily checks include `env-lint`.

## Recovery Procedure

1. Re-point symlink: `ln -sfn /root/XXX/.env.master /root/openclaw_data/.env`
2. Fix permission: `chmod 600 /root/XXX/.env.master && chown root:root /root/XXX/.env.master`
3. Remove inline cron secrets and keep only `OPENCLAW_ENV_FILE=...`
4. Re-run `env-lint` and then `run_cycle.sh`
