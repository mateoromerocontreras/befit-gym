import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

class PlanService {
    muscleGroupLabels = {
        CHEST: 'Pecho',
        BACK: 'Espalda',
        LEGS: 'Piernas',
        SHOULDERS: 'Hombros',
        ARMS: 'Brazos',
        CORE: 'Core',
        FULL_BODY: 'Cuerpo completo'
    };

    difficultyLabels = {
        BEGINNER: 'Principiante',
        INTERMEDIATE: 'Intermedio',
        ADVANCED: 'Avanzado'
    };

    /**
     * Obtiene el header de autorización con el token JWT
     */
    getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    /**
     * Obtiene el plan semanal del usuario autenticado
     * @returns {Promise<Array>} Lista de planes por día de la semana
     */
    async getPlanSemanal() {
        const response = await axios.get(`${API_URL}/weekly-plan/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Obtiene el plan semanal en formato calendario
     * @returns {Promise<Array>} Lista de días con ejercicios anidados
     */
    async getWeeklyPlan() {
        const response = await axios.get(`${API_URL}/weekly-plan/`, {
            headers: this.getAuthHeader()
        });
        return this.extractResults(response.data);
    }

    /**
     * Obtiene el detalle de un plan específico
     * @param {number} planId - ID del plan
     * @returns {Promise<Object>} Detalle del plan con rutina y ejercicios
     */
    async getPlanDetalle(planId) {
        const response = await axios.get(`${API_URL}/weekly-plan/${planId}/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Obtiene todos los ejercicios disponibles
     * @param {string} muscleGroup - Filtro opcional por grupo muscular (ej: CHEST, BACK)
     * @returns {Promise<Array>} Lista de ejercicios
     */
    async getEjercicios(muscleGroup = null) {
        const params = muscleGroup ? { muscle_group: muscleGroup } : {};
        const response = await axios.get(`${API_URL}/exercises/`, {
            headers: this.getAuthHeader(),
            params
        });
        return response.data;
    }

    /**
     * Obtiene todas las rutinas disponibles
     * @returns {Promise<Array>} Lista de rutinas con ejercicios
     */
    async getRutinas() {
        const response = await axios.get(`${API_URL}/routines/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Mapea el número de día a nombre
     * @param {number} dia - Número del día (1-7)
     * @returns {string} Nombre del día
     */
    getDiaNombre(dia) {
        const dias = {
            1: 'Lunes',
            2: 'Martes',
            3: 'Miércoles',
            4: 'Jueves',
            5: 'Viernes',
            6: 'Sábado',
            7: 'Domingo'
        };
        return dias[dia] || 'Desconocido';
    }

    /**
     * Organiza el plan semanal por días
     * @param {Array} planes - Lista de planes
     * @returns {Object} Plan organizado por día
     */
    organizarPorDia(planes) {
        const semana = {};
        for (let i = 1; i <= 7; i++) {
            semana[i] = {
                nombre: this.getDiaNombre(i),
                plan: planes.find(p => p.weekday === i) || null
            };
        }
        return semana;
    }

    extractResults(payload) {
        if (Array.isArray(payload)) {
            return payload;
        }
        return payload?.results || [];
    }

    getMuscleGroupLabel(code) {
        return this.muscleGroupLabels[code] || code || 'Sin grupo';
    }

    getDifficultyLabel(code) {
        return this.difficultyLabels[code] || code || 'Sin nivel';
    }
}

export default new PlanService();
