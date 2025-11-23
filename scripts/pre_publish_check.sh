#!/bin/bash
# Quick verification and fixes before publishing

set -e  # Exit on error

echo "=================================="
echo "RAGLint - Pre-Publishing Checks"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Version in __init__.py
echo -n "1. Checking version in __init__.py... "
if grep -q '__version__ = "0.2.0"' raglint/__init__.py; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "   Fix: Add __version__ = '0.2.0' to raglint/__init__.py"
    exit 1
fi

# Check 2: Remove test database
echo -n "2. Checking for test database... "
if [ -f "raglint.db" ]; then
    echo -e "${YELLOW}Found${NC}"
    rm -f raglint.db
    echo "   Removed raglint.db"
else
    echo -e "${GREEN}✓${NC}"
fi

# Check 3: pyproject.toml is valid
echo -n "3. Validating pyproject.toml... "
python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" 2>/dev/null && echo -e "${GREEN}✓${NC}" || (echo -e "${RED}✗${NC}"; exit 1)

# Check 4: Test imports
echo -n "4. Testing core imports... "
python3 -c "import raglint" 2>/dev/null && echo -e "${GREEN}✓${NC}" || (echo -e "${RED}✗${NC}"; exit 1)

echo -n "5. Testing precision mode imports... "
python3 -c "from raglint.precision_mode import PrecisionMode" 2>/dev/null && echo -e "${GREEN}✓${NC}" || (echo -e "${RED}✗${NC}"; exit 1)

echo -n "6. Testing confidence imports... "
python3 -c "from raglint.confidence import ConfidenceScorer" 2>/dev/null && echo -e "${GREEN}✓${NC}" || (echo -e "${RED}✗${NC}"; exit 1)

echo -n "7. Testing fact extraction imports... "
python3 -c "from raglint.fact_extraction import FactExtractor" 2>/dev/null && echo -e "${GREEN}✓${NC}" || (echo -e "${RED}✗${NC}"; exit 1)

# Check 5: CLI works
echo -n "8. Testing CLI... "
python3 -m raglint.cli --help > /dev/null 2>&1 && echo -e "${GREEN}✓${NC}" || (echo -e "${YELLOW}⚠${NC} CLI may have issues")

# Check 6: No hardcoded secrets
echo -n "9. Checking for hardcoded secrets... "
if grep -r "sk-" raglint/ --include="*.py" 2>/dev/null | grep -v "example" | grep -q "sk-"; then
    echo -e "${RED}✗ Found potential API keys!${NC}"
    grep -r "sk-" raglint/ --include="*.py" | grep -v "example"
    exit 1
else
    echo -e "${GREEN}✓${NC}"
fi

# Check 7: Files exist
echo -n "10. Checking required files... "
REQUIRED_FILES=("README.md" "LICENSE" "CHANGELOG.md" "pyproject.toml" "MANIFEST.in")
MISSING=()
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING+=("$file")
    fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Missing: ${MISSING[*]}${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=================================="
echo "All checks passed! ✓"
echo "==================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review: PYPI_PUBLISHING_GUIDE.md"
echo "2. Build: python -m build"
echo "3. Check: twine check dist/*"
echo "4. Upload: twine upload dist/*"
echo ""
