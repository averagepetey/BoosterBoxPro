#!/bin/bash
# ============================================================
# SECURITY AUDIT SCRIPT
# Run this regularly to check for vulnerable dependencies
# ============================================================

set -e

echo "=============================================="
echo "🔒 BoosterBoxPro Security Audit"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# --------------------------------------------
# Python Dependencies (Backend)
# --------------------------------------------
echo "=============================================="
echo "🐍 Python Dependency Audit"
echo "=============================================="

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip-audit not installed. Installing...${NC}"
    pip install pip-audit
fi

echo "Running pip-audit..."
if pip-audit --requirement requirements.txt; then
    echo -e "${GREEN}✅ No known vulnerabilities in Python dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Python dependencies!${NC}"
    echo "   Run: pip-audit --fix to attempt automatic fixes"
fi

echo ""

# --------------------------------------------
# Node.js Dependencies (Frontend)
# --------------------------------------------
echo "=============================================="
echo "📦 Node.js Dependency Audit"
echo "=============================================="

cd frontend

echo "Running npm audit..."
# npm audit returns non-zero if vulnerabilities found
if npm audit --audit-level=moderate; then
    echo -e "${GREEN}✅ No moderate+ vulnerabilities in Node.js dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Node.js dependencies!${NC}"
    echo "   Run: npm audit fix to attempt automatic fixes"
    echo "   Run: npm audit fix --force for breaking changes (review carefully!)"
fi

cd "$PROJECT_ROOT"

echo ""

# --------------------------------------------
# Check for secrets in code
# --------------------------------------------
echo "=============================================="
echo "🔑 Secret Detection"
echo "=============================================="

echo "Checking for potential secrets in code..."

# Simple grep for common secret patterns (not exhaustive)
SECRETS_FOUND=0

# Check for hardcoded API keys (common patterns)
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "(sk_live_|sk_test_|pk_live_|pk_test_|api_key\s*=\s*['\"][a-zA-Z0-9]{20,})" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential API keys found in source code!${NC}"
    SECRETS_FOUND=1
fi

# Check for hardcoded passwords
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "password\s*=\s*['\"][^'\"]{8,}" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential hardcoded passwords found!${NC}"
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No obvious secrets detected in source code${NC}"
fi

echo ""

# --------------------------------------------
# Check .env files
# --------------------------------------------
echo "=============================================="
echo "📄 Environment File Check"
echo "=============================================="

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env is in .gitignore${NC}"
else
    echo -e "${RED}❌ .env is NOT in .gitignore - secrets may be committed!${NC}"
fi

# Check if any .env files are tracked by git
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}❌ .env is tracked by git! Remove it immediately!${NC}"
    echo "   Run: git rm --cached .env"
else
    echo -e "${GREEN}✅ .env is not tracked by git${NC}"
fi

echo ""

# --------------------------------------------
# Summary
# --------------------------------------------
echo "=============================================="
echo "📋 AUDIT COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Fix any vulnerabilities found above"
echo "2. Run this script before each deployment"
echo "3. Consider setting up GitHub Dependabot for automatic alerts"
echo ""

# ============================================================
# SECURITY AUDIT SCRIPT
# Run this regularly to check for vulnerable dependencies
# ============================================================

set -e

echo "=============================================="
echo "🔒 BoosterBoxPro Security Audit"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# --------------------------------------------
# Python Dependencies (Backend)
# --------------------------------------------
echo "=============================================="
echo "🐍 Python Dependency Audit"
echo "=============================================="

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip-audit not installed. Installing...${NC}"
    pip install pip-audit
fi

echo "Running pip-audit..."
if pip-audit --requirement requirements.txt; then
    echo -e "${GREEN}✅ No known vulnerabilities in Python dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Python dependencies!${NC}"
    echo "   Run: pip-audit --fix to attempt automatic fixes"
fi

echo ""

# --------------------------------------------
# Node.js Dependencies (Frontend)
# --------------------------------------------
echo "=============================================="
echo "📦 Node.js Dependency Audit"
echo "=============================================="

cd frontend

echo "Running npm audit..."
# npm audit returns non-zero if vulnerabilities found
if npm audit --audit-level=moderate; then
    echo -e "${GREEN}✅ No moderate+ vulnerabilities in Node.js dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Node.js dependencies!${NC}"
    echo "   Run: npm audit fix to attempt automatic fixes"
    echo "   Run: npm audit fix --force for breaking changes (review carefully!)"
fi

cd "$PROJECT_ROOT"

echo ""

# --------------------------------------------
# Check for secrets in code
# --------------------------------------------
echo "=============================================="
echo "🔑 Secret Detection"
echo "=============================================="

echo "Checking for potential secrets in code..."

# Simple grep for common secret patterns (not exhaustive)
SECRETS_FOUND=0

