# Contributing Guide

## Branching Strategy (GitHub Flow)

- `main` — production-ready code
- `develop` — integration branch
- `feature/feature-name` — feature branches
- `bugfix/bug-name` — bug fix branches
- `hotfix/fix-name` — urgent fixes

## Workflow

1. Create a feature branch from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. Make your changes with meaningful commits:
   ```bash
   git add .
   git commit -m "feat(module): description of the change"
   ```

3. Push and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

4. Request code review from at least one team member.

5. After approval, merge into `develop`.

## Commit Message Convention (Conventional Commits)

```
type(scope): description

Types:
- feat:     New feature
- fix:      Bug fix
- docs:     Documentation changes
- style:    Code style (formatting, no logic change)
- refactor: Code refactoring
- test:     Adding or updating tests
- chore:    Build, CI, or tooling changes

Examples:
- feat(accounts): add user registration with email verification
- fix(reports): resolve duplicate report detection issue
- docs(readme): update installation instructions
- test(technicians): add unit tests for task assignment
```

## Code Standards

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Keep functions under 30 lines when possible
- Write unit tests for new features

## Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Tests added/updated
- [ ] No new warnings or errors
- [ ] Documentation updated if needed
