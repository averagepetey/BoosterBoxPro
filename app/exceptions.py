"""
Custom exceptions for BoosterBoxPro API
"""


class BoosterBoxProError(Exception):
    """Base exception for all BoosterBoxPro errors"""
    pass


class BoxNotFoundError(BoosterBoxProError):
    """Raised when a booster box is not found"""
    pass


class InvalidDateError(BoosterBoxProError):
    """Raised when an invalid date is provided"""
    pass


class MetricsNotFoundError(BoosterBoxProError):
    """Raised when metrics are not found for a box/date"""
    pass


class InvalidParameterError(BoosterBoxProError):
    """Raised when an invalid parameter is provided"""
    pass

