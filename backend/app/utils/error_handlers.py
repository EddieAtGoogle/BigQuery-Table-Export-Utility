"""
Error Handling Utilities

This module provides centralized error handling for the application.
"""

from flask import Flask, jsonify
from structlog import get_logger
from google.api_core import exceptions as google_exceptions
from werkzeug.exceptions import HTTPException

logger = get_logger(__name__)

class APIError(Exception):
    """Base class for API errors."""
    
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=401, details=details)

def register_error_handlers(app: Flask) -> None:
    """
    Register error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        response = {
            'error': error.message,
            'details': error.details
        }
        return jsonify(response), error.status_code

    @app.errorhandler(google_exceptions.GoogleAPIError)
    def handle_google_api_error(error):
        """Handle Google API errors."""
        logger.error("google_api_error", error=str(error))
        response = {
            'error': 'Google API Error',
            'message': str(error)
        }
        return jsonify(response), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        """Handle HTTP errors."""
        response = {
            'error': error.name,
            'message': error.description
        }
        return jsonify(response), error.code

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle any unhandled exceptions."""
        logger.exception("unhandled_error", error=str(error))
        response = {
            'error': 'Internal Server Error',
            'message': str(error) if app.debug else 'An unexpected error occurred'
        }
        return jsonify(response), 500

# Common API Errors
class ValidationError(APIError):
    """Raised when request validation fails."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)

class NotFoundError(APIError):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=404, details=details)

class ExportError(APIError):
    """Raised when there's an error during the export process."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=500, details=details) 