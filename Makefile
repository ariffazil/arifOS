# arifOS Metabolic Makefile
# Ditempa Bukan Diberi.

PYTHON = uv run python
DIR := /root/arifOS

.PHONY: status forge seal health sync sot-check deploy-local publish-check publish-pypi publish-ghcr publish-law publish-all verify-public security-audit

status:
	@echo "--- arifOS Status (ΔΩΨ) ---"
	@$(PYTHON) -m arifosmcp.runtime.reforge
	@git status -s

forge: security-audit
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
	@curl -s http://localhost:8088/health | jq .  # live VPS port; use PORT=8080 for local Docker dev

deploy-local:
	@echo "Deploying current arifOS HEAD to native bare-metal runtime..."
	@cd $(DIR) && git fetch origin main
	@cd $(DIR) && test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || \
		(echo "888_HOLD: local HEAD is not origin/main; push or rebase before deploy-local" && exit 1)
	@cd $(DIR) && GIT_SHA=$$(git rev-parse --short=7 HEAD); \
	echo "Syncing canonical code to /opt/arifos/app..."; \
	rsync -av --exclude='.git' --exclude='.venv' $(DIR)/ /opt/arifos/app/; \
	echo "$$GIT_SHA" > /opt/arifos/app/.git_commit; \
	echo "Restarting arifOS bare-metal service..."; \
	systemctl restart arifos.service; \
	echo "Deployment complete. Verifying health..."; \
	sleep 3; \
	curl -s http://localhost:8088/health | jq .

sot-check: security-audit
	@echo "Auditing arifOS source-of-truth alignment..."
	@python scripts/audit_sot.py

sync:
	@echo "Synchronizing Planetary Fleet..."
	@git submodule update --remote --merge
	@git add .
	@git commit -m "chore: planetary sync"
	@git push origin main

# security-audit: moved to include

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
	uv build --project . && uv publish --project . --token $(PYPI_TOKEN)
	@echo "✅ PyPI: arifos $(shell grep '^version' pyproject.toml | cut -d'\"' -f2) published"

## GHCR: Build + push Docker image with embedded git metadata
publish-ghcr:
	@echo "🐳 Publishing to GHCR with git provenance..."
	@GIT_SHA=$$(git rev-parse --short HEAD); \
	GIT_BRANCH=$$(git rev-parse --abbrev-ref HEAD); \
	BUILD_TIME=$$(date -u +%Y-%m-%dT%H:%M:%SZ); \
	VERSION=$$(git rev-parse --short HEAD); \
	docker build \
		--build-arg ARIFOS_BUILD_SHA=$$GIT_SHA \
		--build-arg ARIFOS_BUILD_BRANCH=$$GIT_BRANCH \
		--build-arg ARIFOS_BUILD_TIME=$$BUILD_TIME \
		-t ghcr.io/ariffazil/arifos:$$VERSION \
		-t ghcr.io/ariffazil/arifos:$$GIT_SHA \
		-f arifosmcp/Dockerfile . && \
	docker push ghcr.io/ariffazil/arifos:$$VERSION && \
	docker push ghcr.io/ariffazil/arifos:$$GIT_SHA && \
	docker tag ghcr.io/ariffazil/arifos:$$VERSION ghcr.io/ariffazil/arifos:latest && \
	docker push ghcr.io/ariffazil/arifos:latest && \
	:
	sed -i 's/^DEPLOY_GIT_COMMIT=.*/DEPLOY_GIT_COMMIT='"$$GIT_SHA"'/' /root/compose/.env 2>/dev/null || true && \
	echo "✅ GHCR: arifos:$$VERSION ($$GIT_SHA) pushed with embedded git metadata"

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

## ─── Public Parity Verification ───────────────────────────────────────────────
## Verify that public HTTPS surface matches local/container truth.
## Prevents deployment drift from hiding real failures.
verify-public:
	@echo "🔍 Verifying public parity..."
	@$(PYTHON) scripts/verify_public.py
	@echo "📄 Full report: tmp/verify_public_report.json"

verify-live:
	@echo "🔍 Verifying live observatory surface..."
	@python3 scripts/verify_live.py
	@echo "📄 Full report: tmp/verify_live_report.json"
include /root/arifOS/scripts/security_audit.mk
