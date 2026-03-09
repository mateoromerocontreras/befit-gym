import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, Mail, Lock, Loader2 } from 'lucide-react';

const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [password2, setPassword2] = useState('');
    const [age, setAge] = useState('');
    const [goal, setGoal] = useState('GENERAL_HEALTH');
    const [level, setLevel] = useState('BEGINNER');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password !== password2) {
            setError('Las contraseñas no coinciden');
            return;
        }

        setLoading(true);
        const payload = {
            email,
            password,
            password2,
            age: age ? Number(age) : undefined,
            goal,
            level,
        };

        const result = await register(payload);
        setLoading(false);

        if (result.success) {
            navigate('/dashboard');
        } else {
            setError(result.message);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 flex flex-col">
            {/* Navbar */}
            <nav className="bg-gray-900/95 backdrop-blur-sm border-b border-gray-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <Link to="/" className="text-2xl font-bold text-accent-lime">
                            GymFlow
                        </Link>
                        <Link
                            to="/"
                            className="text-gray-300 hover:text-accent-lime transition-colors duration-200 text-sm font-medium"
                        >
                            Volver al inicio
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
                <div className="w-full max-w-md">
                    <div className="bg-gray-900 border border-gray-800 rounded-xl shadow-2xl p-8">
                        {/* Header */}
                        <div className="text-center mb-8">
                            <div className="flex justify-center mb-4">
                                <div className="p-3 bg-accent-lime/10 rounded-full">
                                    <UserPlus className="h-8 w-8 text-accent-lime" />
                                </div>
                            </div>
                            <h2 className="text-3xl font-bold text-gray-100 mb-2">
                                Crear Cuenta
                            </h2>
                            <p className="text-gray-400">
                                Únete a GymFlow y comienza tu transformación
                            </p>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                                <p className="text-red-400 text-sm">{error}</p>
                            </div>
                        )}

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {/* Email Field */}
                            <div>
                                <label
                                    htmlFor="email"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Email
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-gray-500" />
                                    </div>
                                    <input
                                        type="email"
                                        id="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        autoComplete="email"
                                        placeholder="tu@email.com"
                                        className="block w-full pl-10 pr-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                                <p className="mt-2 text-xs text-gray-500">
                                    Nunca compartiremos tu email con nadie.
                                </p>
                            </div>

                            {/* Password Field */}
                            <div>
                                <label
                                    htmlFor="password"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Contraseña
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock className="h-5 w-5 text-gray-500" />
                                    </div>
                                    <input
                                        type="password"
                                        id="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        autoComplete="new-password"
                                        placeholder="Mínimo 8 caracteres"
                                        minLength="8"
                                        className="block w-full pl-10 pr-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                                <p className="mt-2 text-xs text-gray-500">
                                    La contraseña debe tener al menos 8 caracteres.
                                </p>
                            </div>

                            {/* Confirm Password Field */}
                            <div>
                                <label
                                    htmlFor="password2"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Confirmar Contraseña
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Lock className="h-5 w-5 text-gray-500" />
                                    </div>
                                    <input
                                        type="password"
                                        id="password2"
                                        value={password2}
                                        onChange={(e) => setPassword2(e.target.value)}
                                        required
                                        autoComplete="new-password"
                                        placeholder="Confirma tu contraseña"
                                        minLength="8"
                                        className="block w-full pl-10 pr-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                            </div>

                            <div>
                                <label
                                    htmlFor="age"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Edad
                                </label>
                                <input
                                    type="number"
                                    id="age"
                                    value={age}
                                    onChange={(e) => setAge(e.target.value)}
                                    min="1"
                                    max="120"
                                    placeholder="Ej: 28"
                                    className="block w-full px-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                />
                            </div>

                            <div>
                                <label
                                    htmlFor="goal"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Objetivo
                                </label>
                                <select
                                    id="goal"
                                    value={goal}
                                    onChange={(e) => setGoal(e.target.value)}
                                    className="block w-full px-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                >
                                    <option value="LOSE_WEIGHT">Perder peso</option>
                                    <option value="GAIN_MUSCLE">Ganar músculo</option>
                                    <option value="TONE">Tonificar</option>
                                    <option value="STRENGTH">Aumentar fuerza</option>
                                    <option value="ENDURANCE">Mejorar resistencia</option>
                                    <option value="GENERAL_HEALTH">Salud general</option>
                                </select>
                            </div>

                            <div>
                                <label
                                    htmlFor="level"
                                    className="block text-sm font-medium text-gray-300 mb-2"
                                >
                                    Nivel
                                </label>
                                <select
                                    id="level"
                                    value={level}
                                    onChange={(e) => setLevel(e.target.value)}
                                    className="block w-full px-3 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                >
                                    <option value="BEGINNER">Principiante</option>
                                    <option value="INTERMEDIATE">Intermedio</option>
                                    <option value="ADVANCED">Avanzado</option>
                                </select>
                            </div>

                            {/* Submit Button */}
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full py-3 px-4 bg-accent-lime text-gray-950 font-bold rounded-lg hover:bg-accent-electric hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2 shadow-lg shadow-accent-lime/20"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="h-5 w-5 animate-spin" />
                                        Creando cuenta...
                                    </>
                                ) : (
                                    'Registrarse'
                                )}
                            </button>
                        </form>

                        {/* Login Link */}
                        <div className="mt-6 text-center">
                            <p className="text-gray-400 text-sm">
                                ¿Ya tienes una cuenta?{' '}
                                <Link
                                    to="/login"
                                    className="text-accent-lime hover:text-accent-electric font-medium transition-colors duration-200"
                                >
                                    Inicia sesión aquí
                                </Link>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;
