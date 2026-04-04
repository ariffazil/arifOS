# arifOS Monitoring & Backup Setup

**Last Updated:** 2026-02-18  
**VPS:** Hostinger (72.62.71.199)  
**Container:** arifosmcp_server

## Automated Monitoring

### Health Checks
- **Script:** `/root/arifOS/scripts/health-check.sh`
- **Schedule:** Every 5 minutes via cron
- **Actions:**
  - Checks if container is running; starts if stopped
  - Checks Docker health status; restarts if unhealthy
- **Logs:** `/root/arifOS/data/healthcheck.log`

### Data Backups
- **Script:** `/root/arifOS/scripts/backup-data.sh`
- **Schedule:** Daily at 02:00 UTC via cron
- **Backup Location:** `/root/backups/arifos/`
- **Retention:** Last 7 backups (daily)
- **Logs:** `/root/arifOS/data/backup.log`

### Cron Jobs
```bash
# View current jobs
crontab -l

# Edit manually
crontab -e
```

Current cron entries:
```
0 2 * * * /root/arifOS/scripts/backup-data.sh >> /root/arifOS/data/backup.log 2>&1
*/5 * * * * /root/arifOS/scripts/health-check.sh >> /root/arifOS/data/healthcheck.log 2>&1
```

## Docker Log Rotation
Configured in `deployment/docker-compose.vps.yml`:
```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```
Container logs are automatically rotated (max 3 files × 10MB each).

## Manual Tasks

### Cloudflare DNS Cleanup
**Obsolete Record:** `aaamcp` CNAME pointing to Railway (old deployment)

**Steps to Delete:**
1. Log into Cloudflare Dashboard
2. Select domain `arif-fazil.com`
3. Navigate to **DNS → Records**
4. Find CNAME record `aaamcp` (value: `aaamcp.up.railway.app`)
5. Click **Delete** and confirm

**Verification:**
```bash
dig aaamcp.arif-fazil.com CNAME
```
Should return no result after propagation (up to 5 minutes).

### Container Management
```bash
# View logs
docker logs -f arifosmcp_server

# View resource usage
docker stats arifosmcp_server

# Restart container
cd /root/arifOS && docker-compose -f deployment/docker-compose.vps.yml restart

# Update deployment (after git pull)
cd /root/arifOS && docker-compose -f deployment/docker-compose.vps.yml down
git pull origin main
docker-compose -f deployment/docker-compose.vps.yml up -d --build
```

## Alerting (Optional)
Currently not configured. To add email alerts:
1. Install and configure `mailutils`
2. Modify health-check.sh to send email on failure

For webhook alerts (Discord/Telegram):
- Add `curl` call in health-check.sh with appropriate webhook URL

## Troubleshooting

### Health Check Fails
1. Check container logs: `docker logs arifosmcp_server`
2. Verify ports 8888/8889 are free: `netstat -tlnp | grep :8888`
3. Check Nginx configuration: `nginx -t`

### Backup Fails
1. Ensure `/root/backups/arifos` directory exists and is writable
2. Check disk space: `df -h`
3. Verify data directory permissions: `ls -la /root/arifOS/data`

### DNS Issues
If `arifosmcp.arif-fazil.com` fails to resolve:
1. Verify Cloudflare proxy status (orange cloud icon)
2. Check A records point to `72.62.71.199`
3. Ensure SSL/TLS encryption mode is "Full" (recommended)

## Support
- **GitHub Issues:** https://github.com/ariffazil/arifOS/issues
- **Deployment Docs:** `DEPLOYMENT.md`
- **Architecture:** `ARCHITECTURE.md`
