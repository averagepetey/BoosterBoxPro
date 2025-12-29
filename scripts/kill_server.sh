#!/bin/bash
# Kill any process running on port 8000

echo "Killing process on port 8000..."

PID=$(lsof -ti:8000)

if [ -z "$PID" ]; then
    echo "No process found on port 8000"
else
    echo "Found process: $PID"
    kill -9 $PID
    echo "✅ Process killed"
fi

