

# Deploying arifOS MCP Server on Hostinger VPS: Complete Technical Guide

## 1. Pre-Deployment Assessment

### 1.1 Current Infrastructure Status

#### 1.1.1 VPS Specifications (Hostinger KVM 2)

Your **Hostinger KVM 2** VPS provides a robust foundation for production MCP server deployment. The **Ubuntu 25.10** operating system delivers modern kernel features and container-optimized performance, though you should note its non-LTS status implies more frequent upgrade cycles compared to Ubuntu LTS releases. The hardware allocation of **2 CPU cores** and **8 GB RAM** strikes an optimal balance for the Trinity Protocol's dual-process architecture, where SSE and HTTP transport servers operate concurrently within a single containerized environment.

Current utilization metrics indicate healthy operational margins: **35% CPU usage** leaves substantial headroom for traffic spikes, while **48% memory consumption** (approximately 3.84 GB of 8 GB) accommodates the sentence-transformers embedding model's ~2 GB footprint alongside FastMCP runtime, Nginx, and system overhead. The **100 GB SSD storage** at **66% utilization** (34 GB free) provides years of log retention capacity without immediate expansion needs. Network positioning in **Malaysia-Kuala Lumpur** with **8 TB monthly bandwidth**—currently consuming merely **0.111 TB (1.4%)**—ensures geographic accessibility for Asia-Pacific users with massive scaling headroom.

| Resource | Specification | Current Utilization | Available Headroom | Assessment |
|----------|-------------|---------------------|-------------------|------------|
| **Operating System** | Ubuntu 25.10 | — | — | Modern, container-optimized |
| **CPU** | 2 cores | 35% | 65% | Adequate for dual-transport load |
| **Memory** | 8 GB | 48% (3.84 GB) | 52% (4.16 GB) | Comfortable buffer for ML model + traffic |
| **Storage** | 100 GB SSD | 66 GB (66%) | 34 GB (34%) | Sufficient for logs and growth |
| **Bandwidth** | 8 TB/month | 0.111 TB (1.4%) | 7.889 TB (98.6%) | Massive unused capacity |
| **IPv4 Address** | 72.62.71.199 | Static | — | Malaysia-Kuala Lumpur region |
| **Snapshots** | 2 pre-configured | — | — | Critical rollback capability |
| **Uptime** | 4 days 23 hours | — | — | Demonstrates stability |

The **2 pre-existing snapshots** in your Hostinger control panel provide essential safety infrastructure for point-in-time recovery. Your **auto-renewal status is active** with expiration in **2027-02-03**, ensuring long-term service continuity. The single configured SSH key alongside root password access offers flexible authentication pathways, with key-based authentication preferred for operational security and CI/CD automation.

#### 1.1.2 Existing Deployment State

Your arifOS MCP server is **already operational** on this infrastructure, validating the architecture's feasibility and providing reference behavior for troubleshooting. The **Trinity Protocol** implementation runs within the **`arifosmcp_server`** Docker container, exposing **dual transports simultaneously**: **SSE on port 8088→8080** for real-time streaming clients, and **HTTP/StreamableHTTP on port 8889→8089** for request-response interactions. This architectural pattern enables broad client compatibility—from Claude Desktop's native SSE support to Perplexity and Antigravity's HTTP preferences—without forcing transport selection at deployment time.

The **Nginx reverse proxy** handles SSL termination and intelligent request routing, presenting unified HTTPS on port 443 while internally dispatching `/sse` and `/mcp` paths to their respective container ports. **Cloudflare DNS integration** at `arifosmcp.arif-fazil.com` provides DDoS mitigation and edge optimization, though with acknowledged trade-offs regarding SSE long-polling stability that require monitoring and potential configuration adjustment.

### 1.2 Architecture Overview

#### 1.2.1 Traffic Flow Topology

