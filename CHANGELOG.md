# Changelog

All notable changes to the Befit Gym project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- AGENTS.md with project structure, development commands, and coding conventions
- CLAUDE.md with repository overview, architecture, and AI assistant guidance
- CHANGELOG.md for tracking modifications across development
- Updated .gitignore with comprehensive patterns for Python, Django, Node, and IDE artifacts
- Frontend Docker setup with `frontend/Dockerfile` and `frontend/.dockerignore`
- Frontend service in `docker-compose.yml` for containerized Vite development on port 3000
- Frontend development environment file `frontend/.env.development` with `VITE_API_BASE_URL`

### Changed
- Frontend API client services now read API base URL from `VITE_API_BASE_URL` instead of hardcoded localhost endpoints
- Vite dev server configuration tuned for Dockerized hot reload stability

### Security
- Documented environment variable best practices for SECRET_KEY, DEBUG, and database credentials
