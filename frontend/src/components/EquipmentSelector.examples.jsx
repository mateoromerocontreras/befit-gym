// ============================================================================
// EQUIPMENT SELECTOR - EJEMPLOS DE USO AVANZADO
// ============================================================================

// ============================================================================
// 1. INTEGRACIÓN BÁSICA EN UN COMPONENTE EXISTENTE
// ============================================================================

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function BasicUsage() {
    const [equipment, setEquipment] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        setLoading(true);
        equipmentService.getAllEquipment()
            .then(setEquipment)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const handleSave = async (selectedIds) => {
        try {
            await equipmentService.saveEquipmentSelection(selectedIds);
            alert('Equipamiento guardado');
        } catch (error) {
            alert('Error guardando equipamiento');
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

// ============================================================================
// 2. CON GESTIÓN DE ERRORES Y TOASTS
// ============================================================================

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';
import Toast from './Toast'; // Tu componente de toast

export function WithErrorHandling() {
    const [equipment, setEquipment] = useState([]);
    const [loading, setLoading] = useState(true);
    const [toast, setToast] = useState(null);
    const [userSelected, setUserSelected] = useState([]);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            const data = await equipmentService.getAllEquipment();
            setEquipment(data);

            const saved = await equipmentService.getUserEquipmentSelection();
            setUserSelected(saved);
        } catch (error) {
            showToast('Error cargando equipamiento', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async (selectedIds) => {
        try {
            await equipmentService.saveEquipmentSelection(selectedIds);
            setUserSelected(selectedIds);
            showToast(`${selectedIds.length} equipos guardados`, 'success');
        } catch (error) {
            showToast('Error al guardar', 'error');
        }
    };

    const showToast = (message, type) => {
        setToast({ message, type });
        setTimeout(() => setToast(null), 3000);
    };

    return (
        <>
            {toast && <Toast {...toast} />}
            <EquipmentSelector
                equipmentList={equipment}
                onSave={handleSave}
                initialSelected={userSelected}
                loading={loading}
            />
        </>
    );
}

// ============================================================================
// 3. FILTRADO POR CATEGORÍA
// ============================================================================

import { useState } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function FilteredByCategory() {
    const [equipment, setEquipment] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('PESO_LIBRE');

    useEffect(() => {
        equipmentService.getEquipmentByCategory(selectedCategory)
            .then(setEquipment)
            .catch(console.error);
    }, [selectedCategory]);

    return (
        <div>
            <div className="mb-4 flex gap-2">
                {['PESO_LIBRE', 'MAQUINA', 'CARDIO', 'ACCESORIO', 'CALISTENIA'].map(cat => (
                    <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={selectedCategory === cat ? 'active' : ''}
                    >
                        {equipmentService.getCategoryLabel(cat)}
                    </button>
                ))}
            </div>
            <EquipmentSelector
                equipmentList={equipment}
                onSave={(ids) => console.log('Selected:', ids)}
            />
        </div>
    );
}

// ============================================================================
// 4. INTEGRACIÓN CON FORMULARIO MÁS GRANDE
// ============================================================================

import { useState } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function WithinLargerForm() {
    const [formData, setFormData] = useState({
        nombre: '',
        descripcion: '',
        equipamientos: []
    });

    const handleEquipmentSave = (selectedIds) => {
        setFormData(prev => ({
            ...prev,
            equipamientos: selectedIds
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Enviar todo el formulario
            const response = await fetch('/api/something', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(formData)
            });
            console.log('Form submitted with equipment:', formData.equipamientos);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={formData.nombre}
                onChange={(e) => setFormData(prev => ({
                    ...prev,
                    nombre: e.target.value
                }))}
                placeholder="Nombre"
            />

            <textarea
                value={formData.descripcion}
                onChange={(e) => setFormData(prev => ({
                    ...prev,
                    descripcion: e.target.value
                }))}
                placeholder="Descripción"
            />

            <h3>Selecciona Equipamiento</h3>
            <EquipmentSelector
                equipmentList={/* ... */}
                onSave={handleEquipmentSave}
                initialSelected={formData.equipamientos}
            />

            <button type="submit">Guardar</button>
        </form>
    );
}

// ============================================================================
// 5. PRECARGAR SELECCIÓN DEL USUARIO
// ============================================================================

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function WithUserPreferences() {
    const [equipment, setEquipment] = useState([]);
    const [userPreferences, setUserPreferences] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            equipmentService.getAllEquipment(),
            equipmentService.getUserEquipmentSelection()
        ])
            .then(([equip, prefs]) => {
                setEquipment(equip);
                setUserPreferences(prefs);
            })
            .finally(() => setLoading(false));
    }, []);

    return (
        <EquipmentSelector
            equipmentList={equipment}
            initialSelected={userPreferences}
            onSave={async (ids) => {
                await equipmentService.saveEquipmentSelection(ids);
                setUserPreferences(ids);
            }}
            loading={loading}
        />
    );
}

// ============================================================================
// 6. MULTISELECCIÓN CON RECOMENDACIONES
// ============================================================================

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function WithRecommendations() {
    const [equipment, setEquipment] = useState([]);
    const [selected, setSelected] = useState([]);
    const [recommendations, setRecommendations] = useState([]);

    useEffect(() => {
        equipmentService.getAllEquipment().then(setEquipment);
    }, []);

    const handleSelect = (selectedIds) => {
        setSelected(selectedIds);
        // Lógica de recomendación
        const recommended = calculateRecommendations(selectedIds);
        setRecommendations(recommended);
    };

    const calculateRecommendations = (ids) => {
        // Tu lógica aquí
        return equipment
            .filter(e => !ids.includes(e.id))
            .slice(0, 5);
    };

    return (
        <div className="space-y-6">
            <EquipmentSelector
                equipmentList={equipment}
                onSave={handleSelect}
            />

            {recommendations.length > 0 && (
                <div className="bg-blue-900/20 p-4 rounded">
                    <h3>Equipamiento Recomendado</h3>
                    <ul>
                        {recommendations.map(rec => (
                            <li key={rec.id}>{rec.nombre}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// ============================================================================
// 7. CON BÚSQUEDA/FILTRO ADICIONAL
// ============================================================================

import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

export function WithSearch() {
    const [allEquipment, setAllEquipment] = useState([]);
    const [filteredEquipment, setFilteredEquipment] = useState([]);
    const [search, setSearch] = useState('');

    useEffect(() => {
        equipmentService.getAllEquipment().then(setAllEquipment);
    }, []);

    useEffect(() => {
        const filtered = allEquipment.filter(e =>
            e.nombre.toLowerCase().includes(search.toLowerCase())
        );
        setFilteredEquipment(filtered);
    }, [search, allEquipment]);

    return (
        <div className="space-y-4">
            <input
                type="text"
                placeholder="Buscar equipamiento..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full p-2 rounded bg-gray-800 text-white"
            />

            <EquipmentSelector
                equipmentList={filteredEquipment}
                onSave={(ids) => console.log('Guardados:', ids)}
            />
        </div>
    );
}

// ============================================================================
// 8. EXPORTAR/IMPORTAR CONFIGURACIÓN
// ============================================================================

import { useState } from 'react';
import EquipmentSelector from './EquipmentSelector';

export function WithExportImport() {
    const [selected, setSelected] = useState([]);

    const exportConfig = () => {
        const config = {
            timestamp: new Date().toISOString(),
            equipamientos: selected
        };
        const json = JSON.stringify(config, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `equipment-config-${Date.now()}.json`;
        a.click();
    };

    const importConfig = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const config = JSON.parse(event.target?.result);
            setSelected(config.equipamientos);
        };
        reader.readAsText(file);
    };

    return (
        <div className="space-y-4">
            <div className="flex gap-2">
                <button onClick={exportConfig}>Exportar Config</button>
                <label>
                    Importar Config
                    <input
                        type="file"
                        accept=".json"
                        onChange={importConfig}
                        hidden
                    />
                </label>
            </div>

            <EquipmentSelector
                equipmentList={/* ... */}
                initialSelected={selected}
                onSave={setSelected}
            />
        </div>
    );
}

// ============================================================================
// 9. COMPARAR CONFIGURACIONES
// ============================================================================

export function CompareConfigurations() {
    const [config1, setConfig1] = useState([]);
    const [config2, setConfig2] = useState([]);

    const comparison = {
        enAmbas: config1.filter(id => config2.includes(id)),
        soloConfig1: config1.filter(id => !config2.includes(id)),
        soloConfig2: config2.filter(id => !config1.includes(id))
    };

    return (
        <div className="grid grid-cols-2 gap-4">
            <div>
                <h3>Configuración 1</h3>
                <EquipmentSelector
                    equipmentList={/* ... */}
                    initialSelected={config1}
                    onSave={setConfig1}
                />
            </div>

            <div>
                <h3>Configuración 2</h3>
                <EquipmentSelector
                    equipmentList={/* ... */}
                    initialSelected={config2}
                    onSave={setConfig2}
                />
            </div>

            <div className="col-span-2 bg-gray-800 p-4 rounded">
                <p>En ambas: {comparison.enAmbas.length}</p>
                <p>Solo Config 1: {comparison.soloConfig1.length}</p>
                <p>Solo Config 2: {comparison.soloConfig2.length}</p>
            </div>
        </div>
    );
}

// ============================================================================
// 10. ANÁLISIS Y ESTADÍSTICAS
// ============================================================================

import { useMemo } from 'react';
import EquipmentSelector from './EquipmentSelector';

export function WithAnalytics() {
    const [equipment, setEquipment] = useState([]);
    const [selected, setSelected] = useState([]);

    const analytics = useMemo(() => {
        const selectedEquip = equipment.filter(e => selected.includes(e.id));
        const byCategory = {};

        selectedEquip.forEach(e => {
            byCategory[e.categoria] = (byCategory[e.categoria] || 0) + 1;
        });

        return {
            total: selected.length,
            byCategory,
            percentage: (selected.length / equipment.length) * 100
        };
    }, [selected, equipment]);

    return (
        <div className="space-y-4">
            <EquipmentSelector
                equipmentList={equipment}
                initialSelected={selected}
                onSave={setSelected}
            />

            <div className="bg-gray-800 p-4 rounded">
                <h3>Estadísticas</h3>
                <p>Total seleccionado: {analytics.total}</p>
                <p>Porcentaje: {analytics.percentage.toFixed(1)}%</p>
                <div>
                    {Object.entries(analytics.byCategory).map(([cat, count]) => (
                        <p key={cat}>{cat}: {count}</p>
                    ))}
                </div>
            </div>
        </div>
    );
}

// ============================================================================
// Exportar todos los ejemplos
// ============================================================================

export {
    BasicUsage,
    WithErrorHandling,
    FilteredByCategory,
    WithinLargerForm,
    WithUserPreferences,
    WithRecommendations,
    WithSearch,
    WithExportImport,
    CompareConfigurations,
    WithAnalytics
};
