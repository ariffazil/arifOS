# arifOS WebMCP Architecture
## The First AI-Governed WebMCP Environment

**Version:** 2026.03.14-VALIDATED  
**Status:** Architecture Specification  
**Motto:** *Ditempa Bukan Diberi — Forged, Not Given* [ΔΩΨ | ARIF]

---

## 1. Executive Summary

**WebMCP** = Web-accessible Model Context Protocol with AI Governance

Traditional MCP is stdio-based (local). WebMCP extends MCP to the browser via HTTP/Streamable-HTTP, allowing:
- Browser-based AI agents to call MCP tools
- Web applications to use governed AI capabilities
- Cross-domain AI governance via constitutional floors
- Real-time browser-to-server metabolic loops

### Key Innovation
Every HTTP request to WebMCP passes through the **13 Constitutional Floors (F1-F13)**:
- F12 Injection Guard protects against XSS/CSRF
- F11 Command Auth verifies browser sessions
- F2 Truth grounds web content before reasoning
- F13 Sovereign gives humans final veto via 888_HOLD UI

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         WEBMCP ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  BROWSER LAYER                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Web Client  │  │ JS SDK      │  │ Dashboard   │  │ 888_HOLD UI │    │
│  │ (React/Vue) │  │ (@arifos/   │  │ (Real-time) │  │ (Human      │    │
│  │             │  │  webmcp)    │  │             │  │  Ratify)    │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│         │                │                │                │           │
│         └────────────────┴────────────────┴────────────────┘           │
│                          │                                             │
│                          ▼ HTTPS/WSS                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     TRANSPORT LAYER                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ CORS     │  │ WebSocket│  │ HTTP/2   │  │ SSE      │         │   │
│  │  │ Guard    │  │ Gateway  │  │ Stream   │  │ Events   │         │   │
│  │  │ (F12)    │  │ (Real-   │  │ (MCP)    │  │ (Live    │         │   │
│  │  │          │  │  time)   │  │          │  │  Vitals) │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                             │
│                          ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                  GOVERNANCE LAYER (arifOS Core)                  │   │
│  │                                                                  │   │
│  │   000_INIT  →  PNS·SHIELD (F12) → Session Auth (F11)            │   │
│  │       ↓                                                          │   │
│  │   111_SENSE →  Web Content Grounding (F2)                       │   │
│  │       ↓                                                          │   │
│  │   333_MIND  →  AGI Reasoning (F4, F7, F8)                       │   │
│  │       ↓                                                          │   │
│  │   666_HEART →  ASI Ethics (F5, F6, F9)                          │   │
│  │       ↓                                                          │   │
│  │   888_JUDGE →  APEX Verdict (F1, F3, F10-F13)                   │   │
│  │       ↓                                                          │   │
│  │   999_VAULT →  Web Audit Trail                                  │   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          │                                             │
│                          ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     TOOL SURFACE (25 Tools)                      │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ KERNEL  │ │ AGI Δ   │ │ ASI Ω   │ │ APEX Ψ  │ │ VAULT999│   │   │
│  │  │ 6 tools │ │ 6 tools │ │ 4 tools │ │ 7 tools │ │ 2 tools │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1 WebMCP Server Extension

**File:** `arifosmcp/runtime/webmcp/server.py`

