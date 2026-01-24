# How to Start Both Servers

## Backend Server (Required!)

The backend server must be running for the dashboard to work.

### Start Backend:
```bash
cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro

# Activate virtual environment
source venv/bin/activate

# Start the server
python main.py
```

You should see:
```
🚀 Starting BoosterBoxPro API in development mode
✅ Database connection established
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Frontend Server

### Start Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
✓ Ready in [time]
○ Local: http://localhost:3000
```

## Verify Both Are Running

### Check Backend:
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy"}`

### Check Frontend:
```bash
curl http://localhost:3000
```
Should return HTML (the landing page)

## Common Issues

1. **Backend not starting**: 
   - Make sure PostgreSQL is running: `brew services start postgresql@15`
   - Check database connection in `.env` file
   - Check if port 8000 is already in use

2. **Frontend shows internal server error**:
   - **This happens when backend is not running!**
   - Start the backend server first
   - Then refresh the frontend

3. **Port already in use**:
   - Kill the process: `lsof -ti:8000 | xargs kill` (backend)
   - Or: `lsof -ti:3000 | xargs kill` (frontend)

## Order of Operations

1. ✅ Start PostgreSQL database
2. ✅ Start Backend server (port 8000)
3. ✅ Start Frontend server (port 3000)
4. ✅ Open browser to http://localhost:3000/dashboard

