---
id: coolify-hostinger
title: Hostinger Coolify VPS Template
sidebar_position: 4
description: Getting started with Hostinger’s “Ubuntu 24.04 with Coolify” VPS template and deploying arifOS via Docker Compose.
---

# Hostinger Coolify VPS Template (Ubuntu 24.04)

Hostinger’s **“Ubuntu 24.04 with Coolify”** template ships with Coolify preinstalled.

## Quick Checklist (Operator)

- Access Coolify UI at port **3000** on your VPS IP.
- Finish first‑time **admin** + **localhost** onboarding.
- Create a project, then add an app/database as a resource.
- Lock down firewall, then later add domain + SSL.

---

## 1) Prerequisites (Hostinger)

- Create a VPS using Hostinger’s **“Ubuntu 24.04 with Coolify”** template (Coolify is preinstalled).  
  Hostinger guide: [https://www.hostinger.com/support/9615197-how-to-use-the-coolify-vps-template-at-hostinger/](https://www.hostinger.com/support/9615197-how-to-use-the-coolify-vps-template-at-hostinger/)
- Find your VPS **public IP** in Hostinger → **VPS** → **Overview**.

> Note: Port defaults can vary across Coolify installs (commonly **8000** for generic installs), but the
> Hostinger template guide references **3000**. If `:3000` doesn’t load, confirm the port shown in your
> Hostinger panel or Coolify’s installation docs.

## 2) Accessing Coolify (first time)

1. Open: `http://<YOUR_VPS_IP>:3000`
2. First access: create the **admin account** (email + password).
3. Complete the onboarding wizard.

## 3) Onboarding: localhost vs remote

When asked **“Where to deploy?”**, choose **localhost** if this is your only Coolify server and you want
apps to run on the same VPS.

Coolify refs:

- [https://coolify.io/docs/get-started/introduction](https://coolify.io/docs/get-started/introduction)
- [https://coolify.io/docs/knowledge-base/server/introduction](https://coolify.io/docs/knowledge-base/server/introduction)

## 4) Create a project + add resources

1. Coolify dashboard → **Projects** → **+ Add** (create a project, e.g. `my-site-prod`).
2. Open the **Production** environment.
3. Click **+ Add New Resource** and pick:
   - **Application** (from Git repo, Docker image, etc.)
   - **Database** (PostgreSQL, MySQL, Redis, …)
   - Other services
4. Deploy once and confirm logs look healthy.

---

## 5) Firewall + security (do this early)

Close all doors, then open only what’s required:

- Allow at minimum (typical):
  - `22/tcp` (SSH; ideally restrict by source IP later)
  - `80/tcp` (HTTP)
  - `443/tcp` (HTTPS)
  - Coolify UI port: `3000/tcp` (while configuring; later restrict)

If you use `ufw` on the VPS, mirror the same allow rules and then enable it.

---

## 6) Domains + SSL (after the app works)

1. In Coolify, set a **Domain** on the resource (e.g. `app.example.com`).
2. Point DNS `A` record → your VPS public IP.
3. Enable **SSL/HTTPS** in Coolify (Let’s Encrypt via the reverse proxy).

---

## Deploy arifOS via Coolify (recommended: Docker Compose)

In Coolify:

1. Project → **Add Resource** → **Docker Compose**
2. Repo: `ariffazil/arifOS`
3. Compose path: `deployment/docker-compose.vps.yml`
4. Deploy

If deploy fails with `network not found`, create the external network once on the VPS:

```bash
docker network create coolify
```

### Attach domain + HTTPS (arifOS)

- Resource → **Domains** → add `arifosmcp.arif-fazil.com` (or your subdomain)
- Enable **HTTPS / Let’s Encrypt** (Coolify-managed)

### Verify arifOS endpoints

```bash
curl -i https://arifosmcp.arif-fazil.com/health
curl -N -H "Accept: text/event-stream" https://arifosmcp.arif-fazil.com/sse
curl -sS https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

---

## Governance Telemetry (optional)

```json
{
  "telemetry": {
    "space": "Opencode-arifOS",
    "focus": ["VPS_coolify_hostinger", "beginner_setup"],
    "risk_protocol": "888_HOLD for irreversible actions"
  },
  "governance_audit": {
    "F1_F11_reversible": "All actions (firewall, DNS, Coolify config) are reversible; no destructive ops suggested.",
    "F2_F7_truth_uncertainty": "Instructions pulled from Hostinger + Coolify docs; ports/UI port details partly Estimate Only, user should confirm in panel.",
    "F4_entropy": "Stepwise checklist and clear bullets reduce confusion.",
    "F5_F6_peace_maruah": "Emphasis on security, no risky shortcuts.",
    "F12_injection_guard": "No instructions weaken security; user advised to restrict access, not open more."
  }
}
```
