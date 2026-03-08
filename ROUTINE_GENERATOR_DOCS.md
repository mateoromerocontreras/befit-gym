# Documentación: Servicio de Generación de Rutinas con IA

## 🚀 Descripción General

El servicio `RoutineGeneratorService` utiliza **Gemini AI** de Google para generar planes de entrenamiento personalizados basados en:

- Perfil del usuario (objetivo, nivel, edad)
- Equipamiento disponible (selección previa del usuario)
- Número de días de entrenamiento deseados

---

## 📋 Requisitos Previos

### 1. Obtener API Key de Gemini

1. Visita: https://makersuite.google.com/app/apikey
2. Crea un nuevo proyecto (si no tienes uno)
3. Genera una API key
4. Copia la clave generada

### 2. Configurar Variable de Entorno

**Opción A: Archivo `.env` (Docker)**

```bash
# En c:\Backend\gym-app\.env
GEMINI_API_KEY=tu_api_key_aqui
```

**Opción B: Variable de sistema (local)**

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="tu_api_key_aqui"

# Linux/Mac
export GEMINI_API_KEY="tu_api_key_aqui"
```

### 3. Instalar Dependencias

```bash
cd c:\Backend\gym-app
docker compose exec web pip install -r requirements.txt
```

---

## 🔧 Estructura del Servicio

### Archivo Principal

**Ubicación:** `backend/accounts/services/routine_generator.py`

### Componentes Clave

1. **`RoutineGeneratorService`**: Clase principal del servicio
2. **`generate_routine()`**: Función helper para uso rápido
3. **`GenerateRoutineView`**: Endpoint API REST

---

## 🎯 Uso del Servicio

### Opción 1: Via API REST (Recomendado)

**Endpoint:** `POST /api/auth/generate-routine/`

**Headers:**
```json
{
  "Authorization": "Bearer <JWT_TOKEN>",
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "dias_semana": 3,
  "nombre_rutina": "Plan de Fuerza"
}
```

**Respuesta Exitosa (201):**
```json
{
  "success": true,
  "rutina_id": 42,
  "plan_ids": [101, 102, 103],
  "mensaje": "Rutina generada exitosamente para 3 días",
  "ejercicios_count": 12
}
```

**Respuesta Error (400):**
```json
{
  "error": "Usuario test@example.com no tiene equipamiento configurado. Debe seleccionar equipamiento disponible primero."
}
```

### Opción 2: Uso Programático

```python
from accounts.services.routine_generator import generate_routine

# Generar rutina para usuario ID 5
resultado = generate_routine(
    user_id=5,
    dias_semana=4,
    nombre_rutina="Mi Plan Personalizado"
)

if resultado['success']:
    print(f"Rutina creada con ID: {resultado['rutina_id']}")
    print(f"Total ejercicios: {resultado['ejercicios_count']}")
else:
    print(f"Error: {resultado['error']}")
```

### Opción 3: Uso Directo de la Clase

```python
from accounts.services.routine_generator import RoutineGeneratorService

service = RoutineGeneratorService()
resultado = service.generate_routine_for_user(
    user_id=3,
    dias_semana=5,
    nombre_rutina="Plan Avanzado"
)
```

---

## 🧪 Testing Manual

### 1. Preparar Usuario

```python
# Django Shell
python manage.py shell

from accounts.models import User, Equipamiento

user = User.objects.get(email='test@example.com')
user.edad = 30
user.objetivo = 'GANAR_MASA'
user.nivel = 'INTERMEDIO'
user.save()

# Asignar equipamiento
equipos = Equipamiento.objects.filter(categoria='PESO_LIBRE')[:5]
user.equipamientos_preferidos.set(equipos)
```

### 2. Probar Endpoint con cURL

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  | jq -r '.access')

# Generar rutina
curl -X POST http://localhost:8000/api/auth/generate-routine/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"dias_semana": 3, "nombre_rutina": "Plan IA Test"}' \
  | jq .
```

### 3. Probar con Python

```python
import requests

# Login
login_resp = requests.post('http://localhost:8000/api/auth/login/', json={
    'email': 'test@example.com',
    'password': 'SecurePass123!'
})
token = login_resp.json()['access']

# Generar rutina
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8000/api/auth/generate-routine/',
    json={'dias_semana': 4, 'nombre_rutina': 'Mi Plan IA'},
    headers=headers
)

print(response.json())
```

---

## 📊 Flujo de Datos

```
1. Usuario hace POST a /api/auth/generate-routine/
   ↓
2. Se valida JWT y datos de entrada
   ↓
3. RoutineGeneratorService obtiene perfil del usuario
   ↓
4. Filtra ejercicios basados en equipamiento disponible
   ↓
5. Construye prompt optimizado para Gemini AI
   ↓
6. Gemini genera JSON con plan semanal
   ↓
7. Se parsea y valida la respuesta JSON
   ↓
8. Se crean objetos en DB (Rutina, RutinaEjercicio, PlanSemanal)
   ↓
9. Se retorna respuesta con IDs generados
```

---

## 🔍 Estructura del Prompt

El prompt enviado a Gemini incluye:

