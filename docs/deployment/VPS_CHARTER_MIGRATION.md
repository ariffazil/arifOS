# VPS Charter Migration

Use this checklist to align the VPS with the charter naming canon.

## Files To Expect
- `/root/arifOS/deploy/stack.charter.json`
- `/root/arifOS/federation.charter.json`
- `/root/arifOS/config/charter/kernel.charter.yaml`
- `/root/arifOS/CONFIG/sovereignty.charter.json`

## Checklist
1. Pull latest repo state on VPS.
2. Search for stale active paths:
   - `stack.manifest.json`
   - `federation_manifest.json`
   - `federation-manifest.json`
   - `config/manifest/`
   - `SovereigntyManifest.json`
3. Update deploy scripts and systemd/env wrappers to point at `*.charter.*` files.
4. Confirm Observatory static file serves `/federation.charter.json`.
5. Confirm pre-deploy checks read `deploy/stack.charter.json`.
6. Confirm any repo automation or GitHub Actions docs reference charter names.
7. Leave protocol discovery endpoints unchanged: `server.json`, `agent.json`, `registry.json`, `server-card.json`.

## Verification Commands
```bash
ls /root/arifOS/deploy/stack.charter.json /root/arifOS/federation.charter.json
grep -R "stack.manifest.json\|federation_manifest.json\|federation-manifest.json\|SovereigntyManifest.json" /root/arifOS --exclude-dir=.git --exclude-dir=00_legacy_materials
```
