#!/bin/bash

# VastuWise AI - Quick Setup Script
# This script automates the setup process

set -e

echo "🏛️  VastuWise AI - Quick Setup"
echo "================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Install backend dependencies
echo "📦 Step 1/5: Installing backend dependencies..."
cd backend
npm install
cd ..

# Step 2: Install mobile app dependencies
echo "📦 Step 2/5: Installing mobile app dependencies..."
npm install

# Step 3: Create backend .env file
echo "⚙️  Step 3/5: Creating environment configuration..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env - Please update with your configuration"
else
    echo "⚠️  backend/.env already exists - skipping"
fi

# Step 4: Generate Prisma client
echo "🔧 Step 4/5: Generating Prisma client..."
cd backend
npm run prisma:generate
cd ..

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update backend/.env with your database URL and secrets"
echo "2. Run: cd backend && npm run prisma:migrate"
echo "3. Start backend: cd backend && npm run dev"
echo "4. In new terminal, start mobile: npm run android (or npm run ios)"
echo ""
echo "📚 Documentation:"
echo "- Quick Start: QUICK_START.md"
echo "- Backend Setup: backend/README.md"
echo "- Mobile Setup: MOBILE_SETUP.md"
echo "- Auth Guide: AUTHENTICATION_GUIDE.md"
echo ""
echo "🚀 Happy coding!"
