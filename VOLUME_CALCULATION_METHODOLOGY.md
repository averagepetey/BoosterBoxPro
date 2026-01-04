# Real Online Volume Calculation Methodology

## Current Limitations

**What we have:**
- Floor price (lowest listed price)
- Boxes sold per day (aggregate count)
- Active listings count

**What we're missing for accurate volume:**
- Actual sale prices (we only have floor price)
- Price distribution of completed sales
- Individual transaction data
- Market depth/order book data

## Ideal Data Requirements

### 1. **Transaction-Level Data** (Most Accurate)
```
For each sale:
- Exact sale price (not just floor)
- Timestamp
- Platform (e.g., TCGPlayer, eBay, private sale)
- Sale type (public listing, best offer, auction)
- Buyer/seller info (anonymized)
```

**Volume Calculation:**
```
Real Volume = Σ(actual_sale_price × quantity) for all sales in period
```

### 2. **Price Distribution Data** (Good Approximation)
```
For each box:
- Sales at floor price: X%
- Sales above floor: Y% (and distribution)
- Sales below floor: Z% (private sales, quick sales)
- Average sale price vs floor price ratio
```

**Volume Calculation:**
```
Average Sale Price = floor_price × (weighted_average_price_ratio)
Real Volume = average_sale_price × boxes_sold_per_day × days
```

### 3. **Market Depth Data** (Good Proxy)
```
- Order book showing bids/asks at different price levels
- Historical sales distribution
- Price spread analysis
- Liquidity metrics
```

**Volume Calculation:**
```
Average Sale Price = (floor_price + weighted_average_listing_price) / 2
Or use order book depth to estimate where most sales occur
```

## Recommended Approach (Given Current Data)

### Option 1: **Historical Price Analysis**
Track price movements to infer average sale prices:
- If price is rising: more sales likely at higher prices
- If price is stable: sales likely closer to floor
- If price is falling: more sales likely at lower prices

**Implementation:**
```python
def calculate_volume_with_price_trend(floor_price, boxes_sold_per_day, price_change_pct):
    # If price rising, average sale likely above floor
    if price_change_pct > 5:
        avg_sale_ratio = 1.05  # 5% above floor
    elif price_change_pct < -5:
        avg_sale_ratio = 0.92  # 8% below floor
    else:
        avg_sale_ratio = 0.96  # 4% below floor (typical)
    
    avg_sale_price = floor_price * avg_sale_ratio
    return avg_sale_price * boxes_sold_per_day * 30
```

### Option 2: **Liquidity-Based Factor**
Use active listings and liquidity to estimate:
- High liquidity (many listings) → more competition → lower average price
- Low liquidity (few listings) → less competition → closer to floor

**Implementation:**
```python
def calculate_volume_with_liquidity(floor_price, boxes_sold_per_day, active_listings, total_supply):
    # More listings = more competition = lower average price
    listing_ratio = active_listings / total_supply if total_supply > 0 else 0
    
    if listing_ratio > 0.1:  # High liquidity
        avg_sale_ratio = 0.90  # 10% below floor
    elif listing_ratio > 0.05:  # Medium liquidity
        avg_sale_ratio = 0.94  # 6% below floor
    else:  # Low liquidity
        avg_sale_ratio = 0.97  # 3% below floor
    
    avg_sale_price = floor_price * avg_sale_ratio
    return avg_sale_price * boxes_sold_per_day * 30
```

### Option 3: **Multi-Factor Model** (Best with Current Data)
Combine multiple signals:
- Price trend
- Liquidity metrics
- Historical patterns
- Market conditions

**Implementation:**
```python
def calculate_volume_multi_factor(floor_price, boxes_sold_per_day, 
                                   price_change_pct, active_listings, 
                                   total_supply, historical_avg_ratio=None):
    # Base factor
    base_ratio = 0.92
    
    # Adjust for price trend
    if price_change_pct > 5:
        trend_adjustment = 0.03  # Sales higher
    elif price_change_pct < -5:
        trend_adjustment = -0.05  # Sales lower
    else:
        trend_adjustment = 0
    
    # Adjust for liquidity
    listing_ratio = active_listings / total_supply if total_supply > 0 else 0
    if listing_ratio > 0.1:
        liquidity_adjustment = -0.02
    else:
        liquidity_adjustment = 0.01
    
    # Use historical average if available
    if historical_avg_ratio:
        avg_sale_ratio = historical_avg_ratio
    else:
        avg_sale_ratio = base_ratio + trend_adjustment + liquidity_adjustment
    
    avg_sale_price = floor_price * avg_sale_ratio
    return avg_sale_price * boxes_sold_per_day * 30
```

## Data Collection Recommendations

### Short-term (Improve Current Method):
1. **Track price movements** - Use price change % to adjust average sale price
2. **Use liquidity metrics** - Active listings ratio to estimate competition
3. **Historical analysis** - Calculate average sale price ratios over time

### Medium-term (Better Accuracy):
1. **Scrape completed sales** - If platforms show recent sales, track actual prices
2. **Order book analysis** - Use listing prices to estimate where sales occur
3. **Platform-specific factors** - Different platforms may have different patterns

### Long-term (Most Accurate):
1. **API integration** - Direct access to transaction data from platforms
2. **Blockchain data** - If using NFT/blockchain platforms, transaction data is public
3. **Market maker data** - Partnerships with platforms for actual sales data

## Example: What Real Volume Would Look Like

**Current Method (Floor Price Only):**
```
Volume = $362.52 × 19.32 boxes/day × 30 days = $210,116.59
```

**With Market Efficiency Factor (92%):**
```
Volume = $362.52 × 0.92 × 19.32 × 30 = $193,307.26
```

**With Multi-Factor Model:**
```
Price change: +0% → trend adjustment: 0
Liquidity: 22 listings / 220 supply = 10% → liquidity adjustment: -0.02
Average sale ratio: 0.92 + 0 - 0.02 = 0.90
Volume = $362.52 × 0.90 × 19.32 × 30 = $189,000.00
```

**With Actual Transaction Data (Ideal):**
```
Real sales: 
- 5 boxes at $350 (private sales)
- 10 boxes at $362 (floor)
- 4 boxes at $375 (above floor)
Average: $360.50
Volume = $360.50 × 19.32 × 30 = $208,891.80
```

## Recommendation

**Best approach with current data:**
Use a **multi-factor model** that combines:
1. Base market efficiency factor (92%)
2. Price trend adjustment (±3-5%)
3. Liquidity adjustment (±1-2%)
4. Historical patterns (if available)

This would get you within 5-10% of real volume without needing transaction-level data.

