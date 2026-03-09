# Befit Gym

Full-stack fitness platform with a Django REST backend and React frontend, focused on JWT authentication, user fitness profile management, equipment selection, and AI-powered weekly routine generation (Gemini).

---

## Current Features

### 1) Auth & Session (JWT)
- User registration by email/password with validation (`/api/auth/register/`).
- Login returning `access` and `refresh` tokens (`/api/auth/login/`).
- Token refresh (`/api/auth/token/refresh/`).
- Frontend session persistence via `localStorage`.
- Protected frontend navigation through `PrivateRoute`.

### 2) User Profile
- Partial profile updates (`PATCH /api/auth/profile/`).
- Fitness profile fields:
  - `age`, `weight`, `height`
  - `goal` (lose weight, gain muscle, strength, etc.)
  - `level` (beginner/intermediate/advanced)
- Subscription status display (`active_subscription`) in layout.

### 3) Equipment Selector
- Equipment catalog grouped by categories (free weights, machine, cardio, accessory, calisthenics).
- Interactive per-item and per-category selection on frontend.
- User selection persistence:
  - `GET /api/auth/user-equipment/`
  - `POST /api/auth/user-equipment/`
- Backward-compatible payload support (`equipment_ids` and legacy `equipamientos`).

### 4) AI Routine Engine (Gemini)
- Protected routine generation endpoint: `POST /api/auth/generate-routine/`.
- Uses user profile + available equipment to generate weekly plans.
- Implemented pipeline:
  1. user/equipment validation
  2. available exercise filtering
  3. Gemini prompt generation
  4. JSON response parsing and validation
  5. transactional persistence of `Routine`, `RoutineExercise`, and `WeeklyPlan`
- Automatically deactivates previous active plans when a new one is generated.

### 5) Weekly Plan & Training Catalog
- Authenticated user weekly plan listing (`/api/auth/weekly-plan/`).
- Day-level detail (`/api/auth/weekly-plan/{id}/`).
- Exercise catalog query (optional muscle-group filter).
- Routine and equipment read-only catalogs.
- Dashboard empty-state action: “Generate Plan with AI”.

### 6) Frontend UX (React)
- Public landing page.
- Complete register/login flow.
- Responsive private layout sidebar (`Dashboard`, `Profile`, `Equipment`).
- Dashboard weekly plan visualization and day details.
- Tailwind UI with Lucide iconography.

---

## Tech Stack

### Backend
- **Python + Django**: `Django==6.0.1`
- **Django REST Framework**: `djangorestframework==3.15.2`
- **JWT Auth**: `djangorestframework-simplejwt==5.4.0`, `PyJWT==2.10.1`
- **PostgreSQL driver**: `psycopg2-binary==2.9.11`
- **CORS**: `django-cors-headers==4.3.1`
- **AI SDK**: `google-generativeai==0.8.4` (Gemini)

### Frontend
- **React**: `react@^19.2.0`, `react-dom@^19.2.0`
- **Router**: `react-router-dom@^6.22.0`
- **Build tool**: `vite@^7.2.4`
- **Styling**:
  - `tailwindcss@^3.4.19`
  - `bootstrap@^5.3.2`
  - `bootstrap-icons@^1.11.3`
- **Icons**: `lucide-react@^0.563.0`
- **HTTP client**: `axios@^1.6.7`

### Infra
- **Docker Compose** services:
  - `web` (Django)
  - `db` (`postgres:14`)

---

## Database Schema

Core domain models (`accounts/models.py`):

- **User**
  - email-based authentication (custom user model)
  - fitness profile (`weight`, `height`, `age`, `goal`, `level`)
  - membership state (`active_subscription`)
  - preferred equipment relation

- **Equipment**
  - normalized equipment catalog by category

- **Exercise**
  - training metadata (`muscle_group`, `difficulty`, `description`, `image_url`)

- **Routine**
  - routine container with level and estimated duration

- **RoutineExercise** (through table)
  - execution attributes: `series`, `repetitions`, `rest_seconds`, `order`, `notes`

- **WeeklyPlan**
  - assigns one routine to one user/day
  - includes `active` flag and notes

### Key Relationships
- **User ↔ Equipment**: `ManyToMany` (`preferred_equipment`)
- **Exercise ↔ Equipment**: `ManyToMany` (`equipment`)
- **Routine ↔ Exercise**: `ManyToMany` through `RoutineExercise`
- **User → WeeklyPlan**: `OneToMany`
- **Routine → WeeklyPlan**: `OneToMany`

---

## API Endpoints

Base URL: `http://localhost:8000/api/auth/`

### Auth
- `POST /register/`
- `POST /login/`
- `POST /token/refresh/`

### Profile
- `GET /profile/`
- `PATCH /profile/`

### Equipment selection
- `GET /user-equipment/`
- `POST /user-equipment/`

### AI
- `POST /generate-routine/`

### Catalogs and plans (current primary routes)
- `GET /equipment/`
- `GET /equipment/{id}/`
- `GET /exercises/` (optional filter: `?muscle_group=...`)
- `GET /exercises/{id}/`
- `GET /routines/`
- `GET /routines/{id}/`
- `GET /weekly-plan/`
- `GET /weekly-plan/{id}/`

### Legacy compatibility routes (Phase 1)
- `GET /equipamientos/`
- `GET /ejercicios/` (optional filter: `?grupo_muscular=...`)
- `GET /rutinas/`
- `GET /plan-semanal/`
- `POST /generar-rutina/`
- `GET/POST /user-equipamiento/`

> Note: these catalog resources are implemented as `ReadOnlyModelViewSet` (list/retrieve only).

---

## Roadmap (Backlog)

1. **Payments & subscriptions**
- Payment gateway integration (Stripe / Mercado Pago).
- Lifecycle states: renewal, expiration, billing, invoices.

2. **Workout history**
- Session tracking (completed/skipped).
- Volume/load progression and personal records.

3. **Notifications**
- Workout reminders.
- Subscription expiration alerts.
- Push/email/in-app channels.

4. **Production observability & security**
- Structured logging, traces, metrics.
- Rate limiting, JWT hardening, secret rotation.
- Robust error monitoring and auditability.

5. **Operational admin/content management**
- Backoffice CRUD for exercises/equipment/routine templates.
- AI routine moderation and plan versioning.

6. **Advanced AI experience**
- User feedback adaptation (fatigue, pain, preference).
- Partial regeneration by day/muscle group.
- Basic plan explainability.

7. **Testing and CI/CD**
- Full backend/frontend suites (unit, integration, e2e).
- Quality pipeline (lint, test, build, deploy).

8. **Architecture scalability**
- Optional service split for AI/training domain.
- Caching for catalogs and plans.
- Async job queues for routine generation.

---

## Project Structure

```text
befit-gym/
├─ backend/
│  ├─ accounts/
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ views.py
│  │  ├─ urls.py
│  │  └─ services/routine_generator.py
│  ├─ django_project/
│  │  ├─ settings.py
│  │  └─ urls.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ context/
│  │  └─ services/
│  └─ package.json
└─ docker-compose.yml
```

---

## Current Status

Development-ready and functional for:
- auth onboarding,
- user profile capture,
- equipment selection,
- AI routine generation,
- weekly plan visualization.

Recommended next product milestone: **payments + workout history + notifications**.