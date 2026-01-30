# Contributing to Business Card Generator

Thank you for your interest in contributing to Business Card Generator! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version)
- Any relevant logs or screenshots

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- A clear description of the feature
- Use cases and benefits
- Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `uv run pytest`
5. Commit your changes with clear messages
6. Push to your fork
7. Open a Pull Request to the `master` branch

#### PR Guidelines

- Keep changes focused and atomic
- Include tests for new functionality
- Update documentation as needed
- Follow the existing code style
- Ensure all tests pass
- PRs require admin approval before merging to master

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/business-card-generator.git
cd business-card-generator

# Install dependencies with dev tools
uv sync --extra dev

# Run tests
uv run pytest

# Run the application
uv run python main.py
```

## Testing

We use pytest and hypothesis for testing. Please ensure:
- All tests pass before submitting a PR
- New features include appropriate tests
- Test coverage is maintained or improved

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run with verbose output
uv run pytest -v
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write clear docstrings for public APIs
- Keep functions focused and testable
- Use Qt signals/slots for component communication

## Architecture Guidelines

- Data models go in `src/business_card_generator/models/`
- Core logic goes in `src/business_card_generator/core/`
- UI components go in `src/business_card_generator/ui/`
- Use dataclasses for data models
- Use Qt's signal/slot mechanism for UI communication

## Questions?

Feel free to open an issue for any questions about contributing!
