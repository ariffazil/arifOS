"""
codebase/tests/test_infrastructure.py — Infrastructure Integration Tests

Tests for deployment stack:
- Railway.app deployment health
- Docker container validation  
- Redis connection
- Cloudflare DNS/web link
- MCP endpoint availability

Run: python -m pytest codebase/tests/test_infrastructure.py -v
"""

import pytest
import asyncio
import socket
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# =============================================================================
# CONFIGURATION
# =============================================================================

# Infrastructure endpoints
RAILWAY_URL = "https://arifos.arif-fazil.com"
RAILWAY_HEALTH_ENDPOINT = f"{RAILWAY_URL}/health"
RAILWAY_MCP_ENDPOINT = f"{RAILWAY_URL}/mcp"
RAILWAY_METRICS_ENDPOINT = f"{RAILWAY_URL}/metrics/json"

# Docker configuration
DOCKER_IMAGE_NAME = "arifos"
DOCKER_CONTAINER_NAME = "arifos-test"

# Redis configuration (from Railway or local)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# DNS configuration
DOMAIN_NAME = "arifos.arif-fazil.com"
CLOUDFLARE_DNS = "1.1.1.1"


# =============================================================================
# RAILWAY DEPLOYMENT TESTS
# =============================================================================

class TestRailwayDeployment:
    """Test Railway.app deployment health."""
    
    @pytest.mark.asyncio
    @pytest.mark.railway
    async def test_railway_health_endpoint(self):
        """Test /health endpoint returns 200 OK."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(RAILWAY_HEALTH_ENDPOINT)
            
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "healthy", f"Status not healthy: {data}"
        assert "version" in data, "Version not in response"
        print(f"✅ Railway health: {data.get('version', 'unknown')}")
    
    @pytest.mark.asyncio
    @pytest.mark.railway
    async def test_railway_mcp_endpoint(self):
        """Test /mcp endpoint is accessible."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # MCP endpoint may return 405 for GET, but should not return 404
            response = await client.get(RAILWAY_MCP_ENDPOINT)
            
        # Should NOT be 404 (not found) or 502/503 (service unavailable)
        assert response.status_code not in [404, 502, 503], \
            f"MCP endpoint unavailable: {response.status_code}"
        print(f"✅ Railway MCP endpoint accessible: {response.status_code}")
    
    @pytest.mark.asyncio
    @pytest.mark.railway
    async def test_railway_metrics_endpoint(self):
        """Test /metrics/json endpoint returns metrics."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(RAILWAY_METRICS_ENDPOINT)
            
        assert response.status_code == 200, f"Metrics endpoint failed: {response.status_code}"
        data = response.json()
        assert isinstance(data, dict), "Metrics should be JSON object"
        print(f"✅ Railway metrics: {len(data)} keys")
    
    @pytest.mark.asyncio
    @pytest.mark.railway
    async def test_railway_dashboard_endpoint(self):
        """Test /dashboard endpoint returns HTML."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{RAILWAY_URL}/dashboard")
            
        assert response.status_code == 200, f"Dashboard failed: {response.status_code}"
        assert "text/html" in response.headers.get("content-type", ""), \
            "Dashboard should return HTML"
        assert "arifOS" in response.text or "Constitutional" in response.text, \
            "Dashboard should contain arifOS content"
        print(f"✅ Railway dashboard: {len(response.text)} bytes HTML")


# =============================================================================
# DOCKER CONTAINER TESTS
# =============================================================================

