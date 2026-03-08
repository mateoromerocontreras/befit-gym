import { useState, useEffect } from 'react';
import {
    Dumbbell,
    Cpu,
    Heart,
    Package,
    Users,
    Check,
    ChevronDown,
    ChevronUp,
    Save,
    AlertCircle,
} from 'lucide-react';

/**
 * EquipmentSelector Component
 * 
 * Componente interactivo para seleccionar equipamiento de gimnasio.
 * Agrupa equipos por categoría y permite selección individual o por lotes.
 * 
 * Props:
 * - equipmentList: Array de objetos con {id, nombre, categoria}
 * - onSave: Callback que recibe el array de IDs seleccionados
 * - initialSelected: Array de IDs preseleccionados (opcional)
 * - loading: Estado de carga (opcional)
 */
const EquipmentSelector = ({
    equipmentList = [],
    onSave,
    initialSelected = [],
    loading = false
}) => {
    const [selected, setSelected] = useState(initialSelected);
    const [expandedCategories, setExpandedCategories] = useState({});
    const [allExpanded, setAllExpanded] = useState(true);

    // Inicializar categorías expandidas
    useEffect(() => {
        const categories = ['PESO_LIBRE', 'MAQUINA', 'CARDIO', 'ACCESORIO', 'CALISTENIA'];
        const expanded = categories.reduce((acc, cat) => {
            acc[cat] = true;
            return acc;
        }, {});
        setExpandedCategories(expanded);
    }, []);

    // Mapeo de categorías a iconos y colores
    const categoryConfig = {
        PESO_LIBRE: {
            icon: Dumbbell,
            label: 'Peso Libre',
            bgColor: 'bg-orange-900/20',
            borderColor: 'border-orange-700',
            textColor: 'text-orange-300',
        },
        MAQUINA: {
            icon: Cpu,
            label: 'Máquinas',
            bgColor: 'bg-blue-900/20',
            borderColor: 'border-blue-700',
            textColor: 'text-blue-300',
        },
        CARDIO: {
            icon: Heart,
            label: 'Cardio',
            bgColor: 'bg-red-900/20',
            borderColor: 'border-red-700',
            textColor: 'text-red-300',
        },
        ACCESORIO: {
            icon: Package,
            label: 'Accesorios',
            bgColor: 'bg-purple-900/20',
            borderColor: 'border-purple-700',
            textColor: 'text-purple-300',
        },
        CALISTENIA: {
            icon: Users,
            label: 'Calistenia',
            bgColor: 'bg-green-900/20',
            borderColor: 'border-green-700',
            textColor: 'text-green-300',
        },
    };

    // Agrupar equipamiento por categoría
    const groupedEquipment = equipmentList.reduce((acc, item) => {
        if (!acc[item.categoria]) {
            acc[item.categoria] = [];
        }
        acc[item.categoria].push(item);
        return acc;
    }, {});

    // Alternar selección de un equipamiento
    const toggleEquipment = (id) => {
        setSelected((prev) =>
            prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
        );
    };

    // Seleccionar/deseleccionar toda una categoría
    const toggleCategory = (categoria) => {
        const categoryItems = groupedEquipment[categoria] || [];
        const categoryIds = categoryItems.map((item) => item.id);
        const allSelected = categoryIds.every((id) => selected.includes(id));

        if (allSelected) {
            setSelected((prev) =>
                prev.filter((id) => !categoryIds.includes(id))
            );
        } else {
            setSelected((prev) => [
                ...prev,
                ...categoryIds.filter((id) => !prev.includes(id)),
            ]);
        }
    };

    // Expandir/contraer categoría
    const toggleCategoryExpand = (categoria) => {
        setExpandedCategories((prev) => ({
            ...prev,
            [categoria]: !prev[categoria],
        }));
    };

    // Expandir/contraer todo
    const toggleAllExpand = () => {
        const newState = !allExpanded;
        const categories = Object.keys(groupedEquipment);
        const expanded = categories.reduce((acc, cat) => {
            acc[cat] = newState;
            return acc;
        }, {});
        setExpandedCategories(expanded);
        setAllExpanded(newState);
    };

    // Manejar guardado
    const handleSave = () => {
        if (onSave) {
            onSave(selected);
        }
    };

    const categories = Object.keys(groupedEquipment).sort();
    const totalEquipment = equipmentList.length;
    const selectPercentage = totalEquipment > 0 ? (selected.length / totalEquipment) * 100 : 0;

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-lime mx-auto mb-4"></div>
                    <p className="text-gray-300">Cargando equipamiento...</p>
                </div>
            </div>
        );
    }

    if (equipmentList.length === 0) {
        return (
            <div className="bg-gray-800/50 rounded-lg p-8 text-center border border-gray-700">
                <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold text-gray-300 mb-2">
                    Sin equipamiento disponible
                </h3>
                <p className="text-gray-400">
                    No hay equipamiento para mostrar en este momento.
                </p>
            </div>
        );
    }

    return (
        <div className="pb-32">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold text-accent-lime">
                        🏋️ Seleccionar Equipamiento
                    </h2>
                    <button
                        onClick={toggleAllExpand}
                        className="px-3 py-1 text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors border border-gray-700"
                    >
                        {allExpanded ? 'Contraer todo' : 'Expandir todo'}
                    </button>
                </div>
                <p className="text-gray-400">
                    Selecciona los equipos que utilizarás en tus entrenamientos.
                </p>
            </div>

            {/* Categorías */}
            <div className="space-y-4">
                {categories.map((categoria) => {
                    const config = categoryConfig[categoria];
                    const IconComponent = config.icon;
                    const items = groupedEquipment[categoria] || [];
                    const selectedInCategory = items.filter((item) =>
                        selected.includes(item.id)
                    ).length;
                    const allCategorySelected = items.length > 0 &&
                        items.every((item) => selected.includes(item.id));
                    const isExpanded = expandedCategories[categoria];

                    return (
                        <div
                            key={categoria}
                            className="bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden transition-colors hover:border-gray-600"
                        >
                            {/* Encabezado de Categoría */}
                            <div className="p-4 bg-gray-900/50">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3 flex-1">
                                        <button
                                            onClick={() => toggleCategoryExpand(categoria)}
                                            className="p-1 hover:bg-gray-700 rounded transition-colors"
                                        >
                                            {isExpanded ? (
                                                <ChevronUp className="w-5 h-5 text-gray-400" />
                                            ) : (
                                                <ChevronDown className="w-5 h-5 text-gray-400" />
                                            )}
                                        </button>

                                        <IconComponent className={`w-5 h-5 ${config.textColor}`} />

                                        <div className="flex-1">
                                            <h3 className="font-semibold text-gray-100">
                                                {config.label}
                                            </h3>
                                            <p className="text-xs text-gray-400">
                                                {selectedInCategory} de {items.length} seleccionados
                                            </p>
                                        </div>
                                    </div>

                                    {/* Barra de progreso mínima */}
                                    <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden mx-2">
                                        <div
                                            className="h-full bg-accent-lime transition-all duration-300"
                                            style={{
                                                width: items.length > 0
                                                    ? `${(selectedInCategory / items.length) * 100}%`
                                                    : '0%'
                                            }}
                                        ></div>
                                    </div>

                                    {/* Botón Seleccionar Todo */}
                                    <button
                                        onClick={() => toggleCategory(categoria)}
                                        className={`
                      px-3 py-1 text-xs font-medium rounded-md transition-colors whitespace-nowrap
                      ${allCategorySelected
                                                ? 'bg-accent-lime text-gray-900'
                                                : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                                            }
                    `}
                                    >
                                        {allCategorySelected ? '✓ Seleccionado' : 'Seleccionar todo'}
                                    </button>
                                </div>
                            </div>

                            {/* Items de la Categoría */}
                            {isExpanded && (
                                <div className="p-4 border-t border-gray-700">
                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                                        {items.map((item) => {
                                            const isSelected = selected.includes(item.id);

                                            return (
                                                <button
                                                    key={item.id}
                                                    onClick={() => toggleEquipment(item.id)}
                                                    className={`
                            group relative p-3 rounded-lg border-2 transition-all duration-200
                            ${isSelected
                                                            ? 'bg-accent-lime/10 border-accent-lime shadow-lg shadow-accent-lime/20'
                                                            : 'bg-gray-900/50 border-gray-700 hover:border-accent-lime/50'
                                                        }
                            hover:scale-105 active:scale-95
                          `}
                                                >
                                                    {/* Checkmark */}
                                                    {isSelected && (
                                                        <div className="absolute top-2 right-2">
                                                            <div className="bg-accent-lime rounded-full p-0.5">
                                                                <Check className="w-3 h-3 text-gray-900" />
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Icono por categoría */}
                                                    <div className={`mb-2 ${config.textColor}`}>
                                                        <IconComponent className="w-5 h-5" />
                                                    </div>

                                                    {/* Nombre */}
                                                    <p
                                                        className={`
                              text-xs font-medium text-left line-clamp-2
                              ${isSelected ? 'text-accent-lime' : 'text-gray-300'}
                            `}
                                                    >
                                                        {item.nombre}
                                                    </p>
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Panel Sticky Inferior */}
            <div className="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur border-t border-gray-800 p-4">
                <div className="max-w-7xl mx-auto">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div>
                                <p className="text-sm text-gray-400">Equipamiento seleccionado</p>
                                <p className="text-2xl font-bold text-accent-lime">
                                    {selected.length} / {totalEquipment}
                                </p>
                            </div>

                            {/* Barra de progreso grande */}
                            <div className="hidden sm:block w-48 h-2 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-accent-lime to-accent-electric transition-all duration-300"
                                    style={{ width: `${selectPercentage}%` }}
                                ></div>
                            </div>

                            {/* Porcentaje */}
                            <span className="hidden md:inline text-sm font-medium text-gray-300">
                                {Math.round(selectPercentage)}%
                            </span>
                        </div>

                        <button
                            onClick={handleSave}
                            disabled={selected.length === 0 || loading}
                            className={`
                px-6 py-2 font-semibold rounded-lg transition-all duration-200
                flex items-center gap-2
                ${selected.length === 0 || loading
                                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                    : 'bg-accent-lime hover:bg-yellow-300 text-gray-900 shadow-lg shadow-accent-lime/30 hover:shadow-accent-lime/50 active:scale-95'
                                }
              `}
                        >
                            <Save className="w-4 h-4" />
                            <span className="hidden sm:inline">Guardar Configuración</span>
                            <span className="sm:hidden">Guardar</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EquipmentSelector;
