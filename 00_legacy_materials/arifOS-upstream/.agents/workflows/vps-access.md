---
description: Accessing and managing the arifOS VPS (Sovereign Infrastructure)
---

# VPS Access Workflow

This workflow ensures all arifOS AI agents are "conscious" of the sovereign VPS infrastructure and can access it without manual detail reentry.

### 1. Connection Protocol
All agents can now connect to the VPS using the simplified alias:
```bash
ssh arifos
```
*Note: This utilizes the SSH config at `~/.ssh/config` and the private key `~/.ssh/id_ed25519`.*

### 2. Infrastructure Overview
- **Host:** `72.62.71.199` (srv1325122.hstgr.cloud)
- **User:** `root`
- **Root Path:** `/opt/arifos` (Symlinked to `/root/arifOS`)
- **Containers:** 17 production containers (Traefik, arifosmcp, Qdrant, etc.)

### 3. Management Skills
Use the following commands for quick status checks from your local terminal:
- **List Containers:** `ssh arifos "docker ps --format 'table {{.Names}}\t{{.Status}}'"`
- **System Health:** `ssh arifos "df -h /; free -m"`
- **Logs:** `ssh arifos "docker logs -f arifosmcp"`

### 4. Canonical Documentation
Refer to the following files in the local repository for ground truth:
- [VPS Architecture](file:///C:/ariffazil/arifOS/infrastructure/VPS_ARCHITECTURE.md)
- [Capabilities Map](file:///C:/ariffazil/arifOS/infrastructure/VPS_CAPABILITIES_MAP.md)

### 5. Sovereignty Alignment
When operating on the VPS, agents must adhere to **Floor 11 (Auditability)** and **Floor 5 (Peace²)** of the APEX Constitution. All remote operations must be logged and reversible.
