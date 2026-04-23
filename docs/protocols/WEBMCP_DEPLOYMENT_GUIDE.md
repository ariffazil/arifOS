# WebMCP Deployment Guide
## Deploy arifOS as an AI-Governed WebMCP Environment

**Version:** 2026.03.14-VALIDATED  
**Target:** Production WebMCP Deployment

---

## Overview

This guide shows you how to deploy arifOS as one of the first **WebMCP** environments on the internet—an AI-governed MCP server accessible via web browsers with full constitutional enforcement (F1-F13).

### What Makes This Revolutionary?

| Traditional MCP | WebMCP (arifOS) |
|-----------------|-----------------|
| Local stdio only | Browser + HTTP/WebSocket |
| No security layer | F12 Injection Guard (XSS/CSRF) |
| No auth | F11 Command Auth (session-based) |
| No governance | F1-F13 enforced on every request |
| No human veto | 888_HOLD web UI for ratification |

---

## Quick Deploy (5 Minutes)

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/ariffazil/arifosmcp.git
cd arifosmcp

# 2. Create environment file
cat > .env << 'EOF'
ARIFOS_ENV=production
ARIFOS_MODE=webmcp
SESSION_SECRET=$(openssl rand -hex 32)
REDIS_URL=redis://redis:6379
POSTGRES_URL=postgresql://arifos:password@postgres:5432/arifos
EOF

# 3. Start WebMCP stack
docker-compose -f docker-compose.webmcp.yml up -d

# 4. Verify deployment
curl https://localhost:8443/webmcp
```

### Option 2: Python Direct

```bash
# 1. Install arifOS
pip install arifosmcp==2026.3.14

# 2. Install WebMCP dependencies
pip install fastapi uvicorn redis

# 3. Start Redis
redis-server --daemonize yes

# 4. Launch WebMCP
python -m arifosmcp.runtime webmcp --host 0.0.0.0 --port 8443
```

---

## Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                       WEB CLIENTS                            │
│  Browser ←── JavaScript SDK (@arifos/webmcp)                │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTPS/WSS
┌───────────────────────▼─────────────────────────────────────┐
│                    NGINX (SSL/WAF)                          │
│  • SSL termination                                          │
│  • Rate limiting (F5)                                       │
│  • WebSocket proxy                                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                  arifOS WebMCP Server                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ F12 Guard   │  │ F11 Session │  │ 000→999     │         │
│  │ (XSS/CSRF)  │  │ (Auth)      │  │ Metabolic   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│              Infrastructure Layer                            │
│  Redis (sessions)  PostgreSQL (VAULT999)  Qdrant (vectors)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Constitutional |
|----------|-------------|---------|----------------|
| `ARIFOS_ENV` | Runtime mode | `production` | - |
| `ARIFOS_MODE` | Server mode | `webmcp` | - |
| `SESSION_SECRET` | Cookie signing key | **Required** | F11 |
| `SESSION_TTL` | Session lifetime | `3600` | F11 |
| `REDIS_URL` | Session store | `redis://localhost` | F11 |
| `CORS_ORIGINS` | Allowed origins | `*.arif-fazil.com` | F12 |
| `RATE_LIMIT` | Requests/minute | `100` | F5 |
| `WS_MAX_CONN` | Max WebSockets | `100` | F5 |

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/arifos-webmcp

upstream webmcp {
    least_conn;
    server 127.0.0.1:8443;
}

