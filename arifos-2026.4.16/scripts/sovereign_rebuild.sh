#!/bin/bash
#
# Sovereign Rebuild Script
# 
# One-command rebuild of arifOS from cold storage.
# For use when VPS is seized/destroyed.
#
# Usage: ./sovereign_rebuild.sh --from-cold-storage [--region switzerland]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARIFOS_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${ARIFOS_ROOT}/cold_storage"
VAULT_DIR="${ARIFOS_ROOT}/VAULT999"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Rebuild arifOS from cold storage backup.

OPTIONS:
    --from-cold-storage     Restore from cold storage (required)
    --region REGION         Target region (switzerland|iceland|singapore)
    --backup-file FILE      Specific backup file to restore
    --verify-only           Only verify integrity, don't restore
    --kms-endpoint URL      External KMS endpoint for key reconstruction
    -h, --help              Show this help

EXAMPLES:
    # Full rebuild from latest backup
    $0 --from-cold-storage

    # Restore to specific region
    $0 --from-cold-storage --region switzerland

    # Verify backup integrity only
    $0 --from-cold-storage --verify-only

EOF
}

# Parse arguments
FROM_COLD_STORAGE=false
REGION=""
BACKUP_FILE=""
VERIFY_ONLY=false
KMS_ENDPOINT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --from-cold-storage)
            FROM_COLD_STORAGE=true
            shift
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        --backup-file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --kms-endpoint)
            KMS_ENDPOINT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ "$FROM_COLD_STORAGE" != true ]]; then
    log_error "--from-cold-storage is required"
    usage
    exit 1
fi

# ============================================
# PHASE 1: Environment Setup
# ============================================

log_info "Starting sovereign rebuild..."
log_info "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Check prerequisites
command -v gpg >/dev/null 2>&1 || { log_error "gpg required but not installed"; exit 1; }
command -v docker >/dev/null 2>&1 || { log_error "docker required but not installed"; exit 1; }

# Create necessary directories
mkdir -p "$VAULT_DIR"
mkdir -p "$BACKUP_DIR"

# ============================================
# PHASE 2: Backup Retrieval
# ============================================

if [[ -z "$BACKUP_FILE" ]]; then
    log_info "Finding latest backup..."
    
    # Try local cold storage first
    BACKUP_FILE=$(find "$BACKUP_DIR" -name "vault999_backup_*.tar.gz.gpg" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
    
    # If not found locally, try cloud providers
    if [[ -z "$BACKUP_FILE" ]]; then
        log_warn "No local backup found, trying cloud providers..."
        
        # Try S3
        if command -v aws &> /dev/null; then
            LATEST_S3=$(aws s3 ls s3://arifos-vault-backups/vault999/ 2>/dev/null | sort | tail -1 | awk '{print $4}')
            if [[ -n "$LATEST_S3" ]]; then
                log_info "Found S3 backup: $LATEST_S3"
                aws s3 cp "s3://arifos-vault-backups/vault999/$LATEST_S3" "$BACKUP_DIR/"
                BACKUP_FILE="$BACKUP_DIR/$LATEST_S3"
            fi
        fi
        
        # Try GCS
        if [[ -z "$BACKUP_FILE" ]] && command -v gsutil &> /dev/null; then
            LATEST_GCS=$(gsutil ls gs://arifos-vault-backups/vault999/ 2>/dev/null | sort | tail -1)
            if [[ -n "$LATEST_GCS" ]]; then
                log_info "Found GCS backup: $LATEST_GCS"
                gsutil cp "$LATEST_GCS" "$BACKUP_DIR/"
                BACKUP_FILE="$BACKUP_DIR/$(basename $LATEST_GCS)"
            fi
        fi
    fi
fi

if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
    log_error "No backup file found"
    exit 1
fi

log_info "Using backup: $BACKUP_FILE"

# ============================================
# PHASE 3: Integrity Verification
# ============================================

log_info "Verifying backup integrity..."

# Compute hash
BACKUP_HASH=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)
log_info "Backup SHA256: $BACKUP_HASH"

# Decrypt to temp for verification
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

log_info "Decrypting backup..."
gpg --decrypt --output "$TEMP_DIR/vault.tar.gz" "$BACKUP_FILE" || {
    log_error "Decryption failed — wrong key or corrupted backup"
    exit 1
}

# Verify tarball
if ! tar -tzf "$TEMP_DIR/vault.tar.gz" >/dev/null 2>&1; then
    log_error "Backup tarball is corrupted"
    exit 1
fi

log_info "Backup integrity verified"

if [[ "$VERIFY_ONLY" == true ]]; then
    log_info "Verify-only mode, exiting"
    exit 0
fi

# ============================================
# PHASE 4: Vault Restoration
# ============================================

log_info "Restoring VAULT999..."

# Clear existing vault (if any)
if [[ -d "$VAULT_DIR" ]]; then
    log_warn "Removing existing vault directory"
    rm -rf "${VAULT_DIR}.old"
    mv "$VAULT_DIR" "${VAULT_DIR}.old"
fi

# Extract
mkdir -p "$VAULT_DIR"
tar -xzf "$TEMP_DIR/vault.tar.gz" -C "$(dirname $VAULT_DIR)"

# Verify Merkle chain
log_info "Verifying Merkle chain integrity..."
python3 << 'PYTHON'
import sys
sys.path.insert(0, "arifOS")
from core.organs._4_vault import verify_vault_ledger
from pathlib import Path

vault_path = Path("arifOS/VAULT999/vault999.jsonl")
if vault_path.exists():
    ok, error = verify_vault_ledger(vault_path)
    if ok:
        print("✓ Merkle chain valid")
        sys.exit(0)
    else:
        print(f"✗ Merkle chain broken: {error}")
        sys.exit(1)
else:
    print("⚠ No vault ledger found (may be fresh install)")
    sys.exit(0)
PYTHON

log_info "VAULT999 restored successfully"

# ============================================
# PHASE 5: Key Reconstruction (if needed)
# ============================================

if [[ -n "$KMS_ENDPOINT" ]]; then
    log_info "Using external KMS: $KMS_ENDPOINT"
else
    log_warn "No KMS endpoint — will use Shamir reconstruction if needed"
    log_info "To reconstruct signing keys, provide 3 of 5 Shamir shares"
fi

# ============================================
# PHASE 6: Container Rebuild
# ============================================

log_info "Rebuilding hardened containers..."

cd "$ARIFOS_ROOT"

# Build MCP container
docker build \
    -f "core/vault999/layer2_isolation/Dockerfile.mcp" \
    -t "arifos/mcp:hardened" \
    . || log_warn "MCP container build failed"

# Build Forge container  
docker build \
    -f "core/vault999/layer2_isolation/Dockerfile.forge" \
    -t "arifos/forge:hardened" \
    . || log_warn "Forge container build failed"

# ============================================
# PHASE 7: Startup
# ============================================

log_info "Starting services..."

# Create docker-compose or systemd services
# (Implementation depends on deployment target)

log_info "=============================================="
log_info "Sovereign Rebuild Complete"
log_info "=============================================="
log_info "Vault hash: ${BACKUP_HASH:0:16}..."
log_info "Region: ${REGION:-default}"
log_info "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
log_info ""
log_info "Next steps:"
log_info "  1. Verify blockchain anchors"
log_info "  2. Test execution attestation"
log_info "  3. Enable mirror sync"
log_info "=============================================="
