"""
Unit tests for middleware modules.
"""

import pytest
from flask import Flask
from src.middleware.error_handler import APIError, ValidationError, NotFoundError, register_error_handlers
from src.middleware.security import add_security_headers, validate_request_size


class TestErrorHandler:
    """Test cases for error handler middleware"""
    
    def test_api_error_creation(self):
        """Test APIError class creation"""
        error = APIError("Test error", status_code=400)
        
        assert error.message == "Test error"
        assert error.status_code == 400
        assert error.payload == {}
    
    def test_api_error_to_dict(self):
        """Test APIError to_dict method"""
        error = APIError("Test error", status_code=400, payload={"key": "value"})
        error_dict = error.to_dict()
        
        assert error_dict["message"] == "Test error"
        assert error_dict["status_code"] == 400
        assert error_dict["key"] == "value"
    
    def test_validation_error(self):
        """Test ValidationError class"""
        error = ValidationError("Invalid input")
        
        assert error.message == "Invalid input"
        assert error.status_code == 400
    
    def test_not_found_error(self):
        """Test NotFoundError class"""
        error = NotFoundError("Resource not found")
        
        assert error.message == "Resource not found"
        assert error.status_code == 404
    
    def test_register_error_handlers(self):
        """Test register_error_handlers function"""
        app = Flask(__name__)
        register_error_handlers(app)
        
        # Check that error handlers are registered
        assert 400 in app.error_handler_spec[None][400]
        assert 404 in app.error_handler_spec[None][404]
        assert 500 in app.error_handler_spec[None][500]


class TestSecurityMiddleware:
    """Test cases for security middleware"""
    
    def test_add_security_headers(self):
        """Test add_security_headers function"""
        app = Flask(__name__)
        add_security_headers(app)
        
        with app.test_client() as client:
            response = client.get('/')
            
            # Check for security headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-XSS-Protection' in response.headers
            assert 'Content-Security-Policy' in response.headers
            assert 'Referrer-Policy' in response.headers
            assert 'Permissions-Policy' in response.headers
    
    def test_validate_request_size(self):
        """Test validate_request_size function"""
        app = Flask(__name__)
        validate_request_size(app, max_size=1024)
        
        # Test that the before_request handler is registered
        assert len(app.before_request_funcs[None]) > 0
