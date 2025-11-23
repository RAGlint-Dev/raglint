# GitHub Actions CI/CD

RAGLint uses GitHub Actions for continuous integration and deployment.

## Workflows

### CI (Continuous Integration)

**File:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Jobs:**
1. **Test** - Run tests on Python 3.10, 3.11, 3.12
   - Lint with ruff
   - Format check with black
   - Run pytest with coverage
   - Upload to Codecov

2. **Security** - Security scanning
   - Bandit (code security)
   - Safety (dependency vulnerabilities)

### Release (PyPI Publishing)

**File:** `.github/workflows/release.yml`

**Triggers:**
- Git tags matching `v*.*.*` (e.g., `v0.1.0`)
- Manual workflow dispatch

**Jobs:**
1. Build Python package
2. Check package with twine
3. Publish to Test PyPI (manual dispatch)
4. Publish to PyPI (on tags)
5. Create GitHub release

**Usage:**
```bash
# Create and push a tag
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically:
# 1. Build the package
# 2. Publish to PyPI
# 3. Create a GitHub release
```

### Docker Build

**File:** `.github/workflows/docker.yml`

**Triggers:**
- Push to `main`
- Git tags matching `v*.*.*`
- Pull requests to `main`
- Manual workflow dispatch

**Jobs:**
1. Build Docker image
2. Push to GitHub Container Registry (ghcr.io)
3. Test image (on PRs)

**Image Tags:**
- `latest` - Latest main branch
- `v1.0.0` - Semantic version tags
- `sha-abc123` - Git commit SHA

**Usage:**
```bash
# Pull the latest image
docker pull ghcr.io/yourusername/raglint:latest

# Run RAGLint dashboard
docker run -p 8000:8000 ghcr.io/yourusername/raglint:latest
```

### Benchmark (Weekly Testing)

**File:** `.github/workflows/benchmark.yml`

**Triggers:**
- Weekly schedule (Monday 00:00 UTC)
- Manual workflow dispatch

**Jobs:**
1. Run SQUAD benchmark
2. Upload results as artifacts
3. Comment results on PRs (if applicable)

## Setting Up

### 1. PyPI Secrets

Add these secrets to your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Add secrets:
   - `PYPI_API_TOKEN` - PyPI API token
   - `TEST_PYPI_API_TOKEN` - Test PyPI token (optional)

**Get PyPI token:**
```bash
# 1. Create account at https://pypi.org/
# 2. Go to Account Settings → API tokens
# 3. Create token with "Upload packages" scope
# 4. Copy token and add to GitHub secrets
```

### 2. GitHub Container Registry

No setup needed! GitHub automatically provides GITHUB_TOKEN with package write permissions.

## Status Badges

Add these to your README.md:

```markdown
![CI](https://github.com/yourusername/raglint/workflows/CI/badge.svg)
![PyPI](https://img.shields.io/pypi/v/raglint)
![Docker](https://ghcr-badge.egpl.dev/yourusername/raglint/latest_tag?trim=major&label=docker)
[![codecov](https://codecov.io/gh/yourusername/raglint/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/raglint)
```

## Manual Workflows

### Test Release to Test PyPI

```bash
# From GitHub UI:
# 1. Go to Actions → Release to PyPI
# 2. Click "Run workflow"
# 3. Select branch
# 4. Click "Run workflow"
```

### Build Docker Image

```bash
# From GitHub UI:
# 1. Go to Actions → Docker Build
# 2. Click "Run workflow"
# 3. Select branch
# 4. Click "Run workflow"
```

### Run Benchmark

```bash
# From GitHub UI:
# 1. Go to Actions → Benchmark
# 2. Click "Run workflow"
# 3. Wait for results
# 4. Download artifacts
```

## Local Testing

Test workflows locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run CI workflow
act -j test

# Run release workflow
act -j build-and-publish --secret-file .secrets

# Run Docker build
act -j build-and-push
```

## Troubleshooting

### PyPI Upload Fails

**Error:** `File already exists`

**Solution:** Increment version in `pyproject.toml` before creating tag.

### Docker Build Fails

**Error:** `denied: permission_denied`

**Solution:** Ensure `packages: write` permission in workflow file.

### Tests Fail on CI but Pass Locally

**Possible causes:**
1. Missing dependencies in CI
2. Environment variables not set
3. Python version differences

**Debug:**
```yaml
- name: Debug environment
  run: |
    python --version
    pip list
    env
```

## Best Practices

1. **Version Bumping**
   - Update `pyproject.toml` version
   - Update `CHANGELOG.md`
   - Create git tag matching version

2. **Testing Before Release**
   - Run tests locally
   - Test with `./release.sh`
   - Verify package builds cleanly

3. **Docker Images**
   - Keep images small
   - Use `.dockerignore`
   - Test locally before pushing

4. **Security**
   - Never commit secrets
   - Use GitHub Secrets
   - Rotate tokens periodically

## See Also

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Publishing Guide](https://packaging.python.org/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
