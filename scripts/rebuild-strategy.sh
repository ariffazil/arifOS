#!/bin/bash
# arifOS Container Rebuild Strategy Script
# F4 Entropy Control - Determines optimal rebuild path

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔥 arifOS Rebuild Strategy - Constitutional Approach${NC}"
echo "═══════════════════════════════════════════════════════════"

# Function to check if file changed
check_changed() {
    git diff --name-only HEAD~1 HEAD | grep -q "$1" && return 0 || return 1
}

# Function to get file hash
get_hash() {
    git rev-parse HEAD:"$1" 2>/dev/null || echo "none"
}

# Determine rebuild strategy
determine_strategy() {
    echo ""
    echo "📊 Analyzing changes..."
    echo ""
    
    local full_reforge=false
    local fast_rebuild=false
    local hot_reload=false
    local reason=""
    
    # Check for full reforge triggers
    if check_changed "Dockerfile" || check_changed "Dockerfile.optimized"; then
        full_reforge=true
        reason="Dockerfile modified"
    elif check_changed "requirements.txt"; then
        full_reforge=true
        reason="Python dependencies changed"
    elif check_changed "pyproject.toml"; then
        full_reforge=true
        reason="Project configuration changed"
    fi
    
    # Check for fast rebuild triggers
    if check_changed "core/"; then
        fast_rebuild=true
        reason="${reason}Core kernel code changed"
    fi
    
    if check_changed "arifos_mcp/" || check_changed "arifosmcp/"; then
        fast_rebuild=true
        reason="${reason}, MCP interface changed"
    fi
    
    # Check for hot reload (minor changes)
    local changed_files=$(git diff --name-only HEAD~1 HEAD | wc -l)
    if [ "$changed_files" -le 3 ] && [ "$full_reforge" = false ]; then
        hot_reload=true
        reason="Minor changes ($changed_files files)"
    fi
    
    # Output strategy
    echo "📋 CHANGE ANALYSIS:"
    echo "───────────────────"
    git diff --name-only HEAD~1 HEAD | sed 's/^/  • /'
    echo ""
    
    if [ "$full_reforge" = true ]; then
        echo -e "${RED}🔥 STRATEGY: FULL REFORGE${NC}"
        echo "   Reason: $reason"
        echo "   Time: ~10-15 minutes"
        echo "   Command: make reforge"
        echo ""
        echo "   Why full? Base image or dependencies changed."
        echo "   Layer caching will be invalidated."
        return 1
        
    elif [ "$fast_rebuild" = true ]; then
        echo -e "${YELLOW}⚡ STRATEGY: FAST REBUILD${NC}"
        echo "   Reason: $reason"
        echo "   Time: ~2-3 minutes"
        echo "   Command: make fast-deploy"
        echo ""
        echo "   Why fast? Code changed but deps are stable."
        echo "   Layer caching will accelerate build."
        return 2
        
    elif [ "$hot_reload" = true ]; then
        echo -e "${GREEN}🔄 STRATEGY: HOT RELOAD${NC}"
        echo "   Reason: $reason"
        echo "   Time: ~10 seconds"
        echo "   Command: make restart"
        echo ""
        echo "   Why hot? Minimal changes, restart sufficient."
        return 3
        
    else
        echo -e "${GREEN}✅ STRATEGY: NO ACTION${NC}"
        echo "   Reason: No code changes detected"
        echo "   Current container is up to date."
        return 0
    fi
}

# Execute strategy
execute_strategy() {
    local strategy=$1
    
    case $strategy in
        1)
            echo ""
            echo "🚀 Executing FULL REFORGE..."
            echo "═══════════════════════════════════════════════════════════"
            make reforge 2>&1
            ;;
        2)
            echo ""
            echo "⚡ Executing FAST REBUILD..."
            echo "═══════════════════════════════════════════════════════════"
            make fast-deploy 2>&1
            ;;
        3)
            echo ""
            echo "🔄 Executing HOT RELOAD..."
            echo "═══════════════════════════════════════════════════════════"
            make restart 2>&1
            ;;
        0)
            echo ""
            echo "✅ No rebuild needed."
            ;;
    esac
}

# Main
cd "$ROOT_DIR"

if [ "$1" == "--auto" ]; then
    determine_strategy
    strategy=$?
    execute_strategy $strategy
elif [ "$1" == "--check" ]; then
    determine_strategy || true
    exit 0
else
    determine_strategy
    strategy=$?
    
    echo ""
    read -p "Execute recommended strategy? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        execute_strategy $strategy
    else
        echo "Cancelled."
    fi
fi
