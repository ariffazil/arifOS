#!/bin/bash
# Publish arifOS to PyPI and npm
# Usage: ./scripts/publish/publish_all.sh [pypi-token] [npm-otp]

set -e

echo "🔱 arifOS Publish Script — Ditempa Bukan Diberi"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Check versions
echo -e "${YELLOW}📦 Checking versions...${NC}"
PYVERSION=$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
NPMVERSION=$(grep '"version":' npm/arifos-mcp/package.json | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')

echo -e "${GRAY}  PyPI version: $PYVERSION${NC}"
echo -e "${GRAY}  npm version:  $NPMVERSION${NC}"
echo ""

if [ "$PYVERSION" != "$NPMVERSION" ]; then
    echo "❌ Version mismatch! pyproject.toml ($PYVERSION) != package.json ($NPMVERSION)"
    exit 1
fi

echo -e "${GREEN}✅ Versions aligned: $PYVERSION${NC}"
echo ""

# PyPI Publish
echo -e "${YELLOW}📦 Publishing to PyPI...${NC}"
echo -e "${GRAY}----------------------------------------${NC}"

# Clean dist
rm -rf dist/

# Build
echo -e "${GRAY}🔨 Building distribution...${NC}"
python -m build -q

# Check
echo -e "${GRAY}🔍 Checking distribution...${NC}"
python -m twine check dist/*

# Upload
echo -e "${GRAY}📤 Uploading to PyPI...${NC}"
if [ -n "$1" ]; then
    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$1"
fi

python -m twine upload dist/*

echo -e "${GREEN}✅ PyPI publish successful!${NC}"
echo -e "${CYAN}   pip install arifosmcp==$PYVERSION${NC}"
echo ""

# npm Publish
echo -e "${YELLOW}📦 Publishing to npm...${NC}"
echo -e "${GRAY}----------------------------------------${NC}"

cd npm/arifos-mcp

# Check if already logged in
if ! npm whoami &>/dev/null; then
    echo -e "${YELLOW}🔑 Please login to npm:${NC}"
    npm login
else
    echo -e "${GRAY}✅ Already logged in as: $(npm whoami)${NC}"
fi

# Publish
echo -e "${GRAY}📤 Publishing package...${NC}"
if [ -n "$2" ]; then
    npm publish --access public --otp "$2"
else
    npm publish --access public
fi

cd ../..

echo -e "${GREEN}✅ npm publish successful!${NC}"
echo -e "${CYAN}   npm install -g @arifos/mcp@$NPMVERSION${NC}"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 All publishes completed successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${CYAN}Installation commands:${NC}"
echo -e "  pip install arifosmcp==$PYVERSION"
echo -e "  npm install -g @arifos/mcp@$NPMVERSION"
