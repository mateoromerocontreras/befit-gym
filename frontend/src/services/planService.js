import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

class PlanService {
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
        const response = await axios.get(`${API_URL}/plan-semanal/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Obtiene el detalle de un plan específico
     * @param {number} planId - ID del plan
     * @returns {Promise<Object>} Detalle del plan con rutina y ejercicios
     */
    async getPlanDetalle(planId) {
        const response = await axios.get(`${API_URL}/plan-semanal/${planId}/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Obtiene todos los ejercicios disponibles
     * @param {string} grupoMuscular - Filtro opcional por grupo muscular
     * @returns {Promise<Array>} Lista de ejercicios
     */
    async getEjercicios(grupoMuscular = null) {
        const params = grupoMuscular ? { grupo_muscular: grupoMuscular } : {};
        const response = await axios.get(`${API_URL}/ejercicios/`, {
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
        const response = await axios.get(`${API_URL}/rutinas/`, {
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
                plan: planes.find(p => p.dia_semana === i) || null
            };
        }
        return semana;
    }
}

export default new PlanService();