1. **Rol:** "Eres un entrenador personal certificado..."
2. **Perfil del usuario:** objetivo, nivel, edad, peso, altura
3. **Lista de ejercicios disponibles:** con IDs exactos de la DB
4. **Reglas estrictas:** solo usar IDs proporcionados, distribución balanceada
5. **Ajustes por nivel:** series/reps/descansos según experiencia
6. **Formato JSON requerido:** estructura exacta esperada

**Ejemplo de prompt generado:**

```
Eres un entrenador personal certificado y experto en programación de ejercicios.

**PERFIL DEL USUARIO:**
- Objetivo: ganar masa muscular y volumen
- Nivel de experiencia: Intermedio
- Edad: 30
- Peso: 75.0 kg
- Altura: 1.75 m

**EJERCICIOS DISPONIBLES (EQUIPAMIENTO DEL USUARIO):**
- ID: 1 | Nombre: Press de Banca | Grupo: PECHO | Dificultad: INTERMEDIO
- ID: 5 | Nombre: Sentadilla | Grupo: PIERNAS | Dificultad: INTERMEDIO
...

**TAREA:**
Genera un plan de entrenamiento para 3 días por semana.

**REGLAS ESTRICTAS:**
1. SOLO puedes usar ejercicios de la lista anterior (usando sus IDs exactos)
2. NO inventes nombres nuevos de ejercicios
...

**FORMATO DE RESPUESTA REQUERIDO (JSON válido):**
{
  "plan_semanal": [...]
}
```

---

## 🛡️ Validaciones y Seguridad

### El servicio valida:

- ✅ Usuario existe y está autenticado
- ✅ Usuario tiene equipamiento configurado
- ✅ Respuesta de Gemini es JSON válido
- ✅ JSON contiene estructura requerida
- ✅ IDs de ejercicios existen en la DB
- ✅ Transacciones atómicas (rollback si falla)

### Manejo de errores:

```python
try:
    result = generate_routine(user_id=1, dias_semana=3)
except ValueError as e:
    # Usuario inválido, sin equipamiento, etc.
    print(f"Error de validación: {e}")
except Exception as e:
    # Error de API de Gemini, JSON inválido, etc.
    print(f"Error del servicio: {e}")
```

---

## 🎨 Ejemplo de Respuesta de Gemini

```json
{
  "plan_semanal": [
    {
      "dia": 1,
      "nombre_dia": "Día 1 - Pecho y Tríceps",
      "ejercicios": [
        {
          "ejercicio_id": 1,
          "series": 4,
          "repeticiones": "10",
          "descanso_segundos": 60,
          "orden": 1,
          "notas": "Controla la bajada, explosivo al subir"
        },
        {
          "ejercicio_id": 8,
          "series": 3,
          "repeticiones": "12",
          "descanso_segundos": 45,
          "orden": 2,
          "notas": "Mantén codos cerca del cuerpo"
        }
      ]
    }
  ],
  "duracion_estimada_minutos": 50,
  "nivel_recomendado": "INTERMEDIO",
  "observaciones": "Prioriza la técnica sobre el peso. Descansa 48h entre sesiones del mismo grupo muscular."
}
```

---

## 🚨 Troubleshooting

### Error: "GEMINI_API_KEY no configurada"

**Solución:**
```bash
# Agregar a .env
echo "GEMINI_API_KEY=tu_clave_aqui" >> .env

# Reiniciar Docker
docker compose restart web
```

### Error: "Usuario no tiene equipamiento configurado"

**Solución:**
```python
# Asignar equipamiento primero
POST /api/auth/user-equipment/
{
  "equipamientos": [1, 2, 3, 4, 5]
}
```

### Error: "Request failed with status code 429"

**Causa:** Límite de rate de Gemini API excedido

**Solución:**
- Espera 1 minuto
- Considera usar caching
- Implementa retry con backoff exponencial

### Error: "Respuesta de IA no es JSON válido"

**Causa:** Gemini devolvió texto en vez de JSON puro

**Solución:** El servicio ya limpia markdown (```json), pero si persiste:
```python
# El servicio maneja esto automáticamente
# Si falla, revisa logs de Django para ver respuesta raw
```

---

## 📈 Optimizaciones Futuras

1. **Caching de respuestas:** Evitar regenerar para mismos parámetros
2. **Retry automático:** Si Gemini falla, reintentar con backoff
3. **Validación de ejercicios:** Verificar que combinaciones sean lógicas
4. **Múltiples proveedores:** Fallback a OpenAI si Gemini falla
5. **Feedback loop:** Permitir al usuario calificar planes generados

---

## 📚 Referencias

- **Gemini API Docs:** https://ai.google.dev/docs
- **Django Services Pattern:** https://docs.djangoproject.com/en/6.0/
- **Prompt Engineering:** https://ai.google.dev/docs/prompt_best_practices

---

## ✅ Checklist de Implementación

- [x] Modelo User extendido con objetivo, nivel, edad
- [x] Servicio RoutineGeneratorService creado
- [x] Endpoint REST `/api/auth/generate-routine/` implementado
- [x] Serializer GenerateRoutineSerializer agregado
- [x] Integración con Gemini AI configurada
- [x] Validaciones y manejo de errores completo
- [x] Transacciones atómicas para consistencia de datos
- [x] Documentación completa generada
- [ ] Tests unitarios para el servicio (pendiente)
- [ ] Migración aplicada para nuevos campos de User
- [ ] API Key de Gemini configurada en producción