Your complete request lifecycle traverses **four infrastructure layers**, each contributing specific security, performance, or protocol adaptation functions. Understanding this flow is essential for troubleshooting, capacity planning, and security auditing.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CLIENT LAYER                                                           │
│  Claude Desktop / Perplexity / Antigravity / Custom MCP Clients         │
│  HTTPS Request → arifosmcp.arif-fazil.com:443                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CLOUDFLARE EDGE LAYER (DNS + Proxy)                                    │
│  • DDoS mitigation, WAF rules, bot management                           │
│  • TLS 1.3 handshake, certificate management (if Proxied ☁️)            │
│  • Geographic routing, edge caching                                     │
│  ⚠️ Trade-off: 100s timeout may disrupt SSE long-polling                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  HOSTINGER VPS — NGINX REVERSE PROXY (72.62.71.199)                     │
│  SSL Termination: Let's Encrypt or Cloudflare Origin Certificate        │
│  ┌─────────────────┐    ┌─────────────────┐                             │
│  │  Location /sse  │ →  │  127.0.0.1:8088 │  (SSE: 86400s timeout)      │
│  │  Location /mcp  │ →  │  127.0.0.1:8889 │  (HTTP: 300s timeout)       │
│  │  Location /health│ → │  127.0.0.1:8088 │  (Health monitoring)        │
│  └─────────────────┘    └─────────────────┘                             │
│  Protocol: TLS 1.2+, HTTP/2 enabled                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DOCKER CONTAINER: arifosmcp_server                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  PORT MAPPING: 8088:8080 (SSE) | 8889:8089 (HTTP)              │    │
│  │                                                                 │    │
│  │  TRINITY PROTOCOL — start-trinity.sh                            │    │
│  │  ┌─────────────────┐      ┌─────────────────┐                   │    │
│  │  │  SSE Server     │      │  HTTP Server    │                   │    │
│  │  │  python -m aaa_mcp    │      │  python -m aaa_mcp    │                   │    │
│  │  │  Port 8080      │      │  Port 8089      │                   │    │
│  │  │  FastMCP 2.14.5 │      │  FastMCP 2.14.5 │                   │    │
│  │  └─────────────────┘      └─────────────────┘                   │    │
│  │         ↑                          ↑                            │    │
│  │         └──────────┬───────────────┘                            │    │
│  │                    Shared: sentence-transformers (~2GB),        │    │
│  │                          constitutional governance (13 floors)  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

The **Nginx layer's protocol-specific optimizations** are critical for reliable operation. SSE connections require **buffering disabled**, **caching disabled**, and **24-hour read timeouts** to maintain persistent streams, while HTTP connections use conventional settings for efficient request-response handling. This differentiation—implemented through separate location blocks—ensures each transport performs optimally without compromise.

#### 1.2.2 Trinity Protocol Components

The **Trinity Protocol** embodies arifOS's architectural philosophy of **parallel verification paths**—mirroring the constitutional AI governance framework's tripartite structure (Δ Mind, Ω Heart, Ψ Soul) in infrastructure design. The **`start-trinity.sh`** entrypoint orchestrates concurrent Python process execution, launching independent FastMCP server instances that share common state and dependencies while maintaining transport-specific optimizations.

| Component | Internal Port | External Port | Transport Characteristics | Optimal Client |
|-----------|--------------|---------------|--------------------------|--------------|
| **SSE Server** | 8080 | 8088 | Persistent connection, server-push, unidirectional streaming | Claude Desktop, real-time applications |
| **HTTP/StreamableHTTP Server** | 8089 | 8889 | Request-response, stateless-compatible, optional response streaming | Perplexity, Antigravity, API integrations |

Both servers bind to the **FastMCP 2.14.5 framework** with explicit version constraint **`<3.0.0`** to prevent breaking API changes. They share the **sentence-transformers embedding model** (approximately 2 GB RAM) for semantic operations in constitutional floor validation, and unified **`.env.docker` configuration** for API keys and behavioral parameters. The **13 constitutional floors**—from F1 Amanah (Trust) to F13 Unity (Tawhid)—apply uniformly across transports, ensuring consistent AI governance regardless of client connection method.

## 2. System Preparation & Dependencies

### 2.1 SSH Access & Initial Setup

#### 2.1.1 Connection Parameters

Establish administrative access to your VPS using the provided credentials. The **SSH target** is `root@72.62.71.199` with authentication via **root password** (available through Hostinger control panel) or your **pre-configured SSH key**. For operational efficiency and security, prefer key-based authentication:

```bash
# Basic connection
ssh root@72.62.71.199

# Recommended: Configure SSH client for convenience
# Add to ~/.ssh/config:
Host arifos-vps
    HostName 72.62.71.199
    User root
    IdentityFile ~/.ssh/your_key
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

**First-time connection verification:** Confirm the host key fingerprint against Hostinger's documentation to prevent man-in-the-middle attacks. The `ServerAlive` parameters prevent session timeout during long-running operations like Docker image builds.

#### 2.1.2 System Hardening

Prepare your Ubuntu 25.10 environment with security updates and essential tooling. The compound command sequences efficiency while ensuring completeness:

```bash
# Update package index and apply security patches
apt update && apt upgrade -y

# Install deployment essentials
apt install -y curl git nginx certbot python3-certbot-nginx ufw
```

| Package | Function | Deployment Role |
|---------|----------|---------------|
| **curl** | HTTP client utility | API testing, downloads, health checks |
| **git** | Distributed version control | Source code acquisition from GitHub |
| **nginx** | High-performance web server | Reverse proxy, SSL termination, load balancing |
| **certbot** | Let's Encrypt ACME client | Automated TLS certificate issuance and renewal |
| **python3-certbot-nginx** | Nginx plugin for Certbot | Seamless certificate deployment with zero-downtime reload |
| **ufw** | Uncomplicated Firewall | Host-level network access control |

These packages establish the complete deployment pipeline—from source retrieval through secure public service exposure—with each component selected for production maturity and active security maintenance.

### 2.2 Docker Environment Verification

#### 2.2.1 Docker Installation Check

Verify container runtime presence and version compatibility before proceeding:

```bash
docker --version          # Target: 20.10+ for modern features
docker compose version    # Target: v2.0+ for plugin architecture
```

**Version compatibility matters:** Docker Engine 20.10+ ensures support for BuildKit improvements, improved seccomp profiles, and modern Dockerfile syntax. The **Compose V2 plugin** (space-separated `docker compose` command) replaces the legacy Python-based `docker-compose` binary, providing faster execution and consistent CLI integration.

#### 2.2.2 Docker Installation (if missing)

If Docker is absent, install using the official convenience script:

```bash
# Download and execute Docker installation script
curl -fsSL https://get.docker.com | sh

# Enable and start Docker service
systemctl enable --now docker
```

The `-fsSL` flags ensure **fail-fast behavior** (`-f`), **silent operation** (`-s`), **error visibility** (`-S`), and **redirect following** (`-L`). Post-installation, `systemctl enable --now` combines persistent boot-time registration with immediate activation. Verify functionality with `docker run hello-world` before proceeding.

## 3. Application Deployment

### 3.1 Repository & Configuration

#### 3.1.1 Source Code Acquisition

Clone the arifOS repository to establish your working environment:

```bash
cd /root
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
```

The **`/root/arifOS`** path follows convention for system-level service deployments, with root ownership eliminating permission complications during Docker operations. Repository contents include the **`aaa_mcp/`** Python package implementing constitutional AI governance, **Dockerfile** for container construction, infrastructure templates, and operational scripts.

#### 3.1.2 Environment Configuration

Externalize configuration through environment variables, enabling deployment-specific customization without source modification:

```bash
# Create environment file from template
cp .env.docker.example .env.docker

