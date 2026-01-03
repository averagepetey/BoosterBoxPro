# Quick Start Guide

## Starting the Backend Server

The box detail page requires the backend server to be running. Here's how to start it:

### Option 1: Using Python directly
```bash
cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro
python main.py
```

### Option 2: Using uvicorn (recommended)
```bash
cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro
uvicorn main:app --reload --port 8000
```

### Option 3: If you have a virtual environment
```bash
cd /Users/johnpetersenhomefolder/Desktop/Vibe\ Code\ Bin/BoosterBoxPro
source venv/bin/activate  # or: source .venv/bin/activate
uvicorn main:app --reload --port 8000
```

## Verify Backend is Running

Once started, you should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

You can test it by visiting: http://localhost:8000/health

## Starting the Frontend

In a separate terminal:
```bash
cd frontend
npm run dev
```

The frontend will run on: http://localhost:3000

## Troubleshooting

If you see "Request timed out" errors:
1. Make sure the backend is running on port 8000
2. Check that no other process is using port 8000
3. Verify CORS is configured correctly (should allow localhost:3000)
4. Check the browser console for specific error messages


