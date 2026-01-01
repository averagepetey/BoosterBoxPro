# Favorites / My List Feature Design

## Overview

Users can favorite booster boxes to track them in a personal "My List" view. This feature requires user authentication.

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

### User Favorites Table
```sql
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booster_box_id UUID NOT NULL REFERENCES booster_boxes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, booster_box_id),  -- Prevent duplicates
    INDEX idx_user_id (user_id),
    INDEX idx_booster_box_id (booster_box_id),
    INDEX idx_user_created (user_id, created_at DESC)  -- For sorting by favorited date
);
```

---

## API Endpoints

### Authentication

#### Register User
```
POST /api/v1/auth/register
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "optional_username"  // Optional
}

Response (201 Created):
{
  "message": "User registered successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "optional_username",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

#### Login
```
POST /api/v1/auth/login
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,  // seconds
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "optional_username"
  }
}
```

#### Get Current User
```
GET /api/v1/users/me
Authorization: Bearer {token}

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "optional_username",
  "created_at": "2024-01-15T10:00:00Z",
  "favorites_count": 15
}
```

---

### Favorites Management

#### Add Favorite
```
POST /api/v1/users/me/favorites/{booster_box_id}
Authorization: Bearer {token}

Response (201 Created):
{
  "success": true,
  "message": "Booster box added to favorites",
  "data": {
    "booster_box_id": "uuid",
    "favorited_at": "2024-01-15T10:30:00Z"
  }
}

Error (409 Conflict): Already favorited
Error (404 Not Found): Booster box not found
Error (401 Unauthorized): Invalid or missing token
```

#### Remove Favorite
```
DELETE /api/v1/users/me/favorites/{booster_box_id}
Authorization: Bearer {token}

Response (204 No Content): Success

Error (404 Not Found): Not favorited or booster box not found
Error (401 Unauthorized): Invalid or missing token
```

#### Check Favorite Status
```
GET /api/v1/users/me/favorites/{booster_box_id}
Authorization: Bearer {token}

Response (200 OK): Favorited
{
  "is_favorited": true,
  "favorited_at": "2024-01-15T10:30:00Z"
}

Response (404 Not Found): Not favorited
{
  "is_favorited": false
}
```

#### Get My List (Favorited Boxes)
```
GET /api/v1/users/me/favorites?sort=volume&limit=50&offset=0
Authorization: Bearer {token}

Query Parameters:
- sort: volume (default), market_cap, floor_price, floor_change_1d, sales, listed
- order: asc, desc (default: desc)
- limit: number of results (default: 50, max: 100)
- offset: pagination offset (default: 0)

