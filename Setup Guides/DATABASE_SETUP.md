# Database Setup Guide - Step 2

## 🎯 Goal

Set up PostgreSQL database and configure the connection for BoosterBoxPro.

---

## Option 1: Local PostgreSQL (Recommended for giv Development)

### Step 1: Install PostgreSQL

**Using Homebrew:**
```bash
# Install PostgreSQL 15
brew install postgresql@15

# Or install latest version
brew install postgresql

# Start PostgreSQL service
brew services start postgresql@15
# OR
brew services start postgresql
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE boosterboxpro;

# Create user (optional, or use default 'postgres' user)
CREATE USER boosterboxpro_user WITH PASSWORD 'your_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE boosterboxpro TO boosterboxpro_user;

# Exit psql
\q
```

### Step 3: Test Connection

```bash
# Test connection
psql -d boosterboxpro -U postgres
# OR if you created a user:
psql -d boosterboxpro -U boosterboxpro_user

# If connection works, you'll see the psql prompt
# Type \q to exit
```

### Step 4: Configure Connection String

Create `.env` file in project root:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/boosterboxpro
```

---

## Option 2: Cloud PostgreSQL (Recommended for Easier Setup)

### Supabase (Free Tier Available)

1. **Sign up:** https://supabase.com
2. **Create a new project**
3. **Get connection string:**
   - Go to Project Settings → Database
   - Copy "Connection string" (URI format)
   - It will look like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres`

4. **Update for asyncpg:**
   - Change `postgresql://` to `postgresql+asyncpg://`
   - Replace `[YOUR-PASSWORD]` with your actual password

5. **Create `.env` file:**
   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.xxxxx.supabase.co:5432/postgres
   ```

### Neon (Serverless PostgreSQL - Free Tier)

1. **Sign up:** https://neon.tech
2. **Create a new project**
3. **Get connection string:**
   - Dashboard will show connection string
   - Copy it and update for asyncpg

4. **Create `.env` file:**
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@ep-xxxxx.region.aws.neon.tech/neondb
   ```

---

## Quick Start: Local PostgreSQL

If you want to get started quickly with local PostgreSQL:

```bash
# 1. Install (if not already installed)
brew install postgresql@15

# 2. Start service
brew services start postgresql@15

# 3. Create database
createdb boosterboxpro

# 4. Create .env file (use default postgres user, no password for local dev)
# Edit .env and set:
# DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/boosterboxpro
```

---

## Next Steps After Database Setup

Once database is set up and `.env` file is created:

1. ✅ Database created
2. ✅ Connection string configured in `.env`
3. ➡️ **Next:** Step 3 - Create Alembic migrations
4. ➡️ **Next:** Step 4 - Create SQLAlchemy models
5. ➡️ **Next:** Step 5 - Configure database connection in code

---

## Troubleshooting

### Issue: "psql: command not found"
**Solution:** PostgreSQL not in PATH. Add to your shell config:
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: "could not connect to server"
**Solution:** PostgreSQL service not running:
```bash
brew services start postgresql@15
```

### Issue: "password authentication failed"
**Solution:** Check your password in the connection string, or reset PostgreSQL password.

---

**Choose an option and let me know which you prefer!**