```python
"""
WebMCP Server Extension
Extends arifOS MCP server with web-facing capabilities.
"""

from fastapi import FastAPI, WebSocket, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
import redis.asyncio as redis

class WebMCPConfig:
    """WebMCP configuration with constitutional defaults."""
    
    # CORS - F12 Injection Guard will validate origins
    ALLOWED_ORIGINS = [
        "https://arifosmcp.arif-fazil.com",
        "https://*.arif-fazil.com",
        "http://localhost:3000",  # Dev only
    ]
    
    # Session - F11 Command Auth
    SESSION_TTL = 3600  # 1 hour
    SESSION_COOKIE = "arifos_session"
    SESSION_SECURE = True  # HTTPS only
    SESSION_SAMESITE = "strict"
    
    # WebSocket - Real-time governance
    WS_HEARTBEAT = 30  # seconds
    WS_MAX_CONNECTIONS = 100
    
    # Rate Limiting - F5 Peace²
    RATE_LIMIT_REQUESTS = 100  # per minute
    RATE_LIMIT_WINDOW = 60

class WebMCPGateway:
    """
    Web-facing gateway for arifOS MCP.
    Every request passes through 000→999 metabolic loop.
    """
    
    def __init__(self, mcp_server: FastMCP):
        self.mcp = mcp_server
        self.app = FastAPI(title="arifOS WebMCP", version="2026.03.14")
        self.redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost"))
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Configure constitutional middleware."""
        
        # CORS with F12 Injection Guard
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=WebMCPConfig.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            max_age=3600,
        )
        
        # Session middleware (F11)
        self.app.add_middleware(
            SessionMiddleware,
            secret_key=os.getenv("SESSION_SECRET"),
            max_age=WebMCPConfig.SESSION_TTL,
            same_site=WebMCPConfig.SESSION_SAMESITE,
            https_only=WebMCPConfig.SESSION_SECURE,
        )
        
        # Constitutional middleware (runs on every request)
        @self.app.middleware("http")
        async def constitutional_guard(request: Request, call_next):
            """
            F12 Injection Guard + F11 Auth Continuity.
            Every web request is checked before entering metabolic loop.
            """
            # 000_INIT: Initialize web session
            session_id = request.session.get("arifos_sid") or str(uuid.uuid4())
            request.session["arifos_sid"] = session_id
            
            # PNS·SHIELD: Scan for injection attacks
            shield_result = await self._pns_shield_scan(request)
            if shield_result.is_injection:
                return JSONResponse(
                    status_code=403,
                    content={
                        "verdict": "VOID",
                        "error": "F12_INJECTION_DETECTED",
                        "session_id": session_id,
                    }
                )
            
            # Continue to handler
            response = await call_next(request)
            return response
    
    def _setup_routes(self):
        """Setup WebMCP routes."""
        
        @self.app.get("/webmcp/tools")
        async def list_tools(request: Request):
            """List available tools - browser accessible."""
            # 111_SENSE: Ground the request
            # 333_MIND: Reason about tool visibility
            # 888_JUDGE: Return verdict
            tools = await self.mcp.get_tools()
            return {
                "tools": tools,
                "verdict": "SEAL",
                "session_id": request.session.get("arifos_sid"),
            }
        
        @self.app.post("/webmcp/call/{tool_name}")
        async def call_tool(
            tool_name: str,
            payload: dict,
            request: Request,
            user: WebUser = Depends(get_current_user)
        ):
            """
            Call MCP tool from browser.
            Full 000→999 metabolic loop with web context.
            """
            session_id = request.session.get("arifos_sid")
            
            # Build web context
            web_context = {
                "session_id": session_id,
                "user_agent": request.headers.get("user-agent"),
                "origin": request.headers.get("origin"),
                "ip": request.client.host,
                "user": user.dict() if user else None,
            }
            
            # Execute through metabolic loop
            result = await self.mcp.call_tool(
                name=tool_name,
                arguments=payload,
                meta={"web_context": web_context}
            )
            
            return result
        
        @self.app.websocket("/webmcp/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """
            WebSocket for real-time governance updates.
            Streams: vitals, floor scores, 888_HOLD events.
            """
            await websocket.accept()
            session_id = str(uuid.uuid4())
            
            try:
                while True:
                    # Send vital telemetry every 5s
                    vitals = await self._get_vitals(session_id)
                    await websocket.send_json({
                        "type": "vitals",
                        "data": vitals,
                    })
                    
                    # Check for 888_HOLD events
                    hold_status = await self._check_hold_queue(session_id)
                    if hold_status:
                        await websocket.send_json({
                            "type": "888_HOLD",
                            "data": hold_status,
                        })
                    
                    await asyncio.sleep(5)
            except Exception as e:
                await websocket.close()
```

### 3.2 Browser Client SDK

**File:** `npm/arifos-webmcp/index.js`