# Edit with your actual values
nano .env.docker
```

**Critical configuration variables:**

| Variable | Purpose | Example Value | Security Classification |
|----------|---------|-------------|------------------------|
| **`ARIF_SECRET`** | Request authentication header | `IM ARIF` (replace in production) | **High** — shared secret, rotate regularly |
| **`PORT`** | Primary server bind port | `8080` | Low — infrastructure |
| **`HOST`** | Network interface binding | `0.0.0.0` (all interfaces) | Low — infrastructure |
| **`ANTHROPIC_API_KEY`** | Claude API access | `sk-ant-api03-...` | **Critical** — provider credential, never commit |
| **`OPENAI_API_KEY`** | GPT API access | `sk-proj-...` | **Critical** — provider credential, never commit |
| **`GITHUB_TOKEN`** | Repository operations | `github_pat_...` | **High** — scoped access token |

**Absolute security constraint:** The `.env.docker` file **must never be committed to version control**. Verify `.gitignore` exclusion and consider pre-commit hooks to prevent accidental exposure. API key compromise necessitates immediate revocation and rotation through provider dashboards.

### 3.2 Container Orchestration

#### 3.2.1 Docker Compose Specification

Create **`deployment/docker-compose.vps.yml`**—referenced in CI/CD workflows but requiring local generation for environment-specific tuning:

```bash
cat > deployment/docker-compose.vps.yml << 'EOF'
# arifOS MCP Server — Hostinger VPS Production Stack
# Trinity Protocol: Dual SSE (8080) + HTTP (8089) Transport

version: '3.8'

services:
  arifosmcp_server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: arifosmcp_server
    env_file:
      - .env.docker
    environment:
      - PYTHONUNBUFFERED=1           # Unbuffered logs for real-time monitoring
      - ARIFOS_ENV=production        # Runtime mode: production hardening
      - GOVERNANCE_MODE=HARD         # Constitutional floor enforcement: strict
      - AAA_MCP_TRANSPORT=sse        # Default transport identifier
      - LOG_LEVEL=info               # Verbosity: debug, info, warning, error
    ports:
      - "8088:8080"                  # SSE transport (host:container)
      - "8889:8089"                  # HTTP/StreamableHTTP transport
    command: ["./start-trinity.sh"]  # Trinity Protocol orchestration
    restart: unless-stopped          # Automatic recovery, manual override respect
    healthcheck:
      test: ["CMD", "pgrep", "-f", "python -m aaa_mcp"]
      interval: 15s                  # Check frequency
      timeout: 5s                    # Maximum check duration
      retries: 3                     # Failure threshold before unhealthy
      start_period: 30s              # Model loading grace period
    deploy:
      resources:
        limits:
          memory: 4G                 # Hard ceiling: 50% of VPS RAM
        reservations:
          memory: 2G                 # Guaranteed minimum for OOM protection

networks:
  default:
    driver: bridge
EOF
```

**Key design decisions:** The **4 GB memory limit** (50% of VPS RAM) accommodates the sentence-transformers model plus operational headroom, while **2 GB reservation** ensures baseline availability. The **30-second start period** acknowledges model initialization duration, preventing premature health check failures. Port mapping abstraction enables flexible host-side reconfiguration without container rebuilds.

#### 3.2.2 Resource Allocation

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| **Memory limit** | 4 GB | Prevents container-induced host instability |
| **Memory reservation** | 2 GB | Guaranteed minimum for scheduling priority |
| **Health interval** | 15 seconds | Responsive failure detection without excessive load |
| **Health timeout** | 5 seconds | Accommodates slow `pgrep` execution |
| **Health retries** | 3 | Tolerance for transient unavailability |
| **Start period** | 30 seconds | Sentence-transformers model loading duration |
| **Restart policy** | `unless-stopped` | Automatic recovery with manual override respect |

### 3.3 Build & Launch Procedures

#### 3.3.1 Initial Deployment

Execute the complete build-and-launch sequence:

```bash
cd /root/arifOS

# Build image and start container (detached mode)
docker compose -f deployment/docker-compose.vps.yml up -d --build

# Monitor real-time logs
docker compose -f deployment/docker-compose.vps.yml logs -f
```

**Expected build duration: 3–5 minutes**, dominated by **sentence-transformers model download** (hundreds of megabytes) and PyTorch dependency resolution. First builds lack cache acceleration; subsequent builds with unchanged dependencies complete substantially faster.

#### 3.3.2 Verification Tests

Confirm operational status through layered validation:

| Test Level | Command | Success Indicator |
|-----------|---------|-----------------|
| **Container status** | `docker ps --filter "name=arifosmcp"` | `STATUS: Up (healthy)`, ports mapped |
| **SSE transport (internal)** | `curl -H "ARIF_SECRET: IM ARIF" http://127.0.0.1:8088/sse -m 3` | HTTP 200, connection maintained until timeout |
| **HTTP transport (internal)** | `curl -X POST -H "ARIF_SECRET: IM ARIF" -d '{"jsonrpc":"2.0","method":"ping","id":1}' http://127.0.0.1:8889/mcp` | JSON-RPC response with matching `id` |

