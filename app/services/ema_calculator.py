"""
EMA (Exponential Moving Average) Calculator
Utilities for calculating EMA and SMA for volume and other metrics
"""

from decimal import Decimal
from typing import List, Optional
import math


class EMACalculator:
    """Calculator for Exponential Moving Average (EMA) and Simple Moving Average (SMA)"""
    
    @staticmethod
    def calculate_ema(
        values: List[Decimal],
        window: int,
        alpha: Optional[float] = None
    ) -> Optional[Decimal]:
        """
        Calculate Exponential Moving Average (EMA)
        
        EMA formula:
        - First value: SMA of first window values
        - Subsequent: EMA = (value × alpha) + (previous_EMA × (1 - alpha))
        - alpha = 2 / (window + 1)
        
        Args:
            values: List of Decimal values (should be in chronological order)
            window: Number of periods for EMA (e.g., 7 for 7-day EMA)
            alpha: Smoothing factor (optional, defaults to 2/(window+1))
            
        Returns:
            Decimal EMA value, or None if insufficient data
            
        Examples:
            >>> calculator = EMACalculator()
            >>> values = [Decimal('100'), Decimal('110'), Decimal('105'), Decimal('115'), Decimal('120'), Decimal('118'), Decimal('122')]
            >>> ema_7 = calculator.calculate_ema(values, window=7)
        """
        if not values or len(values) < window:
            return None
        
        # Calculate alpha if not provided
        if alpha is None:
            alpha = 2.0 / (window + 1.0)
        
        # Start with SMA of first window values
        sma_sum = sum(values[:window])
        ema = Decimal(str(sma_sum / window))
        
        # Calculate EMA for remaining values
        for value in values[window:]:
            ema = Decimal(str(value)) * Decimal(str(alpha)) + ema * Decimal(str(1 - alpha))
        
        return ema
    
    @staticmethod
    def calculate_sma(values: List[Decimal], window: int) -> Optional[Decimal]:
        """
        Calculate Simple Moving Average (SMA)
        
        SMA = sum of values / number of values
        
        Args:
            values: List of Decimal values (should be in chronological order)
            window: Number of periods for SMA (e.g., 30 for 30-day SMA)
            
        Returns:
            Decimal SMA value, or None if insufficient data
            
        Examples:
            >>> calculator = EMACalculator()
            >>> values = [Decimal('100'), Decimal('110'), Decimal('105')]  # ... up to 30 values
            >>> sma_30 = calculator.calculate_sma(values, window=30)
        """
        if not values or len(values) < window:
            return None
        
        # Take the last 'window' values
        recent_values = values[-window:]
        sma = sum(recent_values) / Decimal(str(window))
        
        return sma
    
    @staticmethod
    def calculate_volume_ema_7d(daily_volumes: List[Decimal]) -> Optional[Decimal]:
        """
        Calculate 7-day EMA of volume
        
        Convenience method for 7-day EMA specifically for volume metrics
        
        Args:
            daily_volumes: List of daily volume values in chronological order
            
        Returns:
            7-day EMA of volume, or None if less than 7 days of data
        """
        return EMACalculator.calculate_ema(daily_volumes, window=7)
    
    @staticmethod
    def calculate_volume_sma_30d(daily_volumes: List[Decimal]) -> Optional[Decimal]:
        """
        Calculate 30-day SMA of volume
        
        Convenience method for 30-day SMA specifically for volume metrics
        
        Args:
            daily_volumes: List of daily volume values in chronological order
            
        Returns:
            30-day SMA of volume, or None if less than 30 days of data
        """
        return EMACalculator.calculate_sma(daily_volumes, window=30)

