# Screenshot-Based Data Entry System

This system processes TCGPlayer screenshots sent via chat, extracts data using AI, checks for duplicates, and updates the database/JSON files.

## How It Works

1. **You send a screenshot** of TCGPlayer data via chat
2. **AI processes the image** using OpenAI Vision API to extract:
   - Product name / Set code (e.g., "OP-01", "One Piece OP-02")
   - Floor price
   - Active listings count
   - Boxes sold today
   - Daily volume USD
   - Visible market cap
   - Boxes added today
   - Estimated total supply
3. **System finds the matching box** in your database by set code or product name
4. **Checks for duplicates** - compares with existing data for the same date
5. **Updates the data** if it's new or different
6. **Reports back** what happened (success, duplicate, or error)

## Screenshot Requirements

- **Format**: PNG, JPEG, or JPG
- **Size**: Maximum 10MB
- **Content**: Should clearly show:
  - Product name or set code (e.g., "OP-01", "One Piece OP-13")
  - Price information
  - Sales/volume data
  - Any other relevant metrics

## What Gets Extracted

The AI will extract any visible data from the screenshot:

- ✅ Product name / Set code
- ✅ Floor price (USD)
- ✅ Active listings count
- ✅ Boxes sold today
- ✅ Daily volume (USD)
- ✅ Visible market cap (USD)
- ✅ Boxes added today
- ✅ Estimated total supply

## Duplicate Detection

The system automatically checks if data already exists:
- **Same box** (by ID)
- **Same date** (defaults to today)
- **Same values** (with small tolerance for floating point)

**If duplicate**: Data is not updated, and you'll be notified it's a duplicate.

**If different**: Data is updated, and you'll see what changed.

## Usage in Chat

Simply send a screenshot of TCGPlayer data. The AI will:
1. Recognize it's a screenshot
2. Process it automatically
3. Extract the data
4. Check for duplicates
5. Update your system
6. Report the results

## Example Flow

**You**: [Sends screenshot of OP-01 TCGPlayer page]

**System**: 
- Extracts: "One Piece OP-01 Romance Dawn", Floor: $3998.49, Volume: $5517.92, Sales: 1
- Finds matching box: "One Piece - OP-01 Romance Dawn Booster Box"
- Checks for duplicates: No existing data for today
- Updates: Successfully saved new data
- **Response**: "✅ Data updated successfully for OP-01. Floor: $3998.49, Volume: $5517.92, Sales: 1"

## Error Handling

If something goes wrong, you'll get a clear message:
- **"Could not identify product name"** - Set code or product name not visible in screenshot
- **"Box not found"** - No matching box in database
- **"Duplicate data"** - Data already exists and matches
- **"Image processing failed"** - Error extracting data from image

## Technical Details

- Uses OpenAI Vision API (GPT-4o) for image analysis
- Processes images as base64-encoded data
- Extracts structured JSON from AI response
- Fuzzy matching for product names
- Tolerance-based comparison for numeric values
- Updates `data/leaderboard.json` (with fallback to `mock_data/leaderboard.json`)

## Cost Considerations

- OpenAI Vision API usage incurs costs per image
- Each screenshot processed = 1 API call
- Costs are minimal but should be monitored
- Can disable AI extraction (`use_ai=false`) for manual entry fallback


