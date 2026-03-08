# 🎬 GUÍA DE INTEGRACIÓN PASO A PASO - EquipmentSelector

## Inicio Rápido (5 minutos)

### Paso 1: Verificar Dependencias

```bash
cd frontend
npm list lucide-react  # Debe estar instalado
npm list tailwindcss   # Debe estar instalado
```

✅ Si faltan: `npm install lucide-react tailwindcss`

### Paso 2: Verificar Backend

```bash
# Verificar que el endpoint funciona
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/equipamientos/
```

Debe retornar JSON con array de equipamientos.

### Paso 3: Acceder al Componente

1. Inicia el frontend: `npm run dev`
2. Inicia el backend: `docker compose up`
3. Navega a: `http://localhost:3000/equipment`

✅ Deberías ver el componente cargado.

---

## Integración en Componente Existente

### Opción A: En Dashboard

```jsx
// frontend/src/components/Dashboard.jsx

import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export default function Dashboard() {
  const { user } = useAuth();
  const [equipment, setEquipment] = useState([]);

  useEffect(() => {
    equipmentService.getAllEquipment()
      .then(setEquipment)
      .catch(err => console.error('Error:', err));
  }, []);

  const handleEquipmentSave = async (selectedIds) => {
    try {
      await equipmentService.saveEquipmentSelection(selectedIds);
      alert('Equipamiento guardado');
    } catch (error) {
      alert('Error al guardar');
    }
  };

  return (
    <div>
      {/* Contenido existente del dashboard */}
      
      {/* Nuevo: Equipment Selector */}
      <section className="mt-8">
        <EquipmentSelector
          equipmentList={equipment}
          onSave={handleEquipmentSave}
        />
      </section>
    </div>
  );
}
```

### Opción B: En Tab/Modal Separado

```jsx
// frontend/src/components/SettingsPage.jsx

import { useState } from 'react';
import EquipmentSelector from './EquipmentSelector';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general');

  return (
    <div>
      <div className="tabs">
        <button onClick={() => setActiveTab('general')}>General</button>
        <button onClick={() => setActiveTab('equipment')}>Equipamiento</button>
      </div>

      {activeTab === 'equipment' && (
        <EquipmentSelector
          equipmentList={equipment}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
```

### Opción C: En Formulario de Rutina

```jsx
// frontend/src/components/CreateRoutineForm.jsx

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export default function CreateRoutineForm() {
  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    equipamientos: []
  });

  const [equipment, setEquipment] = useState([]);

  useEffect(() => {
    equipmentService.getAllEquipment().then(setEquipment);
  }, []);

  const handleEquipmentSelect = (equipmentIds) => {
    setFormData(prev => ({
      ...prev,
      equipamientos: equipmentIds
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Enviar formulario con equipamientos seleccionados
    const response = await fetch('/api/rutinas/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(formData)
    });
    
    console.log('Rutina creada con equipamientos:', formData.equipamientos);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={formData.nombre}
        onChange={(e) => setFormData(p => ({ ...p, nombre: e.target.value }))}
        placeholder="Nombre de la rutina"
      />

      <h3>Selecciona Equipamiento</h3>
      <EquipmentSelector
        equipmentList={equipment}
        initialSelected={formData.equipamientos}
        onSave={handleEquipmentSelect}
      />

      <button type="submit">Crear Rutina</button>
    </form>
  );
}
```

---

## Personalización

### 1. Cambiar Colores Verde Lima a Otro Color

En `EquipmentSelector.jsx`:

```jsx
// Buscar y reemplazar:
// bg-accent-lime → bg-Tu_COLOR (ej: bg-blue-500)
// text-accent-lime → text-TU_COLOR

// Cambiar clase Tailwind:
className={`
  ...
  ${isSelected
    ? 'bg-BLUE-500/10 border-BLUE-500 shadow-lg shadow-BLUE-500/20'
    : 'bg-gray-900/50 border-gray-700'
  }
`}
```

### 2. Agregar Búsqueda

```jsx
// En el componente padre
import { useState, useMemo } from 'react';

export function EquipmentWithSearch() {
  const [search, setSearch] = useState('');
  const [equipment, setEquipment] = useState([]);

  const filtered = useMemo(() => {
    return equipment.filter(e =>
      e.nombre.toLowerCase().includes(search.toLowerCase())
    );
  }, [equipment, search]);

  return (
    <>
      <input
        type="text"
        placeholder="Buscar equipamiento..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full p-2 bg-gray-800 text-white rounded mb-4"
      />
      <EquipmentSelector equipmentList={filtered} onSave={handleSave} />
    </>
  );
}
```

### 3. Agregar Categorías Customizadas

```jsx
// En EquipmentSelector.jsx - Modificar categoryConfig:

const categoryConfig = {
  NUEVO_TIPO: {
    icon: MyCustomIcon,
    label: 'Mi Tipo',
    bgColor: 'bg-pink-900/20',
    borderColor: 'border-pink-700',
    textColor: 'text-pink-300',
  },
  // ...
};
```

### 4. Hacer el Panel Sticky No-Sticky

```jsx
// En EquipmentSelector.jsx - Cambiar:
<div className="fixed bottom-0 left-0 right-0 ...">
// A:
<div className="sticky bottom-0 mt-8 ...">
```

---

## Manejo de Errores

### Con Try-Catch

