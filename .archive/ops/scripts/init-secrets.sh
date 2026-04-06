#!/bin/bash
# init-secrets.sh — Initialize Production Secrets (Linux/macOS)
#
# Constitutional Floor: F11 (Command Authority)
# Purpose: Generate and secure ARIFOS_GOVERNANCE_SECRET for production
#
# Usage:
#   sudo ./scripts/init-secrets.sh [-d /etc/arifos/secrets]
#
# This script:
#   1. Creates a secure secrets directory with restricted permissions (700)
#   2. Generates a cryptographically secure 64-character governance secret
#   3. Sets appropriate file permissions (read-only, root only)
#   4. Outputs environment variable configuration

set -euo pipefail

# Configuration
SECRETS_DIR="${SECRETS_DIR:-/etc/arifos/secrets}"
SECRET_LENGTH=64
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--directory)
            SECRETS_DIR="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [-d SECRETS_DIR] [-f]"
            echo "  -d, --directory   Secrets directory (default: /etc/arifos/secrets)"
            echo "  -f, --force       Overwrite existing secrets"
            echo "  -h, --help        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ASCII banner
cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║     arifOS — Constitutional Secret Initialization            ║
║     F11: Command Authority — Ditempa Bukan Diberi            ║
╚══════════════════════════════════════════════════════════════╝
EOF

# Check if running as root for system-wide secrets
if [[ $EUID -ne 0 ]] && [[ "$SECRETS_DIR" == /etc/* || "$SECRETS_DIR" == /usr/* ]]; then
    echo "Error: Root privileges required for system-wide secrets directory: $SECRETS_DIR"
    echo "Run with: sudo $0"
    exit 1
fi

# Create secrets directory
echo "[1/5] Creating secrets directory: $SECRETS_DIR"
mkdir -p "$SECRETS_DIR"

# Set restrictive permissions (owner only)
echo "[2/5] Setting restrictive permissions (700)..."
chmod 700 "$SECRETS_DIR"
chown root:root "$SECRETS_DIR" 2>/dev/null || chown "$(whoami):$(whoami)" "$SECRETS_DIR"

# Function to generate secure secret
generate_secret() {
    local length="${1:-64}"
    tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c "$length"
}

# Function to write secret with restricted permissions
write_secret() {
    local file="$1"
    local secret="$2"
    
    printf '%s' "$secret" > "$file"
    chmod 600 "$file"
    chown root:root "$file" 2>/dev/null || chown "$(whoami):$(whoami)" "$file"
}

# Generate and write governance secret
echo "[3/5] Generating governance secret (${SECRET_LENGTH} chars)..."
GOVERNANCE_FILE="$SECRETS_DIR/governance.secret"

if [[ -f "$GOVERNANCE_FILE" ]] && [[ "$FORCE" != "true" ]]; then
    echo "      ⚠ Governance secret already exists at: $GOVERNANCE_FILE"
    read -p "      Overwrite? (yes/no) " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "      Cancelled. Existing secret preserved."
    else
        write_secret "$GOVERNANCE_FILE" "$(generate_secret $SECRET_LENGTH)"
        echo "      ✓ Governance secret overwritten"
    fi
else
    write_secret "$GOVERNANCE_FILE" "$(generate_secret $SECRET_LENGTH)"
    echo "      ✓ Governance secret written"
fi

# Generate session secret
echo "[4/5] Generating session secret..."
SESSION_FILE="$SECRETS_DIR/session.secret"
write_secret "$SESSION_FILE" "$(generate_secret $SECRET_LENGTH)"
echo "      ✓ Session secret written"

# Generate PostgreSQL password
echo "      Generating PostgreSQL password..."
PG_FILE="$SECRETS_DIR/postgres.password"
write_secret "$PG_FILE" "$(generate_secret 32)"
echo "      ✓ PostgreSQL password written"

# Generate Redis password
echo "      Generating Redis password..."
REDIS_FILE="$SECRETS_DIR/redis.password"
write_secret "$REDIS_FILE" "$(generate_secret 32)"
echo "      ✓ Redis password written"

# Verification
echo "[5/5] Verifying secrets..."
VERIFIED=true

for file in "$GOVERNANCE_FILE" "$SESSION_FILE" "$PG_FILE" "$REDIS_FILE"; do
    if [[ -f "$file" ]]; then
        length=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        if [[ $length -ge 32 ]]; then
            echo "      ✓ $(basename "$file"): ${length} chars"
        else
            echo "      ✗ $(basename "$file"): Too short (${length} chars)"
            VERIFIED=false
        fi
    else
        echo "      ✗ $(basename "$file"): Missing"
        VERIFIED=false
    fi
done

# Output configuration
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  SECRETS CONFIGURED — Add to environment:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  # Shell environment variables:"
echo "  export ARIFOS_GOVERNANCE_SECRET_FILE=$GOVERNANCE_FILE"
echo "  export ARIFOS_SESSION_SECRET_FILE=$SESSION_FILE"
echo "  export POSTGRES_PASSWORD_FILE=$PG_FILE"
echo "  export REDIS_PASSWORD_FILE=$REDIS_FILE"
echo ""
echo "  # Docker Compose .env file:"
echo "  ARIFOS_GOVERNANCE_SECRET_FILE=$GOVERNANCE_FILE"
echo "  ARIFOS_SESSION_SECRET_FILE=$SESSION_FILE"
echo "  POSTGRES_PASSWORD_FILE=$PG_FILE"
echo "  REDIS_PASSWORD_FILE=$REDIS_FILE"
echo ""
echo "  # Docker secret creation commands:"
echo "  docker secret create arifos_governance_secret_v2026 $GOVERNANCE_FILE"
echo "  docker secret create arifos_session_secret_v2026 $SESSION_FILE"
echo "  docker secret create postgres_password $PG_FILE"
echo "  docker secret create redis_password $REDIS_FILE"
echo ""
echo "═══════════════════════════════════════════════════════════════"

if [[ "$VERIFIED" == "true" ]]; then
    echo "  ✓ ALL SECRETS VERIFIED — F11 Continuity Guaranteed"
else
    echo "  ✗ VERIFICATION FAILED — Check errors above"
    exit 1
fi

echo ""
echo "Motto: Ditempa Bukan Diberi — Forged, Not Given"
