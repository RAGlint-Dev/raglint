# RAGLint Demo Script

**Duration:** ~2 minutes
**Goal:** Showcase RAGLint's value proposition: "Observability and Quality Assurance for RAG."

---

## Scene 1: The Problem (0:00 - 0:20)
**Visual:** Screen recording of a terminal or code editor.
**Voiceover:**
"Building RAG applications is easy. Ensuring they actually work is hard. Silent failures, hallucinations, and slow retrieval can kill your user experience without you even knowing."

## Scene 2: Installation & Setup (0:20 - 0:40)
**Visual:** Terminal.
**Action:**
1. Type `pip install raglint`
2. Show `raglint init` command.
**Voiceover:**
"Meet RAGLint. The all-in-one quality platform for RAG. It installs in seconds and integrates directly with your existing stack."

## Scene 3: Running Analysis (0:40 - 1:00)
**Visual:** VS Code / Terminal.
**Action:**
1. Show a simple Python script using `LangChainEvaluator`.
2. Run the script.
3. Show the CLI output with progress bars and final scores.
**Voiceover:**
"Just wrap your chain with our evaluator. RAGLint automatically measures faithfulness, context relevance, and latency. It even detects hallucinations using LLM-as-a-Judge metrics."

## Scene 4: The Dashboard (1:00 - 1:40)
**Visual:** Web Browser (RAGLint Dashboard).
**Action:**
1. Run `raglint dashboard`.
2. Navigate to `localhost:8000`.
3. Click on a recent run.
4. Expand a row to show "Retrieved Contexts" vs "Response".
5. Show the "Comparison" view between two runs.
**Voiceover:**
"But the real magic happens in the dashboard. Visualize your test runs, debug individual queries, and compare different model versions side-by-side. See exactly what your users are seeing."

## Scene 5: CI/CD & Closing (1:40 - 2:00)
**Visual:** GitHub Actions interface (green checkmarks).
**Action:**
1. Show a GitHub PR with a RAGLint comment/check.
2. Show the Landing Page.
**Voiceover:**
"Stop guessing and start measuring. Catch regressions before they hit production with our CI/CD integration. RAGLint: Ship your RAG apps with confidence. Try it today."

---

## Recording Tips
- **Resolution:** 1920x1080 (1080p)
- **Font Size:** Increase terminal/editor font size for readability.
- **Clean Environment:** Close unnecessary tabs and windows.
- **Pacing:** Speak clearly and pause slightly between scenes.
