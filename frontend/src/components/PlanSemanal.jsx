import { useState, useEffect } from 'react';
import planService from '../services/planService';

const PlanSemanal = () => {
    const [planes, setPlanes] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedDia, setSelectedDia] = useState(null);
    const [detalleRutina, setDetalleRutina] = useState(null);

    useEffect(() => {
        cargarPlanSemanal();
    }, []);

    const cargarPlanSemanal = async () => {
        try {
            setLoading(true);
            const data = await planService.getPlanSemanal();
            const organizado = planService.organizarPorDia(data);
            setPlanes(organizado);
            setError(null);
        } catch (err) {
            setError('Error al cargar el plan semanal');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDiaClick = async (dia, plan) => {
        if (selectedDia === dia) {
            setSelectedDia(null);
            setDetalleRutina(null);
            return;
        }

        setSelectedDia(dia);

        if (plan) {
            try {
                const detalle = await planService.getPlanDetalle(plan.id);
                setDetalleRutina(detalle.rutina);
            } catch (err) {
                console.error('Error al cargar detalle:', err);
                setDetalleRutina(null);
            }
        } else {
            setDetalleRutina(null);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-lime"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-900/30 border border-red-500 text-red-300 px-4 py-3 rounded-lg">
                {error}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-accent-lime mb-6">
                📅 Mi Plan Semanal
            </h2>

            {/* Grid de días */}
            <div className="grid grid-cols-1 md:grid-cols-7 gap-2">
                {Object.entries(planes).map(([dia, { nombre, plan }]) => (
                    <button
                        key={dia}
                        onClick={() => handleDiaClick(Number(dia), plan)}
                        className={`
                            p-4 rounded-lg transition-all duration-200 text-left
                            ${selectedDia === Number(dia)
                                ? 'bg-accent-lime text-gray-900 ring-2 ring-accent-lime'
                                : plan
                                    ? 'bg-gray-800 hover:bg-gray-700 border border-gray-700'
                                    : 'bg-gray-900 hover:bg-gray-800 border border-gray-800 opacity-60'
                            }
                        `}
                    >
                        <div className="font-semibold text-sm">{nombre}</div>
                        <div className={`text-xs mt-1 ${selectedDia === Number(dia) ? 'text-gray-800' : 'text-gray-400'}`}>
                            {plan ? plan.rutina_nombre : 'Descanso'}
                        </div>
                    </button>
                ))}
            </div>

            {/* Detalle del día seleccionado */}
            {selectedDia && (
                <div className="mt-6 bg-gray-800/50 rounded-xl p-6 border border-gray-700 animate-fadeIn">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">
                            {planes[selectedDia]?.nombre}
                        </h3>
                        {planes[selectedDia]?.plan && (
                            <span className="px-3 py-1 bg-accent-lime/20 text-accent-lime rounded-full text-sm font-medium">
                                {planes[selectedDia].plan.rutina_nombre}
                            </span>
                        )}
                    </div>

                    {detalleRutina ? (
                        <div className="space-y-3">
                            {detalleRutina.descripcion && (
                                <p className="text-gray-400 text-sm mb-4">
                                    {detalleRutina.descripcion}
                                </p>
                            )}

                            <h4 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">
                                Ejercicios ({detalleRutina.ejercicios_detalle?.length || 0})
                            </h4>

                            <div className="space-y-2">
                                {detalleRutina.ejercicios_detalle?.map((ej, index) => (
                                    <div
                                        key={index}
                                        className="bg-gray-900/50 rounded-lg p-4 border border-gray-700 hover:border-accent-lime/50 transition-colors"
                                    >
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <h5 className="font-semibold text-white">
                                                    {ej.ejercicio.nombre}
                                                </h5>
                                                {ej.ejercicio.descripcion && (
                                                    <p className="text-gray-400 text-sm mt-1">
                                                        {ej.ejercicio.descripcion}
                                                    </p>
                                                )}
                                            </div>
                                            <div className="ml-4 text-right">
                                                <span className="inline-block px-2 py-1 bg-gray-800 rounded text-xs text-gray-300">
                                                    {ej.ejercicio.grupo_muscular}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex gap-4 mt-3 text-sm">
                                            <div className="flex items-center gap-1">
                                                <span className="text-accent-lime font-bold">{ej.series}</span>
                                                <span className="text-gray-500">series</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <span className="text-accent-lime font-bold">{ej.repeticiones}</span>
                                                <span className="text-gray-500">reps</span>
                                            </div>
                                            {ej.descanso_segundos && (
                                                <div className="flex items-center gap-1">
                                                    <span className="text-accent-lime font-bold">{ej.descanso_segundos}s</span>
                                                    <span className="text-gray-500">descanso</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : planes[selectedDia]?.plan ? (
                        <p className="text-gray-400">Cargando ejercicios...</p>
                    ) : (
                        <div className="text-center py-8">
                            <span className="text-4xl">😴</span>
                            <p className="text-gray-400 mt-2">Día de descanso</p>
                        </div>
                    )}
                </div>
            )}

            {/* Mensaje cuando no hay planes */}
            {Object.values(planes).every(({ plan }) => !plan) && (
                <div className="text-center py-12 bg-gray-800/30 rounded-xl border border-gray-700">
                    <span className="text-5xl">📋</span>
                    <h3 className="text-xl font-semibold text-white mt-4">
                        Sin plan asignado
                    </h3>
                    <p className="text-gray-400 mt-2">
                        Aún no tienes un plan de entrenamiento semanal asignado.
                    </p>
                </div>
            )}
        </div>
    );
};

export default PlanSemanal;
