# Federation Security Audit Include
# DITEMPA BUKAN DIBERI

security-audit:
	@echo "🛡️ Running non-blocking security audit..."
	@trivy fs --severity CRITICAL,HIGH --skip-dirs '.venv,node_modules,.git,dist,build,.tox' . > .audit_output.txt 2>&1 || true
	@semgrep --config auto --exclude '.venv' --exclude 'node_modules' --exclude 'dist' --exclude 'build' --exclude '__pycache__' . --error >> .audit_output.txt 2>&1 || true
	@gitleaks dir . --verbose >> .audit_output.txt 2>&1 || true
	@ruff check . >> .audit_output.txt 2>&1 || true
	@cat .audit_output.txt | python3 /root/arifOS/scripts/audit_parser.py || true
	@rm -f .audit_output.txt
