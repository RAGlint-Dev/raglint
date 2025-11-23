#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Release Process...${NC}"

# 1. Run Tests
echo -e "${GREEN}Running Tests...${NC}"
source venv/bin/activate
pytest
if [ $? -ne 0 ]; then
    echo -e "${RED}Tests failed! Aborting release.${NC}"
    exit 1
fi

# 2. Clean previous builds
echo -e "${GREEN}Cleaning previous builds...${NC}"
rm -rf dist/ build/ *.egg-info

# 3. Build Package
echo -e "${GREEN}Building Package...${NC}"
python -m build
if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed! Aborting release.${NC}"
    exit 1
fi

# 4. Verify Build Artifacts
echo -e "${GREEN}Verifying Build Artifacts...${NC}"
ls -l dist/

echo -e "${GREEN}Release Ready!${NC}"
echo "To upload to PyPI, run: twine upload dist/*"
