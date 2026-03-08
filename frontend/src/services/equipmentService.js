import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

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
     * @param {string} categoria - Filtro opcional por categoría
     * @returns {Promise<Array>} Lista de equipamientos
     */
    async getAllEquipment(categoria = null) {
        try {
            const params = categoria ? { categoria } : {};
            const response = await axios.get(`${API_URL}/equipamientos/`, {
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
     * @param {string} categoria - Categoría a filtrar
     * @returns {Promise<Array>} Lista filtrada de equipamientos
     */
    async getEquipmentByCategory(categoria) {
        return this.getAllEquipment(categoria);
    }

    /**
     * Obtiene un equipamiento específico
     * @param {number} id - ID del equipamiento
     * @returns {Promise<Object>} Datos del equipamiento
     */
    async getEquipmentById(id) {
        const response = await axios.get(`${API_URL}/equipamientos/${id}/`, {
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
            return response.data.equipment_ids || response.data.equipamientos || [];
        } catch (error) {
            console.error('Error fetching user equipment selection:', error);
            return [];
        }
    }

    /**
     * Mapea categorías a etiquetas legibles
     * @param {string} categoria - Categoría en formato UPPERCASE_SNAKE_CASE
     * @returns {string} Etiqueta legible
     */
    getCategoryLabel(categoria) {
        const labels = {
            PESO_LIBRE: 'Peso Libre',
            MAQUINA: 'Máquinas',
            CARDIO: 'Cardio',
            ACCESORIO: 'Accesorios',
            CALISTENIA: 'Calistenia'
        };
        return labels[categoria] || categoria;
    }

    /**
     * Obtiene todas las categorías disponibles
     * @returns {Array<string>} Array de categorías
     */
    getCategories() {
        return ['PESO_LIBRE', 'MAQUINA', 'CARDIO', 'ACCESORIO', 'CALISTENIA'];
    }
}

export default new EquipmentService();
