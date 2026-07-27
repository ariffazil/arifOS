# scripts/wire/Makefile — install/uninstall the Wire enforcement surface
#
# DITEMPA BUKAN DIBERI — Forged, Not Given.

PREFIX        ?= /usr/local
ETCDIR        ?= /etc/arifos
VARRUN        ?= /var/run
LOGDIR        ?= /var/log

BIN_NAMES := arif-dependency-check arif-circuit-breaker arif-f4-monitor

.PHONY: install uninstall status

install:
	@echo "═══ Wire Install — 3-layer constitutional enforcement ═══"
	@mkdir -p $(PREFIX)/bin $(ETCDIR) $(VARRUN) $(LOGDIR)
	@for b in $(BIN_NAMES); do \
		install -m 0755 $$b $(PREFIX)/bin/$$b && echo "  ✓ $$b → $(PREFIX)/bin/"; \
	done
	@install -m 0644 configs/organ_dependencies.json $(ETCDIR)/organ_dependencies.json \
		&& echo "  ✓ organ_dependencies.json → $(ETCDIR)/"
	@echo ""
	@echo "Installed. Verify with:"
	@echo "  arif-dependency-check"

uninstall:
	@echo "═══ Wire Uninstall — reverses cleanly ═══"
	@for b in $(BIN_NAMES); do \
		rm -f $(PREFIX)/bin/$$b && echo "  ✗ removed $(PREFIX)/bin/$$b"; \
	done
	@echo "Note: $(ETCDIR)/organ_dependencies.json left intact (config, not binary)"

status:
	@echo "═══ Wire Status ═══"
	@for b in $(BIN_NAMES); do \
		if [ -x "$(PREFIX)/bin/$$b" ]; then \
			echo "  ✓ $$b installed at $(PREFIX)/bin/$$b"; \
		else \
			echo "  ✗ $$b MISSING from PATH"; \
		fi; \
	done
	@[ -f "$(ETCDIR)/organ_dependencies.json" ] \
		&& echo "  ✓ config at $(ETCDIR)/organ_dependencies.json" \
		|| echo "  ✗ config MISSING at $(ETCDIR)/organ_dependencies.json"
	@echo ""
	@arif-dependency-check 2>/dev/null || echo "  ⚠ dependency check failed"
