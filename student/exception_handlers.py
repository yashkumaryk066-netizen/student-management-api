"""
Custom Exception Handlers for Security
SECURITY FIX #18: Prevent information disclosure in error messages
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('student.security')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that prevents information disclosure
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the actual error for debugging
    request = context.get('request')
    user = request.user if request else None
    
    logger.error(
        f"Exception: {exc.__class__.__name__}: {str(exc)} | "
        f"User: {user} | Path: {request.path if request else 'N/A'}",
        exc_info=True
    )
    
    # If response is None, it's an unhandled exception
    if response is None:
        # Don't expose internal errors to users
        return Response(
            {
                "error": "An internal error occurred. Please contact support if this persists.",
                "error_code": "INTERNAL_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Sanitize error messages for production
    if not hasattr(exc, 'detail'):
        response.data = {
            "error": "An error occurred processing your request.",
            "error_code": "REQUEST_ERROR"
        }
    
    # Add request ID for tracking
    if request:
        response.data['request_id'] = id(request)
    
    return response
