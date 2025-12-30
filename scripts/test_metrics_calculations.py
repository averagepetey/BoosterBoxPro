#!/usr/bin/env python3
"""
Test Metrics Calculations with Variable Inputs
Tests EMA calculator and demonstrates calculations with different scenarios
"""

import sys
import os
from decimal import Decimal
from datetime import date, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ema_calculator import EMACalculator


def generate_sample_volumes(days: int, base_volume: float = 1000, variance: float = 0.2) -> list[Decimal]:
    """Generate sample volume data with some variance"""
    volumes = []
    current = Decimal(str(base_volume))
    
    for i in range(days):
        # Add random variance
        change = Decimal(str(random.uniform(-variance, variance)))
        current = current * (Decimal('1') + change)
        volumes.append(current)
    
    return volumes


def test_ema_basic():
    """Test basic EMA calculation"""
    print("=" * 60)
    print("Test 1: Basic EMA Calculation")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Simple increasing trend
    values = [
        Decimal('100'), Decimal('110'), Decimal('105'),
        Decimal('115'), Decimal('120'), Decimal('118'), Decimal('122')
    ]
    
    print(f"Input values: {[float(v) for v in values]}")
    ema_7 = calculator.calculate_ema(values, window=7)
    print(f"7-day EMA: {ema_7}")
    print(f"Result: {float(ema_7):.2f}\n")


def test_ema_trending_up():
    """Test EMA with upward trend"""
    print("=" * 60)
    print("Test 2: EMA with Upward Trend")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Strong upward trend
    values = [Decimal(str(1000 + i * 50)) for i in range(14)]
    
    print(f"Input values (last 7): {[float(v) for v in values[-7:]]}")
    ema_7 = calculator.calculate_volume_ema_7d(values)
    sma_7 = calculator.calculate_sma(values, window=7)
    
    print(f"7-day EMA: {float(ema_7):.2f}")
    print(f"7-day SMA: {float(sma_7):.2f}")
    print(f"Difference (EMA more responsive): {float(ema_7 - sma_7):.2f}\n")


def test_ema_trending_down():
    """Test EMA with downward trend"""
    print("=" * 60)
    print("Test 3: EMA with Downward Trend")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Decreasing trend
    values = [Decimal(str(5000 - i * 100)) for i in range(14)]
    
    print(f"Input values (last 7): {[float(v) for v in values[-7:]]}")
    ema_7 = calculator.calculate_volume_ema_7d(values)
    sma_7 = calculator.calculate_sma(values, window=7)
    
    print(f"7-day EMA: {float(ema_7):.2f}")
    print(f"7-day SMA: {float(sma_7):.2f}")
    print(f"EMA responds faster to decline: {float(ema_7 - sma_7):.2f}\n")


def test_ema_volatile():
    """Test EMA with volatile data"""
    print("=" * 60)
    print("Test 4: EMA with Volatile Data")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # High volatility
    values = [
        Decimal('1000'), Decimal('1500'), Decimal('800'),
        Decimal('1200'), Decimal('600'), Decimal('1400'), Decimal('900'),
        Decimal('1300'), Decimal('700'), Decimal('1100'), Decimal('850')
    ]
    
    print(f"Input values: {[float(v) for v in values]}")
    ema_7 = calculator.calculate_volume_ema_7d(values)
    sma_7 = calculator.calculate_sma(values, window=7)
    
    print(f"7-day EMA: {float(ema_7):.2f}")
    print(f"7-day SMA: {float(sma_7):.2f}")
    print(f"EMA smooths volatility better\n")


def test_ema_insufficient_data():
    """Test EMA with insufficient data"""
    print("=" * 60)
    print("Test 5: EMA with Insufficient Data")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Only 5 days when we need 7
    values = [Decimal('1000'), Decimal('1100'), Decimal('1050'), Decimal('1150'), Decimal('1200')]
    
    print(f"Input values ({len(values)} days): {[float(v) for v in values]}")
    ema_7 = calculator.calculate_volume_ema_7d(values)
    
    if ema_7 is None:
        print("Result: None (insufficient data - need at least 7 days)")
    else:
        print(f"7-day EMA: {float(ema_7):.2f}")
    print()


