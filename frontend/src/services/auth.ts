// src/services/auth.ts
import api, { setToken, removeToken } from './api';
import { LoginRequest, RegisterRequest, AuthResponse, User } from '../types/api';

export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login/', credentials);
    setToken(response.data.token);
    return response.data;
  },

  // Register new user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register/', userData);
    setToken(response.data.token);
    return response.data;
  },

  // Logout user
  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout/');
    } finally {
      removeToken();
    }
  },

  // Get current user profile
  getProfile: async (): Promise<User> => {
    const response = await api.get<User>('/auth/profile/');
    return response.data;
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    return !!localStorage.getItem('auth_token');
  },
};

export default authService;