"""
arifOS Dashboard Metrics Aggregator
Collects and aggregates metrics from all 22 servers, containers, MCP services, netdata, uptime-kuma.
Provides unified JSON API for React dashboard.
"""

import asyncio
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any

import aiohttp
import docker
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket

# Configuration
NETDATA_URL = "http://localhost:19999"
UPTIME_KUMA_URL = "http://localhost:3001"
MCP_SSE_URL = "http://localhost:8088"
MCP_STREAMABLE_URL = "http://localhost:8889"
DOCKER_SOCKET = "unix://var/run/docker.sock"

# 22 Server definitions (from earlier discovery)
SERVERS = [
    {"name": "nginx", "port": 80, "type": "web", "health_path": "/"},
    {"name": "nginx-ssl", "port": 443, "type": "web", "health_path": "/"},
    {"name": "cupsd", "port": 631, "type": "service", "check": "tcp"},
    {"name": "postgresql", "port": 5432, "type": "database", "check": "tcp"},
    {"name": "redis", "port": 6379, "type": "database", "check": "tcp"},
    {"name": "aaa_mcp_sse", "port": 8088, "type": "mcp", "health_path": "/health"},
    {"name": "aaa_mcp_streamable", "port": 8889, "type": "mcp", "health_path": "/health"},
    {"name": "netdata", "port": 19999, "type": "monitoring", "health_path": "/api/v1/data"},
    {"name": "uptime-kuma", "port": 3001, "type": "monitoring", "health_path": "/api/status-page"},
    {"name": "vaultwarden", "port": 8000, "type": "container", "health_path": "/"},
    {"name": "portainer", "port": 9000, "type": "container", "health_path": "/api/status"},
    {"name": "qdrant", "port": 6333, "type": "container", "health_path": "/health"},
    {"name": "openclaw-gateway", "port": 3000, "type": "container", "health_path": "/"},
    {"name": "AGI_bot", "port": None, "type": "process", "check": "process"},
    {"name": "SearXNG", "port": 8880, "type": "container", "health_path": "/"},
    {"name": "arifos-mcp", "port": None, "type": "container", "check": "process"},
    {"name": "agent-zero", "port": None, "type": "container", "check": "process"},
    {"name": "streamable-http", "port": 8889, "type": "process", "health_path": "/health"},
    {"name": "arifos-dashboard", "port": 3000, "type": "process", "health_path": "/"},
    {"name": "PM2", "port": None, "type": "process", "check": "process"},
    {"name": "docker-daemon", "port": 2375, "type": "service", "check": "tcp"},
    {"name": "ssh", "port": 22, "type": "service", "check": "tcp"},
]


@dataclass
class ServerStatus:
    name: str
    type: str
    port: int | None
    online: bool = False
    latency_ms: float | None = None
    last_checked: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContainerStatus:
    name: str
    id: str
    status: str
    image: str
    created: str
    ports: list[str]


@dataclass
class AggregatedMetrics:
    timestamp: float
    servers: list[ServerStatus]
    containers: list[ContainerStatus]
    constitutional: dict[str, Any]
    system: dict[str, Any]
    uptime_kuma: dict[str, Any]
    netdata: dict[str, Any]