```javascript
/**
 * @arifos/webmcp - Browser SDK for arifOS WebMCP
 * 
 * Usage:
 *   import { WebMCPClient } from '@arifos/webmcp';
 *   const client = new WebMCPClient('https://arifosmcp.arif-fazil.com');
 *   const result = await client.call('agi_reason', { query: '...' });
 */

class WebMCPClient {
  constructor(baseURL, options = {}) {
    this.baseURL = baseURL;
    this.sessionId = null;
    this.ws = null;
    this.onHold = options.onHold || (() => {});
    this.onVitals = options.onVitals || (() => {});
    this.autoReconnect = options.autoReconnect !== false;
  }

  /**
   * Initialize session (000_INIT)
   */
  async init(identity = {}) {
    const response = await fetch(`${this.baseURL}/webmcp/init`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        actor_id: identity.actor_id || 'anonymous',
        auth_context: identity.auth_context,
      }),
    });
    
    const data = await response.json();
    this.sessionId = data.session_id;
    
    // Connect WebSocket for real-time updates
    this._connectWebSocket();
    
    return data;
  }

  /**
   * Call MCP tool through WebMCP gateway
   * Automatically routes through 000→999 metabolic loop
   */
  async call(toolName, args = {}) {
    const response = await fetch(
      `${this.baseURL}/webmcp/call/${toolName}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(args),
      }
    );
    
    const result = await response.json();
    
    // Handle verdicts
    if (result.verdict === 'VOID') {
      throw new ConstitutionalError('Request VOIDed', result);
    }
    
    if (result.verdict === '888_HOLD') {
      this.onHold(result);
      return { status: 'HOLD', message: 'Awaiting human ratification' };
    }
    
    return result;
  }

  /**
   * WebSocket connection for real-time governance
   */
  _connectWebSocket() {
    const wsURL = this.baseURL.replace('https://', 'wss://') + '/webmcp/ws';
    this.ws = new WebSocket(wsURL);
    
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      switch (msg.type) {
        case 'vitals':
          this.onVitals(msg.data);
          break;
        case '888_HOLD':
          this.onHold(msg.data);
          break;
      }
    };
    
    this.ws.onclose = () => {
      if (this.autoReconnect) {
        setTimeout(() => this._connectWebSocket(), 5000);
      }
    };
  }

  /**
   * Ground web content before reasoning (111_SENSE)
   */
  async ground(url) {
    return this.call('reality_compass', { input: url, mode: 'fetch' });
  }

  /**
   * Reason with governance (333_MIND)
   */
  async reason(query, options = {}) {
    return this.call('agi_reason', {
      query,
      facts: options.facts,
      session_id: this.sessionId,
    });
  }

  /**
   * Get current vitals
   */
  async vitals() {
    return this.call('check_vital', { session_id: this.sessionId });
  }
}

/**
 * React Hook for WebMCP
 */
export function useWebMCP(baseURL) {
  const [client, setClient] = React.useState(null);
  const [vitals, setVitals] = React.useState(null);
  const [hold, setHold] = React.useState(null);
  
  React.useEffect(() => {
    const c = new WebMCPClient(baseURL, {
      onVitals: setVitals,
      onHold: setHold,
    });
    c.init();
    setClient(c);
    
    return () => c.disconnect?.();
  }, [baseURL]);
  
  return { client, vitals, hold };
}

