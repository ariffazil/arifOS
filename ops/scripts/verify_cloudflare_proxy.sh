#!/bin/bash
# verify_cloudflare_proxy.sh - Check if Cloudflare proxy is enabled

set -e

DOMAIN="${1:-arifosmcp.arif-fazil.com}"

echo "🔍 Checking Cloudflare proxy status for: $DOMAIN"
echo ""

# Check if resolving to Cloudflare IPs
IPS=$(dig +short "$DOMAIN" 2>/dev/null || echo "")

echo "DNS Resolution:"
echo "$IPS" | while read ip; do
    if [ -n "$ip" ]; then
        echo "  - $ip"
        # Check if IP is Cloudflare
        if [[ "$ip" == 104.* ]] || [[ "$ip" == 172.* ]] || [[ "$ip" == 173.245.* ]] || [[ "$ip" == 188.114.* ]]; then
            echo "    ✅ Cloudflare IP detected"
        else
            echo "    ⚠️  Direct VPS IP (NOT proxied)"
        fi
    fi
done

echo ""
echo "HTTP Headers check:"
HEADERS=$(curl -sI "https://$DOMAIN/" 2>/dev/null | grep -iE "cf-ray|cloudflare|server" || echo "")

if echo "$HEADERS" | grep -q "cloudflare"; then
    echo "  ✅ Cloudflare proxy ACTIVE"
    echo "  $HEADERS" | grep -E "cf-ray|server" | sed 's/^/  /'
    exit 0
else
    echo "  ❌ Cloudflare proxy NOT DETECTED"
    echo ""
    echo "⚠️  WARNING: ChatGPT MCP clients may timeout!"
    echo "   Fix: Enable orange cloud in Cloudflare DNS settings"
    exit 1
fi
