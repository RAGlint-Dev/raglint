# Publishing to PyPI

This guide explains how to publish RAGLint to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org/account/register/
   - Verify your email

2. **API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope "Entire account"
   - Save the token (starts with `pypi-`)

3. **Test PyPI Account** (optional but recommended)
   - Create account at https://test.pypi.org/account/register/
   - Create API token

## Setup GitHub Secrets

For automated publishing via GitHub Actions:

1. Go to your repository settings
2. Navigate to Secrets and variables → Actions
3. Add new repository secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token

## Manual Publishing

### 1. Install Build Tools

```bash
pip install build twine
```

### 2. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

This creates:
- `dist/raglint-0.2.0.tar.gz` (source distribution)
- `dist/raglint-0.2.0-py3-none-any.whl` (wheel)

### 3. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ --no-deps raglint

# Test it works
raglint --help
```

### 4. Publish to PyPI

```bash
twine upload dist/*
```

Enter your username (`__token__`) and API token when prompted.

### 5. Verify

```bash
# Install from PyPI
pip install raglint

# Test
raglint --help
python -c "from raglint import RAGPipelineAnalyzer; print('Success!')"
```

## Automated Publishing (GitHub Actions)

The project includes automated publishing via GitHub Actions.

### Create a Release

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. **Update CHANGELOG.md**:
   ```markdown
   ## [0.2.0] - 2024-11-21
   ### Added
   - Async processing
   - ...
   ```

3. **Commit and push**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to 0.2.0"
   git push
   ```

4. **Create and push tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

5. **GitHub Actions automatically**:
   - Runs all tests
   - Builds the package
   - Publishes to PyPI

### Monitor the Release

- Check GitHub Actions: `https://github.com/yourusername/raglint/actions`
- Check PyPI: `https://pypi.org/project/raglint/`

## Version Numbering

RAGLint follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features (backward compatible)
- **PATCH** (x.x.1): Bug fixes

Examples:
- `0.1.0` → `0.2.0`: Added async processing (new feature)
- `0.2.0` → `0.2.1`: Fixed bug in HTML generation
- `0.2.1` → `1.0.0`: Changed API (breaking change)

## Checklist Before Publishing

- [ ] All tests pass locally (`pytest`)
- [ ] Coverage meets threshold (≥75%)
- [ ] Version bumped in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] README.md is current
- [ ] Documentation is up-to-date
- [ ] Examples work
- [ ] Committed all changes
- [ ] Tagged release

## Post-Publication

### Announce the Release

1. **Create GitHub Release**:
   - Go to https://github.com/yourusername/raglint/releases
   - Click "Create a new release"
   - Select your tag
   - Add release notes from CHANGELOG.md
   - Publish

2. **Update Documentation**:
   - Ensure README badges show correct version
   - Update any version-specific docs

3. **Social Media** (optional):
   - Tweet about the release
   - Post on Reddit (r/Python, r/MachineLearning)
   - Share on LinkedIn

### Monitor

- Check PyPI download stats
- Watch for issues on GitHub
- Respond to user feedback

## Troubleshooting

### "Package already exists"
- You can't re-upload the same version
- Bump version and try again

### "Invalid credentials"
- Ensure you're using `__token__` as username
- Check your API token is correct
- Token should start with `pypi-`

### "File not found"
- Ensure you ran `python -m build` first
- Check `dist/` directory exists

### Test import fails
- Install dependencies: `pip install -e .`
- Check for circular imports
- Verify all packages have `__init__.py`

## Resources

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/
- GitHub Actions: https://docs.github.com/en/actions
