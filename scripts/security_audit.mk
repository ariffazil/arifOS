# Federation Security Audit Include
# DITEMPA BUKAN DIBERI

security-audit:
	@echo "🛡️ Running non-blocking security audit..."
	@timeout 90 trivy fs --scanners vuln --skip-version-check --severity CRITICAL,HIGH --skip-dirs '.venv' --skip-dirs 'node_modules' --skip-dirs '.git' --skip-dirs 'dist' --skip-dirs 'build' --skip-dirs '.tox' . > .audit_output.txt 2>&1 || true
	@changed_files=$$(git diff --name-only HEAD~1 2>/dev/null | grep -E '\.(py|ts|js|jsx|tsx)$$' | head -100 | tr '\n' ' '); \
	if [ -n "$$changed_files" ]; then \
		echo "Running semgrep on changed files..." >> .audit_output.txt; \
		timeout 60 semgrep --config p/security-audit --timeout 30 $$changed_files --error >> .audit_output.txt 2>&1 || true; \
	else \
		echo "No changed source files; skipping semgrep in pre-push audit." >> .audit_output.txt; \
	fi
	@timeout 60 gitleaks detect --source . --verbose --no-banner >> .audit_output.txt 2>&1 || true
	@timeout 60 ruff check . >> .audit_output.txt 2>&1 || true
	@cat .audit_output.txt | python3 /root/arifOS/scripts/audit_parser.py || true
	@rm -f .audit_output.txt