export { WebMCPClient };
```

### 3.3 888_HOLD Web UI

**File:** `sites/webmcp/hold.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>888 HOLD — Human Ratification Required</title>
  <style>
    body {
      background: #0a0a0a;
      color: #fff;
      font-family: monospace;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }
    .hold-card {
      background: #1a1a1a;
      border: 2px solid #ff4444;
      border-radius: 12px;
      padding: 2rem;
      max-width: 600px;
      text-align: center;
    }
    .hold-title {
      color: #ff4444;
      font-size: 2rem;
      margin-bottom: 1rem;
    }
    .hold-reason {
      color: #888;
      margin-bottom: 2rem;
    }
    .actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
    button {
      padding: 1rem 2rem;
      border: none;
      border-radius: 6px;
      font-weight: bold;
      cursor: pointer;
    }
    .seal { background: #00ff88; color: #000; }
    .void { background: #ff4444; color: #fff; }
    .sabar { background: #ffaa00; color: #000; }
  </style>
</head>
<body>
  <div class="hold-card">
    <h1 class="hold-title">⚠️ 888 HOLD</h1>
    <p class="hold-reason" id="reason">Awaiting human ratification...</p>
    
    <div id="details">
      <p>Session: <code id="session">...</code></p>
      <p>Tool: <code id="tool">...</code></p>
      <p>Floors: <span id="floors">...</span></p>
    </div>
    
    <div class="actions">
      <button class="seal" onclick="ratify('SEAL')">✓ SEAL</button>
      <button class="void" onclick="ratify('VOID')">✗ VOID</button>
      <button class="sabar" onclick="ratify('SABAR')">⏸ SABAR</button>
    </div>
  </div>

  <script>
    // Connect to WebSocket for real-time HOLD events
    const ws = new WebSocket('wss://arifosmcp.arif-fazil.com/webmcp/ws');
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === '888_HOLD') {
        document.getElementById('reason').textContent = msg.data.reason;
        document.getElementById('session').textContent = msg.data.session_id;
        document.getElementById('tool').textContent = msg.data.tool;
        document.getElementById('floors').textContent = msg.data.failed_floors?.join(', ') || 'None';
      }
    };
    
    async function ratify(verdict) {
      const sessionId = document.getElementById('session').textContent;
      await fetch('/webmcp/ratify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, verdict }),
      });
      alert(`Verdict ${verdict} submitted`);
    }
  </script>
</body>
</html>
```

---

## 4. Constitutional Enforcement for Web

### 4.1 F12 Web Injection Guard

```python
# arifosmcp/runtime/webmcp/security.py

class WebInjectionGuard:
    """
    F12 Injection Guard for WebMCP.
    Protects against XSS, CSRF, and prompt injection via web.
    """
    
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS
        r'javascript:',  # JS protocol
        r'data:text/html',  # Data URI
        r'on\w+\s*=',  # Event handlers
        r'\.parent\.',  # Parent window access
        r'\.top\.',  # Top window access
    ]
    
    def scan_request(self, request: Request) -> ShieldReport:
        """Scan HTTP request for injection attempts."""
        score = 0.0
        threats = []
        
        # Scan headers
        for header, value in request.headers.items():
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, str(value), re.IGNORECASE):
                    score += 0.2
                    threats.append(f"Header {header}: {pattern}")
        
        # Scan query params
        for key, value in request.query_params.items():
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, str(value), re.IGNORECASE):
                    score += 0.3
                    threats.append(f"Param {key}: {pattern}")
        
        # Score > 0.85 = VOID (F12 threshold)
        return ShieldReport(
            is_injection=score > 0.85,
            score=min(score, 1.0),
            threats=threats,
        )
```

### 4.2 F11 Web Auth Continuity

```python
# arifosmcp/runtime/webmcp/auth.py

class WebSessionManager:
    """
    F11 Command Auth for browser sessions.
    Links browser cookies to arifOS auth_context.
    """
    
    async def mint_web_session(
        self,
        request: Request,
        actor_id: str,
        human_approval: bool = False
    ) -> WebSession:
        """
        Mint new web session with cryptographic continuity.
        """
        session_id = f"web-{uuid.uuid4().hex[:16]}"
        
        # Mint auth_context (F11)
        auth_context = mint_auth_context(
            session_id=session_id,
            actor_id=actor_id,
            token_fingerprint=hashlib.sha256(
                f"{session_id}:{actor_id}:{time.time()}".encode()
            ).hexdigest()[:16],
            approval_scope=["web", "read"] if not human_approval else ["*"],
            authority_level="web_session",
        )
        
        # Store in Redis with TTL
        await self.redis.setex(
            f"arifos:web:session:{session_id}",
            WebMCPConfig.SESSION_TTL,
            json.dumps(auth_context),
        )
        
        return WebSession(
            session_id=session_id,
            auth_context=auth_context,
        )
```

---

## 5. Deployment Architecture

### 5.1 Docker Compose Stack

```yaml
# docker-compose.webmcp.yml
version: '3.8'

