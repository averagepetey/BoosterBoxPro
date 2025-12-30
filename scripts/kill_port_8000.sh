#!/bin/bash
# Kill process running on port 8000

echo "🔍 Finding process on port 8000..."

# Find the process ID (PID) listening on port 8000
PID=$(lsof -ti:8000 2>/dev/null)

if [ -z "$PID" ]; then
  echo "✅ No process found on port 8000."
  echo "   Port is free to use!"
else
  echo "📌 Found process: $PID"
  
  # Show what process it is
  echo "   Process details:"
  ps -p $PID -o pid,ppid,command 2>/dev/null || echo "   (Process may have already exited)"
  
  echo ""
  echo "🛑 Killing process $PID..."
  kill -9 "$PID" 2>/dev/null
  
  if [ $? -eq 0 ]; then
    echo "✅ Process killed successfully"
  else
    echo "⚠️  Could not kill process. It may have already exited."
  fi
fi

echo ""
echo "💡 You can now start the server with: python scripts/run_server.py"