server {
    listen 443 ssl http2;
    server_name arifosmcp.arif-fazil.com;
    
    ssl_certificate /etc/letsencrypt/live/arif-fazil.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arif-fazil.com/privkey.pem;
    
    # Security headers (F12)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # WebMCP API
    location /webmcp/ {
        proxy_pass http://webmcp;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Constitutional timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # WebSocket for real-time governance
    location /webmcp/ws {
        proxy_pass http://webmcp;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        
        proxy_read_timeout 86400;  # WebSocket long-lived
    }
    
    # Static dashboard
    location /dashboard {
        alias /var/www/arifos/dashboard;
        try_files $uri $uri/ =404;
    }
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name arifosmcp.arif-fazil.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Browser Client Usage

### Installation

```bash
npm install @arifos/webmcp
```

### Basic Usage

```javascript
import { WebMCPClient } from '@arifos/webmcp';

// Initialize client
const client = new WebMCPClient('https://arifosmcp.arif-fazil.com');

// Initialize session (000_INIT)
await client.init({
  actor_id: 'web-user-123',
});

// Call tools through constitutional governance
const result = await client.call('agi_reason', {
  query: 'What is constitutional AI?'
});

console.log(result.verdict); // "SEAL", "VOID", "888_HOLD"
console.log(result.payload); // Tool output
```

### React Hook

```javascript
import { useWebMCP } from '@arifos/webmcp/react';

function GovernedApp() {
  const { client, vitals, hold, isConnected } = useWebMCP(
    'https://arifosmcp.arif-fazil.com'
  );
  
  const handleAction = async () => {
    const result = await client.call('eureka_forge', {
      command: 'ls -la',
    });
    
    if (result.verdict === '888_HOLD') {
      // Show human ratification UI
      alert('Human approval required!');
    }
  };
  
  return (
    <div>
      <div className="vitals">
        G★: {vitals?.G_star} | 
        ΔS: {vitals?.dS} | 
        Peace²: {vitals?.peace2}
      </div>
      
      {hold && (
        <div className="hold-alert">
          <h3>888 HOLD</h3>
          <p>{hold.reason}</p>
          <button onClick={() => client.ratify('SEAL')}>Approve</button>
          <button onClick={() => client.ratify('VOID')}>Reject</button>
        </div>
      )}
      
      <button onClick={handleAction}>Execute Action</button>
    </div>
  );
}
```

---

## API Endpoints

### Session Management

```bash
# Initialize session (000_INIT)
POST /webmcp/init
{
  "actor_id": "web-user-123",
  "human_approval": false
}

# Response
{
  "verdict": "SEAL",
  "session_id": "web-abc123",
  "auth_context": {...},
  "expires_at": 1234567890
}
```

### Tool Calls

```bash
# Call tool through metabolic loop
POST /webmcp/call/{tool_name}
Headers:
  Cookie: arifos_session=...
  Content-Type: application/json

Body:
{
  "query": "...",
  "context": "...",
  "options": {...}
}

# Response
{
  "verdict": "SEAL",
  "stage": "VAULT_999",
  "payload": {...},
  "metrics": {
    "G_star": 0.85,
    "dS": -0.3,
    "peace2": 1.05
  },
  "philosophy": {...}
}
```

### System Vitals

```bash
# Get current vitals (F4, F5, F7)
GET /webmcp/vitals

# Response
{
  "verdict": "SEAL",
  "vitals": {
    "G_star": 0.85,
    "dS": -0.3,
    "peace2": 1.05,
    "omega": 0.04
  },
  "floors": {
    "F1": "PASS",
    "F2": "PASS",
    ...
  }
}
```

### WebSocket

```javascript
// Connect to real-time governance stream
const ws = new WebSocket('wss://arifosmcp.arif-fazil.com/webmcp/ws');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  switch (msg.type) {
    case 'vitals':
      updateDashboard(msg.data);
      break;
    case '888_HOLD':
      showRatificationUI(msg.data);
      break;
  }
};
```

---

## Constitutional Enforcement

### F12 Injection Guard (Security)

Every request is scanned for:
- XSS patterns (`<script>`, `javascript:`, event handlers)
- SQL injection (`UNION SELECT`, `DROP TABLE`)
- Path traversal (`../`, `..\`)
- Prompt injection (`ignore previous`, `you are now`)
- CSRF attempts

**Threshold:** Score > 0.85 = **VOID**

### F11 Command Auth (Identity)

- Sessions cryptographically signed
- Redis-backed with TTL
- Auth context propagated through metabolic loop
- Kill switch for session revocation

### F5 Peace² (Stability)

- Rate limiting: 100 requests/minute per IP
- WebSocket connection limits
- Request timeouts: 30s max

### F13 Sovereign (Human Veto)

- 888_HOLD triggers web UI notification
- Human can SEAL, VOID, or SABAR
- All decisions logged to VAULT999

---

## Monitoring

### Health Check

```bash
curl https://arifosmcp.arif-fazil.com/webmcp
```

### Prometheus Metrics

```
webmcp_requests_total{verdict="SEAL"}
webmcp_requests_total{verdict="VOID"}
webmcp_injection_blocked_total
webmcp_sessions_active
webmcp_websocket_connections
```

### Logging

```python
# All requests logged with constitutional metadata
{
  "timestamp": "2026-03-14T10:00:00Z",
  "session_id": "web-abc123",
  "tool": "agi_reason",
  "verdict": "SEAL",
  "floors_passed": ["F1", "F2", "F4", "F7", "F8"],
  "metrics": {
    "G_star": 0.85,
    "dS": -0.3
  }
}
```

---

## Troubleshooting

### "Session expired"
- Session TTL is 1 hour by default
- Call `/webmcp/init` to refresh

### "F12_INJECTION_BLOCKED"
- Request contains suspicious patterns
- Check shield report in response
- Sanitize user input

### "888_HOLD"
- Tool requires human approval
- Open dashboard at `/dashboard`
- Or handle in client UI

### WebSocket disconnects
- Check `WS_MAX_CONNECTIONS` limit
- Verify nginx proxy_read_timeout
- Client will auto-reconnect

---

## Next Steps

1. **Deploy** using Docker Compose
2. **Configure** your domain and SSL
3. **Integrate** the browser SDK
4. **Monitor** via dashboard and metrics
5. **Scale** with multiple WebMCP instances

---

*DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]*
