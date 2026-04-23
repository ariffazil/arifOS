# arifOS Metabolic Makefile
# Ditempa Bukan Diberi.

PYTHON = uv run python

.PHONY: status forge seal health sync

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
