# Testing Checklist

## ✅ Backend API Tests

### Health Check
- [x] `/health` endpoint returns `{"status":"healthy"}`

### Box Detail Endpoint
- [x] `/booster-boxes/{id}` returns valid box data
- [ ] Test with invalid ID (should return 404)
- [ ] Test time-series endpoint
- [ ] Test rank-history endpoint

### Leaderboard Endpoint
- [ ] `/booster-boxes?limit=10` returns list of boxes
- [ ] Sorting works (volume, price, etc.)
- [ ] Pagination works (offset, limit)

## ✅ Frontend Tests

### Dashboard/Leaderboard Page
- [ ] Page loads without errors
- [ ] Table displays all boxes
- [ ] Sorting buttons work
- [ ] Time range buttons (24H, 7D, 30D) work
- [ ] Mobile: Hamburger menu works
- [ ] Mobile: Card layout displays correctly
- [ ] Desktop: Table layout displays correctly
- [ ] Clicking a box row navigates to detail page

### Box Detail Page
- [ ] Page loads for valid box ID
- [ ] All metrics display correctly
- [ ] Price chart renders
- [ ] Rank history chart renders
- [ ] Time range buttons work (7d, 30d, 90d, 1y, all)
- [ ] Back button works
- [ ] Mobile: Layout stacks correctly
- [ ] Mobile: Charts are readable
- [ ] Desktop: Side-by-side layout works
- [ ] Info buttons show tooltips

### Navigation
- [ ] Logo links to dashboard
- [ ] Dashboard link works
- [ ] Account link works (if implemented)
- [ ] Admin link shows only for admins
- [ ] Mobile: Hamburger menu opens/closes
- [ ] Mobile: Menu items are clickable (44x44px touch targets)

### Mobile Responsiveness
- [ ] Test on iPhone (375px width)
- [ ] Test on iPad (768px width)
- [ ] Test on desktop (1920px width)
- [ ] Text is readable on all sizes
- [ ] Buttons are easily tappable
- [ ] No horizontal scrolling
- [ ] Images scale correctly

## ✅ Admin Features (If Accessible)

### Screenshot Upload
- [ ] Admin page loads (requires API key)
- [ ] File upload works
- [ ] Image preview shows
- [ ] Manual entry mode works (without AI)
- [ ] Duplicate detection works
- [ ] Data saves correctly

## 🐛 Known Issues to Verify

- [ ] Box detail page loads (was stuck loading before)
- [ ] No infinite loading states
- [ ] Error messages are clear
- [ ] Timeouts show helpful messages

## 📱 Mobile-Specific Tests

### Touch Targets
- [ ] All buttons are at least 44x44px
- [ ] Links are easily tappable
- [ ] No overlapping clickable areas

### Layout
- [ ] Leaderboard cards stack vertically on mobile
- [ ] Box detail metrics stack on mobile
- [ ] Charts are readable on mobile
- [ ] Navigation is accessible

### Performance
- [ ] Page loads quickly on mobile
- [ ] Images load efficiently
- [ ] No layout shifts during load

## 🔍 Browser Console Checks

When testing, check browser console (F12) for:
- [ ] No JavaScript errors
- [ ] No failed network requests
- [ ] API calls complete successfully
- [ ] No CORS errors
- [ ] No timeout errors

## 📝 Test Results

**Date:** _______________
**Tester:** _______________

### Backend
- Health: ✅ / ❌
- Box Detail: ✅ / ❌
- Leaderboard: ✅ / ❌

### Frontend
- Dashboard: ✅ / ❌
- Box Detail: ✅ / ❌
- Navigation: ✅ / ❌
- Mobile: ✅ / ❌

### Issues Found:
1. 
2. 
3. 


