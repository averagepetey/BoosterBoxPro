# Setup Guides

This directory contains all setup and usage guides for BoosterBoxPro.

## 📚 Guide Index

### Getting Started

1. **[SETUP_VENV_GUIDE.md](./SETUP_VENV_GUIDE.md)** - Virtual environment setup
   - Complete step-by-step instructions
   - Python version requirements
   - Troubleshooting common issues

### Database Setup

2. **[DATABASE_SETUP.md](./DATABASE_SETUP.md)** - Database setup guide
   - Local PostgreSQL installation
   - Cloud PostgreSQL setup (Supabase, Neon)
   - Connection configuration
   - Troubleshooting

3. **[CREATE_ENV.md](./CREATE_ENV.md)** - Environment variables setup
   - Create `.env` file from template
   - Configure database connection

4. **[RUN_MIGRATION.md](./RUN_MIGRATION.md)** - Run database migrations
   - Apply schema to database
   - Migration commands

### Running the Application

5. **[RUN_FASTAPI.md](./RUN_FASTAPI.md)** - Start the FastAPI server
   - Development server setup
   - Testing endpoints

6. **[RESTART_SERVER.md](./RESTART_SERVER.md)** - Restart the server
   - Stop/kill existing server
   - Start fresh instance

### Configuration & Admin

7. **[ADMIN_API_KEY.md](./ADMIN_API_KEY.md)** - Admin API key setup
   - Configure admin endpoints
   - API key authentication

8. **[env.example](./env.example)** - Environment variables template
   - Copy this to `.env` in project root
   - Fill in your actual values

### Data Management

9. **[IMPORT_EXCEL_DATA.md](./IMPORT_EXCEL_DATA.md)** - Import metrics from Excel
   - Excel import process
   - Data format requirements

### Testing

10. **[TEST_PUBLIC_API.md](./TEST_PUBLIC_API.md)** - Test public API endpoints
    - Leaderboard, detail, time-series endpoints
    - Example requests

11. **[TEST_HEALTH.md](./TEST_HEALTH.md)** - Test health endpoint
    - Server health check
    - Troubleshooting

### Troubleshooting

12. **[PORT_IN_USE.md](./PORT_IN_USE.md)** - Port 8000 already in use
    - Find and kill existing process
    - Use different port

13. **[GIT_COMMIT.md](./GIT_COMMIT.md)** - Git commit and push
    - Commit changes
    - Push to repository

---

## 📋 Setup Order

Follow these guides in order:

1. **SETUP_VENV_GUIDE.md** - Set up Python virtual environment
2. **DATABASE_SETUP.md** - Set up PostgreSQL database
3. **CREATE_ENV.md** - Configure environment variables
4. **RUN_MIGRATION.md** - Apply database schema
5. **RUN_FASTAPI.md** - Start the server
6. **TEST_PUBLIC_API.md** - Test the endpoints

---

## 🎯 Quick Links

- [Main README](../README.md) - Project overview
- [Planning Documents](../Planning%20Documents/) - Architecture and planning docs
- [Progress Documents](../Progress%20Documents/) - Phase completion status

---

**Note:** All setup guides are located here for easy reference during development.
