# Step 2: Database Setup - Quick Guide

## Current Status
- ✅ PostgreSQL is **not installed** on your system
- ✅ Configuration files are ready (`app/config.py`, `app/database.py`)
- ✅ `.env.example` template created

---

## Choose Your Setup Option

### Option A: Local PostgreSQL (Traditional)
**Pros:** Full control, no internet needed, standard setup  
**Cons:** Requires installation and management

### Option B: Cloud PostgreSQL (Recommended)
**Pros:** No installation, easy setup, free tier available  
**Cons:** Requires internet connection

---

## 🚀 Quick Start: Cloud PostgreSQL (Recommended)

### Using Supabase (Free Tier)

1. **Sign up at:** https://supabase.com
2. **Create new project:**
   - Click "New Project"
   - Name: `boosterboxpro`
   - Database Password: (choose a strong password)
   - Region: Choose closest to you
   - Click "Create new project"

3. **Get connection string:**
   - Wait for project to finish setting up (~2 minutes)
   - Go to: Project Settings → Database
   - Scroll to "Connection string" section
   - Copy the "URI" connection string
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

4. **Create `.env` file in project root:**
   ```bash
   # In your terminal (in project directory)
   cp .env.example .env
   
   # Then edit .env and update DATABASE_URL:
   # Change: postgresql:// to postgresql+asyncpg://
   # Replace: [YOUR-PASSWORD] with your actual password
   ```

5. **Example `.env` file:**
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:your_actual_password@db.xxxxx.supabase.co:5432/postgres
   ENVIRONMENT=development
   DEBUG=True
   ADMIN_API_KEY=your-secret-api-key-here
   ```

---

## 🖥️ Alternative: Local PostgreSQL

If you prefer local installation:

### Install PostgreSQL:
```bash
# Install PostgreSQL 15
brew install postgresql@15

# Start service
brew services start postgresql@15

# Add to PATH (add to ~/.zshrc)
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Create database
createdb boosterboxpro
```

### Create `.env` file:
```bash
cp .env.example .env
```

### Edit `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/boosterboxpro
ENVIRONMENT=development
DEBUG=True
ADMIN_API_KEY=your-secret-api-key-here
```

**Note:** If you set a password for local PostgreSQL, include it:
```
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/boosterboxpro
```

---

## ✅ Verification Steps

After creating `.env` file, test the connection:

```bash
# Activate virtual environment
source venv/bin/activate

# Test database connection (we'll create this script next)
python -c "from app.config import settings; print(f'Database URL configured: {settings.database_url[:30]}...')"
```

---

## 📋 Checklist

- [ ] Choose setup option (Cloud or Local)
- [ ] Set up PostgreSQL (install locally OR create cloud project)
- [ ] Get connection string
- [ ] Create `.env` file from `.env.example`
- [ ] Update `DATABASE_URL` in `.env` with your connection string
- [ ] Test connection (next step)

---

## 🎯 Next Steps

Once `.env` file is created:

1. ✅ Database connection configured
2. ➡️ **Next:** Test database connection
3. ➡️ **Next:** Step 3 - Initialize Alembic and create migrations

---

**Which option do you prefer?**  
I recommend **Supabase (cloud)** for the quickest setup. Let me know and I can guide you through it!

