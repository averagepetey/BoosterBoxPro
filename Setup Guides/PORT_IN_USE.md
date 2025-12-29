# Port 8000 Already in Use

## The server is already running!

If you see "Address already in use" error, it means the server is already running on port 8000.

## Test the /health endpoint

Since the server is already running, you can test it directly:

### Option 1: Using curl (simplest)
```bash
curl http://localhost:8000/health
```

### Option 2: Using browser
Open: http://localhost:8000/health

### Option 3: Using httpx
```bash
source venv/bin/activate
python -c "import httpx; print(httpx.get('http://localhost:8000/health').json())"
```

### Option 4: Using the test script
```bash
source venv/bin/activate
python scripts/test_health_endpoint.py
```

---

## If you want to restart the server

### Find and kill the existing process:

```bash
# Find the process using port 8000
lsof -ti:8000

# Kill it
kill $(lsof -ti:8000)

# Or kill all Python processes (be careful!)
# pkill -f uvicorn
```

### Or use a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then test with: `curl http://localhost:8001/health`

---

**Since the server is already running, just test the /health endpoint directly!**

