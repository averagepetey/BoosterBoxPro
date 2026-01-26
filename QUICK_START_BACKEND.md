# Quick Start: Backend Server

## The Issue
"Failed to fetch" error means the frontend cannot connect to the backend API server.

## Solution: Start the Backend Server

### Step 1: Activate Virtual Environment
```bash
cd "/Users/johnpetersenhomefolder/Desktop/Vibe Code Bin/BoosterBoxPro"
source venv/bin/activate
```

### Step 2: Start the Backend Server
```bash
python main.py
```

**OR** using uvicorn directly:
```bash
uvicorn main:app --reload --port 8000
```

### Step 3: Verify Backend is Running
Open a new terminal and test:
```bash
curl http://localhost:8000/health
```

You should see a response like:
```json
{"status":"healthy"}
```

### Step 4: Check Backend Logs
You should see output like:
```
🚀 Starting BoosterBoxPro API in development mode
✅ Database connection established
✅ Auth router loaded successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Expected Endpoints

Once the backend is running, these endpoints should be available:

- **Health Check:** `http://localhost:8000/health`
- **API Docs:** `http://localhost:8000/docs`
- **Login:** `POST http://localhost:8000/api/v1/auth/login`
- **Register:** `POST http://localhost:8000/api/v1/auth/register`
- **Current User:** `GET http://localhost:8000/api/v1/auth/me`

## Troubleshooting

### Backend won't start
1. **Check if port 8000 is already in use:**
   ```bash
   lsof -i :8000
   ```
   If something is using it, kill it or use a different port.

2. **Check database connection:**
   ```bash
   # Make sure PostgreSQL is running
   # Check DATABASE_URL in .env file
   ```

3. **Check Python environment:**
   ```bash
   which python
   python --version
   # Should be Python 3.8+
   ```

### Still getting "Failed to fetch"
1. **Verify backend is actually running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check CORS settings:**
   - Backend should allow `http://localhost:3000` (or your frontend URL)
   - Check `CORS_ORIGINS` in `.env` or `app/config.py`

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Check Network tab for the failed request
   - Look for CORS errors or connection refused errors

4. **Verify frontend API URL:**
   - Frontend uses `getApiBaseUrl()` which defaults to `http://localhost:8000`
   - Check if `NEXT_PUBLIC_API_URL` is set in frontend `.env`

## Quick Test

Once backend is running, test login endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234"
  }'
```

---

**Note:** Keep the backend server running in a terminal window while developing. The frontend needs it to be running to work properly.
