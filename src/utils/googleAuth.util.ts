/**
 * Google OAuth Helper
 * Handles Google Sign-In for React Native using expo-auth-session
 */

import * as WebBrowser from 'expo-web-browser';
import { makeRedirectUri } from 'expo-auth-session';
import { Platform } from 'react-native';

WebBrowser.maybeCompleteAuthSession();

const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'; // Replace with your Google Client ID
const BACKEND_URL = 'http://localhost:3000';

/**
 * Initiate Google Sign-In
 * Opens a browser for Google OAuth flow
 */
export const signInWithGoogle = async () => {
  try {
    const redirectUri = makeRedirectUri({
      scheme: 'vastuwiseai',
      path: 'auth/callback',
    });

    console.log('Redirect URI:', redirectUri);

    // Open the Google OAuth URL in browser
    const authUrl = `${BACKEND_URL}/api/auth/google`;
    
    const result = await WebBrowser.openAuthSessionAsync(
      authUrl,
      redirectUri
    );

    if (result.type === 'success') {
      // Extract token from URL
      const url = result.url;
      const token = extractTokenFromUrl(url);
      const userData = extractUserDataFromUrl(url);
      
      return {
        success: true,
        token,
        user: userData,
      };
    }

    return {
      success: false,
      error: 'Authentication cancelled',
    };
  } catch (error) {
    console.error('Google Sign-In Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

/**
 * Extract token from callback URL
 */
const extractTokenFromUrl = (url: string): string | null => {
  try {
    const params = new URLSearchParams(url.split('?')[1]);
    return params.get('token');
  } catch (error) {
    console.error('Error extracting token:', error);
    return null;
  }
};

/**
 * Extract user data from callback URL
 */
const extractUserDataFromUrl = (url: string): any | null => {
  try {
    const params = new URLSearchParams(url.split('?')[1]);
    const userDataString = params.get('user');
    return userDataString ? JSON.parse(decodeURIComponent(userDataString)) : null;
  } catch (error) {
    console.error('Error extracting user data:', error);
    return null;
  }
};

/**
 * Alternative: Using expo-google-app-auth for native Google Sign-In
 * Install: expo install expo-google-app-auth
 * 
 * This provides a better user experience with native Google Sign-In
 */
export const signInWithGoogleNative = async () => {
  try {
    // Uncomment and configure when you have Google credentials
    /*
    const config = {
      androidClientId: 'YOUR_ANDROID_CLIENT_ID',
      iosClientId: 'YOUR_IOS_CLIENT_ID',
      webClientId: 'YOUR_WEB_CLIENT_ID',
    };

    const result = await Google.logInAsync(config);

    if (result.type === 'success') {
      // Send the access token to your backend
      const response = await fetch(`${BACKEND_URL}/api/auth/google/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          accessToken: result.accessToken,
        }),
      });

      const data = await response.json();
      return {
        success: true,
        token: data.token,
        user: data.user,
      };
    }
    */

    return {
      success: false,
      error: 'Google Sign-In not configured',
    };
  } catch (error) {
    console.error('Native Google Sign-In Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};
