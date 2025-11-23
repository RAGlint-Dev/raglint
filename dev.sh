#!/bin/bash
# RAGLint Development Helper Script

set -e

COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}"
echo "╔══════════════════════════════════════╗"
echo "║     RAGLint Development Helper       ║"
echo "╚══════════════════════════════════════╝"
echo -e "${COLOR_RESET}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${COLOR_YELLOW}⚠️  No virtual environment found.${COLOR_RESET}"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${COLOR_GREEN}✅ Virtual environment created!${COLOR_RESET}"
else
    source venv/bin/activate
    echo -e "${COLOR_GREEN}✅ Virtual environment activated${COLOR_RESET}"
fi

# Function to display menu
show_menu() {
    echo ""
    echo "Select an option:"
    echo "  1) Install dependencies"
    echo "  2) Run tests"
    echo "  3) Run tests with coverage"
    echo "  4) Format code (black)"
    echo "  5) Lint code (ruff)"
    echo "  6) Type check (mypy)"
    echo "  7) Run all checks (format + lint + type + test)"
    echo "  8) Build package"
    echo "  9) Run example"
    echo " 10) Clean build artifacts"
    echo " 11) Install pre-commit hooks"
    echo "  q) Quit"
    echo ""
}

# Function handlers
install_deps() {
    echo -e "${COLOR_BLUE}📦 Installing dependencies...${COLOR_RESET}"
    pip install -e ".[dev]"
    echo -e "${COLOR_GREEN}✅ Dependencies installed${COLOR_RESET}"
}

run_tests() {
    echo -e "${COLOR_BLUE}🧪 Running tests...${COLOR_RESET}"
    pytest -v
}

run_coverage() {
    echo -e "${COLOR_BLUE}📊 Running tests with coverage...${COLOR_RESET}"
    pytest --cov=raglint --cov-report=html --cov-report=term-missing
    echo -e "${COLOR_GREEN}✅ Coverage report generated in htmlcov/${COLOR_RESET}"
}

format_code() {
    echo -e "${COLOR_BLUE}🎨 Formatting code with black...${COLOR_RESET}"
    black raglint tests
    echo -e "${COLOR_GREEN}✅ Code formatted${COLOR_RESET}"
}

lint_code() {
    echo -e "${COLOR_BLUE}🔍 Linting code with ruff...${COLOR_RESET}"
    ruff check raglint tests
    echo -e "${COLOR_GREEN}✅ Linting complete${COLOR_RESET}"
}

type_check() {
    echo -e "${COLOR_BLUE}📝 Type checking with mypy...${COLOR_RESET}"
    mypy raglint --ignore-missing-imports || true
    echo -e "${COLOR_GREEN}✅ Type checking complete${COLOR_RESET}"
}

run_all_checks() {
    echo -e "${COLOR_BLUE}🚀 Running all quality checks...${COLOR_RESET}"
    format_code
    echo ""
    lint_code
    echo ""
    type_check
    echo ""
    run_coverage
    echo -e "${COLOR_GREEN}✅ All checks complete!${COLOR_RESET}"
}

build_package() {
    echo -e "${COLOR_BLUE}📦 Building package...${COLOR_RESET}"
    rm -rf dist/ build/ *.egg-info
    python -m build
    echo -e "${COLOR_GREEN}✅ Package built successfully!${COLOR_RESET}"
    ls -lh dist/
}

run_example() {
    echo -e "${COLOR_BLUE}🎬 Running example...${COLOR_RESET}"
    cd examples
    python basic_usage.py
    cd ..
    echo -e "${COLOR_GREEN}✅ Example complete${COLOR_RESET}"
}

clean_build() {
    echo -e "${COLOR_BLUE}🧹 Cleaning build artifacts...${COLOR_RESET}"
    rm -rf dist/ build/ *.egg-info htmlcov/ .coverage .pytest_cache/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${COLOR_GREEN}✅ Cleaned${COLOR_RESET}"
}

install_hooks() {
    echo -e "${COLOR_BLUE}🪝 Installing pre-commit hooks...${COLOR_RESET}"
    pre-commit install
    echo -e "${COLOR_GREEN}✅ Pre-commit hooks installed${COLOR_RESET}"
}

# Main loop
while true; do
    show_menu
    read -p "Enter choice: " choice
    
    case $choice in
        1) install_deps ;;
        2) run_tests ;;
        3) run_coverage ;;
        4) format_code ;;
        5) lint_code ;;
        6) type_check ;;
        7) run_all_checks ;;
        8) build_package ;;
        9) run_example ;;
        10) clean_build ;;
        11) install_hooks ;;
        q|Q) 
            echo -e "${COLOR_GREEN}👋 Goodbye!${COLOR_RESET}"
            exit 0 
            ;;
        *) 
            echo -e "${COLOR_RED}❌ Invalid option${COLOR_RESET}" 
            ;;
    esac
done
