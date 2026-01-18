# VastuWise AI - React Native Mobile App with Authentication

A mobile application for Vastu Shastra analysis built with React Native, TypeScript, Express, Prisma, and PostgreSQL. Features complete user authentication with email/password and Google OAuth, persistent login state, and a custom drawer navigation menu.

## 🚀 Quick Start

```bash
# Install backend dependencies
cd backend
npm install

# Install mobile app dependencies
cd ..
npm install

# Setup environment variables
cp backend/.env.example backend/.env
# Update DATABASE_URL and Google OAuth credentials in backend/.env

# Start backend
cd backend
npm run dev

# In a new terminal, start mobile app
npm run android  # or npm run ios
```

## 🎯 Features Implemented

### ✅ Authentication System
- **Email/Password Authentication** - Secure signup and login with validation
- **Google OAuth Integration** - Configured with OAuth 2.0 credentials (in progress)
- **JWT Token Management** - Secure token-based session handling
- **Password Security** - bcrypt hashing with salt rounds (10)
- **Token Storage** - AsyncStorage for persistent sessions across app restarts
- **Persistent Login** - User data and token automatically restored on app launch

### ✅ Screens
1. **LoginScreen** - Email/password authentication with validation, API integration, links to SignUp
2. **SignUpScreen** - User registration with email, password, name fields, real-time validation
3. **WelcomeScreen** - Onboarding page with feature grid, menu button (☰), and smooth animations
4. **CustomDrawer** - Side menu with user profile (avatar, name, email), menu items (Home, Dashboard, Profile, Learn Vastu, Settings), and logout button
5. **DashboardScreen** - Protected screen template for post-authentication content
6. **ProfileFormScreen** - User profile management form template

### ✅ Backend API (Node.js + Express + Prisma)
- **RESTful API** - Complete authentication endpoints (signup, login, profile management)
- **PostgreSQL Database** - Prisma ORM with type safety, automatically migrated
- **Google OAuth** - Passport.js integration configured and ready for testing
- **JWT Authentication** - Secure token-based auth with JWT signing and verification
- **Input Validation** - express-validator middleware for email, password, and name fields
- **Error Handling** - Comprehensive error responses with proper HTTP status codes
- **Database Models** - User (with email, password, name, googleId, profile fields) and VastuAnalysis tables

### ✅ Reusable Components
- `CustomButton` - Primary, secondary, and outline variants with loading/disabled states
- `CustomTextInput` - Labeled input with validation, password toggle, and error display
- `CustomCard` - Glass morphism and solid card variants with icon support
- `CustomDrawer` - Custom Modal-based drawer with animated slide transitions and user profile display

### ✅ Theme System
- **Colors** - Centralized color palette with primary (#db7706)
- **Typography** - Font families, sizes, weights, and line heights
- **Spacing** - Consistent spacing scale and border radius system

### ✅ Services & Utilities
- **AuthService** - API call management
- **StorageService** - Token and user data persistence
- **Google Auth Util** - OAuth flow handling
- **API Config** - Centralized endpoint configuration

## 📂 Project Structure

```
Vastu-Analyzer-mad/
├── backend/                    # Backend API Server
│   ├── prisma/
│   │   └── schema.prisma      # Database schema
│   ├── src/
│   │   ├── config/            # Database & OAuth config
│   │   ├── middleware/        # Auth & error middleware
│   │   ├── routes/            # API routes
│   │   ├── utils/             # JWT & password utilities
│   │   └── index.ts           # Server entry
│   ├── .env.example           # Environment template
│   └── package.json
│
├── src/
│   ├── screens/               # All screens
│   │   ├── LoginScreen.tsx    # ✅ Email/password auth, API integrated
│   │   ├── SignUpScreen.tsx   # ✅ User registration with validation
│   │   ├── WelcomeScreen.tsx  # ✅ Onboarding with feature grid and menu button
│   │   ├── DashboardScreen.tsx # ✅ Protected dashboard template
│   │   └── ProfileFormScreen.tsx # ✅ Profile management template
│   ├── components/            # Reusable components
│   │   ├── CustomButton.tsx
│   │   ├── CustomTextInput.tsx
│   │   ├── CustomCard.tsx
│   │   └── CustomDrawer.tsx   # ✅ NEW - Modal-based side menu
│   ├── services/              # ✅ API services and storage
│   │   ├── storage.service.ts # ✅ AsyncStorage for token/user data
│   │   └── auth.service.ts
│   ├── config/                # ✅ API configuration
│   ├── utils/                 # ✅ Helper functions
│   └── theme/                 # Design system
│
├── QUICK_START.md             # 🚀 Start here!
├── AUTHENTICATION_GUIDE.md    # Auth implementation details
├── MOBILE_SETUP.md            # Mobile app setup
├── backend/README.md          # Backend setup guide
├── setup.bat / setup.sh       # Automated setup scripts
└── package.json
```

## 📚 Documentation

- **[QUICK_START.md](./QUICK_START.md)** - Get up and running in 5 minutes
- **[AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md)** - Complete auth implementation
- **[backend/README.md](./backend/README.md)** - Backend setup and deployment
- **[MOBILE_SETUP.md](./MOBILE_SETUP.md)** - Mobile app configuration

## 🔐 Authentication Flow

1. **Sign Up**: User creates account with email/password → validation → API call to `/api/auth/signup` → token received → stored in AsyncStorage
2. **Login**: User enters credentials → validation → API call to `/api/auth/login` → JWT token received → user data stored → navigates to Welcome screen
3. **Persistent Login**: App checks AsyncStorage on launch → if token exists, user automatically logged in → skips authentication screens
4. **Token Storage**: JWT token and user data (name, email) saved in AsyncStorage using `storage.service.ts`
5. **Drawer Menu**: After successful login, hamburger menu (☰) displays on Welcome screen → opens custom drawer → shows user profile and menu items → logout clears AsyncStorage
6. **Session Management**: Token sent with protected API requests, logout clears stored credentials

## 🛠️ Tech Stack

### Frontend (Mobile)
- React Native 0.83.1
- TypeScript
- AsyncStorage (token persistence)
- Expo Web Browser & Auth Session (OAuth)

### Backend (API)
- Node.js + Express
- Prisma ORM
- PostgreSQL
- Passport.js (Google OAuth)
- JWT (jsonwebtoken)
- bcryptjs (password hashing)

## 📋 API Endpoints

# Authentication
POST   /api/auth/signup          - Create account (email, password, name)
POST   /api/auth/login           - Email/password login (returns JWT token)
GET    /api/auth/google          - Initiate Google OAuth flow
GET    /api/auth/google/callback - OAuth callback handler
GET    /api/auth/verify          - Verify JWT token validity (protected)

# User Profile
GET    /api/user/profile         - Get user profile data (protected)
PUT    /api/user/profile         - Update profile info (protected)

# Vastu Analysis (Future)
POST   /api/analysis/upload      - Upload floor plan/image
GET    /api/analysis/list        - Get user's analyses
GET    /api/analysis/:id         - Get analysis detailsd)
PUT    /api/user/profile         - Update profile (protected)
```

# Getting Started

> **Note**: Make sure you have completed the [Set Up Your Environment](https://reactnative.dev/docs/set-up-your-environment) guide before proceeding.

## Quick Setup

### 1. Install Dependencies

```bash
# Backend
cd backend
npm install