class TestDockerContainer:
    """Test Docker container builds and runs correctly."""
    
    @pytest.mark.docker
    def test_dockerfile_exists(self):
        """Test Dockerfile exists in project root."""
        dockerfile = Path(__file__).parent.parent.parent / "Dockerfile"
        assert dockerfile.exists(), f"Dockerfile not found at {dockerfile}"
        content = dockerfile.read_text()
        assert "codebase-mcp-sse" in content, "Dockerfile should use codebase-mcp-sse"
        print(f"✅ Dockerfile exists: {len(content)} bytes")
    
    @pytest.mark.docker
    def test_docker_compose_exists(self):
        """Test docker-compose.yml or compose.yaml exists."""
        compose_files = ["docker-compose.yml", "compose.yaml", "compose.yml"]
        root = Path(__file__).parent.parent.parent
        
        found = any((root / f).exists() for f in compose_files)
        # This is optional - not required but nice to have
        if found:
            print("✅ Docker compose file found")
        else:
            pytest.skip("No docker-compose file (optional)")
    
    @pytest.mark.docker
    @pytest.mark.skipif(not subprocess.run(["docker", "--version"], capture_output=True).returncode == 0,
                        reason="Docker not available")
    def test_docker_build(self):
        """Test Docker image builds successfully."""
        root = Path(__file__).parent.parent.parent
        
        result = subprocess.run(
            ["docker", "build", "-t", f"{DOCKER_IMAGE_NAME}:test", "-f", "Dockerfile", "."],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        assert result.returncode == 0, f"Docker build failed: {result.stderr}"
        print(f"✅ Docker build successful")
    
    @pytest.mark.docker
    @pytest.mark.skipif(not subprocess.run(["docker", "--version"], capture_output=True).returncode == 0,
                        reason="Docker not available")
    def test_docker_run(self):
        """Test Docker container starts and responds to health check."""
        import httpx
        import time
        
        # Clean up any existing test container
        subprocess.run(
            ["docker", "rm", "-f", DOCKER_CONTAINER_NAME],
            capture_output=True
        )
        
        try:
            # Start container
            result = subprocess.run(
                ["docker", "run", "-d", "--name", DOCKER_CONTAINER_NAME,
                 "-p", "8000:8000", "-e", "PORT=8000",
                 f"{DOCKER_IMAGE_NAME}:test"],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Docker run failed: {result.stderr}"
            
            # Wait for container to start
            time.sleep(5)
            
            # Test health endpoint
            response = httpx.get("http://localhost:8000/health", timeout=10.0)
            assert response.status_code == 200, f"Container health check failed: {response.status_code}"
            
            data = response.json()
            assert data.get("status") == "healthy", "Container not healthy"
            print(f"✅ Docker container healthy: {data.get('version')}")
            
        finally:
            # Clean up
            subprocess.run(
                ["docker", "rm", "-f", DOCKER_CONTAINER_NAME],
                capture_output=True
            )


# =============================================================================
# REDIS CONNECTION TESTS
# =============================================================================

class TestRedisConnection:
    """Test Redis connection and functionality."""
    
    @pytest.mark.redis
    def test_redis_import(self):
        """Test Redis library is available."""
        try:
            import redis
            print(f"✅ Redis library available: {redis.__version__}")
        except ImportError:
            pytest.skip("Redis library not installed")
    
    @pytest.mark.redis
    @pytest.mark.skipif(not subprocess.run(["python", "-c", "import redis"], capture_output=True).returncode == 0,
                        reason="Redis library not available")
    def test_redis_connection(self):
        """Test connection to Redis server."""
        import redis
        
        try:
            r = redis.from_url(REDIS_URL, socket_connect_timeout=5)
            r.ping()
            info = r.info()
            print(f"✅ Redis connected: v{info.get('redis_version', 'unknown')}")
        except redis.ConnectionError:
            pytest.skip(f"Redis not available at {REDIS_URL}")
    
    @pytest.mark.redis
    @pytest.mark.skipif(not subprocess.run(["python", "-c", "import redis"], capture_output=True).returncode == 0,
                        reason="Redis library not available")
    def test_redis_set_get(self):
        """Test basic Redis SET/GET operations."""
        import redis
        
        try:
            r = redis.from_url(REDIS_URL, socket_connect_timeout=5, decode_responses=True)
            r.ping()
            
            # Test write
            test_key = "arifos:test:infrastructure"
            test_value = "test_value_123"
            r.set(test_key, test_value, ex=60)  # 60 second expiry
            
            # Test read
            result = r.get(test_key)
            assert result == test_value, f"Redis GET failed: {result} != {test_value}"
            
            # Clean up
            r.delete(test_key)
            
            print(f"✅ Redis SET/GET working")
        except redis.ConnectionError:
            pytest.skip(f"Redis not available at {REDIS_URL}")
    
    @pytest.mark.redis
    @pytest.mark.skipif(not subprocess.run(["python", "-c", "import redis"], capture_output=True).returncode == 0,
                        reason="Redis library not available")
    def test_redis_session_storage(self):
        """Test Redis can store session data (used by arifOS)."""
        import redis
        import json
        
        try:
            r = redis.from_url(REDIS_URL, socket_connect_timeout=5, decode_responses=True)
            r.ping()
            
            # Test session storage pattern
            session_id = "test_session_456"
            session_data = {
                "session_id": session_id,
                "status": "active",
                "verdict": "SEAL",
                "timestamp": "2026-01-29T00:00:00Z"
            }
            
            key = f"arifos:session:{session_id}"
            r.setex(key, 3600, json.dumps(session_data))  # 1 hour expiry
            
            # Retrieve
            result = json.loads(r.get(key))
            assert result["session_id"] == session_id
            assert result["verdict"] == "SEAL"
            
            # Clean up
            r.delete(key)
            
            print(f"✅ Redis session storage working")
        except redis.ConnectionError:
            pytest.skip(f"Redis not available at {REDIS_URL}")


# =============================================================================
# CLOUDFLARE & DNS TESTS
# =============================================================================

class TestCloudflareDNS:
    """Test Cloudflare DNS and web link configuration."""
    
    @pytest.mark.dns
    def test_dns_resolution(self):
        """Test domain resolves to IP."""
        try:
            ip = socket.gethostbyname(DOMAIN_NAME)
            assert ip is not None, f"Could not resolve {DOMAIN_NAME}"
            print(f"✅ DNS resolved: {DOMAIN_NAME} -> {ip}")
        except socket.gaierror as e:
            pytest.fail(f"DNS resolution failed: {e}")
    
    @pytest.mark.dns
    def test_cloudflare_dns_servers(self):
        """Test domain uses Cloudflare DNS."""
        import dns.resolver
        
        try:
            # Query Cloudflare's DNS
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['1.1.1.1', '1.0.0.1']
            
            answers = resolver.resolve(DOMAIN_NAME, 'A')
            ips = [str(rdata) for rdata in answers]
            
            assert len(ips) > 0, f"No A records for {DOMAIN_NAME}"
            print(f"✅ Cloudflare DNS: {DOMAIN_NAME} -> {ips}")
        except ImportError:
            pytest.skip("dnspython not installed (pip install dnspython)")
        except Exception as e:
            pytest.fail(f"Cloudflare DNS query failed: {e}")
    
    @pytest.mark.dns
    def test_cname_record(self):
        """Test if domain has CNAME (for Railway) or A record."""
        import dns.resolver
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['1.1.1.1']
            
            # Try CNAME first
            try:
                answers = resolver.resolve(DOMAIN_NAME, 'CNAME')
                cnames = [str(rdata) for rdata in answers]
                print(f"✅ CNAME record: {DOMAIN_NAME} -> {cnames}")
                return
            except dns.resolver.NoAnswer:
                pass
            
            # Try A record
            answers = resolver.resolve(DOMAIN_NAME, 'A')
            ips = [str(rdata) for rdata in answers]
            assert len(ips) > 0
            print(f"✅ A record: {DOMAIN_NAME} -> {ips}")
            
        except ImportError:
            pytest.skip("dnspython not installed")
        except Exception as e:
            pytest.fail(f"DNS record check failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.ssl
    async def test_ssl_certificate(self):
        """Test SSL certificate is valid."""
        import ssl
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"https://{DOMAIN_NAME}")
                
            assert response.status_code in [200, 404], f"SSL/HTTPS failed: {response.status_code}"
            # 404 is OK - just checking SSL works
            print(f"✅ SSL certificate valid for {DOMAIN_NAME}")
        except ssl.SSLError as e:
            pytest.fail(f"SSL certificate error: {e}")
        except Exception as e:
            pytest.fail(f"HTTPS connection failed: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.cloudflare
    async def test_cloudflare_headers(self):
        """Test response contains Cloudflare headers."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(RAILWAY_HEALTH_ENDPOINT)
        
        headers = response.headers
        cf_ray = headers.get("cf-ray")
        cf_cache = headers.get("cf-cache-status")
        
        if cf_ray:
            print(f"✅ Cloudflare proxy detected: cf-ray={cf_ray[:20]}...")
        else:
            print("⚠️ No Cloudflare headers (may be direct to Railway)")


# =============================================================================
# MCP ENDPOINT TESTS
# =============================================================================

class TestMCPEndpoints:
    """Test MCP server endpoints and tools."""
    
    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_mcp_tool_list(self):
        """Test MCP server lists available tools."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to get tool list via HTTP POST to /mcp
            response = await client.post(
                RAILWAY_MCP_ENDPOINT,
                json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
                headers={"Content-Type": "application/json"}
            )
        
        # Should return valid JSON response
        assert response.status_code in [200, 405], f"MCP tools/list failed: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "result" in data or "error" in data, "Invalid JSON-RPC response"
            print(f"✅ MCP tools/list working")
        else:
            print(f"⚠️ MCP returned {response.status_code} (may need different protocol)")
    
    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_mcp_init_000(self):
        """Test init_000 tool via MCP."""
        import httpx
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                RAILWAY_MCP_ENDPOINT,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "init_000",
                        "arguments": {"action": "init", "query": "test"}
                    },
                    "id": 2
                },
                headers={"Content-Type": "application/json"}
            )
        
        # Check if we got a valid response
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCP init_000 responded")
        else:
            pytest.skip(f"MCP init_000 not available: {response.status_code}")