def test_sma_30d():
    """Test 30-day SMA"""
    print("=" * 60)
    print("Test 6: 30-day SMA Calculation")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Generate 30 days of data
    values = generate_sample_volumes(30, base_volume=5000, variance=0.15)
    
    print(f"Generated {len(values)} days of volume data")
    print(f"First 5 values: {[float(v) for v in values[:5]]}")
    print(f"Last 5 values: {[float(v) for v in values[-5:]]}")
    
    sma_30 = calculator.calculate_volume_sma_30d(values)
    
    print(f"30-day SMA: {float(sma_30):.2f}")
    print(f"Average of all values: {float(sum(values) / Decimal(str(len(values)))):.2f}\n")


def test_ema_vs_sma_comparison():
    """Compare EMA vs SMA responsiveness"""
    print("=" * 60)
    print("Test 7: EMA vs SMA Responsiveness Comparison")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Start stable, then sudden spike
    values = [Decimal('1000')] * 10  # Stable
    values.extend([Decimal('5000')] * 5)  # Sudden spike
    
    print(f"Stable (first 10): {[float(v) for v in values[:10]]}")
    print(f"Spike (last 5): {[float(v) for v in values[-5:]]}")
    
    ema_7 = calculator.calculate_volume_ema_7d(values)
    sma_7 = calculator.calculate_sma(values, window=7)
    
    print(f"\n7-day EMA: {float(ema_7):.2f}")
    print(f"7-day SMA: {float(sma_7):.2f}")
    print(f"EMA responds faster to spike: {float(ema_7 - sma_7):.2f}")
    print("EMA gives more weight to recent values\n")


def test_realistic_scenario():
    """Test with realistic booster box volume scenario"""
    print("=" * 60)
    print("Test 8: Realistic Booster Box Volume Scenario")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Simulate 14 days of volume for a popular box
    # Starting at $50k/day, trending up with some variance
    base = 50000
    volumes = []
    for i in range(14):
        # Upward trend with some variance
        value = base + (i * 2000) + random.randint(-5000, 5000)
        volumes.append(Decimal(str(max(10000, value))))  # Floor at $10k
    
    print(f"Daily volumes (USD): {[f'${float(v):,.0f}' for v in volumes]}")
    
    ema_7 = calculator.calculate_volume_ema_7d(volumes)
    sma_30 = calculator.calculate_volume_sma_30d(volumes) if len(volumes) >= 30 else None
    
    print(f"\n7-day EMA: ${float(ema_7):,.2f}")
    if sma_30:
        print(f"30-day SMA: ${float(sma_30):,.2f}")
    else:
        print(f"30-day SMA: Not enough data (need 30 days, have {len(volumes)})")
    print()


def test_edge_cases():
    """Test edge cases"""
    print("=" * 60)
    print("Test 9: Edge Cases")
    print("=" * 60)
    
    calculator = EMACalculator()
    
    # Empty list
    result = calculator.calculate_ema([], window=7)
    print(f"Empty list: {result}")
    
    # Single value
    result = calculator.calculate_ema([Decimal('100')], window=7)
    print(f"Single value: {result}")
    
    # All zeros
    result = calculator.calculate_ema([Decimal('0')] * 7, window=7)
    print(f"All zeros: {result}")
    
    # Very large numbers
    large_values = [Decimal(str(1000000 + i * 100000)) for i in range(10)]
    result = calculator.calculate_volume_ema_7d(large_values)
    print(f"Large numbers (7-day EMA): {float(result):,.2f}")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("EMA Calculator & Metrics Calculation Tests")
    print("=" * 60 + "\n")
    
    test_ema_basic()
    test_ema_trending_up()
    test_ema_trending_down()
    test_ema_volatile()
    test_ema_insufficient_data()
    test_sma_30d()
    test_ema_vs_sma_comparison()
    test_realistic_scenario()
    test_edge_cases()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

