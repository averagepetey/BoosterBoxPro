# Screenshot-Based Manual Entry Guide

## Overview

The screenshot-based entry system allows you to upload screenshots of your data source (TCGplayer, Excel, etc.) and have the AI (Cursor) extract the metrics and create entries automatically.

**Two Types of Screenshots Supported:**
1. **Daily Metrics Screenshots** - Aggregate data (floor price, total listings, volume)
2. **Individual Sales Screenshots** - Individual completed sales from TCGplayer
3. **Listing Data Screenshots** - Active listing data with individual prices/quantities

---

## 🔄 Two Workflows

### Workflow 1: Admin Panel Upload (Recommended)

**Best for:** Quick entries via web interface

1. **Upload Screenshot**
   - Go to Admin Panel: `http://localhost:8000/admin`
   - Click "📷 Screenshot Upload" tab
   - Select image file (PNG, JPG, etc.)
   - Optionally select box and date
   - Click "Upload Screenshot"

2. **View & Extract**
   - Screenshot displays in the panel
   - Fill in the extraction form with values from the screenshot
   - Click "✓ Confirm & Save Metrics"

3. **Auto-Calculation**
   - System automatically calculates:
     - Market cap (if not provided)
     - Volume EMA/SMA
     - Liquidity score
     - Expected days to sell
     - All derived metrics

---

### Workflow 2: AI-Assisted Extraction (For Cursor Chat)

**Best for:** When you want Cursor AI to extract the data automatically

#### Step 1: Upload Screenshot

**Option A: Via Command Line**
```bash
python scripts/process_screenshot_for_ai.py path/to/screenshot.png --box-name "OP-01 Romance Dawn" --date "2024-01-15"
```

This will return a `processing_id` like: `abc123-def456-...`

**Option B: Via Admin Panel**
1. Upload screenshot in admin panel
2. Note the processing_id shown (or get it from the URL)

#### Step 2: Share with Cursor AI

Share in Cursor chat:
```
I uploaded a screenshot. Processing ID: abc123-def456-...
[Attach screenshot image here]
```

#### Step 3: AI Extracts and Saves

The AI will:
1. Analyze the screenshot
2. Extract metrics (floor price, listings, volume, etc.)
3. Identify which box it is (if not already specified)
4. Calculate derived metrics
5. Save to database using the API

**Example AI Command:**
```bash
python scripts/ai_extract_from_screenshot.py \
  abc123-def456-... \
  550e8400-e29b-41d4-a716-446655440001 \
  2024-01-15 \
  245.99 \
  3044 \
  --volume 45230.50 \
  --units-sold 18
```

---

## 📋 API Endpoints

### 1. Upload Screenshot
```
POST /api/v1/admin/screenshot/upload
Content-Type: multipart/form-data

Form fields:
- file: Image file (required)
- box_id: UUID (optional)
- box_name: String (optional)
- metric_date: YYYY-MM-DD (optional)

Response:
{
  "processing_id": "uuid",
  "needs_review": true,
  "message": "..."
}
```

### 2. Get Screenshot
```
GET /api/v1/admin/screenshot/{processing_id}
Response: {
  "processing_id": "...",
  "image_data_url": "data:image/png;base64,...",
  "box_name": "...",
  "metric_date": "..."
}
```

### 3. Confirm Extraction
```
POST /api/v1/admin/screenshot/confirm
{
  "processing_id": "uuid",
  "booster_box_id": "uuid",
  "metric_date": "YYYY-MM-DD",
  "floor_price_usd": 245.99,
  "active_listings_count": 3044,
  "daily_volume_usd": 45230.50,
  "units_sold_count": 18,
  "visible_market_cap_usd": 748476.56
}
```

---

## 🎯 Usage Examples

### Example 1: TCGplayer Screenshot

1. Take screenshot of TCGplayer page showing:
   - Floor price
   - Active listings count
   - Volume data (if visible)

2. Upload to admin panel

3. Extract values from screenshot:
   - Floor Price: $245.99
   - Active Listings: 3,044
   - Daily Volume: $45,230.50 (if visible)

4. System auto-calculates:
   - Market Cap = $245.99 × 3,044 = $748,476.56
   - EMA/SMA of volume
   - Liquidity score
   - Expected days to sell

### Example 2: Excel/Spreadsheet Screenshot

1. Take screenshot of Excel row with metrics

2. Upload to admin panel

3. Extract values:
   - All metrics from the row

4. System processes and saves

---

## 💡 Tips

1. **Clear Screenshots**: Make sure text is readable in the screenshot
2. **Box Identification**: Provide box name when uploading to help auto-match
3. **Date Defaults**: If date not provided, defaults to today
4. **Auto-Calculations**: Don't worry about calculating market cap - system does it automatically
5. **Validation**: System validates all inputs before saving

---

## 🔧 Technical Details

- **Image Storage**: Screenshots stored in-memory (temporary) during processing session
- **Processing ID**: Unique identifier for each screenshot upload session
- **Base64 Encoding**: Images encoded as base64 data URLs for display
- **Auto-Calculation**: Triggers metrics calculator service automatically
- **Validation**: All data validated via Pydantic schemas before saving

---

## 📝 For Cursor AI

When user shares a screenshot with a processing_id:

1. **Analyze the screenshot** to extract:
   - Floor price (USD)
   - Active listings count
   - Daily volume (if visible)
   - Units sold (if visible)
   - Market cap (if visible, or will be calculated)

2. **Identify the box** from:
   - Box name provided
   - Image content (product name)
   - Context from user

3. **Use the confirmation script**:
   ```bash
   python scripts/ai_extract_from_screenshot.py \
     <processing_id> \
     <box_uuid> \
     <date> \
     <floor_price> \
     <listings_count> \
     [--volume <volume>] \
     [--units-sold <count>]
   ```

4. **The script will**:
   - Submit extracted values
   - Trigger metrics calculations
   - Save to database
   - Return confirmation

---

## ✅ Benefits

- **Fast Entry**: Upload screenshot and extract in seconds
- **AI-Assisted**: Cursor can extract complex data automatically
- **Auto-Calculations**: All derived metrics calculated automatically
- **Validation**: Built-in validation prevents errors
- **Audit Trail**: Processing sessions can be tracked

---

**Ready to use!** Upload a screenshot and start extracting data! 🚀