The **`-m 3` timeout** for SSE testing prevents indefinite hanging on successful connection establishment—SSE connections intentionally persist awaiting server-pushed events.

## 4. Network Security & Access Control

### 4.1 Firewall Configuration

#### 4.1.1 UFW Rules (Host Level)

Implement defense-in-depth with explicit port access control:

```bash
# Allow essential services
ufw allow 22/tcp comment 'SSH administrative access'
ufw allow 80/tcp comment 'HTTP redirect to HTTPS'
ufw allow 443/tcp comment 'HTTPS production traffic'

# Block direct Docker port access (Nginx handles all routing)
ufw deny 8088/tcp comment 'Block direct SSE — force Nginx proxy'
ufw deny 8889/tcp comment 'Block direct HTTP MCP — force Nginx proxy'

# Apply and verify
ufw enable
ufw status verbose
```

**Critical security principle:** The **DENY rules for 8088 and 8889** enforce architectural integrity—all external traffic must traverse Nginx for unified logging, rate limiting, and request inspection. Without these rules, Docker's default `0.0.0.0` binding exposes containers directly to the internet, bypassing protective layers.

#### 4.1.2 Hostinger Panel Firewall

Configure cloud-level protection through Hostinger control panel (**VPS → Firewall Rules**):

| Rule | Protocol | Port | Action | Purpose |
|------|----------|------|--------|---------|
| SSH | TCP | 22 | ACCEPT | Administrative access |
| HTTP | TCP | 80 | ACCEPT | Certificate validation, redirects |
| HTTPS | TCP | 443 | ACCEPT | Production traffic |

This **dual-layer approach**—Hostinger cloud firewall plus UFW—ensures that even host-level misconfiguration doesn't expose internal services. Cloud-level rules propagate faster and persist across OS reinstallations, while UFW provides granular process-level control.

### 4.2 Reverse Proxy Setup

#### 4.2.1 Nginx Site Configuration

Deploy the production Nginx configuration with dual-transport optimization:

```bash
cat > /etc/nginx/sites-available/arifosmcp << 'EOF'
# arifOS MCP Server — Nginx reverse proxy (Dual Transport)
# VPS: 72.62.71.199 (Hostinger KVM 2)
# Domain: arifosmcp.arif-fazil.com

server {
    listen 80;
    server_name arifosmcp.arif-fazil.com;
    
    # Universal HTTPS redirect
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name arifosmcp.arif-fazil.com;

    # SSL certificate paths (Let's Encrypt or Cloudflare Origin)
    ssl_certificate /etc/letsencrypt/live/arifosmcp.arif-fazil.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arifosmcp.arif-fazil.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;

    # ═══════════════════════════════════════════════════════════
    # SSE TRANSPORT — Server-Sent Events (Real-time streaming)
    # ═══════════════════════════════════════════════════════════
    location /sse {
        proxy_pass http://127.0.0.1:8088/sse;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Critical SSE optimizations
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;           # Disable response buffering
        proxy_cache off;               # Disable caching
        proxy_read_timeout 86400s;     # 24-hour connection lifetime
        chunked_transfer_encoding off; # Compatibility mode
        
        # Additional SSE protocol headers
        proxy_set_header Cache-Control "no-cache";
        add_header X-Accel-Buffering "no";
    }

    # ═══════════════════════════════════════════════════════════
    # HTTP/STREAMABLEHTTP TRANSPORT — Request-response
    # ═══════════════════════════════════════════════════════════
    location /mcp {
        proxy_pass http://127.0.0.1:8889/mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering on;            # Enable for efficiency
        proxy_read_timeout 300s;       # Standard API timeout
    }

    # Health check endpoint for monitoring
    location /health {
        proxy_pass http://127.0.0.1:8088/health;
        access_log off;                # Reduce log noise
    }

    # Service discovery information
    location = / {
        return 200 '{"service":"arifOS-AAA","endpoints":["/sse","/mcp"],"status":"operational","version":"2026.02.17-FORGE-VPS-SEAL"}';
        add_header Content-Type application/json;
    }

    # Invalid path guidance
    location / {
        return 404 '{"error":"Invalid endpoint. Use /sse or /mcp"}';
        add_header Content-Type application/json;
    }
}
EOF
```

