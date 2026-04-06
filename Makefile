# arifOS MCP Server - Constitutional Deployment Makefile
# DITEMPA BUKAN DIBERI — Forged, Not Given
# F4 Entropy Control | F5 Witness | F11 Auth

.PHONY: help build deploy fast-deploy reforge clean logs status stop restart strategy auto-deploy maintenance setup-cron

# Default target
help:
	@echo "arifOS MCP Server - Constitutional Deployment Commands"
	@echo "======================================================="
	@echo ""
	@echo "🚀 DEPLOYMENT STRATEGIES:"
	@echo "  make strategy       Analyze and recommend rebuild strategy"
	@echo "  make fast-deploy    Fast redeploy (2-3 min) - code changes only"
	@echo "  make reforge        Full rebuild (10-15 min) - deps changed"
	@echo "  make auto-deploy    Autonomous deploy based on changes"
	@echo "  make hot-restart    Instant restart - config only"
	@echo ""
	@echo "📊 MONITORING:"
	@echo "  make status         Check service status"
	@echo "  make logs           Follow logs"
	@echo "  make health         Check health endpoint"
	@echo "  make doctor         Run OpenClaw doctor"
	@echo ""
	@echo "🧹 MAINTENANCE (Low Entropy):"
	@echo "  make maintenance    Run automated maintenance"
	@echo "  make setup-cron     Install automated cron jobs"
	@echo "  make clean          Clean Docker cache and unused images"
	@echo "  make stop           Stop services"
	@echo "  make restart        Restart services"
	@echo ""
	@echo "🔧 BUILD:"
	@echo "  make build          Standard build"
	@echo "  make deploy         Full deploy with health check"

# ============================================================================
# REBUILD STRATEGIES (Constitutional Approach)
# ============================================================================

# Analyze and recommend strategy
strategy:
	@echo "🔍 Analyzing changes..."
	@chmod +x ops/scripts/rebuild-strategy.sh
	@./ops/scripts/rebuild-strategy.sh --check

# Fast deployment - uses optimized Dockerfile with layer caching
# Use when: Core code changes, tool additions, minor updates
fast-deploy:
	@echo "⚡ Fast deploying arifOS MCP (2-3 min)..."
	@echo "   Strategy: Layer cache + code only"
	@chmod +x ops/scripts/fast-deploy.sh
	@./ops/scripts/fast-deploy.sh

# Full reforge - rebuilds from scratch
# Use when: Dockerfile, requirements.txt, or base image changed
reforge:
	@echo "🔥 Full reforge arifOS MCP (10-15 min)..."
	@echo "   Strategy: Complete rebuild, no cache"
	@echo "   ⚠️  This will take longer but ensures clean state"
	@export DOCKER_BUILDKIT=1
	@docker compose down arifosmcp
	@docker rmi arifos/arifosmcp:latest 2>/dev/null || true
	@docker compose build --no-cache arifosmcp
	@docker compose up -d arifosmcp
	@echo "⏳ Waiting for health..."
	@sleep 30
	@make health

# Autonomous deployment - decides strategy automatically
auto-deploy:
	@echo "🤖 Autonomous deployment..."
	@chmod +x ops/scripts/auto-deploy.sh
	@./ops/scripts/auto-deploy.sh --auto

# Hot restart - just restart container (10s)
# Use when: Config changes only
hot-restart:
	@echo "🔄 Hot restart (10s)..."
	@GIT_SHA=$$(git rev-parse HEAD 2>/dev/null); \
	  SHORT=$${GIT_SHA:0:8}; \
	  sed -i "s/^GIT_COMMIT=.*/GIT_COMMIT=$$GIT_SHA/" .env.docker && \
	  echo "$$SHORT" > arifosmcp/.git_commit && \
	  echo "   Pinned GIT_COMMIT=$$SHORT"
	@GIT_COMMIT=$$(git rev-parse HEAD 2>/dev/null) docker compose up -d --no-deps --force-recreate arifosmcp
	@sleep 5
	@make health

# Development mode - mounts code for instant changes
dev:
	@echo "🔧 Starting in development mode..."
	@docker compose -f docker-compose.yml -f docker-compose.override.yml up -d arifosmcp
	@echo "Code changes will be reflected immediately (no rebuild needed)"

# ============================================================================
# MONITORING & DIAGNOSTICS
# ============================================================================

# Check status
status:
	@echo "📊 Container Status:"
	@docker ps --filter "name=arifosmcp" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "💾 Resource Usage:"
	@docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" arifosmcp 2>/dev/null || echo "Container not running"

# Health check
health:
	@echo "🏥 Health Check:"
	@curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health

# OpenClaw doctor
doctor:
	@echo "🏥 Running OpenClaw Doctor..."
	@docker exec openclaw openclaw doctor 2>&1 || echo "Doctor not available"

# Follow logs
logs:
	@docker logs -f arifosmcp

# ============================================================================
# LOW-ENTROPY MAINTENANCE (F4 Entropy Control)
# ============================================================================

