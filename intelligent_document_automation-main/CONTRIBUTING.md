# Contributing to Intelligent Document Automation

Thank you for your interest in contributing to the Intelligent Document Automation project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR installed
- Poppler library installed
- Git

### Setup Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/intelligent_document_automation-main.git
   cd intelligent_document_automation-main/intelligent_document_automation-main
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

## Development Workflow

### Branch Strategy

- `main` - Production branch
- `develop` - Development branch (if needed)
- Feature branches - `feature/your-feature-name`
- Bugfix branches - `bugfix/your-bugfix-name`

### Creating a Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes following the coding standards
2. Test your changes thoroughly
3. Update documentation as needed
4. Commit your changes with descriptive messages

### Commit Message Format

Follow conventional commit format:

```
type(scope): subject

body

footer
```

Types:
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting)
- `refactor` - Code refactoring
- `test` - Test changes
- `chore` - Maintenance tasks

Example:
```
feat(pipeline): add support for additional document types

Add support for invoices and receipts in addition to quotations,
SOWs, and contracts. Updated document classifier with new
patterns and rules.

Closes #123
```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### JavaScript Code

- Use modern ES6+ syntax
- Follow Airbnb JavaScript Style Guide
- Add comments for complex logic
- Use meaningful variable names

### CSS Code

- Use BEM naming convention for classes
- Group related styles
- Use CSS variables for theming
- Ensure responsive design

## Testing

### Running Tests

```bash
pytest
```

### Test Coverage

```bash
pytest --cov=src
```

### Writing Tests

- Write unit tests for new functions
- Test edge cases and error conditions
- Aim for >80% code coverage
- Use descriptive test names

## Documentation

### Code Documentation

- Add docstrings to all functions and classes
- Include parameter descriptions
- Document return values
- Add usage examples for complex functions

### README Updates

- Update README for new features
- Keep installation instructions current
- Update examples as needed
- Maintain clear structure

### API Documentation

- Update API endpoint documentation
- Include request/response examples
- Document error responses
- Keep version information current

## Submitting Changes

### Pull Request Process

1. Ensure your branch is up to date:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Run tests and ensure they pass
3. Create a pull request with:
   - Clear title and description
   - Reference related issues
   - Screenshots for UI changes
   - Testing instructions

4. Wait for code review
5. Address review feedback
6. Get approval and merge

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Questions or Issues?

Feel free to open an issue for questions or problems. We're happy to help!

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
