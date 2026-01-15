# CLAUDE.md

This file provides guidance for Claude Code when working in this repository.
Keep it current; update after significant changes.

## Repository Overview

Gym management application with:
- Django REST backend using a custom user model and JWT authentication.
- React frontend with protected routes and login/logout flows.

Stage one scope: login and logout must work as expected.

## Commands

Backend (Docker):
```bash
docker compose up -d --build
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose down
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Architecture

```
backend/
  accounts/                  # User model + auth endpoints
  django_project/            # Settings and URL routing
frontend/
  src/components/            # Login/Register/Dashboard/PrivateRoute
  src/context/AuthContext.jsx
  src/services/authService.js
docker-compose.yml
```

## Key Conventions

- Use Django authentication primitives; do not reimplement password handling.
- Prefer a custom user model early to avoid migration risk.
- Use environment variables for secrets and deployment config.
- Default secure settings when env vars are missing.
- Use explicit timeouts and retries with exponential backoff + jitter for I/O.
- Use structured logging for service boundaries and errors.
- If AI features are introduced, define evaluation metrics, monitoring, and feedback loops.

## Security and Operations

- Run `python manage.py check --deploy` before production changes.
- Keep Django current; do not skip releases when upgrading.
- Use CSRF protections and CORS allowlists.

## Documentation Maintenance

After significant changes, update:
- `AGENTS.md` for workflow and coding standards.
- `CHANGELOG.md` for user-visible or operational changes.
- This file for command, architecture, or config updates.
