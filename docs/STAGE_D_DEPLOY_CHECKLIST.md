# arifOS Stage D — Deploy Checklist

## SEAL Reference
- **SEAL:** `seal-20260523T125400-DITEMPA-BUKAN-DIBERI-999-SEAL`
- **Date:** 2026-05-23

---

## Pre-Deploy Verification

### Host Requirements
- [ ] Python 3.11+ (`python3 --version`)
- [ ] Node.js 22+ (`node --version`)
- [ ] systemd running (`systemctl --version`)
- [ ] Root/sudo access
- [ ] Internet access (for npm/pip packages)

### Artifact Integrity
```bash
# Verify checksums (Stage C deploy manifest)
md5sum /workspace/arifOS/arifosd.py
md5sum /workspace/arifOS/lib_ARCHIVE/contract_schemas.py
md5sum /workspace/arifOS/lib_ARCHIVE/adapters.py
md5sum /workspace/arifOS/lib_ARCHIVE/arifOS_emulator.py
md5sum /workspace/arifOS/infrastructure/systemd/arifos.service
md5sum /workspace/arifOS/infrastructure/systemd/arifos.socket
md5sum /workspace/arifOS/config/arifosd.yaml
md5sum /workspace/arifOS/commands/arif_run.py
md5sum /workspace/arifOS/commands/arif_exec.py
md5sum /workspace/arifOS/commands/arif_sudo.py
md5sum /workspace/arifOS/commands/arif-systemctl.py
md5sum /workspace/arifOS/scripts/arifos_install.sh
```

---

## Deploy Sequence

### Step 1 — Prep
```bash
# Copy deploy bundle to VPS
scp -i ~/.ssh/hermes_vps_key -r /workspace/arifOS/ root@72.62.71.199:/root/arifOS/

# OR run install script directly on VPS
ssh -i ~/.ssh/hermes_vps_key root@72.62.71.199
```

### Step 2 — Install
```bash
cd /root/arifOS
bash scripts/arifos_install.sh
```

### Step 3 — Wrapper Verification
```bash
# Test atomic HOLD
python3 commands/arif_run.py "rm -rf /"
# Expected: HOLD, exit 1

# Test safe PROCEED
python3 commands/arif_run.py "ls /tmp"
# Expected: PROCEED, exit 0
```

### Step 4 — Daemon Verification
```bash
systemctl status arifos
systemctl status arifos.socket
curl http://localhost:8081/health
```

---

## Post-Deploy Verification

| Check | Command | Expected |
|-------|---------|-----------|
| Daemon alive | `systemctl status arifos` | active (running) |
| Socket unit | `systemctl status arifos.socket` | listening |
| Health endpoint | `curl http://localhost:8081/health` | 200 + JSON |
| Vault999 | `curl http://localhost:8081/vault/verify` | valid |
| Floor status | `curl http://localhost:8081/floors` | F01-F13 listed |
| Wrapper LOW | `python3 commands/arif_run.py "ls /tmp"` | PROCEED |
| Wrapper ATOMIC | `python3 commands/arif_run.py "rm -rf /"` | HOLD, exit 1 |
| Bashrc intercept | `bash -c "rm -rf /"` | arif_hold blocked |

---

## Blast Radius & Rollback

**Blast radius (worst case):**
- arifosd misconfiguration → daemon won't start
- Wrapper false positives → safe commands blocked
- systemd unit conflict → other services affected

**Rollback procedure:**
```bash
# Option A: Undo via install script
cd /root/arifOS
bash scripts/arifos_install.sh --rollback

# Option B: Manual rollback
systemctl stop arifos arifos.socket
rm /etc/systemd/system/arifos.service
rm /etc/systemd/system/arifos.socket
rm /etc/arifos/ -rf
pip uninstall arifos 2>/dev/null
```

---

## VPS Firewall Note

**Current VPS status:** Port 22 SSH BLOCKED from this host.
- Ping works (host alive)
- All TCP ports filtered/blocked
- Requires Arif to open SSH from VPS provider console before deploy

---

## Stage Gate

| Gate | Status |
|------|--------|
| Stage D Sandbox Deploy | 🚫 **888_HOLD required** |
| Stage E Production | 🚫 888_HOLD + SSH access |

**Conditions for 888_HOLD:**
1. Arif explicit approval (given: "I approve all")
2. VPS SSH access restored
3. Disposable/test VPS target confirmed