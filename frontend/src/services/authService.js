import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';

class AuthService {
    async register(dataOrEmail, password, password2) {
        const payload = typeof dataOrEmail === 'object'
            ? dataOrEmail
            : { email: dataOrEmail, password, password2 };

        const response = await axios.post(`${API_URL}/register/`, {
            email: payload.email,
            password: payload.password,
            password2: payload.password2,
            age: payload.age,
            goal: payload.goal,
            level: payload.level
        });
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
    }

    async login(email, password) {
        const response = await axios.post(`${API_URL}/login/`, {
            email,
            password
        });
        if (response.data.access) {
            localStorage.setItem('access_token', response.data.access);
            localStorage.setItem('refresh_token', response.data.refresh);
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response.data;
    }

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    }

    getCurrentUser() {
        const userStr = localStorage.getItem('user');
        if (userStr) return JSON.parse(userStr);
        return null;
    }

    getAccessToken() {
        return localStorage.getItem('access_token');
    }

    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    }

    async refreshToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) return null;

        try {
            const response = await axios.post(`${API_URL}/token/refresh/`, {
                refresh: refreshToken
            });
            if (response.data.access) {
                localStorage.setItem('access_token', response.data.access);
            }
            return response.data.access;
        } catch (error) {
            this.logout();
            return null;
        }
    }
}

export default new AuthService();
