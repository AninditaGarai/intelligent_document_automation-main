"""
Middleware for error handling and request validation
"""

from .error_handler import register_error_handlers

__all__ = ['register_error_handlers']
