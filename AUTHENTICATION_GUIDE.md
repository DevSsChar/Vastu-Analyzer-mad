# Authentication Implementation Guide

## Overview

This guide explains the complete authentication system for VastuWise AI, including:
- Email/password authentication
- Google OAuth integration
- JWT token management
- Secure password hashing
- User profile management

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  React Native   │   HTTP  │   Express API   │   ORM   │   PostgreSQL    │
│  Mobile App     │ ◄─────► │   + Passport    │ ◄─────► │   Database      │
└─────────────────┘         └─────────────────┘         └─────────────────┘
       │                            │
       │                            │
       ▼                            ▼
┌─────────────────┐         ┌─────────────────┐
│  AsyncStorage   │         │   Prisma ORM    │
│  (Token Cache)  │         │   (Type Safety) │
└─────────────────┘         └─────────────────┘
```

## Database Schema

### User Model

```prisma
model User {
  id             String    @id @default(uuid())
  email          String    @unique
  password       String?   // Null for OAuth users
  name           String?
  googleId       String?   @unique
  profilePicture String?
  phoneNumber    String?
  address        String?
  dateOfBirth    DateTime?
  createdAt      DateTime  @default(now())
  updatedAt      DateTime  @updatedAt
  
  analyses       VastuAnalysis[]
}
```

## Backend API Endpoints

### 1. Sign Up (Email/Password)

**Endpoint**: `POST /api/auth/signup`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "John Doe"
}
```

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "createdAt": "2024-01-17T..."
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Validation**:
- Email must be valid format
- Password minimum 6 characters
- Email must be unique

### 2. Login (Email/Password)

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "profilePicture": null
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 3. Google OAuth

**Initiate Flow**: `GET /api/auth/google`
- Redirects to Google login page

**Callback**: `GET /api/auth/google/callback`
- Receives Google auth code
- Creates or updates user
- Redirects to mobile app with token

**Redirect URL**: `vastuwiseai://auth/callback?token=JWT_TOKEN&user=USER_DATA`

### 4. Verify Token

**Endpoint**: `GET /api/auth/verify`

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response** (200 OK):
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "profilePicture": null,
    "phoneNumber": null,
    "address": null,
    "dateOfBirth": null
  }
}
```

### 5. Get Profile

**Endpoint**: `GET /api/user/profile`

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response**: Same as verify token

### 6. Update Profile

**Endpoint**: `PUT /api/user/profile`

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Request Body**:
```json
{
  "name": "John Doe Updated",
  "phoneNumber": "+1234567890",
  "address": "123 Main St, City, Country",
  "dateOfBirth": "1990-01-15"
}
```

## Frontend Integration

### 1. Login Screen Implementation

```typescript
import authService from './services/auth.service';
import storageService from './services/storage.service';

const handleLogin = async () => {
  try {
    const response = await authService.login({
      email: email.trim().toLowerCase(),
      password
    });
    
    // Store token
    await storageService.setToken(response.token);
    await storageService.setUserData(response.user);
    
    // Navigate to dashboard
    navigation.navigate('Dashboard');
  } catch (error) {
    Alert.alert('Error', error.message);
  }
};
```

### 2. Sign Up Screen Implementation

```typescript
const handleSignUp = async () => {
  try {
    const response = await authService.signup({
      name: name.trim(),
      email: email.trim().toLowerCase(),
      password
    });
    
    await storageService.setToken(response.token);
    await storageService.setUserData(response.user);
    
    navigation.navigate('Dashboard');
  } catch (error) {
    Alert.alert('Error', error.message);
  }
};
```

### 3. Google OAuth Implementation

```typescript
import { signInWithGoogle } from './utils/googleAuth.util';

const handleGoogleSignIn = async () => {
  try {
    const result = await signInWithGoogle();
    
    if (result.success) {
      await storageService.setToken(result.token);
      await storageService.setUserData(result.user);
      
      navigation.navigate('Dashboard');
    } else {
      Alert.alert('Error', result.error);
    }
  } catch (error) {
    Alert.alert('Error', 'Google sign-in failed');
  }
};
```

### 4. Protected API Calls

```typescript
const getProfile = async () => {
  try {
    const token = await storageService.getToken();
    
    if (!token) {
      navigation.navigate('Login');
      return;
    }
    
    const response = await authService.getProfile(token);
    setUserProfile(response.user);
  } catch (error) {
    // Token invalid or expired
    await storageService.clearAll();
    navigation.navigate('Login');
  }
};
```

## Security Features

### 1. Password Hashing

```typescript
// Backend: utils/password.util.ts
import bcrypt from 'bcryptjs';

const hashPassword = async (password: string): Promise<string> => {
  return await bcrypt.hash(password, 10);
};

const comparePassword = async (
  password: string,
  hashedPassword: string
): Promise<boolean> => {
  return await bcrypt.compare(password, hashedPassword);
};
```

### 2. JWT Token Generation

```typescript
// Backend: utils/jwt.util.ts
import jwt from 'jsonwebtoken';

const generateToken = (userId: string): string => {
  return jwt.sign(
    { userId },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
};

const verifyToken = (token: string): any => {
  return jwt.verify(token, process.env.JWT_SECRET);
};
```

### 3. Authentication Middleware

```typescript
// Backend: middleware/auth.middleware.ts
export const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  
  const decoded = verifyToken(token);
  const user = await prisma.user.findUnique({
    where: { id: decoded.userId }
  });
  
  req.user = user;
  next();
};
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL="postgresql://user:password@localhost:5432/vastu_analyzer"
JWT_SECRET="your-secret-key-min-32-characters-long"
JWT_EXPIRES_IN="7d"
GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="xxx"
GOOGLE_CALLBACK_URL="http://localhost:3000/auth/google/callback"
PORT=3000
NODE_ENV="development"
FRONTEND_URL="http://localhost:8081"
ALLOWED_ORIGINS="http://localhost:8081,http://localhost:19006"
```

### Mobile App (api.config.ts)

```typescript
export const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:3000/api'  // Android Emulator
  : 'https://api.vastuwiseai.com/api';
```

## Error Handling

### Backend Error Responses

```json
{
  "error": "Invalid email or password"
}
```

```json
{
  "errors": [
    {
      "field": "email",
      "message": "Valid email is required"
    }
  ]
}
```

### Frontend Error Handling

```typescript
try {
  const response = await authService.login(credentials);
} catch (error) {
  if (error.message === 'Invalid email or password') {
    Alert.alert('Login Failed', 'Please check your credentials');
  } else {
    Alert.alert('Error', 'Something went wrong');
  }
}
```

## Testing

### Test User Creation

```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User"
  }'
```

### Test Login

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

### Test Protected Endpoint

```bash
curl -X GET http://localhost:3000/api/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Production Considerations

1. **Use HTTPS**: Always use SSL/TLS in production
2. **Secure JWT Secret**: Use a strong, random secret (min 32 characters)
3. **Token Expiration**: Implement refresh tokens for better security
4. **Rate Limiting**: Add rate limiting to prevent brute force attacks
5. **Input Validation**: Validate all user inputs
6. **CORS**: Configure proper CORS origins
7. **Logging**: Implement comprehensive logging
8. **Monitoring**: Set up error tracking and monitoring

## Next Steps

1. Implement token refresh mechanism
2. Add email verification
3. Implement password reset flow
4. Add two-factor authentication (2FA)
5. Implement session management
6. Add social login providers (Facebook, Apple)
