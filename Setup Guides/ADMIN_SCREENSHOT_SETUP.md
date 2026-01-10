# Admin Screenshot Data Entry Setup Guide

## Overview

The admin screenshot ingestion system allows you to upload screenshots of marketplace data (TCGplayer, eBay, etc.) and automatically extract structured data using AI/OCR. The system includes duplicate detection to prevent overwriting existing data.

## Features

- ✅ **Screenshot Upload**: Drag-and-drop or file picker
- ✅ **AI/OCR Extraction**: Uses OpenAI Vision API to extract structured data
- ✅ **Duplicate Detection**: Automatically detects if data already exists for a date/box combination
- ✅ **Admin Protection**: Only accessible with admin API key
- ✅ **Data Preservation**: Only updates if data is new or different

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies

```bash
pip install Pillow openai
```

Or add to `requirements.txt` (already added):
```
Pillow>=10.0.0
openai>=1.0.0
```

#### Configure Environment Variables

Add to your `.env` file:

```bash
# Admin API Key (required for admin endpoints)
ADMIN_API_KEY=your-secret-api-key-here

# OpenAI API Key (required for screenshot processing)
OPENAI_API_KEY=your-openai-api-key-here
```

**Get OpenAI API Key:**
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it to your `.env` file

**Set Admin API Key:**
- Choose a strong, random string (e.g., use `openssl rand -hex 32`)
- This key will be used to authenticate admin requests

### 2. Frontend Setup

The admin interface is automatically available at `/admin` once the backend is configured.

### 3. Using the Admin Interface

1. **Navigate to Admin Page**
   - Go to `/admin` in your browser
   - The "Admin" link will only appear in navigation if you have admin access

2. **Authenticate**
   - Enter your admin API key (stored in localStorage after first entry)
   - Click "Authenticate"

3. **Upload Screenshot**
   - Drag and drop an image or click to select
   - Supported formats: PNG, JPEG, JPG
   - Maximum size: 10MB

4. **Process Screenshot**
   - Click "Process Screenshot"
   - The system will extract data using AI/OCR
   - Review the extracted values

5. **Select Box & Date**
   - Choose the booster box from the dropdown
   - Select the date for these metrics

6. **Check for Duplicates**
   - Click "Check for Duplicates"
   - The system will compare with existing data
   - Shows differences if data exists but differs

7. **Save Data**
   - Click "Save to Database"
   - System will only save if:
     - Data is new (no existing record for that date/box)
     - Data is different from existing (updates existing record)
   - Duplicate data (exact match) will not be saved

## API Endpoints

### `POST /api/v1/admin/upload-screenshot`

Upload a screenshot and extract data.

**Headers:**
```
X-Admin-API-Key: your-admin-api-key
```

**Request:**
- `file`: Image file (multipart/form-data)

**Response:**
```json
{
  "success": true,
  "extracted_data": {
    "product_name": "OP-01",
    "floor_price_usd": 120.50,
    "active_listings_count": 45,
    ...
  },
  "confidence_scores": {
    "floor_price_usd": 0.85,
    ...
  },
  "detected_box": "OP-01",
  "errors": []
}
```

### `POST /api/v1/admin/check-duplicate`

Check if data already exists for a box/date combination.

**Headers:**
```
X-Admin-API-Key: your-admin-api-key
Content-Type: application/json
```

**Request:**
```json
{
  "booster_box_id": "uuid-here",
  "metric_date": "2024-12-29",
  "floor_price_usd": 120.50,
  "active_listings_count": 45,
  ...
}
```

**Response:**
```json
{
  "is_duplicate": false,
  "existing_data": {...},
  "differences": {
    "floor_price_usd": {
      "existing": 120.00,
      "new": 120.50,
      "difference": 0.50,
      "changed": true
    }
  },
  "message": "Data exists but differs in: floor_price_usd"
}
```

### `POST /api/v1/admin/save-extracted-data`

Save extracted data to database (only if new or different).

**Headers:**
```
X-Admin-API-Key: your-admin-api-key
Content-Type: application/json
```

**Request:** Same as check-duplicate

**Response:**
```json
{
  "success": true,
  "message": "New data saved successfully.",
  "is_duplicate": false,
  "action": "created"
}
```

### `GET /api/v1/admin/boxes`

List all boxes for dropdown selection.

**Headers:**
```
X-Admin-API-Key: your-admin-api-key
```

## Duplicate Detection Logic

The system prevents duplicate data entry by:

1. **Checking for existing record**: Queries `box_metrics_unified` table for matching `booster_box_id` and `metric_date`

2. **Comparing values**: Compares key fields with tolerance:
   - `floor_price_usd`: 0.01 tolerance
   - `active_listings_count`: Exact match
   - `boxes_sold_today`: Exact match
   - `daily_volume_usd`: 0.01 tolerance
   - `visible_market_cap_usd`: 0.01 tolerance
   - `boxes_added_today`: Exact match

3. **Action taken**:
   - **No existing data**: Creates new record
   - **Data exists and matches**: Returns duplicate warning, no update
   - **Data exists but differs**: Updates existing record with new values

## Security

- **Admin API Key**: Required for all admin endpoints
- **Frontend Protection**: Admin pages are hidden from non-admin users
- **Route Protection**: Non-admin users are redirected away from `/admin`
- **Backend Validation**: All admin endpoints verify API key

## Troubleshooting

### "OpenAI API not configured"
- Make sure `OPENAI_API_KEY` is set in your `.env` file
- Restart the backend server after adding the key

### "Invalid or missing admin API key"
- Check that `ADMIN_API_KEY` is set in your `.env` file
- Verify you're using the correct key in the frontend (check localStorage)

### "Failed to load boxes"
- Make sure the database is running and accessible
- Check that boxes exist in the `booster_boxes` table

### Screenshot processing fails
- Verify OpenAI API key is valid and has credits
- Check image format (PNG, JPEG, JPG only)
- Ensure image size is under 10MB
- Check backend logs for detailed error messages

## Next Steps

- Add more fields to extraction (e.g., reprint risk, sentiment)
- Support batch uploads (multiple screenshots at once)
- Add data validation rules
- Implement data history/audit trail




