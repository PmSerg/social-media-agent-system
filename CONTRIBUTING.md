# Contributing to Social Media Agent System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/social-media-agent-system.git
   cd social-media-agent-system
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/social-media-agent-system.git
   ```

## 🔧 Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend-system/requirements.txt
   pip install -r backend-system/requirements-test.txt
   ```

3. Set up pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 📝 Making Changes

### Branch Naming
- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactor: `refactor/description`

### Commit Messages
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

Examples:
```
feat: add Instagram support to copywriter agent
fix: handle rate limit errors in research agent
docs: update API endpoint documentation
```

### Code Style
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions

### Testing
- Write tests for new features
- Ensure all tests pass: `pytest`
- Maintain test coverage above 80%
- Test edge cases and error handling

## 🔄 Submitting Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature
   ```

4. Create a Pull Request:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Link related issues

## 📋 Pull Request Guidelines

### PR Title
Use the same format as commit messages:
`feat: add Instagram support to copywriter agent`

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated documentation

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] No new warnings
```

### Review Process
1. Automated tests must pass
2. Code review by maintainer
3. Address feedback
4. Merge when approved

## 🐛 Reporting Issues

### Bug Reports
Include:
- Python version
- OS details
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests
Include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Additional context

## 📚 Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md

## 🏗️ Project Structure

```
social-media-agent-system/
├── frontend-agencii/      # Agency Swarm frontend
├── backend-system/        # FastAPI backend
│   ├── agents/           # Agent implementations
│   ├── api/              # API endpoints
│   ├── shared/           # Shared utilities
│   └── tests/            # Test files
└── docs/                 # Documentation
```

## 🔍 Code Review Checklist

- [ ] Code is readable and well-commented
- [ ] No hardcoded values
- [ ] Error handling is comprehensive
- [ ] Security best practices followed
- [ ] Performance considerations addressed
- [ ] Tests cover new functionality

## 📞 Getting Help

- Create an issue for questions
- Join our Discord server (if applicable)
- Check existing issues and PRs
- Read the documentation

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in relevant documentation

Thank you for contributing to make this project better! 🚀