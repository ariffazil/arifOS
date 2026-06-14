# Federation Forge Entry — DITEMPA BUKAN DIBERI
# Auto-imported by each repo's Makefile
# Every push must pass through this gate

.PHONY: forge forge-full

# Quick forge: lint + security audit + SOT bump + clean temp
forge: sot-bump clean-temp security-audit
	@echo ""
	@echo "╔══════════════════════════════════════════════════╗"
	@echo "║  FORGE PASSED — entropy reduced, truth aligned   ║"
	@echo "╚══════════════════════════════════════════════════╝"

# Full forge: everything above + test + build + SOT verify
forge-full: forge test build verify-sot
	@echo ""
	@echo "╔══════════════════════════════════════════════════╗"
	@echo "║  FORGE FULL — ready for SEAL                     ║"
	@echo "╚══════════════════════════════════════════════════╝"

# Bump SOT-MANIFEST timestamps in current repo
sot-bump:
	@echo "🔄 Bumping SOT-MANIFEST timestamps..."
	@find . -name "*.md" -path "*/AGENTS.md" -o -name "*.md" -path "*/README.md" -o -name "*.md" -path "*/INVARIANTS.md" -o -name "*.md" -path "*/BOUNDARY.md" -o -name "*.md" -path "*/GENESIS/*.md" 2>/dev/null | while read f; do \
		if grep -q 'last_verified: ' "$$f"; then \
			sed -i 's/last_verified: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/last_verified: '$(shell date +%Y-%m-%d)'/' "$$f"; \
			sed -i 's/valid_until: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/valid_until: '$(shell date -d '+30 days' +%Y-%m-%d)'/' "$$f"; \
			echo "  ✅ $$f"; \
		fi; \
	done
	@echo "✅ SOT timestamps aligned"

# Clean temp files — reduce entropy
clean-temp:
	@echo "🧹 Cleaning temporary files..."
	@find . -name ".audit_output.txt" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name ".ruff_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Temp files cleaned"

# Verify SOT integrity — check no stale markers
verify-sot:
	@echo "🔍 Verifying SOT integrity..."
	@stale=0; \
	find . -name "*.md" -path "*/AGENTS.md" -o -name "*.md" -path "*/README.md" 2>/dev/null | while read f; do \
		verified=$$(grep -oP 'last_verified: \K[0-9]{4}-[0-9]{2}-[0-9]{2}' "$$f" 2>/dev/null); \
		valid=$$(grep -oP 'valid_until: \K[0-9]{4}-[0-9]{2}-[0-9]{2}' "$$f" 2>/dev/null); \
		if [ "$$verified" != "$(shell date +%Y-%m-%d)" ]; then \
			echo "  ⚠️  $$f — last_verified: $$verified (expected $(shell date +%Y-%m-%d))"; \
			stale=$$((stale + 1)); \
		fi; \
	done; \
	if [ "$$stale" -gt 0 ]; then \
		echo "❌ $$stale files have stale SOT timestamps. Run 'make sot-bump'."; \
		exit 1; \
	fi; \
	echo "✅ All SOT timestamps current"
