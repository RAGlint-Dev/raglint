#!/bin/bash
# RAGLint Demo Script - Visar hur du testar systemet

echo "🚀 RAGLint Demo - Steg för Steg"
echo "================================"
echo ""

# Steg 1: Aktivera environment
echo "📦 Steg 1: Aktivera virtual environment..."
cd /home/yesir/Dokument/RAGlint
source .venv/bin/activate
echo "✅ Environment aktiverat"
echo ""

# Steg 2: Verifiera installation
echo "🔍 Steg 2: Verifiera installation..."
python -c "import raglint; print('✅ RAGLint importeras korrekt')"
echo ""

# Steg 3: Visa CLI hjälp
echo "📖 Steg 3: Visa CLI kommandohäl..."
raglint --help
echo ""

# Steg 4: Analysera demo data
echo "🎯 Steg 4: Analysera demo data med Mock LLM..."
if [ -f demo_data.json ]; then
    raglint analyze demo_data.json --provider mock
    echo ""
    echo "✅ Analys klar! Rapport sparad i raglint_report.html"
else
    echo "❌ demo_data.json finns inte. Kör först:"
    echo "   Se QUICKSTART_SWEDISH.md för instruktioner"
fi
echo ""

# Steg 5: Visa plugins
echo "🔌 Steg 5: Visa tillgängliga plugins..."
raglint plugins list | head -20
echo ""

# Steg 6: Starta dashboard (optional)
echo "🌐 Steg 6: För att starta dashboard, kör:"
echo "   raglint dashboard"
echo ""
echo "   Sedan öppna: http://localhost:8000"
echo ""

# Steg 7: Kör tester
echo "🧪 Steg 7: För att köra tester:"
echo "   pytest -v                    # Alla tester"
echo "   pytest tests/core/ -v        # Core tester"
echo "   pytest --cov=raglint         # Med coverage"
echo ""

echo "✨ Demo klar! För mer information, se QUICKSTART_SWEDISH.md"
