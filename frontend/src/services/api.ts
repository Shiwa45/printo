// src/services/api.ts
import axios, { AxiosInstance } from 'axios';

// Determine API base URL
const envBase = (process.env.REACT_APP_API_BASE_URL || '').trim();
const defaultBase = '/api/v1'; // same-origin by default (works when frontend is served by Django)
const fallbackDevBase = 'http://localhost:8000/api/v1'; // fallback for separate dev servers
const baseURL = envBase || (window.location.origin.includes('localhost') ? fallbackDevBase : defaultBase);

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token management
export const getToken = (): string | null => {
  return localStorage.getItem('auth_token');
};

export const setToken = (token: string): void => {
  localStorage.setItem('auth_token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('auth_token');
};

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      // Let the app route decide what to do; fallback redirect for now
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Helper to extract data from axios response
export const handleResponse = <T>(response: any): T => response.data as T;

export { api };
export default api;