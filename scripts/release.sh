#!/bin/bash

# Release helper script
# Usage: ./scripts/release.sh [major|minor|patch]

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 [major|minor|patch]"
    exit 1
fi

PART=$1

# Ensure we are on main
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "Error: Must be on main branch to release."
    exit 1
fi

# Ensure working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory not clean."
    exit 1
fi

echo "Bumping version ($PART)..."
# We assume bump2version or similar is installed, or we do simple sed replacement
# For this script, let's assume a simple manual update or use a tool if available.
# Since we don't have bump2version in requirements, we'll just echo instructions for now
# or implement a simple sed for pyproject.toml if the user wants automation.

# Let's try to use python to bump the version in pyproject.toml for a robust solution without extra deps
CURRENT_VERSION=$(grep -m1 'version = "' pyproject.toml | cut -d '"' -f 2)
echo "Current version: $CURRENT_VERSION"

# Calculate new version (very simple logic)
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

if [ "$PART" == "major" ]; then
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
elif [ "$PART" == "minor" ]; then
    MINOR=$((MINOR + 1))
    PATCH=0
elif [ "$PART" == "patch" ]; then
    PATCH=$((PATCH + 1))
else
    echo "Invalid argument. Use major, minor, or patch."
    exit 1
fi

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "New version: $NEW_VERSION"

# Update pyproject.toml
sed -i "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# Update __init__.py
sed -i "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" raglint/__init__.py

echo "Updated files. Committing and tagging..."

git add pyproject.toml raglint/__init__.py
git commit -m "Release v$NEW_VERSION"
git tag "v$NEW_VERSION"

echo "Release v$NEW_VERSION ready!"
echo "Run 'git push && git push --tags' to trigger CI/CD."
