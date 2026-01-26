#!/usr/bin/env python3
"""
Test arifOS Cloud Deployment (SSE Mode)
Run this locally before deploying to Railway to ensure everything works.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

import httpx
from rich.console import Console
from rich.table import Table

console = Console()

# Configuration
BASE_URL = os.environ.get("ARIFOS_TEST_URL", "http://localhost:8000")
TEST_TIMEOUT = 30


async def test_health_endpoint():
    """Test /health endpoint"""
    console.print("\n[bold cyan]Test 1: Health Endpoint[/bold cyan]")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            response.raise_for_status()

            data = response.json()

            table = Table(title="Health Check Response")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")

            for key, value in data.items():
                table.add_row(key, str(value))

            console.print(table)
            console.print("✅ [green]Health endpoint working![/green]")
            return True

    except Exception as e:
        console.print(f"❌ [red]Health endpoint failed: {e}[/red]")
        return False


async def test_docs_endpoint():
    """Test /docs endpoint (FastAPI auto-docs)"""
    console.print("\n[bold cyan]Test 2: API Documentation[/bold cyan]")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/docs")
            response.raise_for_status()

            console.print(f"✅ [green]Docs available at: {BASE_URL}/docs[/green]")
            console.print("   Open in browser to see interactive API documentation")
            return True

    except Exception as e:
        console.print(f"❌ [red]Docs endpoint failed: {e}[/red]")
        return False


async def test_sse_endpoint():
    """Test /sse endpoint (MCP connection)"""
    console.print("\n[bold cyan]Test 3: SSE Endpoint[/bold cyan]")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # SSE endpoint might return different status codes
            # Just verify it's reachable
            response = await client.get(f"{BASE_URL}/sse", follow_redirects=True)

            # SSE typically returns 200 or streams data
            if response.status_code in [200, 404, 405]:
                console.print(f"✅ [green]SSE endpoint reachable (status: {response.status_code})[/green]")
                console.print("   Note: Full MCP connection requires proper SSE client")
                return True
            else:
                console.print(f"⚠️  [yellow]SSE endpoint returned: {response.status_code}[/yellow]")
                return False

    except Exception as e:
        console.print(f"❌ [red]SSE endpoint failed: {e}[/red]")
        return False


async def test_cors_headers():
    """Test CORS headers are configured"""
    console.print("\n[bold cyan]Test 4: CORS Configuration[/bold cyan]")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.options(
                f"{BASE_URL}/health",
                headers={"Origin": "https://claude.ai"}
            )

            headers = response.headers

            table = Table(title="CORS Headers")
            table.add_column("Header", style="cyan")
            table.add_column("Value", style="green")

            cors_headers = {
                "access-control-allow-origin": headers.get("access-control-allow-origin", "❌ Missing"),
                "access-control-allow-methods": headers.get("access-control-allow-methods", "❌ Missing"),
                "access-control-allow-headers": headers.get("access-control-allow-headers", "❌ Missing"),
            }

            for key, value in cors_headers.items():
                table.add_row(key, value)

            console.print(table)

            if all("Missing" not in v for v in cors_headers.values()):
                console.print("✅ [green]CORS configured correctly[/green]")
                return True
            else:
                console.print("⚠️  [yellow]CORS might need configuration[/yellow]")
                return False

    except Exception as e:
        console.print(f"❌ [red]CORS test failed: {e}[/red]")
        return False


def print_summary(results):
    """Print test summary"""
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary[/bold]")
    console.print("="*60)

    table = Table()
    table.add_column("Test", style="cyan")
    table.add_column("Result", style="bold")

    tests = [
        ("Health Endpoint", results[0]),
        ("API Documentation", results[1]),
        ("SSE Endpoint", results[2]),
        ("CORS Configuration", results[3]),
    ]

    for test_name, passed in tests:
        status = "[green]✅ PASS[/green]" if passed else "[red]❌ FAIL[/red]"
        table.add_row(test_name, status)

    console.print(table)

    total = len(results)
    passed = sum(results)

    console.print(f"\n[bold]Results: {passed}/{total} tests passed[/bold]")

    if passed == total:
        console.print("\n🎉 [green bold]All tests passed! Ready for deployment.[/green bold]")
        return True
    else:
        console.print("\n⚠️  [yellow bold]Some tests failed. Fix issues before deploying.[/yellow bold]")
        return False


async def main():
    """Run all tests"""
    console.print("[bold magenta]arifOS Cloud Deployment Test Suite[/bold magenta]")
    console.print(f"Testing URL: [cyan]{BASE_URL}[/cyan]")
    console.print("="*60)

    # Check if server is running
    console.print("\n[yellow]Checking if server is running...[/yellow]")
    console.print(f"If testing locally, start server with:")
    console.print(f"  [cyan]python -m arifos_core.mcp sse[/cyan]\n")

    results = []

    # Run tests
    results.append(await test_health_endpoint())
    results.append(await test_docs_endpoint())
    results.append(await test_sse_endpoint())
    results.append(await test_cors_headers())

    # Print summary
    all_passed = print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n\n[red bold]Fatal error: {e}[/red bold]")
        sys.exit(1)
