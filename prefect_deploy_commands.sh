
# ═══════════════════════════════════════════════════════════════════════
# PREFECT HORIZON DEPLOYMENT COMMANDS
# ═══════════════════════════════════════════════════════════════════════

# 1. Login to Prefect Cloud
prefect cloud login

# 2. Set workspace (if needed)
prefect cloud workspace set --workspace "arifos/arifos"

# 3. Create managed work pool for arifOS
prefect work-pool create arifos-pool --type prefect:managed

# 4. Deploy the server (after env vars are configured in UI)
prefect deploy arifosmcp/integrations/prefect/tasks.py:constitutional_flow \
    --name arifos-mcp-server \
    --pool arifos-pool \
    --description "Constitutional AI Governance Server"

# 5. Check deployment status
prefect deployment ls

# 6. View server logs
prefect server logs

# ═══════════════════════════════════════════════════════════════════════
# HORIZON UI URL
# ═══════════════════════════════════════════════════════════════════════
# Configure environment variables at:
# https://horizon.prefect.io/arifos/servers/arifOS/settings/environment-variables

