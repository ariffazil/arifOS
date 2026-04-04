# 📦 Package Publishing Guide

**Version:** 2026.03.20-CONSOLIDATION  
**Date:** 2026-03-20  
**Status:** Ready for Publish

---

## 🐍 PyPI Publishing (Python)

### Prerequisites
```bash
# Install build tools
pip install --upgrade build twine

# Verify version
python -c "import arifosmcp; print(arifosmcp.__version__)"
# Should output: 2026.03.20
```

### Build & Upload
```bash
# 1. Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# 2. Build distribution
python -m build

# 3. Verify package
twine check dist/*

# 4. Upload to TestPyPI (optional but recommended)
twine upload --repository testpypi dist/*

# 5. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ arifosmcp

# 6. Upload to Production PyPI
twine upload dist/*
```

### Post-Publish Verification
```bash
# Verify on PyPI
open https://pypi.org/project/arifosmcp/

# Test fresh install
pip uninstall arifosmcp -y
pip install arifosmcp
python -c "from arifosmcp.runtime.server import mcp; print(f'arifOS {mcp.version} installed')"
```

---

## 📦 NPM Publishing (JavaScript/TypeScript)

### Package 1: @arifos/mcp (Server Wrapper)

```bash
# Navigate to npm package
cd npm/arifos-mcp

# 1. Verify version in package.json
# Should show: "version": "2026.3.20"

# 2. Login to npm (if not already logged in)
npm login

# 3. Publish
npm publish --access public

# 4. Verify
npm view @arifos/mcp version
# Should output: 2026.3.20
```

### Package 2: @arifos/mcp (TypeScript Client)

```bash
# Navigate to TypeScript package
cd arifosmcp/packages/npm/arifos-mcp

# 1. Install dependencies
npm install

# 2. Build
npm run build

# 3. Verify version in package.json
# Should show: "version": "2026.3.20"

# 4. Publish
npm publish --access public

# 5. Verify
npm view @arifos/mcp version
# Should output: 2026.3.20
```

---

## 🐳 Docker Publishing

### Build & Push
```bash
# 1. Build optimized image
docker build -f Dockerfile.optimized -t arifos/arifosmcp:2026.03.20 .
docker tag arifos/arifosmcp:2026.03.20 arifos/arifosmcp:latest

# 2. Push to Docker Hub
docker push arifos/arifosmcp:2026.03.20
docker push arifos/arifosmcp:latest

# 3. Verify
docker pull arifos/arifosmcp:latest
docker run --rm arifos/arifosmcp:latest python -c "import arifosmcp; print(arifosmcp.__version__)"
```

---

## ✅ Version Verification Checklist

### Files Updated
- [x] `pyproject.toml` — version 2026.03.20, description updated to 11 Mega-Tools
- [x] `npm/arifos-mcp/package.json` — version 2026.3.20, description updated
- [x] `arifosmcp/packages/npm/arifos-mcp/package.json` — version 2026.3.20, description updated
- [x] `arifosmcp/runtime/server.py` — FastMCP version updated to 2026.03.20-CONSOLIDATION

### Version Strings Changed
| File | Old Version | New Version |
|------|-------------|-------------|
| pyproject.toml | 2026.03.19 | 2026.03.20 |
| npm/arifos-mcp/package.json | 2026.3.17 | 2026.3.20 |
| arifosmcp/packages/npm/arifos-mcp/package.json | 0.5.0 | 2026.3.20 |
| README badges | 2026.03.19-ANTICHAOS | 2026.03.20-CONSOLIDATION |

### Tool Counts Updated
| Location | Old | New |
|----------|-----|-----|
| pyproject.toml description | 32 tools | 11 Mega-Tools (37 modes) |
| npm package descriptions | generic | 11 Mega-Tools (37 modes) |
| README badge | 42 Tools | Mega-Tools-11 (37 Modes) |

---

## 🚀 Quick Install Commands (For Users)

### Python
```bash
pip install arifosmcp

# With all optional dependencies
pip install arifosmcp[all]

# Development install
pip install arifosmcp[dev]
```

### Node.js
```bash
# Server wrapper
npm install -g @arifos/mcp

# TypeScript client
npm install @arifos/mcp

# Or via npx
npx @arifos/mcp
```

### Docker
```bash
docker run -p 8080:8080 arifos/arifosmcp:latest
```

---

## 📊 Package Statistics

| Package | Registry | Version | Downloads |
|---------|----------|---------|-----------|
| arifosmcp | PyPI | 2026.03.20 | - |
| @arifos/mcp (server) | NPM | 2026.3.20 | - |
| @arifos/mcp (client) | NPM | 2026.3.20 | - |
| arifos/arifosmcp | Docker Hub | 2026.03.20 | - |

---

## 🔄 Rollback Plan

If issues are discovered:

```bash
# PyPI - cannot delete, but can yank
# Mark version as broken (keeps installable with --force-reinstall)
twine yank dist/arifosmcp-2026.03.20-py3-none-any.whl

# NPM - can unpublish within 24 hours
npm unpublish @arifos/mcp@2026.3.20

# Docker - retag previous
# Revert to previous version
docker pull arifos/arifosmcp:2026.03.19
docker tag arifos/arifosmcp:2026.03.19 arifos/arifosmcp:latest
docker push arifos/arifosmcp:latest
```

---

## 📞 Support

- **PyPI Issues:** https://github.com/ariffazil/arifosmcp/issues
- **NPM Issues:** https://github.com/ariffazil/arifosmcp/issues
- **Docker Hub:** https://hub.docker.com/r/arifos/arifosmcp

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
