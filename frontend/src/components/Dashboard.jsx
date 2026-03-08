import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PlanSemanal from './PlanSemanal';
import profileService from '../services/profileService';
import planService from '../services/planService';
import { Sparkles, Loader, AlertCircle, CheckCircle, Dumbbell, Calendar, Target } from 'lucide-react';

const Dashboard = () => {
    const { user } = useAuth();
    const navigate = useNavigate();
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
            const data = await planService.getPlanSemanal();
            setPlanSemanal(data.results || data);
        } catch (error) {
            console.error('Error loading plan semanal:', error);
            setPlanSemanal([]);
        } finally {
            setLoadingPlan(false);
        }
    };

    const handleGenerateRoutine = async () => {
        setGenerating(true);
        setMessage(null);

        try {
            const result = await profileService.generateRoutine(3);

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
            const errorMsg = error.response?.data?.error || 'Error al comunicarse con el servidor';
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

                {/* Plan Semanal o Empty State */}
                {loadingPlan ? (
                    <div className="flex items-center justify-center py-12">
                        <Loader className="w-8 h-8 text-accent-lime animate-spin" />
                    </div>
                ) : hasActivePlan ? (
                    <PlanSemanal />
                ) : (
                    /* Empty State */
                    <div className="bg-gray-900/50 rounded-2xl p-12 border-2 border-dashed border-gray-700 text-center mb-8">
                        <div className="max-w-md mx-auto">
                            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-accent-lime/20 to-accent-electric/20 flex items-center justify-center">
                                <Dumbbell className="w-10 h-10 text-accent-lime" />
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-3">
                                No tienes un plan activo
                            </h3>
                            <p className="text-gray-400 mb-6">
                                Genera tu plan de entrenamiento personalizado con IA en segundos.
                                La inteligencia artificial creará rutinas adaptadas a tu nivel y objetivos.
                            </p>

                            <button
                                onClick={handleGenerateRoutine}
                                disabled={generating}
                                className={`
                                    group relative inline-flex items-center gap-3 px-8 py-4 rounded-xl font-bold text-lg
                                    transition-all duration-200 overflow-hidden
                                    ${generating
                                        ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-accent-lime to-yellow-300 hover:from-yellow-300 hover:to-accent-lime text-gray-900 shadow-2xl shadow-accent-lime/50 hover:shadow-accent-lime/70 hover:scale-105 active:scale-95'
                                    }
                                `}
                            >
                                {generating ? (
                                    <>
                                        <Loader className="w-6 h-6 animate-spin" />
                                        <span>Generando con IA...</span>
                                    </>
                                ) : (
                                    <>
                                        <Sparkles className="w-6 h-6 group-hover:rotate-12 transition-transform" />
                                        <span>Generar Plan con IA</span>
                                    </>
                                )}
                            </button>

                            <div className="mt-8 grid grid-cols-3 gap-4 text-sm">
                                <div className="text-center">
                                    <div className="w-12 h-12 mx-auto mb-2 rounded-lg bg-accent-lime/10 flex items-center justify-center">
                                        <Calendar className="w-6 h-6 text-accent-lime" />
                                    </div>
                                    <p className="text-gray-400">3 días por semana</p>
                                </div>
                                <div className="text-center">
                                    <div className="w-12 h-12 mx-auto mb-2 rounded-lg bg-accent-electric/10 flex items-center justify-center">
                                        <Target className="w-6 h-6 text-accent-electric" />
                                    </div>
                                    <p className="text-gray-400">Personalizado</p>
                                </div>
                                <div className="text-center">
                                    <div className="w-12 h-12 mx-auto mb-2 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                        <Sparkles className="w-6 h-6 text-blue-400" />
                                    </div>
                                    <p className="text-gray-400">Con IA</p>
                                </div>
                            </div>
                        </div>
                    </div>
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
