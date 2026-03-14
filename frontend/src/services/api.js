import axios from 'axios';

const apiClient = axios.create({
    baseURL: (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/auth').replace(/\/$/, ''),
});

// You can also add interceptors here to automatically add auth tokens to requests.

export default apiClient;