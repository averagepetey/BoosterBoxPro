"""
Unit tests for EMA Calculator
"""

import pytest
from decimal import Decimal

from app.services.ema_calculator import EMACalculator


class TestEMACalculator:
    """Test EMA and SMA calculations"""
    
    def test_sma_basic(self):
        """Test basic SMA calculation"""
        calculator = EMACalculator()
        values = [Decimal('100'), Decimal('110'), Decimal('105')]
        result = calculator.calculate_sma(values, window=3)
        
        assert result is not None
        assert result == Decimal('105')  # (100 + 110 + 105) / 3
    
    def test_sma_insufficient_data(self):
        """Test SMA with insufficient data"""
        calculator = EMACalculator()
        values = [Decimal('100'), Decimal('110')]
        result = calculator.calculate_sma(values, window=3)
        
        assert result is None
    
    def test_sma_empty_list(self):
        """Test SMA with empty list"""
        calculator = EMACalculator()
        result = calculator.calculate_sma([], window=7)
        
        assert result is None
    
    def test_ema_basic(self):
        """Test basic EMA calculation"""
        calculator = EMACalculator()
        # 7 values for 7-day EMA
        values = [
            Decimal('100'), Decimal('110'), Decimal('105'),
            Decimal('115'), Decimal('120'), Decimal('118'), Decimal('122')
        ]
        result = calculator.calculate_ema(values, window=7)
        
        assert result is not None
        assert result > Decimal('0')  # Should be positive
    
    def test_ema_insufficient_data(self):
        """Test EMA with insufficient data"""
        calculator = EMACalculator()
        values = [Decimal('100'), Decimal('110'), Decimal('105')]
        result = calculator.calculate_ema(values, window=7)
        
        assert result is None
    
    def test_volume_ema_7d(self):
        """Test 7-day EMA convenience method"""
        calculator = EMACalculator()
        daily_volumes = [
            Decimal('1000'), Decimal('1100'), Decimal('1050'),
            Decimal('1150'), Decimal('1200'), Decimal('1180'), Decimal('1220')
        ]
        result = calculator.calculate_volume_ema_7d(daily_volumes)
        
        assert result is not None
        assert result > Decimal('0')
    
    def test_volume_sma_30d(self):
        """Test 30-day SMA convenience method"""
        calculator = EMACalculator()
        daily_volumes = [Decimal(str(1000 + i * 10)) for i in range(30)]
        result = calculator.calculate_volume_sma_30d(daily_volumes)
        
        assert result is not None
        assert result > Decimal('0')
    
    def test_ema_with_custom_alpha(self):
        """Test EMA with custom alpha value"""
        calculator = EMACalculator()
        values = [
            Decimal('100'), Decimal('110'), Decimal('105'),
            Decimal('115'), Decimal('120'), Decimal('118'), Decimal('122')
        ]
        result_default = calculator.calculate_ema(values, window=7)
        result_custom = calculator.calculate_ema(values, window=7, alpha=0.3)
        
        assert result_default is not None
        assert result_custom is not None
        # Results should differ with different alpha
        assert result_default != result_custom

