# arifOS Metabolic Makefile
# Ditempa Bukan Diberi.

PYTHON = uv run python

.PHONY: status forge seal health sync publish-check publish-pypi publish-ghcr publish-law publish-all

status:
	@echo "--- arifOS Status (ΔΩΨ) ---"
	@$(PYTHON) -m arifosmcp.runtime.reforge
	@git status -s

forge:
	@echo "Executing Surgical Burn..."
	@$(PYTHON) -m arifosmcp.runtime.reforge
	@git add .
	@echo "Metabolic Cycle Complete. Awaiting 888_SEAL for commit."

seal:
	@echo "Sealing Vault 999..."
	@git commit -m "feat(kernel): metabolic seal v$$(date +%Y.%m.%d)"
	@git push origin main
	@echo "System Sealed."

health:
	@echo "Verifying 111_SENSE..."
	@curl -s http://localhost:8000/health | jq .

sync:
	@echo "Synchronizing Planetary Fleet..."
	@git submodule update --remote --merge
	@git add .
	@git commit -m "chore: planetary sync"
	@git push origin main

# ============================================================
# SOVEREIGN PUBLISH PIPELINE — arifOS Federation
# Usage: make publish-check | make publish-pypi | make publish-all
# ============================================================

## Pre-flight: verify all tokens and configs exist
publish-check:
	@echo "🔍 Checking publish prerequisites..."
	@test -n "$(PYPI_TOKEN)" || (echo "❌ PYPI_TOKEN not set" && exit 1)
	@test -f pyproject.toml || (echo "❌ pyproject.toml missing" && exit 1)
	@test -f smithery.yaml || (echo "⚠️  smithery.yaml missing — MCP Registry unreachable")
	@python -m pytest tests/ -q --tb=short || (echo "❌ Tests failed — 888 HOLD" && exit 1)
	@echo "✅ Publish preflight passed"

## PyPI: Build + publish with uv
publish-pypi:
	@echo "🔱 Publishing to PyPI..."
	uv build
	uv publish --token $(PYPI_TOKEN)
	@echo "✅ PyPI: arifos $(shell grep '^version' pyproject.toml | cut -d'\"' -f2) published"

## GHCR: Build + push Docker image
publish-ghcr:
	@echo "🐳 Publishing to GHCR..."
	docker build -t ghcr.io/ariffazil/arifos:$(shell grep '^version' pyproject.toml | cut -d'\"' -f2) .
	docker push ghcr.io/ariffazil/arifos:$(shell grep '^version' pyproject.toml | cut -d'\"' -f2)
	docker tag ghcr.io/ariffazil/arifos:$(shell grep '^version' pyproject.toml | cut -d'\"' -f2) ghcr.io/ariffazil/arifos:latest
	docker push ghcr.io/ariffazil/arifos:latest

## GitGist: Sync 000_LAW.md to public gist
publish-law:
	@echo "📜 Syncing Living Law to Gist..."
	@curl -X PATCH \
	  -H "Authorization: token $(GITHUB_TOKEN)" \
	  -d "{\"files\":{\"000_LAW.md\":{\"content\":$$(jq -Rs . < 000_LAW.md)}}}" \
	  https://api.github.com/gists/$(CONSTITUTIONAL_GIST_ID)
	@echo "✅ 000_LAW.md synced"

## Forge tag + publish all surfaces
publish-all: publish-check publish-pypi publish-ghcr publish-law
	@echo "🔱 All surfaces published. DITEMPA BUKAN DIBERI — 999 SEAL ALIVE"
	@git tag -s v$(shell date +%Y.%m.%d) -m "Sovereign release $(shell date +%Y.%m.%d)"
	@git push origin --tags
