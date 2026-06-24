# Federation Security Audit Include
# DITEMPA BUKAN DIBERI

security-audit:
	@echo "🛡️ Running non-blocking security audit..."
	@timeout 90 trivy fs --scanners vuln --skip-version-check --severity CRITICAL,HIGH --skip-dirs '.venv' --skip-dirs 'node_modules' --skip-dirs '.git' --skip-dirs 'dist' --skip-dirs 'build' --skip-dirs '.tox' . > .audit_output.txt 2>&1 || true
	@timeout 120 semgrep --config auto --timeout 60 --exclude '.venv' --exclude 'node_modules' --exclude 'dist' --exclude 'build' --exclude '__pycache__' . --error >> .audit_output.txt 2>&1 || true
	@timeout 60 gitleaks detect --source . --verbose --no-banner >> .audit_output.txt 2>&1 || true
	@timeout 60 ruff check . >> .audit_output.txt 2>&1 || true
	@cat .audit_output.txt | python3 /root/arifOS/scripts/audit_parser.py || true
	@rm -f .audit_output.txt