Response (200 OK):
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "is_favorited": true,  // Always true in this endpoint
      "favorited_at": "2024-01-10T12:30:00Z",  // When user favorited
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      "set_name": "Modern Horizons 3",
      "game_type": "MTG",
      "image_url": "https://cdn.example.com/mh3-box.jpg",
      "metrics": {
        "floor_price_usd": 245.99,
        "floor_price_1d_change_pct": -1.3,
        "daily_volume_usd": 45230.50,
        "volume_7d_ema": 43890.25,
        "visible_market_cap_usd": 1250000.00,
        "units_sold_count": 18,
        "active_listings_count": 3044,
        "listed_percentage": 8.3,
        "estimated_total_supply": 36600,
        "days_to_20pct_increase": 12.5,
        "price_sparkline_1d": [...]
      },
      "reprint_risk": "LOW",
      "metric_date": "2024-01-15"
    }
  ],
  "meta": {
    "total": 15,  // Total favorited boxes for this user
    "sort": "volume",
    "sort_direction": "desc",
    "limit": 50,
    "offset": 0,
    "date": "2024-01-15"
  }
}
```

---

## Updated Leaderboard Response (with Favorite Status)

When a user is authenticated, the leaderboard endpoint includes favorite status:

```
GET /api/v1/booster-boxes?sort=volume&limit=10
Authorization: Bearer {token}  // Optional - only needed for favorite status
```

**Updated Response (with auth):**
```json
{
  "data": [
    {
      "id": "uuid",
      "rank": 1,
      "is_favorited": false,  // User's favorite status (only if authenticated)
      "product_name": "Magic: The Gathering - Modern Horizons 3",
      // ... rest of fields same as before
    },
    {
      "id": "uuid-2",
      "rank": 2,
      "is_favorited": true,  // This one is favorited
      // ...
    }
  ],
  "meta": {
    "total": 150,
    "sort": "volume",
    "date": "2024-01-15"
  }
}
```

**Note:** If not authenticated, `is_favorited` field is omitted or defaults to `false`.

---

## UI Integration

### Leaderboard View

**Visual Indicators:**
- Star icon (⭐) next to favorited boxes
- Empty star icon (☆) for non-favorited boxes (when authenticated)
- Tap/click star to toggle favorite
- Show loading state while API call in progress

**Interaction Flow:**
1. User taps star icon
2. If not authenticated → Show login prompt/modal
3. If authenticated → Toggle favorite (add/remove)
4. Update UI immediately (optimistic update)
5. If API call fails, revert UI change and show error

### My List View

**Location:**
- Separate tab/screen in mobile app
- Separate page/section in website
- Accessible from navigation menu

**Features:**
- Same table structure as leaderboard
- Shows only favorited boxes
- Sortable by all metrics (volume, market cap, floor price, etc.)
- Remove from favorites action (tap star again or remove button)
- Empty state: "You haven't favorited any boxes yet"

**Sorting:**
- Default: Sort by favorited date (newest first)
- User can change sort to: volume, market cap, floor price, etc.

---

## Authentication Flow

### Mobile App

**Login Screen:**
- Email/password fields
- "Remember me" checkbox
- "Forgot password?" link (future feature)
- Social auth buttons (optional: Google Sign-In, Apple Sign-In)

**Token Storage:**
- iOS: Keychain Services (secure)
- Android: EncryptedSharedPreferences or Keystore
- Token refresh: Handle token expiration, auto-refresh if possible

**Session Management:**
- Store user info and token after login
- Auto-login on app launch if token valid
- Logout clears stored credentials

### Website

**Login:**
- Modal dialog or dedicated page
- Same email/password fields
- "Remember me" checkbox

**Token Storage:**
- Option 1: httpOnly cookie (more secure, CSRF protection needed)
- Option 2: localStorage (simpler, XSS risk)
- Recommendation: httpOnly cookie for production

**Session Management:**
- Auto-login if valid token/cookie exists
- Logout clears cookie/token

---

## Security Considerations

1. **Password Requirements:**
   - Minimum 8 characters (recommend 12+)
   - Hash with bcrypt or argon2 (never store plaintext)
   - Rate limit login attempts (prevent brute force)

2. **JWT Token:**
   - Short expiration (1 hour access token)
   - Refresh token for longer sessions (optional)
   - Secure signing key
   - Validate token on every protected request

3. **API Security:**
   - HTTPS only (no HTTP in production)
   - CORS configured for mobile app and website domains
   - Rate limiting per user (prevent abuse)
   - Input validation (SQL injection, XSS prevention)

4. **Data Privacy:**
   - Users can only see/modify their own favorites
   - User IDs validated on all favorite endpoints
   - No user data exposed in public endpoints

---

## Implementation Notes

### Database Queries

**Get user's favorites with metrics:**
```sql
SELECT 
    bb.*,
    ddm.*,
    uf.created_at as favorited_at
FROM user_favorites uf
JOIN booster_boxes bb ON uf.booster_box_id = bb.id
JOIN daily_derived_metrics ddm ON bb.id = ddm.booster_box_id
WHERE uf.user_id = ?
    AND ddm.metric_date = (SELECT MAX(metric_date) FROM daily_derived_metrics)
ORDER BY ddm.volume_7d_ema DESC  -- Or other sort field
LIMIT ? OFFSET ?;
```

**Check if box is favorited (for leaderboard):**
```sql
SELECT booster_box_id
FROM user_favorites
WHERE user_id = ? AND booster_box_id IN (?, ?, ?, ...)  -- Batch check
```

### Performance

- Use batch queries to check favorite status for multiple boxes
- Cache favorite status in API response if needed
- Index `user_favorites(user_id, booster_box_id)` for fast lookups
- Consider pagination for users with many favorites

---

## Future Enhancements (Optional)

1. **Favorite Lists/Collections:**
   - Multiple named lists (e.g., "Watchlist", "Potential Buys")
   - Organize favorites into categories

2. **Favorite Alerts:**
   - Notifications when favorited box price changes significantly
   - Daily/weekly digest of favorited boxes

3. **Social Features:**
   - Share favorite lists
   - See public favorite lists from other users
   - Follow other users

4. **Favorite Notes:**
   - Add personal notes to favorited boxes
   - Price targets, reasons for tracking, etc.


