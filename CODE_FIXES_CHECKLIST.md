# CODE FIXES CHECKLIST

## ⚠️ ÄRLIGT: Vad som måste fixas

Based on analysis, here are the code issues that need fixing:

---

## 1. Update raglint/__init__.py with new versions

**Current**: Unknown
**Should be**: `__version__ = "0.2.0"`

**Check**:
```bash
grep "__version__" raglint/__init__.py
```

**Fix if needed**:
Edit `raglint/__init__.py` and ensure:
```python
__version__ = "0.2.0"
```

---

## 2. Verify pyproject.toml URLs

**Current**: `https://github.com/raglint/raglint`
**Should update to**: YOUR actual GitHub username

**File**: `pyproject.toml` lines 51-54

**Fix**:
```toml
[project.urls]
"Homepage" = "https://github.com/YOUR_USERNAME/raglint"
"Bug Tracker" = "https://github.com/YOUR_USERNAME/raglint/issues"
Repository = "https://github.com/YOUR_USERNAME/raglint"
Changelog = "https://github.com/YOUR_USERNAME/raglint/blob/main/CHANGELOG.md"
```

---

## 3. Remove test database from git (if present)

**Check**:
```bash
ls -la raglint.db
```

**If exists**:
```bash
rm raglint.db
echo "raglint.db" >> .gitignore
git rm --cached raglint.db 2>/dev/null || true
```

---

## 4. Verify no hardcoded API keys

**Check**:
```bash
grep -r "sk-" raglint/ --include="*.py" | grep -v "example"
grep -r "api_key.*=" raglint/ --include="*.py" | grep -v "Optional\|None"
```

**Expected**: No results (all keys should be from env or config)

---

## 5. Update README badges with YOUR username

**File**: `README.md`

**Find** (around line 3-10):
```markdown
[![GitHub](https://img.shields.io/github/...)](https://github.com/raglint/raglint)
```

**Replace with**:
```markdown
[![GitHub](https://img.shields.io/github/...)](https://github.com/YOUR_USERNAME/raglint)
```

---

## 6. Verify precision mode imports work

**Test**:
```bash
python3 -c "from raglint.precision_mode import PrecisionMode; print('OK')"
python3 -c "from raglint.confidence import ConfidenceScorer; print('OK')"
python3 -c "from raglint.fact_extraction import FactExtractor; print('OK')"
python3 -c "from raglint.metrics.enhanced_faithfulness import EnhancedFaithfulnessScorer; print('OK')"
```

**Expected**: All print "OK"

**If error**: Fix import paths

---

## 7. Test CLI works

**Test**:
```bash
python3 -m raglint.cli --help
```

**Expected**: Shows help message

**If error**: Fix CLI module

---

## 8. Verify dashboard runs

**Test**:
```bash
# Start dashboard (will run in background)
timeout 5 python3 -m raglint.dashboard.app || true
```

**Expected**: Should start (will timeout after 5s, that's OK)

**If error before 5s**: Fix dashboard imports

---

## 9. Check for TODO/FIXME in critical files

**Check**:
```bash
grep -n "TODO\|FIXME" raglint/core.py raglint/metrics/*.py raglint/precision_mode.py
```

**Expected**: Should be empty (all todos removed)

**If found**: Decide if critical or can stay

---

## 10. Verify LICENSE file

**Check**:
```bash
head -5 LICENSE
```

**Expected**: Should show MIT License with correct year/author

**Fix if needed**: Update year to 2024-2025

---

## ✅ Quick Fix Script

Run this to fix common issues automatically:

```bash
#!/bin/bash
# Quick fixes script

echo "1. Checking __version__..."
grep "__version__" raglint/__init__.py || echo "__version__ = '0.2.0'" >> raglint/__init__.py

echo "2. Remove test database..."
rm -f raglint.db

echo "3. Add to gitignore..."
grep -q "raglint.db" .gitignore || echo "raglint.db" >> .gitignore

echo "4. Test imports..."
python3 -c "import raglint; print('raglint:', raglint.__version__)"
python3 -c "from raglint.precision_mode import PrecisionMode; print('precision_mode: OK')"
python3 -c "from raglint.confidence import ConfidenceScorer; print('confidence: OK')"

echo "5. Test CLI..."
python3 -m raglint.cli --help > /dev/null && echo "CLI: OK"

echo "✅ Basic checks complete!"
echo "⚠️ Remember to update GitHub URLs in pyproject.toml and README.md with YOUR username"
```

Save as `quick_fixes.sh` and run:
```bash
chmod +x quick_fixes.sh
./quick_fixes.sh
```

---

## ⏱️ Time Estimate

- Checks: 10 minutes
- Fixes: 15-30 minutes
- Verification: 10 minutes

**Total**: 35-50 minutes

---

## ✅ Final checklist before publishing:

- [ ] `__version__ = "0.2.0"` in __init__.py
- [ ] GitHub URLs updated with YOUR username
- [ ] No raglint.db in git
- [ ] No hardcoded API keys
- [ ] All new modules import correctly
- [ ] CLI works
- [ ] Dashboard starts
- [ ] No critical TODOs
- [ ] LICENSE updated
- [ ] .gitignore complete

**After all checked**: Ready for PyPI!