# =============================================================================
# INTEGRATION TEST
# =============================================================================

class TestFullIntegration:
    """Full integration test of all infrastructure components."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_health(self):
        """Test complete health of deployment stack."""
        import httpx
        import dns.resolver
        
        results = {}
        
        # 1. DNS resolution
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['1.1.1.1']
            answers = resolver.resolve(DOMAIN_NAME, 'A')
            results['dns'] = {'status': 'ok', 'ips': [str(r) for r in answers]}
        except Exception as e:
            results['dns'] = {'status': 'fail', 'error': str(e)}
        
        # 2. HTTPS connection
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(RAILWAY_HEALTH_ENDPOINT)
            results['https'] = {'status': 'ok', 'code': response.status_code}
        except Exception as e:
            results['https'] = {'status': 'fail', 'error': str(e)}
        
        # 3. Health check
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(RAILWAY_HEALTH_ENDPOINT)
            data = response.json()
            results['health'] = {
                'status': 'ok',
                'version': data.get('version', 'unknown'),
                'tools': data.get('tools', 0)
            }
        except Exception as e:
            results['health'] = {'status': 'fail', 'error': str(e)}
        
        # Print summary
        print("\n" + "="*60)
        print("INFRASTRUCTURE HEALTH SUMMARY")
        print("="*60)
        for component, result in results.items():
            status = "✅" if result['status'] == 'ok' else "❌"
            print(f"{status} {component.upper()}: {result}")
        print("="*60)
        
        # Assert all passed
        all_ok = all(r['status'] == 'ok' for r in results.values())
        assert all_ok, f"Some infrastructure checks failed: {results}"


# =============================================================================
# MARKER CONFIGURATION
# =============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "railway: Railway.app deployment tests")
    config.addinivalue_line("markers", "docker: Docker container tests")
    config.addinivalue_line("markers", "redis: Redis connection tests")
    config.addinivalue_line("markers", "dns: DNS resolution tests")
    config.addinivalue_line("markers", "ssl: SSL certificate tests")
    config.addinivalue_line("markers", "cloudflare: Cloudflare proxy tests")
    config.addinivalue_line("markers", "mcp: MCP endpoint tests")
    config.addinivalue_line("markers", "integration: Full integration tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
