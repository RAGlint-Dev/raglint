# PyPI Publishing Guide - RAGLint

## ⚠️ VIKTIGT: Checklista INNAN publicering

Gå igenom denna checklista INNAN du publicerar till PyPI:

### ✅ Pre-Publishing Checklist

- [ ] **README.md är uppdaterad**
  - Installation instructions
  - Quick start
  - Features list
  - No broken links

- [ ] **CHANGELOG.md uppdaterad**
  - Version 0.2.0 changes documented
  - All features listed

- [ ] **Tests körs**
  ```bash
  pytest tests/ -v
  ```
  - Alla tests passar
  - Inga kritiska fel

- [ ] **Security scan clean**
  ```bash
  pip-audit
  bandit -r raglint/
  ```

- [ ] **Version nummer korrekt**
  - `pyproject.toml`: version = "0.2.0"
  - `raglint/__init__.py`: __version__ = "0.2.0"

- [ ] **Dependencies listade**
  - Alla runtime deps i pyproject.toml
  - Test deps i [dev]
  - Optional deps correct

---

## 📦 Steg 1: Install Build Tools

```bash
# I ditt virtual environment
pip install --upgrade pip
pip install build twine
```

**Verify installation**:
```bash
python -m build --version
twine --version
```

---

## 🏗️ Steg 2: Clean Previous Builds

```bash
# Ta bort gamla builds
rm -rf dist/ build/ *.egg-info

# Verify cleanup
ls -la | grep -E "dist|build|egg"
# (should show nothing)
```

---

## 📦 Steg 3: Build Package

```bash
# Build both wheel and source distribution
python -m build

# Check output
ls -lh dist/
```

**Expected output**:
```
raglint-0.2.0-py3-none-any.whl
raglint-0.2.0.tar.gz
```

---

## ✅ Steg 4: Verify Package

```bash
# Check package contents
tar -tzf dist/raglint-0.2.0.tar.gz | head -20
unzip -l dist/raglint-0.2.0-py3-none-any.whl | head -20

# Verify metadata
twine check dist/*
```

**Expected**:
```
Checking dist/raglint-0.2.0-py3-none-any.whl: PASSED
Checking dist/raglint-0.2.0.tar.gz: PASSED
```

❌ **If FAILED**: Fix errors before continuing!

---

## 🧪 Steg 5: Test Install Locally

```bash
# Create test environment
python -m venv test_venv
source test_venv/bin/activate

# Install from wheel
pip install dist/raglint-0.2.0-py3-none-any.whl

# Test import
python -c "import raglint; print(raglint.__version__)"
# Should print: 0.2.0

# Test CLI
raglint --help

# Cleanup
deactivate
rm -rf test_venv
```

---

## 🔐 Steg 6: Create PyPI Account

### 6.1 Main PyPI (Production)
1. Gå till https://pypi.org/account/register/
2. Registrera konto
3. Verifiera email
4. Enable 2FA (REKOMMENDERAT!)

### 6.2 Test PyPI (Optional but RECOMMENDED)
1. Gå till https://test.pypi.org/account/register/
2. Registrera separat konto
3. Verifiera email

---

## 🔑 Steg 7: Create API Token

### For PyPI:
1. Login till https://pypi.org
2. Account settings → API tokens
3. "Add API token"
   - Name: "RAGLint Publishing"
   - Scope: "Entire account" (first time) eller "Project: raglint" (later)
4. **COPY TOKEN NOW** (visas bara en gång!)
5. Spara i säker password manager

**Token format**: `pypi-AgEIcHlwaS5vcmc...` (starts with "pypi-")

### For Test PyPI (if testing first):
1. Login till https://test.pypi.org
2. Samma process
3. Token format: `pypi-AgEIcHlwaS5vcmc...`

---

## 🔧 Steg 8: Configure Credentials

### Option A: Using .pypirc (RECOMMENDED)

Create `~/.pypirc`:
```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_TEST_TOKEN_HERE...
EOF

# Secure the file
chmod 600 ~/.pypirc
```

