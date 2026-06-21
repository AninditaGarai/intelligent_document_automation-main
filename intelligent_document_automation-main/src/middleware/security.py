"""
Security middleware for Flask application
"""

from flask import Flask, request, make_response
from typing import Callable


def add_security_headers(app: Flask) -> None:
    """Add security headers to all responses"""
    
    @app.after_request
    def add_headers(response: make_response) -> make_response:
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Strict transport security (only in production)
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content security policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions policy
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        return response


def validate_request_size(app: Flask, max_size: int = 25 * 1024 * 1024) -> None:
    """Validate request size before processing"""
    
    @app.before_request
    def check_request_size():
        if request.content_length and request.content_length > max_size:
            return {'error': f'Request too large. Maximum size is {max_size / (1024*1024)}MB'}, 413
