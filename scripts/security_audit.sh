#!/usr/bin/env bash
#
# Security audit automation script for RAGlint
# Run this to perform comprehensive security scanning
#

set -e  # Exit on error

echo "========================================="
echo "RAGlint Security Audit Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create security directory
mkdir -p security/reports
echo "Created security/reports directory"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing RAGlint in development mode..."
    pip install -e .[dev]
else
    source venv/bin/activate
fi

echo ""
echo "========================================="
echo "1. Installing Security Tools"
echo "========================================="

pip install pip-audit bandit safety ruff --quiet

echo -e "${GREEN}✓ Security tools installed${NC}"
echo ""

echo "========================================="
echo "2. Dependency Vulnerability Scan (pip-audit)"
echo "========================================="

pip-audit --desc > security/reports/pip-audit_$(date +%Y%m%d).txt 2>&1 || {
    echo -e "${YELLOW}⚠ Some vulnerabilities found. Check security/reports/pip-audit_*.txt${NC}"
}

echo -e "${GREEN}✓ Dependency scan complete${NC}"
cat security/reports/pip-audit_$(date +%Y%m%d).txt
echo ""

echo "========================================="
echo "3. Code Security Scan (bandit)"
echo "========================================="

# Run bandit
bandit -r raglint/ -f json -o security/reports/bandit_$(date +%Y%m%d).json 2>&1 || {
    echo -e "${YELLOW}⚠ Security issues found${NC}"
}

# Also create text version
bandit -r raglint/ -f txt -o security/reports/bandit_$(date +%Y%m%d).txt 2>&1 || true

echo -e "${GREEN}✓ Code security scan complete${NC}"
echo "Summary:"
grep -A 5 "Total lines of code" security/reports/bandit_$(date +%Y%m%d).txt || echo "Check JSON file"
echo ""

echo "========================================="
echo "4. Known CVE Check (safety)"
echo "========================================="

safety check --json > security/reports/safety_$(date +%Y%m%d).json 2>&1 || {
    echo -e "${YELLOW}⚠ Known vulnerabilities found${NC}"
}

echo -e "${GREEN}✓ CVE check complete${NC}"
echo ""

echo "========================================="
echo "5. Code Quality Scan (ruff)"
echo "========================================="

# Check for security-related lint issues
ruff check raglint/ --select S > security/reports/ruff_security_$(date +%Y%m%d).txt 2>&1 || {
    echo -e "${YELLOW}⚠ Security lints found${NC}"
}

echo -e "${GREEN}✓ Code quality scan complete${NC}"
echo ""

echo "========================================="
echo "6. Generating Summary Report"
echo "========================================="

# Create summary
cat > security/reports/SUMMARY_$(date +%Y%m%d).md << EOF
# Security Audit Summary

**Date**: $(date +%Y-%m-%d)
**RAGlint Version**: $(python -c "import raglint; print(raglint.__version__)" 2>/dev/null || echo "development")

## Scans Performed

### 1. Dependency Vulnerabilities (pip-audit)
\`\`\`
$(head -20 security/reports/pip-audit_$(date +%Y%m%d).txt)
\`\`\`

**Status**: $(grep -q "No known vulnerabilities found" security/reports/pip-audit_$(date +%Y%m%d).txt 2>/dev/null && echo "✅ PASS" || echo "⚠️ REVIEW REQUIRED")

### 2. Code Security (bandit)  
\`\`\`
$(grep -A 10 "Total lines of code" security/reports/bandit_$(date +%Y%m%d).txt 2>/dev/null || echo "See JSON report")
\`\`\`

**Status**: $(grep -q "No issues identified" security/reports/bandit_$(date +%Y%m%d).txt 2>/dev/null && echo "✅ PASS" || echo "⚠️ REVIEW REQUIRED")

### 3. Known CVEs (safety)
**Status**: $(grep -q '"vulnerabilities": \[\]' security/reports/safety_$(date +%Y%m%d).json 2>/dev/null && echo "✅ PASS" || echo "⚠️ REVIEW REQUIRED")

### 4. Security Lints (ruff)
**Status**: $([ ! -s security/reports/ruff_security_$(date +%Y%m%d).txt ] && echo "✅ PASS" || echo "⚠️ REVIEW REQUIRED")

## Files Generated
- \`security/reports/pip-audit_$(date +%Y%m%d).txt\`
- \`security/reports/bandit_$(date +%Y%m%d).json\`
- \`security/reports/bandit_$(date +%Y%m%d).txt\`
- \`security/reports/safety_$(date +%Y%m%d).json\`
- \`security/reports/ruff_security_$(date +%Y%m%d).txt\`

## Next Steps

1. Review all ⚠️ items above
2. Fix critical and high severity issues
3. Document accepted risks for low severity items
4. Re-run this script after fixes

## Recommendations

- Schedule regular scans (weekly/monthly)
- Integrate into CI/CD pipeline
- Consider professional security audit for production deployment
EOF

echo -e "${GREEN}✓ Summary report generated${NC}"
echo ""

echo "========================================="
echo "Security Audit Complete!"
echo "========================================="
echo ""
echo "Reports saved to: security/reports/"
echo "Summary: security/reports/SUMMARY_$(date +%Y%m%d).md"
echo ""

# Check overall status
ISSUES=0

grep -q "No known vulnerabilities found" security/reports/pip-audit_$(date +%Y%m%d).txt 2>/dev/null || ISSUES=$((ISSUES + 1))
grep -q "No issues identified" security/reports/bandit_$(date +%Y%m%d).txt 2>/dev/null || ISSUES=$((ISSUES + 1))

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ No critical security issues found!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  $ISSUES scan(s) found issues. Please review reports.${NC}"
    exit 1
fi