**Enable and activate:**

```bash
# Symlink to sites-enabled
ln -sf /etc/nginx/sites-available/arifosmcp /etc/nginx/sites-enabled/

# Remove default site to prevent conflicts
rm -f /etc/nginx/sites-enabled/default

# Validate syntax
nginx -t
```

#### 4.2.2 SSL Certificate Management

**Path A: Let's Encrypt (DNS-only / Grey Cloud mode)**

```bash
# Obtain and install certificate with automatic Nginx configuration
certbot --nginx -d arifosmcp.arif-fazil.com

# Verify auto-renewal
certbot renew --dry-run
```

**Path B: Cloudflare Origin Certificate (Proxied / Orange Cloud mode)**

1. Navigate to **Cloudflare Dashboard → SSL/TLS → Origin Server**
2. Click **Create Certificate**
3. Select **RSA (2048-bit)** or **ECC (256-bit)**
4. Choose **15-year validity**
5. Copy certificate and private key to:
   - `/etc/nginx/ssl/arifosmcp.arif-fazil.com.crt`
   - `/etc/nginx/ssl/arifosmcp.arif-fazil.com.key`
6. Update Nginx `ssl_certificate` and `ssl_certificate_key` paths accordingly

**Final activation:**

```bash
systemctl reload nginx
systemctl enable nginx
```

| Certificate Source | Validity | Renewal | Best For |
|-------------------|----------|---------|----------|
| **Let's Encrypt** | 90 days | Automatic (Certbot) | DNS-only mode, maximum flexibility |
| **Cloudflare Origin** | 15 years | Manual | Proxied mode, simplified operations |

## 5. DNS & External Access

### 5.1 Cloudflare Configuration

#### 5.1.1 DNS Records

Configure your domain for service exposure:

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|------------|-----|
| **A** | `arifosmcp` | `72.62.71.199` | ☁️ **Proxied** (orange) or ⚪ **DNS-only** (grey) | Auto |

**Proxy status decision matrix:**

| Mode | Visual | Benefits | Risks | When to Choose |
|------|--------|----------|-------|--------------|
| **Proxied** ☁️ | Orange cloud | DDoS protection, WAF, edge caching, universal SSL | **100s timeout breaks SSE**; requires keepalive or Enterprise plan | Maximum security, HTTP-primary clients |
| **DNS-only** ⚪ | Grey cloud | Native SSE compatibility, direct origin control, Let's Encrypt | Origin exposed to direct attacks, manual certificate management | SSE-critical applications, debugging |

**Your current deployment uses Proxied mode**—monitor for SSE disconnection issues and consider switching to DNS-only if Claude Desktop experiences frequent reconnections.

#### 5.1.2 SSL/TLS Settings

| Setting | Recommended Value | Purpose |
|---------|-----------------|---------|
| **Encryption mode** | **Full (strict)** | End-to-end encryption with origin certificate validation |
| **Always Use HTTPS** | **On** | Automatic HTTP→HTTPS redirect |
| **Minimum TLS Version** | **1.2** | Exclude vulnerable legacy protocols |
| **Automatic HTTPS Rewrites** | **On** | Fix mixed content issues |

### 5.2 External Connectivity Testing

Execute validation from your **local machine** (not VPS) to confirm complete stack functionality:

```bash
# Test service discovery endpoint
curl https://arifosmcp.arif-fazil.com/

# Test SSE transport (3-second timeout, expect hang then Ctrl+C)
curl -v -H "ARIF_SECRET: IM ARIF" \
  https://arifosmcp.arif-fazil.com/sse -m 3

# Test HTTP transport with JSON-RPC ping
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -H "ARIF_SECRET: IM ARIF" \
  -d '{"jsonrpc":"2.0","method":"ping","id":1}'
```

