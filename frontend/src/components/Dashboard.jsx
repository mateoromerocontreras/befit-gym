import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import PlanSemanal from './PlanSemanal';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-950">
            {/* Navbar */}
            <nav className="bg-gray-900 border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-2">
                            <span className="text-2xl">💪</span>
                            <span className="text-xl font-bold text-accent-lime">Befit Gym</span>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="text-gray-400 text-sm hidden sm:block">
                                {user?.email}
                            </span>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 rounded-lg transition-colors border border-gray-700"
                            >
                                Cerrar sesión
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

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

                {/* Plan Semanal */}
                <PlanSemanal />

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
