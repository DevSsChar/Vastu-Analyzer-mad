/**
 * API Configuration
 * Central configuration for API endpoints and settings
 */

// Change this to your actual backend URL when deployed
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:3000/api'
  : 'https://your-production-api.com/api';

export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: '/auth/login',
  SIGNUP: '/auth/signup',
  GOOGLE_AUTH: '/auth/google',
  VERIFY_TOKEN: '/auth/verify',
  
  // User endpoints
  GET_PROFILE: '/user/profile',
  UPDATE_PROFILE: '/user/profile',
};

export const API_CONFIG = {
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};
