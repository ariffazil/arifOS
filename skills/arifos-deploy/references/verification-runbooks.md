# Verification Runbooks — Exact Checks for Every Surface

These are the exact verification steps for each surface. Run these in order. Every step must return the expected result before the surface is considered verified.

---

## Hub — arifOS-fazil.com

### Step 1: Homepage Verification

```bash
curl -s -o /dev/null -w "%{http_code}" https://arifOS-fazil.com/
# Expected: 200
curl -s https://arifOS-fazil.com/ | grep -o "<title>.*</title>"
# Expected: <title>arifOS — Constitutional Intelligence Kernel</title>
```

### Step 2: Machine File — llms.txt

```bash
curl -s -o /dev/null -w "%{http_code} %{content_type}" https://arifOS-fazil.com/llms.txt
# Expected: 200 text/plain; charset=utf-8
curl -s https://arifOS-fazil.com/llms.txt | head -5
# Expected: First lines of llms.txt, plain text
```

### Step 3: Machine File — agent.json

```bash
curl -s -o /dev/null -w "%{http_code} %{content type}" https://arifOS-fazil.com/.well-known/agent.json
# Expected: 200 application/json
curl -s https://arifOS-fazil.com/.well-known/agent.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['name'], d['version'])"
# Expected: arifOS 2026.03.25
```

### Step 4: Machine File — robots.txt

```bash
curl -s -o /dev/null -w "%{http_code}" https://arifOS-fazil.com/robots.txt
# Expected: 200
curl -s https://arifOS-fazil.com/robots.txt | grep -i sitemap
# Expected: Sitemap: https://arifOS-fazil.com/sitemap.xml
```

### Step 5: Machine File — sitemap.xml

```bash
curl -s -o /dev/null -w "%{http_code}" https://arifOS-fazil.com/sitemap.xml
# Expected: 200
curl -s https://arifOS-fazil.com/sitemap.xml | grep -o '<?xml'
# Expected: <?xml
```

### Step 6: CSS Asset

```bash
curl -s -o /dev/null -w "%{http_code} %{content type}" https://arifOS-fazil.com/assets/style.css
# Expected: 200 text/css
```

### Step 7: Links to Docs — Outbound Check

```bash
curl -s https://arifOS-fazil.com/ | grep -o 'https://arifos.arifOS-fazil.com[^"]*'
# Expected: Links to docs domain appear
```

---

## Docs — arifos.arifOS-fazil.com

### Step 1: Homepage Verification

```bash
curl -s -o /dev/null -w "%{http_code}" https://arifos.arifOS-fazil.com/
# Expected: 200
```

### Step 2: Docs Content Check

```bash
curl -s https://arifos.arifOS-fazil.com/ | grep -o "<title>.*</title>"
# Expected: Title reflects docs content, not hub content
```

### Step 3: No Hub Content on Docs

```bash
# Docs should NOT contain full hub-style summaries
curl -s https://arifos.arifOS-fazil.com/ | grep -i "I build governed AI"
# Expected: No match (hub content, not docs content)
```

---

## Runtime — arifOS:8080/mcp

### Step 1: Health Check

```bash
curl -s https://arifOSmcp.arifOS-fazil.com/health
# Expected: JSON with status, tools_loaded, version
curl -s -o /dev/null -w "%{http_code}" https://arifOSmcp.arifOS-fazil.com/health
# Expected: 200
```

### Step 2: MCP Endpoint

```bash
curl -s -X POST https://arifOSmcp.arifOS-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"init_anchor","arguments":{"mode":"status","declared_name":"TestAgent"}},"id":1}'
# Expected: JSON response with verdict field
```

### Step 3: Container Status (if VPS accessible)

```bash
ssh arifos "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep arifOS"
# Expected: arifOS container in healthy/Up state
```

---

## Machine File Verification Checklist

After any hub deploy, verify ALL of these before marking deploy complete:

- [ ] `curl /llms.txt` → 200, Content-Type: text/plain
- [ ] `curl /.well-known/agent.json` → 200, Content-Type: application/json
- [ ] `curl /robots.txt` → 200
- [ ] `curl /sitemap.xml` → 200
- [ ] llms.txt content contains no HTML tags
- [ ] agent.json is valid JSON and parses correctly
- [ ] agent.json mcpServers.arifos.url points to correct MCP endpoint
- [ ] No machine files return HTML or redirect

---

## Post-Deploy Verification for Content Updates

After any content deploy:

1. Fetch the changed page — confirm HTTP 200
2. Confirm title and meta description are correct
3. Check for broken links on the changed page (at minimum: links to other arifOS surfaces)
4. Confirm machine files unaffected — no Content-Type change on llms.txt or agent.json
5. If sitemap changed — verify valid XML

---

## Failure States and Responses

| Check | Failure | Response |
|-------|---------|---------|
| Homepage → non-200 | Deploy failed or wrong file served | Rollback to previous deploy |
| llms.txt → non-200 or HTML | SPA routing swallowed .txt | Deploy failed — 888_HOLD, surface not suitable |
| llms.txt → wrong Content-Type | Hosting platform issue | 888_HOLD, surface not suitable |
| agent.json → non-200 or HTML | SPA routing swallowed .json | Deploy failed — surface not suitable |
| Health check → non-200 | Runtime down | Rollback runtime deploy, alert |
| CSS → 404 | Asset not deployed | Redeploy with correct asset path |