class MetricsAggregator:
    def __init__(self):
        self.docker_client = docker.DockerClient(base_url=DOCKER_SOCKET)
        self.session: aiohttp.ClientSession | None = None

    async def start(self):
        self.session = aiohttp.ClientSession()

    async def stop(self):
        if self.session:
            await self.session.close()

    async def check_server(self, server: dict) -> ServerStatus:
        """Check if a server is reachable."""
        status = ServerStatus(name=server["name"], type=server["type"], port=server["port"])
        check_type = server.get("check", "http")
        health_path = server.get("health_path", "/")

        if server["port"] is None or check_type == "process":
            # Process check via ps? For now assume online
            status.online = True
            return status

        start = time.time()
        online = False
        try:
            if check_type == "tcp":
                # TCP port check
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection("localhost", server["port"]), timeout=2
                )
                writer.close()
                await writer.wait_closed()
                online = True
            else:  # http
                url = f"http://localhost:{server['port']}{health_path}"
                async with self.session.get(url, timeout=2) as resp:
                    online = resp.status < 500
        except (aiohttp.ClientError, asyncio.TimeoutError, ConnectionRefusedError, OSError):
            online = False
        status.online = online
        status.latency_ms = (time.time() - start) * 1000
        status.last_checked = time.time()
        return status

    async def get_servers_status(self) -> list[ServerStatus]:
        """Check status of all defined servers."""
        tasks = [self.check_server(s) for s in SERVERS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        statuses = []
        for r in results:
            if isinstance(r, Exception):
                # Create offline status
                continue
            statuses.append(r)
        return statuses

    async def get_containers_status(self) -> list[ContainerStatus]:
        """Get Docker container status."""
        containers = []
        try:
            for container in self.docker_client.containers.list(all=True):
                ports = []
                if (
                    "NetworkSettings" in container.attrs
                    and "Ports" in container.attrs["NetworkSettings"]
                ):
                    port_mapping = container.attrs["NetworkSettings"]["Ports"]
                    if isinstance(port_mapping, dict):
                        for container_port, bindings in port_mapping.items():
                            if bindings:
                                for binding in bindings:
                                    host_port = binding.get("HostPort", "")
                                    ports.append(f"{host_port}:{container_port}")
                containers.append(
                    ContainerStatus(
                        name=container.name,
                        id=container.short_id,
                        status=container.status,
                        image=container.image.tags[0] if container.image.tags else "unknown",
                        created=container.attrs["Created"],
                        ports=ports,
                    )
                )
        except Exception as e:
            print(f"Error fetching containers: {e}")
        return containers

    async def get_constitutional_metrics(self) -> dict[str, Any]:
        """Fetch constitutional metrics from MCP servers."""
        metrics = {}
        # Try SSE server health
        try:
            async with self.session.get(f"{MCP_SSE_URL}/health", timeout=2) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    metrics["sse"] = data
        except Exception:
            pass
        # Try streamable server health
        try:
            async with self.session.get(f"{MCP_STREAMABLE_URL}/health", timeout=2) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    metrics["streamable"] = data
        except Exception:
            pass
        # Compute constitutional metrics using core functions

        return metrics

    async def get_netdata_metrics(self) -> dict[str, Any]:
        """Fetch system metrics from netdata."""
        try:
            async with self.session.get(
                f"{NETDATA_URL}/api/v1/data?chart=system.cpu", timeout=5
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return {}

    async def get_uptime_kuma_status(self) -> dict[str, Any]:
        """Fetch status page from uptime-kuma."""
        try:
            async with self.session.get(f"{UPTIME_KUMA_URL}/api/status-page", timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return {}

    async def get_system_metrics(self) -> dict[str, Any]:
        """Get basic system metrics (CPU, memory, disk) via netdata or psutil."""
        # Use netdata for now
        return await self.get_netdata_metrics()

    async def get_system_summary(self) -> dict[str, Any]:
        """Get summarized system metrics for dashboard."""
        try:
            # Try netdata first
            async with self.session.get(
                f"{NETDATA_URL}/api/v1/data?chart=system.cpu", timeout=5
            ) as resp:
                if resp.status == 200:
                    cpu_data = await resp.json()
                    # Sum all CPU dimensions for total usage percentage
                    cpu_percent = 0.0
                    if (
                        "data" in cpu_data
                        and isinstance(cpu_data["data"], list)
                        and len(cpu_data["data"]) > 0
                    ):
                        # Each dimension is a list of values; take the latest
                        for dim_name, dim_values in cpu_data.get("labels", {}).items():
                            if dim_name != "time" and dim_name in cpu_data.get("data", [])[0]:
                                idx = cpu_data["labels"].index(dim_name)
                                latest = cpu_data["data"][0][idx]
                                if isinstance(latest, (int, float)):
                                    cpu_percent += latest
                    cpu_percent = min(cpu_percent, 100.0)
                else:
                    cpu_percent = 0.0
        except Exception:
            cpu_percent = 0.0

        try:
            async with self.session.get(
                f"{NETDATA_URL}/api/v1/data?chart=system.ram", timeout=5
            ) as resp:
                if resp.status == 200:
                    mem_data = await resp.json()
                    # Calculate memory used percent
                    if "data" in mem_data and mem_data["data"] and len(mem_data["data"][0]) >= 3:
                        used = mem_data["data"][0][1]  # assuming second column is used
                        total = mem_data["data"][0][2]  # third column is total
                        memory_percent = (used / total * 100) if total > 0 else 0.0
                    else:
                        memory_percent = 0.0
                else:
                    memory_percent = 0.0
        except Exception:
            memory_percent = 0.0

        try:
            async with self.session.get(
                f"{NETDATA_URL}/api/v1/data?chart=system.load", timeout=5
            ) as resp:
                if resp.status == 200:
                    load_data = await resp.json()
                    if "data" in load_data and load_data["data"] and len(load_data["data"][0]) >= 4:
                        load_1 = load_data["data"][0][1]  # 1min load
                        load_5 = load_data["data"][0][2]  # 5min load
                        load_15 = load_data["data"][0][3]  # 15min load
                        load_avg = [load_1, load_5, load_15]
                    else:
                        load_avg = [0.0, 0.0, 0.0]
                else:
                    load_avg = [0.0, 0.0, 0.0]
        except Exception:
            load_avg = [0.0, 0.0, 0.0]

        # Disk usage - approximate via netdata disk space chart
        disk_percent = 0.0
        try:
            async with self.session.get(
                f"{NETDATA_URL}/api/v1/data?chart=disk_space._", timeout=5
            ) as resp:
                if resp.status == 200:
                    disk_data = await resp.json()
                    if "data" in disk_data and disk_data["data"] and len(disk_data["data"][0]) >= 3:
                        used = disk_data["data"][0][1]
                        total = disk_data["data"][0][2]
                        disk_percent = (used / total * 100) if total > 0 else 0.0
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            ZeroDivisionError,
        ):
            disk_percent = 0.0

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "load_avg": load_avg,
            "timestamp": time.time(),
        }

    async def aggregate_all(self) -> AggregatedMetrics:
        """Aggregate all metrics."""
        servers = await self.get_servers_status()
        containers = await self.get_containers_status()
        constitutional = await self.get_constitutional_metrics()
        netdata = await self.get_netdata_metrics()
        uptime_kuma = await self.get_uptime_kuma_status()
        system = await self.get_system_metrics()

        return AggregatedMetrics(
            timestamp=time.time(),
            servers=servers,
            containers=containers,
            constitutional=constitutional,
            system=system,
            uptime_kuma=uptime_kuma,
            netdata=netdata,
        )


# Global aggregator instance
aggregator = MetricsAggregator()


# Starlette app
async def homepage(request: Request):
    return JSONResponse(
        {
            "name": "arifOS Dashboard Aggregator",
            "version": "1.0",
            "endpoints": {
                "/": "this info",
                "/api/health": "aggregated health status",
                "/api/metrics": "all aggregated metrics",
                "/api/servers": "server statuses",
                "/api/containers": "container statuses",
                "/api/constitutional": "constitutional metrics",
                "/api/netdata": "netdata metrics",
                "/api/uptime-kuma": "uptime-kuma status",
                "/ws": "WebSocket for real-time updates",
            },
        }
    )


async def health(request: Request):
    """Overall health endpoint."""
    servers = await aggregator.get_servers_status()
    online = sum(1 for s in servers if s.online)
    total = len(servers)
    constitutional = await aggregator.get_constitutional_metrics()
    return JSONResponse(
        {
            "status": "healthy" if online > total * 0.8 else "degraded",
            "online_servers": online,
            "total_servers": total,
            "timestamp": time.time(),
            "constitutional_metrics": {
                "truth": constitutional.get("truth", 0.0),
                "empathy": constitutional.get("empathy", 0.0),
                "vitality": constitutional.get("vitality", 0.0),
                "clarity": constitutional.get("clarity", 0.0),
                "floor_scores": constitutional.get("floor_scores", {}),
            },
        }
    )


async def metrics(request: Request):
    """All aggregated metrics."""
    data = await aggregator.aggregate_all()
    # Convert dataclasses to dicts
    return JSONResponse(
        {
            "timestamp": data.timestamp,
            "servers": [asdict(s) for s in data.servers],
            "containers": [asdict(c) for c in data.containers],
            "constitutional": data.constitutional,
            "system": data.system,
            "uptime_kuma": data.uptime_kuma,
            "netdata": data.netdata,
        }
    )


async def servers(request: Request):
    """Server statuses only."""
    servers = await aggregator.get_servers_status()
    return JSONResponse([asdict(s) for s in servers])


async def containers(request: Request):
    """Container statuses only."""
    containers = await aggregator.get_containers_status()
    return JSONResponse([asdict(c) for c in containers])


async def constitutional(request: Request):
    """Constitutional metrics only."""
    metrics = await aggregator.get_constitutional_metrics()
    return JSONResponse(metrics)


async def netdata(request: Request):
    """Netdata metrics."""
    metrics = await aggregator.get_netdata_metrics()
    return JSONResponse(metrics)


async def uptime_kuma(request: Request):
    """Uptime-kuma status."""
    status = await aggregator.get_uptime_kuma_status()
    return JSONResponse(status)


async def system(request: Request):
    """System metrics summary."""
    metrics = await aggregator.get_system_summary()
    return JSONResponse(metrics)


async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    try:
        while True:
            data = await aggregator.aggregate_all()
            await websocket.send_json(
                {
                    "timestamp": data.timestamp,
                    "servers": [asdict(s) for s in data.servers],
                    "containers": [asdict(c) for c in data.containers],
                    "constitutional": data.constitutional,
                }
            )
            await asyncio.sleep(5)  # update every 5 seconds
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


routes = [
    Route("/", homepage),
    Route("/api/health", health),
    Route("/api/metrics", metrics),
    Route("/api/servers", servers),
    Route("/api/containers", containers),
    Route("/api/constitutional", constitutional),
    Route("/api/netdata", netdata),
    Route("/api/uptime-kuma", uptime_kuma),
    Route("/api/system", system),
    WebSocketRoute("/ws", websocket_endpoint),
]

app = Starlette(routes=routes)


@app.on_event("startup")
async def startup():
    await aggregator.start()


@app.on_event("shutdown")
async def shutdown():
    await aggregator.stop()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3002, log_level="info")
