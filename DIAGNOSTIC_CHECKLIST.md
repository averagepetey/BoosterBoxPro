# Diagnostic Checklist for Internal Server Error

## What to Check:

### 1. Frontend Terminal Logs
Look for these log messages in your frontend terminal (where `npm run dev` is running):

**Expected Success Logs:**
```
[API Proxy] Fetching from backend: http://localhost:8000/booster-boxes?sort=unified_volume_usd&limit=100
[API Proxy] BACKEND_URL: http://localhost:8000
[API Proxy] Got data in [TIME]ms, first box: One Piece - OP-13 Carrying on His Will Booster Box
```

**Error Logs to Watch For:**
```
[API Proxy] Request timeout after 30 seconds
[API Proxy] Backend error: [status] [statusText]
[API Proxy] Fetch error: [error message]
```

### 2. Browser Console (F12 → Console Tab)
Look for these messages:

**Expected Success:**
```
Fetching leaderboard from proxy: /api/booster-boxes?sort=unified_volume_usd&limit=100
Response status: 200 OK
Leaderboard data received: {data: Array(18), meta: {...}}
```

**Error Messages:**
```
Failed to fetch leaderboard: [error]
API Error Response: [error details]
```

### 3. Backend Terminal Logs
Check your backend terminal for:
- Any error messages when `/booster-boxes` is called
- Slow query warnings
- Database connection issues

### 4. Network Tab (F12 → Network Tab)
1. Open browser DevTools (F12)
2. Go to Network tab
3. Refresh the dashboard page
4. Look for the `/api/booster-boxes` request:
   - **Status**: Should be `200` (success) or `504` (timeout)
   - **Time**: Should be under 30 seconds
   - **Response**: Should contain JSON data or error message

## Quick Tests:

### Test Backend Directly:
```bash
curl http://localhost:8000/booster-boxes?limit=5
```
Should return JSON data quickly (under 5 seconds)

### Test Frontend API Route:
```bash
curl http://localhost:3000/api/booster-boxes?limit=5
```
Should return JSON data (may take up to 30 seconds)

## Common Issues:

1. **Timeout (504 error)**: Backend is taking longer than 30 seconds
   - Check backend logs for slow queries
   - Consider optimizing historical data processing

2. **Connection Error**: Frontend can't reach backend
   - Verify backend is running on port 8000
   - Check firewall/network settings

3. **500 Internal Server Error**: Something crashed
   - Check frontend terminal for full error stack trace
   - Check backend terminal for errors

## Current Configuration:
- **Frontend API Route Timeout**: 30 seconds
- **Next.js Route maxDuration**: 30 seconds
- **Backend URL**: http://localhost:8000 (or from NEXT_PUBLIC_API_URL env var)


