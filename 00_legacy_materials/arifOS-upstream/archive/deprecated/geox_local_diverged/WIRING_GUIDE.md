# GEOX ↔ arifOS Wiring Guide
## "Plugging the Earth Coprocessor into the Constitutional Kernel"

> DITEMPA BUKAN DIBERI

---

## 1. Create the HuggingFace Hub Repo

The HF files are ready in `/home/user/workspace/geox-hub/`. Run these commands on your VPS or local machine:

```bash
# Install huggingface_hub
pip install huggingface_hub

# Login (use your HF token from https://huggingface.co/settings/tokens)
huggingface-cli login

# Create the dataset repo
python3 - << 'EOF'
from huggingface_hub import HfApi
api = HfApi()
api.create_repo(
    repo_id="ariffazil/geox-hub",
    repo_type="dataset",
    exist_ok=True,
    private=False,
)
print("Repo created: https://huggingface.co/datasets/ariffazil/geox-hub")
EOF

# Clone and push the hub files
git clone https://huggingface.co/datasets/ariffazil/geox-hub geox-hub-remote
cp -r /path/to/geox-hub/* geox-hub-remote/
cd geox-hub-remote
git add -A
git commit -m "feat: GEOX schemas, configs, notebooks, examples"
git push
```

---

## 2. Install GEOX on Your VPS

```bash
# SSH into srv1325122.hstgr.cloud
ssh your-vps

# Clone the repo
git clone https://github.com/ariffazil/arifos-geox.git /opt/arifos/geox

# Install into your arifOS Python environment
cd /opt/arifos/geox
pip install -e ".[dev]"

# Verify install
python3 -c "from arifos.geox import GeoXAgent, GeoXConfig; print('GEOX OK')"
```

---

## 3. Add GEOX to Docker Compose

In your arifOS `docker-compose.yml` (at `/opt/arifos/`), add:

```yaml
services:
  # ... existing services ...

  geox_server:
    image: python:3.11-slim
    container_name: geox_server
    working_dir: /app
    volumes:
      - /opt/arifos/geox:/app
      - /opt/arifos/logs:/app/logs
    command: >
      sh -c "pip install -e '.[dev]' -q &&
             python arifos/geox/geox_mcp_server.py"
    ports:
      - "8100:8100"
    environment:
      - GEOX_ARIFOS_KERNEL_URL=http://arifosmcp:8000/mcp
      - GEOX_QDRANT_URL=http://qdrant:6333
      - GEOX_LOG_LEVEL=INFO
    depends_on:
      - arifosmcp
      - qdrant
    restart: unless-stopped
    networks:
      - arifos_network
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.geox.rule=Host(`geox.arif-fazil.com`)"
      - "traefik.http.services.geox.loadbalancer.server.port=8100"
```

```bash
# Deploy
cd /opt/arifos
docker compose up -d geox_server
docker compose logs -f geox_server
```

---

## 4. Register GEOX in arifOS MCP Registry

In your arifOS configuration (wherever your MCP server registry is defined — likely `config/mcp_servers.yaml` or equivalent), add:

```yaml
# /opt/arifos/config/mcp_servers.yaml
mcp_servers:
  # ... existing servers ...

  - name: geox
    description: "GEOX — Geological Intelligence Coprocessor"
    url: http://geox_server:8100/mcp
    tools:
      - name: geox_evaluate_prospect
        description: "Run a governed geological prospect evaluation"
      - name: geox_query_memory
        description: "Query geological memory store by basin or prospect"
      - name: geox_health
        description: "GEOX server health check"
    auth: none
    timeout_seconds: 120
    enabled: true
```

---

## 5. Inject arifOS Kernel into GeoXAgent

In production, wire arifOS's `agi_mind` and `vault_ledger` into the agent:

```python
# production_bootstrap.py
import httpx
import asyncio
from arifos.geox.geox_agent import GeoXAgent, GeoXConfig
from arifos.geox.geox_validator import GeoXValidator
from arifos.geox.geox_memory import GeoMemoryStore
from arifos.geox.geox_tools import ToolRegistry

arifosmcp_URL = "http://arifosmcp:8000/mcp"

async def call_arifos_tool(tool_name: str, arguments: dict) -> str:
    """Adapter: calls any arifOS MCP tool by name."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{arifosmcp_URL}",
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }
        )
        result = resp.json()
        return result.get("result", {}).get("content", [{}])[0].get("text", "")


async def arifos_llm_planner(query: str, context: dict) -> str:
    """Injects arifOS agi_mind(333) as GEOX's LLM planner."""
    prompt = f"""
You are the arifOS agi_mind geological planning module (333 EXPLORE).
Plan a tool sequence for this geological query.
Available tools: EarthModelTool, EOFoundationModelTool, SeismicVLMTool, SimulatorTool, GeoRAGTool

Query: {query}
Context: {context}

Return a JSON list of tool names in execution order.
Example: ["EarthModelTool", "SimulatorTool", "GeoRAGTool"]
"""
    response = await call_arifos_tool("agi_mind", {"query": prompt, "depth": "333"})
    # Parse tool list from response
    import re, json
    match = re.search(r'\[.*?\]', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    # Fallback: default geological sequence
    return ["EarthModelTool", "SimulatorTool", "GeoRAGTool"]


async def arifos_vault_seal(audit_record: dict) -> None:
    """Injects arifOS vault_ledger(999) as GEOX's audit sink."""
    await call_arifos_tool("vault_ledger", {
        "action": "seal",
        "record": audit_record,
        "source": "GEOX",
        "stage": "999_SEAL",
    })


async def create_production_agent() -> GeoXAgent:
    """Build a GeoXAgent fully wired to the arifOS kernel."""
    config = GeoXConfig(
        lem_confidence_threshold=0.75,
        allowed_tools=["EarthModelTool", "EOFoundationModelTool", "SeismicVLMTool", "SimulatorTool", "GeoRAGTool"],
        provenance_required=True,
    )

    # Production tool registry (plug in real LEM/VLM adapters here)
    registry = ToolRegistry.default_registry()

    # Qdrant memory (same cluster as arifOS M4)
    from qdrant_client import QdrantClient
    qdrant = QdrantClient(url="http://qdrant:6333")
    memory = GeoMemoryStore(qdrant_client=qdrant)

    return GeoXAgent(
        config=config,
        tool_registry=registry,
        validator=GeoXValidator(),
        llm_planner=arifos_llm_planner,
        audit_sink=arifos_vault_seal,
        memory_store=memory,
    )
```

