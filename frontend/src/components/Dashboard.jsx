import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import WeeklyCalendarView from './WeeklyCalendarView';
import profileService from '../services/profileService';
import planService from '../services/planService';
import { Sparkles, Loader, AlertCircle, CheckCircle, Dumbbell } from 'lucide-react';

const Dashboard = () => {
    const { user } = useAuth();
    const [planSemanal, setPlanSemanal] = useState([]);
    const [loadingPlan, setLoadingPlan] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        loadPlanSemanal();
    }, []);

    const loadPlanSemanal = async () => {
        try {
            setLoadingPlan(true);
            const data = await planService.getWeeklyPlan();
            setPlanSemanal(data);
        } catch (error) {
            console.error('Error loading plan semanal:', error);
            setPlanSemanal([]);
        } finally {
            setLoadingPlan(false);
        }
    };

    const extractErrorMessage = (error) => {
        const data = error?.response?.data;
        if (!data) {
            return 'Error al comunicarse con el servidor';
        }

        if (typeof data === 'string') {
            return data;
        }

        if (data.error) {
            return data.error;
        }

        if (data.message) {
            return data.message;
        }

        if (data.detail) {
            return data.detail;
        }

        const firstFieldError = Object.values(data).find((value) => Array.isArray(value) && value.length > 0);
        if (firstFieldError) {
            return firstFieldError[0];
        }

        return 'No se pudo generar la rutina en este momento';
    };

    const handleGenerateRoutine = async () => {
        setGenerating(true);
        setMessage(null);

        try {
            const selectedWeekdays = user?.training_weekdays || user?.dias_entrenamiento || [1, 3, 5];

            const precheck = await profileService.getGenerateRoutinePrecheck(
                selectedWeekdays.length,
                selectedWeekdays
            );

            if (!precheck.ready) {
                const messages = {
                    api_key: 'Falta configurar GEMINI_API_KEY en backend.',
                    equipment: 'Selecciona equipamiento en tu perfil antes de generar la rutina con IA.',
                    compatible_exercises: 'No hay ejercicios compatibles con tu equipamiento actual.',
                    training_weekdays: 'Selecciona al menos un día de entrenamiento en tu perfil.'
                };
                const firstMissing = precheck.missing?.[0];

                setMessage({
                    type: 'error',
                    text: messages[firstMissing] || 'No se cumplen los requisitos para generar rutina.'
                });
                return;
            }

            const result = await profileService.generateRoutine(
                selectedWeekdays.length,
                null,
                selectedWeekdays
            );

            if (result.success) {
                setMessage({
                    type: 'success',
                    text: `✓ ${result.mensaje}. Se crearon ${result.ejercicios_count} ejercicios.`
                });

                // Recargar plan después de 2 segundos
                setTimeout(() => {
                    loadPlanSemanal();
                    setMessage(null);
                }, 2000);
            } else {
                setMessage({
                    type: 'error',
                    text: result.error || 'Error al generar rutina'
                });
            }
        } catch (error) {
            console.error('Error generating routine:', error);
            const errorMsg = extractErrorMessage(error);
            setMessage({
                type: 'error',
                text: errorMsg
            });
        } finally {
            setGenerating(false);
        }
    };

    const hasActivePlan = planSemanal.length > 0;

    return (
        <div className="min-h-screen bg-gray-950">
            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Welcome Card */}
                <div className="bg-gradient-to-r from-accent-lime/10 to-accent-electric/10 rounded-xl p-6 border border-gray-800 mb-8">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-full bg-accent-lime/20 flex items-center justify-center">
                            <span className="text-3xl">🏋️</span>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">
                                ¡Bienvenido de vuelta!
                            </h1>
                            <p className="text-gray-400">
                                Miembro desde {user?.date_joined && new Date(user.date_joined).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Message */}
                {message && (
                    <div
                        className={`mb-6 p-4 rounded-lg border flex items-center gap-3 ${message.type === 'success'
                                ? 'bg-green-900/20 border-green-700 text-green-300'
                                : 'bg-red-900/20 border-red-700 text-red-300'
                            }`}
                    >
                        {message.type === 'success' ? (
                            <CheckCircle className="w-5 h-5" />
                        ) : (
                            <AlertCircle className="w-5 h-5" />
                        )}
                        <span>{message.text}</span>
                    </div>
                )}

                <div className="mb-6">
                    <button
                        onClick={handleGenerateRoutine}
                        disabled={generating}
                        className={`
                            group relative inline-flex items-center gap-3 px-6 py-3 rounded-xl font-bold
                            transition-all duration-200 overflow-hidden
                            ${generating
                                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                : 'bg-gradient-to-r from-accent-lime to-yellow-300 hover:from-yellow-300 hover:to-accent-lime text-gray-900 shadow-xl shadow-accent-lime/40 hover:shadow-accent-lime/60'
                            }
                        `}
                    >
                        {generating ? (
                            <>
                                <Loader className="w-5 h-5 animate-spin" />
                                <span>Generando con IA...</span>
                            </>
                        ) : (
                            <>
                                <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform" />
                                <span>Generar Plan con IA</span>
                            </>
                        )}
                    </button>
                </div>

                {loadingPlan ? (
                    <div className="flex items-center justify-center py-12">
                        <Loader className="w-8 h-8 text-accent-lime animate-spin" />
                    </div>
                ) : (
                    <>
                        {!hasActivePlan && (
                            <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800 mb-6 text-gray-300 flex items-center gap-3">
                                <Dumbbell className="w-5 h-5 text-accent-lime" />
                                <span>No tienes rutina asignada todavía. Los días se mostrarán como Rest Day.</span>
                            </div>
                        )}
                        <WeeklyCalendarView weeklyPlan={planSemanal} />
                    </>
                )}

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 hover:border-accent-lime/30 transition-colors">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-accent-lime/20 flex items-center justify-center">
                                <span className="text-2xl">🏃</span>
                            </div>
                            <div>
                                <p className="text-gray-400 text-sm">Entrenamientos</p>
                                <p className="text-2xl font-bold text-white">0</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 hover:border-accent-electric/30 transition-colors">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-accent-electric/20 flex items-center justify-center">
                                <span className="text-2xl">🔥</span>
                            </div>
                            <div>
                                <p className="text-gray-400 text-sm">Racha actual</p>
                                <p className="text-2xl font-bold text-white">0 días</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 hover:border-blue-500/30 transition-colors">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-blue-500/20 flex items-center justify-center">
                                <span className="text-2xl">💎</span>
                            </div>
                            <div>
                                <p className="text-gray-400 text-sm">Estado</p>
                                <p className="text-lg font-bold text-accent-lime">
                                    {user?.suscripcion_activa ? 'Activo' : 'Sin suscripción'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
