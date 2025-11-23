# GitHub Setup Guide - RAGLint

## 🎯 Complete GitHub Repository Setup

---

## Steg 1: Create GitHub Repository

### 1.1 Via GitHub Website

1. Gå till https://github.com/new
2. Fyll i:
   - **Repository name**: `raglint`
   - **Description**: `A comprehensive, privacy-first RAG evaluation framework with 99%+ precision mode`
   - **Visibility**: Public
   - **DO NOT initialize** with README (vi har redan)
3. Click "Create repository"

### 1.2 Note Your Repository URL

```
https://github.com/YOUR_USERNAME/raglint.git
```

---

## Steg 2: Initialize Git (if not already)

```bash
cd /home/yesir/Dokument/RAGlint

# Check if git initialized
git status

# If not initialized:
git init
git branch -M main
```

---

## Steg 3: Create .gitignore (if needed)

Check if exists:
```bash
ls -la .gitignore
```

If missing or incomplete, create:
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
*.cover

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# RAGLint specific
raglint.db
*.log
raglint_report.html
demo_report.html

# Build artifacts
dist/
build/
*.egg-info/

# Ruff cache
.ruff_cache/
EOF
```

---

## Steg 4: Add All Files

```bash
# Stage all files
git add .

# Check what will be committed
git status

# If you see files that should NOT be committed:
git reset HEAD path/to/file
echo "path/to/file" >> .gitignore
```

---

## Steg 5: Initial Commit

```bash
git commit -m "Initial commit: RAGLint v0.2.0

- Complete RAG evaluation framework
- 15 built-in plugins
- 99%+ precision mode
- FastAPI dashboard
- LangChain integration
- Comprehensive documentation"
```

---

## Steg 6: Add Remote and Push

```bash
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/raglint.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

**Enter credentials when prompted** (or use SSH if configured)

---

## Steg 7: Verify on GitHub

1. Gå till https://github.com/YOUR_USERNAME/raglint
2. Verify:
   - [ ] README displays correctly
   - [ ] File structure looks good
   - [ ] No sensitive files (API keys, etc.)

---

## Steg 8: Add Topics/Tags

On GitHub repository page:
1. Click ⚙️ (Settings icon) next to "About"
2. Add topics:
   - `rag`
   - `evaluation`
   - `llm`
   - `python`
   - `machine-learning`
   - `retrieval-augmented-generation`
   - `quality-assurance`
   - `ai`
3. Save

---

## Steg 9: Create GitHub Release

### 9.1 Create Tag

```bash
git tag -a v0.2.0 -m "Release v0.2.0

- Complete RAG evaluation framework
- 99%+ precision mode
- 15 built-in plugins
- Dashboard with auth
- See CHANGELOG.md for full details"

git push origin v0.2.0
```

### 9.2 Create Release on GitHub

1. Go to: https://github.com/YOUR_USERNAME/raglint/releases/new
2. Choose tag: `v0.2.0`
3. Release title: `RAGLint v0.2.0 - Production-Ready Release`
4. Description: Copy from CHANGELOG.md
5. Attach files:
   - dist/raglint-0.2.0-py3-none-any.whl
   - dist/raglint-0.2.0.tar.gz
6. Click "Publish release"

---

## Steg 10: Setup Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```bash
mkdir -p .github/ISSUE_TEMPLATE

cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With configuration '....'
3. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.11]
 - RAGLint version: [e.g. 0.2.0]
 - Installation method: [pip/git clone]

**Additional context**
Add any other context about the problem here.
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
EOF
```

---

## Steg 11: Setup Pull Request Template

```bash
cat > .github/pull_request_template.md << 'EOF'
## Description
<!-- Describe your changes in detail -->

## Related Issue
<!-- If fixing a bug, link to the issue here -->
Fixes #(issue)

## Type of Change
<!-- Mark with x -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Checklist
- [ ] My code follows the code style of this project
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] I have updated the documentation accordingly
- [ ] All tests pass locally
EOF
```

---

## Steg 12: Setup GitHub Actions (CI/CD)

Verify `.github/workflows/ci.yml` exists and update if needed:

```bash
ls -la .github/workflows/ci.yml
```

If missing or incomplete:
```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=raglint
    
    - name: Security scan
      run: |
        pip-audit
        bandit -r raglint/
```

---

## Steg 13: Update Repository Settings

On GitHub:

### 13.1 General Settings
1. Go to Settings
2. Features:
   - ✅ Issues
   - ✅ Projects (if you want)
   - ✅ Wiki (if you want)
   - ✅ Discussions (recommended!)

### 13.2 Branch Protection (Recommended)
1. Settings → Branches
2. Add rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

---

## Steg 14: Add README Badges

Update README.md with working badges:

```markdown
# RAGlint 🔍

[![PyPI version](https://badge.fury.io/py/raglint.svg)](https://pypi.org/project/raglint/)
[![Tests](https://github.com/YOUR_USERNAME/raglint/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/raglint/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/raglint.svg?style=social)](https://github.com/YOUR_USERNAME/raglint)
```

Commit and push:
```bash
git add README.md
git commit -m "Add GitHub badges"
git push
```

---

## Steg 15: Create GitHub Pages (Optional - For Docs)

1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /docs/_build/html
4. Save

**Or use ReadTheDocs** (recommended for Sphinx docs)

---

## ✅ Post-Setup Checklist

- [ ] Repository is public
- [ ] README displays correctly
- [ ] LICENSE file present
- [ ] .gitignore configured
- [ ] Initial commit pushed
- [ ] Release v0.2.0 created
- [ ] Issue templates created
- [ ] PR template created
- [ ] CI/CD workflow added
- [ ] Branch protection enabled
- [ ] Topics/tags added
- [ ] Badges updated
- [ ] GitHub Actions working

---

## 📢 Announce Your Repository

### On GitHub:
- Star your own repo (why not!)
- Watch for activity

### External:
- Tweet: "Just released RAGLint v0.2.0 - Open-source RAG evaluation framework with 99%+ precision! Check it out: [link]"
- LinkedIn post
- Reddit: r/Python, r/MachineLearning
- Hacker News (if you dare!)

---

## 🔄 Daily Workflow

```bash
# Morning routine
git pull origin main

# After changes
git add .
git commit -m "Description of changes"
git push origin main

# For new features
git checkout -b feature/new-feature
# ... make changes ...
git push origin feature/new-feature
# Then create PR on GitHub
```

---

## ⏱️ Estimated Time

- **Initial setup**: 30-60 minutes
- **Daily commits**: 2-5 minutes

---

**🎉 DONE! You now have a professional GitHub repository!**
