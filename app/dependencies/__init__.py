"""
Dependencies package
"""

from .auth import get_current_user, get_current_user_required

__all__ = [
    "get_current_user",
    "get_current_user_required",
    "CurrentUser",
]

