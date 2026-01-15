# Authentication API Documentation

Your Django REST API with JWT authentication is now ready! 

## API Endpoints

### 1. User Registration
**POST** `/api/auth/register/`

Request body:
```json
{
    "email": "user@example.com",
    "password": "securePassword123",
    "password2": "securePassword123"
}
```

Response (201 Created):
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "date_joined": "2026-01-15T00:00:00Z"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "User registered successfully"
}
```

### 2. User Login
**POST** `/api/auth/login/`

Request body:
```json
{
    "email": "user@example.com",
    "password": "securePassword123"
}
```

email : user@example.com
password : passwd123


Response (200 OK):
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "date_joined": "2026-01-15T00:00:00Z"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "message": "Login successful"
}
```

### 3. Token Refresh
**POST** `/api/auth/token/refresh/`

Request body:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Response (200 OK):
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## JWT Configuration

- **Access Token Lifetime**: 60 minutes
- **Refresh Token Lifetime**: 7 days
- **Token Type**: Bearer

## Using the Access Token

Include the access token in the Authorization header for protected endpoints:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Docker Commands

- **Start containers**: `docker compose up -d`
- **Stop containers**: `docker compose down`
- **View logs**: `docker compose logs web`
- **Run migrations**: `docker compose exec web python manage.py migrate`
- **Create superuser**: `docker compose exec web python manage.py createsuperuser`

## Testing with curl

### Register:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","password2":"testpass123"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### Access Protected Endpoint:
```bash
curl -X GET http://localhost:8000/api/protected-endpoint/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Django Admin

Access Django admin at: http://localhost:8000/admin/

The custom User model uses email as the username field.