---

## 6. Minimal evaluate_prospect Call

```python
import asyncio
from datetime import datetime, timezone
from arifos.geox.geox_schemas import CoordinatePoint, GeoRequest

async def main():
    agent = await create_production_agent()

    request = GeoRequest(
        query="Evaluate HC prospectivity of Blok Selatan structural closure",
        prospect_name="Blok Selatan",
        location=CoordinatePoint(latitude=4.5, longitude=104.2, depth_m=2800.0),
        basin="Malay Basin",
        play_type="structural",
        available_data=["seismic_2d", "well_logs", "eo"],
        risk_tolerance="medium",
        requester_id="ariffazil_888_JUDGE",
        timestamp=datetime.now(timezone.utc),
    )

    response = await agent.evaluate_prospect(request)

    print(f"Verdict: {response.verdict}")
    print(f"Confidence: {response.confidence_aggregate:.2f}")
    print(f"Hold: {response.arifos_telemetry['hold']}")
    print(f"Human Signoff Required: {response.human_signoff_required}")
    print(f"\narifOS Telemetry:")
    for k, v in response.arifos_telemetry.items():
        print(f"  {k}: {v}")

asyncio.run(main())
```

---

## 7. Verify the MCP Connection

```bash
# Test GEOX health from inside Docker network
docker exec arifosmcp curl -s http://geox_server:8100/health

# Test tools/list
curl -s -X POST http://localhost:8100/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 -m json.tool

# Test evaluate_prospect via MCP
curl -s -X POST http://localhost:8100/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":2,
    "method":"tools/call",
    "params":{
      "name":"geox_evaluate_prospect",
      "arguments":{
        "request":{
          "query":"Test prospect evaluation",
          "prospect_name":"Test Prospect",
          "location":{"latitude":4.5,"longitude":104.2,"depth_m":2500.0,"crs":"EPSG:4326"},
          "basin":"Malay Basin",
          "play_type":"structural",
          "available_data":["seismic_2d"],
          "risk_tolerance":"low",
          "requester_id":"test_user"
        }
      }
    }
  }' | python3 -m json.tool
```

---

## 8. arifOS Routing — Let agi_mind Discover GEOX

Once GEOX is registered in the MCP registry, arifOS's `agi_mind(333)` can autonomously call GEOX for geological queries:

```
User query: "Evaluate the Sabah Basin for gas prospectivity"
    │
    ▼
arifOS init_anchor(000) — session established
    │
    ▼
arifOS physics_reality(111) — searches for Sabah Basin geological data
    │
    ▼
arifOS agi_mind(333) — recognizes geological domain
    │  discovers geox_evaluate_prospect in MCP registry
    ▼
geox_evaluate_prospect called with GeoRequest
    │
    ▼
GEOX runs Earth→Language pipeline
    │
    ▼
GeoResponse returned with SEAL/PARTIAL/SABAR/VOID + telemetry
    │
    ▼
arifOS vault_ledger(999) — seals the full audit trail
    │
    ▼
User receives governed geological intelligence
```

---

## 9. ops/ Kubernetes Reference

A minimal Kubernetes deployment is at `ops/k8s/`. For your current Hostinger VPS setup, Docker Compose is sufficient. The k8s manifests are provided for when GEOX scales to multi-node.

```bash
# k8s deploy (future)
kubectl apply -f ops/k8s/
kubectl get pods -l app=geox
```

---

## 10. Quick Reference

| Action | Command |
|--------|---------|
| Run tests | `PYTHONPATH=/opt/arifos/geox/arifos python -m pytest tests/` |
| Start server | `python arifos/geox/geox_mcp_server.py` |
| Run demo | `PYTHONPATH=arifos python arifos/geox/examples/geox_malay_basin_demo.py` |
| GitHub repo | https://github.com/ariffazil/arifos-geox |
| HF hub | https://huggingface.co/datasets/ariffazil/geox-hub |
| MCP port | 8100 |
| arifOS port | 8000 |

---

```
arifOS telemetry v2.1 | pipeline 999 SEAL | floors F1·F4·F7
confidence CLAIM | P2 1.0 | hold CLEAR | uncertainty [0.03, 0.15]
DITEMPA BUKAN DIBERI
```
