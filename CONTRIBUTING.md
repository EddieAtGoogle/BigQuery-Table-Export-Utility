# Contributing to BigQuery Table Export Utility

We appreciate your interest in contributing to the BigQuery Table Export Utility! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Code Style](#code-style)
8. [Documentation](#documentation)
9. [Security](#security)
10. [Community](#community)

## Code of Conduct

This project follows the [Google Open Source Community Guidelines](https://opensource.google/conduct/). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

1. Python 3.9+
2. Google Cloud SDK
3. Docker Desktop
4. Terraform 1.0.0+
5. Node.js 16+ (for frontend development)

### Initial Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/bq-table-to-csv.git
   cd bq-table-to-csv
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/original-org/bq-table-to-csv.git
   ```

## Development Setup

### Backend Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

### Frontend Development

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

### Local Testing Environment

1. Set up local environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

2. Start local services:
   ```bash
   docker-compose up -d
   ```

## Making Changes

### Branch Strategy

- Main branch: `main`
- Feature branches: `feature/description`
- Bug fix branches: `fix/description`
- Release branches: `release/version`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance

Example:
```
feat(export): add progress tracking for large exports

- Implement progress monitoring
- Add WebSocket updates
- Update UI components

Closes #123
```

## Testing

### Running Tests

1. Unit tests:
   ```bash
   python -m pytest tests/unit
   ```

2. Integration tests:
   ```bash
   python -m pytest tests/integration
   ```

3. Frontend tests:
   ```bash
   cd frontend
   npm test
   ```

### Test Coverage

- Aim for 80%+ coverage for new code
- Include both positive and negative test cases
- Mock external services appropriately

## Submitting Changes

1. Update your fork:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Push your changes:
   ```bash
   git push origin feature/your-feature
   ```

3. Create a Pull Request:
   - Use the provided template
   - Link related issues
   - Provide clear description
   - Include test results

## Code Style

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for formatting
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Use type hints

Example:
```python
from typing import List, Optional

def process_export(
    table_id: str,
    chunk_size: Optional[int] = None,
) -> List[str]:
    """Process table export with optional chunking.

    Args:
        table_id: BigQuery table ID
        chunk_size: Optional size for chunking

    Returns:
        List of export file paths
    """
    ...
```

### TypeScript/React Code Style

- Follow [Airbnb Style Guide](https://github.com/airbnb/javascript)
- Use ESLint and Prettier
- Implement proper typing

Example:
```typescript
interface ExportProps {
  tableId: string;
  onProgress?: (progress: number) => void;
}

const ExportComponent: React.FC<ExportProps> = ({
  tableId,
  onProgress,
}) => {
  // Implementation
};
```

## Documentation

### Code Documentation

- Add docstrings to all public functions
- Include type hints
- Document exceptions
- Provide usage examples

### API Documentation

- Use OpenAPI/Swagger
- Document all endpoints
- Include request/response examples
- Note authentication requirements

### Architecture Documentation

- Update architecture.md for system changes
- Include sequence diagrams
- Document design decisions
- Note security implications

## Security

### Security Considerations

1. Authentication
   - Use Google Cloud native auth
   - Implement proper token handling
   - Follow OAuth best practices

2. Authorization
   - Use least privilege principle
   - Document required permissions
   - Implement proper access controls

3. Data Protection
   - Use encryption in transit
   - Protect sensitive data
   - Follow security best practices

### Reporting Security Issues

- Do not open public issues
- Contact maintainers directly
- Provide detailed information
- Allow time for fixes

## Community

### Communication Channels

- GitHub Issues for bugs
- Discussions for features
- Stack Overflow for questions
- Google Cloud community

### Getting Help

1. Check documentation
2. Search existing issues
3. Ask in discussions
4. Contact maintainers

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## Additional Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform Documentation](https://www.terraform.io/docs) 