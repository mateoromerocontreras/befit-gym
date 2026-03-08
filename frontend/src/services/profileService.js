import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

class ProfileService {
    /**
     * Obtiene el header de autorización con el token JWT
     */
    getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    /**
     * Obtiene el perfil completo del usuario autenticado
     * @returns {Promise<Object>} Datos del usuario
     */
    async getUserProfile() {
        try {
            const response = await axios.get(`${API_URL}/profile/`, {
                headers: this.getAuthHeader()
            });
            return response.data;
        } catch (error) {
            console.error('Error fetching user profile:', error);
            throw error;
        }
    }

    /**
     * Actualiza el perfil del usuario
     * @param {Object} data - Datos a actualizar
     * @returns {Promise<Object>} Usuario actualizado
     */
    async updateUserProfile(data) {
        try {
            const response = await axios.patch(`${API_URL}/profile/`, data, {
                headers: this.getAuthHeader()
            });
            return response.data;
        } catch (error) {
            console.error('Error updating profile:', error);
            throw error;
        }
    }

    /**
     * Genera una rutina con IA
     * @param {number} diasSemana - Número de días de entrenamiento
     * @param {string} nombreRutina - Nombre personalizado (opcional)
     * @returns {Promise<Object>} Resultado de la generación
     */
    async generateRoutine(diasSemana = 3, nombreRutina = null) {
        try {
            const payload = { dias_semana: diasSemana };
            if (nombreRutina) {
                payload.nombre_rutina = nombreRutina;
            }

            const response = await axios.post(`${API_URL}/generate-routine/`, payload, {
                headers: this.getAuthHeader()
            });
            return response.data;
        } catch (error) {
            console.error('Error generating routine:', error);
            throw error;
        }
    }
}

export default new ProfileService();
