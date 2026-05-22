#!/usr/bin/env python3
"""
arifOS Sites Health Check
Checks key arifOS infrastructure sites and logs/report failures.
"""

import urllib.request
import urllib.error
import socket
import json
import sys
from datetime import datetime

# Sites to monitor (from arifosmcp/sites/ai.json trinity_network + endpoints)
SITES = [
    {
        "name": "Human (arif-fazil.com)",
        "url": "https://arif-fazil.com/",
        "expected_status": 200,
    },
    {
        "name": "Theory (arifos.arif-fazil.com)",
        "url": "https://arifos.arif-fazil.com/",
        "expected_status": 200,
    },
    {
        "name": "Apps MCP Hub (arifosmcp.arif-fazil.com)",
        "url": "https://arifosmcp.arif-fazil.com/",
        "expected_status": 200,
    },
    {
        "name": "MCP Endpoint",
        "url": "https://arifosmcp.arif-fazil.com/mcp",
        "expected_status": 200,
    },
    {
        "name": "Dashboard",
        "url": "https://arifosmcp.arif-fazil.com/dashboard",
        "expected_status": 200,
    },
    {
        "name": "Developer Portal",
        "url": "https://arifosmcp.arif-fazil.com/developer",
        "expected_status": 200,
    },
    {
        "name": "LLMs.txt",
        "url": "https://arifosmcp.arif-fazil.com/llms.txt",
        "expected_status": 200,
    },
]

TIMEOUT = 15  # seconds


def check_site(site):
    """Check a single site and return result."""
    name = site["name"]
    url = site["url"]
    expected = site["expected_status"]

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "arifOS-SiteHealth/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            actual = resp.getcode()
            if actual == expected:
                return {
                    "name": name,
                    "url": url,
                    "status": "UP",
                    "code": actual,
                    "error": None,
                }
            else:
                return {
                    "name": name,
                    "url": url,
                    "status": "DOWN",
                    "code": actual,
                    "error": f"Unexpected status {actual} (expected {expected})",
                }
    except urllib.error.HTTPError as e:
        return {
            "name": name,
            "url": url,
            "status": "DOWN",
            "code": e.code,
            "error": str(e),
        }
    except urllib.error.URLError as e:
        return {
            "name": name,
            "url": url,
            "status": "DOWN",
            "code": None,
            "error": str(e.reason),
        }
    except socket.timeout:
        return {
            "name": name,
            "url": url,
            "status": "DOWN",
            "code": None,
            "error": "Timeout",
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "status": "DOWN",
            "code": None,
            "error": str(e),
        }


def main():
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%Y-%m-%d %H:%M UTC")

    print("=== arifOS Sites Health Check ===")
    print(f"Time: {time_str}")
    print()

    results = []
    for site in SITES:
        result = check_site(site)
        results.append(result)

    # Output results
    up_sites = [r for r in results if r["status"] == "UP"]
    down_sites = [r for r in results if r["status"] == "DOWN"]

    print(f"UP: {len(up_sites)}/{len(results)}")
    for r in up_sites:
        print(f"  ✓ {r['name']} ({r['url']})")

    if down_sites:
        print(f"\nDOWN: {len(down_sites)}/{len(results)}")
        for r in down_sites:
            print(f"  ✗ {r['name']} ({r['url']}) - {r['error'] or f'HTTP {r["code"]}'}")

    # Return data for caller
    output = {
        "timestamp": time_str,
        "date": date_str,
        "total": len(results),
        "up": len(up_sites),
        "down": len(down_sites),
        "down_sites": down_sites,
    }

    # Print JSON for parsing if needed
    print()
    print("---JSON---")
    print(json.dumps(output, indent=2))

    return 0 if len(down_sites) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
