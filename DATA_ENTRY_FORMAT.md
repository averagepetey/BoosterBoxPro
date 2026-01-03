# Data Entry Format Guide

## How to Signal Data Entry Requests

When you want me to extract data from a screenshot and add it to the database, use one of these formats:

### Option 1: Simple Prefix
Start your message with:
```
DATA ENTRY:
```
or
```
ADD DATA:
```

### Option 2: Structured Format
Use this format:
```
[DATA ENTRY]
Box: [box name]
Date: [YYYY-MM-DD]
[then paste screenshot or describe data]
```

### Option 3: Clear Statement
Just say:
```
"I'm sending data to add to the system"
"Here's a screenshot to extract data from"
"Add this data to the database"
```

## What I'll Do

When I see a data entry request, I will:
1. ✅ Extract all visible data from the screenshot
2. ✅ Check for duplicates automatically
3. ✅ Only add if new or different
4. ✅ Tell you exactly what happened (added/updated/skipped)
5. ✅ Show you the data I extracted

## Example Messages

**Good:**
```
DATA ENTRY: Screenshot of OP-01 from today
```

**Good:**
```
[DATA ENTRY]
Box: OP-01
Date: 2024-12-29
[attached screenshot]
```

**Good:**
```
I'm sending you a screenshot to extract data from and add to the system
```

**Also Good:**
```
Here's today's data for OP-02
[attached screenshot]
```

## What Data I Extract

I'll look for:
- Floor price
- Active listings count
- Boxes sold today
- Daily volume
- Market cap
- Boxes added today
- Any other visible metrics

## After I Extract

I'll show you:
```
Extracted Data:
- Box: OP-01
- Date: 2024-12-29
- Floor Price: $120.50
- Active Listings: 45
- Boxes Sold: 3
- Daily Volume: $361.50
- Market Cap: $5,422.50
- Boxes Added: 2

Duplicate Check: ✅ New data - Adding to database
Result: ✅ Successfully added
```

## Tips

- You can send multiple screenshots at once
- I'll process each one separately
- If you don't specify a date, I'll use today's date
- If you don't specify a box, I'll try to detect it from the screenshot


