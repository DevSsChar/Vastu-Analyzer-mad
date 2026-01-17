/**
 * Storage Utility
 * Handles local storage for authentication tokens and user data
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

const STORAGE_KEYS = {
  AUTH_TOKEN: '@vastu_auth_token',
  USER_DATA: '@vastu_user_data',
};

class StorageService {
  /**
   * Store authentication token
   */
  async setToken(token: string): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
    } catch (error) {
      console.error('Error storing token:', error);
      throw error;
    }
  }

  /**
   * Get authentication token
   */
  async getToken(): Promise<string | null> {
    try {
      return await AsyncStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }

  /**
   * Remove authentication token
   */
  async removeToken(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
    } catch (error) {
      console.error('Error removing token:', error);
      throw error;
    }
  }

  /**
   * Store user data
   */
  async setUserData(userData: any): Promise<void> {
    try {
      await AsyncStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));
    } catch (error) {
      console.error('Error storing user data:', error);
      throw error;
    }
  }

  /**
   * Get user data
   */
  async getUserData(): Promise<any | null> {
    try {
      const data = await AsyncStorage.getItem(STORAGE_KEYS.USER_DATA);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  }

  /**
   * Remove user data
   */
  async removeUserData(): Promise<void> {
    try {
      await AsyncStorage.removeItem(STORAGE_KEYS.USER_DATA);
    } catch (error) {
      console.error('Error removing user data:', error);
      throw error;
    }
  }

  /**
   * Clear all stored data (logout)
   */
  async clearAll(): Promise<void> {
    try {
      await AsyncStorage.multiRemove([
        STORAGE_KEYS.AUTH_TOKEN,
        STORAGE_KEYS.USER_DATA,
      ]);
    } catch (error) {
      console.error('Error clearing storage:', error);
      throw error;
    }
  }
}

const storageService = new StorageService();

export const setToken = (token: string) => storageService.setToken(token);
export const getToken = () => storageService.getToken();
export const removeToken = () => storageService.removeToken();
export const setUserData = (userData: any) => storageService.setUserData(userData);
export const getUserData = () => storageService.getUserData();
export const removeUserData = () => storageService.removeUserData();
export const clearStorage = () => storageService.clearAll();

export default storageService;