**Expected responses:**
- Root: `{"service":"arifOS-AAA","endpoints":["/sse","/mcp"],"status":"operational",...}`
- SSE: HTTP 200, connection maintained, server-ready for event stream
- HTTP: `{"jsonrpc":"2.0","result":"pong","id":1}` or equivalent acknowledgment

Use the **`test-arifosmcp.sh`** script from repository attachments for automated validation:

```bash
chmod +x test-arifosmcp.sh
./test-arifosmcp.sh
```

## 6. Client Integration

### 6.1 Claude Desktop Configuration

#### 6.1.1 Configuration File Locations

| Platform | Path | Notes |
|----------|------|-------|
| **macOS** | `~/Library/Application Support/Claude/claude_desktop_config.json` | Sandbox container in App Store versions |
| **Windows** | `%APPDATA%\Claude\claude_desktop_config.json` | Expands to `C:\Users\<user>\AppData\Roaming\` |
| **Linux** | `~/.config/Claude/claude_desktop_config.json` | XDG Base Directory compliance |

Create or edit the configuration file with restricted permissions (`chmod 600` on Unix systems) given credential inclusion.

#### 6.1.2 MCP Server Entry

```json
{
  "mcpServers": {
    "arifOS-AAA": {
      "transport": {
        "type": "sse",
        "url": "https://arifosmcp.arif-fazil.com/sse",
        "headers": {
          "ARIF_SECRET": "IM ARIF"
        }
      }
    }
  }
}
```

**Restart Claude Desktop** to load configuration. Verify connection through:
- Server appearance in **Settings → MCP Servers**
- Tool enumeration in conversation interface
- Successful tool invocation with constitutional governance applied

### 6.2 Alternative Client Configurations

#### 6.2.1 HTTP-Based Clients (Perplexity, Antigravity)

```json
{
  "mcpServers": {
    "arifOS-AAA": {
      "url": "https://arifosmcp.arif-fazil.com/mcp",
      "transport": "http",
      "headers": {
        "ARIF_SECRET": "IM ARIF"
      }
    }
  }
}
```

**StreamableHTTP benefits:** Stateless compatibility, standard load balancer support, request batching, and graceful degradation for non-streaming clients. The same **13 constitutional floors** apply uniformly across transports.

## 7. Operational Maintenance

### 7.1 Production Hardening

#### 7.1.1 Resource Controls

Apply runtime adjustments without container recreation:

```bash
# Enforce memory constraints with swap buffer
docker update --memory 4G --memory-swap 6G arifosmcp_server

