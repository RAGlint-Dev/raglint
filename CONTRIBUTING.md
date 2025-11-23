# Contributing to RAGLint

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to RAGLint. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by the [RAGLint Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for RAGLint. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps to reproduce the problem** in as many details as possible.
- **Provide specific examples** to demonstrate the steps.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for RAGLint, including completely new features and minor improvements to existing functionality.

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
- **Explain why this enhancement would be useful** to most RAGLint users.

### Pull Requests

1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the test suite passes.
5.  Make sure your code lints.

## Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/raglint.git
    cd raglint
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -e ".[dev]"
    ```

4.  **Run tests:**
    ```bash
    pytest
    ```

## Style Guide

- We use `black` for code formatting.
- We use `isort` for import sorting.
- We use `flake8` for linting.
- We use `mypy` for static type checking.

Run the following before committing:
```bash
black .
isort .
flake8
mypy raglint
```

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
