#!/bin/bash
echo "Testing frontend API route..."
echo ""

# Test if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend server is running"
else
    echo "❌ Frontend server is NOT running on port 3000"
    echo "   Start it with: cd frontend && npm run dev"
    exit 1
fi

# Test if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend server is running"
else
    echo "❌ Backend server is NOT running on port 8000"
    exit 1
fi

# Test frontend API route
echo ""
echo "Testing /api/booster-boxes endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:3000/api/booster-boxes 2>&1)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Frontend API route is working (HTTP $http_code)"
    echo "   First box: $(echo "$body" | grep -o '"product_name":"[^"]*' | head -1 | cut -d'"' -f4)"
else
    echo "❌ Frontend API route returned HTTP $http_code"
    echo "   Response: $body"
fi
