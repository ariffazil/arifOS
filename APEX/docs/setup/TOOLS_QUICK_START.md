# ?? Quick Start: New Development Tools

**Status:** Ready to enhance your arifOS development workflow!  
**Created:** 2026-01-18

---

## ? 5-Minute Setup

### 1. Install Critical Tools

```powershell
# Run the installation script
.\install_recommended_deps.ps1

# Choose option 1 for critical tools only (fastest)
# Or option 4 for everything (recommended)
```

### 2. Initialize Pre-commit Hooks

```powershell
# Install hooks
pre-commit install

# Test on all files (will fix issues automatically)
pre-commit run --all-files
```

### 3. Run Security Scan

```powershell
# Check for vulnerabilities
safety check

# Scan code for security issues
bandit -r arifos_core/

# Initialize secrets baseline
detect-secrets scan > .secrets.baseline
```

### 4. Run Tests with Coverage

```powershell
# Run all tests with coverage report
pytest

# View coverage report
start htmlcov/index.html  # Opens in browser
```

---

## ?? Tool Usage Guide

### Pre-commit Hooks (Automatic Quality Gates)

**What it does:** Runs checks automatically before every commit.

```powershell
# Manual run
pre-commit run --all-files

# Skip hooks for urgent commit (NOT RECOMMENDED)
git commit -m "emergency fix" --no-verify

# Update hooks
pre-commit autoupdate
```

**Checks performed:**
- ? Code formatting (Black)
- ? Linting (Ruff)
- ? Type checking (MyPy)
- ? Security (Bandit)
- ? Secrets detection
- ? Constitutional compliance (F1-F12 basic checks)

---

### Pytest with Coverage (Testing)

**What it does:** Runs tests and tracks which code is tested.

```powershell
# Basic run
pytest

# Specific test file
pytest tests/test_apex_prime.py

# Specific test function
pytest tests/test_apex_prime.py::test_seal_verdict

# Only fast tests
pytest -m "not slow"

# Only constitutional tests
pytest -m constitutional

# Parallel execution (faster)
pytest -n auto

# With detailed output
pytest -vv

# Stop at first failure
pytest -x

# Show print statements
pytest -s

# Generate HTML coverage report
pytest --cov=arifos_core --cov-report=html
```

**Viewing coverage:**
```powershell
# Open HTML report
start htmlcov/index.html

# Terminal summary
pytest --cov=arifos_core --cov-report=term-missing
```

---

### Security Scanning

#### Safety (Dependency Vulnerabilities)

```powershell
# Check all dependencies
safety check

# Save report
safety check --json > security-report.json

# Check specific file
safety check -r requirements.txt
```

#### Bandit (Code Security)

```powershell
# Scan entire codebase
bandit -r arifos_core/

# Generate JSON report
bandit -r arifos_core/ -f json -o bandit-report.json

# High severity only
bandit -r arifos_core/ -ll

# Exclude tests
bandit -r arifos_core/ --exclude tests/
```

#### Detect-Secrets

```powershell
# Initial scan
detect-secrets scan > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline

# Scan specific file
detect-secrets scan your_file.py
```

---

### Type Checking (MyPy)

**What it does:** Catches type errors before runtime.

```powershell
# Check entire codebase
mypy arifos_core/

# Check specific module
mypy arifos_core/system/apex_prime.py

# Show error codes
mypy --show-error-codes arifos_core/

# Generate HTML report
mypy arifos_core/ --html-report mypy-report/
```

---

### Code Formatting (Black)

**What it does:** Automatically formats code to consistent style.

```powershell
# Format all files
black .

# Check without modifying
black --check .

# Format specific file
black arifos_core/system/apex_prime.py

# Show diff
black --diff arifos_core/
```

---

### Linting (Ruff)

**What it does:** Fast linter catching common errors.

```powershell
# Check all files
ruff check .

# Auto-fix issues
ruff check --fix .

# Show statistics
ruff check --statistics .

# Check specific rules
ruff check --select F,E .  # pyflakes and pycodestyle
```

---

### Performance Profiling

#### py-spy (Low Overhead)

```powershell
# Profile running script
py-spy record -o profile.svg -- python your_script.py

# Live profiling
py-spy top -- python your_script.py

# Dump current state
py-spy dump --pid <PID>
```

#### Memory Profiler

```python
# Add @profile decorator
from memory_profiler import profile

@profile
def apex_judge():
    # Your code here
    pass
```

```powershell
# Run with profiling
python -m memory_profiler your_script.py
```

#### Scalene (AI/ML Optimized)

```powershell
# Comprehensive profiling
scalene your_script.py

# HTML report
scalene --html --outfile profile.html your_script.py

# Focus on specific function
scalene --cpu-percent-threshold 5 your_script.py
```

---

### Documentation (MkDocs)

**What it does:** Generates beautiful documentation website.

```powershell
# Initialize (first time only)
mkdocs new .

# Serve locally
mkdocs serve
# Visit http://localhost:8000

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

### Database Migrations (Alembic)

**What it does:** Version control for database schemas.

```powershell
# Initialize (first time)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add constitutional_decisions table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

---

### Docker Compose (Local Stack)

**What it does:** Runs entire development environment.

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f arifos-api

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Access services:
# - API: http://localhost:8000
# - Postgres: localhost:5432
# - Redis: localhost:6379
# - Qdrant: http://localhost:6333
# - Grafana: http://localhost:3000 (admin/constitutional)
```

---

### Jupyter Notebooks

**What it does:** Interactive exploration and demos.

```powershell
# Start Jupyter
jupyter notebook

