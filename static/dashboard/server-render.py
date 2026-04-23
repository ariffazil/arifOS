#!/usr/bin/env python3
"""
arifOS Dashboard - Server-Side Rendered Version
Fetches data at request time for better SEO and initial load
"""

import json
import urllib.request
from datetime import datetime

MCP_BASE_URL = "https://mcp.a-forge.io"

def fetch_data():
    """Fetch health and build data from MCP server"""
    try:
        with urllib.request.urlopen(f"{MCP_BASE_URL}/health", timeout=5) as resp:
            health = json.loads(resp.read().decode())
    except Exception as e:
        health = {"status": "unreachable", "error": str(e)}
    
    try:
        with urllib.request.urlopen(f"{MCP_BASE_URL}/build", timeout=5) as resp:
            build = json.loads(resp.read().decode())
    except Exception:
        build = {"version": "unknown", "build_sha": "unknown", "tools_available": []}
    
    return health, build

def generate_html(health, build):
    """Generate HTML with embedded data"""
    status = health.get("status", "unknown")
    status_class = "status-healthy" if status == "ok" else "status-degraded" if status == "degraded" else "status-error"
    
    version = build.get("version", "unknown")
    build_sha = build.get("build_sha", "unknown")[:12]
    tools = build.get("tools_available", [])
    tools_html = "".join([f'<div class="tool-tag">{t}</div>' for t in tools])
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>arifOS MCP — Constitutional Health</title>
    <meta name="description" content="arifOS Constitutional AI Governance System - Live deployment status">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #e8e8e8;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            text-align: center;
            padding: 40px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(90deg, #2ecc71, #3498db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #888; font-size: 1.1rem; }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 24px;
        }}
        .card-header {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #888;
            margin-bottom: 16px;
        }}
        .card-value {{
            font-size: 1.8rem;
            font-weight: 600;
            font-family: 'Courier New', monospace;
        }}
        .status-healthy {{ color: #2ecc71; }}
        .status-degraded {{ color: #f1c40f; }}
        .status-error {{ color: #e74c3c; }}
        .tools-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 10px;
        }}
        .tool-tag {{
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid rgba(46, 204, 113, 0.3);
            padding: 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-family: 'Courier New', monospace;
        }}
        footer {{
            text-align: center;
            padding: 40px;
            color: #555;
            border-top: 1px solid rgba(255,255,255,0.1);
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚖️ arifOS MCP</h1>
            <p class="subtitle">Constitutional AI Governance System</p>
            <p style="font-style: italic; color: #666; margin-top: 15px;">"Ditempa Bukan Diberi" — Forged, Not Given</p>
        </header>
        
        <div class="status-grid">
            <div class="card">
                <div class="card-header">● System Status</div>
                <div class="card-value {status_class}">{status.upper()}</div>
            </div>
            <div class="card">
                <div class="card-header">⚡ Version</div>
                <div class="card-value" style="font-size: 1.2rem;">{version}</div>
            </div>
            <div class="card">
                <div class="card-header">🔨 Build SHA</div>
                <div class="card-value" style="font-size: 1rem;">{build_sha}</div>
            </div>
            <div class="card">
                <div class="card-header">🛠️ Tools Available</div>
                <div class="card-value">{len(tools)}</div>
            </div>
        </div>
        
        <div class="card" style="margin-bottom: 20px;">
            <div class="card-header">🔧 Available Tools</div>
            <div class="tools-grid">{tools_html}</div>
        </div>
        
        <footer>
            <p>arifOS v{version} — Constitutional AI Governance</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p><a href="https://github.com/ariffazil/arifOS" style="color: #3498db;">GitHub</a></p>
        </footer>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    health, build = fetch_data()
    html = generate_html(health, build)
    print(html)
