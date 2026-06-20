# arifOS Reality Check + Deploy Sequence

Read-only preparation artifact for the bare-metal `arifOS` runtime.

This sequence is intentionally split into:

1. reality check
2. deploy readiness
3. explicit hold point
4. deploy execution
5. post-deploy verification

Nothing in this document authorizes execution by itself.

## Preconditions

- Local repo state is understood and intentionally clean enough to deploy.
- `origin/main` contains the target SHA.
- F13 has explicitly approved live execution.

## Phase 1: Reality Check

Run these without mutating the VPS:

```bash
cd /root/arifOS
git rev-parse --short HEAD
curl -fsS http://127.0.0.1:8088/health | python3 -m json.tool
systemctl is-active arifos.service arifosd.service
cat /opt/arifos/app/.git_commit 2>/dev/null || true
python3 scripts/federation_reality_probe.py --write-md --write-json --public
```

What to record:

- source SHA from `/root/arifOS`
- live SHA from `/opt/arifos/app/.git_commit`
- service status for `arifos.service` and `arifosd.service`
- health payload status and version fields
- whether runtime drift exists

## Phase 2: Deploy Readiness

Check whether the current local checkout is actually deployable:

```bash
cd /root/arifOS
git fetch origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
uv run python -m arifosmcp.transport.conformance_spine
```

If `HEAD != origin/main`, stop.

If conformance fails, stop.

## Phase 3: F13 Hold Point

Required explicit decision:

- proceed with `make deploy-local`
- or stop and keep drift visible

## Phase 4: Deploy Execution

Only after explicit approval:

```bash
cd /root/arifOS
make deploy-local
```

`make deploy-local` performs:

- `rsync` into `/opt/arifos/app`
- writes `/opt/arifos/app/.git_commit`
- restarts `arifos.service`
- waits for `/health`
- runs conformance post-deploy

## Phase 5: Post-Deploy Verification

Re-run the same reality checks:

```bash
curl -fsS http://127.0.0.1:8088/health | python3 -m json.tool
systemctl is-active arifos.service arifosd.service
cat /opt/arifos/app/.git_commit
```

Expected result:

- live SHA matches source SHA
- `status` is `healthy` or explicitly accepted `degraded`
- conformance remains green

## Failure Conditions

Stop and hold if any of these occur:

- `/opt/arifos/app/.git_commit` does not match target SHA after deploy
- `arifos.service` fails to become active
- `/health` returns non-200 or unhealthy payload
- conformance spine fails post-deploy

## Notes

- This runtime is bare-metal systemd, not the older GHCR/Compose path.
- Drift visibility is desirable. Auto-tracking repo head is not.
- The correct constitutional behavior is visible drift plus explicit sovereign approval for execution.
