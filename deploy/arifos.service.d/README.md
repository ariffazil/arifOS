# arifos.service.d — Tracked systemd drop-in templates

This directory holds **tracked** drop-in overrides for the systemd unit
that boots arifOS.  Drop-ins live here in source control so the override
intent is reviewable in PRs — they are NOT installed into
`/etc/systemd/system/` by any automated tooling.

## Contents

| File | Purpose |
|---|---|
| `01-clear-execstartpost.conf` | Clears any inherited `ExecStartPost=` directive from the upstream `arifos.service`.  Used by the 2026-07-22 HIB/recovery refactor to retire the in-service auto-registration path. |

## Install (operator-only, F13)

```bash
sudo install -d /etc/systemd/system/arifos.service.d
sudo install -m 0644 \
    /root/arifOS/deploy/arifos.service.d/01-clear-execstartpost.conf \
    /etc/systemd/system/arifos.service.d/01-clear-execstartpost.conf
sudo systemctl daemon-reload
sudo systemctl restart arifos.service
```

## Why drop-ins and not a full unit rewrite

Drop-ins apply **last** in systemd's precedence chain (lowest first).
Override one directive here and the upstream unit file in
`/etc/systemd/system/arifos.service` stays untouched.  This keeps the
blast radius of any change to a single 200-byte file and an F13-approved
restart.

## What the override does

The recovery refactor moved federation auto-registration onto the AAA
side (`AAA/a2a-server/auto-register-organs.js` with bounded readiness
probes).  The per-organ `ExecStartPost=` hook that previously called a
post-start registration helper is now redundant; this drop-in clears
that directive so arifOS boots cleanly without depending on an external
helper script that may have been retired.

DITEMPA BUKAN DIBERI.
