# Chat-Based Data Entry System

This system allows you to send data via chat, and the AI assistant will:
1. Parse and understand the data
2. Check for duplicates
3. Update the database/JSON files if the data is new or different

## How to Use

### Format for Sending Data

You can send data in natural language. The system will automatically extract:
- Product name or set code (e.g., "OP-01", "OP-13")
- Floor price
- Daily volume
- Units sold
- Active listings
- Market cap
- Boxes added today
- Date (defaults to today if not specified)

### Examples

**Simple format:**
```
OP-01: Floor $100, Volume $5000, Sales 10
```

**Detailed format:**
```
One Piece OP-13: Floor Price: $362.52, Daily Volume: $7003.88, Units Sold: 19, Listings: 22
```

**With date:**
```
OP-02: Floor $195.50, Volume $37000, Sales 15, Date: 2024-01-15
```

**Multiple metrics:**
```
OP-01 Romance Dawn: Floor $3998.49, Volume $5517.92, Sales 1, Listings 0, Market Cap $39984900
```

### What Happens

1. **Parsing**: The system extracts all relevant data from your message
2. **Box Matching**: It finds the matching box by set code or product name
3. **Duplicate Check**: It compares with existing data for the same date
4. **Update**: If data is new or different, it updates the JSON file
5. **Response**: You'll get a message confirming success or explaining any issues

### Duplicate Detection

The system checks:
- Same box ID
- Same date
- Same metric values (with small tolerance for floating point)

If data is identical, it will **not** update and will inform you it's a duplicate.

If data differs, it will:
- Show what changed
- Update the existing record
- Confirm the update

### Error Handling

If something goes wrong, you'll get a clear error message:
- Box not found
- Missing required fields
- Invalid data format
- File write errors

## Technical Details

The system uses:
- `scripts/chat_data_entry.py` - Main processing script
- `data/leaderboard.json` - Data storage (with fallback to `mock_data/leaderboard.json`)
- Fuzzy matching for product names
- Set code extraction (OP-01, EB-01, PRB-01, etc.)
- Tolerance-based comparison for numeric values

## Integration with AI Assistant

When you send data in chat, the AI assistant will:
1. Recognize it's data entry (looks for set codes, prices, metrics)
2. Call `process_data_entry()` function
3. Process and validate the data
4. Check for duplicates
5. Update the system
6. Report back the results





