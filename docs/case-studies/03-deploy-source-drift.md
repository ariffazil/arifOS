# Case 3 — The published manifest said "aligned" while the deployed process ran older code

## 1. What happened

`/root/arifOS/README.md` opens with a machine-maintained SOT-MANIFEST block. On the
checkout used for this study it read:

```
$ sed -n '1,9p' /root/arifOS/README.md
<!-- SOT-MANIFEST
kernel_release: v2026.09.18
pypi_version: 1!2026.9.2
last_verified: 2026-09-18T00:40:00+00:00
live_commit: fdf4c93b6 (chore(entropy): remove stale test stubs + add repo entropy audit)
source_commit: fdf4c93b6
built_commit: a033a0d (deployed, reconciler pending)
deployment_drift_status: aligned (deployed=a033a0d, source=fdf4c93b6 — reconciler will close gap)
```

Line 8 asserts `aligned` while naming two different commits in the same sentence, and
line 4 dates the whole block three days before the observation. The live process disagreed
with all of it:

```
$ curl -s http://127.0.0.1:8088/health   # fields extracted
source_commit   e8e6f933563d2a92caa9e29bb082f62550d33146
built_commit    e8e6f93
deployed_commit e8e6f933563d2a92caa9e29bb082f62550d33146
drift           False
deployment_drift_status aligned
runtime_import_path /opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp/__init__.py
```

So the manifest named a deployed commit (`a033a0d`) that the process no longer runs, and a
source commit (`fdf4c93b6`) that is not the repository HEAD. The repository's own
cross-organ probe reports the gap directly:

```
$ .venv/bin/python scripts/drift_check_live.py
arifos-drift: ❌ DRIFT DETECTED at 2026-09-20T19:15:09.708098+00:00
  ⚠️ DRIFT arifos: src=b8219c53 deployed=e8e6f93
  ⚠️ DRIFT geox: src=d669605c deployed=d669605c
  ⚠️ DRIFT aforge: src=89b2bac7 deployed=9f2cecd
  ⚠️ DRIFT aaa: src=9d7b01a0 deployed=9d7b01a
    OK wealth: src=eaa87d5a deployed=UNKNOWN
    OK well: src=f61a435d deployed=f61a435
```

The arifos gap is one commit. At the start of this session `git rev-parse HEAD` returned
`e8e6f933563d2a92caa9e29bb082f62550d33146`, identical to the deployed stamp. A
concurrent writer then landed `b8219c538cc46d2a583d432e8691a955b0681caa` ("docs(positioning):
lead README with the domain-grounded positioning"), and the deployed process kept running
the previous commit. The failure is a window between source moving and the release being
stamped, not a broken pipeline.

The static manifest check is real and enforced, but only for pushes that touch README.md.
Reproducing its logic by hand:

```
$ README_COMMIT=$(grep 'live_commit:' README.md | head -1 | awk '{print $2}' | cut -c1-7)
$ GIT_HEAD=$(git rev-parse --short=7 HEAD); GIT_HEAD_PREV=$(git rev-parse --short=7 HEAD~1)
README live_commit: fdf4c93
git HEAD:          b8219c5
git HEAD~1:        e8e6f93
RESULT: SOT MANIFEST DRIFT DETECTED (CI job 13 would fail)
```

## 2. The systemic cause

A generated number has no owner between generations. The manifest is produced by reading a
live endpoint, so it is correct at the instant it is stamped and decays silently
afterwards. Two mechanisms compound it:

1. The stamp is taken from the repository, the deployment is taken from the release
   artifact, and nothing forces the two to be stamped in the same transaction. A commit
   that moves source without a release is invisible to the deployment path.
2. The gate on the manifest fires on a narrow trigger (`on: push: paths: ['README.md']`),
   so a stale manifest does not block or fail anything except the push that would have
   fixed it. The one check that could catch the decay only runs when someone already
   touched the file.

The README line itself is the tell: a status field that says `aligned` next to two unequal
hashes is a human-readable field carrying a machine-checkable claim without a machine
check attached to it.

## 3. The mechanism that closes the gap

- `/root/arifOS/scripts/deploy-release.sh` — the reconciler. It resolves
  `GIT_COMMIT="$(git rev-parse --short=7 HEAD)"` from the repo, writes
  `/opt/arifos/releases/release-manifest.json`, writes the deployed stamp to
  `/opt/arifos/releases/deployed-commit` and `$REPO_DIR/.git_commit`, restarts the service,
  then polls `/health?nocache=1` for up to 30 iterations and exits non-zero if the kernel
  does not become healthy. The stamp is deliberately a single stable path: the script's own
  comment reads "ONE stable path (build.py + reconciler read this). No legacy
  /opt/arifos/app stamp".
- `/root/arifOS/arifosmcp/runtime/build.py::get_runtime_attestation` — computes drift at
  request time from three independent readings: `source_commit` (repo stamp),
  `built_commit` (release manifest or `ARIFOS_BUILT_COMMIT`), `deployed_commit` (stamp
  file). Drift fires when those disagree, and separately when `ONE_ORIGIN` finds the live
  package importing from anywhere other than the active release venv.
- `/root/arifOS/scripts/update_readme_sot.py` — re-stamps the manifest header from live
  `/health`, patches `built_commit` and `deployment_drift_status` together, and supports
  `--dry-run`.
- `/root/arifOS/.github/workflows/13-sot-manifest-check.yml` — the gate that fails a push
  when `live_commit` matches neither HEAD nor HEAD~1, or warns when `last_verified` is
  more than 7 days old.

Current deployed truth, from the artifact the runtime actually reads:

```
$ cat /opt/arifos/releases/deployed-commit
e8e6f933563d2a92caa9e29bb082f62550d33146
$ cat /opt/arifos/releases/release-manifest.json   # key fields
"git_commit": "e8e6f93",
"build_timestamp": "2026-09-20T17:53:23Z",
"wheel_sha256": "a1bbbf9bc0b6b1b1bcf716fa319a1dfc5a9d856a0d1794a1c92fb3fa798ec674",
"canon_version": "2026.09.20-e8e6f93"
```

## 4. What is still missing

- No automatic restamp on release. `update_readme_sot.py` is run by hand before a commit;
  nothing in `deploy-release.sh` calls it, so the manifest can lag a deploy indefinitely.
- `live_commit == HEAD` is unachievable by construction — the workflow's own comment
  explains the stamp rides the next commit. The check therefore accepts HEAD~1, so a
  one-commit lag is tolerated by design rather than treated as drift.
- The `/opt/arifos/app` checkout still exists (HEAD `4b4c7c89dab917f35f2ab3e4f8c9d159d6c25dd6`,
  appended 2026-09-19) although the deploy script states the tree is retired by ONE_ORIGIN.
  `evidence not located`: no document found reconciling or formally deprecating that tree.
- `drift` on `/health` reads `false` while the repo HEAD is one commit ahead: the process
  cannot see a commit that was never released. Source-vs-deployed drift is only visible
  from outside, which is why `drift_check_live.py` exists — a script, not a scheduled gate.
- The GEOX and A-FORGE rows in the drift probe show cross-organ gaps that this study did
  not investigate.

## 5. The lesson

A status field that can disagree with reality needs a machine check on the same trigger
that can change reality — otherwise "aligned" is a timestamp, not a guarantee.