```jsx
const handleSave = async (selectedIds) => {
  try {
    await equipmentService.saveEquipmentSelection(selectedIds);
    setMessage({ type: 'success', text: 'Guardado' });
  } catch (error) {
    if (error.response?.status === 401) {
      // Token expirado
      redirectToLogin();
    } else if (error.response?.status === 400) {
      // Datos inválidos
      setMessage({ type: 'error', text: 'Datos inválidos' });
    } else {
      // Error genérico
      setMessage({ type: 'error', text: 'Error inesperado' });
    }
  }
};
```

### Con Toast/Notificación

```jsx
import { toast } from 'react-toastify';  // Si lo usas

const handleSave = async (selectedIds) => {
  try {
    await equipmentService.saveEquipmentSelection(selectedIds);
    toast.success(`${selectedIds.length} equipos guardados`);
  } catch (error) {
    toast.error('Error al guardar equipamiento');
  }
};
```

---

## Testing

### Test Unitario Básico

```jsx
// frontend/src/components/__tests__/EquipmentSelector.test.jsx

import { render, screen, fireEvent } from '@testing-library/react';
import EquipmentSelector from '../EquipmentSelector';

describe('EquipmentSelector', () => {
  const mockEquipment = [
    { id: 1, nombre: 'Barra', categoria: 'PESO_LIBRE' },
    { id: 2, nombre: 'Cinta', categoria: 'CARDIO' }
  ];

  it('renders equipment list', () => {
    render(
      <EquipmentSelector equipmentList={mockEquipment} onSave={jest.fn()} />
    );
    expect(screen.getByText('Barra')).toBeInTheDocument();
    expect(screen.getByText('Cinta')).toBeInTheDocument();
  });

  it('calls onSave when button clicked', () => {
    const onSave = jest.fn();
    render(
      <EquipmentSelector equipmentList={mockEquipment} onSave={onSave} />
    );
    // Seleccionar un equipamiento
    fireEvent.click(screen.getByText('Barra'));
    // Guardar
    fireEvent.click(screen.getByText('Guardar Configuración'));
    expect(onSave).toHaveBeenCalledWith([1]);
  });
});
```

---

## Performance

### Optimizaciones Implementadas

✅ `useMemo` para cálculos de categorías  
✅ `useCallback` para funciones toggle  
✅ Prefetch de datos en servicios  
✅ Paginación en backend  

### Para Listas Grandes (> 1000 items)

```jsx
// Usar react-virtual para virtualización
import { FixedSizeList } from 'react-window';

// O implementar lazy loading:
const loadMore = () => {
  setPage(p => p + 1);
  equipmentService.getAllEquipment(page + 1)
    .then(newData => setEquipment(p => [...p, ...newData]));
};
```

---

## Deployement

### Producción Frontend

```bash
# Build
npm run build

# Output en dist/
# Servir con nginx, vercel, netlify, etc.
```

### Producción Backend

```bash
# Verificar collectstatic
docker compose exec web python manage.py collectstatic --noinput

# Ejecutar en producción
docker compose -f docker-compose.prod.yml up -d
```

---

## Solución de Problemas

### Problema: "Módulo no encontrado"

```
Error: Cannot find module './EquipmentSelector'
```

✅ Verificar ruta relativa es correcta  
✅ Verificar archivo existe  
✅ Verificar extensión `.jsx`

### Problema: Componente No Carga Datos

```
El selector aparece pero sin equipamientos
```

✅ Verificar token JWT en localStorage  
✅ Verificar endpoint en `equipmentService.js`  
✅ Abrir console y revisar errores (F12)

### Problema: Estilos Tailwind No Aplican

```
Colores no se ven correctamente
```

✅ Verificar `tailwind.config.js` incluye `src/`  
✅ Ejecutar `npm run build` (rebuild)  
✅ Limpiar cache del navegador (Ctrl+Shift+Del)

### Problema: Botón Guardar No Funciona

```
Selecciono pero guardar no hace nada
```

✅ Verificar `onSave` prop está pasada  
✅ Verificar `equipmentService.saveEquipmentSelection()` existe  
✅ Revisar network tab (F12) para ver requests

---

## Checklist de Integración

- [ ] Frontend correctamente cargado en http://localhost:3000
- [ ] Backend corriendo en http://localhost:8000
- [ ] JWT token funciona correctamente
- [ ] Endpoint `/api/auth/equipamientos/` responde
- [ ] Componente renderiza sin errores
- [ ] Selecciones funcionan
- [ ] Botón guardar funciona
- [ ] Respuestas del servidor se guardan
- [ ] Estilos Tailwind se aplican correctamente
- [ ] Responsivo en mobile/tablet/desktop

---

## Soporte y Debugging

### Logs Útiles

```javascript
// En equipmentService.js
console.log('Token:', localStorage.getItem('access_token'));
console.log('Request:', { equipment, headers });
console.log('Response:', data);

// En EquipmentSelector.jsx
console.log('Selected:', selected);
console.log('Expanded:', expandedCategories);
```

### Browser DevTools

1. **Console** (F12): Ver errores JavaScript
2. **Network**: Ver requests/responses API
3. **Elements**: Inspeccionar HTML y Tailwind classes
4. **Storage**: Verificar localStorage (token)

---

## Próximos Features

1. **Buscar**: Agregar barra de búsqueda
2. **Filtros**: Por precio, dificultad, etc.
3. **Favoritos**: Guardar configuraciones
4. **Historial**: Ver selecciones anteriores
5. **Exportar**: Descargar configuración como PDF

---

**¡Listo para integrar!** 🚀
