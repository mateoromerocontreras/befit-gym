import { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
    LayoutDashboard,
    User,
    Dumbbell,
    LogOut,
    Menu,
    X,
    Sparkles
} from 'lucide-react';

/**
 * Layout Component
 * 
 * Componente principal de navegación con sidebar lateral responsive.
 * Incluye navegación, perfil de usuario y estado de suscripción.
 */
const Layout = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navigation = [
        {
            name: 'Dashboard',
            href: '/dashboard',
            icon: LayoutDashboard,
            description: 'Panel principal'
        },
        {
            name: 'Mi Perfil',
            href: '/profile',
            icon: User,
            description: 'Configuración personal'
        },
        {
            name: 'Equipamiento',
            href: '/equipment',
            icon: Dumbbell,
            description: 'Mi equipo disponible'
        }
    ];

    return (
        <div className="min-h-screen bg-gray-950 flex">
            {/* Sidebar Desktop */}
            <aside className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-gray-900 border-r border-gray-800">
                {/* Logo */}
                <div className="flex items-center gap-3 h-16 px-6 border-b border-gray-800">
                    <span className="text-2xl">💪</span>
                    <span className="text-xl font-bold text-accent-lime">Befit Gym</span>
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-4 py-6 space-y-2">
                    {navigation.map((item) => (
                        <NavLink
                            key={item.name}
                            to={item.href}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${isActive
                                    ? 'bg-accent-lime/10 text-accent-lime border border-accent-lime/30'
                                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                                }`
                            }
                        >
                            {({ isActive }) => (
                                <>
                                    <item.icon className={`w-5 h-5 ${isActive ? 'text-accent-lime' : 'group-hover:text-gray-200'}`} />
                                    <div className="flex-1">
                                        <p className={`text-sm font-medium ${isActive ? 'text-accent-lime' : ''}`}>
                                            {item.name}
                                        </p>
                                        <p className="text-xs text-gray-500 group-hover:text-gray-400">
                                            {item.description}
                                        </p>
                                    </div>
                                </>
                            )}
                        </NavLink>
                    ))}
                </nav>

                {/* User Info */}
                <div className="border-t border-gray-800 p-4">
                    <div className="flex items-center gap-3 mb-3">
                        <div className="w-10 h-10 rounded-full bg-accent-lime/20 flex items-center justify-center">
                            <User className="w-5 h-5 text-accent-lime" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-200 truncate">
                                {user?.email}
                            </p>
                            <div className="flex items-center gap-1 mt-0.5">
                                {user?.suscripcion_activa ? (
                                    <>
                                        <Sparkles className="w-3 h-3 text-accent-lime" />
                                        <p className="text-xs text-accent-lime">Premium</p>
                                    </>
                                ) : (
                                    <p className="text-xs text-gray-500">Free</p>
                                )}
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors text-sm"
                    >
                        <LogOut className="w-4 h-4" />
                        Cerrar sesión
                    </button>
                </div>
            </aside>

            {/* Mobile Sidebar */}
            <div
                className={`fixed inset-0 z-50 lg:hidden transition-opacity duration-300 ${sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
                    }`}
            >
                {/* Backdrop */}
                <div
                    className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                    onClick={() => setSidebarOpen(false)}
                ></div>

                {/* Sidebar Content */}
                <aside
                    className={`absolute inset-y-0 left-0 w-64 bg-gray-900 border-r border-gray-800 transform transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                        }`}
                >
                    {/* Logo */}
                    <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">💪</span>
                            <span className="text-xl font-bold text-accent-lime">Befit Gym</span>
                        </div>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="p-2 rounded-lg hover:bg-gray-800 text-gray-400"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-4 py-6 space-y-2">
                        {navigation.map((item) => (
                            <NavLink
                                key={item.name}
                                to={item.href}
                                onClick={() => setSidebarOpen(false)}
                                className={({ isActive }) =>
                                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${isActive
                                        ? 'bg-accent-lime/10 text-accent-lime border border-accent-lime/30'
                                        : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                                    }`
                                }
                            >
                                {({ isActive }) => (
                                    <>
                                        <item.icon className={`w-5 h-5 ${isActive ? 'text-accent-lime' : ''}`} />
                                        <div className="flex-1">
                                            <p className={`text-sm font-medium ${isActive ? 'text-accent-lime' : ''}`}>
                                                {item.name}
                                            </p>
                                            <p className="text-xs text-gray-500">
                                                {item.description}
                                            </p>
                                        </div>
                                    </>
                                )}
                            </NavLink>
                        ))}
                    </nav>

                    {/* User Info Mobile */}
                    <div className="border-t border-gray-800 p-4">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-full bg-accent-lime/20 flex items-center justify-center">
                                <User className="w-5 h-5 text-accent-lime" />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-200 truncate">
                                    {user?.email}
                                </p>
                                <p className="text-xs text-gray-500">
                                    {user?.suscripcion_activa ? '✨ Premium' : 'Free'}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors text-sm"
                        >
                            <LogOut className="w-4 h-4" />
                            Cerrar sesión
                        </button>
                    </div>
                </aside>
            </div>

            {/* Main Content */}
            <div className="flex-1 lg:pl-64">
                {/* Mobile Header */}
                <header className="lg:hidden sticky top-0 z-40 bg-gray-900/95 backdrop-blur border-b border-gray-800">
                    <div className="flex items-center justify-between h-16 px-4">
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="p-2 rounded-lg hover:bg-gray-800 text-gray-400"
                        >
                            <Menu className="w-6 h-6" />
                        </button>
                        <div className="flex items-center gap-2">
                            <span className="text-xl">💪</span>
                            <span className="text-lg font-bold text-accent-lime">Befit Gym</span>
                        </div>
                        <div className="w-10"></div> {/* Spacer para centrar */}
                    </div>
                </header>

                {/* Page Content */}
                <main className="min-h-screen">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default Layout;
