# Unit Tests - Befit Gym

## Tests Implementados

Se han creado 15 tests unitarios para verificar la funcionalidad del sistema de autenticación:

### 1. Tests del Modelo User (5 tests)

- `test_create_user` - Verifica la creación correcta de un usuario
- `test_create_user_without_email` - Valida que el email es obligatorio
- `test_create_superuser` - Verifica la creación de superusuarios
- `test_user_str_representation` - Comprueba la representación string del usuario
- `test_email_normalization` - Valida la normalización del email

### 2. Tests del API de Registro (7 tests)

- `test_user_registration_success` - Registro exitoso de usuario
- `test_user_registration_password_mismatch` - Error cuando las contraseñas no coinciden
- `test_user_registration_duplicate_email` - Error al registrar email duplicado
- `test_user_registration_invalid_email` - Error con formato de email inválido
- `test_user_registration_weak_password` - Error con contraseña débil
- `test_user_registration_missing_fields` - Error cuando faltan campos requeridos
- Verifica que el usuario se guarda correctamente en la base de datos

### 3. Tests del API de Login (4 tests)

- `test_user_login_success` - Login exitoso
- `test_user_login_invalid_credentials` - Error con credenciales incorrectas
- `test_user_login_nonexistent_user` - Error con usuario inexistente
- `test_user_login_inactive_user` - Error con usuario inactivo

## Ejecutar los Tests

### Dentro del contenedor Docker:

```bash
# Ejecutar todos los tests de la app accounts
docker compose exec web python manage.py test accounts

# Ejecutar un test específico
docker compose exec web python manage.py test accounts.tests.UserModelTest

# Ejecutar con más detalle (verbose)
docker compose exec web python manage.py test accounts --verbosity=2

# Ejecutar test mock del generador de rutinas (determinista)
docker compose exec web python manage.py test accounts.tests_routine_generator --verbosity=2

# Smoke test IA en modo mock (sin depender de cuota Gemini)
docker-compose exec -T web python manage.py shell < backend/test_ia.py

# Smoke test IA en modo live (usa Gemini real)
docker-compose exec -T web env TEST_IA_MODE=live python manage.py shell < backend/test_ia.py
```

### Tests con cobertura:

```bash
# Instalar coverage
docker compose exec web pip install coverage

# Ejecutar tests con cobertura
docker compose exec web coverage run --source='accounts' manage.py test accounts

# Ver reporte de cobertura
docker compose exec web coverage report

# Generar reporte HTML
docker compose exec web coverage html
```

## Resultados

✅ **15/15 tests pasaron exitosamente**

```
Found 15 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
...............
----------------------------------------------------------------------
Ran 15 tests in 12.960s

OK
Destroying test database for alias 'default'...
```

## Cobertura de Tests

Los tests cubren:
- ✅ Creación de usuarios en la base de datos
- ✅ Validaciones del modelo User
- ✅ Endpoints de API (registro y login)
- ✅ Autenticación con JWT tokens
- ✅ Validación de contraseñas
- ✅ Manejo de errores
- ✅ Casos edge (emails duplicados, usuarios inactivos, etc.)

## Estructura del Archivo de Tests

```python
accounts/tests.py
├── UserModelTest
│   ├── Pruebas del modelo User personalizado
│   └── Validaciones de creación de usuarios
├── UserRegistrationAPITest
│   ├── Pruebas del endpoint de registro
│   └── Validaciones de datos de entrada
└── UserLoginAPITest
    ├── Pruebas del endpoint de login
    └── Validaciones de autenticación
```

## Comandos Útiles

```bash
# Crear base de datos de prueba manualmente
docker compose exec web python manage.py test --keepdb

# Ejecutar solo tests que fallaron
docker compose exec web python manage.py test --failfast

# Ejecutar tests en paralelo
docker compose exec web python manage.py test --parallel
```

## Próximos Tests a Implementar

- [ ] Tests para el refresh token endpoint
- [ ] Tests de integración frontend-backend
- [ ] Tests de rendimiento
- [ ] Tests de seguridad (SQL injection, XSS, etc.)
- [ ] Tests de email verification (cuando se implemente)
- [ ] Tests de password reset (cuando se implemente)