# Mobile App
cd ..
npm install
```

### 2. Set Up Database

Use [Supabase](https://supabase.com) (free) or local PostgreSQL:

```bash
# Create backend/.env file
cp backend/.env.example backend/.env

# Update DATABASE_URL in backend/.env
DATABASE_URL="postgresql://user:password@localhost:5432/vastu_analyzer"
```

### 3. Initialize Database

```bash
cd backend
npm run prisma:generate
npm run prisma:migrate
```

### 4. Start Backend

```bash
cd backend
npm run dev
# Server running on http://localhost:3000
```

### 5. Start Mobile App

```bash
# In a new terminal
npm run android  # or npm run ios
```

## Step 1: Start Metro

First, you will need to run **Metro**, the JavaScript build tool for React Native.

To start the Metro dev server, run the following command from the root of your React Native project:

```sh
# Using npm
npm start

# OR using Yarn
yarn start
```

## Step 2: Build and run your app

With Metro running, open a new terminal window/pane from the root of your React Native project, and use one of the following commands to build and run your Android or iOS app:

### Android

```sh
# Using npm
npm run android

# OR using Yarn
yarn android
```

### iOS

For iOS, remember to install CocoaPods dependencies (this only needs to be run on first clone or after updating native deps).

The first time you create a new project, run the Ruby bundler to install CocoaPods itself:

```sh
bundle install
```

Then, and every time you update your native dependencies, run:

```sh
bundle exec pod install
```

For more information, please visit [CocoaPods Getting Started guide](https://guides.cocoapods.org/using/getting-started.html).

```sh
# Using npm
npm run ios

# OR using Yarn
yarn ios
```

If everything is set up correctly, you should see your new app running in the Android Emulator, iOS Simulator, or your connected device.

This is one way to run your app — you can also build it directly from Android Studio or Xcode.

## Step 3: Modify your app

Now that you have successfully run the app, let's make changes!

Open `App.tsx` in your text editor of choice and make some changes. When you save, your app will automatically update and reflect these changes — this is powered by [Fast Refresh](https://reactnative.dev/docs/fast-refresh).

When you want to forcefully reload, for example to reset the state of your app, you can perform a full reload:

- **Android**: Press the <kbd>R</kbd> key twice or select **"Reload"** from the **Dev Menu**, accessed via <kbd>Ctrl</kbd> + <kbd>M</kbd> (Windows/Linux) or <kbd>Cmd ⌘</kbd> + <kbd>M</kbd> (macOS).
- **iOS**: Press <kbd>R</kbd> in iOS Simulator.

## Congratulations! :tada:

You've successfully run and modified your React Native App. :partying_face:

### Now what?

- If you want to add this new React Native code to an existing application, check out the [Integration guide](https://reactnative.dev/docs/integration-with-existing-apps).
- If you're curious to learn more about React Native, check out the [docs](https://reactnative.dev/docs/getting-started).

# Troubleshooting

If you're having issues getting the above steps to work, see the [Troubleshooting](https://reactnative.dev/docs/troubleshooting) page.

# Learn More

To learn more about React Native, take a look at the following resources:

- [React Native Website](https://reactnative.dev) - learn more about React Native.
- [Getting Started](https://reactnative.dev/docs/environment-setup) - an **overview** of React Native and how setup your environment.
- [Learn the Basics](https://reactnative.dev/docs/getting-started) - a **guided tour** of the React Native **basics**.
- [Blog](https://reactnative.dev/blog) - read the latest official React Native **Blog** posts.
- [`@facebook/react-native`](https://github.com/facebook/react-native) - the Open Source; GitHub **repository** for React Native.