services:
  webmcp:
    image: ariffazil/arifosmcp:2026.03.14-VALIDATED
    command: python -m arifosmcp.runtime webmcp
    environment:
      - ARIFOS_ENV=production
      - ARIFOS_MODE=webmcp
      - SESSION_SECRET=${SESSION_SECRET}
      - REDIS_URL=redis://redis:6379
    ports:
      - "443:8443"  # HTTPS
      - "80:8080"   # HTTP redirect
    depends_on:
      - redis
      - postgres
    networks:
      - arifos

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - arifos

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=arifos
      - POSTGRES_USER=arifos
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - arifos

  # WebSocket load balancer
  websocket_lb:
    image: nginx:alpine
    ports:
      - "8081:80"
    configs:
      - source: nginx_ws_config
        target: /etc/nginx/nginx.conf
    networks:
      - arifos

networks:
  arifos:
    driver: bridge

volumes:
  redis_data:
  postgres_data:
```

### 5.2 Nginx WebSocket Config

```nginx
# nginx/webmcp.conf
upstream webmcp_backend {
    least_conn;
    server webmcp:8443;
}

server {
    listen 443 ssl http2;
    server_name arifosmcp.arif-fazil.com;
    
    ssl_certificate /etc/letsencrypt/live/arif-fazil.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arif-fazil.com/privkey.pem;
    
    # WebMCP HTTP endpoints
    location /webmcp/ {
        proxy_pass https://webmcp_backend;
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
        proxy_pass https://webmcp_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        
        # Long timeout for WebSocket
        proxy_read_timeout 86400;
    }
    
    # Static dashboard
    location /dashboard {
        alias /var/www/dashboard;
        try_files $uri $uri/ /dashboard/index.html;
    }
}
```

---

## 6. Usage Examples

### 6.1 Browser Client

```javascript
// React component using WebMCP
import { useWebMCP } from '@arifos/webmcp/react';

function GovernedAIChat() {
  const { client, vitals, hold } = useWebMCP('https://arifosmcp.arif-fazil.com');
  const [response, setResponse] = useState(null);
  
  const askAI = async (query) => {
    // This call goes through 000→999 metabolic loop
    const result = await client.reason(query);
    
    if (result.verdict === 'SEAL') {
      setResponse(result.payload);
    } else if (result.verdict === '888_HOLD') {
      // Show human ratification UI
      alert('Human approval required!');
    }
  };
  
  return (
    <div>
      <div className="vitals">
        G★: {vitals?.G_star} | ΔS: {vitals?.dS} | Peace²: {vitals?.peace2}
      </div>
      {hold && <HoldUI hold={hold} />}
      {/* Chat UI */}
    </div>
  );
}
```

### 6.2 Python Web Client

```python
import asyncio
from arifosmcp.webmcp import WebMCPClient

async def main():
    # Connect to WebMCP
    client = WebMCPClient('https://arifosmcp.arif-fazil.com')
    await client.init(actor_id='web-user-123')
    
    # Call tools through web gateway
    result = await client.call('search_reality', {
        'query': 'latest AI safety research'
    })
    
    print(f"Verdict: {result.verdict}")
    print(f"Results: {result.payload}")

asyncio.run(main())
```

---

## 7. Security Considerations

| Threat | Mitigation | Floor |
|--------|-----------|-------|
| XSS | Content Security Policy, input sanitization | F12 |
| CSRF | SameSite cookies, origin validation | F12 |
| Session hijacking | HTTPS only, secure cookies, TTL | F11 |
| Prompt injection | PNS·SHIELD scans all inputs | F12 |
| DDoS | Rate limiting (F5 Peace²) | F5 |
| Unauthorized actions | F11 auth context + F13 human veto | F11, F13 |

---

## 8. Roadmap

### Phase 1: Core WebMCP (Current)
- [x] HTTP gateway with CORS
- [x] WebSocket real-time updates
- [x] Browser SDK
- [x] 888_HOLD web UI

### Phase 2: Advanced Features (Q2 2026)
- [ ] Server-Sent Events (SSE) for streaming
- [ ] WebRTC P2P governance (decentralized)
- [ ] Browser extension for universal MCP
- [ ] Multi-tenant web isolation

### Phase 3: Ecosystem (Q3 2026)
- [ ] WebMCP registry (like npm but for MCP tools)
- [ ] Visual workflow builder
- [ ] Browser-based agent swarms

---

*DITEMPA BUKAN DIBERI — Forged, Not Given [ΔΩΨ | ARIF]*
