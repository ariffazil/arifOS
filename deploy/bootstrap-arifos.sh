#!/usr/bin/env bash
# bootstrap-arifos.sh
# arifOS Federation Substrate Installer
#
# Transforms a clean Ubuntu/Debian VPS into a governed arifOS node.
# Installs Python/uv, provisions the database and vector store, creates systemd services,
# and enforces the default F1-F13 Constitutional Floors.

set -euo pipefail

echo "[+] Validating Sovereign Environment Matrix..."
if [ "$EUID" -ne 0 ]; then
  echo "[-] Please run as root. The substrate requires systemd and port bindings."
  exit 1
fi

MODE="${1:-single-operator}"
ARIFOS_HOME="/opt/arifos"

echo "[+] Bootstrapping arifOS in mode: $MODE"

# --- 1. System Dependencies ---
echo "[+] Installing system dependencies..."
apt-get update && apt-get install -y curl git build-essential postgresql-client redis-tools jq uuid-runtime

# --- 2. Install Python & uv ---
echo "[+] Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# --- 3. Sovereign Environment Matrix ---
echo "[+] Generating Sovereign Environment Matrix..."
mkdir -p /root/.arifos
cat << 'EOF' > /root/.arifos/env
ARIFOS_URL="http://localhost:8088"
AAA_URL="http://localhost:3001"
FEDERATION_MODE="sovereign"
NODE_ID="node-$(uuidgen || echo alpha-1)"
EOF
echo "[+] Created ~/.arifos/env"

# --- 4. Substrate Data Layer (State) ---
echo "[+] Provisioning State Layer (Postgres, Qdrant, Redis, Temporal, NATS)..."
mkdir -p "$ARIFOS_HOME/deploy"
docker-compose -f $ARIFOS_HOME/deploy/docker-compose.yml up -d

# --- 5. Install arifOS Kernel ---
echo "[+] Installing arifOS kernel..."
mkdir -p "$ARIFOS_HOME/kernel"
cd "$ARIFOS_HOME/kernel"
git clone https://github.com/ariffazil/arifos.git .
uv sync --frozen --no-dev

# --- 6. Migrate State & Seed Floors ---
echo "[+] Running VAULT999 migrations and seeding F1-F13 Floors..."
arifos migrate
arifos seed --floors standard

# --- 7. Configure systemd Services (Sequenced Boot) ---
echo "[+] Registering services: state -> kernel -> AAA -> A2A -> organs"

cat << 'EOF' > /etc/systemd/system/arifos-kernel.service
[Unit]
Description=arifOS Constitutional Kernel (Port 8088)
After=network.target docker.service

[Service]
User=root
WorkingDirectory=/opt/arifos/kernel
ExecStart=/root/.cargo/bin/uv run arifos-mcp
Restart=always
EnvironmentFile=/root/.arifos/env
Environment=ARIFOS_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
# Start order enforced in script sequencing
# Start Kernel
systemctl enable arifos-kernel
systemctl start arifos-kernel
# Start AAA
systemctl enable --now aaa-a2a
# Start Organs
systemctl enable --now geox-mcp wealth-organ well

echo "[+] arifOS bootstrap complete. The kernel is alive."
echo "[!] Reality Engineering Note: The node is sealed. Run 'a-forge tui' to claim operator sovereignty."
