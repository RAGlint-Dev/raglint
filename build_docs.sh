#!/bin/bash
# Build Sphinx documentation

set -e

echo "Building Sphinx documentation..."

# Install docs dependencies
pip install -e ".[docs]" -q

# Clean previous build
rm -rf docs/_build

# Build HTML
cd docs
sphinx-build -b html . _build/html

echo ""
echo "✅ Documentation built successfully!"
echo "📄 Open: docs/_build/html/index.html"
echo ""
echo "To serve locally:"
echo "  cd docs/_build/html && python -m http.server 8080"