# Automated maintenance - minimizes manual intervention
maintenance:
	@echo "🔧 Running low-entropy maintenance..."
	@chmod +x ops/scripts/low-entropy-cron.sh
	@./ops/scripts/low-entropy-cron.sh all

# Setup automated cron jobs
setup-cron:
	@echo "⚙️  Setting up automated cron jobs..."
	@echo "# arifOS Low-Entropy Maintenance" | sudo tee /etc/cron.d/arifos-maintenance
	@echo "*/5 * * * * root /root/arifosmcp/ops/scripts/low-entropy-cron.sh health >> /var/log/arifos-cron.log 2>&1" | sudo tee -a /etc/cron.d/arifos-maintenance
	@echo "0 */6 * * * root /root/arifosmcp/ops/scripts/low-entropy-cron.sh all >> /var/log/arifos-cron.log 2>&1" | sudo tee -a /etc/cron.d/arifos-maintenance
	@echo "✅ Cron jobs installed:"
	@echo "   • Health check: every 5 minutes"
	@echo "   • Full maintenance: every 6 hours"

# ============================================================================
# BUILD & DEPLOY (Legacy/Standard)
# ============================================================================

# Standard build
build:
	@echo "📦 Building arifOS MCP..."
	@export DOCKER_BUILDKIT=1
	@docker build -f Dockerfile.optimized -t arifos/arifosmcp:latest .

# Full deployment with health check
deploy: build
	@echo "🔄 Deploying..."
	@docker compose up -d arifosmcp
	@echo "⏳ Waiting for health..."
	@sleep 5
	@curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health

# Stop services
stop:
	@echo "🛑 Stopping arifOS MCP..."
	@docker compose stop arifosmcp

# Restart services
restart:
	@echo "🔄 Restarting arifOS MCP..."
	@docker compose restart arifosmcp
	@sleep 3
	@make health

# Clean Docker cache
clean:
	@echo "🧹 Cleaning Docker..."
	@docker system prune -f
	@docker builder prune -f

# ============================================================================
# DECISION TREE (When to use what)
# ============================================================================
#
# DID YOU CHANGE...?                    USE THIS COMMAND
# ───────────────────────────────────────────────────────────────
# Dockerfile/requirements.txt           make reforge    (10-15 min)
# Core code (core/, arifosmcp/)         make fast-deploy (2-3 min)
# Config only (.env, yaml)              make hot-restart (10s)
# Not sure what changed                 make strategy   (analysis)
# Want it to decide automatically       make auto-deploy (smart)
# Just need a quick restart             make restart    (30s)
#
# AUTONOMOUS MODE:
#   make setup-cron → Enables auto-healing & auto-deploy
#
# ============================================================================

# ============================================================================
# ZERO-CHAOS AUTOMATED DEPLOYMENT (New - Recommended)
# ============================================================================
# These commands use ops/scripts/deploy.py for safe, reversible deployments

# Deploy to staging (automated, no approval needed)
deploy-staging:
	@echo "🚀 Deploying to STAGING..."
	@python ops/scripts/deploy.py --environment staging

# Deploy to production (requires manual confirmation)
deploy-production:
	@echo "🚀 Deploying to PRODUCTION..."
	@echo "⚠️  This will affect the live system at arifosmcp.arif-fazil.com"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] && python ops/scripts/deploy.py --environment production || echo "Cancelled"

# Dry run production deploy (see what would happen)
deploy-dry-run:
	@echo "🔍 Dry-run production deployment..."
	@python ops/scripts/deploy.py --environment production --dry-run

# Verify current deployment health
deploy-verify:
	@echo "✅ Verifying deployment health..."
	@curl -s https://arifosmcp.arif-fazil.com/health | python3 -m json.tool 2>/dev/null || curl -s https://arifosmcp.arif-fazil.com/health

# Deploy to GitHub Actions (no local setup needed)
deploy-gh:
	@echo "Triggering GitHub Actions deployment..."
	@gh workflow run deploy-automated.yml --field environment=staging

# Quick reference for AI agents
deploy-help:
	@echo ""
	@echo "🤖 AI AGENT DEPLOYMENT CHEATSHEET"
	@echo "=================================="
	@echo ""
	@echo "For STAGING (automatic):"
	@echo "  make deploy-staging"
	@echo "  or: python ops/scripts/deploy.py"
	@echo ""
	@echo "For PRODUCTION (needs care):"
	@echo "  Step 1: Dry run first"
	@echo "    make deploy-dry-run"
	@echo ""
	@echo "  Step 2: If dry run looks good, deploy"
	@echo "    make deploy-production"
	@echo ""
	@echo "  Step 3: Verify after deploy"
	@echo "    make deploy-verify"
	@echo ""
	@echo "Via GitHub Actions (easiest):"
	@echo "  make deploy-gh"
	@echo ""
	@echo "Emergency rollback:"
	@echo "  ssh root@arif-fazil.com 'cd /root/arifosmcp && docker-compose restart'"
	@echo ""

# ============================================================================
