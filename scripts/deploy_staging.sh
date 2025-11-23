#!/bin/bash
set -e

echo "🚀 Deploying RAGLint to Staging..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up -d --build

echo "✅ Deployment complete!"
echo "🌍 Dashboard available at http://localhost:8000"
echo "📝 Logs:"
docker-compose logs -f raglint
