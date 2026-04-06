#!/bin/bash
# Health check for arifOS container, restart if unhealthy
set -e

CONTAINER_NAME="arifosmcp"
LOG_FILE="/root/arifOS/data/healthcheck.log"

echo "[$(date)] Health check for $CONTAINER_NAME" >> "$LOG_FILE"

# Check if container is running
if ! docker ps --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "Container not running, starting..." >> "$LOG_FILE"
    cd /root/arifOS && docker-compose -f deployment/docker-compose.vps.yml up -d
    exit 0
fi

# Check health status
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")

if [ "$HEALTH_STATUS" = "unhealthy" ]; then
    echo "Container unhealthy, restarting..." >> "$LOG_FILE"
    docker restart "$CONTAINER_NAME"
fi

echo "[$(date)] Health status: $HEALTH_STATUS" >> "$LOG_FILE"
