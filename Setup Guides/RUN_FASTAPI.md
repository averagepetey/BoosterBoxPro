# Run FastAPI Application

## Quick Start

```bash
source venv/bin/activate

# Option 1: Use the run script
python scripts/run_server.py

# Option 2: Use uvicorn directly
uvicorn app.main:app --reload
```

## Test the Application

First, test that the app can be imported:

```bash
source venv/bin/activate
python scripts/test_app.py
```

## Access the Application

Once the server is running:

- **API Root:** http://localhost:8000/
- **Health Check:** http://localhost:8000/health
- **Interactive API Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc

## Expected Output

When you start the server, you should see:

```
🚀 Starting BoosterBoxPro API...
✅ Database connection initialized
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Troubleshooting

### Error: "Could not initialize database"

- Check that your `.env` file exists and has the correct `DATABASE_URL`
- Verify database connection: `python scripts/test_db_connection.py`

### Error: "Module not found"

- Make sure virtual environment is activated: `source venv/bin/activate`
- Make sure you're in the project root directory

### Port 8000 already in use

- Change the port: `uvicorn app.main:app --port 8001 --reload`
- Or kill the process using port 8000

---

**The FastAPI application is ready to run!**

