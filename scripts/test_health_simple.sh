#!/bin/bash
# Simple health check test using curl

echo "Testing /health endpoint..."
echo ""

curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health

echo ""
echo ""

