# arifOS Secrets Directory

This directory documents the expected secret layout only.
No live secret file should ever be committed here.

## Canonical VPS Secret Path

```bash
/opt/arifos/secrets/governance.secret
```

## Use

```bash
export ARIFOS_GOVERNANCE_SECRET_FILE=/opt/arifos/secrets/governance.secret
```

## Rules

- Forge or securely copy the secret onto the VPS outside Git.
- Keep permissions at `600` for the file and `700` for the directory.
- Use `ARIFOS_GOVERNANCE_SECRET_PREVIOUS_FILE` only during rotation grace periods.
