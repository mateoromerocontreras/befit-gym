# Befit Gym - Full Stack Application

Complete authentication system with Django REST API backend and React frontend.

## Architecture

### Backend (Django + PostgreSQL)
- **Location**: `/backend`
- **Port**: 8000
- **Database**: PostgreSQL 14
- **Features**:
  - Custom User model with email-based authentication
  - JWT token authentication (djangorestframework-simplejwt)
  - RESTful API endpoints
  - CORS enabled for frontend
  - Docker containerization

### Frontend (React + Bootstrap)
- **Location**: `/frontend`
- **Port**: 3000 (Vite dev server on 5173 initially, configured for 3000)
- **Features**:
  - React 19 with Vite
  - Bootstrap 5 UI framework
  - React Router for navigation
  - Axios for API calls
  - JWT token management
  - Protected routes

## Quick Start

### 1. Start Backend (Docker)

```bash
cd c:\Backend\gym-app
docker compose up -d --build
docker compose exec web python manage.py migrate
```

Backend API: http://localhost:8000

### 2. Start Frontend

```bash
cd c:\Backend\gym-app\frontend
npm install
npm run dev
```

Frontend App: http://localhost:3000 (or 5173)

## API Endpoints

### Authentication
- **POST** `/api/auth/register/` - User registration
- **POST** `/api/auth/login/` - User login  
- **POST** `/api/auth/token/refresh/` - Refresh access token

All endpoints return JWT tokens (access & refresh) on success.

## Frontend Routes

- `/` - Redirects to login
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Protected dashboard (requires authentication)

## Authentication Flow

1. **Register/Login**: User enters email and password
2. **Token Storage**: JWT tokens stored in localStorage
   - `access_token` - Valid for 60 minutes
   - `refresh_token` - Valid for 7 days
3. **Protected Routes**: PrivateRoute component checks authentication
4. **API Requests**: Access token sent in Authorization header
5. **Token Refresh**: Automatic refresh when access token expires
6. **Logout**: Clear tokens from localStorage

## Project Structure

```
gym-app/
├── backend/
│   ├── accounts/              # Authentication app
│   │   ├── models.py         # Custom User model
│   │   ├── serializers.py    # API serializers
│   │   ├── views.py          # API views
│   │   ├── urls.py           # URL routing
│   │   └── backends.py       # Email authentication backend
│   ├── django_project/        # Project settings
│   │   └── settings.py       # Django configuration
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   └── PrivateRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # Authentication state management
│   │   ├── services/
│   │   │   └── authService.js    # API service
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── API_DOCUMENTATION.md
```

## Technologies

### Backend
- Django 6.0
- Django REST Framework
- djangorestframework-simplejwt
- PostgreSQL 14
- Django CORS Headers
- Docker

### Frontend
- React 19
- Vite
- React Router DOM 6
- Bootstrap 5
- Bootstrap Icons
- Axios

## Development

### Backend Commands

```bash
# Start containers
docker compose up -d

# View logs
docker compose logs -f web

# Run migrations
docker compose exec web python manage.py migrate

# Create superuser
docker compose exec web python manage.py createsuperuser

# Stop containers
docker compose down
```

### Frontend Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing the Application

1. Start both backend and frontend
2. Open http://localhost:3000 (or 5173)
3. Register a new account
4. Login with credentials
5. Access protected dashboard
6. Logout to clear session

## Security Features

- CSRF protection disabled for API (using JWT tokens)
- CORS configured for specific origins
- Password validation (Django validators)
- JWT token expiration
- Secure password hashing (Django default)
- Email-based authentication (no usernames)

## Next Steps

- Add password reset functionality
- Implement email verification
- Add user profile management
- Create workout tracking features
- Add gym schedule booking
- Implement progress tracking
- Add social features (friends, groups)
- Deploy to production

## Git Repository

GitHub: https://github.com/Khandurian/befit-gym
Branch: mateo
