# EquipmentSelector Component - Documentación

Componente React interactivo para seleccionar equipamiento de gimnasio con interfaz moderna Dark Mode y Verde Lima.

## Características

✨ **Interfaz Moderna**
- Dark Mode con acentos Verde Lima
- Cards seleccionables con efecto hover y transiciones suaves
- Diseño responsive (2 cols móvil, 4-5 desktop)
- Iconos de lucide-react por categoría

🎯 **Funcionalidades**
- Selección individual o por lotes (categorías)
- Expansión/contracción de categorías
- Panel sticky inferior con resumen de selección
- Barra de progreso por categoría
- Contador total de equipamientos seleccionados

📱 **Responsive**
- Mobile: grid de 1-2 columnas
- Tablet: grid de 2-3 columnas
- Desktop: grid de 4-5 columnas

## Instalación

### 1. Requisitos previos

El componente depende de:
- React 19+
- Tailwind CSS 3+
- lucide-react (ya incluido en package.json)

```bash
npm install lucide-react
```

### 2. Estructura de carpetas

```
frontend/
├── src/
│   ├── components/
│   │   ├── EquipmentSelector.jsx  ← Componente principal
│   │   └── EquipmentPage.jsx      ← Página de ejemplo
│   └── services/
│       └── equipmentService.js    ← Servicio de API
```

## Uso

### Opción 1: Uso Directo del Componente

```jsx
import { useState, useEffect } from 'react';
import EquipmentSelector from './components/EquipmentSelector';
import equipmentService from './services/equipmentService';

function MyPage() {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadEquipment();
  }, []);

  const loadEquipment = async () => {
    try {
      const data = await equipmentService.getAllEquipment();
      setEquipment(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (selectedIds) => {
    try {
      await equipmentService.saveEquipmentSelection(selectedIds);
      alert('¡Equipamiento guardado!');
    } catch (error) {
      console.error('Error guardando:', error);
    }
  };

  return (
    <EquipmentSelector
      equipmentList={equipment}
      onSave={handleSave}
      loading={loading}
    />
  );
}
```

### Opción 2: Uso de EquipmentPage (Completo)

```jsx
import EquipmentPage from './components/EquipmentPage';

function App() {
  return <EquipmentPage />;
}
```

## Props del Componente

```typescript
interface EquipmentSelectorProps {
  equipmentList: Array<{
    id: number;
    nombre: string;
    categoria: 'PESO_LIBRE' | 'MAQUINA' | 'CARDIO' | 'ACCESORIO' | 'CALISTENIA';
  }>;
  
  onSave: (selectedIds: number[]) => void | Promise<void>;
  
  initialSelected?: number[];  // IDs preseleccionados
  
  loading?: boolean;  // Estado de carga
}
```

## API Endpoints

El servicio `equipmentService` proporciona métodos para:

### Obtener Equipamiento

```javascript
// Todos los equipamientos
const all = await equipmentService.getAllEquipment();

// Filtrado por categoría
const cardio = await equipmentService.getEquipmentByCategory('CARDIO');

// Equipamiento específico
const item = await equipmentService.getEquipmentById(1);
```

### Guardar Selección

```javascript
// Guardar IDs seleccionados
await equipmentService.saveEquipmentSelection([1, 2, 3, 5, 7]);

// Obtener selección guardada del usuario
const saved = await equipmentService.getUserEquipmentSelection();
```

## Personalización

### Colores

Los colores se definen en `categoryConfig` dentro del componente:

```javascript
const categoryConfig = {
  PESO_LIBRE: {
    icon: Dumbbell,
    label: 'Peso Libre',
    bgColor: 'bg-orange-900/20',
    borderColor: 'border-orange-700',
    textColor: 'text-orange-300',
  },
  // ... más categorías
};
```

### Iconos

Cambiar iconos de lucide-react:

```javascript
import { Trophy, Zap, Flame } from 'lucide-react';

const categoryConfig = {
  CARDIO: {
    icon: Flame,  // Cambiar icono
    // ...
  },
};
```

### Estilos Tailwind

Modificar efectos hover, colores, tamaños:

```jsx
<button
  onClick={() => toggleEquipment(item.id)}
  className={`
    // Cambiar escala de hover
    hover:scale-110  // De 105 a 110
    
    // Cambiar colores de selección
    ${isSelected
      ? 'bg-yellow-400/10 border-yellow-400'  // Cambiar color
      : 'bg-gray-900/50 border-gray-700'
    }
  `}
>
```

## Manejo de Errores

El componente maneja automáticamente:

- Estado de carga (spinner)
- Lista vacía (mensaje informativo)
- Errores de API (mediante try-catch en servicios)

Para agregar manejo custom:

```jsx
const [error, setError] = useState(null);

const handleSave = async (selectedIds) => {
  try {
    await equipmentService.saveEquipmentSelection(selectedIds);
  } catch (error) {
    setError(error.message);
    // mostrar toast o notificación
  }
};
```

## Integración con Backend

### Configuración en Django

1. El ViewSet ya está configurado en `accounts/views.py`:

```python
class EquipamientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipamiento.objects.all().order_by("nombre")
    serializer_class = EquipamientoSerializer
    permission_classes = [IsAuthenticated]
```

2. Endpoints disponibles:
   - `GET /api/auth/equipamientos/` - Listar todos
   - `GET /api/auth/equipamientos/?categoria=PESO_LIBRE` - Filtrar
   - `GET /api/auth/equipamientos/{id}/` - Detalle

3. Para crear endpoint de guardar preferencias de usuario, agregar modelo en Django:

```python
class UserEquipmentPreference(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    equipamientos = models.ManyToManyField(Equipamiento)
```

## Troubleshooting

**Problema**: Componente no carga equipamiento
- Verificar token JWT en localStorage
- Validar que endpoint retorna datos válidos

**Problema**: Colores no se aplican
- Asegurar que Tailwind CSS está configurado correctamente
- Verificar que `tailwind.config.js` incluya la carpeta `src/`

**Problema**: Iconos no se muestran
- Instalar lucide-react: `npm install lucide-react`
- Verificar que los nombres de iconos sean correctos

## Rendimiento

- ✅ Uso de `useState` para estado local
- ✅ `useEffect` sin dependencias innecesarias
- ✅ Manejo de paginación en backend automático
- ✅ Prefetch de datos en API

## Seguridad

- ✅ Autenticación JWT requerida
- ✅ CORS configurado
- ✅ Validación de token en localStorage
- ✅ Headers de autorización seguros

## Ejemplos de Respuesta API

```json
{
  "results": [
    {
      "id": 1,
      "nombre": "Barra Olímpica",
      "categoria": "PESO_LIBRE",
      "categoria_display": "Peso Libre"
    },
    {
      "id": 16,
      "nombre": "Cinta de Correr",
      "categoria": "CARDIO",
      "categoria_display": "Cardio"
    }
  ],
  "count": 32,
  "next": "http://localhost:8000/api/auth/equipamientos/?page=2",
  "previous": null
}
```

## Notas Técnicas

- El componente usa `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` para responsive
- Panel sticky usa `fixed bottom-0` con `max-w-7xl mx-auto`
- Animaciones use `transition-all duration-200` para suavidad
- Checkmarks aparecen con `absolute top-2 right-2`

## Licencia

Este componente es parte del proyecto Befit Gym.
