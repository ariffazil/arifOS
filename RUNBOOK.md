# RUNBOOK.md — arifOS (Constitutional Kernel)

> **Scope:** Operational procedures for the arifOS kernel on the `af-forge` VPS.
> **Authority:** F13 SOVEREIGN. Irreversible actions require explicit ratification.
> **Last Updated:** 2026-06-16

---

## 1. Health Checks

### Quick probe
```bash
curl -s http://localhost:8088/health | python3 -m json.tool
```
Expected: `status: healthy`, `tools_loaded: 13`, `floors_active: 13`.

### Full federation organ probe
```bash
for p in 8088 8081 18082 18083 7071 3001; do
  echo "--- localhost:$p ---"
  curl -s --max-time 3 http://localhost:$p/health | head -c 200
  echo
done
```

---

## 2. Restart

### Restart arifOS only
```bash
sudo systemctl restart arifos.service arifosd.service
```

### Verify after restart
```bash
sudo systemctl status arifos.service arifosd.service
curl -s http://localhost:8088/health | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])"
```

---

## 3. Logs

```bash
# Real-time kernel logs
sudo journalctl -u arifos -f

# Recent logs across federation organs
sudo journalctl -u arifos -u arifosd -u geox-mcp -u wealth-organ -u well -u a-forge -u aaa-a2a --since "1 hour ago"
```

---

## 4. Tests

```bash
cd /root/arifOS

# Fast unit/integration suite
uv run pytest tests/ -q --tb=short

# Exclude slow/e2e
uv run pytest tests/ -m "not e3e and not slow" -q --tb=short

# Source-of-truth drift audit
make sot-check

# Canon drift check (T0)
make canon-drift
```

---

## 5. Rollback

### Code rollback
```bash
cd /root/arifOS
git log --oneline -5
git revert <bad-commit-hash>
sudo systemctl restart arifos.service arifosd.service
```

### Deploy rollback (if `deploy-local` was used)
```bash
cd /root/arifOS
GIT_SHA=$(git rev-parse --short=7 HEAD~1)
rsync -av --exclude='.git' --exclude='.venv' ./ /opt/arifos/app/
sudo systemctl restart arifos.service arifosd.service
```

Always seal a VAULT999 rollback receipt after any rollback.

---

## 6. Security / Audit

```bash
make security-audit   # non-blocking scan
make conformance      # ARIF Conformance Spine
python scripts/vault999_status.py
```

---

## 7. Escalation

| Condition | Action |
|-----------|--------|
| Kernel unhealthy after restart | Check `journalctl -u arifos -n 100`; escalate to F13 if data loss suspected. |
| Constitutional floor violation triggered | Route through `arif_judge_deliberate` / `888_HOLD`. Do not override without F13. |
| VAULT999 chain gap | Per sovereign ruling 2026-06-05: pre-migration gaps (id < 62) are non-issue. Seal any new anomaly. |
| Need Caddy reload | Validate config, **STOP**, get F13 approval, then `sudo systemctl reload caddy`. |

---

## 8. Contact / Ownership

- **Sovereign:** Muhammad Arif Fazil
- **Runtime host:** `af-forge` VPS
- **Canonical repo:** `ariffazil/arifos`
