import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import profileService from '../services/profileService';
import {
    User,
    Mail,
    Scale,
    Ruler,
    Calendar,
    Target,
    TrendingUp,
    Save,
    AlertCircle,
    CheckCircle,
    Loader
} from 'lucide-react';

/**
 * ProfilePage Component
 * 
 * Página de perfil del usuario con formulario completo de datos personales
 * y preferencias de entrenamiento.
 */
const ProfilePage = () => {
    const { user, setUser } = useAuth();
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null);

    const [formData, setFormData] = useState({
        edad: '',
        peso: '',
        altura: '',
        objetivo: 'GENERAL_HEALTH',
        nivel: 'BEGINNER',
        training_weekdays: [1, 3, 5]
    });

    const weekdayOptions = [
        { value: 1, label: 'Lun' },
        { value: 2, label: 'Mar' },
        { value: 3, label: 'Mié' },
        { value: 4, label: 'Jue' },
        { value: 5, label: 'Vie' },
        { value: 6, label: 'Sáb' },
        { value: 7, label: 'Dom' }
    ];

    useEffect(() => {
        if (user) {
            setFormData({
                edad: user.edad || '',
                peso: user.peso || '',
                altura: user.altura || '',
                objetivo: user.objetivo || 'GENERAL_HEALTH',
                nivel: user.nivel || 'BEGINNER',
                training_weekdays: user.training_weekdays || user.dias_entrenamiento || [1, 3, 5]
            });
        }
    }, [user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const toggleWeekday = (weekday) => {
        setFormData((prev) => {
            const exists = prev.training_weekdays.includes(weekday);
            const nextDays = exists
                ? prev.training_weekdays.filter((day) => day !== weekday)
                : [...prev.training_weekdays, weekday];

            return {
                ...prev,
                training_weekdays: nextDays.sort((a, b) => a - b)
            };
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        try {
            if (!formData.training_weekdays || formData.training_weekdays.length === 0) {
                setMessage({
                    type: 'error',
                    text: 'Selecciona al menos un día de entrenamiento.'
                });
                return;
            }

            // Preparar datos (convertir strings vacíos a null)
            const dataToSend = {
                age: formData.edad ? parseInt(formData.edad) : null,
                weight: formData.peso ? parseFloat(formData.peso) : null,
                height: formData.altura ? parseFloat(formData.altura) : null,
                goal: formData.objetivo,
                level: formData.nivel,
                training_weekdays: formData.training_weekdays
            };

            const updatedUser = await profileService.updateUserProfile(dataToSend);

            // Actualizar contexto de usuario
            const currentUser = JSON.parse(localStorage.getItem('user'));
            const newUser = { ...currentUser, ...updatedUser };
            localStorage.setItem('user', JSON.stringify(newUser));
            setUser(newUser);

            setMessage({
                type: 'success',
                text: '✓ Perfil actualizado correctamente'
            });

            // Limpiar mensaje después de 3 segundos
            setTimeout(() => setMessage(null), 3000);

        } catch (error) {
            console.error('Error updating profile:', error);
            setMessage({
                type: 'error',
                text: error.response?.data?.error || 'Error al actualizar el perfil'
            });
        } finally {
            setSaving(false);
        }
    };

    const objetivoOptions = [
        { value: 'LOSE_WEIGHT', label: 'Perder Peso', emoji: '🔥' },
        { value: 'GAIN_MUSCLE', label: 'Ganar Masa Muscular', emoji: '💪' },
        { value: 'TONE', label: 'Tonificar', emoji: '✨' },
        { value: 'STRENGTH', label: 'Aumentar Fuerza', emoji: '🏋️' },
        { value: 'ENDURANCE', label: 'Mejorar Resistencia', emoji: '🏃' },
        { value: 'GENERAL_HEALTH', label: 'Salud General', emoji: '❤️' }
    ];

    const nivelOptions = [
        { value: 'BEGINNER', label: 'Principiante', description: '0-6 meses de experiencia' },
        { value: 'INTERMEDIATE', label: 'Intermedio', description: '6 meses - 2 años' },
        { value: 'ADVANCED', label: 'Avanzado', description: 'Más de 2 años' }
    ];

    return (
        <div className="min-h-screen bg-gray-950 py-8 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-accent-lime to-accent-electric flex items-center justify-center">
                            <User className="w-8 h-8 text-gray-900" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-white">Mi Perfil</h1>
                            <p className="text-gray-400">Configura tu información personal y objetivos</p>
                        </div>
                    </div>

                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Calendar className="w-5 h-5 text-accent-lime" />
                            Días de Entrenamiento
                        </h2>
                        <p className="text-gray-400 text-sm mb-4">
                            Selecciona los días en los que entrenas normalmente.
                        </p>
                        <div className="grid grid-cols-4 sm:grid-cols-7 gap-2">
                            {weekdayOptions.map((day) => {
                                const isSelected = formData.training_weekdays.includes(day.value);
                                return (
                                    <button
                                        key={day.value}
                                        type="button"
                                        onClick={() => toggleWeekday(day.value)}
                                        className={`
                                            px-3 py-2 rounded-lg text-sm font-semibold transition-all border
                                            ${isSelected
                                                ? 'bg-accent-lime text-gray-900 border-accent-lime'
                                                : 'bg-gray-800 text-gray-300 border-gray-700 hover:border-gray-500'
                                            }
                                        `}
                                    >
                                        {day.label}
                                    </button>
                                );
                            })}
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

                {/* Form */}
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Email (readonly) */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Mail className="w-5 h-5 text-accent-lime" />
                            Información de Cuenta
                        </h2>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                value={user?.email || ''}
                                disabled
                                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-gray-500 cursor-not-allowed"
                            />
                            <p className="mt-1 text-xs text-gray-500">El email no puede ser modificado</p>
                        </div>
                    </div>

                    {/* Datos Físicos */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Scale className="w-5 h-5 text-accent-lime" />
                            Datos Físicos
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {/* Edad */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Edad (años)
                                </label>
                                <div className="relative">
                                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type="number"
                                        name="edad"
                                        value={formData.edad}
                                        onChange={handleChange}
                                        min="13"
                                        max="120"
                                        placeholder="Ej: 25"
                                        className="w-full pl-11 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                            </div>

                            {/* Peso */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Peso (kg)
                                </label>
                                <div className="relative">
                                    <Scale className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type="number"
                                        name="peso"
                                        value={formData.peso}
                                        onChange={handleChange}
                                        step="0.1"
                                        min="30"
                                        max="300"
                                        placeholder="Ej: 75.5"
                                        className="w-full pl-11 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                            </div>

                            {/* Altura */}
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Altura (m)
                                </label>
                                <div className="relative">
                                    <Ruler className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                                    <input
                                        type="number"
                                        name="altura"
                                        value={formData.altura}
                                        onChange={handleChange}
                                        step="0.01"
                                        min="1.00"
                                        max="2.50"
                                        placeholder="Ej: 1.75"
                                        className="w-full pl-11 pr-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:ring-2 focus:ring-accent-lime focus:border-transparent transition-all"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Objetivo */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5 text-accent-lime" />
                            Objetivo de Entrenamiento
                        </h2>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            {objetivoOptions.map((option) => (
                                <label
                                    key={option.value}
                                    className={`relative flex items-center gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${formData.objetivo === option.value
                                            ? 'border-accent-lime bg-accent-lime/10'
                                            : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                                        }`}
                                >
                                    <input
                                        type="radio"
                                        name="objetivo"
                                        value={option.value}
                                        checked={formData.objetivo === option.value}
                                        onChange={handleChange}
                                        className="sr-only"
                                    />
                                    <span className="text-2xl">{option.emoji}</span>
                                    <span
                                        className={`text-sm font-medium ${formData.objetivo === option.value
                                                ? 'text-accent-lime'
                                                : 'text-gray-300'
                                            }`}
                                    >
                                        {option.label}
                                    </span>
                                    {formData.objetivo === option.value && (
                                        <CheckCircle className="absolute top-2 right-2 w-4 h-4 text-accent-lime" />
                                    )}
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Nivel */}
                    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
                        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-accent-lime" />
                            Nivel de Experiencia
                        </h2>
                        <div className="space-y-3">
                            {nivelOptions.map((option) => (
                                <label
                                    key={option.value}
                                    className={`relative flex items-start gap-4 p-4 rounded-lg border-2 cursor-pointer transition-all ${formData.nivel === option.value
                                            ? 'border-accent-lime bg-accent-lime/10'
                                            : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                                        }`}
                                >
                                    <input
                                        type="radio"
                                        name="nivel"
                                        value={option.value}
                                        checked={formData.nivel === option.value}
                                        onChange={handleChange}
                                        className="mt-1"
                                    />
                                    <div className="flex-1">
                                        <p
                                            className={`font-medium ${formData.nivel === option.value
                                                    ? 'text-accent-lime'
                                                    : 'text-gray-300'
                                                }`}
                                        >
                                            {option.label}
                                        </p>
                                        <p className="text-sm text-gray-500 mt-0.5">
                                            {option.description}
                                        </p>
                                    </div>
                                    {formData.nivel === option.value && (
                                        <CheckCircle className="w-5 h-5 text-accent-lime" />
                                    )}
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Submit Button */}
                    <div className="flex items-center justify-end gap-4 pt-4">
                        <button
                            type="submit"
                            disabled={saving}
                            className={`
                                flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all
                                ${saving
                                    ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                                    : 'bg-accent-lime hover:bg-yellow-300 text-gray-900 shadow-lg shadow-accent-lime/30 hover:shadow-accent-lime/50 active:scale-95'
                                }
                            `}
                        >
                            {saving ? (
                                <>
                                    <Loader className="w-5 h-5 animate-spin" />
                                    Guardando...
                                </>
                            ) : (
                                <>
                                    <Save className="w-5 h-5" />
                                    Guardar Cambios
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ProfilePage;
