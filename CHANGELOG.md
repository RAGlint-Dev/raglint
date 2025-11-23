# Changelog

All notable changes to RAGLint will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-21

### Added
- **Web Dashboard:** Full observability UI with run history, details, and comparison view.
- **LangChain Integration:** `LangChainEvaluator` for easy integration with existing chains.
- **Benchmark Suite:** SQUAD dataset support and `BenchmarkRegistry`.
- **Cost & Latency Tracking:** Token usage and performance metrics.
- **API Documentation:** Sphinx-generated docs at `docs/`.
- **Async Processing:** Parallel LLM calls for 2-20x speedup.
- **CI/CD:** GitHub Actions pipeline for automated testing.
- **Landing Page:** Marketing assets in `docs/landing/`.

### Changed
- Refactored `raglint.core` for better async support.
- Improved CLI output with progress bars.
- Updated `raglint.yml` configuration structure.

## [0.1.0] - 2024-11-21

### Added
- Initial release
- Basic RAG pipeline analysis
- Chunking metrics (size distribution, coherence)
- Retrieval metrics (precision, recall, MRR, nDCG)
- Smart metrics (semantic similarity, faithfulness scoring)
- HTML report generation with visualizations
- CLI interface
- Configuration via YAML
- Support for OpenAI and Ollama LLM providers
- Mock mode for testing without API calls
- Basic test suite

### Features
- Analyze chunk size and semantic coherence
- Calculate retrieval quality metrics
- LLM-based faithfulness and relevance scoring
- Generate interactive HTML reports with charts
- Command-line interface for easy integration
- Configurable via `raglint.yml`

[Unreleased]: https://github.com/yourusername/raglint/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/raglint/releases/tag/v0.1.0
