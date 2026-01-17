# VastuWise AI - Mobile App Setup Guide

## Prerequisites

- Node.js (v18 or higher)
- React Native development environment
- Android Studio (for Android) or Xcode (for iOS)
- Backend server running (see backend/README.md)

## Step 1: Install Dependencies

```bash
# Install mobile app dependencies
npm install

# For iOS only (Mac required)
cd ios
pod install
cd ..
```

## Step 2: Configure API Endpoint

Update the API URL in `src/config/api.config.ts`:

```typescript
export const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:3000/api'  // Android Emulator
  // ? 'http://localhost:3000/api'  // iOS Simulator
  : 'https://your-production-api.com/api';
```

### Network Configuration for Different Environments:

- **iOS Simulator**: Use `http://localhost:3000/api`
- **Android Emulator**: Use `http://10.0.2.2:3000/api`
- **Physical Device**: Use your computer's IP (e.g., `http://192.168.1.100:3000/api`)

## Step 3: Configure Google OAuth (Optional)

### For Expo (Managed Workflow)

1. Install Expo dependencies:

```bash
npx expo install expo-web-browser expo-auth-session
```

2. Update `app.json`:

```json
{
  "expo": {
    "scheme": "vastuwiseai",
    "android": {
      "package": "com.vastuwiseai"
    },
    "ios": {
      "bundleIdentifier": "com.vastuwiseai"
    }
  }
}
```

3. Update Google OAuth credentials in Google Cloud Console:
   - Add redirect URI: `vastuwiseai://auth/callback`

### For Bare React Native

Install community OAuth library:

```bash
npm install @react-native-google-signin/google-signin
```

Follow setup instructions: https://github.com/react-native-google-signin/google-signin

## Step 4: Run the Application

### Start Metro Bundler

```bash
npm start
```

### Run on Android

```bash
npm run android
```

### Run on iOS

```bash
npm run ios
```

## Authentication Flow

### Email/Password Authentication

1. **Sign Up**: 
   - Navigate to SignUpScreen
   - Enter name, email, and password
   - Click "Create Account"
   - Token is stored in AsyncStorage
   - Redirect to Dashboard

2. **Login**:
   - Navigate to LoginScreen
   - Enter email and password
   - Click "Login"
   - Token is stored in AsyncStorage
   - Redirect to Dashboard

### Google OAuth

1. Click "Sign in with Google" button
2. Browser opens with Google login
3. User authenticates with Google
4. Callback returns token and user data
5. Token is stored in AsyncStorage
6. Redirect to Dashboard

## Available Screens

- **WelcomeScreen**: Initial landing screen
- **LoginScreen**: Email/password login + Google OAuth
- **SignUpScreen**: Email/password registration + Google OAuth
- **DashboardScreen**: Main app interface (after login)
- **ProfileFormScreen**: User profile management

## Token Management

Tokens are automatically stored using AsyncStorage:

```typescript
import storageService from './services/storage.service';

// Store token after login
await storageService.setToken(token);

// Get token for API calls
const token = await storageService.getToken();

// Remove token on logout
await storageService.clearAll();
```

## API Service Usage

Use the auth service for API calls:

```typescript
import authService from './services/auth.service';

// Login
const response = await authService.login({
  email: 'user@example.com',
  password: 'password123'
});

// Sign Up
const response = await authService.signup({
  name: 'John Doe',
  email: 'john@example.com',
  password: 'password123'
});

// Get Profile (requires token)
const token = await storageService.getToken();
const profile = await authService.getProfile(token);
```

## Troubleshooting

### Cannot connect to backend

1. Check if backend is running: `curl http://localhost:3000/health`
2. Verify API_BASE_URL in `api.config.ts`
3. For Android emulator, use `10.0.2.2` instead of `localhost`
4. For physical devices, use your computer's IP address

### AsyncStorage errors

Make sure `@react-native-async-storage/async-storage` is installed:

```bash
npm install @react-native-async-storage/async-storage
cd ios && pod install  # iOS only
```

### Google OAuth not working

1. Verify redirect URI in Google Cloud Console
2. Check app scheme in `app.json`
3. Ensure `expo-web-browser` and `expo-auth-session` are installed
4. Test backend OAuth endpoint: `http://localhost:3000/api/auth/google`

## Production Checklist

- [ ] Update API_BASE_URL to production URL
- [ ] Configure proper Google OAuth credentials
- [ ] Enable code obfuscation
- [ ] Add error tracking (Sentry, Bugsnag)
- [ ] Implement proper token refresh
- [ ] Add biometric authentication
- [ ] Set up deep linking
- [ ] Configure app icons and splash screen
- [ ] Test on multiple devices
- [ ] Implement offline support

## Next Steps

1. Implement navigation between screens
2. Add loading states and error handling
3. Create profile update functionality
4. Integrate Vastu analysis features
5. Add image upload for floor plans
6. Implement AI analysis integration