# Ensure persistent restart behavior
docker update --restart unless-stopped arifosmcp_server
```

#### 7.1.2 Log Management

Prevent disk exhaustion from unbounded container logs:

```bash
cat > /etc/logrotate.d/docker-containers << 'EOF'
/var/lib/docker/containers/*/*.log {
    rotate 7              # 7 days retention
    daily                 # Daily rotation
    compress              # Gzip compression (~85% reduction)
    missingok             # Tolerance for container recreation
    notifempty            # Skip empty logs
    delaycompress         # Compress previous cycle, not current
}
EOF
```

### 7.2 CI/CD Automation

#### 7.2.1 GitHub Actions Integration

Configure repository secrets for automated deployment (**Settings → Secrets → Actions**):

| Secret | Value | Source |
|--------|-------|--------|
| `VPS_HOST` | `72.62.71.199` | VPS IPv4 address |
| `VPS_USERNAME` | `root` | SSH username |
| `VPS_SSH_KEY` | Private key content | `~/.ssh/id_rsa` or dedicated deploy key |

**Security best practice:** Generate a **dedicated deploy key** (`ssh-keygen -t ed25519 -f ~/.ssh/arifos_deploy`) rather than using personal keys, enabling isolated credential rotation.

Post-configuration, every `git push` to `main` triggers automatic VPS deployment.

#### 7.2.2 Manual Rebuild Procedures

| Operation | Command | Use Case |
|-----------|---------|----------|
| **Full rebuild** | `./rebuild-arifosmcp.sh` | Code changes, dependency updates |
| **Service restart** | `docker compose -f deployment/docker-compose.vps.yml restart` | Configuration reload, quick recovery |
| **Log inspection** | `docker logs -f arifosmcp_server` | Real-time troubleshooting |
| **Health check** | `curl http://127.0.0.1:8088/health` | Container status verification |

## 8. Troubleshooting & Governance

### 8.1 Known Uncertainties & Risks

#### 8.1.1 Configuration Gaps

| Uncertainty | Impact | Mitigation | Status |
|-------------|--------|------------|--------|
| `deployment/docker-compose.vps.yml` repository presence | Deployment reproducibility | Verify post-clone; create from documentation if absent | **Verify required** |
| Cloudflare proxy mode vs. SSE stability | Client disconnection experience | Monitor Claude Desktop behavior; switch to DNS-only if issues arise | **Monitor actively** |
| `.env.docker` version control exclusion | Credential exposure risk | Verify `.gitignore`; implement pre-commit hooks | **Verify required** |

**Quantified uncertainty: Ω₀ ≈ 0.03** — low but non-zero operational risk requiring verification steps.

#### 8.1.2 Recovery Mechanisms

| Mechanism | Trigger | Recovery Time | Data Preservation |
|-----------|---------|-------------|-----------------|
| **Hostinger snapshot** | Control panel initiation | 5–15 minutes | To snapshot timestamp |
| **Docker container restart** | `docker restart` or compose | <30 seconds | In-flight requests lost |
| **Git-based redeploy** | `git pull` + rebuild | 3–5 minutes | Stateless, no data loss |
| **Nginx reload** | `systemctl reload nginx` | <1 second | Zero downtime |

### 8.2 Capacity & Performance Monitoring

#### 8.2.1 Resource Headroom Analysis

| Resource | Current | Limit | Headroom | Scaling Trigger |
|----------|---------|-------|----------|---------------|
| **CPU** | 35% | 2 cores | 65% | Sustained >80% |
| **Memory** | 48% (3.84 GB) | 8 GB | 52% (4.16 GB) | Container OOM, swap pressure |
| **Disk** | 66 GB | 100 GB | 34 GB (34%) | >85% utilization |
| **Bandwidth** | 0.111 TB/month | 8 TB/month | 7.889 TB (98.6%) | N/A — massive headroom |

**Fixed overhead:** Sentence-transformers model consumes **~2 GB RAM** regardless of traffic. Per-request memory scales sublinearly due to FastMCP's async architecture.

#### 8.2.2 Scaling Considerations

| Path | Action | When Needed | Effort |
|------|--------|-------------|--------|
| **Vertical (Hostinger)** | Upgrade to KVM 4/8/16 | Memory pressure, CPU saturation | Low — in-place upgrade |
| **Horizontal** | Multi-VPS with load balancer | Geographic distribution, fault tolerance | Medium — architectural change |
| **Optimization** | Model quantization, caching layer | Cost reduction, latency improvement | Medium — code changes |

---

## Quick Reference Card

| Component | Value |
|-----------|-------|
| **VPS IP** | `72.62.71.199` |
| **Domain** | `arifosmcp.arif-fazil.com` |
| **SSE Endpoint** | `https://arifosmcp.arif-fazil.com/sse` |
| **HTTP Endpoint** | `https://arifosmcp.arif-fazil.com/mcp` |
| **Authentication** | `ARIF_SECRET: IM ARIF` |
| **Container** | `arifosmcp_server` |
| **Port Mapping** | `8088:8080` (SSE), `8889:8089` (HTTP) |
| **Framework** | FastMCP 2.14.5 (pinned `<3.0.0`) |
| **Health Check** | `http://127.0.0.1:8088/health` |
| **Logs** | `docker logs -f arifosmcp_server` |
| **Restart** | `docker compose -f deployment/docker-compose.vps.yml restart` |
| **Rebuild** | `./rebuild-arifosmcp.sh` |

---

*DITEMPA BUKAN DIBERI* 🔥💎🧠

**Attribution:** arifOS constitutional AI governance | [GitHub: ariffazil/arifOS](https://github.com/ariffazil/arifOS)
