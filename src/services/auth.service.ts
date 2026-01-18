/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { API_BASE_URL, API_ENDPOINTS, API_CONFIG } from '../config/api.config';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignUpData {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  user: {
    id: string;
    email: string;
    name: string | null;
    profilePicture: string | null;
  };
  token: string;
}

class AuthService {
  private baseUrl = API_BASE_URL;

  /**
   * Login with email and password
   */
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.LOGIN}`, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify(credentials),
      });

      const data: any = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Login failed');
      }

      return data as AuthResponse;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Sign up with email and password
   */
  async signup(signupData: SignUpData): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.SIGNUP}`, {
        method: 'POST',
        headers: API_CONFIG.headers,
        body: JSON.stringify(signupData),
      });

      const data: any = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Sign up failed');
      }

      return data as AuthResponse;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Verify authentication token
   */
  async verifyToken(token: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.VERIFY_TOKEN}`, {
        method: 'GET',
        headers: {
          ...API_CONFIG.headers,
          'Authorization': `Bearer ${token}`,
        },
      });

      const data: any = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Token verification failed');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Get user profile
   */
  async getProfile(token: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.GET_PROFILE}`, {
        method: 'GET',
        headers: {
          ...API_CONFIG.headers,
          'Authorization': `Bearer ${token}`,
        },
      });

      const data: any = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get profile');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(token: string, profileData: any): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}${API_ENDPOINTS.UPDATE_PROFILE}`, {
        method: 'PUT',
        headers: {
          ...API_CONFIG.headers,
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profileData),
      });

      const data: any = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to update profile');
      }

      return data;
    } catch (error) {
      throw error;
    }
  }
}

export default new AuthService();
