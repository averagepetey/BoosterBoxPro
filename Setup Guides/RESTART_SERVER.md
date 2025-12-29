# How to Restart the FastAPI Server

## Method 1: Stop and Restart in Terminal

If your server is running in a terminal window:

1. **Stop the server**: Press `Ctrl+C` in the terminal where the server is running
2. **Start the server again**:
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```
   
   OR use the run script:
   ```bash
   source venv/bin/activate
   python scripts/run_server.py
   ```

## Method 2: Kill Process and Restart

If you can't find the terminal or Ctrl+C doesn't work:

1. **Find the process**:
   ```bash
   lsof -ti:8000
   ```
   This will show the process ID (PID) using port 8000

2. **Kill the process**:
   ```bash
   kill $(lsof -ti:8000)
   ```
   
   OR if that doesn't work, force kill:
   ```bash
   kill -9 $(lsof -ti:8000)
   ```

3. **Start the server again**:
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

## Method 3: Using the Run Script

Simply use the run script which handles everything:

```bash
source venv/bin/activate
python scripts/run_server.py
```

## Verify Server is Running

After restarting, verify the server is working:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{"status":"healthy","environment":"development"}
```

Or open in browser: http://localhost:8000/docs

## Quick Reference

**Stop server**: `Ctrl+C`  
**Start server**: `uvicorn app.main:app --reload` (with venv activated)  
**Check if running**: `curl http://localhost:8000/health`  
**Kill process**: `kill $(lsof -ti:8000)`