# Check for hardcoded API keys (common patterns)
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "(sk_live_|sk_test_|pk_live_|pk_test_|api_key\s*=\s*['\"][a-zA-Z0-9]{20,})" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential API keys found in source code!${NC}"
    SECRETS_FOUND=1
fi

# Check for hardcoded passwords
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "password\s*=\s*['\"][^'\"]{8,}" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential hardcoded passwords found!${NC}"
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No obvious secrets detected in source code${NC}"
fi

echo ""

# --------------------------------------------
# Check .env files
# --------------------------------------------
echo "=============================================="
echo "📄 Environment File Check"
echo "=============================================="

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env is in .gitignore${NC}"
else
    echo -e "${RED}❌ .env is NOT in .gitignore - secrets may be committed!${NC}"
fi

# Check if any .env files are tracked by git
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}❌ .env is tracked by git! Remove it immediately!${NC}"
    echo "   Run: git rm --cached .env"
else
    echo -e "${GREEN}✅ .env is not tracked by git${NC}"
fi

echo ""

# --------------------------------------------
# Summary
# --------------------------------------------
echo "=============================================="
echo "📋 AUDIT COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Fix any vulnerabilities found above"
echo "2. Run this script before each deployment"
echo "3. Consider setting up GitHub Dependabot for automatic alerts"
echo ""

# ============================================================
# SECURITY AUDIT SCRIPT
# Run this regularly to check for vulnerable dependencies
# ============================================================

set -e

echo "=============================================="
echo "🔒 BoosterBoxPro Security Audit"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 Project root: $PROJECT_ROOT"
echo ""

# --------------------------------------------
# Python Dependencies (Backend)
# --------------------------------------------
echo "=============================================="
echo "🐍 Python Dependency Audit"
echo "=============================================="

# Check if pip-audit is installed
if ! command -v pip-audit &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip-audit not installed. Installing...${NC}"
    pip install pip-audit
fi

echo "Running pip-audit..."
if pip-audit --requirement requirements.txt; then
    echo -e "${GREEN}✅ No known vulnerabilities in Python dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Python dependencies!${NC}"
    echo "   Run: pip-audit --fix to attempt automatic fixes"
fi

echo ""

# --------------------------------------------
# Node.js Dependencies (Frontend)
# --------------------------------------------
echo "=============================================="
echo "📦 Node.js Dependency Audit"
echo "=============================================="

cd frontend

echo "Running npm audit..."
# npm audit returns non-zero if vulnerabilities found
if npm audit --audit-level=moderate; then
    echo -e "${GREEN}✅ No moderate+ vulnerabilities in Node.js dependencies${NC}"
else
    echo -e "${RED}❌ Vulnerabilities found in Node.js dependencies!${NC}"
    echo "   Run: npm audit fix to attempt automatic fixes"
    echo "   Run: npm audit fix --force for breaking changes (review carefully!)"
fi

cd "$PROJECT_ROOT"

echo ""

# --------------------------------------------
# Check for secrets in code
# --------------------------------------------
echo "=============================================="
echo "🔑 Secret Detection"
echo "=============================================="

echo "Checking for potential secrets in code..."

# Simple grep for common secret patterns (not exhaustive)
SECRETS_FOUND=0

# Check for hardcoded API keys (common patterns)
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "(sk_live_|sk_test_|pk_live_|pk_test_|api_key\s*=\s*['\"][a-zA-Z0-9]{20,})" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential API keys found in source code!${NC}"
    SECRETS_FOUND=1
fi

# Check for hardcoded passwords
if grep -rn --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js" \
    -E "password\s*=\s*['\"][^'\"]{8,}" \
    --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git . 2>/dev/null; then
    echo -e "${RED}⚠️  Potential hardcoded passwords found!${NC}"
    SECRETS_FOUND=1
fi

if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No obvious secrets detected in source code${NC}"
fi

echo ""

# --------------------------------------------
# Check .env files
# --------------------------------------------
echo "=============================================="
echo "📄 Environment File Check"
echo "=============================================="

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✅ .env is in .gitignore${NC}"
else
    echo -e "${RED}❌ .env is NOT in .gitignore - secrets may be committed!${NC}"
fi

# Check if any .env files are tracked by git
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}❌ .env is tracked by git! Remove it immediately!${NC}"
    echo "   Run: git rm --cached .env"
else
    echo -e "${GREEN}✅ .env is not tracked by git${NC}"
fi

echo ""

# --------------------------------------------
# Summary
# --------------------------------------------
echo "=============================================="
echo "📋 AUDIT COMPLETE"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Fix any vulnerabilities found above"
echo "2. Run this script before each deployment"
echo "3. Consider setting up GitHub Dependabot for automatic alerts"
echo ""


