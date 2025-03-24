# Contributing to GCP VM Manager

Thank you for considering contributing to GCP VM Manager! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by its Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

Bug reports help make GCP VM Manager more stable. When you're creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps to reproduce the problem
- Describe the behavior you observed and why it's problematic
- Include version information (Python version, OS, package versions)
- Include error messages or screenshots if applicable

### Suggesting Features

Feature suggestions are always welcome. Please provide:

- A clear and detailed explanation of the feature
- The motivation for the feature (why would it be useful?)
- Possible implementations or design ideas (if you have any)

### Pull Requests

Here's the general process for submitting code changes:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-new-feature`)
3. Make your changes
4. Add or update tests for your changes
5. Run the tests and ensure they pass
6. Update documentation if necessary
7. Commit your changes (`git commit -am 'Add new feature'`)
8. Push to the branch (`git push origin feature/my-new-feature`)
9. Submit a Pull Request

## Coding Guidelines

### Code Style

- Follow PEP 8 standards
- Use meaningful variable and function names
- Add type hints where appropriate
- Add docstrings for all functions, classes, and modules

### Tests

- Add tests for new functionality
- Ensure all tests pass before submitting a Pull Request
- Try to maintain or improve the current test coverage

### Documentation

- Update the README.md if you're changing or adding features
- Add docstrings to your code
- Include usage examples for new features

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Run the tests: `python -m unittest discover -s tests`

## Running Tests

```bash
# Run all tests
python -m unittest discover -s tests

# Run tests with coverage
python run_coverage.py
```

## License

By contributing to GCP VM Manager, you agree that your contributions will be licensed under the project's MIT License. 