### Option B: Environment Variable
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE...
```

---

## 🚀 Steg 9: Upload to Test PyPI (RECOMMENDED FIRST!)

```bash
# Upload to TEST PyPI first
twine upload --repository testpypi dist/*
```

**Expected output**:
```
Uploading distributions to https://test.pypi.org/legacy/
Uploading raglint-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB • 00:01
Uploading raglint-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45.0/45.0 kB • 00:00

View at:
https://test.pypi.org/project/raglint/0.2.0/
```

### Test Installation from Test PyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ raglint

# Verify
python -c "import raglint; print(raglint.__version__)"
```

---

## 🎉 Steg 10: Upload to REAL PyPI

**⚠️ VARNING: This is PERMANENT! Cannot delete packages from PyPI!**

```bash
# Final check
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

**Expected output**:
```
Uploading distributions to https://upload.pypi.org/legacy/
Uploading raglint-0.2.0-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 50.0/50.0 kB • 00:01
Uploading raglint-0.2.0.tar.gz
100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45.0/45.0 kB • 00:00

View at:
https://pypi.org/project/raglint/0.2.0/
```

---

## ✅ Steg 11: Verify Live Package

```bash
# Wait 1-2 minutes for PyPI to index

# Install from PyPI
pip install raglint

# Verify version
python -c "import raglint; print(raglint.__version__)"
# Should print: 0.2.0

# Test CLI
raglint --version
```

---

## 📢 Steg 12: Announce!

1. **Update README badges**
   ```markdown
   [![PyPI version](https://badge.fury.io/py/raglint.svg)](https://pypi.org/project/raglint/)
   [![PyPI downloads](https://img.shields.io/pypi/dm/raglint.svg)](https://pypi.org/project/raglint/)
   ```

2. **GitHub Release**
   - Create tag: `v0.2.0`
   - Write release notes (use CHANGELOG.md)
   - Upload dist files as assets

3. **Social Media**
   - LinkedIn post
   - Twitter/X announcement
   - Reddit (r/Python, r/MachineLearning)

---

## 🔄 Future Updates (v0.2.1, v0.3.0, etc.)

### Version Bump Process:

1. **Update version**:
   ```bash
   # In pyproject.toml
   version = "0.2.1"
   
   # In raglint/__init__.py
   __version__ = "0.2.1"
   ```

2. **Update CHANGELOG.md**

3. **Build and upload**:
   ```bash
   rm -rf dist/ build/
   python -m build
   twine check dist/*
   twine upload dist/*
   ```

---

## 🆘 Troubleshooting

### Error: "File already exists"
**Problem**: Version already published to PyPI
**Solution**: Bump version number (can't overwrite!)

### Error: "Invalid distribution file"
**Problem**: Package build issue
**Solution**: 
```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine check dist/*
```

### Error: "403 Forbidden"
**Problem**: Wrong token or permissions
**Solution**:
- Verify token copied correctly
- Check token hasn't expired
- Ensure .pypirc has __token__ as username

### Error: "Package name already taken"
**Problem**: Name collision
**Solution**: Choose different name (if first upload)

---

## 📊 Post-Publishing Checklist

- [ ] Package appears on https://pypi.org/project/raglint/
- [ ] `pip install raglint` works
- [ ] CLI works: `raglint --help`
- [ ] Import works: `import raglint`
- [ ] Version correct: `raglint.__version__`
- [ ] README displays correctly on PyPI
- [ ] Links work in PyPI description
- [ ] GitHub release created
- [ ] Social media announcement made

---

## 🎯 Quick Reference

**Build**:
```bash
python -m build
```

**Check**:
```bash
twine check dist/*
```

**Upload (Test)**:
```bash
twine upload --repository testpypi dist/*
```

**Upload (Production)**:
```bash
twine upload dist/*
```

**Install**:
```bash
pip install raglint
```

---

## ⏱️ Estimated Time

- **First time** (med setup): 1-2 timmar
- **Subsequent updates**: 15-30 minuter

---

**🎉 LYCKA TILL! Efter publicering har du ett RIKTIGT open-source projekt!**
