"""
Centralized error handling middleware for Flask application
"""

import logging
import traceback
from typing import Any, Dict, Tuple
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message: str, status_code: int = 500, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}

    def to_dict(self) -> Dict[str, Any]:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv


class ValidationError(APIError):
    """Validation error for invalid input"""
    def __init__(self, message: str, payload: Dict[str, Any] = None):
        super().__init__(message, status_code=400, payload=payload)


class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message: str = "Resource not found", payload: Dict[str, Any] = None):
        super().__init__(message, status_code=404, payload=payload)


def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        """Handle custom API errors"""
        logger.error(f"API Error: {error.message} - Status: {error.status_code} - Path: {request.path}")
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP Exception: {error.code} - {error.description} - Path: {request.path}")
        response = jsonify({
            'message': error.description,
            'status_code': error.code
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors"""
        logger.warning(f"Bad Request: {str(error)} - Path: {request.path}")
        response = jsonify({
            'message': 'Bad request',
            'status_code': 400,
            'error': str(error)
        })
        response.status_code = 400
        return response
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors"""
        logger.warning(f"Not Found: {request.path}")
        response = jsonify({
            'message': 'Resource not found',
            'status_code': 404
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(413)
    def handle_request_entity_too_large(error):
        """Handle file too large errors"""
        logger.warning(f"Request Entity Too Large: {request.path}")
        response = jsonify({
            'message': 'File size exceeds maximum limit (25MB)',
            'status_code': 413
        })
        response.status_code = 413
        return response
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors"""
        logger.error(f"Internal Server Error: {str(error)} - Path: {request.path}\n{traceback.format_exc()}")
        response = jsonify({
            'message': 'Internal server error',
            'status_code': 500
        })
        response.status_code = 500
        return response
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        """Handle unexpected errors"""
        logger.error(f"Unexpected Error: {str(error)} - Path: {request.path}\n{traceback.format_exc()}")
        response = jsonify({
            'message': 'An unexpected error occurred',
            'status_code': 500
        })
        response.status_code = 500
        return response
