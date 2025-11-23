# RAGlint Community Guidelines

Welcome to the RAGlint community! We're building the best RAG evaluation platform, and we need your help.

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in RAGlint a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, level of experience, nationality, personal appearance, race, religion, or sexual identity.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behavior:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Violations can be reported to team@raglint.ai. All complaints will be reviewed and result in appropriate response.

---

## 💡 How to Contribute

### Reporting Bugs

Found a bug? Help us fix it!

1. **Check existing issues** - Someone may have already reported it
2. **Create a detailed bug report**:
   - What you expected
   - What actually happened
   - Steps to reproduce  
   - Environment (Python version, OS, RAGlint version)
   - Error messages/logs

Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)

### Suggesting Features

Have an idea? We'd love to hear it!

1. **Check existing feature requests**
2. **Create a feature request** with:
   - Problem it solves
   - Proposed solution
   - Alternative solutions considered
   - Use cases

Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)

### Contributing Code

Ready to code? Awesome!

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/amazing-plugin`
3. **Make your changes**
4. **Add tests** (we maintain 83%+ coverage!)
5. **Run tests**: `pytest`
6. **Run linting**: `ruff check raglint/` and `black raglint/`
7. **Commit**: Use [conventional commits](https://conventionalcommits.org/)
8. **Push and create PR**

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Contributing Plugins

Plugins are the heart of RAGlint's extensibility!

**What makes a good plugin:**
- ✅ Solves a specific, clear problem
- ✅ Well-documented with examples
- ✅ Tested (includes unit tests)
- ✅ Follows plugin interface

See [Plugin Development Guide](examples/plugins/README.md)

**Plugin bounty program** (coming soon!): Earn $100-500 for accepted plugins.

---

## 🎯 Development Workflow

### Setting Up Development Environment

```bash
# Clone repo
git clone https://github.com/yourusername/raglint.git
cd raglint

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in dev mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=raglint --cov-report=term-missing

# Specific test
pytest tests/test_llm.py::test_openai_llm
```

### Code Quality

```bash
# Format code
black raglint/ tests/

# Lint
ruff check raglint/

# Type checking (if using mypy)
mypy raglint/
```

---

## 🏆 Recognition

We value every contribution! Contributors will be recognized:

### Hall of Fame
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor badge

### Special Recognition
- **Top Contributors**: Featured on README
- **Plugin Authors**: Listed in plugin documentation
- **Major Features**: Blog post highlighting your work

### Swag
Coming soon: RAGlint t-shirts and stickers for significant contributors!

---

## 📢 Communication Channels

### GitHub
- **Issues**: Bug reports, feature requests
- **Discussions**: Questions, ideas, show-and-tell
- **Pull Requests**: Code contributions

### Discord (coming soon!)
- Real-time help
- Community chat
- Office hours with maintainers

### Twitter/X
- Follow [@raglint](https://twitter.com/raglint) (if exists)
- Use #RAGlint hashtag

### Email
- Security issues: security@raglint.ai
- General inquiries: team@raglint.ai

---

## 🗓️ Community Events

### Office Hours (planned)
- **When**: Every other Friday, 10am PT
- **Where**: Discord voice channel
- **What**: Q&A, pair programming, feature discussions

### Monthly Challenges (planned)
- Build the best custom plugin
- Optimize a RAG pipeline
- Write the best tutorial

### Conferences
We'll be at:
- PyData conferences
- MLOps World
- AI Engineer Summit

Come say hi!

---

##  📚 Resources for Contributors

### Documentation
- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Plugin Development](examples/plugins/README.md)
- [Best Practices](docs/BEST_PRACTICES.md)

### Code Examples
- [Built-in Plugins](raglint/plugins/builtins/)
- [Example Use Cases](examples/)
- [Integration Tests](tests/dashboard/test_api.py)

### Learning
- **RAG Fundamentals**: [Pinecone's RAG Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- **Evaluation Metrics**: [RAGAS Paper](https://arxiv.org/abs/2309.15217)

---

## 🎓 Mentorship

New to open source? We've got you covered!

- **Good First Issues**: Tagged with `good-first-issue`
- **Mentorship**: Request a mentor in Discord
- **Pair Programming**: Schedule sessions with maintainers

---

## 🚀 Roadmap

### Current Focus (Q4 2024)
- Expanding plugin ecosystem
- Dashboard improvements
- Performance optimizations

### Future Plans
- Multi-language support
- Cloud deployment options
- Enterprise features (SSO, audit logs)

See [GitHub Projects](https://github.com/yourusername/raglint/projects) for detailed roadmap.

---

## ❓ FAQ

**Q: Can I contribute if I'm a beginner?**  
A: Absolutely! Look for `good-first-issue` labels and ask for help.

**Q: How long until my PR is reviewed?**  
A: We aim for 48 hours for initial feedback, 1 week for full review.

**Q: Can I contribute documentation?**  
A: Yes! Docs are just as valuable as code.

**Q: Do I need to sign a CLA?**  
A: Not currently. We may add one in the future.

**Q: Can I use RAGlint in commercial projects?**  
A: Yes! It's MIT licensed.

---

## 🙏 Thank You!

Every contribution, no matter how small, makes RAGlint better. Thank you for being part of this community!

**Together, we're making RAG evaluation accessible to everyone.** 🌟

---

**Last Updated**: 2025-11-22
