# Run FastAPI Application - Updated

## Quick Start

```bash
source venv/bin/activate

# Option 1: Use uvicorn directly (RECOMMENDED)
uvicorn app.main:app --reload

# Option 2: Use the run script (fixed)
python scripts/run_server.py
```

## Access the Application

Once the server is running:

- **API Root:** http://localhost:8000/
- **Health Check:** http://localhost:8000/health
- **Interactive API Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc

---

**The recommended way is to use `uvicorn app.main:app --reload` directly!**

