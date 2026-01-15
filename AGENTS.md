# Repository Guidelines

These guidelines apply to all work in this repository and must be kept current.
Update this file as new preferences, constraints, or practices are discovered.

## Project Structure

- `backend/`: Django REST API and authentication services.
  - `accounts/`: custom user model, authentication logic, serializers, views, urls.
  - `django_project/`: Django settings and URL routing.
- `frontend/`: React application (Vite) with authentication UI and routing.
- `docker-compose.yml`: local development services (Django + Postgres).
- `API_DOCUMENTATION.md`, `FULL_STACK_README.md`: reference docs.

## Build, Test, and Development Commands

Backend (Docker):
- Start services: `docker compose up -d --build`
- Run migrations: `docker compose exec web python manage.py migrate`
- Create superuser: `docker compose exec web python manage.py createsuperuser`
- Stop services: `docker compose down`

Frontend:
- Install dependencies: `npm install` (in `frontend/`)
- Run dev server: `npm run dev` (in `frontend/`)

## Coding Style & Naming Conventions

- Python: 4-space indentation, PEP 8, explicit imports, avoid unused code.
- JavaScript: prefer modern ES syntax and consistent formatting.
- Functions: use verbs (e.g., `create_access_token`).
- Booleans: use `is_`, `has_`, `should_` prefixes.
- Avoid custom auth implementations; use Django auth and vetted libraries.

## Reliability Patterns

For all network or I/O operations:
- Use explicit timeouts.
- Use retries with exponential backoff and jitter.
- Keep workflows idempotent by default.
- Use structured logging for key operations and errors.

## Testing Guidelines

- Backend: use `python manage.py test` for Django tests.
- Frontend: add targeted tests when UI logic changes; keep tests focused.
- Stage one scope: prioritize login and logout tests.

## Commit & Pull Request Guidelines

- Prefer small, frequent commits for rollback safety.
- Commit messages must be short, imperative, and scoped.
- Check `git status` before staging.
- Do not use `git add -A` or `git add .` without review.
- Do not commit secrets, local `.env` files, or database artifacts.
- Update `CHANGELOG.md` for meaningful changes.

## Security & Configuration

- Store secrets in environment variables, not in source code.
- Default secure settings when env vars are missing (for example, `DEBUG=False`).
- Use Django deployment checks: `python manage.py check --deploy`.
- Maintain CSRF protections and CORS allowlists.

## AI Features (If Introduced)

- Define evaluation criteria before release.
- Add monitoring and user feedback loops.
- Document model inputs, outputs, and limitations.

## Documentation Maintenance

After significant changes:
- Update `CLAUDE.md` with new commands, architecture, or config changes.
- Update `CHANGELOG.md` with a concise entry.
- Update this file with new engineering preferences.
