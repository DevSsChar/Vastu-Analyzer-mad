# VastuWise AI - Backend Setup Guide

This guide will help you set up the backend server with Prisma and PostgreSQL for authentication.

## Prerequisites

- **Node.js** (v18 or higher)
- **PostgreSQL** (v14 or higher)
- **npm** or **yarn**

## Step 1: Install Dependencies

Navigate to the backend folder and install dependencies:

```bash
cd backend
npm install
```

## Step 2: Set Up PostgreSQL Database

### Option A: Local PostgreSQL Installation

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Create a new database:

```sql
CREATE DATABASE vastu_analyzer;
CREATE USER vastu_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE vastu_analyzer TO vastu_user;
```

### Option B: Using Docker

```bash
docker run --name vastu-postgres \
  -e POSTGRES_DB=vastu_analyzer \
  -e POSTGRES_USER=vastu_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:14
```

### Option C: Cloud Database (Recommended for Production)

Use a cloud PostgreSQL service:
- **Supabase** (Free tier available): https://supabase.com
- **Railway**: https://railway.app
- **Neon**: https://neon.tech
- **ElephantSQL**: https://www.elephantsql.com

## Step 3: Configure Environment Variables

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Update `.env` with your configuration:

```env
# Database - Update with your PostgreSQL credentials
DATABASE_URL="postgresql://vastu_user:your_password@localhost:5432/vastu_analyzer?schema=public"

# JWT Secret - Generate a secure random string
JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
JWT_EXPIRES_IN="7d"

# Google OAuth - Get from Google Cloud Console
GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
GOOGLE_CALLBACK_URL="http://localhost:3000/auth/google/callback"

# Server
PORT=3000
NODE_ENV="development"

# Frontend URL - Update for production
FRONTEND_URL="http://localhost:8081"

# CORS - Add your mobile app URL
ALLOWED_ORIGINS="http://localhost:8081,http://localhost:19006"
```

## Step 4: Set Up Google OAuth (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure the OAuth consent screen
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (development)
   - Your production URL (when deployed)
7. Copy the Client ID and Client Secret to your `.env` file

## Step 5: Initialize Prisma Database

Run Prisma migrations to create database tables:

```bash
# Generate Prisma Client
npm run prisma:generate

# Run migrations to create tables
npm run prisma:migrate

# (Optional) Open Prisma Studio to view your database
npm run prisma:studio
```

## Step 6: Start the Backend Server

### Development Mode (with hot reload):

```bash
npm run dev
```

### Production Mode:

```bash
npm run build
npm start
```

The server should now be running on `http://localhost:3000`

## Step 7: Test the API

### Health Check:

```bash
curl http://localhost:3000/health
```

### Test Sign Up:

```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User"
  }'
```

### Test Login:

```bash
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

## API Endpoints

### Authentication

- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login with email/password
- `GET /api/auth/google` - Initiate Google OAuth
- `GET /api/auth/google/callback` - Google OAuth callback
- `GET /api/auth/verify` - Verify JWT token

### User

- `GET /api/user/profile` - Get user profile (requires auth)
- `PUT /api/user/profile` - Update user profile (requires auth)

## Common Issues

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

### Database Connection Error

- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists and credentials are correct

### Prisma Migration Errors

```bash
# Reset database (WARNING: This deletes all data)
npx prisma migrate reset

# Push schema without migrations
npx prisma db push
```

## Production Deployment

### Environment Variables

Update these for production:
- `DATABASE_URL` - Production PostgreSQL URL
- `JWT_SECRET` - Strong random secret
- `GOOGLE_CALLBACK_URL` - Production callback URL
- `FRONTEND_URL` - Production frontend URL
- `NODE_ENV="production"`

### Deployment Platforms

- **Railway**: Deploy with one click
- **Render**: Free tier available
- **Heroku**: Easy PostgreSQL integration
- **AWS/Azure/GCP**: Full control

### Security Checklist

- [ ] Use strong JWT secret
- [ ] Enable HTTPS
- [ ] Set proper CORS origins
- [ ] Use environment variables
- [ ] Enable rate limiting
- [ ] Add request validation
- [ ] Implement logging
- [ ] Set up monitoring

## Next Steps

1. Configure your React Native app to connect to this backend
2. Update API URLs in `src/config/api.config.ts`
3. Test authentication flow end-to-end
4. Implement additional features (Vastu analysis, reports, etc.)
