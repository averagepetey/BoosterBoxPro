# Testing Guide - Option 1: Test and Verify

## 🎯 Quick Test Steps

### 1. Backend Verification ✅

**Status:** All backend endpoints are working!

- ✅ Health: `http://localhost:8000/health` → `{"status":"healthy"}`
- ✅ Box Detail: Returns valid data for box ID `550e8400-e29b-41d4-a716-446655440018`
- ✅ Leaderboard: Returns list of boxes

### 2. Frontend Testing

#### A. Dashboard/Leaderboard Page

**Test Steps:**
1. Navigate to `http://localhost:3000/dashboard`
2. Verify:
   - [ ] Page loads without errors
   - [ ] Leaderboard table displays boxes
   - [ ] Box images show (or placeholder)
   - [ ] All columns display data
   - [ ] Sorting works (click column headers)
   - [ ] Time range buttons work (24H, 7D, 30D)

**Mobile Test:**
- [ ] Open browser DevTools (F12)
- [ ] Toggle device toolbar (Ctrl+Shift+M / Cmd+Shift+M)
- [ ] Select iPhone or mobile device
- [ ] Verify:
  - [ ] Hamburger menu appears (☰ icon)
  - [ ] Table becomes card layout
  - [ ] Cards are readable
  - [ ] Touch targets are large enough

#### B. Box Detail Page

**Test Steps:**
1. Click any box from the leaderboard
2. Verify:
   - [ ] Page loads (no infinite loading)
   - [ ] Box image displays
   - [ ] All metrics show values
   - [ ] Price chart renders (may be empty if no time-series data)
   - [ ] Rank history chart renders
   - [ ] Info buttons (i) show tooltips on hover
   - [ ] Back button works

**Mobile Test:**
- [ ] Switch to mobile view in DevTools
- [ ] Verify:
  - [ ] Layout stacks vertically
  - [ ] Text is readable
  - [ ] Charts fit on screen
  - [ ] Touch targets are 44x44px minimum

#### C. Navigation

**Test Steps:**
1. Check navigation bar
2. Verify:
   - [ ] Logo links to dashboard
   - [ ] Dashboard link works
   - [ ] Account link works
   - [ ] Admin link only shows if you have admin access
   - [ ] Mobile: Hamburger menu works

### 3. Browser Console Check

**Open DevTools (F12) → Console tab:**

Look for:
- ✅ No red errors
- ✅ API calls complete successfully
- ✅ No "Failed to fetch" errors
- ✅ No timeout errors

**Network Tab:**
- ✅ Requests to `/booster-boxes` return 200 OK
- ✅ Requests to `/booster-boxes/{id}` return 200 OK
- ✅ No CORS errors
- ✅ Response times are reasonable (< 1 second)

### 4. Mobile Responsiveness Checklist

**Test on Different Screen Sizes:**

1. **Mobile (375px - iPhone)**
   - [ ] Navigation: Hamburger menu visible
   - [ ] Leaderboard: Card layout
   - [ ] Box Detail: Stacked layout
   - [ ] Text: Readable (not too small)
   - [ ] Buttons: Easy to tap

2. **Tablet (768px - iPad)**
   - [ ] Layout adapts appropriately
   - [ ] Some side-by-side layouts appear
   - [ ] Still touch-friendly

3. **Desktop (1920px)**
   - [ ] Full table layout
   - [ ] Side-by-side layouts
   - [ ] Optimal use of space

### 5. Known Issues to Watch For

**Fixed Issues (Should Work Now):**
- ✅ Box detail page loading (was stuck before)
- ✅ Backend startup (missing dependencies fixed)
- ✅ Mobile navigation (hamburger menu added)

**Potential Issues:**
- ⚠️ Time-series data may be empty (no mock data yet)
- ⚠️ Rank history may be empty (no mock data yet)
- ⚠️ Charts may show "No data" message (expected if no data)

## 🐛 If Something Doesn't Work

### Box Detail Page Stuck Loading
1. Check browser console for errors
2. Check Network tab - is the request pending or failed?
3. Verify backend is running: `curl http://localhost:8000/health`
4. Check the box ID is valid

### Mobile Layout Broken
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
3. Check if Tailwind classes are applying
4. Verify viewport meta tag is present

### API Errors
1. Check backend terminal for errors
2. Verify CORS is configured correctly
3. Check API base URL in frontend

## 📊 Test Results Template

```
Date: _______________
Browser: _______________
Device: _______________

Backend:
- Health: ✅ / ❌
- Box Detail: ✅ / ❌  
- Leaderboard: ✅ / ❌

Frontend:
- Dashboard: ✅ / ❌
- Box Detail: ✅ / ❌
- Navigation: ✅ / ❌
- Mobile: ✅ / ❌

Issues Found:
1. 
2. 
3. 
```

## ✅ Success Criteria

Everything is working if:
- ✅ Dashboard loads and shows boxes
- ✅ Clicking a box opens detail page
- ✅ Detail page shows all metrics
- ✅ Mobile view is usable
- ✅ No console errors
- ✅ All API calls succeed


