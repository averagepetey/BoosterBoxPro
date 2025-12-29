#!/bin/bash
# Script to commit and push changes to GitHub

set -e  # Exit on error

echo "🚀 Committing and pushing to GitHub..."
echo ""

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
fi

# Add remote if needed
if ! git remote | grep -q origin; then
    echo "Adding remote origin..."
    git remote add origin https://github.com/averagepetey/BoosterBoxPro.git
else
    echo "Updating remote origin..."
    git remote set-url origin https://github.com/averagepetey/BoosterBoxPro.git
fi

# Stage all files
echo "Staging files..."
git add .

# Check if .env is staged (should not be)
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo "⚠️  WARNING: .env file is staged! Removing it..."
    git reset HEAD .env
fi

# Create commit
echo "Creating commit..."
git commit -m "Initial commit: Phase 0 & Phase 1 Steps 1-4

- Phase 0: OpenAPI spec, mock data, TypeScript types
- Phase 1 Step 1: Project setup, dependencies, virtual environment
- Phase 1 Step 2: Database setup (Supabase PostgreSQL), configuration
- Phase 1 Step 3: Alembic migrations - all database tables created
- Phase 1 Step 4: SQLAlchemy models (BoosterBox, UnifiedBoxMetrics)
- Database schema: 9 tables with indexes and constraints
- Configuration: FastAPI, SQLAlchemy, Alembic setup
- Documentation: Setup guides, progress tracking"

# Set branch to main
git branch -M main

# Push to GitHub
echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to GitHub!"
echo "Repository: https://github.com/averagepetey/BoosterBoxPro"

