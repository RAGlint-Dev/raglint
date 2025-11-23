# RAGLint Cheat Sheet 🚀

## 1. Setup
Always activate your virtual environment first:
```bash
source venv/bin/activate
```

## 2. Run Analysis
Analyze a JSON dataset to get quality metrics.
```bash
# Basic analysis (fast)
raglint analyze sample_data.json

# Smart analysis (requires OpenAI API key)
raglint analyze sample_data.json --smart --api-key sk-...
```

## 3. Web Dashboard
Visualize your results in a modern UI.
```bash
# Start the server
raglint dashboard

# Open in browser
# http://localhost:8000
```

## 4. Benchmarks
Test your RAG pipeline against standard datasets.
```bash
# Run SQUAD benchmark (50 examples)
raglint benchmark --dataset squad --subset-size 50

# Run CoQA benchmark
raglint benchmark --dataset coqa --subset-size 50
```

## 5. A/B Testing
Compare two configurations to see which is better.
```bash
raglint compare config_v1.yml config_v2.yml --dataset squad
```

## 6. Landing Page
View the marketing landing page.
```bash
# Open file in browser
xdg-open docs/landing/index.html
```
