#!/bin/bash
# arifOS Bootstrap Script (Bash)
# Automatically sets up development environment on fresh clone
#
# Usage:
#   ./bootstrap.sh                  # Interactive mode
#   ./bootstrap.sh --auto           # Auto mode (use defaults)
#   ./bootstrap.sh --minimal        # Minimal setup (core only)
#   ./bootstrap.sh --full           # Full setup (all tools)

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}${BOLD}======================================================================${NC}"
    echo -e "${BLUE}${BOLD}$1${NC}"
    echo -e "${BLUE}${BOLD}======================================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}? $1${NC}"
}

print_error() {
    echo -e "${RED}? $1${NC}"
}

print_info() {
    echo -e "${CYAN}? $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}? $1${NC}"
}

# Parse arguments
MODE="interactive"
AUTO=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --auto) AUTO=true; MODE="full" ;;
        --minimal) MODE="minimal" ;;
        --full) MODE="full" ;;
        --help)
            echo "arifOS Bootstrap Script"
            echo ""
            echo "Usage:"
            echo "  ./bootstrap.sh                  # Interactive mode"
            echo "  ./bootstrap.sh --auto           # Auto mode (use defaults)"
            echo "  ./bootstrap.sh --minimal        # Minimal setup (core only)"
            echo "  ./bootstrap.sh --full           # Full setup (all tools)"
            echo ""
            echo "DITEMPA BUKAN DIBERI - Your environment will be forged!"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Interactive mode selection
if [ "$MODE" = "interactive" ]; then
    print_header "arifOS Development Environment Bootstrap"
    echo "Choose setup mode:"
    echo "1. Minimal - Core dependencies only"
    echo "2. Full - Core + all development tools (recommended)"
    echo ""
    read -p "Enter choice (1-2, default 2): " choice
    MODE=$( [ "$choice" = "1" ] && echo "minimal" || echo "full" )
fi

echo -e "\n${YELLOW}Running $MODE setup...${NC}\n"

# Step 1: Check Python version
print_header "Step 1: Checking Python Version"

if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    print_error "Python not found"
    print_info "Please install Python 3.10+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    print_success "Python $PYTHON_VERSION detected (required: 3.10+)"
else
    print_error "Python $PYTHON_VERSION detected (required: 3.10+)"
    print_info "Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_success "Git is installed"
else
    print_error "Git is not installed"
    print_info "Please install Git from https://git-scm.com"
    exit 1
fi

# Check Docker (optional)
if command -v docker &> /dev/null; then
    print_success "Docker is installed"
else
    print_warning "Docker is not installed (optional but recommended)"
fi

# Step 2: Create virtual environment
print_header "Step 2: Creating Virtual Environment"

if [ -d ".venv" ]; then
    print_info "Virtual environment already exists at .venv"
    if [ "$AUTO" = false ]; then
        read -p "Recreate it? (y/N): " response
        if [ "$response" = "y" ]; then
            print_info "Removing existing virtual environment..."
            rm -rf .venv
        else
            print_success "Using existing virtual environment"
        fi
    else
        print_success "Using existing virtual environment"
    fi
fi

if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment at .venv..."
    $PYTHON_CMD -m venv .venv
    print_success "Virtual environment created successfully"
fi

# Activate virtual environment
source .venv/bin/activate

# Step 3: Install dependencies
print_header "Step 3: Installing Dependencies"

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Install arifOS
print_info "Installing arifOS package..."
if [ "$MODE" = "minimal" ]; then
    python -m pip install -e .
else
    python -m pip install -e ".[all]"
fi

if [ $? -eq 0 ]; then
    print_success "arifOS installed successfully"
else
    print_error "Failed to install arifOS"
    exit 1
fi

# Install dev tools if full mode
if [ "$MODE" = "full" ]; then
    print_info "Installing development tools..."
    
    DEV_TOOLS=(
        "pre-commit"
        "safety"
        "bandit"
        "detect-secrets"
        "pytest-cov"
        "pytest-xdist"
        "mypy"
        "types-requests"
        "types-pyyaml"
    )
    
    for tool in "${DEV_TOOLS[@]}"; do
        print_info "Installing $tool..."
        python -m pip install "$tool" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            print_warning "Failed to install $tool (continuing...)"
        fi
    done
    
    print_success "Development tools installed"
fi

# Step 4: Setup pre-commit (if full mode)
if [ "$MODE" = "full" ]; then
    print_header "Step 4: Setting Up Pre-commit Hooks"
    
    if [ -f ".pre-commit-config.yaml" ]; then
        print_info "Installing pre-commit hooks..."
        python -m pre_commit install > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            print_success "Pre-commit hooks installed"
            
            if [ "$AUTO" = false ]; then
                read -p "Run pre-commit on all files now? (y/N): " response
                if [ "$response" = "y" ]; then
                    print_info "Running pre-commit on all files (this may take a while)..."
                    python -m pre_commit run --all-files || true
                fi
            fi
        else
            print_warning "Failed to install pre-commit hooks (non-critical)"
        fi
    else
        print_warning "Pre-commit config not found, skipping..."
    fi
fi

# Step 5: Setup .env file
print_header "Step 5: Setting Up Environment File"

if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        print_info "Creating .env file from .env.example..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Remember to edit .env and add your API keys!"
    else
        print_info ".env file already exists"
    fi
else
    print_warning ".env.example not found, skipping..."
fi

# Step 6: Run verification
print_header "Step 6: Verifying Installation"

if [ -f "verify_setup.py" ]; then
    print_info "Running verification..."
    python verify_setup.py
    
    if [ $? -ne 0 ]; then
        print_warning "Verification failed, but setup is complete"
        print_info "You may need to manually install some dependencies"
    fi
else
    print_warning "verify_setup.py not found, skipping verification..."
fi

# Show next steps
print_header "?? Setup Complete!"

echo -e "${GREEN}Your arifOS development environment is ready!${NC}\n"

echo -e "${BOLD}Next steps:${NC}\n"

echo "1. Activate the virtual environment:"
echo -e "   ${CYAN}source .venv/bin/activate${NC}\n"

echo "2. Edit .env file with your API keys:"
echo -e "   ${CYAN}nano .env${NC}\n"

echo "3. Run tests:"
echo -e "   ${CYAN}pytest${NC}\n"

echo "4. Read the documentation:"
echo -e "   ${CYAN}docs/setup/QUICK_START.md${NC}\n"

echo "5. Start coding!"
echo -e "   ${CYAN}code .  # VS Code${NC}"
echo -e "   ${CYAN}# Or use your preferred editor${NC}\n"

echo -e "${BOLD}DITEMPA BUKAN DIBERI${NC} — Your environment is forged! ???\n"
