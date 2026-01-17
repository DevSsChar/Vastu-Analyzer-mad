# VastuWise AI - Quick Start Guide

Complete authentication system with Login/SignUp screens, Email/Password authentication, Google OAuth, and Prisma with PostgreSQL.

## 🚀 Quick Start (5 minutes)

### Step 1: Install Backend Dependencies

```bash
cd backend
npm install
```

### Step 2: Set Up Database

**Option A: Using Supabase (Recommended - Free & Easy)**

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Create a new project
3. Copy the "Connection string" from Settings > Database
4. It looks like: `postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres`

**Option B: Local PostgreSQL**

```bash
# Install PostgreSQL, then create database:
psql -U postgres
CREATE DATABASE vastu_analyzer;
\q
```

### Step 3: Configure Backend

```bash
cd backend
cp .env.example .env
```

Edit `.env` and update:
```env
DATABASE_URL="your-database-url-here"
JWT_SECRET="your-random-secret-at-least-32-chars"
```

### Step 4: Initialize Database

```bash
npm run prisma:generate
npm run prisma:migrate
```

### Step 5: Start Backend

```bash
npm run dev
```

You should see: `🚀 Server running on http://localhost:3000`

### Step 6: Install Mobile App Dependencies

Open a new terminal:

```bash
cd ..  # Go back to root
npm install
```

### Step 7: Configure Mobile App

Update `src/config/api.config.ts`:

```typescript
export const API_BASE_URL = __DEV__ 
  ? 'http://10.0.2.2:3000/api'  // For Android Emulator
  // ? 'http://localhost:3000/api'  // For iOS Simulator
  // ? 'http://YOUR_IP:3000/api'  // For Physical Device
  : 'https://your-production-api.com/api';
```

### Step 8: Run Mobile App

**Android:**
```bash
npm run android
```

**iOS:**
```bash
npm run ios
```

## 📱 Features Implemented

### ✅ Screens
- **LoginScreen**: Email/password login + Google OAuth button
- **SignUpScreen**: Registration with validation + Google OAuth
- **WelcomeScreen**: Landing page
- **DashboardScreen**: Protected screen (after login)
- **ProfileFormScreen**: User profile management

### ✅ Backend API
- **POST /api/auth/signup** - Create account
- **POST /api/auth/login** - Email/password login
- **GET /api/auth/google** - Google OAuth flow
- **GET /api/auth/verify** - Verify JWT token
- **GET /api/user/profile** - Get user profile
- **PUT /api/user/profile** - Update profile

### ✅ Security
- Password hashing with bcrypt (10 rounds)
- JWT token authentication (7-day expiry)
- Secure session management
- CORS protection
- Input validation

### ✅ Database
- PostgreSQL with Prisma ORM
- User model with OAuth support
- Migration system
- Type-safe queries

## 🧪 Test the System

### 1. Test Backend (without mobile app)

```bash
# Health check
curl http://localhost:3000/health

# Create account
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 2. Test Mobile App

1. Open the app
2. Navigate to Sign Up screen
3. Enter email, password, name
4. Click "Create Account"
5. Verify token is stored (check console logs)
6. Navigate to Login screen
7. Login with same credentials
8. Should redirect to Dashboard

## 📂 Project Structure

```
Vastu-Analyzer-mad/
├── backend/                     # Backend API server
│   ├── prisma/
│   │   └── schema.prisma       # Database schema
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.ts     # Prisma client
│   │   │   └── passport.config.ts  # Google OAuth
│   │   ├── middleware/
│   │   │   ├── auth.middleware.ts  # JWT verification
│   │   │   └── error.middleware.ts
│   │   ├── routes/
│   │   │   ├── auth.routes.ts  # Auth endpoints
│   │   │   └── user.routes.ts  # User endpoints
│   │   ├── utils/
│   │   │   ├── jwt.util.ts     # Token management
│   │   │   └── password.util.ts # Password hashing
│   │   └── index.ts            # Server entry
│   ├── .env.example
│   ├── package.json
│   └── tsconfig.json
│
├── src/
│   ├── screens/
│   │   ├── LoginScreen.tsx     # ✅ Login with API
│   │   ├── SignUpScreen.tsx    # ✅ NEW - Sign up
│   │   ├── WelcomeScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   └── ProfileFormScreen.tsx
│   ├── services/
│   │   ├── auth.service.ts     # ✅ API calls
│   │   └── storage.service.ts  # ✅ Token storage
│   ├── config/
│   │   └── api.config.ts       # ✅ API endpoints
│   ├── utils/
│   │   └── googleAuth.util.ts  # ✅ Google OAuth
│   └── theme/
│       ├── colors.ts
│       ├── typography.ts
│       └── spacing.ts
│
├── AUTHENTICATION_GUIDE.md      # Detailed auth docs
├── MOBILE_SETUP.md             # Mobile setup guide
└── backend/README.md           # Backend setup guide
```

## 🔐 Google OAuth Setup (Optional)

### Get Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 Client ID:
   - **Application type**: Web application
   - **Authorized redirect URIs**: 
     - `http://localhost:3000/auth/google/callback`
     - `vastuwiseai://auth/callback` (for mobile)
5. Copy Client ID and Secret to `backend/.env`:

```env
GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="xxx"
```

### Configure Mobile App

Update `src/utils/googleAuth.util.ts`:
```typescript
const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID';
```

## 🛠️ Common Issues & Solutions

### Backend won't start

```bash
# Check if port 3000 is in use
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Mac/Linux

# Kill the process or change PORT in .env
```

### Database connection error

- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Test connection: `npx prisma studio`

### Mobile app can't connect to backend

**For Android Emulator**: Use `http://10.0.2.2:3000/api`
**For iOS Simulator**: Use `http://localhost:3000/api`
**For Physical Device**: Use your computer's IP (e.g., `http://192.168.1.100:3000/api`)

Find your IP:
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

### AsyncStorage not found

```bash
npm install @react-native-async-storage/async-storage
cd ios && pod install  # iOS only
```

## 📋 Next Steps

### Immediate Tasks
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Run Prisma migrations
- [ ] Test backend API
- [ ] Test mobile app authentication
- [ ] Configure Google OAuth (optional)

### Future Enhancements
- [ ] Implement navigation (React Navigation)
- [ ] Add loading states and error boundaries
- [ ] Implement token refresh mechanism
- [ ] Add email verification
- [ ] Implement password reset
- [ ] Add biometric authentication
- [ ] Create profile update UI
- [ ] Implement Vastu analysis features
- [ ] Add floor plan upload
- [ ] Integrate AI analysis

## 📚 Documentation

- **[AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md)** - Complete auth implementation details
- **[backend/README.md](./backend/README.md)** - Backend setup and deployment
- **[MOBILE_SETUP.md](./MOBILE_SETUP.md)** - Mobile app configuration

## 🆘 Support

If you encounter issues:

1. Check the console logs (both backend and mobile)
2. Verify all environment variables are set
3. Ensure PostgreSQL is running
4. Test backend API with curl/Postman
5. Check network configuration for mobile app

## 🎉 Success!

If you can:
- ✅ Start the backend server
- ✅ Create an account from mobile app
- ✅ Login with email/password
- ✅ See authentication token in logs

**Congratulations! Your authentication system is working!**

---

**Built with**: React Native, Express, Prisma, PostgreSQL, JWT, Passport.js
