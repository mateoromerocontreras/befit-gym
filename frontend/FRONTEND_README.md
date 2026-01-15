# Befit Gym - React Frontend

React frontend application with Bootstrap for the Befit Gym authentication system.

## Features

- User Registration
- User Login
- JWT Token Authentication
- Protected Dashboard
- Bootstrap UI Components
- Responsive Design

## Technologies

- React 19
- Vite
- React Router DOM
- Bootstrap 5
- Axios
- Bootstrap Icons

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The frontend will run on http://localhost:3000

## Backend API

Make sure the Django backend is running on http://localhost:8000

## Available Routes

- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Protected dashboard (requires authentication)

## Project Structure

```
src/
├── components/
│   ├── Login.jsx          # Login component
│   ├── Register.jsx       # Registration component
│   ├── Dashboard.jsx      # Protected dashboard
│   └── PrivateRoute.jsx   # Route protection wrapper
├── context/
│   └── AuthContext.jsx    # Authentication context provider
├── services/
│   └── authService.js     # API service for authentication
├── App.jsx                # Main app component with routing
└── main.jsx               # Entry point
```

## Authentication Flow

1. User registers or logs in
2. JWT tokens (access & refresh) are stored in localStorage
3. Access token is used for authenticated requests
4. Refresh token is used to get new access tokens
5. User can logout to clear tokens

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` folder.