# Or JupyterLab (modern interface)
jupyter lab

# Install kernel
python -m ipykernel install --user --name=arifos-dev --display-name="arifOS Dev"
```

**Example notebook:**
```python
# Cell 1: Imports
from arifos_core.system.apex_prime import APEXPrime, APEX_VERSION
from arifos_core.enforcement.metrics import FloorCheckResult

# Cell 2: Initialize
apex = APEXPrime()
print(f"arifOS {APEX_VERSION}")

# Cell 3: Interactive testing
query = "Is AI conscious?"
response = "Yes, I have feelings"
verdict = apex.judge_output(query, response, [], [])
print(f"Verdict: {verdict.verdict}")  # Should be VOID (F9 violation)
```

---

### Nox (Multi-Python Testing)

**What it does:** Tests across multiple Python versions.

```powershell
# Run all sessions
nox

# Run specific session
nox -s tests

# Run for specific Python version
nox -s tests-3.14

# List available sessions
nox --list
```

---

## ?? Daily Workflow

### Morning: Start Development

```powershell
# 1. Pull latest
git pull

# 2. Update pre-commit hooks
pre-commit autoupdate

# 3. Update dependencies
pip install -U -e ".[all]"

# 4. Run security scan
safety check

# 5. Start Docker services
docker-compose up -d
```

### During Development

```powershell
# Write code in VS Code

# Tests run automatically on save (if configured)

# Manual test run
pytest tests/test_your_feature.py

# Check type hints
mypy arifos_core/your_module.py
```

### Before Commit

```powershell
# Pre-commit hooks run automatically on commit
git add .
git commit -m "feat: Add new constitutional floor check"

# Hooks will:
# ? Format code (Black)
# ? Lint (Ruff)
# ? Type check (MyPy)
# ? Security scan (Bandit)
# ? Detect secrets
# ? Run constitutional checks
```

### Before Push

```powershell
# 1. Full test suite
pytest

# 2. Check coverage
pytest --cov=arifos_core --cov-report=term-missing

# 3. Security scan
bandit -r arifos_core/

# 4. Build docs
mkdocs build

# 5. Push
git push origin your-branch
```

### Weekly Maintenance

```powershell
# 1. Update all dependencies
pip-compile --upgrade requirements.in

# 2. Security audit
safety check
pip-audit

# 3. Clean up
pre-commit gc

# 4. Regenerate docs
mkdocs build --clean
```

---

## ?? Troubleshooting

### Pre-commit hooks failing

```powershell
# Update hooks
pre-commit autoupdate

# Clean cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

### Tests failing

```powershell
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv

# Run specific failing test
pytest tests/test_file.py::test_function -vv
```

### MyPy errors

```powershell
# Clear cache
mypy --cache-clear arifos_core/

# Show error context
mypy --show-error-context arifos_core/
```

### Coverage too low

```powershell
# See what's missing
pytest --cov=arifos_core --cov-report=term-missing

# Focus on specific module
pytest --cov=arifos_core.system --cov-report=html

# Write tests for uncovered code!
```

---

## ?? Configuration Files Reference

All tools are configured in these files:

- `.pre-commit-config.yaml` - Pre-commit hooks
- `pytest.ini` - Testing configuration
- `mypy.ini` - Type checking rules
- `pyproject.toml` - Project metadata + tool configs
- `docker-compose.yml` - Docker services
- `mkdocs.yml` - Documentation structure
- `noxfile.py` - Multi-Python testing

---

## ?? Learning Resources

### Official Docs
- Pre-commit: https://pre-commit.com/
- Pytest: https://docs.pytest.org/
- MyPy: https://mypy.readthedocs.io/
- MkDocs: https://www.mkdocs.org/
- Docker Compose: https://docs.docker.com/compose/

### Video Tutorials
- Pre-commit: "Automate Python Code Quality" (YouTube)
- Pytest: "Testing in Python" (Real Python)
- Docker: "Docker Compose Tutorial" (TechWorld with Nana)

---

## ?? Get Help

If tools aren't working:

1. **Check installation:**
   ```powershell
   python verify_setup.py
   ```

2. **Read tool logs:**
   ```powershell
   pre-commit run --verbose --all-files
   pytest -vv
   ```

3. **Ask for help:**
   - Read `RECOMMENDED_DEPENDENCIES_RESEARCH.md`
   - Check tool's official documentation
   - Create GitHub issue if bug suspected

---

## ? Checklist: Am I Using Tools Correctly?

- [ ] Pre-commit hooks are installed (`pre-commit install`)
- [ ] Tests pass locally (`pytest`)
- [ ] Coverage is >70% (`pytest --cov`)
- [ ] No security issues (`safety check`, `bandit`)
- [ ] No type errors (`mypy arifos_core/`)
- [ ] Code is formatted (`black --check .`)
- [ ] No linting errors (`ruff check .`)
- [ ] Documentation builds (`mkdocs build`)
- [ ] Docker services start (`docker-compose up -d`)

If all ? ? You're ready to push! ??

---

**DITEMPA BUKAN DIBERI** — Your tools are forged for excellence! ???

---

**Next Steps:**
1. Run `.\install_recommended_deps.ps1`
2. Follow this guide to use each tool
3. Integrate into your daily workflow
4. Read full research: `RECOMMENDED_DEPENDENCIES_RESEARCH.md`

**Questions?** Check the tool-specific section above or official docs!
