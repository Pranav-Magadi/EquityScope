# Contributing to EquityScope

Thank you for your interest in contributing to EquityScope! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/EquityScope.git`
3. Run setup: `./start_development.sh`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

### Development Environment
- Python 3.9+ for backend
- Node.js 16+ for frontend
- FastAPI for backend API
- React 18+ for frontend

## 📝 Code Standards

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints where possible
- Add docstrings for functions and classes
- Write unit tests for new features

### JavaScript/TypeScript (Frontend)
- Use TypeScript for new components
- Follow React best practices
- Use Tailwind CSS for styling
- Add PropTypes or TypeScript interfaces

### Git Workflow
1. Create feature branches from `main`
2. Use descriptive commit messages
3. Keep commits atomic and focused
4. Rebase before submitting PR

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 🔧 Architecture Guidelines

### Backend Structure
```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── services/     # Business logic
│   ├── models/       # Data models
│   └── main.py       # FastAPI app
```

### Frontend Structure
```
frontend/src/
├── components/       # React components
├── services/        # API calls
├── data/           # Static data
└── App.tsx         # Main app
```

## 📋 Pull Request Process

1. **Before Submitting**
   - Run all tests
   - Update documentation
   - Add changelog entry
   - Ensure code follows style guidelines

2. **PR Description**
   - Clear title describing the change
   - Detailed description of what was changed
   - Screenshots for UI changes
   - Link to related issues

3. **Review Process**
   - All tests must pass
   - Code review by maintainers
   - Address feedback promptly
   - Squash commits before merge

## 🐛 Bug Reports

When reporting bugs, include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node versions)
- Error messages and logs
- Screenshots if applicable

## 💡 Feature Requests

For new features:
- Check existing issues first
- Provide clear use case
- Consider implementation complexity
- Discuss in issues before coding

## 🔒 Security

- Report security issues privately
- Don't commit API keys or secrets
- Use environment variables for configuration
- Follow security best practices

## 📚 Documentation

- Update README for new features
- Add API documentation
- Include code comments
- Update deployment guides

## 🎯 Areas for Contribution

### High Priority
- Additional DCF models
- Enhanced AI analysis
- Performance optimizations
- Mobile responsiveness

### Medium Priority
- Additional data sources
- Export functionality
- User authentication
- Caching improvements

### Good First Issues
- UI/UX improvements
- Documentation updates
- Test coverage
- Bug fixes

## 💬 Community

- Be respectful and inclusive
- Help others learn
- Share knowledge
- Follow code of conduct

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
