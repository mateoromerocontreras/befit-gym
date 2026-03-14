import axios from 'axios';

const API_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/auth').replace(/\/$/, '');

class EquipmentService {
    /**
     * Obtiene el header de autorización con el token JWT
     */
    getAuthHeader() {
        const token = localStorage.getItem('access_token');
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    /**
     * Obtiene todos los equipamientos disponibles
     * @param {string} category - Filtro opcional por categoría (ej: WEIGHTS, MACHINE)
     * @returns {Promise<Array>} Lista de equipamientos
     */
    async getAllEquipment(category = null) {
        try {
            const params = category ? { category } : {};
            const response = await axios.get(`${API_URL}/equipment/`, {
                headers: this.getAuthHeader(),
                params
            });
            // Si es paginado, extraer results, sino devolver directamente
            return Array.isArray(response.data) ? response.data : response.data.results || [];
        } catch (error) {
            console.error('Error fetching equipment:', error);
            throw error;
        }
    }

    /**
     * Obtiene equipamiento por categoría
     * @param {string} category - Categoría a filtrar (ej: WEIGHTS, MACHINE)
     * @returns {Promise<Array>} Lista filtrada de equipamientos
     */
    async getEquipmentByCategory(category) {
        return this.getAllEquipment(category);
    }

    /**
     * Obtiene un equipamiento específico
     * @param {number} id - ID del equipamiento
     * @returns {Promise<Object>} Datos del equipamiento
     */
    async getEquipmentById(id) {
        const response = await axios.get(`${API_URL}/equipment/${id}/`, {
            headers: this.getAuthHeader()
        });
        return response.data;
    }

    /**
     * Guarda la selección de equipamientos para un usuario
     * Nota: Este método asume que tienes un endpoint para guardar preferencias
     * Ajusta según tu estructura de backend
     * @param {Array<number>} selectedIds - Array de IDs seleccionados
     * @returns {Promise<Object>} Respuesta del servidor
     */
    async saveEquipmentSelection(selectedIds) {
        try {
            const response = await axios.post(`${API_URL}/user-equipment/`, {
                equipment_ids: selectedIds
            }, {
                headers: this.getAuthHeader()
            });
            return response.data;
        } catch (error) {
            console.error('Error saving equipment selection:', error);
            throw error;
        }
    }

    /**
     * Obtiene la selección de equipamiento guardada del usuario
     * @returns {Promise<Array>} Array de IDs de equipamiento seleccionado
     */
    async getUserEquipmentSelection() {
        try {
            const response = await axios.get(`${API_URL}/user-equipment/`, {
                headers: this.getAuthHeader()
            });
            if (Array.isArray(response.data)) {
                return response.data;
            }
            return response.data.equipment_ids || [];
        } catch (error) {
            console.error('Error fetching user equipment selection:', error);
            return [];
        }
    }

    /**
     * Mapea categorías a etiquetas legibles
     * @param {string} category - Categoría en formato UPPERCASE (ej: WEIGHTS)
     * @returns {string} Etiqueta legible
     */
    getCategoryLabel(category) {
        const labels = {
            WEIGHTS: 'Peso Libre',
            MACHINE: 'Máquinas',
            CARDIO: 'Cardio',
            ACCESSORY: 'Accesorios',
            CALISTHENICS: 'Calistenia',
        };
        return labels[category] || category;
    }

    /**
     * Obtiene todas las categorías disponibles
     * @returns {Array<string>} Array de categorías en inglés
     */
    getCategories() {
        return ['WEIGHTS', 'MACHINE', 'CARDIO', 'ACCESSORY', 'CALISTHENICS'];
    }
}

export default new EquipmentService();
