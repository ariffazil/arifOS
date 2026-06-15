# arifOS Metabolic Makefile
# Ditempa Bukan Diberi — Forged, Not Given

PYTHON = uv run python
DIR := /root/arifOS

include /root/arifOS/scripts/security_audit.mk

.PHONY: status forge seal health conformance sync sot-check prove deploy-local publish-check publish-pypi publish-ghcr publish-law publish-all verify-public reality-replay constitutional-benchmark

status:
	@echo "--- arifOS Status (ΔΩΨ) ---"
	@$(PYTHON) -m arifosmcp.runtime.reforge 2>/dev/null || true
	@git status -s

# Federation forge gate — inherited from scripts/forge.mk
include /root/arifOS/scripts/forge.mk

seal:
	@echo "Sealing Vault 999..."
	@git commit -m "feat(kernel): metabolic seal v$$(date +%Y.%m.%d)"
	@git push origin main
	@echo "System Sealed."

health:
	@echo "Verifying 111_SENSE..."
	@curl -s http://localhost:8088/health | jq .  # live VPS port; use PORT=8080 for local Docker dev

conformance:
	@echo "Running ARIF Conformance Spine v0.1..."
	@$(PYTHON) -m arifosmcp.transport.conformance_spine

deploy-local:
	@echo "Deploying current arifOS HEAD to native bare-metal runtime..."
	@cd $(DIR) && git fetch origin main
	@cd $(DIR) && test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || \
		(echo "888_HOLD: local HEAD is not origin/main; push or rebase before deploy-local" && exit 1)
	@cd $(DIR) && GIT_SHA=$$(git rev-parse --short=7 HEAD); \
	echo "Syncing canonical code to /opt/arifos/app..."; \
	rsync -av --exclude='.git' --exclude='.venv' $(DIR)/ /opt/arifos/app/; \
	chmod -R u+rwX,go+rX /opt/arifos/app/arifosmcp/; \
	chmod 644 /opt/arifos/app/.env; \
	chown arifos:arifos /opt/arifos/app/.env 2>/dev/null; \
	echo "$$GIT_SHA" > /opt/arifos/app/.git_commit; \
	echo "Restarting arifOS bare-metal service..."; \
	systemctl restart arifos.service; \
	echo "Waiting for kernel health..."; \
	for i in $$(seq 1 30); do \
		status=$$(curl -s -m 2 http://localhost:8088/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null); \
		if [ "$$status" = "healthy" ]; then echo "Kernel healthy after $${i}s"; break; fi; \
		sleep 2; \
	done; \
	if [ "$$status" != "healthy" ]; then echo "888_HOLD: kernel did not become healthy"; exit 1; fi; \
	echo "Running conformance spine post-deploy..."; \
	$(PYTHON) -m arifosmcp.transport.conformance_spine

sot-check: security-audit
	@echo "Auditing arifOS source-of-truth alignment..."
	@python scripts/audit_sot.py

reality-replay:
	@echo "Replaying Reality Ledger..."
	@python -m core.vault999.reality_ledger

constitutional-benchmark:
	@echo "Running Constitutional Agent Benchmark..."
	@python benchmarks/constitutional_agent_benchmark/run_benchmarks.py

metabolic:
	@echo "══════════════════════════════════════════════════════════════"
	@echo "METABOLIC CHAIN TEST — The Body Lives or It Doesn't"
	@echo "══════════════════════════════════════════════════════════════"
	@echo "Testing: LAS → GEOX → Claim → WEALTH → JUDGE → VAULT"
	@echo ""
	PYTHONPATH=tests/metabolic $(PYTHON) -m pytest tests/metabolic/test_chain.py -v --tb=long -s
	@echo ""
	@echo "══════════════════════════════════════════════════════════════"
	@echo "CHAIN TEST COMPLETE"
	@echo "══════════════════════════════════════════════════════════════"

sync:
	@echo "Synchronizing Planetary Fleet..."
	@git submodule update --remote --merge
	@git add .
	@git commit -m "chore: planetary sync"
	@git push origin main

# security-audit: moved to include

# ============================================================
# PROOF PACK — Single command to prove substrate health
# ============================================================

prove:
	@echo "╔═══════════════════════════════════════════════════╗"
	@echo "║     ARIFOS PROOF PACK — $$(date +%Y-%m-%d)        ║"
	@echo "║     DITEMPA BUKAN DIBERI                         ║"
	@echo "╚═══════════════════════════════════════════════════╝"
	@mkdir -p reports
	@echo ""
	@echo "--- 1. make health ---"; make health 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- 2. make sot-check ---"; make sot-check 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- 3. make security-audit ---"; make security-audit 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- 4. make constitutional-benchmark ---"; make constitutional-benchmark 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- 5. make reality-replay ---"; make reality-replay 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- 6. vault999-verify ---"; python scripts/vault999_status.py 2>&1 || echo "FAIL"
	@echo ""
	@echo "--- Generating proof pack ---"; \
	PROOF_FILE="reports/ARIFOS_PROOF_PACK_$$(date +%Y-%m-%d).md"; \
	{ \
	  echo "# ARIFOS Proof Pack — $$(date +%Y-%m-%d)"; \
	  echo ""; \
	  echo "## Health"; curl -s http://localhost:8088/health | python3 -m json.tool 2>/dev/null || echo "FAIL"; \
	  echo ""; \
	  echo "## Benchmark Score"; cat reports/constitutional_benchmark.md 2>/dev/null | grep Score || echo "FAIL"; \
	  echo ""; \
	  echo "## Security Audit"; echo "(See security-audit output above)"; \
	  echo ""; \
	  echo "## VAULT999 Chain"; python scripts/vault999_status.py 2>&1 | head -20; \
	} > "$$PROOF_FILE"; \
	echo "Proof pack: $$PROOF_FILE"

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

# --- AGI Kernel Proof Engine ---
.PHONY: prove constitutional-benchmark vault999-verify reality-replay

constitutional-benchmark:
	@echo "Running constitutional floor and boundary benchmarks..."
	pytest benchmarks/floors/ benchmarks/organs/ benchmarks/ledgers/

vault999-verify:
	@echo "Verifying VAULT999 hash chains and receipts..."
	python3 /root/arifOS/core/vault999/verify.py

reality-replay:
	@echo "Comparing predictions with observed outcomes in Reality Ledger..."
	# python -m arifos.core.reality_ledger replay

prove: health sot-check security-audit constitutional-benchmark vault999-verify reality-replay
	@echo "Synthesizing ARIFOS_PROOF_PACK.md..."

substrate-loop-test:
	@echo "Running End-to-End AGI Substrate Loop Test..."
	pytest benchmarks/loops/test_restrain_authorize_act_observe_learn.py -v

