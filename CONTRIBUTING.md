# Contributing to DocuMind

Thank you for your interest in contributing to DocuMind! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Sampath1576/documind/issues)
2. If not, create a new issue with:
   - Clear title describing the bug
   - Detailed description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)

### Suggesting Enhancements

1. Check existing [Issues](https://github.com/Sampath1576/documind/issues) and [Discussions](https://github.com/Sampath1576/documind/discussions)
2. Create a new issue with:
   - Clear title
   - Detailed description of the enhancement
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add or update tests as needed
5. Run tests: `pytest tests/ -v`
6. Commit with clear messages: `git commit -m "Add: your feature description"`
7. Push to your fork: `git push origin feature/your-feature`
8. Open a Pull Request with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots for UI changes

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/documind.git
cd documind

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Write docstrings for all functions
- Keep functions focused and simple
- Max line length: 100 characters

## Testing Requirements

- All new features must include tests
- Maintain or improve code coverage
- Tests should be in the `tests/` directory
- Use descriptive test names: `test_<function>_<scenario>`

## Commit Messages

Use conventional commit format:

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `perf`: Performance
- `test`: Tests

Example:
```
feat: Add hybrid search combining BM25 and vector similarity

Implement ensemble retriever that combines lexical and semantic search.
This improves recall for queries with specific terms.

Closes #42
```

## Code Review Process

1. At least one maintainer will review your PR
2. We may request changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Questions?

Feel free to open a discussion or issue if you have questions!

Thank you for contributing! 🎉
