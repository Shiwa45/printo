// src/types/api.ts

// User & Authentication Types
export interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
    company_name?: string;
    avatar?: string;
    gst_number?: string;
    is_verified: boolean;
    date_joined: string;
  }
  
  export interface LoginRequest {
    email: string;
    password: string;
  }
  
  export interface RegisterRequest {
    email: string;
    password: string;
    password_confirm: string;
    first_name: string;
    last_name: string;
    phone?: string;
    company_name?: string;
  }
  
  export interface AuthResponse {
    token: string;
    user: User;
    message: string;
  }
  
  // API Error Types
  export interface ApiError {
    message: string;
    errors?: Record<string, string[]>;
    status?: number;
  }