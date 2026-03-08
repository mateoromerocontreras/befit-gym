import { useState, useEffect } from 'react';
import EquipmentSelector from './EquipmentSelector';
import equipmentService from '../services/equipmentService';

/**
 * EquipmentPage Component
 * 
 * Página de ejemplo para usar EquipmentSelector.jsx
 * Gestiona la carga de datos y el guardado de preferencias.
 */
const EquipmentPage = () => {
    const [equipmentList, setEquipmentList] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);
    const [userSelected, setUserSelected] = useState([]);

    // Cargar equipamiento al montar el componente
    useEffect(() => {
        loadEquipment();
        loadUserSelection();
    }, []);

    const loadEquipment = async () => {
        try {
            setLoading(true);
            const data = await equipmentService.getAllEquipment();
            setEquipmentList(data);
        } catch (error) {
            console.error('Error loading equipment:', error);
            setMessage({
                type: 'error',
                text: 'Error al cargar el equipamiento'
            });
        } finally {
            setLoading(false);
        }
    };

    const loadUserSelection = async () => {
        try {
            const selected = await equipmentService.getUserEquipmentSelection();
            setUserSelected(selected);
        } catch (error) {
            console.error('Error loading user selection:', error);
        }
    };

    const handleSave = async (selectedIds) => {
        try {
            setSaving(true);
            await equipmentService.saveEquipmentSelection(selectedIds);
            setUserSelected(selectedIds);
            setMessage({
                type: 'success',
                text: `✓ Se guardaron ${selectedIds.length} equipos correctamente`
            });
            // Limpiar mensaje después de 3 segundos
            setTimeout(() => setMessage(null), 3000);
        } catch (error) {
            console.error('Error saving selection:', error);
            setMessage({
                type: 'error',
                text: 'Error al guardar la configuración'
            });
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950">
            {/* Header */}
            <div className="bg-gray-900 border-b border-gray-800 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <h1 className="text-3xl font-bold text-accent-lime">
                        Mi Equipo de Entrenamiento
                    </h1>
                    <p className="text-gray-400 mt-2">
                        Personaliza tu equipamiento disponible para crear entrenamientos adaptados
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Mensaje */}
                {message && (
                    <div
                        className={`mb-6 p-4 rounded-lg border ${message.type === 'success'
                                ? 'bg-green-900/20 border-green-700 text-green-300'
                                : 'bg-red-900/20 border-red-700 text-red-300'
                            }`}
                    >
                        {message.text}
                    </div>
                )}

                {/* Equipment Selector */}
                <EquipmentSelector
                    equipmentList={equipmentList}
                    onSave={handleSave}
                    initialSelected={userSelected}
                    loading={loading || saving}
                />
            </main>
        </div>
    );
};

export default EquipmentPage;
